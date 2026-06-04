#!/usr/bin/env python3
"""Finalize ManhattanMidtownGrid map for paper-ready 03_vehicles corpus."""

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
    resolve_route_path_polyline,
    transform_points,
    wkt_to_sim_coords,
    world_size_from_metadata,
)
from manhattan_vehicle_routes import (  # noqa: E402
    regenerate_vehicle_routes,
    validate_vehicle_route,
)
from repair_map_pois import audit_and_repair_map, write_poi_report  # noqa: E402

MAP_NAME = "ManhattanMidtownGrid"
MAP_DATA = SCENARIOS_DIR / "analysis" / "data" / "maps"
REPORTS = SCENARIOS_DIR / "analysis" / "reports" / "maps"
BASE_VEH = SCENARIOS_DIR / "base_scenarios" / "03_vehicles"
CORPUS_VEH = SCENARIOS_DIR / "corpus_v1" / "03_vehicles"

VEHICLE_OK_M = 30.0
VEHICLE_WARN_M = 75.0

EXPECTED_FILES = (
    "roads.wkt",
    "A_homes.wkt",
    "A_offices.wkt",
    "A_meetingspots.wkt",
    "A_vehicle_route.wkt",
    "B_vehicle_route.wkt",
)

ROUTE_FILES = ("A_vehicle_route.wkt", "B_vehicle_route.wkt")

def ensure_dirs() -> None:
    MAP_DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (SCENARIOS_DIR / "analysis" / "figures" / "paper" / "maps").mkdir(parents=True, exist_ok=True)

def build_asset_inventory() -> list[dict]:
    wkt_dir = WKT_DIR / MAP_NAME
    data_dir = DATA_DIR / MAP_NAME
    rows: list[dict] = []
    for fname in EXPECTED_FILES:
        wkt_p = wkt_dir / fname
        data_p = data_dir / fname
        legacy_bus = wkt_dir / fname.replace("_vehicle_route", "_bus").replace("B_bus", "B_bus")
        if fname.endswith("_route.wkt"):
            legacy_name = fname.replace("vehicle_route", "bus")
            legacy_bus = wkt_dir / legacy_name
        else:
            legacy_bus = None
        parseable = "no"
        n_verts = 0
        if wkt_p.is_file():
            if fname == "roads.wkt" or fname.endswith("_route.wkt"):
                ls = parse_linestrings(wkt_p)
                n_verts = sum(len(s) for s in ls) if ls else 0
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
                "legacy_bus_wkt_on_disk": legacy_bus.is_file() if legacy_bus else False,
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

    for p in list_route_wkt_files(map_dir):
        raw = parse_linestrings(p)
        stops = wkt_to_sim_coords(raw)[0] if raw else []
        inside = all(0 <= x <= wx and 0 <= y <= wy for x, y in stops) if wx and stops else True
        _, failed = resolve_route_path_polyline(rg, stops) if len(stops) >= 2 else ([], [])
        rows.append(
            {
                "asset": p.name,
                "asset_type": "route",
                "n_elements": len(stops),
                "empty": len(stops) == 0,
                "within_world_size": inside,
                "status": "FAIL" if not stops or not inside or failed else "PASS",
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

def write_family_fit_report() -> None:
    path = REPORTS / "ManhattanMidtownGrid_family_fit_report.md"
    path.write_text(
        """# ManhattanMidtownGrid — family fit (03_vehicles)

Generated as part of vehicle map finalization.

## Why this map fits 03_vehicles

| Criterion | ManhattanMidtownGrid |
|-----------|-------------------|
| Geographic scale | OSM Midtown Manhattan grid (EPSG:32618), sim window **2500 × 2366 m** |
| Network | Regular street grid — ideal for taxis, bus carriers, car-ownership contrasts |
| Coverage | ~12% road length / worldSize (large window, sparse relative to bbox) |
| vs campus | No SPMM pedestrian focus; vehicle speeds and route-following |
| vs urban | Helsinki uses integrated bus WDM; Manhattan isolates **vehicle mobility** levers |
| vs rural | Dense grid vs trail networks |

## Visual rotation (UTM → sim frame)

The sim transform (mirror Y + translate from WKT metadata) can **visually tilt** the Manhattan grid in figures. **Street topology is preserved** — acceptable for paper figures.

## Scenario mapping (V1–V5)

| Scenario | Movement | Routes | POI | Role |
|----------|----------|--------|-----|------|
| V1 TaxiLow | MapRouteMovement | Group1 → A_vehicle | No | Few taxis, high speed |
| V2 TaxiHigh | MapRouteMovement | Group1 → A_vehicle | No | Many taxis |
| V3 BusCarriers | BusMovement | A + B vehicle routes | No | Two carrier groups |
| V4 CarOwnership 0% | WDM + bus (`busControlSystemNr = -1`) | A_vehicle | Yes | No private cars |
| V5 CarOwnership 100% | WDM + bus | A_vehicle | Yes | Full car ownership |

## Route semantics

- **A_vehicle_route.wkt** — longitudinal axis (N–S dominant on grid).
- **B_vehicle_route.wkt** — transversal axis (E–W dominant).
- Legacy **`A_bus.wkt`** removed from disk; settings unified to `A_vehicle_route.wkt`.

## Difference from other families

- **01_urban (HelsinkiDowntown):** pedestrian WDM, semantic bus lines A/B/C, smaller effective density.
- **02_campus (Kumpula):** SPMM, optional shuttle figure only.
- **04_rural (Nuuksio):** ranger patrol on trails, not grid taxis.
""",
        encoding="utf-8",
    )

def write_validation_report(
    geom_rows: list[dict],
    poi_val: list[dict],
    route_vals: list[dict],
    settings_fails: int,
) -> None:
    blocking = [r for r in geom_rows if r["status"] == "FAIL"]
    route_fail = [r for r in route_vals if r.get("status") == "FAIL"]
    path = REPORTS / "ManhattanMidtownGrid_validation_report.md"
    lines = [
        f"# {MAP_NAME} — validation report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Blocking errors",
        "",
    ]
    if blocking or route_fail:
        for r in blocking:
            lines.append(f"- geometry `{r['asset']}`")
        for r in route_fail:
            lines.append(f"- route `{r['route_file']}`: {r.get('notes', '')}")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Acceptable warnings",
            "",
            "- POI offices/meetings >50 m: see poi_report (urban thresholds 30/75 m)",
            "- Route A may show WARNING (origin frame / coverage); B should PASS",
            "- Grid visual rotation in figures does not affect simulation topology",
            "",
            "## Methodological decisions",
            "",
            "- Single Midtown OSM extract for all `03_vehicles` scenarios.",
            "- `Group.routeFile` legacy `A_bus.wkt` → `A_vehicle_route.wkt` (file absent on disk).",
            "- Header comments `HelsinkiMedium` → `ManhattanMidtownGrid` (comments only).",
            "",
            f"- Settings audit FAIL count: {settings_fails}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def build_affected_scenarios() -> list[dict]:
    rows: list[dict] = []
    for root, tree in ((BASE_VEH, "base_scenarios"), (CORPUS_VEH, "corpus_v1")):
        if not root.is_dir():
            continue
        for sp in sorted(root.glob("*.settings")):
            if "ManhattanMidtownGrid" not in sp.name:
                continue
            reason = "vehicle_map_wkt_or_settings"
            if "V1_" in sp.name or "V2_" in sp.name:
                reason = "legacy_A_bus_routeFile_fix"
            rows.append(
                {
                    "scenario_settings": sp.name,
                    "tree": tree,
                    "reason": reason,
                    "resimulation_recommended": "yes_if_wkt_or_route_changed",
                }
            )
    return rows

def write_resimulation_plan(n: int) -> None:
    path = REPORTS / "ManhattanMidtownGrid_resimulation_plan.md"
    path.write_text(
        f"""# {MAP_NAME} — re-simulation plan

Generated: {datetime.now().isoformat(timespec='seconds')}

## Recommendation

- **Re-run 03_vehicles simulations** if vehicle route WKT or POI files changed before publishing new KPIs.
- **Settings path fix** (`A_bus` → `A_vehicle_route`) corrects broken `Group.routeFile` for WDM groups; MapRouteMovement (V1/V2) primarily uses `Group1.routeFile`.

## Scope

- Affected settings files: **{n}** (5 base + 60 TP variants).
- Traffic Profile blocks (`Events*`) not modified.

## Priority

1. V3 (dual bus carriers on A/B routes)
2. V4, V5 (WDM + POI + vehicle route)
3. V1, V2 (taxi MapRouteMovement)
""",
        encoding="utf-8",
    )

def write_final_decision(global_pass: bool) -> None:
    path = REPORTS / "ManhattanMidtownGrid_final_decision.md"
    status = "PASS — paper-ready" if global_pass else "FAIL — see validation_report"
    path.write_text(
        f"""# ManhattanMidtownGrid — final decision

**Status:** {status}

Generated: {datetime.now().isoformat(timespec='seconds')}

## Summary

ManhattanMidtownGrid is the sole map for **03_vehicles**. Finalization covers POI audit (30/75 m),
vehicle routes A/B validation/regeneration, settings audit (legacy bus paths), figures, and wiki.

## Reproducibility

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_manhattan_midtown.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_manhattan_midtown.py --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps ManhattanMidtownGrid --validation
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps ManhattanMidtownGrid --paper-ready
bash scenarios/setup/bootstrap_maps.sh --install
```

## Artifacts

| Artifact | Path |
|----------|------|
| Asset inventory | `analysis/data/maps/ManhattanMidtownGrid_asset_inventory.csv` |
| Geometry validation | `analysis/data/maps/ManhattanMidtownGrid_geometry_validation.csv` |
| POI report | `analysis/reports/maps/ManhattanMidtownGrid_poi_report.md` |
| Vehicle routes | `analysis/data/maps/ManhattanMidtownGrid_vehicle_route_validation.csv` |
| Settings audit | `analysis/data/maps/ManhattanMidtownGrid_vehicle_settings_audit.csv` |
| Validation | `analysis/figures/maps/ManhattanMidtownGrid_validation.png` |
| Paper figure | `analysis/figures/paper/maps/ManhattanMidtownGrid_paper_ready.png` |
| Wiki | `.wiki-clone/08-Vehicles-Family.md` |

## Excluded

Other map families; OSM full regen; Traffic Profile changes; automatic re-simulation.
""",
        encoding="utf-8",
    )

def print_summary(**kwargs) -> None:
    print("\n" + "=" * 60)
    print(f"GLOBAL: {'PASS' if kwargs['global_pass'] else 'FAIL'}")
    print(f"POIs reviewed: {kwargs['poi_reviewed']}")
    print(f"POIs corrected: {kwargs['poi_corrected']}")
    print(f"Vehicle routes reviewed: {kwargs['routes_reviewed']}")
    print(f"Vehicle routes corrected: {kwargs['routes_corrected']}")
    print(f"Vehicle scenarios: {kwargs['n_scenarios']}")
    print(f"Files modified: {len(kwargs['modified'])}")
    print(f"Files generated: {len(kwargs['generated'])}")
    print("Re-simulation: RECOMMENDED if POI/route WKT or settings paths changed")
    print("=" * 60)

def main() -> int:
    ap = argparse.ArgumentParser(description="Finalize ManhattanMidtownGrid for paper")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--install", action="store_true")
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

    asset_rows = build_asset_inventory()
    inv_csv = MAP_DATA / "ManhattanMidtownGrid_asset_inventory.csv"
    with inv_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asset_rows[0].keys()))
        w.writeheader()
        w.writerows(asset_rows)
    generated.append(str(inv_csv))

    meta = load_map_metadata(WKT_DIR / MAP_NAME)
    geom_rows = build_geometry_validation(meta)
    geom_csv = MAP_DATA / "ManhattanMidtownGrid_geometry_validation.csv"
    with geom_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(geom_rows[0].keys()))
        w.writeheader()
        w.writerows(geom_rows)
    generated.append(str(geom_csv))

    write_family_fit_report()
    generated.append(str(REPORTS / "ManhattanMidtownGrid_family_fit_report.md"))

    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copytree(WKT_DIR / MAP_NAME, WKT_DIR / f"_backup_manhattan_poi_{stamp}" / MAP_NAME, dirs_exist_ok=True)

    poi_val, poi_corr, poi_mod = audit_and_repair_map(
        MAP_NAME,
        apply=apply,
        install=False,
        ok_m=VEHICLE_OK_M,
        warn_m=VEHICLE_WARN_M,
    )
    modified.extend(poi_mod)
    poi_csv = MAP_DATA / "ManhattanMidtownGrid_poi_validation.csv"
    with poi_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(poi_val[0].keys()))
        w.writeheader()
        w.writerows(poi_val)
    if poi_corr:
        with (MAP_DATA / "ManhattanMidtownGrid_poi_corrections.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(poi_corr[0].keys()))
            w.writeheader()
            w.writerows(poi_corr)
    write_poi_report(
        MAP_NAME,
        poi_val,
        poi_corr,
        REPORTS / "ManhattanMidtownGrid_poi_report.md",
        ok_m=VEHICLE_OK_M,
        warn_m=VEHICLE_WARN_M,
        threshold_label="vehicle (urban-equivalent)",
    )

    map_dir = WKT_DIR / MAP_NAME
    rng = random.Random(args.seed)
    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copytree(map_dir, WKT_DIR / f"_backup_manhattan_vehicle_{stamp}" / MAP_NAME, dirs_exist_ok=True)
    route_corr = regenerate_vehicle_routes(map_dir, rng, apply=apply)
    if apply:
        for rf in ROUTE_FILES:
            modified.append(f"maps/wkt/{MAP_NAME}/{rf}")

    wx, wy = world_size_from_metadata(meta)
    rg, _, _ = load_road_graph(MAP_NAME)
    stops_by_file: dict[str, list] = {}
    for rf in ROUTE_FILES:
        p = map_dir / rf
        if p.is_file():
            raw = parse_linestrings(p)
            stops_by_file[rf] = wkt_to_sim_coords(raw)[0] if raw else []

    route_vals: list[dict] = []
    for rf in ROUTE_FILES:
        p = map_dir / rf
        other = stops_by_file.get("B_vehicle_route.wkt" if rf == "A_vehicle_route.wkt" else "A_vehicle_route.wkt")
        if p.is_file():
            route_vals.append(validate_vehicle_route(rg, p, wx, wy, other_stops=other))
        else:
            route_vals.append({"route_file": rf, "status": "FAIL", "notes": "missing"})

    val_csv = MAP_DATA / "ManhattanMidtownGrid_vehicle_route_validation.csv"
    with val_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(route_vals[0].keys()))
        w.writeheader()
        w.writerows(route_vals)
    with (MAP_DATA / "ManhattanMidtownGrid_vehicle_route_corrections.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(route_corr[0].keys()))
        w.writeheader()
        w.writerows(route_corr)

    notes = "; ".join(f"{r['route_file']}: {r.get('status')} — {r.get('notes', '')}" for r in route_vals)
    (REPORTS / "ManhattanMidtownGrid_vehicle_route_report.md").write_text(
        f"# Vehicle routes\n\n{notes}\n",
        encoding="utf-8",
    )

    if apply and args.install:
        dst = DATA_DIR / MAP_NAME
        dst.mkdir(parents=True, exist_ok=True)
        for p in list_route_wkt_files(map_dir) + list_poi_wkt_files(map_dir):
            shutil.copy2(p, dst / p.name)

    audit_script = _SETUP / "audit_manhattan_vehicle_settings.py"
    cmd = [sys.executable, str(audit_script)]
    if apply:
        cmd += ["--fix-legacy-bus", "--apply"]
    subprocess.run(cmd, cwd=SCENARIOS_DIR.parent, check=False)

    settings_csv = MAP_DATA / "ManhattanMidtownGrid_vehicle_settings_audit.csv"
    settings_fails = 0
    if settings_csv.is_file():
        with settings_csv.open(encoding="utf-8") as f:
            settings_fails = sum(1 for r in csv.DictReader(f) if r.get("status") == "FAIL")

    write_validation_report(geom_rows, poi_val, route_vals, settings_fails)

    affected = build_affected_scenarios()
    with (MAP_DATA / "ManhattanMidtownGrid_affected_scenarios.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(affected[0].keys()))
        w.writeheader()
        w.writerows(affected)
    write_resimulation_plan(len(affected))

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

    route_fail = any(r.get("status") == "FAIL" for r in route_vals)
    poi_block = any(r["status"] == "FIX_REQUIRED" and r.get("action") == "none" for r in poi_val)
    geom_fail = any(r["status"] == "FAIL" for r in geom_rows)
    global_pass = not (route_fail or poi_block or geom_fail or settings_fails)

    write_final_decision(global_pass)

    print_summary(
        global_pass=global_pass,
        poi_reviewed=len(poi_val),
        poi_corrected=len(poi_corr),
        routes_reviewed=len(route_vals),
        routes_corrected=len(route_corr) if apply else 0,
        n_scenarios=len(affected),
        modified=modified,
        generated=generated,
    )
    return 0 if global_pass else 1

if __name__ == "__main__":
    raise SystemExit(main())