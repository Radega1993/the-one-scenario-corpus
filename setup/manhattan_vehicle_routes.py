"""ManhattanMidtownGrid vehicle route validation and regeneration."""

from __future__ import annotations

import math
import random
from pathlib import Path

from family_routes import generate_vehicle_grid_routes
from map_geometry import (
    RoadGraph,
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

ROUTE_ROLES = {
    "A_vehicle_route.wkt": "longitudinal (N-S dominant)",
    "B_vehicle_route.wkt": "transversal (E-W dominant)",
}

BORDER_EPS = 2.0
ORIGIN_EPS = 15.0
MIN_DIST_FROM_ORIGIN = 80.0

def _route_separation(stops_a: list[tuple[float, float]], stops_b: list[tuple[float, float]]) -> float:
    """Mean min distance between stop sets (differentiation metric)."""
    if not stops_a or not stops_b:
        return 0.0
    dists = [min(math.hypot(a[0] - b[0], a[1] - b[1]) for b in stops_b) for a in stops_a]
    return sum(dists) / len(dists)

def validate_vehicle_route(
    rg: RoadGraph,
    route_path: Path,
    wx: float,
    wy: float,
    other_stops: list[tuple[float, float]] | None = None,
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
    sep_m = round(_route_separation(stops, other_stops), 1) if other_stops else ""

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
        notes.append("one stop at sim origin (bbox SW corner frame)")
    if failed:
        status = "FAIL"
        notes.append(f"{len(failed)} unresolved segment(s)")
    elif pct_over_50 > 25 or max_d > 150:
        status = "FAIL"
        notes.append("stops too far from network")
    elif pct_over_50 > 5 or max_d > 50 or on_border > 0:
        if status == "PASS":
            status = "WARNING"
        if on_border:
            notes.append(f"{on_border} stop(s) near border")
        if max_d > 50:
            notes.append("some stops >50m from road")
    if other_stops and _route_separation(stops, other_stops) < 80:
        notes.append("low separation from other route")

    return {
        "route_file": route_path.name,
        "semantic_role": ROUTE_ROLES.get(route_path.name, ""),
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
        "mean_separation_from_other_route_m": sep_m,
        "status": status,
        "notes": "; ".join(notes),
    }

def regenerate_vehicle_routes(
    map_dir: Path,
    rng: random.Random,
    apply: bool,
) -> list[dict]:
    rg, roads_path, _ = load_road_graph("ManhattanMidtownGrid")
    raw_lines = parse_linestrings(roads_path)
    routes = generate_vehicle_grid_routes(rg, rng)
    corrections: list[dict] = []

    for fname, stops in routes.items():
        repaired = repair_route_waypoints(rg, [], stops, rng, "03_vehicles")
        repaired = [p for p in repaired if math.hypot(p[0], p[1]) >= MIN_DIST_FROM_ORIGIN]
        if apply:
            raw_pts = sim_waypoints_to_raw(repaired, raw_lines, rg)
            write_linestring_wkt(raw_pts, map_dir / fname)
        corrections.append(
            {
                "route_file": fname,
                "action": "regenerated" if apply else "would_regenerate",
                "n_stops": len(repaired),
                "semantic_role": ROUTE_ROLES.get(fname, ""),
            }
        )
    return corrections