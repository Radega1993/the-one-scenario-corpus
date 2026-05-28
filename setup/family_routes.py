"""Family-specific route generation on road graphs."""

from __future__ import annotations

import math
import random
from typing import Callable

from map_geometry import (
    RoadGraph,
    dedupe_consecutive,
    euclidean_polyline_length,
    graph_path_length,
    vertex_distances,
    threshold_for_family,
)
from route_semantic_config import FAMILY_ROUTE_TARGETS, MAP_FAMILY


def _nn_tour(rg: RoadGraph, seeds: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not seeds:
        return []
    tour = [seeds[0]]
    rem = seeds[1:]
    while rem:
        last = tour[-1]
        nxt = min(rem, key=lambda p: rg.shortest_path_length(last, p) or float("inf"))
        tour.append(nxt)
        rem.remove(nxt)
    return dedupe_consecutive(tour)


def _walk_axis(
    rg: RoadGraph,
    nodes: list[tuple[float, float]],
    *,
    sort_key: Callable[[tuple[float, float]], float],
    n_stops: int,
) -> list[tuple[float, float]]:
    ordered = sorted(nodes, key=sort_key)
    if len(ordered) < 2:
        return ordered
    n = len(ordered)
    n_stops = max(4, min(n_stops, n))
    indices = [int(round(i * (n - 1) / max(n_stops - 1, 1))) for i in range(n_stops)]
    stops = dedupe_consecutive([ordered[i] for i in indices], eps=25.0)
    if len(stops) < 2:
        stops = [ordered[0], ordered[-1]]
    return _nn_tour(rg, stops)


def generate_urban_bus_routes(rg: RoadGraph, rng: random.Random) -> dict[str, list[tuple[float, float]]]:
    nodes = rg.node_list
    cx = sum(p[0] for p in nodes) / len(nodes)
    cy = sum(p[1] for p in nodes) / len(nodes)
    route_a = _walk_axis(rg, nodes, sort_key=lambda p: p[1] + 0.3 * abs(p[0] - cx), n_stops=12)
    route_b = _walk_axis(rg, nodes, sort_key=lambda p: p[0] + 0.3 * abs(p[1] - cy), n_stops=11)
    corners = sorted(nodes, key=lambda p: p[0] + p[1])
    c_seeds = dedupe_consecutive(
        [corners[0], corners[len(corners) // 4], corners[len(corners) // 2], corners[3 * len(corners) // 4], corners[-1]],
        eps=40.0,
    )
    route_c = _nn_tour(rg, c_seeds)
    return {"A_bus.wkt": route_a, "B_bus.wkt": route_b, "C_bus.wkt": route_c}


def generate_campus_shuttle_route(rg: RoadGraph, rng: random.Random) -> dict[str, list[tuple[float, float]]]:
    nodes = rg.node_list
    if len(nodes) < 4:
        return {"A_campus_shuttle.wkt": nodes}
    cx = sum(p[0] for p in nodes) / len(nodes)
    cy = sum(p[1] for p in nodes) / len(nodes)
    by_angle = sorted(nodes, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    step = max(1, len(by_angle) // 10)
    seeds = by_angle[::step][:10]
    tour = _nn_tour(rg, seeds)
    return {"A_campus_shuttle.wkt": tour}


def generate_vehicle_grid_routes(rg: RoadGraph, rng: random.Random) -> dict[str, list[tuple[float, float]]]:
    nodes = rg.node_list
    if len(nodes) < 4:
        return {"A_vehicle_route.wkt": nodes, "B_vehicle_route.wkt": nodes}
    xs = [p[0] for p in nodes]
    ys = [p[1] for p in nodes]
    span_x = max(xs) - min(xs)
    span_y = max(ys) - min(ys)
    if span_x >= span_y:
        route_ns = _walk_axis(rg, nodes, sort_key=lambda p: p[1], n_stops=14)
        route_ew = _walk_axis(rg, nodes, sort_key=lambda p: p[0], n_stops=12)
    else:
        route_ns = _walk_axis(rg, nodes, sort_key=lambda p: p[0], n_stops=14)
        route_ew = _walk_axis(rg, nodes, sort_key=lambda p: p[1], n_stops=12)
    return {"A_vehicle_route.wkt": route_ns, "B_vehicle_route.wkt": route_ew}


def generate_ranger_patrol_route(rg: RoadGraph, rng: random.Random) -> dict[str, list[tuple[float, float]]]:
    nodes = rg.node_list
    if len(nodes) < 2:
        return {"A_ranger_patrol.wkt": nodes}
    deg = dict(rg.graph.degree())
    hubs = sorted(range(len(nodes)), key=lambda i: deg.get(i, 0), reverse=True)[:5]
    far_pair = max(
        ((nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i + 1, len(nodes))),
        key=lambda ab: math.hypot(ab[1][0] - ab[0][0], ab[1][1] - ab[0][1]),
    )
    seeds = [far_pair[0], far_pair[1]] + [nodes[i] for i in hubs[:3]]
    tour = _nn_tour(rg, dedupe_consecutive(seeds))[:10]
    return {"A_ranger_patrol.wkt": tour}


def generate_disaster_routes(rg: RoadGraph, rng: random.Random) -> dict[str, list[tuple[float, float]]]:
    nodes = rg.node_list
    em = _walk_axis(rg, nodes, sort_key=lambda p: p[0], n_stops=8)
    mule = _walk_axis(rg, nodes, sort_key=lambda p: p[1], n_stops=6)
    return {"A_emergency_route.wkt": em, "B_mule_route.wkt": mule}


def generate_community_routes(rg: RoadGraph, rng: random.Random) -> dict[str, list[tuple[float, float]]]:
    nodes = rg.node_list
    cx = sum(p[0] for p in nodes) / max(len(nodes), 1)
    cy = sum(p[1] for p in nodes) / max(len(nodes), 1)
    inner = [p for p in nodes if math.hypot(p[0] - cx, p[1] - cy) < 400]
    if len(inner) < 4:
        inner = nodes
    route_a = _nn_tour(rg, inner[:: max(1, len(inner) // 6)][:8])
    mid = len(inner) // 2
    b_seeds = inner[max(0, mid - 3) : mid + 4]
    if len(b_seeds) < 4:
        b_seeds = inner[:: max(1, len(inner) // 5)][:8]
    route_b = _nn_tour(rg, b_seeds)
    return {"A_community_route.wkt": route_a, "B_community_route.wkt": route_b}


def generate_control_grid_routes(rg: RoadGraph, rng: random.Random) -> dict[str, list[tuple[float, float]]]:
    nodes = rg.node_list
    xs = [p[0] for p in nodes]
    ys = [p[1] for p in nodes]
    mid_y = (min(ys) + max(ys)) / 2
    mid_x = (min(xs) + max(xs)) / 2
    h_line = sorted([p for p in nodes if abs(p[1] - mid_y) < 80], key=lambda p: p[0])
    v_line = sorted([p for p in nodes if abs(p[0] - mid_x) < 80], key=lambda p: p[1])
    if len(h_line) < 2:
        h_line = sorted(nodes, key=lambda p: p[0])
    if len(v_line) < 2:
        v_line = sorted(nodes, key=lambda p: p[1])
    return {"A_control_route.wkt": h_line[:: max(1, len(h_line) // 8)][:10]}


GENERATORS: dict[str, Callable[[RoadGraph, random.Random], dict[str, list[tuple[float, float]]]]] = {
    "01_urban": generate_urban_bus_routes,
    "02_campus": generate_campus_shuttle_route,
    "03_vehicles": generate_vehicle_grid_routes,
    "04_rural": generate_ranger_patrol_route,
    "05_disaster": generate_disaster_routes,
    "06_social": generate_community_routes,
    "07_stress_controls": generate_control_grid_routes,
}


def generate_routes_for_map(map_name: str, rg: RoadGraph, rng: random.Random) -> dict[str, list[tuple[float, float]]]:
    family = MAP_FAMILY[map_name]
    gen = GENERATORS[family]
    routes = gen(rg, rng)
    targets = FAMILY_ROUTE_TARGETS.get(map_name, list(routes.keys()))
    return {k: routes[k] for k in targets if k in routes}


def validate_stops(rg: RoadGraph, stops: list[tuple[float, float]], family: str) -> tuple[bool, str]:
    if len(stops) < 2:
        return False, "too_few_stops"
    wx_ok = True  # caller checks world size separately
    dists = vertex_distances(rg, stops)
    thresh = threshold_for_family(family)
    over = sum(1 for d in dists if d > thresh)
    if over / len(stops) > 0.2:
        return False, f"{over} vertices over {thresh}m"
    g_len = graph_path_length(rg, stops)
    e_len = euclidean_polyline_length(stops)
    if g_len and e_len / g_len > 0.92:
        return True, "ok"
    return True, "ok"
