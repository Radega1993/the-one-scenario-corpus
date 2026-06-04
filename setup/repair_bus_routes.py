#!/usr/bin/env python3
"""Repair *_bus.wkt routes to be graph-coherent (reproducible, with backup)."""

from __future__ import annotations

import argparse
import csv
import random
import shutil
import sys
from datetime import datetime
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import (  # noqa: E402
    ACTIVE_MAPS,
    ANALYSIS_DATA,
    DATA_DIR,
    WKT_DIR,
    generate_bus_route_on_graph,
    list_route_wkt_files,
    repair_route_waypoints,
    load_road_graph,
    parse_linestrings,
    sim_waypoints_to_raw,
    write_linestring_wkt,
    wkt_to_sim_coords,
    SCENARIOS_DIR,
)

REPORTS_DIR = SCENARIOS_DIR / "analysis" / "reports" / "maps"

from validate_bus_routes import validate_one  # noqa: E402

def load_validation_rows() -> list[dict]:
    p = ANALYSIS_DATA / "bus_route_validation.csv"
    if not p.is_file():
        return []
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_repair_plan(rows: list[dict], repairs: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Bus route repair plan",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Routes to repair",
        "",
        "| Map | Route | Before | Strategy | Auto | Scenarios affected |",
        "|-----|-------|--------|----------|------|-------------------|",
    ]
    for r in repairs:
        lines.append(
            f"| {r['map_name']} | {r['route_file']} | {r['before_status']} | "
            f"{r['strategy']} | {r['auto']} | {r.get('scenarios','see route_usage CSV')} |"
        )
    if not repairs:
        lines.append("| — | — | — | No repairs needed | — | — |")
    lines.extend(
        [
            "",
            "## Re-simulation",
            "",
            "Repairing bus/taxi waypoints may change carrier trajectories. "
            "Re-run simulations for scenarios referencing repaired routes "
            "(urban, vehicles, R4, D5) before publishing new protocol KPIs.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")

def repair_map_routes(
    map_name: str,
    rng: random.Random,
    *,
    only_status: set[str] | None = None,
) -> list[dict]:
    rg, roads_path, meta = load_road_graph(map_name)
    raw_roads = parse_linestrings(roads_path)
    family = meta.get("family", "")
    map_dir = WKT_DIR / map_name
    actions: list[dict] = []
    for bus_path in list_route_wkt_files(map_dir):
        before = validate_one(map_name, bus_path, 50, 150, 100, 200, 2.0)
        if only_status and before.get("status") not in only_status:
            continue
        if before.get("status") == "PASS":
            continue
        raw_lines = parse_linestrings(bus_path)
        from map_geometry import threshold_for_family, vertex_distances  # noqa: WPS433

        thresh = threshold_for_family(family)
        new_sim: list[tuple[float, float]] = []
        new_raw: list[tuple[float, float]] = []
        for attempt in range(12):
            trial_rng = random.Random(42 + hash(f"{map_name}/{bus_path.name}") % 10000 + attempt)
            if before.get("status") == "FAIL" or attempt > 0:
                new_sim = generate_bus_route_on_graph(
                    rg, trial_rng, n_stops=12, family=family
                )
            else:
                sim_lines = wkt_to_sim_coords(raw_lines)
                old_verts = sim_lines[0] if sim_lines else []
                new_sim = repair_route_waypoints(
                    rg, raw_lines[0] if raw_lines else [], old_verts, trial_rng, family
                )
            new_raw = sim_waypoints_to_raw(new_sim, raw_roads, rg)
            check_verts = wkt_to_sim_coords([new_raw])[0]
            dists = vertex_distances(rg, check_verts)
            over = sum(1 for d in dists if d > thresh)
            pct = 100.0 * over / len(dists) if dists else 0
            if pct <= 20 and (max(dists) if dists else 0) <= thresh * 2:
                break
        actions.append(
            {
                "map_name": map_name,
                "route_file": bus_path.name,
                "path": bus_path,
                "before_status": before.get("status"),
                "strategy": "A_graph_tour",
                "auto": "yes",
                "new_raw": new_raw,
                "scenarios": "see route_usage_by_scenario.csv",
            }
        )
    return actions

def main() -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", default=True, help="Default: no writes")
    mode.add_argument("--apply", action="store_true", help="Write repaired WKT (creates backup)")
    ap.add_argument("--install", action="store_true", help="Copy repaired maps to data/")
    ap.add_argument("--maps", type=str, default="", help="Comma-separated map names")
    ap.add_argument("--repair-all", action="store_true", help="Repair all bus routes, not only FAIL/WARNING")
    args = ap.parse_args()

    maps = [m.strip() for m in args.maps.split(",") if m.strip()] or ACTIVE_MAPS
    do_apply = args.apply
    rng = random.Random(42)
    only_status = None if args.repair_all else {"FAIL", "WARNING"}

    all_actions: list[dict] = []
    for map_name in maps:
        all_actions.extend(repair_map_routes(map_name, rng, only_status=only_status))

    write_repair_plan([], all_actions, REPORTS_DIR / "bus_route_repair_plan.md")

    if not do_apply:
        print(f"Dry-run: would repair {len(all_actions)} route file(s)")
        for a in all_actions:
            print(f"  {a['map_name']}/{a['route_file']} ({a['before_status']})")
        return 0

    if not all_actions:
        print("No routes to repair.")
        return 0

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = WKT_DIR / f"_backup_bus_routes_{ts}"
    backup_root.mkdir(parents=True, exist_ok=True)
    for map_name in {a["map_name"] for a in all_actions}:
        src = WKT_DIR / map_name
        dst = backup_root / map_name
        if src.is_dir():
            shutil.copytree(src, dst)
    print(f"Backup: {backup_root}")

    for a in all_actions:
        write_linestring_wkt(a["new_raw"], a["path"])
        print(f"Repaired {a['map_name']}/{a['route_file']}")

    if args.install:
        for map_name in {a["map_name"] for a in all_actions}:
            src = WKT_DIR / map_name
            dst = DATA_DIR / map_name
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"Installed {map_name} -> data/")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())