"""Generate local route WKT files for map-aware mobility repair (S1, S6, D1, R2)."""

from __future__ import annotations

import math
import random
from pathlib import Path

from family_routes import _nn_tour
from map_geometry import (
    RoadGraph,
    dedupe_consecutive,
    parse_linestrings,
    parse_points,
    sim_waypoints_to_raw,
    transform_points,
    write_linestring_wkt,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

def _local_loop_from_seed(
    rg: RoadGraph,
    seed: tuple[float, float],
    *,
    radius_m: float = 120.0,
    n_stops: int = 6,
) -> list[tuple[float, float]]:
    """Short loop on road graph near seed (sim coords)."""
    nodes = rg.node_list
    if not nodes:
        return [seed]
    nearby = [
        p
        for p in nodes
        if math.hypot(p[0] - seed[0], p[1] - seed[1]) <= radius_m
    ]
    if len(nearby) < 3:
        nearby = sorted(nodes, key=lambda p: math.hypot(p[0] - seed[0], p[1] - seed[1]))[:8]
    step = max(1, len(nearby) // n_stops)
    seeds = dedupe_consecutive(nearby[::step][:n_stops], eps=20.0)
    if len(seeds) < 2:
        seeds = [rg.snap_to_nearest_node(seed[0], seed[1]), seed]
    tour = _nn_tour(rg, seeds)
    return tour if len(tour) >= 2 else [seed, rg.snap_to_nearest_node(seed[0], seed[1])]

def _path_through_seeds(rg: RoadGraph, seeds: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if len(seeds) < 2:
        return seeds
    out: list[tuple[float, float]] = []
    for i in range(len(seeds) - 1):
        seg = rg.path_coords(seeds[i], seeds[i + 1])
        if not out:
            out.extend(seg)
        else:
            out.extend(seg[1:])
    return dedupe_consecutive(out)

def write_sim_route_raw(
    map_data_dir: Path,
    filename: str,
    sim_pts: list[tuple[float, float]],
    roads_path: Path,
) -> Path:
    raw_lines = parse_linestrings(roads_path)
    rg = RoadGraph.from_roads_wkt(roads_path)
    raw_pts = sim_waypoints_to_raw(sim_pts, raw_lines, rg)
    out = map_data_dir / filename
    write_linestring_wkt(raw_pts, out)
    return out

def _rg_for_map(map_dir: Path) -> tuple[RoadGraph, Path]:
    roads = map_dir / "roads.wkt"
    return RoadGraph.from_roads_wkt(roads), roads

def generate_s1_routes(map_dir: Path, rng: random.Random) -> dict[str, Path]:
    rg, roads = _rg_for_map(map_dir)
    centers = [(219, 306), (1239, 306), (219, 1223), (1239, 1223)]
    out: dict[str, Path] = {}
    for i, c in enumerate(centers, start=1):
        loop = _local_loop_from_seed(rg, c, radius_m=100.0, n_stops=7)
        out[f"S1_community_{i}.wkt"] = write_sim_route_raw(
            map_dir, f"S1_community_{i}.wkt", loop, roads
        )
    mid = (729, 764)
    bridge_seeds = [centers[0], mid, centers[1], mid, centers[2], mid, centers[3]]
    bridge = _path_through_seeds(rg, [rg.snap_to_nearest_node(x, y) for x, y in bridge_seeds])
    out["S1_bridge_route.wkt"] = write_sim_route_raw(map_dir, "S1_bridge_route.wkt", bridge, roads)
    return out

def generate_s6_routes(map_dir: Path, rng: random.Random) -> dict[str, Path]:
    rg, roads = _rg_for_map(map_dir)
    centers = [
        (194, 275),
        (535, 245),
        (875, 367),
        (1215, 275),
        (170, 764),
        (583, 856),
        (923, 795),
        (1264, 734),
        (219, 1223),
        (559, 1284),
        (899, 1193),
        (1239, 1254),
    ]
    out: dict[str, Path] = {}
    for i, c in enumerate(centers, start=1):
        loop = _local_loop_from_seed(rg, c, radius_m=70.0, n_stops=5)
        out[f"S6_family_{i}.wkt"] = write_sim_route_raw(
            map_dir, f"S6_family_{i}.wkt", loop, roads
        )
    civic = transform_points(parse_points(map_dir / "A_meetingspots.wkt"))
    if len(civic) >= 2:
        civic_route = _path_through_seeds(rg, civic[:3])
        out["S6_shared_civic.wkt"] = write_sim_route_raw(
            map_dir, "S6_shared_civic.wkt", civic_route, roads
        )
    return out

def generate_r2_routes(map_dir: Path, rng: random.Random) -> dict[str, Path]:
    rg, roads = _rg_for_map(map_dir)
    villages = [(456, 471), (1595, 471), (1025, 1649)]
    out: dict[str, Path] = {}
    for i, c in enumerate(villages, start=1):
        loop = _local_loop_from_seed(rg, c, radius_m=180.0, n_stops=6)
        out[f"R2_village_{i}.wkt"] = write_sim_route_raw(
            map_dir, f"R2_village_{i}.wkt", loop, roads
        )
    inter = _path_through_seeds(rg, [rg.snap_to_nearest_node(x, y) for x, y in villages])
    out["R2_inter_village.wkt"] = write_sim_route_raw(
        map_dir, "R2_inter_village.wkt", inter, roads
    )
    return out

def generate_all_repair_routes(apply: bool = True) -> dict[str, dict[str, Path]]:
    rng = random.Random(42)
    results: dict[str, dict[str, Path]] = {}
    if apply:
        results["KallioCommunityCompact"] = {
            **generate_s1_routes(REPO_ROOT / "data" / "KallioCommunityCompact", rng),
            **generate_s6_routes(REPO_ROOT / "data" / "KallioCommunityCompact", rng),
        }
        results["NuuksioSparseTrails"] = generate_r2_routes(
            REPO_ROOT / "data" / "NuuksioSparseTrails", rng
        )
    return results

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    r = generate_all_repair_routes(apply=args.apply)
    for m, files in r.items():
        print(m, len(files), "routes")