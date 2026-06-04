#!/usr/bin/env python3
"""Regenerate auxiliary route WKT files per scenario family."""

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

from family_routes import generate_routes_for_map, validate_stops  # noqa: E402
from map_geometry import (  # noqa: E402
    ACTIVE_MAPS,
    ANALYSIS_DATA,
    DATA_DIR,
    SCENARIOS_DIR,
    WKT_DIR,
    load_road_graph,
    list_route_wkt_files,
    parse_linestrings,
    repair_route_waypoints,
    sim_waypoints_to_raw,
    write_linestring_wkt,
)
from route_semantic_config import MAP_FAMILY, ROUTE_SEMANTIC_ROWS  # noqa: E402

REPORTS_DIR = SCENARIOS_DIR / "analysis" / "reports" / "maps"
SUMMARY_CSV = ANALYSIS_DATA / "family_route_generation_summary.csv"
REPORT_MD = REPORTS_DIR / "family_route_generation_report.md"

FAMILY_MAPS = {
    "01_urban": ["HelsinkiDowntown"],
    "02_campus": ["KumpulaCampus"],
    "03_vehicles": ["ManhattanMidtownGrid"],
    "04_rural": ["NuuksioSparseTrails"],
    "05_disaster": ["HelsinkiDisrupted"],
    "06_social": ["KallioCommunityCompact"],
}

LEGACY_BY_MAP: dict[str, set[str]] = {}
for m, cur, rec, _ in ROUTE_SEMANTIC_ROWS:
    if cur != rec:
        LEGACY_BY_MAP.setdefault(m, set()).add(cur)

def backup_map_dir(map_name: str, stamp: str) -> Path:
    dest = WKT_DIR / f"_backup_semantic_regen_{stamp}" / map_name
    src = WKT_DIR / map_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest, dirs_exist_ok=True)
    return dest

def install_to_data(map_name: str) -> None:
    src = WKT_DIR / map_name
    dst = DATA_DIR / map_name
    dst.mkdir(parents=True, exist_ok=True)
    for p in list_route_wkt_files(src):
        shutil.copy2(p, dst / p.name)

def process_map(map_name: str, rng: random.Random, apply: bool) -> list[dict]:
    family = MAP_FAMILY[map_name]
    rg, roads_path, _ = load_road_graph(map_name)
    raw_lines = __import__("map_geometry").parse_linestrings(roads_path)
    routes = generate_routes_for_map(map_name, rg, rng)
    rows: list[dict] = []
    map_dir = WKT_DIR / map_name

    for fname, stops in routes.items():
        stops = repair_route_waypoints(rg, [], stops, rng, family)
        ok, note = validate_stops(rg, stops, family)
        rows.append(
            {
                "map_name": map_name,
                "family": family,
                "route_file": fname,
                "n_stops": len(stops),
                "valid": "yes" if ok else "no",
                "note": note,
                "applied": "dry-run" if not apply else "yes",
            }
        )
        if not apply:
            continue
        raw_pts = sim_waypoints_to_raw(stops, raw_lines, rg)
        write_linestring_wkt(raw_pts, map_dir / fname)

    if apply:
        for legacy in LEGACY_BY_MAP.get(map_name, set()):
            lp = map_dir / legacy
            if lp.is_file():
                lp.unlink()
    return rows

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", type=str, default="", help="e.g. 03_vehicles")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--install", action="store_true", help="Copy routes to data/ after apply")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if not args.dry_run and not args.apply:
        print("Specify --dry-run or --apply")
        return 1

    maps: list[str] = []
    if args.all:
        maps = list(ACTIVE_MAPS)
    elif args.family:
        maps = FAMILY_MAPS.get(args.family, [])
        if not maps:
            print(f"Unknown family: {args.family}")
            return 1
    else:
        print("Use --family or --all")
        return 1

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rng = random.Random(args.seed)
    all_rows: list[dict] = []

    if args.apply:
        for m in maps:
            backup_map_dir(m, stamp)
            print(f"Backup {m} -> _backup_semantic_regen_{stamp}/{m}")

    for m in maps:
        all_rows.extend(process_map(m, rng, apply=args.apply))
        if args.apply and args.install:
            install_to_data(m)
        print(f"{'[dry-run] ' if args.dry_run else ''}{m}: {len(all_rows)} route(s)")

    ANALYSIS_DATA.mkdir(parents=True, exist_ok=True)
    fields = ["map_name", "family", "route_file", "n_stops", "valid", "note", "applied"]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_rows)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Family route generation report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Mode: {'dry-run' if args.dry_run else 'apply'}",
        f"Maps: {', '.join(maps)}",
        "",
        f"Summary CSV: `{SUMMARY_CSV.relative_to(SCENARIOS_DIR)}`",
        "",
        "| Map | Route | Stops | Valid | Note |",
        "|-----|-------|-------|-------|------|",
    ]
    for r in all_rows:
        lines.append(
            f"| {r['map_name']} | {r['route_file']} | {r['n_stops']} | {r['valid']} | {r['note']} |"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {SUMMARY_CSV} and {REPORT_MD}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())