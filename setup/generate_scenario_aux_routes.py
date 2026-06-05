#!/usr/bin/env python3
"""
Generate scenario-specific auxiliary route WKT for R2, S1, S6 only.

Writes ONLY the 22 allowlisted files under scenarios/maps/wkt/.
Does not modify roads.wkt, POIs, metadata, or family semantic routes.
"""

from __future__ import annotations

import argparse
import math
import random
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from family_routes import _nn_tour, validate_stops  # noqa: E402
from map_geometry import (  # noqa: E402
    DATA_DIR,
    WKT_DIR,
    dedupe_consecutive,
    load_road_graph,
    parse_linestrings,
    repair_route_waypoints,
    sim_waypoints_to_raw,
    transform_points,
    write_linestring_wkt,
)

# Explicit allowlist — script refuses to write any other filename.
SCENARIO_ROUTE_SPECS: dict[str, list[tuple[str, str, int]]] = {
    # (filename, scenario_key, rng_seed)
    "NuuksioSparseTrails": [
        ("R2_village_1.wkt", "R2", 30),
        ("R2_village_2.wkt", "R2", 30),
        ("R2_village_3.wkt", "R2", 30),
        ("R2_inter_village.wkt", "R2", 30),
    ],
    "KallioCommunityCompact": [
        ("S1_community_1.wkt", "S1", 45),
        ("S1_community_2.wkt", "S1", 45),
        ("S1_community_3.wkt", "S1", 45),
        ("S1_community_4.wkt", "S1", 45),
        ("S1_bridge_route.wkt", "S1", 45),
        ("S6_family_1.wkt", "S6", 50),
        ("S6_family_2.wkt", "S6", 50),
        ("S6_family_3.wkt", "S6", 50),
        ("S6_family_4.wkt", "S6", 50),
        ("S6_family_5.wkt", "S6", 50),
        ("S6_family_6.wkt", "S6", 50),
        ("S6_family_7.wkt", "S6", 50),
        ("S6_family_8.wkt", "S6", 50),
        ("S6_family_9.wkt", "S6", 50),
        ("S6_family_10.wkt", "S6", 50),
        ("S6_family_11.wkt", "S6", 50),
        ("S6_family_12.wkt", "S6", 50),
        ("S6_shared_civic.wkt", "S6", 50),
    ],
}

ALLOWLIST: set[str] = {fname for specs in SCENARIO_ROUTE_SPECS.values() for fname, _, _ in specs}

SCENARIO_KEYS = {"R2", "S1", "S6"}

FAMILY_BY_SCENARIO = {
    "R2": "04_rural",
    "S1": "06_social",
    "S6": "06_social",
}


@dataclass
class RouteResult:
    map_name: str
    filename: str
    scenario: str
    n_stops: int
    valid: bool
    note: str
    action: str


def _centroid(nodes: list[tuple[float, float]]) -> tuple[float, float]:
    if not nodes:
        return (0.0, 0.0)
    return (sum(p[0] for p in nodes) / len(nodes), sum(p[1] for p in nodes) / len(nodes))


def _cluster_by_angle(
    nodes: list[tuple[float, float]], k: int
) -> list[list[tuple[float, float]]]:
    if not nodes:
        return [[] for _ in range(k)]
    cx, cy = _centroid(nodes)
    buckets: list[list[tuple[float, float]]] = [[] for _ in range(k)]
    for p in nodes:
        ang = math.atan2(p[1] - cy, p[0] - cx)
        idx = int((ang + math.pi) / (2 * math.pi) * k) % k
        buckets[idx].append(p)
    # Rebalance empty buckets
    non_empty = [b for b in buckets if b]
    if len(non_empty) < k:
        all_sorted = sorted(nodes, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
        buckets = [[] for _ in range(k)]
        for i, p in enumerate(all_sorted):
            buckets[i % k].append(p)
    return buckets


def _cluster_by_quadrant(
    nodes: list[tuple[float, float]], cx: float, cy: float
) -> list[list[tuple[float, float]]]:
    quads: list[list[tuple[float, float]]] = [[], [], [], []]
    for p in nodes:
        if p[0] <= cx and p[1] <= cy:
            quads[0].append(p)
        elif p[0] > cx and p[1] <= cy:
            quads[1].append(p)
        elif p[0] <= cx and p[1] > cy:
            quads[2].append(p)
        else:
            quads[3].append(p)
    for i, q in enumerate(quads):
        if not q:
            quads[i] = nodes[i::4] if nodes else []
    return quads


def _sample_stops(
    pool: list[tuple[float, float]], n: int, rng: random.Random
) -> list[tuple[float, float]]:
    if len(pool) <= n:
        return dedupe_consecutive(pool)
    step = max(1, len(pool) // n)
    seeds = dedupe_consecutive([pool[i] for i in range(0, len(pool), step)][:n])
    if len(seeds) < 2 and len(pool) >= 2:
        seeds = [pool[0], pool[-1]]
    return seeds


def _loop_on_pool(
    rg,
    pool: list[tuple[float, float]],
    rng: random.Random,
    family: str,
    *,
    n_stops: int = 7,
) -> list[tuple[float, float]]:
    if len(pool) < 2:
        pool = rg.node_list
    seeds = _sample_stops(pool, n_stops, rng)
    tour = _nn_tour(rg, seeds)
    return repair_route_waypoints(rg, [], tour, rng, family)


def _generate_r2_routes(rg, rng: random.Random) -> dict[str, list[tuple[float, float]]]:
    family = FAMILY_BY_SCENARIO["R2"]
    clusters = _cluster_by_angle(rg.node_list, 3)
    out: dict[str, list[tuple[float, float]]] = {}
    for i, cluster in enumerate(clusters, start=1):
        out[f"R2_village_{i}.wkt"] = _loop_on_pool(rg, cluster, rng, family, n_stops=8)

    centroids = [_centroid(c) for c in clusters if c]
    deg = dict(rg.graph.degree())
    hubs = sorted(range(len(rg.node_list)), key=lambda j: deg.get(j, 0), reverse=True)[:3]
    hub_pts = [rg.node_list[j] for j in hubs]
    inter_seeds = dedupe_consecutive(centroids + hub_pts)[:5]
    inter = _nn_tour(rg, inter_seeds)
    out["R2_inter_village.wkt"] = repair_route_waypoints(rg, [], inter, rng, family)
    return out


def _generate_s1_routes(
    rg, rng: random.Random, map_dir: Path
) -> dict[str, list[tuple[float, float]]]:
    family = FAMILY_BY_SCENARIO["S1"]
    cx, cy = _centroid(rg.node_list)
    quads = _cluster_by_quadrant(rg.node_list, cx, cy)
    out: dict[str, list[tuple[float, float]]] = {}
    for i, quad in enumerate(quads, start=1):
        out[f"S1_community_{i}.wkt"] = _loop_on_pool(rg, quad, rng, family, n_stops=7)

    guide_path = map_dir / "A_community_route.wkt"
    guide_sim: list[tuple[float, float]] = []
    if guide_path.is_file():
        raw = parse_linestrings(guide_path)
        if raw and raw[0]:
            guide_sim = transform_points(raw[0])
    if len(guide_sim) >= 2:
        bridge_seeds = guide_sim[:: max(1, len(guide_sim) // 6)][:8]
    else:
        bridge_seeds = sorted(rg.node_list, key=lambda p: p[0] + p[1])[:: max(1, len(rg.node_list) // 8)][:8]
    bridge = _nn_tour(rg, dedupe_consecutive(bridge_seeds))
    out["S1_bridge_route.wkt"] = repair_route_waypoints(rg, [], bridge, rng, family)
    return out


def _generate_s6_routes(rg, rng: random.Random) -> dict[str, list[tuple[float, float]]]:
    family = FAMILY_BY_SCENARIO["S6"]
    sectors = _cluster_by_angle(rg.node_list, 12)
    out: dict[str, list[tuple[float, float]]] = {}
    for i, sector in enumerate(sectors, start=1):
        out[f"S6_family_{i}.wkt"] = _loop_on_pool(rg, sector, rng, family, n_stops=5)

    cx, cy = _centroid(rg.node_list)
    inner = [p for p in rg.node_list if math.hypot(p[0] - cx, p[1] - cy) < 350]
    if len(inner) < 6:
        inner = rg.node_list
    civic_seeds = inner[:: max(1, len(inner) // 8)][:10]
    civic = _nn_tour(rg, dedupe_consecutive(civic_seeds))
    out["S6_shared_civic.wkt"] = repair_route_waypoints(rg, [], civic, rng, family)
    return out


def _routes_for_scenario(scenario: str, rg, rng: random.Random, map_dir: Path) -> dict[str, list[tuple[float, float]]]:
    if scenario == "R2":
        return _generate_r2_routes(rg, rng)
    if scenario == "S1":
        return _generate_s1_routes(rg, rng, map_dir)
    if scenario == "S6":
        return _generate_s6_routes(rg, rng)
    raise ValueError(f"Unknown scenario: {scenario}")


def _assert_allowlist(filenames: list[str]) -> None:
    bad = [f for f in filenames if f not in ALLOWLIST]
    if bad:
        raise RuntimeError(f"Refusing to write non-allowlisted files: {bad}")


def generate_for_map(
    map_name: str,
    *,
    scenario_filter: set[str] | None,
    apply: bool,
    only_missing: bool,
    force: bool,
) -> list[RouteResult]:
    if map_name not in SCENARIO_ROUTE_SPECS:
        return []

    rg, roads_path, _ = load_road_graph(map_name)
    raw_lines = parse_linestrings(roads_path)
    map_dir = WKT_DIR / map_name
    map_dir.mkdir(parents=True, exist_ok=True)

    specs = SCENARIO_ROUTE_SPECS[map_name]
    scenarios_in_map = {sk for _, sk, _ in specs}
    if scenario_filter:
        scenarios_in_map &= scenario_filter

    all_routes: dict[str, list[tuple[float, float]]] = {}
    for sk in sorted(scenarios_in_map):
        seed = next(s for _, s, sd in specs if s == sk)
        rng = random.Random(seed)
        generated = _routes_for_scenario(sk, rg, rng, map_dir)
        _assert_allowlist(list(generated.keys()))
        for fname, stops in generated.items():
            if any(s == sk for f, s, _ in specs if f == fname):
                all_routes[fname] = stops

    results: list[RouteResult] = []
    for fname, scenario, seed in specs:
        if scenario_filter and scenario not in scenario_filter:
            continue
        out_path = map_dir / fname
        if fname not in all_routes:
            continue

        if out_path.is_file() and only_missing and not force:
            results.append(
                RouteResult(map_name, fname, scenario, 0, True, "skipped_exists", "skip")
            )
            continue

        stops = all_routes[fname]
        family = FAMILY_BY_SCENARIO[scenario]
        ok, note = validate_stops(rg, stops, family)
        action = "dry-run"
        if apply:
            raw_pts = sim_waypoints_to_raw(stops, raw_lines, rg)
            write_linestring_wkt(raw_pts, out_path)
            action = "written"
        results.append(
            RouteResult(map_name, fname, scenario, len(stops), ok, note, action)
        )

    return results


def install_files(map_name: str, filenames: list[str]) -> int:
    src_dir = WKT_DIR / map_name
    dst_dir = DATA_DIR / map_name
    dst_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for fname in filenames:
        if fname not in ALLOWLIST:
            raise RuntimeError(f"install blocked: {fname} not in allowlist")
        sp = src_dir / fname
        if sp.is_file():
            shutil.copy2(sp, dst_dir / fname)
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate R2/S1/S6 auxiliary route WKT only.")
    ap.add_argument("--dry-run", action="store_true", help="Preview only (default if no --apply)")
    ap.add_argument("--apply", action="store_true", help="Write allowlisted WKT under maps/wkt/")
    ap.add_argument("--install", action="store_true", help="Copy written files to data/ (requires --apply)")
    ap.add_argument("--scenario", choices=sorted(SCENARIO_KEYS), action="append", default=None)
    ap.add_argument("--only-missing", action="store_true", default=True)
    ap.add_argument("--no-only-missing", action="store_false", dest="only_missing")
    ap.add_argument("--force", action="store_true", help="Overwrite existing allowlisted files")
    args = ap.parse_args()

    if not args.apply:
        args.dry_run = True

    scenario_filter = set(args.scenario) if args.scenario else None
    maps = list(SCENARIO_ROUTE_SPECS.keys())
    if scenario_filter:
        maps = [
            m
            for m in maps
            if any(sk in scenario_filter for _, sk, _ in SCENARIO_ROUTE_SPECS[m])
        ]

    all_results: list[RouteResult] = []
    for map_name in maps:
        rows = generate_for_map(
            map_name,
            scenario_filter=scenario_filter,
            apply=args.apply,
            only_missing=args.only_missing,
            force=args.force,
        )
        all_results.extend(rows)
        if args.apply and args.install:
            written = [r.filename for r in rows if r.action == "written"]
            if written:
                n = install_files(map_name, written)
                print(f"Installed {n} file(s) -> data/{map_name}/")

    mode = "apply" if args.apply else "dry-run"
    print(f"\nMode: {mode} | Maps: {', '.join(maps)}")
    print(f"{'Map':<22} {'File':<28} {'Stops':>5} {'Valid':>5} {'Action':<10} Note")
    print("-" * 90)
    for r in all_results:
        print(
            f"{r.map_name:<22} {r.filename:<28} {r.n_stops:>5} "
            f"{'yes' if r.valid else 'no':>5} {r.action:<10} {r.note}"
        )

    invalid = [r for r in all_results if not r.valid and r.action != "skip"]
    if invalid:
        print(f"\n*** {len(invalid)} route(s) failed validation ***")
        return 1

    written = sum(1 for r in all_results if r.action == "written")
    skipped = sum(1 for r in all_results if r.action == "skip")
    print(f"\nTotal: {len(all_results)} | written: {written} | skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
