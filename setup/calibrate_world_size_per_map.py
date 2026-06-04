#!/usr/bin/env python3
"""Per-map worldSize calibration from sim road span + occupancy margin tuning."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import re

_SETUP = Path(__file__).resolve().parent
_SCENARIOS = _SETUP.parent
_ANALYSIS = _SCENARIOS / "analysis"
_ANALYSIS_DATA = _SCENARIOS / "analysis" / "data"
WKT_DIR = _SCENARIOS / "maps" / "wkt"
LINESTRING_RE = re.compile(r"LINESTRING\s*\(([^)]+)\)", re.IGNORECASE)

ACTIVE_MAPS = [
    "HelsinkiDowntown",
    "KumpulaCampus",
    "ManhattanMidtownGrid",
    "NuuksioSparseTrails",
    "HelsinkiDisrupted",
    "KallioCommunityCompact",
]

def _roads_bbox_sim(
    roads_sim: list[list[tuple[float, float]]],
    margin: float,
) -> tuple[float, float, float, float] | None:
    xs: list[float] = []
    ys: list[float] = []
    for line in roads_sim:
        for x, y in line:
            xs.append(x)
            ys.append(y)
    if not xs:
        return None
    return (min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin)


def _map_bbox_cell_count(
    roads_sim: list[list[tuple[float, float]]],
    wx: float,
    wy: float,
    grid_size: int,
    margin: float,
) -> int:
    bbox = _roads_bbox_sim(roads_sim, margin)
    if bbox is None:
        return 0
    x0, y0, x1, y1 = bbox
    gs = grid_size
    cell_w = wx / gs
    cell_h = wy / gs
    count = 0
    for i in range(gs):
        cx = (i + 0.5) * cell_w
        if cx < x0 or cx > x1:
            continue
        for j in range(gs):
            cy = (j + 0.5) * cell_h
            if y0 <= cy <= y1:
                count += 1
    return count


def _parse_linestrings(path: Path) -> list[list[tuple[float, float]]]:
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


def _wkt_to_sim_coords(raw_lines: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    if not raw_lines:
        return []
    mirrored = [[(x, -y) for x, y in line] for line in raw_lines]
    xs = [x for line in mirrored for x, _ in line]
    ys = [y for line in mirrored for _, y in line]
    min_x, min_y = min(xs), min(ys)
    return [[(x - min_x, y - min_y) for x, y in line] for line in mirrored]


def sim_road_max(roads_path: Path) -> tuple[float, float]:
    sim = _wkt_to_sim_coords(_parse_linestrings(roads_path))
    xs = [x for line in sim for x, _ in line]
    ys = [y for line in sim for _, y in line]
    return max(xs), max(ys)


def sim_road_span(roads_path: Path) -> tuple[float, float]:
    return sim_road_max(roads_path)


def world_size_from_sim_roads(roads_path: Path, margin_m: float) -> tuple[int, int]:
    max_x, max_y = sim_road_max(roads_path)
    return int(math.ceil(max_x + margin_m)), int(math.ceil(max_y + margin_m))


def load_map_metadata(map_dir: Path) -> dict:
    meta_path = map_dir / "metadata.json"
    if meta_path.is_file():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return {}

DEFAULT_GRID_SIZE = 50
MIN_BBOX_WORLD_CELL_RATIO = 0.88
MARGIN_CANDIDATES = (20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80)

# map_name -> corpus_v1 pilot scenario (TP01)
PILOT_SCENARIOS: dict[str, str] = {
    "HelsinkiDowntown": "U1_CBD_Commuting_HelsinkiDowntown__TP01_Baseline",
    "KumpulaCampus": "C1_Campus_ClassChange__TP01_Baseline",
    "ManhattanMidtownGrid": "V1_TaxiLow_ManhattanMidtownGridMidtownGrid__TP01_Baseline",
    "NuuksioSparseTrails": "R1_Rural_SparseSPMM__TP01_Baseline",
    "HelsinkiDisrupted": "D1_ShelterHotspots_EmergencyMobility__TP01_Baseline",
    "KallioCommunityCompact": "S2_WeakCommunities_HighMixing__TP01_Baseline",
}

MAP_TO_FAMILY: dict[str, str] = {
    "HelsinkiDowntown": "01_urban",
    "KumpulaCampus": "02_campus",
    "ManhattanMidtownGrid": "03_vehicles",
    "NuuksioSparseTrails": "04_rural",
    "HelsinkiDisrupted": "05_disaster",
    "KallioCommunityCompact": "06_social",
}


def _cell_ratio_at_margin(
    roads_path: Path,
    margin_m: float,
    grid_size: int = DEFAULT_GRID_SIZE,
) -> tuple[float, int, int]:
    """Fraction of world grid cells whose centre lies inside roads_bbox (+margin)."""
    wx, wy = world_size_from_sim_roads(roads_path, margin_m)
    sim = _wkt_to_sim_coords(_parse_linestrings(roads_path))
    world_total = grid_size * grid_size
    bbox_total = _map_bbox_cell_count(sim, wx, wy, grid_size, margin_m)
    return bbox_total / world_total, wx, wy


def choose_margin(roads_path: Path, grid_size: int = DEFAULT_GRID_SIZE) -> tuple[float, int, int, float]:
    """Pick smallest margin with map_bbox_cells/world_cells >= threshold."""
    best_m = float(MARGIN_CANDIDATES[-1])
    best_ws = world_size_from_sim_roads(roads_path, best_m)
    best_ratio = 0.0
    for m in MARGIN_CANDIDATES:
        ratio, wx, wy = _cell_ratio_at_margin(roads_path, m, grid_size)
        if ratio >= MIN_BBOX_WORLD_CELL_RATIO:
            return float(m), wx, wy, ratio
        if ratio > best_ratio:
            best_ratio = ratio
            best_m = float(m)
            best_ws = (wx, wy)
    return best_m, best_ws[0], best_ws[1], best_ratio


def calibrate_map(map_name: str, grid_size: int = DEFAULT_GRID_SIZE) -> dict:
    roads = WKT_DIR / map_name / "roads.wkt"
    span_x, span_y = sim_road_span(roads)
    margin_m, wx, wy, cell_ratio = choose_margin(roads, grid_size)
    return {
        "map_name": map_name,
        "family": MAP_TO_FAMILY.get(map_name, ""),
        "sim_span_x_m": round(span_x, 1),
        "sim_span_y_m": round(span_y, 1),
        "occupancy_margin_m": margin_m,
        "world_size_x": wx,
        "world_size_y": wy,
        "map_bbox_cell_ratio": round(cell_ratio, 4),
        "pilot_scenario": PILOT_SCENARIOS.get(map_name, ""),
        "grid_size": grid_size,
    }


def apply_to_metadata(row: dict) -> None:
    map_dir = WKT_DIR / row["map_name"]
    meta_path = map_dir / "metadata.json"
    meta = load_map_metadata(map_dir)
    meta["world_size"] = [int(row["world_size_x"]), int(row["world_size_y"])]
    meta["occupancy_margin_m"] = float(row["occupancy_margin_m"])
    meta["world_size_policy"] = (
        f"sim_road_max_plus_{int(row['occupancy_margin_m'])}m_margin_per_axis"
    )
    meta["sim_road_span_m"] = [row["sim_span_x_m"], row["sim_span_y_m"]]
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def sync_family_map() -> None:
    """Update migrate_corpus_maps.FAMILY_MAP from metadata."""
    if str(_SETUP) not in sys.path:
        sys.path.insert(0, str(_SETUP))
    import migrate_corpus_maps as mcm  # noqa: WPS433

    for _fam, pol in mcm.FAMILY_MAP.items():
        meta_path = WKT_DIR / pol["map_name"] / "metadata.json"
        if meta_path.is_file():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            ws = meta.get("world_size", pol["world_size"])
            pol["world_size"] = (int(ws[0]), int(ws[1]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--grid-size", type=int, default=DEFAULT_GRID_SIZE)
    ap.add_argument("--apply", action="store_true", help="Write metadata.json + refresh FAMILY_MAP")
    ap.add_argument("--maps", default="", help="Comma-separated map names")
    args = ap.parse_args()

    names = [m.strip() for m in args.maps.split(",") if m.strip()] or list(ACTIVE_MAPS)
    rows = [calibrate_map(n, args.grid_size) for n in names]

    out_csv = _ANALYSIS_DATA / "world_size_calibration.csv"
    _ANALYSIS_DATA.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {out_csv}")
    print(
        f"{'map':<22} {'margin':>6} {'worldSize':>12} {'bbox/world cells':>16} pilot"
    )
    for r in rows:
        print(
            f"{r['map_name']:<22} {r['occupancy_margin_m']:>5.0f} "
            f"{r['world_size_x']:>5}x{r['world_size_y']:<5} "
            f"{r['map_bbox_cell_ratio']:>15.3f} {r['pilot_scenario']}"
        )

    if args.apply:
        for r in rows:
            apply_to_metadata(r)
        sync_family_map()
        print("\nApplied metadata.json + FAMILY_MAP sync")
    else:
        print("\n(dry-run; use --apply to update metadata)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
