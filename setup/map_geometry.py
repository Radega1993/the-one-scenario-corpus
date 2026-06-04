"""
Shared WKT geometry, sim-coordinate transforms, and road-graph utilities
for map validation / repair scripts under scenarios/setup/.
"""

from __future__ import annotations

import json
import math
import random
import re
from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx

SCENARIOS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SCENARIOS_DIR.parent
WKT_DIR = SCENARIOS_DIR / "maps" / "wkt"
DATA_DIR = REPO_ROOT / "data"
ANALYSIS_DATA = SCENARIOS_DIR / "analysis" / "data"

LINESTRING_RE = re.compile(r"LINESTRING\s*\(([^)]+)\)", re.IGNORECASE)
POINT_RE = re.compile(r"POINT\s*\(([^)]+)\)", re.IGNORECASE)

ACTIVE_MAPS = [
    "HelsinkiDowntown",
    "KumpulaCampus",
    "ManhattanMidtownGrid",
    "NuuksioSparseTrails",
    "HelsinkiDisrupted",
    "KallioCommunityCompact",
]

FAMILY_THRESHOLD_M = {
    "01_urban": 50.0,
    "02_campus": 50.0,
    "03_vehicles": 50.0,
    "04_rural": 150.0,
    "05_disaster": 50.0,
    "06_social": 50.0,
}

BUS_COLORS = {
    "A_bus": "#c05621",
    "B_bus": "#dd6b20",
    "C_bus": "#ed8936",
    "D_bus": "#f6ad55",
}

def parse_linestrings(path: Path) -> list[list[tuple[float, float]]]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines: list[list[tuple[float, float]]] = []
    for m in LINESTRING_RE.finditer(text):
        pts: list[tuple[float, float]] = []
        for pair in m.group(1).split(","):
            parts = pair.strip().split()
            if len(parts) >= 2:
                try:
                    pts.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    continue
        if len(pts) >= 2:
            lines.append(pts)
    return lines

def parse_points(path: Path) -> list[tuple[float, float]]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    pts: list[tuple[float, float]] = []
    for m in POINT_RE.finditer(text):
        parts = m.group(1).strip().split()
        if len(parts) >= 2:
            try:
                pts.append((float(parts[0]), float(parts[1])))
            except ValueError:
                continue
    return pts

def wkt_to_sim_coords(raw_lines: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    if not raw_lines:
        return []
    mirrored = [[(x, -y) for x, y in line] for line in raw_lines]
    xs = [x for line in mirrored for x, _ in line]
    ys = [y for line in mirrored for _, y in line]
    if not xs:
        return []
    min_x, min_y = min(xs), min(ys)
    return [[(x - min_x, y - min_y) for x, y in line] for line in mirrored]

def transform_points(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not pts:
        return []
    mirrored = [(x, -y) for x, y in pts]
    min_x = min(x for x, _ in mirrored)
    min_y = min(y for _, y in mirrored)
    return [(x - min_x, y - min_y) for x, y in mirrored]

@dataclass
class SimTransform:
    min_x: float
    min_y: float  # min of mirrored Y

    @classmethod
    def from_raw_lines(cls, raw_lines: list[list[tuple[float, float]]]) -> SimTransform:
        mirrored = [[(x, -y) for x, y in line] for line in raw_lines]
        xs = [x for line in mirrored for x, _ in line]
        ys = [y for line in mirrored for _, y in line]
        return cls(min(xs), min(ys))

    def sim_to_raw(self, x: float, y: float) -> tuple[float, float]:
        return (x + self.min_x, -(y + self.min_y))

    def raw_to_sim(self, x: float, y: float) -> tuple[float, float]:
        return (x - self.min_x, -y - self.min_y)

def sim_waypoints_to_raw(
    sim_pts: list[tuple[float, float]],
    raw_lines: list[list[tuple[float, float]]],
    rg: RoadGraph | None = None,
) -> list[tuple[float, float]]:
    if rg is not None and rg.raw_node_list:
        out: list[tuple[float, float]] = []
        for x, y in sim_pts:
            idx = rg.snap_index(x, y)
            out.append(rg.raw_node_list[idx])
        return dedupe_consecutive(out)
    tf = SimTransform.from_raw_lines(raw_lines)
    return dedupe_consecutive([tf.sim_to_raw(x, y) for x, y in sim_pts])

def point_to_segment_distance(
    px: float, py: float,
    x1: float, y1: float, x2: float, y2: float,
) -> float:
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)

def nearest_segment_distance(px: float, py: float, segments: list[tuple[tuple, tuple]]) -> float:
    if not segments:
        return float("inf")
    return min(point_to_segment_distance(px, py, a[0], a[1], b[0], b[1]) for a, b in segments)

def _round_key(x: float, y: float, prec: int = 3) -> tuple[float, float]:
    return (round(x, prec), round(y, prec))

@dataclass
class RoadGraph:
    """Road network in sim-aligned coordinates."""
    segments: list[tuple[tuple[float, float], tuple[float, float]]] = field(default_factory=list)
    node_list: list[tuple[float, float]] = field(default_factory=list)
    raw_node_list: list[tuple[float, float]] = field(default_factory=list)
    node_index: dict[tuple[float, float], int] = field(default_factory=dict)
    graph: nx.Graph = field(default_factory=nx.Graph)
    bbox: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    raw_segments: list[tuple[tuple[float, float], tuple[float, float]]] = field(default_factory=list)

    @classmethod
    def from_roads_wkt(cls, roads_path: Path) -> RoadGraph:
        raw = parse_linestrings(roads_path)
        sim = wkt_to_sim_coords(raw)
        rg = cls()
        seen: dict[tuple[float, float], int] = {}
        rg.raw_segments = []
        for rseg, sseg in zip(raw, sim):
            for i in range(len(sseg) - 1):
                a, b = sseg[i], sseg[i + 1]
                ra, rb = rseg[i], rseg[i + 1]
                rg.segments.append((a, b))
                rg.raw_segments.append((ra, rb))
                for p, rp in ((a, ra), (b, rb)):
                    k = _round_key(p[0], p[1])
                    if k not in seen:
                        seen[k] = len(rg.node_list)
                        rg.node_list.append(p)
                        rg.raw_node_list.append(rp)
                        rg.node_index[k] = seen[k]
                ia, ib = seen[_round_key(a[0], a[1])], seen[_round_key(b[0], b[1])]
                w = math.hypot(b[0] - a[0], b[1] - a[1])
                if w > 0:
                    rg.graph.add_edge(ia, ib, weight=w)
        if rg.node_list:
            xs = [p[0] for p in rg.node_list]
            ys = [p[1] for p in rg.node_list]
            rg.bbox = (min(xs), min(ys), max(xs), max(ys))
        return rg

    def snap_to_nearest_node(self, x: float, y: float) -> tuple[float, float]:
        if not self.node_list:
            return (x, y)
        best = min(self.node_list, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)
        return best

    def snap_index(self, x: float, y: float) -> int:
        p = self.snap_to_nearest_node(x, y)
        return self.node_index[_round_key(p[0], p[1])]

    def shortest_path_length(self, a: tuple[float, float], b: tuple[float, float]) -> float | None:
        if self.graph.number_of_nodes() < 2:
            return None
        try:
            ia = self.snap_index(a[0], a[1])
            ib = self.snap_index(b[0], b[1])
            return nx.shortest_path_length(self.graph, ia, ib, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def path_coords(self, a: tuple[float, float], b: tuple[float, float]) -> list[tuple[float, float]]:
        ia = self.snap_index(a[0], a[1])
        ib = self.snap_index(b[0], b[1])
        try:
            idxs = nx.shortest_path(self.graph, ia, ib, weight="weight")
            return [self.node_list[i] for i in idxs]
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return [a, b]

def load_map_metadata(map_dir: Path) -> dict:
    meta_path = map_dir / "metadata.json"
    if meta_path.is_file():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return {}

def world_size_from_metadata(meta: dict) -> tuple[float, float]:
    ws = meta.get("world_size", [0, 0])
    if len(ws) >= 2:
        return float(ws[0]), float(ws[1])
    return 0.0, 0.0

def points_inside_world_size(pts: list[tuple[float, float]], wx: float, wy: float) -> bool:
    if wx <= 0 or wy <= 0:
        return True
    return all(0 <= x <= wx and 0 <= y <= wy for x, y in pts)

def threshold_for_family(family: str) -> float:
    return FAMILY_THRESHOLD_M.get(family, 50.0)

def list_bus_wkt_files(map_dir: Path) -> list[Path]:
    return sorted(map_dir.glob("*_bus.wkt"))

def list_route_wkt_files(map_dir: Path) -> list[Path]:
    """All auxiliary route WKT files (bus, shuttle, patrol, vehicle, etc.)."""
    patterns = (
        "*_bus.wkt",
        "*_shuttle.wkt",
        "*_patrol.wkt",
        "*_route.wkt",
        "*_mule*.wkt",
        "*_emergency*.wkt",
        "*_community*.wkt",
        "*_control*.wkt",
        "*_rescue*.wkt",
    )
    seen: set[Path] = set()
    out: list[Path] = []
    for pat in patterns:
        for p in sorted(map_dir.glob(pat)):
            if p not in seen:
                seen.add(p)
                out.append(p)
    return sorted(out, key=lambda p: p.name)

def resolve_route_path_polyline(
    rg: RoadGraph,
    stops: list[tuple[float, float]],
) -> tuple[list[tuple[float, float]], list[tuple[int, int]]]:
    """Concatenate Dijkstra paths between consecutive stops (sim coords).

    Returns (polyline_coords, unresolved_segment_indices) where each index
    is the stop pair index i meaning segment stops[i] -> stops[i+1] failed.
    """
    if len(stops) < 2:
        return list(stops), []
    poly: list[tuple[float, float]] = []
    failed: list[tuple[int, int]] = []
    for i in range(len(stops) - 1):
        seg = rg.path_coords(stops[i], stops[i + 1])
        if len(seg) == 2 and rg.shortest_path_length(stops[i], stops[i + 1]) is None:
            failed.append((i, i + 1))
        if poly:
            seg = seg[1:]
        poly.extend(seg)
    return dedupe_consecutive(poly), failed

def list_poi_wkt_files(map_dir: Path) -> list[Path]:
    out = []
    for name in ("A_homes.wkt", "A_offices.wkt", "A_meetingspots.wkt"):
        p = map_dir / name
        if p.is_file():
            out.append(p)
    return out

def euclidean_polyline_length(pts: list[tuple[float, float]]) -> float:
    if len(pts) < 2:
        return 0.0
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))

def graph_path_length(rg: RoadGraph, pts: list[tuple[float, float]]) -> float | None:
    if len(pts) < 2:
        return 0.0
    total = 0.0
    for i in range(len(pts) - 1):
        d = rg.shortest_path_length(pts[i], pts[i + 1])
        if d is None:
            return None
        total += d
    return total

def vertex_distances(rg: RoadGraph, pts: list[tuple[float, float]]) -> list[float]:
    return [nearest_segment_distance(x, y, rg.segments) for x, y in pts]

def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * p / 100.0
    f = int(math.floor(k))
    c = int(math.ceil(k))
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)

def dedupe_consecutive(pts: list[tuple[float, float]], eps: float = 1.0) -> list[tuple[float, float]]:
    if not pts:
        return []
    out = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
            out.append(p)
    return out

def generate_bus_route_on_graph(
    rg: RoadGraph,
    rng: random.Random,
    *,
    n_stops: int = 12,
    family: str = "01_urban",
) -> list[tuple[float, float]]:
    """Build a graph-coherent bus route (waypoints on road nodes)."""
    if rg.graph.number_of_nodes() < 2:
        return list(rg.node_list[: min(n_stops, len(rg.node_list))])

    nodes = rg.node_list
    n_stops = min(n_stops, len(nodes))
    if n_stops < 2:
        return nodes[:]

    # Seed stops: peripheral + high-degree spread
    deg = dict(rg.graph.degree())
    by_deg = sorted(range(len(nodes)), key=lambda i: deg.get(i, 0), reverse=True)
    corners = sorted(nodes, key=lambda p: p[0] + p[1])
    seeds: list[tuple[float, float]] = []
    if corners:
        seeds.append(corners[0])
        seeds.append(corners[-1])
    for i in by_deg[: max(2, n_stops // 3)]:
        seeds.append(nodes[i])
    while len(seeds) < n_stops:
        seeds.append(rng.choice(nodes))
    seeds = dedupe_consecutive([rg.snap_to_nearest_node(p[0], p[1]) for p in seeds])[:n_stops]

    if family in ("04_rural", "05_disaster"):
        n_stops = min(n_stops, 8)
        seeds = seeds[:n_stops]

    # Nearest-neighbor tour on graph metric from first seed
    tour: list[tuple[float, float]] = [seeds[0]]
    remaining = seeds[1:]
    while remaining:
        last = tour[-1]
        nxt = min(
            remaining,
            key=lambda p: rg.shortest_path_length(last, p) or float("inf"),
        )
        tour.append(nxt)
        remaining.remove(nxt)

    return dedupe_consecutive(tour)

def repair_route_waypoints(
    rg: RoadGraph,
    raw_route: list[tuple[float, float]],
    sim_route: list[tuple[float, float]],
    rng: random.Random,
    family: str,
) -> list[tuple[float, float]]:
    """Return sim-aligned waypoints snapped and reordered on graph."""
    snapped = dedupe_consecutive([rg.snap_to_nearest_node(x, y) for x, y in sim_route])
    if len(snapped) < 2:
        return generate_bus_route_on_graph(rg, rng, family=family)
    graph_len = graph_path_length(rg, snapped)
    eucl = euclidean_polyline_length(snapped)
    ratio = (eucl / graph_len) if graph_len and graph_len > 0 else 1.0
    if ratio > 0.85 and all(d <= threshold_for_family(family) for d in vertex_distances(rg, snapped)):
        return snapped
    return generate_bus_route_on_graph(rg, rng, n_stops=max(8, min(15, len(snapped))), family=family)

def write_linestring_wkt(points: list[tuple[float, float]], path: Path) -> None:
    def fmt(v: float) -> str:
        return f"{v:.6f}"

    with path.open("w", encoding="utf-8") as f:
        if len(points) >= 2:
            pts = ", ".join(f"{fmt(x)} {fmt(y)}" for x, y in points)
            f.write(f"LINESTRING ({pts})\n\n")

def map_wkt_dir(map_name: str, prefer_data: bool = False) -> Path:
    if prefer_data:
        p = DATA_DIR / map_name
        if p.is_dir():
            return p
    return WKT_DIR / map_name

def load_road_graph(map_name: str) -> tuple[RoadGraph, Path, dict]:
    map_dir = WKT_DIR / map_name
    roads_path = map_dir / "roads.wkt"
    if not roads_path.is_file():
        roads_path = DATA_DIR / map_name / "roads.wkt"
    meta = load_map_metadata(map_dir)
    return RoadGraph.from_roads_wkt(roads_path), roads_path, meta