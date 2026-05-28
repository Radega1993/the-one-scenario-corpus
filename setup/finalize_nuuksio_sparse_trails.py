#!/usr/bin/env python3
"""Finalize NuuksioSparseTrails map for paper-ready 04_rural corpus."""

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
from nuuksio_ranger_route import (  # noqa: E402
    PATROL_FILE,
    load_all_poi_sim,
    regenerate_ranger_route,
    validate_ranger_route,
)
from repair_map_pois import audit_and_repair_map, write_poi_report  # noqa: E402

MAP_NAME = "NuuksioSparseTrails"
MAP_DATA = SCENARIOS_DIR / "analysis" / "data" / "maps"
REPORTS = SCENARIOS_DIR / "analysis" / "reports" / "maps"
BASE_RURAL = SCENARIOS_DIR / "base_scenarios" / "04_rural"
CORPUS_RURAL = SCENARIOS_DIR / "corpus_v1" / "04_rural"

RURAL_OK_M = 50.0
RURAL_WARN_M = 120.0

EXPECTED_FILES = (
    "roads.wkt",
    "A_homes.wkt",
    "A_offices.wkt",
    "A_meetingspots.wkt",
    "A_ranger_patrol.wkt",
)

LEGACY_ROUTE_NAMES = ("A_bus.wkt", "B_bus.wkt", "A_vehicle_route.wkt", "B_vehicle_route.wkt")


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
        legacy_on_disk = any((wkt_dir / leg).is_file() for leg in LEGACY_ROUTE_NAMES)
        parseable = "no"
        n_verts = 0
        if wkt_p.is_file():
            if fname == "roads.wkt" or fname.endswith("_patrol.wkt"):
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
                "legacy_bus_or_vehicle_wkt_on_disk": legacy_on_disk,
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
    path = REPORTS / "NuuksioSparseTrails_family_fit_report.md"
    path.write_text(
        """# NuuksioSparseTrails — family fit (04_rural)

Generated as part of rural map finalization.

## Why this map fits 04_rural

| Criterion | NuuksioSparseTrails |
|-----------|---------------------|
| Geographic scale | Nuuksio National Park OSM (EPSG:3067), sim window **2848 × 2945 m** |
| Network | Sparse trail graph (~326 segments, ~122 nodes); **low spatial coverage (~12%)** |
| Mobility | SPMM, ClusterMovement, MapRouteMovement (ranger patrol) |
| Methodological value | Scarce contacts, long routes, partial partitions, high delay |
| vs urban/campus | No dense grid or pedestrian campus; trails not streets |
| vs vehicles | No taxi/bus grid routes |
| vs stress grid | Real OSM trails, not synthetic `ControlCompactGrid` |

## Expected outcomes (not errors)

> NuuksioSparseTrails is used as a sparse rural trail map. Low spatial coverage, low encounter rates, and low delivery ratios are expected outcomes in this family and should not be interpreted as configuration errors by default.

## Scenario mapping (R1–R12)

| ID | Category | Movement | Patrol route |
|----|----------|----------|--------------|
| R1 Rural_SparseSPMM | realistic | SPMM | no |
| R2 VillagesTrails | realistic | 3× ClusterMovement | no |
| R3 WildlifeTracking | realistic | SPMM | no |
| R4 ParkRangers | realistic | MapRouteMovement | **A_ranger_patrol** |
| R5 MountainRescue | realistic | SPMM | no |
| R6–R7, R9–R12 | extreme control | SPMM (+ levers) | no |
| R8 IntermittentPower | realistic (tech) | SPMM | no |

See `NuuksioSparseTrails_rural_scenario_classification.md` for full notes.
""",
        encoding="utf-8",
    )


def write_validation_report(
    geom_rows: list[dict],
    poi_val: list[dict],
    patrol_val: dict,
    settings_fails: int,
) -> None:
    blocking = [r for r in geom_rows if r["status"] == "FAIL"]
    path = REPORTS / "NuuksioSparseTrails_validation_report.md"
    lines = [
        f"# {MAP_NAME} — validation report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Blocking errors",
        "",
    ]
    if blocking or patrol_val.get("status") == "FAIL":
        for r in blocking:
            lines.append(f"- geometry `{r['asset']}`")
        if patrol_val.get("status") == "FAIL":
            lines.append(f"- patrol route: {patrol_val.get('notes', '')}")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Acceptable warnings",
            "",
            "- Low trail coverage and partial map span are **methodological**, not defects",
            f"- Patrol route: {patrol_val.get('status', 'n/a')} — {patrol_val.get('notes', '')}",
            "- POI 50–120 m from trail: documented WARNING band",
            "",
            "## Methodological decisions",
            "",
            "- Single Nuuksio OSM extract for all `04_rural` scenarios.",
            "- `A_bus.wkt` → `A_ranger_patrol.wkt` in settings; no urban bus semantics.",
            "- R1 renamed to `R1_Rural_SparseSPMM` (SPMM, not RandomWaypoint).",
            "",
            f"- Settings audit FAIL count: {settings_fails}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_affected_scenarios() -> list[dict]:
    rows: list[dict] = []
    for root, tree in ((BASE_RURAL, "base_scenarios"), (CORPUS_RURAL, "corpus_v1")):
        if not root.is_dir():
            continue
        for sp in sorted(root.glob("*.settings")):
            reason = "rural_map_wkt_or_settings"
            if "R4_" in sp.name:
                reason = "legacy_A_bus_routeFile_fix"
            elif "R1_Rural" in sp.name:
                reason = "r1_rename_sparse_sppm"
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
    path = REPORTS / "NuuksioSparseTrails_resimulation_plan.md"
    path.write_text(
        f"""# {MAP_NAME} — re-simulation plan

Generated: {datetime.now().isoformat(timespec='seconds')}

## Recommendation

- **Re-run 04_rural simulations** if POI or ranger patrol WKT changed before publishing new KPIs.
- **R4 path fix** and **R1 rename** change settings identifiers; update external pipelines referencing `R1_Rural_RandomWaypoint`.
- Historical `output_metrics.csv` rows keep old R1 name until analysis is regenerated.

## Scope

- Affected settings files: **{n}** (12 base × 12 TP + variants).
- Traffic Profile blocks (`Events*`) not modified.

## Priority

1. R4 ParkRangers (MapRoute + patrol route)
2. R2 VillagesTrails (clusters on map)
3. R1, R3, R5 realistic SPMM
4. R6–R12 controls only if comparing before/after map fixes
""",
        encoding="utf-8",
    )


def write_final_decision(global_pass: bool, class_counts: dict[str, int]) -> None:
    path = REPORTS / "NuuksioSparseTrails_final_decision.md"
    status = "PASS — paper-ready" if global_pass else "FAIL — see validation_report"
    path.write_text(
        f"""# NuuksioSparseTrails — final decision

**Status:** {status}

Generated: {datetime.now().isoformat(timespec='seconds')}

## Summary

NuuksioSparseTrails is the sole map for **04_rural**. Finalization covers POI audit (50/120 m),
ranger patrol validation/regeneration, settings audit (A_bus fix, R1 rename), scenario classification, figures, and wiki.

## Scenario classification

- `rural_realistic`: {class_counts.get('rural_realistic', 0)}
- `rural_extreme_control`: {class_counts.get('rural_extreme_control', 0)}

## Methodological note

NuuksioSparseTrails is used as a sparse rural trail map. Low spatial coverage, low encounter rates, and low delivery ratios are expected outcomes in this family and should not be interpreted as configuration errors by default.

## Reproducibility

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_nuuksio_sparse_trails.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_nuuksio_sparse_trails.py --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps NuuksioSparseTrails --validation
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps NuuksioSparseTrails --paper-ready
bash scenarios/setup/bootstrap_maps.sh --install
```

## Artifacts

| Artifact | Path |
|----------|------|
| Asset inventory | `analysis/data/maps/NuuksioSparseTrails_asset_inventory.csv` |
| Classification | `analysis/data/maps/NuuksioSparseTrails_rural_scenario_classification.csv` |
| POI report | `analysis/reports/maps/NuuksioSparseTrails_poi_report.md` |
| Ranger route | `analysis/data/maps/NuuksioSparseTrails_ranger_route_validation.csv` |
| Settings audit | `analysis/data/maps/NuuksioSparseTrails_rural_settings_audit.csv` |
| Validation figure | `analysis/figures/maps/NuuksioSparseTrails_validation.png` |
| Paper figure | `analysis/figures/paper/maps/NuuksioSparseTrails_paper_ready.png` |
| Wiki | `.wiki-clone/09-Rural-Family.md` |

## R1 rename and historical data

`R1_Rural_RandomWaypoint` → `R1_Rural_SparseSPMM` in settings and manifests. Analysis CSVs (`output_metrics.csv`, etc.) are **not** bulk-updated.

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
    print(f"Patrol routes reviewed: {kwargs['routes_reviewed']}")
    print(f"Patrol routes corrected: {kwargs['routes_corrected']}")
    print(f"Rural realistic scenarios: {kwargs.get('n_realistic', 0)}")
    print(f"Rural control scenarios: {kwargs.get('n_control', 0)}")
    print(f"Rural scenarios (settings): {kwargs['n_scenarios']}")
    print(f"Files modified: {len(kwargs['modified'])}")
    print(f"Files generated: {len(kwargs['generated'])}")
    print("Re-simulation: RECOMMENDED if POI/patrol WKT or settings changed")
    print("=" * 60)


def main() -> int:
    ap = argparse.ArgumentParser(description="Finalize NuuksioSparseTrails for paper")
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
    inv_csv = MAP_DATA / "NuuksioSparseTrails_asset_inventory.csv"
    with inv_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asset_rows[0].keys()))
        w.writeheader()
        w.writerows(asset_rows)
    generated.append(str(inv_csv))

    meta = load_map_metadata(WKT_DIR / MAP_NAME)
    geom_rows = build_geometry_validation(meta)
    geom_csv = MAP_DATA / "NuuksioSparseTrails_geometry_validation.csv"
    with geom_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(geom_rows[0].keys()))
        w.writeheader()
        w.writerows(geom_rows)
    generated.append(str(geom_csv))

    write_family_fit_report()
    generated.append(str(REPORTS / "NuuksioSparseTrails_family_fit_report.md"))

    classify_script = _SETUP / "classify_nuuksio_rural_scenarios.py"
    subprocess.run([sys.executable, str(classify_script)], cwd=SCENARIOS_DIR.parent, check=False)

    class_counts: dict[str, int] = {}
    class_csv = MAP_DATA / "NuuksioSparseTrails_rural_scenario_classification.csv"
    if class_csv.is_file():
        with class_csv.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                cat = r.get("category", "")
                class_counts[cat] = class_counts.get(cat, 0) + 1

    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copytree(WKT_DIR / MAP_NAME, WKT_DIR / f"_backup_nuuksio_poi_{stamp}" / MAP_NAME, dirs_exist_ok=True)

    poi_val, poi_corr, poi_mod = audit_and_repair_map(
        MAP_NAME,
        apply=apply,
        install=False,
        ok_m=RURAL_OK_M,
        warn_m=RURAL_WARN_M,
    )
    modified.extend(poi_mod)
    poi_csv = MAP_DATA / "NuuksioSparseTrails_poi_validation.csv"
    with poi_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(poi_val[0].keys()))
        w.writeheader()
        w.writerows(poi_val)
    if poi_corr:
        with (MAP_DATA / "NuuksioSparseTrails_poi_corrections.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(poi_corr[0].keys()))
            w.writeheader()
            w.writerows(poi_corr)
    write_poi_report(
        MAP_NAME,
        poi_val,
        poi_corr,
        REPORTS / "NuuksioSparseTrails_poi_report.md",
        ok_m=RURAL_OK_M,
        warn_m=RURAL_WARN_M,
        threshold_label="rural",
    )

    map_dir = WKT_DIR / MAP_NAME
    rng = random.Random(args.seed)
    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copytree(map_dir, WKT_DIR / f"_backup_nuuksio_ranger_{stamp}" / MAP_NAME, dirs_exist_ok=True)
    patrol_corr = regenerate_ranger_route(map_dir, rng, apply=apply)
    if apply:
        modified.append(f"maps/wkt/{MAP_NAME}/{PATROL_FILE}")

    wx, wy = world_size_from_metadata(meta)
    rg, roads_path, _ = load_road_graph(MAP_NAME)
    poi_pts = load_all_poi_sim(map_dir)
    patrol_path = map_dir / PATROL_FILE
    patrol_val = (
        validate_ranger_route(rg, patrol_path, wx, wy, poi_pts=poi_pts, roads_path=roads_path)
        if patrol_path.is_file()
        else {"status": "FAIL", "notes": "missing"}
    )
    with (MAP_DATA / "NuuksioSparseTrails_ranger_route_validation.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(patrol_val.keys()))
        w.writeheader()
        w.writerow(patrol_val)
    with (MAP_DATA / "NuuksioSparseTrails_ranger_route_corrections.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(patrol_corr[0].keys()))
        w.writeheader()
        w.writerows(patrol_corr)
    (REPORTS / "NuuksioSparseTrails_ranger_route_report.md").write_text(
        f"# Ranger patrol route\n\n- **{patrol_val.get('route_file', PATROL_FILE)}**: "
        f"{patrol_val.get('status')} — {patrol_val.get('notes', '')}\n",
        encoding="utf-8",
    )

    if apply and args.install:
        dst = DATA_DIR / MAP_NAME
        dst.mkdir(parents=True, exist_ok=True)
        for p in list_route_wkt_files(map_dir) + list_poi_wkt_files(map_dir):
            shutil.copy2(p, dst / p.name)

    audit_script = _SETUP / "audit_nuuksio_rural_settings.py"
    cmd = [sys.executable, str(audit_script)]
    if apply:
        cmd += ["--fix-legacy-bus", "--rename-r1", "--apply"]
    subprocess.run(cmd, cwd=SCENARIOS_DIR.parent, check=False)

    settings_csv = MAP_DATA / "NuuksioSparseTrails_rural_settings_audit.csv"
    settings_fails = 0
    if settings_csv.is_file():
        with settings_csv.open(encoding="utf-8") as f:
            settings_fails = sum(1 for r in csv.DictReader(f) if r.get("status") == "FAIL")

    write_validation_report(geom_rows, poi_val, patrol_val, settings_fails)

    affected = build_affected_scenarios()
    if affected:
        with (MAP_DATA / "NuuksioSparseTrails_affected_scenarios.csv").open("w", newline="", encoding="utf-8") as f:
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

    patrol_fail = patrol_val.get("status") == "FAIL"
    poi_block = any(r["status"] == "FIX_REQUIRED" and r.get("action") == "none" for r in poi_val)
    geom_fail = any(r["status"] == "FAIL" for r in geom_rows)
    global_pass = not (patrol_fail or poi_block or geom_fail or settings_fails)

    write_final_decision(global_pass, class_counts)

    print_summary(
        global_pass=global_pass,
        poi_reviewed=len(poi_val),
        poi_corrected=len(poi_corr),
        routes_reviewed=1,
        routes_corrected=len(patrol_corr) if apply else 0,
        n_realistic=class_counts.get("rural_realistic", 0),
        n_control=class_counts.get("rural_extreme_control", 0),
        n_scenarios=len(affected),
        modified=modified,
        generated=generated,
    )
    return 0 if global_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
