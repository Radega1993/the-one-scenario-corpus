#!/usr/bin/env python3
"""Finalize HelsinkiDowntown map for paper-ready 01_urban corpus."""

from __future__ import annotations

import argparse
import csv
import random
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import (  # noqa: E402
    DATA_DIR,
    SCENARIOS_DIR,
    WKT_DIR,
    list_poi_wkt_files,
    list_route_wkt_files,
    load_map_metadata,
    load_road_graph,
    parse_linestrings,
    parse_points,
    transform_points,
    world_size_from_metadata,
)
from helsinki_bus_routes import (  # noqa: E402
    regenerate_helsinki_bus_routes,
    validate_bus_route_extended,
)
from repair_map_pois import audit_and_repair_map, write_poi_report  # noqa: E402

MAP_NAME = "HelsinkiDowntown"
MAP_DATA = SCENARIOS_DIR / "analysis" / "data" / "maps"
REPORTS = SCENARIOS_DIR / "analysis" / "reports" / "maps"
BASE_URBAN = SCENARIOS_DIR / "base_scenarios" / "01_urban"
CORPUS_URBAN = SCENARIOS_DIR / "corpus_v1" / "01_urban"

EXPECTED_FILES = (
    "roads.wkt",
    "A_homes.wkt",
    "A_offices.wkt",
    "A_meetingspots.wkt",
    "A_bus.wkt",
    "B_bus.wkt",
    "C_bus.wkt",
)


def ensure_dirs() -> None:
    MAP_DATA.mkdir(parents=True, exist_ok=True)
    (SCENARIOS_DIR / "analysis" / "figures" / "paper" / "maps").mkdir(parents=True, exist_ok=True)


def build_asset_inventory() -> list[dict]:
    wkt_dir = WKT_DIR / MAP_NAME
    data_dir = DATA_DIR / MAP_NAME
    rows: list[dict] = []
    for fname in EXPECTED_FILES:
        wkt_p = wkt_dir / fname
        data_p = data_dir / fname
        parseable = "no"
        n_verts = 0
        if wkt_p.is_file():
            if fname == "roads.wkt" or fname.endswith("_bus.wkt"):
                ls = parse_linestrings(wkt_p)
                n_verts = sum(len(s) for s in ls)
                parseable = "yes" if ls else "no"
            else:
                pts = parse_points(wkt_p)
                n_verts = len(pts)
                parseable = "yes" if pts else "no"
        rows.append(
            {
                "asset": fname,
                "wkt_exists": wkt_p.is_file(),
                "data_exists": data_p.is_file(),
                "wkt_size_bytes": wkt_p.stat().st_size if wkt_p.is_file() else 0,
                "parseable": parseable,
                "n_vertices_or_points": n_verts,
            }
        )
    return rows


def build_geometry_validation(meta: dict) -> list[dict]:
    wx, wy = world_size_from_metadata(meta)
    rg, _, _ = load_road_graph(MAP_NAME)
    map_dir = WKT_DIR / MAP_NAME
    rows: list[dict] = []

    for p in list_poi_wkt_files(map_dir):
        pts = transform_points(parse_points(p))
        inside = all(0 <= x <= wx and 0 <= y <= wy for x, y in pts) if wx else True
        rows.append(
            {
                "asset": p.name,
                "asset_type": "poi",
                "n_elements": len(pts),
                "empty": len(pts) == 0,
                "within_world_size": inside,
                "status": "FAIL" if not pts or not inside else "PASS",
            }
        )

    from map_geometry import resolve_route_path_polyline, wkt_to_sim_coords

    for p in list_route_wkt_files(map_dir):
        raw = parse_linestrings(p)
        stops = wkt_to_sim_coords(raw)[0] if raw else []
        inside = all(0 <= x <= wx and 0 <= y <= wy for x, y in stops) if wx and stops else True
        _, failed = resolve_route_path_polyline(rg, stops) if len(stops) >= 2 else ([], [])
        st = "FAIL" if not stops or not inside or failed else "PASS"
        rows.append(
            {
                "asset": p.name,
                "asset_type": "route",
                "n_elements": len(stops),
                "empty": len(stops) == 0,
                "within_world_size": inside,
                "status": st if not failed else "FAIL",
            }
        )

    roads = parse_linestrings(map_dir / "roads.wkt")
    rows.append(
        {
            "asset": "roads.wkt",
            "asset_type": "roads",
            "n_elements": sum(len(s) for s in roads),
            "empty": not roads,
            "within_world_size": True,
            "status": "PASS" if roads else "FAIL",
        }
    )
    return rows


def write_validation_report(
    asset_rows: list[dict],
    geom_rows: list[dict],
    poi_val: list[dict],
    bus_val: list[dict],
    settings_fails: int,
) -> None:
    blocking = [r for r in geom_rows if r["status"] == "FAIL"]
    path = REPORTS / "HelsinkiDowntown_validation_report.md"
    lines = [
        f"# {MAP_NAME} — validation report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Blocking errors",
        "",
    ]
    if blocking:
        for r in blocking:
            lines.append(f"- `{r['asset']}`: {r['asset_type']}")
    else:
        lines.append("- None")
    lines.extend(["", "## Acceptable warnings", ""])
    warn_poi = sum(1 for r in poi_val if r.get("status") == "WARNING")
    warn_bus = sum(1 for r in bus_val if r.get("status") == "WARNING")
    lines.append(f"- POI points in 30–75 m band: documented in poi_report")
    lines.append(f"- Bus routes WARNING: {warn_bus}")
    lines.extend(
        [
            "",
            "## Methodological decisions",
            "",
            "- Single OSM downtown extract for all `01_urban` scenarios (2093×1838 m).",
            "- `A_bus.wkt` used in settings for WDM+bus integration; `B_bus`/`C_bus` optional assets.",
            "- U2 renamed to SparseUrban (density lever, not geographic suburb).",
            "",
            "## Actions applied",
            "",
            "See `finalize_helsinki_downtown.py --apply` logs and correction CSVs.",
            "",
            f"- Settings audit FAIL count: {settings_fails}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_affected_scenarios() -> list[dict]:
    rows: list[dict] = []
    for root, tree in ((BASE_URBAN, "base_scenarios"), (CORPUS_URBAN, "corpus_v1")):
        if not root.is_dir():
            continue
        for sp in sorted(root.glob("*HelsinkiDowntown*.settings")):
            rows.append(
                {
                    "scenario_settings": sp.name,
                    "tree": tree,
                    "reason": "poi_or_bus_wkt_or_u2_rename",
                    "resimulation_recommended": "yes",
                }
            )
    return rows


def write_resimulation_plan(n_scenarios: int) -> None:
    path = REPORTS / "HelsinkiDowntown_resimulation_plan.md"
    lines = [
        f"# {MAP_NAME} — re-simulation plan",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Recommendation",
        "",
        "**Re-run urban simulations** after POI and bus WKT updates before publishing new KPIs.",
        "",
        f"- Affected scenario settings: **{n_scenarios}** (7 base × 12 TP + variants).",
        "- U2 rename changes `Scenario.name` only; geometry unchanged but external pipelines may need path updates.",
        "",
        "## Not in scope",
        "",
        "- Traffic Profile blocks (`Events*`) unchanged.",
        "- No automatic simulation launch in this task.",
        "",
        "## Priority order",
        "",
        "1. U1, U4 (CBD / congestion) — primary bus route sensitivity",
        "2. U2 SparseUrban — density lever",
        "3. U3–U7 as needed for paper tables",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(
    *,
    global_pass: bool,
    poi_reviewed: int,
    poi_corrected: int,
    routes_reviewed: int,
    routes_corrected: int,
    n_scenarios: int,
    modified: list[str],
    generated: list[str],
) -> None:
    print("\n" + "=" * 60)
    print(f"GLOBAL: {'PASS' if global_pass else 'FAIL'}")
    print(f"POIs reviewed: {poi_reviewed}")
    print(f"POIs corrected: {poi_corrected}")
    print(f"Bus routes reviewed: {routes_reviewed}")
    print(f"Bus routes corrected: {routes_corrected}")
    print(f"Urban scenarios affected: {n_scenarios}")
    print(f"Files modified: {len(modified)}")
    print(f"Files generated: {len(generated)}")
    print("Re-simulation: RECOMMENDED for all 01_urban after WKT changes")
    print("=" * 60)


def main() -> int:
    ap = argparse.ArgumentParser(description="Finalize HelsinkiDowntown for paper")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--install", action="store_true", help="Copy wkt -> data/HelsinkiDowntown/")
    ap.add_argument("--skip-render", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if not args.dry_run and not args.apply:
        print("Use --dry-run or --apply")
        return 1

    apply = args.apply
    ensure_dirs()
    modified: list[str] = []
    generated: list[str] = []

    # 1. Asset inventory
    asset_rows = build_asset_inventory()
    inv_csv = MAP_DATA / "HelsinkiDowntown_asset_inventory.csv"
    with inv_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asset_rows[0].keys()))
        w.writeheader()
        w.writerows(asset_rows)
    generated.append(str(inv_csv))

    meta = load_map_metadata(WKT_DIR / MAP_NAME)
    geom_rows = build_geometry_validation(meta)
    geom_csv = MAP_DATA / "HelsinkiDowntown_geometry_validation.csv"
    with geom_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(geom_rows[0].keys()))
        w.writeheader()
        w.writerows(geom_rows)
    generated.append(str(geom_csv))

    # 2. POIs
    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = WKT_DIR / f"_backup_helsinki_poi_{stamp}"
        shutil.copytree(WKT_DIR / MAP_NAME, backup / MAP_NAME, dirs_exist_ok=True)
    poi_val, poi_corr, poi_mod = audit_and_repair_map(
        MAP_NAME, apply=apply, install=args.install and apply
    )
    modified.extend(poi_mod)
    poi_val_csv = MAP_DATA / "HelsinkiDowntown_poi_validation.csv"
    with poi_val_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(poi_val[0].keys()))
        w.writeheader()
        w.writerows(poi_val)
    if poi_corr:
        corr_csv = MAP_DATA / "HelsinkiDowntown_poi_corrections.csv"
        with corr_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(poi_corr[0].keys()))
            w.writeheader()
            w.writerows(poi_corr)
        generated.append(str(corr_csv))
    write_poi_report(MAP_NAME, poi_val, poi_corr, REPORTS / "HelsinkiDowntown_poi_report.md")
    generated.append(str(poi_val_csv))

    # 3. Bus routes
    map_dir = WKT_DIR / MAP_NAME
    rng = random.Random(args.seed)
    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = WKT_DIR / f"_backup_helsinki_bus_{stamp}"
        shutil.copytree(map_dir, backup / MAP_NAME, dirs_exist_ok=True)
    _, bus_corr = regenerate_helsinki_bus_routes(map_dir, rng, apply=apply)
    if apply:
        modified.extend([f"maps/wkt/{MAP_NAME}/{c['route_file']}" for c in bus_corr])

    wx, wy = world_size_from_metadata(meta)
    rg, _, _ = load_road_graph(MAP_NAME)
    bus_val: list[dict] = []
    for rp in list_route_wkt_files(map_dir):
        bus_val.append(validate_bus_route_extended(rg, rp, wx, wy))
    bus_csv = MAP_DATA / "HelsinkiDowntown_bus_route_validation.csv"
    with bus_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(bus_val[0].keys()))
        w.writeheader()
        w.writerows(bus_val)
    corr_csv = MAP_DATA / "HelsinkiDowntown_bus_route_corrections.csv"
    with corr_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(bus_corr[0].keys()))
        w.writeheader()
        w.writerows(bus_corr)
    generated.append(str(bus_csv))

    bus_report = REPORTS / "HelsinkiDowntown_bus_route_report.md"
    bus_report.write_text(
        f"# {MAP_NAME} bus routes\n\n"
        + "\n".join(
            f"- **{r['route_file']}** ({r['semantic_role']}): {r['status']} — {r.get('notes','')}"
            for r in bus_val
        )
        + "\n",
        encoding="utf-8",
    )

    if apply and args.install:
        dst = DATA_DIR / MAP_NAME
        dst.mkdir(parents=True, exist_ok=True)
        for p in list_route_wkt_files(map_dir) + list_poi_wkt_files(map_dir):
            shutil.copy2(p, dst / p.name)

    # 4. Settings + U2 rename
    audit_script = _SETUP / "audit_helsinki_urban_settings.py"
    cmd = [sys.executable, str(audit_script)]
    if apply:
        cmd += ["--rename-u2", "--apply"]
    subprocess.run(cmd, cwd=SCENARIOS_DIR.parent, check=False)

    settings_csv = MAP_DATA / "HelsinkiDowntown_urban_settings_audit.csv"
    settings_fails = 0
    if settings_csv.is_file():
        with settings_csv.open(encoding="utf-8") as f:
            settings_fails = sum(1 for r in csv.DictReader(f) if r.get("status") == "FAIL")

    write_validation_report(asset_rows, geom_rows, poi_val, bus_val, settings_fails)
    generated.append(str(REPORTS / "HelsinkiDowntown_validation_report.md"))

    affected = build_affected_scenarios()
    aff_csv = MAP_DATA / "HelsinkiDowntown_affected_scenarios.csv"
    with aff_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(affected[0].keys()))
        w.writeheader()
        w.writerows(affected)
    write_resimulation_plan(len(affected))
    generated.append(str(aff_csv))

    # 5. Render
    if not args.skip_render and apply:
        render = _SETUP / "render_wiki_map_previews.py"
        subprocess.run(
            [sys.executable, str(render), "--maps", MAP_NAME, "--validation"],
            cwd=SCENARIOS_DIR.parent,
            check=False,
        )
        subprocess.run(
            [sys.executable, str(render), "--maps", MAP_NAME, "--paper-ready"],
            cwd=SCENARIOS_DIR.parent,
            check=False,
        )

    bus_fail = any(r["status"] == "FAIL" for r in bus_val)
    poi_block = any(r["status"] == "FIX_REQUIRED" and r.get("action") == "none" for r in poi_val)
    geom_fail = any(r["status"] == "FAIL" for r in geom_rows)
    global_pass = not (bus_fail or poi_block or geom_fail or settings_fails)

    print_summary(
        global_pass=global_pass,
        poi_reviewed=len(poi_val),
        poi_corrected=len(poi_corr),
        routes_reviewed=len(bus_val),
        routes_corrected=len(bus_corr) if apply else 0,
        n_scenarios=len(affected),
        modified=modified,
        generated=generated,
    )
    return 0 if global_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
