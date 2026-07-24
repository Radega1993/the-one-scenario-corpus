"""Synthetic road-graph generators for map_space_v1 (metric coordinates)."""

from __future__ import annotations

import math
import random
from typing import Any

Coord = tuple[float, float]
Edge = list[Coord]


def _fmt(v: float) -> str:
    return f"{v:.6f}"


def write_roads_wkt(edges: list[Edge], path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for coords in edges:
            if len(coords) < 2:
                continue
            pts = ", ".join(f"{_fmt(x)} {_fmt(y)}" for x, y in coords)
            f.write(f"LINESTRING ({pts})\n\n")


def _edge(a: Coord, b: Coord) -> Edge:
    return [a, b]


def _add_edge(edges: list[Edge], a: Coord, b: Coord) -> None:
    if a != b:
        edges.append(_edge(a, b))


def _jitter(pt: Coord, amount: float, rng: random.Random) -> Coord:
    if amount <= 0:
        return pt
    return (
        pt[0] + rng.uniform(-amount, amount),
        pt[1] + rng.uniform(-amount, amount),
    )


def generate_grid(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    rows = int(params["grid_rows"])
    cols = int(params["grid_cols"])
    block = float(params["block_size_m"])
    diagonal = bool(params.get("diagonal_links", False))
    margin = 50.0
    edges: list[Edge] = []
    nodes: dict[tuple[int, int], Coord] = {}
    for r in range(rows + 1):
        for c in range(cols + 1):
            nodes[(r, c)] = (margin + c * block, margin + r * block)
    for r in range(rows + 1):
        for c in range(cols):
            _add_edge(edges, nodes[(r, c)], nodes[(r, c + 1)])
    for r in range(rows):
        for c in range(cols + 1):
            _add_edge(edges, nodes[(r, c)], nodes[(r + 1, c)])
    if diagonal:
        for r in range(rows):
            for c in range(cols):
                if rng.random() < 0.25:
                    _add_edge(edges, nodes[(r, c)], nodes[(r + 1, c + 1)])
    span_x = margin * 2 + cols * block
    span_y = margin * 2 + rows * block
    return edges, {"span_x": span_x, "span_y": span_y, "n_nodes": len(nodes)}


def generate_jittered_grid(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    rows = int(params["grid_rows"])
    cols = int(params["grid_cols"])
    block = float(params["block_size_m"])
    jitter_m = float(params.get("jitter_m", 0))
    diagonal = bool(params.get("diagonal_links", False))
    margin = 50.0
    edges: list[Edge] = []
    nodes: dict[tuple[int, int], Coord] = {}
    for r in range(rows + 1):
        for c in range(cols + 1):
            base = (margin + c * block, margin + r * block)
            nodes[(r, c)] = _jitter(base, jitter_m, rng)
    for r in range(rows + 1):
        for c in range(cols):
            _add_edge(edges, nodes[(r, c)], nodes[(r, c + 1)])
    for r in range(rows):
        for c in range(cols + 1):
            _add_edge(edges, nodes[(r, c)], nodes[(r + 1, c)])
    if diagonal:
        for r in range(rows):
            for c in range(cols):
                if rng.random() < 0.2:
                    _add_edge(edges, nodes[(r, c)], nodes[(r + 1, c + 1)])
    xs = [p[0] for p in nodes.values()]
    ys = [p[1] for p in nodes.values()]
    return edges, {
        "span_x": max(xs) - min(xs),
        "span_y": max(ys) - min(ys),
        "n_nodes": len(nodes),
        "jitter_m": jitter_m,
    }


def generate_radial_city(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    n_rings = int(params["n_rings"])
    n_spokes = int(params["n_spokes"])
    ring_spacing = float(params["ring_spacing_m"])
    noise = float(params.get("radial_noise_m", 0))
    cx, cy = 400.0, 400.0
    edges: list[Edge] = []
    ring_nodes: list[list[Coord]] = []
    for ring in range(1, n_rings + 1):
        radius = ring * ring_spacing
        pts: list[Coord] = []
        for i in range(n_spokes):
            angle = 2 * math.pi * i / n_spokes
            pt = (
                cx + radius * math.cos(angle) + rng.uniform(-noise, noise),
                cy + radius * math.sin(angle) + rng.uniform(-noise, noise),
            )
            pts.append(pt)
        ring_nodes.append(pts)
        for i in range(n_spokes):
            _add_edge(edges, pts[i], pts[(i + 1) % n_spokes])
    for i in range(n_spokes):
        for ring in range(n_rings - 1):
            _add_edge(edges, ring_nodes[ring][i], ring_nodes[ring + 1][i])
    _add_edge(edges, (cx, cy), ring_nodes[0][0])
    all_pts = [p for ring in ring_nodes for p in ring] + [(cx, cy)]
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    return edges, {"span_x": max(xs) - min(xs), "span_y": max(ys) - min(ys), "n_nodes": len(all_pts)}


def generate_hub_and_spoke(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    n_hubs = max(1, int(params["n_hubs"]))
    spokes_per_hub = max(10, int(params["spokes_per_hub"]))
    hub_spacing = float(params["hub_spacing_m"])
    spoke_length = max(80.0, float(params["spoke_length_m"]))
    margin = 80.0
    edges: list[Edge] = []
    hubs: list[Coord] = []
    base_x, base_y = margin, margin
    for h in range(n_hubs):
        hubs.append((base_x + h * hub_spacing, base_y))
    all_nodes: list[Coord] = list(hubs)
    for hub in hubs:
        spoke_ends: list[Coord] = []
        for i in range(spokes_per_hub):
            angle = 2 * math.pi * i / spokes_per_hub + rng.uniform(-0.08, 0.08)
            end = (hub[0] + spoke_length * math.cos(angle), hub[1] + spoke_length * math.sin(angle))
            spoke_ends.append(end)
            all_nodes.append(end)
            _add_edge(edges, hub, end)
            mid = (
                hub[0] + 0.55 * spoke_length * math.cos(angle),
                hub[1] + 0.55 * spoke_length * math.sin(angle),
            )
            all_nodes.append(mid)
            _add_edge(edges, hub, mid)
            _add_edge(edges, mid, end)
        for i in range(spokes_per_hub):
            _add_edge(edges, spoke_ends[i], spoke_ends[(i + 1) % spokes_per_hub])
    if n_hubs > 1:
        for i in range(n_hubs - 1):
            _add_edge(edges, hubs[i], hubs[i + 1])
    xs = [p[0] for p in all_nodes]
    ys = [p[1] for p in all_nodes]
    return edges, {
        "span_x": max(xs) - min(xs) + 2 * margin,
        "span_y": max(ys) - min(ys) + 2 * margin,
        "n_nodes": len(all_nodes),
    }


def generate_corridor(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    length_m = float(params["length_m"])
    width_m = float(params["width_m"])
    branch_prob = float(params.get("branch_prob", 0.0))
    branch_length = float(params.get("branch_length_m", 200))
    branch_count_max = int(params.get("branch_count_max", 4))
    margin = 50.0
    edges: list[Edge] = []
    main_y = margin + width_m / 2
    n_main = max(6, int(length_m / 120))
    main_pts = [(margin + i * (length_m / (n_main - 1)), main_y) for i in range(n_main)]
    for i in range(len(main_pts) - 1):
        _add_edge(edges, main_pts[i], main_pts[i + 1])
    branches = 0
    min_branches = min(branch_count_max, max(2, int(branch_prob * len(main_pts))))
    for pt in main_pts[1:-1]:
        if branches >= branch_count_max:
            break
        take = branches < min_branches or rng.random() < branch_prob
        if take:
            direction = 1 if rng.random() < 0.5 else -1
            end = (pt[0], pt[1] + direction * branch_length)
            _add_edge(edges, pt, end)
            branches += 1
    all_pts = main_pts + [
        (pt[0], pt[1] + branch_length) for pt in main_pts[1:-1]
    ]
    return edges, {
        "span_x": length_m + 2 * margin,
        "span_y": width_m + 2 * margin + branch_length,
        "n_nodes": len(main_pts) + branches,
    }


def generate_tree_trails(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    branch_factor = max(2, int(params["branch_factor"]))
    depth = max(4, int(params["depth"]))
    edge_length = float(params.get("edge_length_m", 120))
    trail_jitter = float(params.get("trail_jitter_m", 0))
    margin = 80.0
    edges: list[Edge] = []
    nodes: list[Coord] = [(margin, margin)]

    def _expand(parent: Coord, d: int, angle: float) -> None:
        if d >= depth:
            return
        spread = math.pi / 3
        for i in range(branch_factor):
            a = angle - spread / 2 + i * spread / max(branch_factor - 1, 1)
            end = _jitter(
                (parent[0] + edge_length * math.cos(a), parent[1] + edge_length * math.sin(a)),
                trail_jitter,
                rng,
            )
            nodes.append(end)
            _add_edge(edges, parent, end)
            _expand(end, d + 1, a)

    _expand(nodes[0], 0, math.pi / 4)
    xs = [p[0] for p in nodes]
    ys = [p[1] for p in nodes]
    return edges, {"span_x": max(xs) - min(xs), "span_y": max(ys) - min(ys), "n_nodes": len(nodes)}


def generate_clustered_communities(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    n_clusters = max(2, int(params["n_clusters"]))
    nodes_per_cluster = max(8, int(params["nodes_per_cluster"]))
    intra_density = float(params["intra_density"])
    inter_gap = max(120.0, float(params["inter_gap_m"]))
    inter_bridges = max(1, int(params.get("inter_bridge_count", 1)))
    margin = 60.0
    edges: list[Edge] = []
    cluster_centers: list[Coord] = []
    cluster_nodes: list[list[Coord]] = []
    cols = max(2, int(math.ceil(math.sqrt(n_clusters))))
    for i in range(n_clusters):
        row, col = divmod(i, cols)
        center = (margin + col * inter_gap, margin + row * inter_gap)
        cluster_centers.append(center)
        local: list[Coord] = []
        for _ in range(nodes_per_cluster):
            local.append(
                (
                    center[0] + rng.uniform(-inter_gap * 0.12, inter_gap * 0.12),
                    center[1] + rng.uniform(-inter_gap * 0.12, inter_gap * 0.12),
                )
            )
        cluster_nodes.append(local)
        for node in local:
            _add_edge(edges, center, node)
        for a in range(len(local)):
            for b in range(a + 1, len(local)):
                if rng.random() < intra_density:
                    _add_edge(edges, local[a], local[b])
    for i in range(n_clusters - 1):
        for _ in range(inter_bridges):
            a = rng.choice(cluster_nodes[i])
            b = rng.choice(cluster_nodes[i + 1])
            _add_edge(edges, a, b)
        _add_edge(edges, cluster_centers[i], cluster_centers[i + 1])
    all_nodes = [n for part in cluster_nodes for n in part] + cluster_centers
    xs = [p[0] for p in all_nodes]
    ys = [p[1] for p in all_nodes]
    return edges, {
        "span_x": max(xs) - min(xs) + 2 * margin,
        "span_y": max(ys) - min(ys) + 2 * margin,
        "n_nodes": len(all_nodes),
        "topology_flags": ["clustered"],
    }


def generate_partitioned_bridge(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    n_partitions = int(params["n_partitions"])
    nodes_per = int(params["nodes_per_partition"])
    intra_density = float(params["intra_density"])
    bridges_per_pair = int(params["bridges_per_pair"])
    gap = 350.0
    edges: list[Edge] = []
    partition_nodes: list[list[Coord]] = []
    for p in range(n_partitions):
        base_x = 100 + p * gap
        local = [(base_x + rng.uniform(0, 80), 100 + rng.uniform(0, 80)) for _ in range(nodes_per)]
        partition_nodes.append(local)
        for a in range(len(local)):
            for b in range(a + 1, len(local)):
                if rng.random() < intra_density:
                    _add_edge(edges, local[a], local[b])
    bridges_per_pair = max(1, int(params["bridges_per_pair"]))
    for p in range(n_partitions - 1):
        for _ in range(bridges_per_pair):
            a = rng.choice(partition_nodes[p])
            b = rng.choice(partition_nodes[p + 1])
            _add_edge(edges, a, b)
        _add_edge(edges, partition_nodes[p][0], partition_nodes[p + 1][0])
    all_nodes = [n for part in partition_nodes for n in part]
    xs = [n[0] for n in all_nodes]
    ys = [n[1] for n in all_nodes]
    return edges, {
        "span_x": max(xs) - min(xs),
        "span_y": max(ys) - min(ys),
        "n_nodes": len(all_nodes),
        "n_partitions": n_partitions,
        "topology_flags": ["partitioned"],
    }


def generate_disrupted_grid(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    base_params = {
        "grid_rows": params["grid_rows"],
        "grid_cols": params["grid_cols"],
        "block_size_m": params["block_size_m"],
        "diagonal_links": False,
    }
    edges, info = generate_grid(base_params, rng)
    removal_rate = float(params["removal_rate"])
    removal_mode = params.get("removal_mode", "random")
    min_keep = max(20, int(params.get("min_edges_keep", 20)))
    n_remove = max(1, int(len(edges) * removal_rate))
    n_remove = min(n_remove, max(0, len(edges) - min_keep))
    if removal_mode == "articulation_bias" and len(edges) > n_remove:
        # remove edges from the middle of the grid preferentially
        mid = len(edges) // 2
        indices = list(range(max(0, mid - n_remove), min(len(edges), mid + n_remove)))
        edges = [e for i, e in enumerate(edges) if i not in set(indices[:n_remove])]
    else:
        rng.shuffle(edges)
        edges = edges[n_remove:]
    return edges, {**info, "removal_rate": removal_rate}


def generate_sparse_rural(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    n_nodes = int(params["n_nodes"])
    radius = float(params["connection_radius_m"])
    long_edge_prob = float(params.get("long_edge_prob", 0.2))
    long_mult = float(params.get("long_edge_multiplier", 3.0))
    pos_noise = float(params.get("pos_noise_m", 0))
    margin = 100.0
    span = margin * 2 + math.sqrt(n_nodes) * radius * 1.5
    nodes = [
        _jitter((rng.uniform(margin, span), rng.uniform(margin, span)), pos_noise, rng)
        for _ in range(n_nodes)
    ]
    edges: list[Edge] = []
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            dist = math.hypot(nodes[i][0] - nodes[j][0], nodes[i][1] - nodes[j][1])
            threshold = radius * (long_mult if rng.random() < long_edge_prob else 1.0)
            if dist <= threshold:
                _add_edge(edges, nodes[i], nodes[j])
    if len(edges) < max(2, n_nodes // 2) and n_nodes >= 2:
        for i in range(n_nodes - 1):
            _add_edge(edges, nodes[i], nodes[i + 1])
        for i in range(0, n_nodes - 2, 2):
            _add_edge(edges, nodes[i], nodes[i + 2])
    xs = [p[0] for p in nodes]
    ys = [p[1] for p in nodes]
    return edges, {"span_x": max(xs) - min(xs), "span_y": max(ys) - min(ys), "n_nodes": n_nodes}


def generate_conference_event_compact(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    """Compact venue layout inspired by INFOCOM-style contact traces."""
    hall_count = max(2, int(params["hall_count"]))
    rooms_per_hall = max(4, int(params["rooms_per_hall"]))
    corridor_w = max(12.0, float(params["corridor_width_m"]))
    room_spacing = max(15.0, float(params["room_spacing_m"]))
    inter_gap = max(20.0, float(params["inter_hall_gap_m"]))
    margin = 40.0
    edges: list[Edge] = []
    nodes: list[Coord] = []
    hall_spines: list[tuple[Coord, Coord]] = []
    x_cursor = margin
    for h in range(hall_count):
        cy = margin + corridor_w / 2
        left = (x_cursor, cy)
        right = (x_cursor + rooms_per_hall * room_spacing, cy)
        nodes.extend([left, right])
        _add_edge(edges, left, right)
        hall_spines.append((left, right))
        for r in range(rooms_per_hall):
            rx = x_cursor + r * room_spacing + room_spacing / 2
            top = (rx, cy + corridor_w / 2 + room_spacing / 3)
            bot = (rx, cy - corridor_w / 2 - room_spacing / 3)
            nodes.extend([top, bot])
            _add_edge(edges, top, (rx, cy))
            _add_edge(edges, bot, (rx, cy))
            if r > 0:
                prev_rx = x_cursor + (r - 1) * room_spacing + room_spacing / 2
                _add_edge(edges, (prev_rx, cy), (rx, cy))
        if h > 0:
            prev_right = hall_spines[h - 1][1]
            _add_edge(edges, prev_right, left)
        x_cursor += rooms_per_hall * room_spacing + inter_gap
    xs = [p[0] for p in nodes]
    ys = [p[1] for p in nodes]
    return edges, {
        "span_x": max(xs) - min(xs) + margin,
        "span_y": max(ys) - min(ys) + margin,
        "n_nodes": len(nodes),
        "topology_flags": ["compact_event"],
    }


def generate_campus_compact(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    n_buildings = int(params["n_buildings"])
    spacing = float(params["building_spacing_m"])
    ring_roads = int(params["ring_roads"])
    path_density = float(params["path_density"])
    quad_size = float(params["quad_size_m"])
    margin = 60.0
    edges: list[Edge] = []
    cols = max(2, int(math.ceil(math.sqrt(n_buildings))))
    building_nodes: list[Coord] = []
    for i in range(n_buildings):
        row, col = divmod(i, cols)
        pt = (margin + col * spacing, margin + row * spacing)
        building_nodes.append(pt)
    min_paths = max(4, int(len(building_nodes) * path_density))
    added = 0
    for a in range(len(building_nodes)):
        for b in range(a + 1, len(building_nodes)):
            if rng.random() < path_density or added < min_paths:
                _add_edge(edges, building_nodes[a], building_nodes[b])
                added += 1
    cx = margin + (cols - 1) * spacing / 2
    cy = margin + (math.ceil(n_buildings / cols) - 1) * spacing / 2
    for ring in range(ring_roads):
        radius = quad_size / 2 + ring * spacing * 0.3
        ring_pts: list[Coord] = []
        for k in range(8):
            angle = 2 * math.pi * k / 8
            ring_pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        for k in range(len(ring_pts)):
            _add_edge(edges, ring_pts[k], ring_pts[(k + 1) % len(ring_pts)])
            if k < len(building_nodes):
                _add_edge(edges, ring_pts[k], building_nodes[k % len(building_nodes)])
    all_nodes = building_nodes + [(cx, cy)]
    xs = [p[0] for p in all_nodes]
    ys = [p[1] for p in all_nodes]
    return edges, {"span_x": max(xs) - min(xs) + margin, "span_y": max(ys) - min(ys) + margin, "n_nodes": len(all_nodes)}


def generate_bus_route_corridor(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    length_m = float(params["corridor_length_m"])
    width_m = float(params["corridor_width_m"])
    n_stops = int(params["n_stops"])
    feeder_prob = float(params.get("feeder_branch_prob", 0.0))
    n_lanes = int(params.get("n_parallel_lanes", 1))
    margin = 50.0
    edges: list[Edge] = []
    main_y = margin + width_m / 2
    n_pts = max(n_stops + 2, 6)
    main_pts = [(margin + i * (length_m / (n_pts - 1)), main_y) for i in range(n_pts)]
    for i in range(len(main_pts) - 1):
        _add_edge(edges, main_pts[i], main_pts[i + 1])
    for lane in range(1, n_lanes):
        offset_y = main_y + lane * (width_m / max(n_lanes, 1))
        lane_pts = [(p[0], offset_y) for p in main_pts]
        for i in range(len(lane_pts) - 1):
            _add_edge(edges, lane_pts[i], lane_pts[i + 1])
        for i in range(0, len(main_pts), max(1, len(main_pts) // n_stops)):
            _add_edge(edges, main_pts[i], lane_pts[i])
    for i in range(1, n_stops + 1):
        idx = min(len(main_pts) - 2, int(i * (len(main_pts) - 1) / n_stops))
        stop = main_pts[idx]
        if rng.random() < feeder_prob:
            direction = 1 if rng.random() < 0.5 else -1
            feeder = (stop[0], stop[1] + direction * width_m * 0.8)
            _add_edge(edges, stop, feeder)
    xs = [p[0] for p in main_pts]
    ys = [p[1] for p in main_pts]
    return edges, {
        "span_x": length_m + 2 * margin,
        "span_y": width_m + 2 * margin,
        "n_nodes": len(main_pts) + n_stops,
    }


def generate_multi_component_with_bridges(params: dict[str, Any], rng: random.Random) -> tuple[list[Edge], dict[str, Any]]:
    n_components = int(params["n_components"])
    nodes_per = int(params["nodes_per_component"])
    intra_density = float(params["intra_density"])
    n_bridges = int(params["n_bridges"])
    bridge_length = float(params.get("bridge_length_m", 150))
    gap = 280.0
    edges: list[Edge] = []
    components: list[list[Coord]] = []
    for c in range(n_components):
        base_x = 80 + c * gap
        local = [(base_x + rng.uniform(0, 60), 80 + rng.uniform(0, 60)) for _ in range(nodes_per)]
        components.append(local)
        for a in range(len(local)):
            for b in range(a + 1, len(local)):
                if rng.random() < intra_density:
                    _add_edge(edges, local[a], local[b])
    for _ in range(n_bridges):
        c1, c2 = rng.sample(range(n_components), 2)
        a = rng.choice(components[c1])
        b = (
            components[c2][0][0] + bridge_length,
            components[c2][0][1],
        )
        components[c2].append(b)
        _add_edge(edges, a, b)
    all_nodes = [n for comp in components for n in comp]
    xs = [n[0] for n in all_nodes]
    ys = [n[1] for n in all_nodes]
    return edges, {
        "span_x": max(xs) - min(xs),
        "span_y": max(ys) - min(ys),
        "n_nodes": len(all_nodes),
        "n_components": n_components,
        "topology_flags": ["partitioned", "multi_component"],
    }


GENERATORS: dict[str, Any] = {
    "grid": generate_grid,
    "jittered_grid": generate_jittered_grid,
    "radial_city": generate_radial_city,
    "hub_and_spoke": generate_hub_and_spoke,
    "corridor": generate_corridor,
    "tree_trails": generate_tree_trails,
    "clustered_communities": generate_clustered_communities,
    "partitioned_bridge": generate_partitioned_bridge,
    "disrupted_grid": generate_disrupted_grid,
    "sparse_rural": generate_sparse_rural,
    "multi_component_with_bridges": generate_multi_component_with_bridges,
    "conference_event_compact": generate_conference_event_compact,
    "campus_compact": generate_campus_compact,
    "bus_route_corridor": generate_bus_route_corridor,
}


def sample_discrete_params(spec: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Pick one value per discrete parameter key."""
    out: dict[str, Any] = {}
    for key, values in spec.get("discrete_parameters", {}).items():
        if isinstance(values, list) and values:
            out[key] = rng.choice(values)
    return out
