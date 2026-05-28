#!/usr/bin/env python3
"""
prepare_maps.py — Convert downloaded OSM GraphML to The ONE WKT format.

For each map defined in map_config.py:
  1. Load GraphML (osmnx) or generate synthetic grid
  2. Re-project to metre-based CRS (EPSG:3067 for Helsinki, EPSG:32618 for Manhattan)
  3. Extract largest connected component (The ONE requires a connected graph)
  4. Write roads.wkt (LINESTRING per edge)
  5. Generate POI files (POINT per location): homes, offices, meetingspots
  6. Generate bus route(s) as LINESTRING along longest path
  7. Write metadata JSON

Usage:
  python3 scenarios/setup/prepare_maps.py [--install]

  --install  Copy WKT directories into data/ for The ONE to find them.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import sys
from pathlib import Path

SCENARIOS_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = SCENARIOS_DIR / "maps" / "raw"
WKT_DIR = SCENARIOS_DIR / "maps" / "wkt"
DATA_DIR = SCENARIOS_DIR.parent / "data"

WORLD_SIZE_MARGIN_M = 200
SEED = 42

# ── Map definitions (duplicated from map_config.py to be self-contained) ─────

MAP_DEFS: dict[str, dict] = {
    "HelsinkiDowntown": {
        "bbox": (60.165, 60.178, 24.925, 24.955),
        "crs": "EPSG:3067",
        "family": "01_urban",
        "network_type": "drive",
        "description": "Helsinki city centre (Kluuvi / Kamppi / Esplanadi).",
        "poi_density": {"homes": 80, "offices": 40, "meetingspots": 25, "bus_routes": 3},
    },
    "KumpulaCampus": {
        "bbox": (60.2025, 60.2115, 24.958, 24.978),
        "crs": "EPSG:3067",
        "family": "02_campus",
        "network_type": "all",
        "description": "University of Helsinki Kumpula campus.",
        "poi_density": {"homes": 30, "offices": 20, "meetingspots": 15, "bus_routes": 1},
    },
    "ManhattanMidtownGrid": {
        "bbox": (40.748, 40.766, -73.993, -73.968),
        "crs": "EPSG:32618",
        "family": "03_vehicles",
        "network_type": "drive",
        "description": "Midtown Manhattan (34th-59th St).",
        "poi_density": {"homes": 60, "offices": 50, "meetingspots": 30, "bus_routes": 2},
    },
    "NuuksioSparseTrails": {
        "bbox": (60.310, 60.335, 24.490, 24.535),
        "crs": "EPSG:3067",
        "family": "04_rural",
        "network_type": "all",
        "description": "Nuuksio National Park (sparse trails).",
        "poi_density": {"homes": 10, "offices": 5, "meetingspots": 8, "bus_routes": 1},
    },
    "HelsinkiDisrupted": {
        "bbox": (60.180, 60.196, 24.965, 24.995),
        "crs": "EPSG:3067",
        "family": "05_disaster",
        "network_type": "all",
        "description": "Kalasatama / Soernainen industrial harbour.",
        "poi_density": {"homes": 40, "offices": 25, "meetingspots": 15, "bus_routes": 2},
    },
    "KallioCommunityCompact": {
        "bbox": (60.179, 60.189, 24.938, 24.957),
        "crs": "EPSG:3067",
        "family": "06_social",
        "network_type": "all",
        "description": "Kallio residential neighbourhood.",
        "poi_density": {"homes": 70, "offices": 20, "meetingspots": 30, "bus_routes": 2},
    },
    "ControlCompactGrid": {
        "synthetic": True,
        "grid_size": (12, 10),
        "block_m": 150,
        "margin_m": 100,
        "crs": "local",
        "family": "07_stress_controls",
        "description": "Synthetic rectangular grid (12x10 blocks, 150 m spacing).",
        "poi_density": {"homes": 50, "offices": 30, "meetingspots": 20, "bus_routes": 1},
    },
}


# ── WKT writers ──────────────────────────────────────────────────────────────

def _fmt(v: float) -> str:
    return f"{v:.6f}"


def write_roads_wkt(edges: list[list[tuple[float, float]]], path: Path) -> None:
    with open(path, "w") as f:
        for coords in edges:
            pts = ", ".join(f"{_fmt(x)} {_fmt(y)}" for x, y in coords)
            f.write(f"LINESTRING ({pts})\n\n")


def write_points_wkt(points: list[tuple[float, float]], path: Path) -> None:
    with open(path, "w") as f:
        for x, y in points:
            f.write(f"POINT ({_fmt(x)} {_fmt(y)})\n\n")


def write_bus_route_wkt(route_points: list[tuple[float, float]], path: Path) -> None:
    if len(route_points) < 2:
        return
    pts = ", ".join(f"{_fmt(x)} {_fmt(y)}" for x, y in route_points)
    with open(path, "w") as f:
        f.write(f"LINESTRING ({pts})\n")


# ── Synthetic grid generator ────────────────────────────────────────────────

def _generate_synthetic_grid(cfg: dict) -> tuple[list[list[tuple[float, float]]], list[tuple[float, float]]]:
    cols, rows = cfg["grid_size"]
    block = cfg["block_m"]
    margin = cfg.get("margin_m", 100)
    edges: list[list[tuple[float, float]]] = []
    nodes: list[tuple[float, float]] = []
    for r in range(rows + 1):
        row_pts = [(margin + c * block, margin + r * block) for c in range(cols + 1)]
        edges.append(row_pts)
        nodes.extend(row_pts)
    for c in range(cols + 1):
        col_pts = [(margin + c * block, margin + r * block) for r in range(rows + 1)]
        edges.append(col_pts)
    return edges, list(set(nodes))


# ── OSM graph processing ────────────────────────────────────────────────────

def _process_osm_map(name: str, cfg: dict) -> dict:
    import networkx as nx
    import osmnx as ox

    graphml = RAW_DIR / f"{name}.graphml"
    if not graphml.exists():
        raise FileNotFoundError(f"Run download_maps.sh first: missing {graphml}")

    G = ox.load_graphml(str(graphml))
    target_crs = cfg["crs"]
    G_proj = ox.project_graph(G, to_crs=target_crs)

    if not nx.is_weakly_connected(G_proj):
        components = sorted(nx.weakly_connected_components(G_proj), key=len, reverse=True)
        print(f"  Graph has {len(components)} components; keeping largest ({len(components[0])} nodes)")
        G_proj = G_proj.subgraph(components[0]).copy()

    nodes_gdf, edges_gdf = ox.graph_to_gdfs(G_proj)

    all_edges: list[list[tuple[float, float]]] = []
    for _, row in edges_gdf.iterrows():
        geom = row.geometry
        coords = [(c[0], c[1]) for c in geom.coords]
        if len(coords) >= 2:
            all_edges.append(coords)

    all_node_coords = [(row.geometry.x, row.geometry.y) for _, row in nodes_gdf.iterrows()]

    xs = [c[0] for c in all_node_coords]
    ys = [c[1] for c in all_node_coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max_x - min_x
    span_y = max_y - min_y
    world_x = math.ceil(span_x + 2 * WORLD_SIZE_MARGIN_M)
    world_y = math.ceil(span_y + 2 * WORLD_SIZE_MARGIN_M)

    return {
        "edges": all_edges,
        "node_coords": all_node_coords,
        "min_x": min_x, "max_x": max_x,
        "min_y": min_y, "max_y": max_y,
        "world_size": (world_x, world_y),
        "n_nodes": len(all_node_coords),
        "n_edges": len(all_edges),
    }


# ── POI generation ──────────────────────────────────────────────────────────

def _load_osm_pois(name: str) -> dict[str, list[dict]]:
    pois_path = RAW_DIR / f"{name}_pois.geojson"
    if pois_path.exists():
        with open(pois_path) as f:
            return json.load(f)
    return {}


def _generate_pois_at_nodes(
    node_coords: list[tuple[float, float]],
    count: int,
    rng: random.Random,
) -> list[tuple[float, float]]:
    """Pick POI locations from actual road-network nodes.

    The ONE resolves POI coordinates via exact HashMap lookup
    (SimMap.getNodeByCoord), so every POINT must match a MapNode
    coordinate precisely — no offset or jitter is allowed.
    """
    if not node_coords:
        return []
    if count >= len(node_coords):
        return list(node_coords)
    return rng.sample(node_coords, count)


def _snap_to_nearest_node(
    pt: tuple[float, float],
    node_coords: list[tuple[float, float]],
) -> tuple[float, float]:
    """Return the node coordinate closest to pt (Euclidean distance)."""
    best = node_coords[0]
    best_d = (pt[0] - best[0]) ** 2 + (pt[1] - best[1]) ** 2
    for nc in node_coords[1:]:
        d = (pt[0] - nc[0]) ** 2 + (pt[1] - nc[1]) ** 2
        if d < best_d:
            best, best_d = nc, d
    return best


def _reproject_and_snap_pois(
    raw_pts: list[dict],
    target_crs: str,
    node_coords: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    """Re-project lon/lat POI points to the target CRS, then snap each
    to the nearest road-network node so The ONE's exact-coord lookup works."""
    from pyproj import Transformer

    if target_crs == "local":
        projected = [(p["x"], p["y"]) for p in raw_pts]
    else:
        tr = Transformer.from_crs("EPSG:4326", target_crs, always_xy=True)
        projected = [tr.transform(p["x"], p["y"]) for p in raw_pts]

    seen: set[tuple[float, float]] = set()
    snapped: list[tuple[float, float]] = []
    for pt in projected:
        nearest = _snap_to_nearest_node(pt, node_coords)
        if nearest not in seen:
            seen.add(nearest)
            snapped.append(nearest)
    return snapped


def _generate_bus_route(
    roads_path: Path,
    rng: random.Random,
    *,
    family: str = "01_urban",
    n_stops: int = 12,
) -> list[tuple[float, float]]:
    """Graph-coherent bus waypoints in map CRS (via map_geometry)."""
    _setup = Path(__file__).resolve().parent
    if str(_setup) not in sys.path:
        sys.path.insert(0, str(_setup))
    from map_geometry import (  # noqa: WPS433
        RoadGraph,
        generate_bus_route_on_graph,
        parse_linestrings,
        sim_waypoints_to_raw,
    )

    raw_roads = parse_linestrings(roads_path)
    rg = RoadGraph.from_roads_wkt(roads_path)
    sim_stops = generate_bus_route_on_graph(rg, rng, n_stops=n_stops, family=family)
    return sim_waypoints_to_raw(sim_stops, raw_roads, rg)


# ── Main processing ─────────────────────────────────────────────────────────

def process_all(install: bool = False) -> None:
    rng = random.Random(SEED)
    results: dict[str, dict] = {}

    for name, cfg in MAP_DEFS.items():
        print(f"\n{'='*60}")
        print(f"Processing: {name}")
        print(f"{'='*60}")

        out_dir = WKT_DIR / name
        out_dir.mkdir(parents=True, exist_ok=True)

        if cfg.get("synthetic"):
            edges, nodes = _generate_synthetic_grid(cfg)
            cols, rows = cfg["grid_size"]
            block = cfg["block_m"]
            margin = cfg.get("margin_m", 100)
            world_x = 2 * margin + cols * block
            world_y = 2 * margin + rows * block
            info = {
                "edges": edges,
                "node_coords": nodes,
                "min_x": margin, "max_x": margin + cols * block,
                "min_y": margin, "max_y": margin + rows * block,
                "world_size": (world_x, world_y),
                "n_nodes": len(nodes),
                "n_edges": len(edges),
            }
        else:
            info = _process_osm_map(name, cfg)

        write_roads_wkt(info["edges"], out_dir / "roads.wkt")
        print(f"  roads.wkt: {info['n_edges']} segments, {info['n_nodes']} nodes")
        print(f"  worldSize: {info['world_size']}")

        target_crs = cfg.get("crs", "local")
        density = cfg.get("poi_density", {})
        osm_pois = _load_osm_pois(name)

        for cat in ("homes", "offices", "meetingspots"):
            want = density.get(cat, 20)
            osm_raw = osm_pois.get(cat, [])
            if osm_raw and not cfg.get("synthetic"):
                snapped = _reproject_and_snap_pois(osm_raw, target_crs, info["node_coords"])
                pts = snapped[:want] if len(snapped) >= want else list(snapped)
                if len(pts) < want:
                    used = set(pts)
                    remaining = [n for n in info["node_coords"] if n not in used]
                    pts.extend(_generate_pois_at_nodes(remaining, want - len(pts), rng))
            else:
                pts = _generate_pois_at_nodes(info["node_coords"], want, rng)
            write_points_wkt(pts, out_dir / f"A_{cat}.wkt")
            print(f"  A_{cat}.wkt: {len(pts)} points (snapped to road nodes)")

        n_bus = density.get("bus_routes", 1)
        roads_path = out_dir / "roads.wkt"
        for i in range(n_bus):
            route = _generate_bus_route(
                roads_path, rng, family=cfg.get("family", ""), n_stops=12
            )
            suffix = f"A_bus.wkt" if i == 0 else f"{'ABCDEFGH'[min(i,7)]}_bus.wkt"
            write_bus_route_wkt(route, out_dir / suffix)
            print(f"  {suffix}: {len(route)} stops")

        meta = {
            "name": name,
            "family": cfg.get("family", ""),
            "description": cfg.get("description", ""),
            "crs": target_crs,
            "source": "synthetic" if cfg.get("synthetic") else "osm",
            "world_size": list(info["world_size"]),
            "bbox_m": [info["min_x"], info["min_y"], info["max_x"], info["max_y"]],
            "n_road_segments": info["n_edges"],
            "n_nodes": info["n_nodes"],
        }
        with open(out_dir / "metadata.json", "w") as f:
            json.dump(meta, f, indent=2)

        results[name] = meta

    if install:
        _install_maps()

    print(f"\n{'='*60}")
    print("All maps processed.")
    for n, m in results.items():
        print(f"  {n}: {m['n_road_segments']} edges, worldSize={m['world_size']}")


def _install_maps() -> None:
    """Copy WKT map directories into the repo data/ folder for The ONE."""
    print("\n--- Installing maps to data/ ---")
    for name in MAP_DEFS:
        src = WKT_DIR / name
        dst = DATA_DIR / name
        if not src.exists():
            print(f"  [SKIP] {name}: WKT not yet generated")
            continue
        if dst.exists():
            print(f"  [UPDATE] {name}: removing old {dst}")
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"  [OK] {name} -> {dst}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert OSM GraphML to The ONE WKT.")
    ap.add_argument("--install", action="store_true", help="Copy WKT to data/ after processing")
    args = ap.parse_args()
    process_all(install=args.install)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
