#!/usr/bin/env python3
"""Conditional POI and route generation per map_asset_policy_v1.yaml."""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Any

import yaml

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_space_topology import build_road_graph  # noqa: E402

SCENARIOS_DIR = _SETUP.parent
DEFAULT_POLICY = SCENARIOS_DIR / "analysis" / "config" / "map_asset_policy_v1.yaml"


def load_asset_policy(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_POLICY
    with p.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("map_asset_policy_v1", data)


def _fmt(v: float) -> str:
    return f"{v:.6f}"


def write_points_wkt(points: list[tuple[float, float]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for x, y in points:
            f.write(f"POINT ({_fmt(x)} {_fmt(y)})\n\n")


def write_route_wkt(points: list[tuple[float, float]], path: Path) -> None:
    if len(points) < 2:
        return
    pts = ", ".join(f"{_fmt(x)} {_fmt(y)}" for x, y in points)
    with path.open("w", encoding="utf-8") as f:
        f.write(f"LINESTRING ({pts})\n")


def should_generate_pois(meta: dict[str, Any], policy: dict[str, Any]) -> bool:
    ap = policy.get("asset_policy", {})
    skip = ap.get("skip_assets_for", {})
    if meta.get("source_type") in skip.get("source_types", []):
        return False
    arch = meta.get("archetype", "")
    if arch in skip.get("archetypes", []):
        return False
    pois = ap.get("generate_pois", {})
    if arch in pois.get("only_for_archetypes", []):
        return True
    wdm = set(policy.get("wdm_capable_archetypes", []))
    return arch in wdm


def should_generate_routes(meta: dict[str, Any], policy: dict[str, Any]) -> bool:
    ap = policy.get("asset_policy", {})
    skip = ap.get("skip_assets_for", {})
    if meta.get("source_type") in skip.get("source_types", []):
        return False
    arch = meta.get("archetype", "")
    if arch in skip.get("archetypes", []):
        return False
    routes = ap.get("generate_routes", {})
    return arch in routes.get("only_for_archetypes", [])


def _sample_nodes(rg, n: int, rng: random.Random) -> list[tuple[float, float]]:
    nodes = list(rg.node_list)
    if not nodes:
        return []
    if len(nodes) <= n:
        return nodes
    return rng.sample(nodes, n)


def _longest_route_points(rg, rng: random.Random) -> list[tuple[float, float]]:
    import networkx as nx

    g = rg.graph
    if g.number_of_nodes() < 2:
        return []
    nodes = list(g.nodes())
    start = rng.choice(nodes)
    lengths = nx.single_source_dijkstra_path_length(g, start, weight="weight")
    far = max(lengths, key=lengths.get)
    path = nx.shortest_path(g, start, far, weight="weight")
    idx_to_coord = {i: rg.node_list[i] for i in range(len(rg.node_list))}
    return [idx_to_coord.get(n, rg.node_list[0]) for n in path if n in idx_to_coord]


def generate_assets_for_map(
    wkt_dir: Path,
    *,
    policy: dict[str, Any] | None = None,
    seed: int = 42,
) -> dict[str, bool]:
    """Generate POIs/routes when policy allows. Returns which assets were created."""
    policy = policy or load_asset_policy()
    meta_path = wkt_dir / "metadata.json"
    if not meta_path.is_file():
        return {}
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    roads = wkt_dir / "roads.wkt"
    if not roads.is_file():
        return {}

    rng = random.Random(seed)
    rg = build_road_graph(roads)
    created: dict[str, bool] = {}

    if should_generate_pois(meta, policy):
        homes = _sample_nodes(rg, 40, rng)
        offices = _sample_nodes(rg, 20, rng)
        meetings = _sample_nodes(rg, 15, rng)
        write_points_wkt(homes, wkt_dir / "A_homes.wkt")
        write_points_wkt(offices, wkt_dir / "A_offices.wkt")
        write_points_wkt(meetings, wkt_dir / "A_meetingspots.wkt")
        created["pois"] = True

    if should_generate_routes(meta, policy):
        route_pts = _longest_route_points(rg, rng)
        if len(route_pts) >= 2:
            arch = meta.get("archetype", "")
            if arch in ("sparse_trails", "rural_roads"):
                write_route_wkt(route_pts, wkt_dir / "A_ranger_patrol.wkt")
            elif arch == "industrial_disrupted":
                write_route_wkt(route_pts, wkt_dir / "A_emergency_route.wkt")
            elif arch in ("urban_grid", "bus_route_urban_suburban"):
                write_route_wkt(route_pts, wkt_dir / "A_bus.wkt")
                write_route_wkt(route_pts, wkt_dir / "A_vehicle_route.wkt")
            else:
                write_route_wkt(route_pts, wkt_dir / "A_vehicle_route.wkt")
            created["routes"] = True

    return created


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate conditional map assets")
    parser.add_argument("--wkt-dir", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    policy = load_asset_policy(args.policy)
    created = generate_assets_for_map(args.wkt_dir, policy=policy, seed=args.seed)
    print(f"Created assets: {created}")


if __name__ == "__main__":
    main()
