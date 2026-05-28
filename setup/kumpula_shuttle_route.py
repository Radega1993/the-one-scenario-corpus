"""KumpulaCampus shuttle route validation and regeneration."""

from __future__ import annotations

import math
import random
from pathlib import Path

from family_routes import _nn_tour, generate_campus_shuttle_route
from map_geometry import (
    RoadGraph,
    dedupe_consecutive,
    graph_path_length,
    load_road_graph,
    parse_linestrings,
    repair_route_waypoints,
    resolve_route_path_polyline,
    sim_waypoints_to_raw,
    vertex_distances,
    write_linestring_wkt,
    wkt_to_sim_coords,
)

SHUTTLE_FILE = "A_campus_shuttle.wkt"
BORDER_EPS = 2.0
ORIGIN_EPS = 15.0
MIN_DIST_FROM_ORIGIN = 80.0


def generate_kumpula_shuttle_route(rg: RoadGraph, rng: random.Random) -> list[tuple[float, float]]:
    """Campus shuttle: hub nodes + angular spread, avoid origin artifact."""
    nodes = rg.node_list
    if len(nodes) < 4:
        return nodes

    deg = dict(rg.graph.degree())
    by_deg = sorted(range(len(nodes)), key=lambda i: deg.get(i, 0), reverse=True)
    hubs = [nodes[i] for i in by_deg[: max(4, len(by_deg) // 20)]]

    cx = sum(p[0] for p in nodes) / len(nodes)
    cy = sum(p[1] for p in nodes) / len(nodes)
    by_angle = sorted(nodes, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    step = max(1, len(by_angle) // 12)
    angular = by_angle[::step][:12]

    seeds = dedupe_consecutive(hubs[:4] + angular[:8], eps=30.0)
    seeds = [
        p
        for p in seeds
        if math.hypot(p[0], p[1]) > ORIGIN_EPS
        or math.hypot(p[0] - cx, p[1] - cy) > 100
    ]
    if len(seeds) < 4:
        seeds = [p for p in nodes if math.hypot(p[0], p[1]) > ORIGIN_EPS][:10]
    if len(seeds) < 2:
        seeds = nodes[: min(10, len(nodes))]

    tour = _nn_tour(rg, seeds[:10])
    tour = [p for p in dedupe_consecutive(tour) if math.hypot(p[0], p[1]) >= MIN_DIST_FROM_ORIGIN]
    if len(tour) < 4:
        tour = [p for p in nodes if math.hypot(p[0], p[1]) >= MIN_DIST_FROM_ORIGIN][:10]
    return dedupe_consecutive(tour) if tour else nodes[: min(8, len(nodes))]


def validate_shuttle_route(
    rg: RoadGraph,
    route_path: Path,
    wx: float,
    wy: float,
) -> dict:
    raw = parse_linestrings(route_path)
    if not raw or not raw[0]:
        return {"route_file": route_path.name, "status": "FAIL", "notes": "empty"}
    stops = wkt_to_sim_coords(raw)[0]
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
        notes.append("one stop at sim origin (SW bbox corner / campus entrance frame)")
    if failed:
        status = "FAIL"
        notes.append(f"{len(failed)} unresolved segment(s)")
    elif pct_over_50 > 25 or max_d > 120:
        if status != "FAIL":
            status = "FAIL"
        notes.append("stops too far from network")
    elif pct_over_50 > 5 or max_d > 50 or on_border > 0:
        if status == "PASS":
            status = "WARNING"
        if on_border:
            notes.append(f"{on_border} stop(s) near worldSize border")
        if max_d > 50:
            notes.append("some stops >50m from path")

    return {
        "route_file": route_path.name,
        "semantic_role": "campus shuttle (optional figure asset)",
        "n_stops": n_stops,
        "resolved_path_length_m": round(resolved_len, 1),
        "graph_stop_path_length_m": round(g_len, 1) if g_len else "",
        "n_unresolved_segments": len(failed),
        "stops_near_origin": at_origin,
        "stops_near_border": on_border,
        "within_world_size": inside,
        "max_stop_dist_to_road_m": round(max_d, 2),
        "pct_stops_over_50m": round(pct_over_50, 2),
        "spatial_coverage_pct": round(cov, 2),
        "status": status,
        "notes": "; ".join(notes),
    }


def regenerate_shuttle(
    map_dir: Path,
    rng: random.Random,
    apply: bool,
) -> list[dict]:
    rg, roads_path, _ = load_road_graph("KumpulaCampus")
    raw_lines = parse_linestrings(roads_path)
    stops = generate_kumpula_shuttle_route(rg, rng)
    stops = repair_route_waypoints(rg, [], stops, rng, "02_campus")
    stops = [p for p in stops if math.hypot(p[0], p[1]) >= MIN_DIST_FROM_ORIGIN]
    if len(stops) < 4:
        stops = generate_kumpula_shuttle_route(rg, rng)
        stops = [p for p in stops if math.hypot(p[0], p[1]) >= MIN_DIST_FROM_ORIGIN]
    if apply:
        raw_pts = sim_waypoints_to_raw(stops, raw_lines, rg)
        write_linestring_wkt(raw_pts, map_dir / SHUTTLE_FILE)
    return [
        {
            "route_file": SHUTTLE_FILE,
            "action": "regenerated" if apply else "would_regenerate",
            "n_stops": len(stops),
            "semantic_role": "campus shuttle loop",
        }
    ]
