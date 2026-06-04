#!/usr/bin/env python3
"""Finalize HelsinkiDisrupted map for paper-ready 05_disaster corpus."""

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
from helsinki_disaster_routes import (  # noqa: E402
    ROUTE_FILES,
    load_all_poi_sim,
    regenerate_disaster_routes,
    validate_disaster_route,
)
from repair_map_pois import audit_and_repair_map, write_poi_report  # noqa: E402

MAP_NAME = "HelsinkiDisrupted"
MAP_DATA = SCENARIOS_DIR / "analysis" / "data" / "maps"
REPORTS = SCENARIOS_DIR / "analysis" / "reports" / "maps"
BASE_DISASTER = SCENARIOS_DIR / "base_scenarios" / "05_disaster"
CORPUS_DISASTER = SCENARIOS_DIR / "corpus_v1" / "05_disaster"

DISASTER_OK_M = 40.0
DISASTER_WARN_M = 100.0

EXPECTED_FILES = (
    "roads.wkt",
    "A_homes.wkt",
    "A_offices.wkt",
    "A_meetingspots.wkt",
    "A_emergency_route.wkt",
    "B_mule_route.wkt",
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
    path = REPORTS / "HelsinkiDisrupted_family_fit_report.md"
    path.write_text(
        """# HelsinkiDisrupted — family fit (05_disaster)

Generated as part of disaster map finalization.

## Why this map fits 05_disaster

| Criterion | HelsinkiDisrupted |
|-----------|-------------------|
| Geographic scale | Kalasatama / Sörnäinen OSM (EPSG:3067), sim window **2067 × 2206 m** |
| Network | Urban drive network (~8398 segments, ~3142 nodes); partial connectivity |
| Mobility | ClusterMovement, SPMM, MapRouteMovement (emergency/UAV) |
| Methodological value | Degraded comms, hotspots, partitions, mule bridges, critical TTL |
| vs HelsinkiDowntown | Normal urban commuting — not disaster-degraded |
| vs stress grid | Real OSM harbour/industrial fabric, not synthetic |

## Expected outcomes (not errors)

> HelsinkiDisrupted is used as a degraded urban disaster map. Low delivery, high latency, and structural partitioning can be expected outcomes in specific scenarios and should not be interpreted as configuration errors by default.

## Scenario mapping (D1–D9)

| ID | Category | Role |
|----|----------|------|
| D1 | realistic | Shelter hotspots (clusters) |
| D2 | bridge/mule | Partitioned city + SPMM mule |
| D3–D4, D8 | realistic | Aftershock, triage, infrastructure return |
| D5 | bridge/mule | UAV on A_emergency_route; civilians SPMM |
| D6, D9 | critical TTL | Short / 1 min TTL controls |
| D7 | stress control | High load traffic storm |

See `HelsinkiDisrupted_disaster_scenario_classification.md` for full notes.
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
    path = REPORTS / "HelsinkiDisrupted_validation_report.md"
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
            "- Low delivery / partition in D2 is **methodological**",
            "- Route origin/border WARNING documented",
            "- POI 40–100 m from road: documented WARNING band",
            "",
            "## Methodological decisions",
            "",
            "- Single Kalasatama OSM extract for all `05_disaster` scenarios.",
            "- D5 Group1: MapRouteMovement+roads.wkt → ShortestPathMapBasedMovement.",
            "- `A_emergency_route` / `B_mule_route` (not legacy bus names).",
            "",
            f"- Settings audit FAIL count: {settings_fails}",
        ]
    )
    for r in route_vals:
        lines.append(f"- Route {r['route_file']}: {r.get('status')} — {r.get('notes', '')}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def build_affected_scenarios() -> list[dict]:
    rows: list[dict] = []
    for root, tree in ((BASE_DISASTER, "base_scenarios"), (CORPUS_DISASTER, "corpus_v1")):
        if not root.is_dir():
            continue
        for sp in sorted(root.glob("*.settings")):
            reason = "disaster_map_wkt_or_settings"
            if "D5_" in sp.name:
                reason = "d5_group1_spmm_fix"
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
    path = REPORTS / "HelsinkiDisrupted_resimulation_plan.md"
    path.write_text(
        f"""# {MAP_NAME} — re-simulation plan

Generated: {datetime.now().isoformat(timespec='seconds')}

## Recommendation

- **Re-run 05_disaster simulations** if POI or disaster route WKT changed before publishing new KPIs.
- **D5 Group1 SPMM fix** changes civilian mobility model — re-run D5 and TP variants.

## Scope

- Affected settings files: **{n}** (9 base × 12 TP).
- Traffic Profile blocks (`Events*`) not modified.

## Priority

1. D5 UAVMule (MapRoute UAV + SPMM civilians)
2. D2 PartitionedCity (structural partition)
3. D1, D4, D8 narrative cluster scenarios
4. D6, D7, D9 controls only if comparing before/after map fixes
""",
        encoding="utf-8",
    )

def write_final_decision(global_pass: bool, class_counts: dict[str, int]) -> None:
    path = REPORTS / "HelsinkiDisrupted_final_decision.md"
    status = "PASS — paper-ready" if global_pass else "FAIL — see validation_report"
    n_narrative = (
        class_counts.get("disaster_realistic", 0)
        + class_counts.get("disaster_bridge_or_mule", 0)
    )
    n_control = (
        class_counts.get("disaster_critical_ttl", 0)
        + class_counts.get("disaster_stress_control", 0)
    )
    path.write_text(
        f"""# HelsinkiDisrupted — final decision

**Status:** {status}

Generated: {datetime.now().isoformat(timespec='seconds')}

## Summary

HelsinkiDisrupted is the sole map for **05_disaster**. Finalization covers POI audit (40/100 m),
emergency/mule route validation/regeneration, settings audit (D5 SPMM), scenario classification, figures, and wiki.

## Scenario classification

- Narrative (realistic + bridge/mule): {n_narrative}
- Controls (TTL + stress): {n_control}

## Methodological note

HelsinkiDisrupted is used as a degraded urban disaster map. Low delivery, high latency, and structural partitioning can be expected outcomes in specific scenarios and should not be interpreted as configuration errors by default.

## Reproducibility

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_helsinki_disrupted.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_helsinki_disrupted.py --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps HelsinkiDisrupted --validation
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps HelsinkiDisrupted --paper-ready
bash scenarios/setup/bootstrap_maps.sh --install
```

## Artifacts

| Artifact | Path |
|----------|------|
| Asset inventory | `analysis/data/maps/HelsinkiDisrupted_asset_inventory.csv` |
| Classification | `analysis/data/maps/HelsinkiDisrupted_disaster_scenario_classification.csv` |
| POI report | `analysis/reports/maps/HelsinkiDisrupted_poi_report.md` |
| Routes | `analysis/data/maps/HelsinkiDisrupted_route_validation.csv` |
| Settings audit | `analysis/data/maps/HelsinkiDisrupted_disaster_settings_audit.csv` |
| Validation figure | `analysis/figures/maps/HelsinkiDisrupted_validation.png` |
| Paper figure | `analysis/figures/paper/maps/HelsinkiDisrupted_paper_ready.png` |
| Wiki | `.wiki-clone/10-Disaster-Family.md` |

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
    print(f"Disaster routes reviewed: {kwargs['routes_reviewed']}")
    print(f"Disaster routes corrected: {kwargs['routes_corrected']}")
    print(f"Narrative disaster scenarios: {kwargs.get('n_narrative', 0)}")
    print(f"Control/stress scenarios: {kwargs.get('n_control', 0)}")
    print(f"Disaster scenarios (settings): {kwargs['n_scenarios']}")
    print(f"Files modified: {len(kwargs['modified'])}")
    print(f"Files generated: {len(kwargs['generated'])}")
    print("Re-simulation: RECOMMENDED if POI/route WKT or D5 settings changed")
    print("=" * 60)

def main() -> int:
    ap = argparse.ArgumentParser(description="Finalize HelsinkiDisrupted for paper")
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
    inv_csv = MAP_DATA / "HelsinkiDisrupted_asset_inventory.csv"
    with inv_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asset_rows[0].keys()))
        w.writeheader()
        w.writerows(asset_rows)
    generated.append(str(inv_csv))

    meta = load_map_metadata(WKT_DIR / MAP_NAME)
    geom_rows = build_geometry_validation(meta)
    geom_csv = MAP_DATA / "HelsinkiDisrupted_geometry_validation.csv"
    with geom_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(geom_rows[0].keys()))
        w.writeheader()
        w.writerows(geom_rows)
    generated.append(str(geom_csv))

    write_family_fit_report()
    generated.append(str(REPORTS / "HelsinkiDisrupted_family_fit_report.md"))

    classify_script = _SETUP / "classify_helsinki_disaster_scenarios.py"
    subprocess.run([sys.executable, str(classify_script)], cwd=SCENARIOS_DIR.parent, check=False)

    class_counts: dict[str, int] = {}
    class_csv = MAP_DATA / "HelsinkiDisrupted_disaster_scenario_classification.csv"
    if class_csv.is_file():
        with class_csv.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                cat = r.get("category", "")
                class_counts[cat] = class_counts.get(cat, 0) + 1

    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copytree(WKT_DIR / MAP_NAME, WKT_DIR / f"_backup_helsinki_poi_{stamp}" / MAP_NAME, dirs_exist_ok=True)

    poi_val, poi_corr, poi_mod = audit_and_repair_map(
        MAP_NAME,
        apply=apply,
        install=False,
        ok_m=DISASTER_OK_M,
        warn_m=DISASTER_WARN_M,
    )
    modified.extend(poi_mod)
    poi_csv = MAP_DATA / "HelsinkiDisrupted_poi_validation.csv"
    with poi_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(poi_val[0].keys()))
        w.writeheader()
        w.writerows(poi_val)
    if poi_corr:
        with (MAP_DATA / "HelsinkiDisrupted_poi_corrections.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(poi_corr[0].keys()))
            w.writeheader()
            w.writerows(poi_corr)
    write_poi_report(
        MAP_NAME,
        poi_val,
        poi_corr,
        REPORTS / "HelsinkiDisrupted_poi_report.md",
        ok_m=DISASTER_OK_M,
        warn_m=DISASTER_WARN_M,
        threshold_label="disaster",
    )

    map_dir = WKT_DIR / MAP_NAME
    rng = random.Random(args.seed)
    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copytree(map_dir, WKT_DIR / f"_backup_helsinki_disaster_routes_{stamp}" / MAP_NAME, dirs_exist_ok=True)
    route_corr = regenerate_disaster_routes(map_dir, rng, apply=apply)
    if apply:
        for rf in ROUTE_FILES:
            modified.append(f"maps/wkt/{MAP_NAME}/{rf}")

    wx, wy = world_size_from_metadata(meta)
    rg, roads_path, _ = load_road_graph(MAP_NAME)
    poi_pts = load_all_poi_sim(map_dir)
    stops_by_file: dict[str, list] = {}
    route_vals: list[dict] = []
    for rf in ROUTE_FILES:
        p = map_dir / rf
        if p.is_file():
            from helsinki_disaster_routes import _route_stops_sim

            stops_by_file[rf] = _route_stops_sim(p, roads_path)

    for rf in ROUTE_FILES:
        p = map_dir / rf
        other_key = "B_mule_route.wkt" if rf == "A_emergency_route.wkt" else "A_emergency_route.wkt"
        other = stops_by_file.get(other_key)
        if p.is_file():
            route_vals.append(
                validate_disaster_route(rg, p, wx, wy, other_stops=other, poi_pts=poi_pts, roads_path=roads_path)
            )
        else:
            route_vals.append({"route_file": rf, "status": "FAIL", "notes": "missing"})

    val_csv = MAP_DATA / "HelsinkiDisrupted_route_validation.csv"
    with val_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(route_vals[0].keys()))
        w.writeheader()
        w.writerows(route_vals)
    with (MAP_DATA / "HelsinkiDisrupted_route_corrections.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(route_corr[0].keys()))
        w.writeheader()
        w.writerows(route_corr)
    notes = "; ".join(f"{r['route_file']}: {r.get('status')} — {r.get('notes', '')}" for r in route_vals)
    (REPORTS / "HelsinkiDisrupted_route_report.md").write_text(f"# Disaster routes\n\n{notes}\n", encoding="utf-8")

    if apply and args.install:
        dst = DATA_DIR / MAP_NAME
        dst.mkdir(parents=True, exist_ok=True)
        for p in list_route_wkt_files(map_dir) + list_poi_wkt_files(map_dir):
            shutil.copy2(p, dst / p.name)

    audit_script = _SETUP / "audit_helsinki_disaster_settings.py"
    cmd = [sys.executable, str(audit_script)]
    if apply:
        cmd += ["--fix-d5-spmm", "--fix-comments", "--apply"]
    subprocess.run(cmd, cwd=SCENARIOS_DIR.parent, check=False)

    settings_csv = MAP_DATA / "HelsinkiDisrupted_disaster_settings_audit.csv"
    settings_fails = 0
    if settings_csv.is_file():
        with settings_csv.open(encoding="utf-8") as f:
            settings_fails = sum(1 for r in csv.DictReader(f) if r.get("status") == "FAIL")

    write_validation_report(geom_rows, poi_val, route_vals, settings_fails)

    affected = build_affected_scenarios()
    if affected:
        with (MAP_DATA / "HelsinkiDisrupted_affected_scenarios.csv").open("w", newline="", encoding="utf-8") as f:
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

    write_final_decision(global_pass, class_counts)

    n_narrative = class_counts.get("disaster_realistic", 0) + class_counts.get("disaster_bridge_or_mule", 0)
    n_control = class_counts.get("disaster_critical_ttl", 0) + class_counts.get("disaster_stress_control", 0)

    print_summary(
        global_pass=global_pass,
        poi_reviewed=len(poi_val),
        poi_corrected=len(poi_corr),
        routes_reviewed=len(route_vals),
        routes_corrected=len(route_corr) if apply else 0,
        n_narrative=n_narrative,
        n_control=n_control,
        n_scenarios=len(affected),
        modified=modified,
        generated=generated,
    )
    return 0 if global_pass else 1

if __name__ == "__main__":
    raise SystemExit(main())