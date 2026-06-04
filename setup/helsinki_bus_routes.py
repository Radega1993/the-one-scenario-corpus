"""HelsinkiDowntown bus route validation and regeneration."""

from __future__ import annotations

import random
from pathlib import Path

from family_routes import generate_urban_bus_routes
from map_geometry import (
    RoadGraph,
    graph_path_length,
    load_road_graph,
    parse_linestrings,
    repair_route_waypoints,
    resolve_route_path_polyline,
    sim_waypoints_to_raw,
    vertex_distances,
    world_size_from_metadata,
    write_linestring_wkt,
    wkt_to_sim_coords,
)

ROUTE_ROLES = {
    "A_bus.wkt": "CBD / north-south main axis",
    "B_bus.wkt": "East-west cross axis",
    "C_bus.wkt": "Peripheral loop / edge coverage",
}

def validate_bus_route_extended(
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
    resolved, failed = resolve_route_path_polyline(rg, stops)
    resolved_len = 0.0
    if len(resolved) >= 2:
        resolved_len = sum(
            ((resolved[i + 1][0] - resolved[i][0]) ** 2 + (resolved[i + 1][1] - resolved[i][1]) ** 2) ** 0.5
            for i in range(len(resolved) - 1)
        )
    g_len = graph_path_length(rg, stops)
    xs = [p[0] for p in stops]
    ys = [p[1] for p in stops]
    span_x = max(xs) - min(xs) if xs else 0
    span_y = max(ys) - min(ys) if ys else 0
    cov = (span_x * span_y) / (wx * wy) * 100 if wx and wy else 0

    max_d = max(dists) if dists else 0
    pct_over_50 = 100 * sum(1 for d in dists if d > 50) / n_stops if n_stops else 0

    status = "PASS"
    notes: list[str] = []
    if not inside:
        status = "FAIL"
        notes.append("stops outside worldSize")
    if failed:
        status = "FAIL"
        notes.append(f"{len(failed)} unresolved segment(s)")
    elif pct_over_50 > 20 or max_d > 150:
        status = "FAIL"
        notes.append("too many stops far from road")
    elif pct_over_50 > 5 or max_d > 50:
        status = "WARNING"
        notes.append("some stops >50m from road")

    return {
        "route_file": route_path.name,
        "semantic_role": ROUTE_ROLES.get(route_path.name, ""),
        "n_stops": n_stops,
        "resolved_path_length_m": round(resolved_len, 1),
        "graph_stop_path_length_m": round(g_len, 1) if g_len else "",
        "n_unresolved_segments": len(failed),
        "within_world_size": inside,
        "max_stop_dist_to_road_m": round(max_d, 2),
        "pct_stops_over_50m": round(pct_over_50, 2),
        "spatial_coverage_pct": round(cov, 2),
        "status": status,
        "notes": "; ".join(notes),
    }

def regenerate_helsinki_bus_routes(
    map_dir: Path,
    rng: random.Random,
    apply: bool,
) -> tuple[dict[str, list[tuple[float, float]]], list[dict]]:
    rg, roads_path, _ = load_road_graph("HelsinkiDowntown")
    raw_lines = parse_linestrings(roads_path)
    routes = generate_urban_bus_routes(rg, rng)
    corrections: list[dict] = []

    for fname, stops in routes.items():
        repaired = repair_route_waypoints(rg, [], stops, rng, "01_urban")
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
    return routes, corrections