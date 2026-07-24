"""Topology metrics and discovery for map_space_v1 validation / features."""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import networkx as nx

from map_geometry import RoadGraph, parse_linestrings, wkt_to_sim_coords

MAP_SPACE_ROOT = Path(__file__).resolve().parent.parent / "map_space_v1"
DEGENERATE_LEN_M = 1e-6


@dataclass
class MapRecord:
    map_id: str
    wkt_dir: Path
    roads_path: Path
    source_type: str = ""
    archetype: str = ""
    generator_type: str = ""
    manifest_row: dict[str, str] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def metadata_path(self) -> Path:
        return self.wkt_dir / "metadata.json"

    def preview_path(self, map_space_root: Path) -> Path | None:
        for sub in ("synthetic/previews", "real_osm/previews"):
            p = map_space_root / sub / f"{self.map_id}.png"
            if p.is_file():
                return p
        return None


def load_manifest(manifest_path: Path) -> dict[str, dict[str, str]]:
    if not manifest_path.is_file():
        return {}
    with manifest_path.open(encoding="utf-8") as f:
        return {row["map_id"]: row for row in csv.DictReader(f)}


def discover_maps(map_space_root: Path, manifest_path: Path) -> list[MapRecord]:
    """Union of manifest entries and filesystem wkt/*/roads.wkt."""
    manifest = load_manifest(manifest_path)
    by_id: dict[str, MapRecord] = {}

    for map_id, row in manifest.items():
        wkt_rel = row.get("wkt_dir", "")
        wkt_dir = map_space_root / wkt_rel if wkt_rel else None
        if wkt_dir and (wkt_dir / "roads.wkt").is_file():
            by_id[map_id] = MapRecord(
                map_id=map_id,
                wkt_dir=wkt_dir,
                roads_path=wkt_dir / "roads.wkt",
                source_type=row.get("source_type", ""),
                archetype=row.get("archetype", ""),
                generator_type=row.get("generator_type", ""),
                manifest_row=row,
            )

    for roads in sorted(map_space_root.glob("**/wkt/*/roads.wkt")):
        if "_archive" in roads.parts:
            continue
        map_id = roads.parent.name
        if map_id in by_id:
            continue
        wkt_dir = roads.parent
        rel = wkt_dir.relative_to(map_space_root)
        source_type = "osm" if "real_osm" in str(rel) else "synthetic"
        by_id[map_id] = MapRecord(
            map_id=map_id,
            wkt_dir=wkt_dir,
            roads_path=roads,
            source_type=source_type,
            archetype="",
            generator_type="",
        )

    for rec in by_id.values():
        if rec.metadata_path.is_file():
            rec.meta = json.loads(rec.metadata_path.read_text(encoding="utf-8"))
            rec.source_type = rec.meta.get("source_type") or rec.meta.get("source") or rec.source_type
            rec.archetype = rec.meta.get("map_archetype") or rec.meta.get("archetype") or rec.archetype
            rec.generator_type = rec.meta.get("map_generator_type") or rec.meta.get("generator_type") or rec.generator_type

    return sorted(by_id.values(), key=lambda r: r.map_id)


def build_road_graph(roads_path: Path) -> RoadGraph:
    return RoadGraph.from_roads_wkt(roads_path)


def segment_length_stats(rg: RoadGraph) -> tuple[float, int]:
    total = 0.0
    degenerate = 0
    for a, b in rg.segments:
        w = math.hypot(b[0] - a[0], b[1] - a[1])
        total += w
        if w < DEGENERATE_LEN_M:
            degenerate += 1
    return total, degenerate


def road_bbox_area(rg: RoadGraph) -> float:
    min_x, min_y, max_x, max_y = rg.bbox
    return max(0.0, (max_x - min_x) * (max_y - min_y))


def spatial_coverage_ratio(rg: RoadGraph, world_size: tuple[int, int]) -> float:
    """Fraction of worldSize box occupied by the road-network bounding box."""
    wx, wy = world_size
    world_area = float(wx * wy) if wx > 0 and wy > 0 else 0.0
    if world_area <= 0:
        return 0.0
    return road_bbox_area(rg) / world_area


def margin_m_from_meta(meta: dict[str, Any], default: float = 20.0) -> float:
    for key in ("occupancy_margin_m", "world_size_margin_m"):
        if key in meta:
            try:
                return float(meta[key])
            except (TypeError, ValueError):
                pass
    return default


def roads_encroach_world_margin(
    rg: RoadGraph,
    world_size: tuple[int, int],
    margin_m: float,
    tol: float = 1.0,
) -> bool:
    """True when roads extend into the reserved worldSize margin band."""
    wx, wy = world_size
    if wx <= 0 or wy <= 0:
        return False
    min_x, min_y, max_x, max_y = rg.bbox
    inner_x = wx - margin_m
    inner_y = wy - margin_m
    return max_x > inner_x + tol or max_y > inner_y + tol or min_x < -tol or min_y < -tol


def count_components(graph: nx.Graph) -> tuple[int, float]:
    if graph.number_of_nodes() == 0:
        return 0, 0.0
    comps = list(nx.connected_components(graph))
    sizes = [len(c) for c in comps]
    largest = max(sizes)
    ratio = largest / graph.number_of_nodes()
    return len(comps), ratio


def bridge_and_articulation(graph: nx.Graph) -> tuple[int, int]:
    if graph.number_of_nodes() < 2:
        return 0, 0
    n_bridges = sum(1 for _ in nx.bridges(graph))
    n_art = sum(1 for _ in nx.articulation_points(graph))
    return n_bridges, n_art


def _edge_bearings(segments: list[tuple[tuple[float, float], tuple[float, float]]]) -> list[float]:
    bearings: list[float] = []
    for a, b in segments:
        dx, dy = b[0] - a[0], b[1] - a[1]
        if dx == 0 and dy == 0:
            continue
        bearings.append(math.degrees(math.atan2(dy, dx)) % 180.0)
    return bearings


def orientation_entropy(segments: list[tuple[tuple[float, float], tuple[float, float]]]) -> float:
    bearings = _edge_bearings(segments)
    if not bearings:
        return 0.0
    n_bins = 36
    counts = [0] * n_bins
    for b in bearings:
        idx = min(int(b / (180.0 / n_bins)), n_bins - 1)
        counts[idx] += 1
    total = sum(counts)
    ent = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            ent -= p * math.log2(p)
    return ent


def gridness_score(segments: list[tuple[tuple[float, float], tuple[float, float]]]) -> float:
    bearings = _edge_bearings(segments)
    if not bearings:
        return 0.0
    aligned = 0
    for b in bearings:
        d_axis = min(b, abs(b - 90), 180 - b)
        if d_axis <= 15:
            aligned += 1
    return aligned / len(bearings)


def corridor_score(node_coords: list[tuple[float, float]]) -> float:
    if len(node_coords) < 3:
        return 1.0
    xs = [p[0] for p in node_coords]
    ys = [p[1] for p in node_coords]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    cxx = sum((x - mx) ** 2 for x in xs) / len(xs)
    cyy = sum((y - my) ** 2 for y in ys) / len(ys)
    cxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(len(xs))) / len(xs)
    # eigenvalues of 2x2 covariance
    trace = cxx + cyy
    det = cxx * cyy - cxy * cxy
    disc = max(0.0, trace * trace / 4 - det)
    lam1 = trace / 2 + math.sqrt(disc)
    lam2 = trace / 2 - math.sqrt(disc)
    if lam2 < 1e-9:
        return 10.0
    return lam1 / lam2


def radial_score(node_coords: list[tuple[float, float]]) -> float:
    if len(node_coords) < 3:
        return 0.0
    xs = [p[0] for p in node_coords]
    ys = [p[1] for p in node_coords]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    dists = [math.hypot(x - cx, y - cy) for x, y in node_coords]
    mean_d = sum(dists) / len(dists)
    if mean_d < 1e-9:
        return 0.0
    var = sum((d - mean_d) ** 2 for d in dists) / len(dists)
    cv = math.sqrt(var) / mean_d
    return max(0.0, 1.0 - cv)


def partition_score(graph: nx.Graph) -> float:
    n_comp, _ = count_components(graph)
    if n_comp <= 1:
        return 0.0
    n_bridges, _ = bridge_and_articulation(graph)
    max_possible = n_comp * (n_comp - 1) // 2
    if max_possible == 0:
        return 0.0
    return min(1.0, n_bridges / max_possible)


def community_score(graph: nx.Graph) -> float:
    """Fraction of edges within greedy-modularity communities (higher = more clustered)."""
    if graph.number_of_edges() < 2:
        return 0.0
    try:
        from networkx.algorithms import community

        comms = list(community.greedy_modularity_communities(graph, weight="weight"))
        if len(comms) <= 1:
            return 0.0
        node_to_c: dict[Any, int] = {}
        for i, c in enumerate(comms):
            for n in c:
                node_to_c[n] = i
        intra = sum(1 for u, v in graph.edges() if node_to_c.get(u) == node_to_c.get(v))
        return intra / graph.number_of_edges()
    except Exception:
        return 0.0


def diameter_and_avg_path(
    graph: nx.Graph,
    *,
    samples: int = 64,
    seed: int = 42,
) -> tuple[float, float]:
    nodes = list(graph.nodes())
    if len(nodes) < 2:
        return 0.0, 0.0
    # diameter approx from highest-degree node
    start = max(nodes, key=lambda n: graph.degree(n))
    dists = nx.single_source_dijkstra_path_length(graph, start, weight="weight")
    ecc = max(dists.values()) if dists else 0.0
    diameter = 2.0 * ecc

    rng = random.Random(seed)
    path_lengths: list[float] = []
    attempts = 0
    while len(path_lengths) < samples and attempts < samples * 10:
        attempts += 1
        a, b = rng.sample(nodes, 2)
        try:
            d = nx.shortest_path_length(graph, a, b, weight="weight")
            path_lengths.append(d)
        except nx.NetworkXNoPath:
            continue
    avg_path = sum(path_lengths) / len(path_lengths) if path_lengths else 0.0
    return diameter, avg_path


def circuity_approx(
    graph: nx.Graph,
    node_list: list[tuple[float, float]],
    *,
    samples: int = 64,
    seed: int = 42,
) -> float:
    nodes = list(graph.nodes())
    if len(nodes) < 2:
        return 1.0
    rng = random.Random(seed + 1)
    ratios: list[float] = []
    attempts = 0
    while len(ratios) < samples and attempts < samples * 10:
        attempts += 1
        a, b = rng.sample(nodes, 2)
        pa, pb = node_list[a], node_list[b]
        eucl = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
        if eucl < 1e-6:
            continue
        try:
            sp = nx.shortest_path_length(graph, a, b, weight="weight")
            ratios.append(sp / eucl)
        except nx.NetworkXNoPath:
            continue
    return sum(ratios) / len(ratios) if ratios else 1.0


def graph_with_node_positions(rg: RoadGraph) -> nx.Graph:
    g = nx.Graph()
    for i, p in enumerate(rg.node_list):
        g.add_node(i, x=p[0], y=p[1])
    for u, v, data in rg.graph.edges(data=True):
        g.add_edge(u, v, weight=data.get("weight", 1.0))
    return g


def edge_length_stats(rg: RoadGraph) -> tuple[float, float, float]:
    """Return (total_length_m, avg_length_m, median_length_m)."""
    lengths: list[float] = []
    for a, b in rg.segments:
        w = math.hypot(b[0] - a[0], b[1] - a[1])
        if w > DEGENERATE_LEN_M:
            lengths.append(w)
    if not lengths:
        return 0.0, 0.0, 0.0
    total = sum(lengths)
    return total, total / len(lengths), statistics.median(lengths)


def intersection_ratio(graph: nx.Graph) -> float:
    n = graph.number_of_nodes()
    if n == 0:
        return 0.0
    intersections = sum(1 for _, d in graph.degree() if d >= 3)
    return intersections / n


def tree_like_score(graph: nx.Graph) -> float:
    """Higher when largest component is close to a tree (high dead-ends, E ≈ N-1)."""
    if graph.number_of_nodes() < 2:
        return 0.0
    comps = list(nx.connected_components(graph))
    if not comps:
        return 0.0
    largest = max(comps, key=len)
    sub = graph.subgraph(largest).copy()
    n = sub.number_of_nodes()
    e = sub.number_of_edges()
    if n == 0:
        return 0.0
    tree_closeness = 1.0 - min(1.0, abs(e - (n - 1)) / max(e, 1))
    dead_ends = sum(1 for _, d in sub.degree() if d == 1)
    dead_end_ratio = dead_ends / n
    return max(0.0, min(1.0, tree_closeness * (0.5 + 0.5 * dead_end_ratio)))


def community_score_safe(graph: nx.Graph) -> float:
    try:
        return community_score(graph)
    except Exception:
        return float("nan")


def bbox_dimensions(rg: RoadGraph) -> tuple[float, float]:
    min_x, min_y, max_x, max_y = rg.bbox
    return max(0.0, max_x - min_x), max(0.0, max_y - min_y)


def extract_saturation_features(
    rg: RoadGraph,
    world_size: tuple[int, int],
    seed: int = 42,
    *,
    max_samples: int = 64,
) -> tuple[dict[str, float | int], list[str]]:
    """
    Full feature vector for map_space_saturation feature extraction.
    Returns (features_dict, list_of_omitted_feature_names).
    """
    omissions: list[str] = []
    g = graph_with_node_positions(rg)
    wx, wy = world_size
    world_area = float(wx * wy) if wx > 0 and wy > 0 else 0.0
    useful_area = road_bbox_area(rg)
    bbox_w, bbox_h = bbox_dimensions(rg)

    n_nodes = g.number_of_nodes()
    n_edges = rg.graph.number_of_edges()
    degrees = [d for _, d in g.degree()]
    avg_degree = (2 * n_edges / n_nodes) if n_nodes else 0.0
    max_degree = max(degrees) if degrees else 0
    dead_ends = sum(1 for d in degrees if d == 1)
    dead_end_ratio = dead_ends / n_nodes if n_nodes else 0.0

    total_len, avg_edge_len, median_edge_len = edge_length_stats(rg)

    feats: dict[str, float | int] = {
        "world_size_x": wx,
        "world_size_y": wy,
        "world_area": world_area,
        "bbox_width": round(bbox_w, 2),
        "bbox_height": round(bbox_h, 2),
        "useful_area": round(useful_area, 2),
        "useful_area_ratio": (useful_area / world_area) if world_area > 0 else 0.0,
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "total_road_length_m": round(total_len, 2),
        "road_density": (n_edges / world_area) if world_area > 0 else 0.0,
        "avg_edge_length_m": round(avg_edge_len, 4),
        "median_edge_length_m": round(median_edge_len, 4),
        "avg_degree": round(avg_degree, 4),
        "max_degree": max_degree,
        "dead_end_ratio": round(dead_end_ratio, 4),
        "intersection_ratio": round(intersection_ratio(g), 4),
    }

    try:
        n_comp, largest_ratio = count_components(g)
        n_bridges, n_art = bridge_and_articulation(g)
        feats["n_components"] = n_comp
        feats["largest_component_ratio"] = round(largest_ratio, 4)
        feats["bridge_edges_count"] = n_bridges
        feats["bridge_edges_ratio"] = round(n_bridges / n_edges, 6) if n_edges else 0.0
        feats["articulation_points_count"] = n_art
        feats["articulation_points_ratio"] = round(n_art / n_nodes, 6) if n_nodes else 0.0
    except Exception:
        for k in (
            "n_components",
            "largest_component_ratio",
            "bridge_edges_count",
            "bridge_edges_ratio",
            "articulation_points_count",
            "articulation_points_ratio",
        ):
            feats[k] = float("nan")
            omissions.append(k)

    samples = max_samples if n_nodes <= 10_000 else min(max_samples, 32)

    try:
        diameter, avg_path = diameter_and_avg_path(g, samples=samples, seed=seed)
        feats["graph_diameter_approx"] = round(diameter, 2)
        feats["avg_shortest_path_approx"] = round(avg_path, 2)
    except Exception:
        feats["graph_diameter_approx"] = float("nan")
        feats["avg_shortest_path_approx"] = float("nan")
        omissions.extend(["graph_diameter_approx", "avg_shortest_path_approx"])

    try:
        feats["circuity_approx"] = round(circuity_approx(g, rg.node_list, samples=samples, seed=seed), 4)
    except Exception:
        feats["circuity_approx"] = float("nan")
        omissions.append("circuity_approx")

    shape_features: dict[str, Any] = {
        "orientation_entropy": lambda: orientation_entropy(rg.segments),
        "gridness_score": lambda: gridness_score(rg.segments),
        "corridor_score": lambda: corridor_score(rg.node_list),
        "radial_score": lambda: radial_score(rg.node_list),
        "partition_score": lambda: partition_score(g),
        "community_score": lambda: community_score_safe(g),
        "tree_like_score": lambda: tree_like_score(g),
    }
    for name, fn in shape_features.items():
        try:
            val = fn()
            if isinstance(val, float) and math.isnan(val):
                feats[name] = float("nan")
                omissions.append(name)
            else:
                feats[name] = round(float(val), 4)
        except Exception:
            feats[name] = float("nan")
            omissions.append(name)

    return feats, omissions


def extract_topology_features(rg: RoadGraph, world_size: tuple[int, int], seed: int = 42) -> dict[str, float | int]:
    g = graph_with_node_positions(rg)
    total_len, _ = segment_length_stats(rg)
    n_nodes = g.number_of_nodes()
    n_edges = rg.graph.number_of_edges()
    wx, wy = world_size
    world_area = float(wx * wy) if wx > 0 and wy > 0 else 0.0
    useful_area = road_bbox_area(rg)

    degrees = [d for _, d in g.degree()]
    avg_degree = (2 * n_edges / n_nodes) if n_nodes else 0.0
    max_degree = max(degrees) if degrees else 0
    dead_ends = sum(1 for d in degrees if d == 1)
    dead_end_ratio = dead_ends / n_nodes if n_nodes else 0.0

    n_comp, largest_ratio = count_components(g)
    n_bridges, n_art = bridge_and_articulation(g)
    diameter, avg_path = diameter_and_avg_path(g, seed=seed)
    circuity = circuity_approx(g, rg.node_list, seed=seed)

    return {
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "total_road_length_m": round(total_len, 2),
        "road_density": (n_edges / world_area) if world_area > 0 else 0.0,
        "world_area": world_area,
        "useful_area": round(useful_area, 2),
        "useful_area_ratio": (useful_area / world_area) if world_area > 0 else 0.0,
        "avg_degree": round(avg_degree, 4),
        "max_degree": max_degree,
        "dead_end_ratio": round(dead_end_ratio, 4),
        "n_components": n_comp,
        "largest_component_ratio": round(largest_ratio, 4),
        "bridge_edges": n_bridges,
        "articulation_points": n_art,
        "orientation_entropy": round(orientation_entropy(rg.segments), 4),
        "gridness_score": round(gridness_score(rg.segments), 4),
        "corridor_score": round(corridor_score(rg.node_list), 4),
        "radial_score": round(radial_score(rg.node_list), 4),
        "partition_score": round(partition_score(g), 4),
        "community_score": round(community_score(g), 4),
        "graph_diameter_approx": round(diameter, 2),
        "avg_shortest_path_approx": round(avg_path, 2),
        "circuity_approx": round(circuity, 4),
    }


def render_validation_preview(
    rg: RoadGraph,
    *,
    world_size: tuple[int, int],
    map_id: str,
    validation_class: str,
    out_path: Path,
    failure_reasons: str = "",
    warnings: str = "",
    n_components: int = 1,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    wx, wy = world_size
    min_x, min_y, max_x, max_y = rg.bbox

    class_colors = {
        "valid": "#2c5282",
        "valid_partitioned": "#2b6cb0",
        "stress": "#d69e2e",
        "invalid": "#e53e3e",
    }
    road_color = class_colors.get(validation_class, "#2c5282")

    fig, ax = plt.subplots(figsize=(7, 6), dpi=100)
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    if validation_class == "valid_partitioned" and n_components > 1:
        g = rg.graph
        comp_ids: dict[int, int] = {}
        for ci, comp in enumerate(nx.connected_components(g)):
            for node in comp:
                comp_ids[node] = ci
        palette = plt.cm.tab10.colors  # type: ignore[attr-defined]
        for u, v in g.edges():
            c = palette[comp_ids.get(u, 0) % len(palette)]
            p1, p2 = rg.node_list[u], rg.node_list[v]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=c, linewidth=0.6, alpha=0.85)
    else:
        for a, b in rg.segments:
            ax.plot([a[0], b[0]], [a[1], b[1]], color=road_color, linewidth=0.6, alpha=0.85)

    if wx > 0 and wy > 0:
        ax.add_patch(Rectangle((0, 0), wx, wy, fill=False, edgecolor="#a0aec0", linestyle="--", linewidth=1.2))
    if max_x > min_x:
        ax.add_patch(
            Rectangle(
                (min_x, min_y),
                max_x - min_x,
                max_y - min_y,
                fill=False,
                edgecolor="#cbd5e0",
                linestyle=":",
                linewidth=0.8,
            )
        )

    title = f"{map_id} — {validation_class}"
    ax.set_title(title, fontsize=10, color=road_color if validation_class == "invalid" else "black")
    if failure_reasons:
        ax.text(0.02, 0.98, failure_reasons[:120], transform=ax.transAxes, fontsize=7, color="#e53e3e", va="top")
    elif warnings:
        ax.text(0.02, 0.98, warnings[:120], transform=ax.transAxes, fontsize=7, color="#d69e2e", va="top")

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def is_partition_marked(meta: dict[str, Any]) -> bool:
    flags = meta.get("topology_flags") or []
    if isinstance(flags, list):
        return "partitioned" in flags or "multi_component" in flags
    return False
