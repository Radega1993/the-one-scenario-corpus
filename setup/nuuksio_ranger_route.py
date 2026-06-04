"""NuuksioSparseTrails ranger patrol route validation and regeneration."""

from __future__ import annotations

import math
import random
from pathlib import Path

from family_routes import _nn_tour, generate_ranger_patrol_route
from map_geometry import (
    RoadGraph,
    SimTransform,
    dedupe_consecutive,
    graph_path_length,
    load_road_graph,
    parse_linestrings,
    parse_points,
    resolve_route_path_polyline,
    transform_points,
    vertex_distances,
    write_linestring_wkt,
)

PATROL_FILE = "A_ranger_patrol.wkt"
BORDER_EPS = 2.0
ORIGIN_EPS = 15.0
MIN_DIST_FROM_ORIGIN = 50.0
MAX_STOP_DIST_M = 150.0

def _nearest_poi_dist(stops: list[tuple[float, float]], poi_pts: list[tuple[float, float]]) -> float:
    if not stops or not poi_pts:
        return 0.0
    return min(
        min(math.hypot(s[0] - p[0], s[1] - p[1]) for p in poi_pts)
        for s in stops
    )

def _route_stops_sim(route_path: Path, roads_path: Path) -> list[tuple[float, float]]:
    raw = parse_linestrings(route_path)
    if not raw or not raw[0]:
        return []
    roads_lines = parse_linestrings(roads_path)
    tf = SimTransform.from_raw_lines(roads_lines)
    return [tf.raw_to_sim(x, y) for x, y in raw[0]]

def validate_ranger_route(
    rg: RoadGraph,
    route_path: Path,
    wx: float,
    wy: float,
    poi_pts: list[tuple[float, float]] | None = None,
    roads_path: Path | None = None,
) -> dict:
    raw = parse_linestrings(route_path)
    if not raw or not raw[0]:
        return {"route_file": route_path.name, "status": "FAIL", "notes": "empty"}
    if roads_path and roads_path.is_file():
        stops = _route_stops_sim(route_path, roads_path)
    else:
        stops = transform_points(raw[0])
    n_stops = len(stops)
    dists = vertex_distances(rg, stops)
    inside = all(0 <= x <= wx and 0 <= y <= wy for x, y in stops) if wx and wy else True
    at_origin = sum(1 for x, y in stops if math.hypot(x, y) < ORIGIN_EPS)
    on_border = sum(
        1 for x, y in stops
        if wx > 0 and (x <= BORDER_EPS or y <= BORDER_EPS or x >= wx - BORDER_EPS or y >= wy - BORDER_EPS)
    )
    resolved, failed = resolve_route_path_polyline(rg, stops)
    resolved_len = 0.0
    if len(resolved) >= 2:
        resolved_len = sum(
            math.hypot(resolved[i + 1][0] - resolved[i][0], resolved[i + 1][1] - resolved[i][1])
            for i in range(len(resolved) - 1)
        )
    g_len = graph_path_length(rg, stops)
    xs = [p[0] for p in stops]
    ys = [p[1] for p in stops]
    cov = ((max(xs) - min(xs)) * (max(ys) - min(ys))) / (wx * wy) * 100 if wx and wy and xs else 0
    max_d = max(dists) if dists else 0
    pct_over_50 = 100 * sum(1 for d in dists if d > 50) / n_stops if n_stops else 0
    near_poi_m = round(_nearest_poi_dist(stops, poi_pts or []), 1) if poi_pts else ""

    status = "PASS"
    notes: list[str] = []
    if not inside:
        status = "FAIL"
        notes.append("stops outside worldSize")
    if at_origin >= 2:
        status = "FAIL"
        notes.append(f"{at_origin} stops near (0,0)")
    elif at_origin == 1:
        if status == "PASS":
            status = "WARNING"
        notes.append("one stop at sim origin (SW bbox corner frame)")
    if failed:
        status = "FAIL"
        notes.append(f"{len(failed)} unresolved segment(s)")
    elif pct_over_50 > 40 or max_d > MAX_STOP_DIST_M:
        status = "FAIL"
        notes.append("stops too far from trail network")
    elif pct_over_50 > 5 or max_d > 120 or on_border > 0:
        if status == "PASS":
            status = "WARNING"
        if on_border:
            notes.append(f"{on_border} stop(s) near border")
        if max_d > 120:
            notes.append("some stops >120m from trail")
    if cov > 85:
        notes.append("high spatial coverage (unusual for rural patrol; OK if documented)")

    return {
        "route_file": route_path.name,
        "semantic_role": "ranger patrol on sparse trails",
        "n_stops": n_stops,
        "resolved_path_length_m": round(resolved_len, 1),
        "graph_stop_path_length_m": round(g_len, 1) if g_len else "",
        "n_unresolved_segments": len(failed),
        "stops_near_origin": at_origin,
        "stops_near_border": on_border,
        "within_world_size": inside,
        "max_stop_dist_to_trail_m": round(max_d, 2),
        "pct_stops_over_50m": round(pct_over_50, 2),
        "spatial_coverage_pct": round(cov, 2),
        "min_dist_to_any_poi_m": near_poi_m,
        "status": status,
        "notes": "; ".join(notes),
    }

def _refine_patrol_stops(rg: RoadGraph, stops: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Snap stops to trail graph; drop points far from network or near sim origin."""
    refined: list[tuple[float, float]] = []
    for p in stops:
        if math.hypot(p[0], p[1]) < MIN_DIST_FROM_ORIGIN:
            continue
        snapped = rg.snap_to_nearest_node(p[0], p[1])
        dists = vertex_distances(rg, [snapped])
        if dists and dists[0] <= MAX_STOP_DIST_M:
            refined.append(snapped)
    refined = dedupe_consecutive(refined)
    if len(refined) >= 4:
        return refined

    nodes = rg.node_list
    deg = dict(rg.graph.degree())
    ranked = sorted(range(len(nodes)), key=lambda i: deg.get(i, 0), reverse=True)
    seeds = [nodes[i] for i in ranked[:8] if math.hypot(nodes[i][0], nodes[i][1]) >= MIN_DIST_FROM_ORIGIN]
    if len(seeds) < 4:
        seeds = [p for p in nodes if math.hypot(p[0], p[1]) >= MIN_DIST_FROM_ORIGIN][:8]
    tour = _nn_tour(rg, seeds[:8])
    return dedupe_consecutive(tour)[:10]

def _graph_node_patrol(rg: RoadGraph, rng: random.Random) -> list[tuple[float, float]]:
    """Build patrol entirely from graph nodes (vertex_dist == 0 on trails)."""
    nodes = [p for p in rg.node_list if math.hypot(p[0], p[1]) >= MIN_DIST_FROM_ORIGIN]
    if len(nodes) < 4:
        nodes = list(rg.node_list)
    generated = generate_ranger_patrol_route(rg, rng)[PATROL_FILE]
    tour = _refine_patrol_stops(rg, generated)
    if tour and max(vertex_distances(rg, tour)) <= 1.0:
        return tour
    deg = dict(rg.graph.degree())
    ranked = sorted(range(len(rg.node_list)), key=lambda i: deg.get(i, 0), reverse=True)
    hubs = [
        rg.node_list[i]
        for i in ranked[:6]
        if math.hypot(rg.node_list[i][0], rg.node_list[i][1]) >= MIN_DIST_FROM_ORIGIN
    ]
    if len(nodes) >= 2:
        far_pair = max(
            ((nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i + 1, len(nodes))),
            key=lambda ab: math.hypot(ab[1][0] - ab[0][0], ab[1][1] - ab[0][1]),
        )
    else:
        far_pair = (nodes[0], nodes[0])
    seeds = dedupe_consecutive([far_pair[0], far_pair[1]] + hubs[:4])
    tour = _nn_tour(rg, seeds)[:10]
    return dedupe_consecutive(tour)

def regenerate_ranger_route(
    map_dir: Path,
    rng: random.Random,
    apply: bool,
) -> list[dict]:
    rg, roads_path, _ = load_road_graph("NuuksioSparseTrails")
    raw_lines = parse_linestrings(roads_path)
    corrections: list[dict] = []

    repaired = _graph_node_patrol(rg, rng)
    if apply:
        tf = SimTransform.from_raw_lines(raw_lines)
        raw_pts = [tf.sim_to_raw(x, y) for x, y in repaired]
        write_linestring_wkt(raw_pts, map_dir / PATROL_FILE)
    corrections.append(
        {
            "route_file": PATROL_FILE,
            "action": "regenerated" if apply else "would_regenerate",
            "n_stops": len(repaired),
            "semantic_role": "ranger patrol",
        }
    )
    return corrections

def load_all_poi_sim(map_dir: Path) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for name in ("A_homes.wkt", "A_offices.wkt", "A_meetingspots.wkt"):
        p = map_dir / name
        if p.is_file():
            pts.extend(transform_points(parse_points(p)))
    return pts