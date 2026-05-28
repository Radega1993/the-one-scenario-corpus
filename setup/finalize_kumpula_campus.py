#!/usr/bin/env python3
"""Finalize KumpulaCampus map for paper-ready 02_campus corpus."""

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
from kumpula_shuttle_route import (  # noqa: E402
    SHUTTLE_FILE,
    regenerate_shuttle,
    validate_shuttle_route,
)
from repair_map_pois import audit_and_repair_map, write_poi_report  # noqa: E402

MAP_NAME = "KumpulaCampus"
MAP_DATA = SCENARIOS_DIR / "analysis" / "data" / "maps"
REPORTS = SCENARIOS_DIR / "analysis" / "reports" / "maps"
BASE_CAMPUS = SCENARIOS_DIR / "base_scenarios" / "02_campus"
CORPUS_CAMPUS = SCENARIOS_DIR / "corpus_v1" / "02_campus"

CAMPUS_OK_M = 25.0
CAMPUS_WARN_M = 60.0

EXPECTED_FILES = (
    "roads.wkt",
    "A_homes.wkt",
    "A_offices.wkt",
    "A_meetingspots.wkt",
    "A_campus_shuttle.wkt",
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
            if fname == "roads.wkt" or fname.endswith("_shuttle.wkt") or fname.endswith("_bus.wkt"):
                ls = parse_linestrings(wkt_p)
                n_verts = sum(len(s) for s in ls) if ls else 0
                parseable = "yes" if ls else "no"
            elif fname.endswith(".wkt"):
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
    path = REPORTS / "KumpulaCampus_family_fit_report.md"
    path.write_text(
        """# KumpulaCampus — family fit (02_campus)

Generated as part of campus map finalization.

## Why this map fits 02_campus

| Criterion | KumpulaCampus |
|-----------|---------------|
| Geographic scale | Compact university campus (~1.1 km × 1.0 km sim window) |
| Network | OSM `all` — internal roads + pedestrian paths (4059 segments) |
| POI density | 30 homes, 20 offices, 15 meeting spots — sufficient for class/exam/social scenarios |
| Coverage | ~51% road length / worldSize area — high for a bounded campus |
| vs urban | No bus-integrated WDM; SPMM only; smaller, pedestrian-dominant |

## Scenario mapping

| Scenario | Methodological role on this map |
|----------|-----------------------------------|
| C1 ClassChange | Frequent between-class movement, moderate speed/wait |
| C2 ExamDay | Long stays, low speed, exam-day static behavior |
| C3 Hackathon 24h | 86400 s horizon, very long waits, slow persistent nodes |
| C4 CampusEvent | Two traffic peaks (ingress/egress) — renamed from Stadium; auditorium-scale event |
| C5 Library_Quiet | Low speed, long waits, sparse movement |
| C6 EmergencyDrill | Fast SPMM evacuation (high speed, low wait); no LinearMovement |

## C4 naming decision

`C4_Stadium_IngressEgress` → **`C4_CampusEvent_IngressEgress`**: the OSM extract has no sports stadium polygon; the scenario models a **mass campus event** (lecture hall, open day, graduation) with bimodal message load, not athletic ingress/egress.

## Shuttle asset

`A_campus_shuttle.wkt` is an **optional documentation route** (not referenced in `.settings`). Figures show resolved path (solid) vs stop order (dotted).

## Difference from HelsinkiDowntown (01_urban)

- Urban: dense CBD, WorkingDayMovement + bus integration, 2093×1838 m.
- Campus: single institution footprint, SPMM only, shuttle for visualization only.
""",
        encoding="utf-8",
    )


def write_validation_report(
    geom_rows: list[dict],
    poi_val: list[dict],
    shuttle_val: dict,
    settings_fails: int,
) -> None:
    blocking = [r for r in geom_rows if r["status"] == "FAIL"]
    path = REPORTS / "KumpulaCampus_validation_report.md"
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
            lines.append(f"- `{r['asset']}`")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Acceptable warnings",
            "",
            f"- POI points in 25–60 m band: see poi_report",
            f"- Shuttle: {shuttle_val.get('status', 'n/a')} — {shuttle_val.get('notes', '')}",
            "",
            "## Methodological decisions",
            "",
            "- Single Kumpula OSM extract for all `02_campus` scenarios (1524×1416 m).",
            "- C4 renamed to CampusEvent; C6 LinearMovement residuals removed.",
            "- Shuttle not in simulation settings.",
            "",
            f"- Settings audit FAIL count: {settings_fails}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_affected_scenarios() -> list[dict]:
    rows: list[dict] = []
    for root, tree in ((BASE_CAMPUS, "base_scenarios"), (CORPUS_CAMPUS, "corpus_v1")):
        if not root.is_dir():
            continue
        for sp in sorted(root.glob("*.settings")):
            reason = "campus_map_wkt_or_settings"
            if "C4_CampusEvent" in sp.name:
                reason = "c4_rename"
            elif "C6_EmergencyDrill" in sp.name:
                reason = "c6_linear_cleanup"
            rows.append(
                {
                    "scenario_settings": sp.name,
                    "tree": tree,
                    "reason": reason,
                    "resimulation_recommended": "yes_if_wkt_changed",
                }
            )
    return rows


def write_resimulation_plan(n: int) -> None:
    path = REPORTS / "KumpulaCampus_resimulation_plan.md"
    path.write_text(
        f"""# {MAP_NAME} — re-simulation plan

Generated: {datetime.now().isoformat(timespec='seconds')}

## Recommendation

- **Re-run campus simulations** if POI or shuttle WKT changed before publishing new KPIs.
- **C4 rename / C6 cleanup** change scenario names and settings structure only; mobility geometry unchanged — update external pipelines referencing `C4_Stadium_*`.

## Scope

- Affected settings files: **{n}** (6 base × 12 TP + variants).
- Traffic Profile blocks (`Events*`) not modified.

## Priority

1. C1, C4 (class change, event peaks)
2. C3 hackathon (24h)
3. C2, C5, C6 as needed
""",
        encoding="utf-8",
    )


def print_summary(**kwargs) -> None:
    print("\n" + "=" * 60)
    print(f"GLOBAL: {'PASS' if kwargs['global_pass'] else 'FAIL'}")
    print(f"POIs reviewed: {kwargs['poi_reviewed']}")
    print(f"POIs corrected: {kwargs['poi_corrected']}")
    print(f"Shuttle routes reviewed: {kwargs['routes_reviewed']}")
    print(f"Shuttle routes corrected: {kwargs['routes_corrected']}")
    print(f"Campus scenarios: {kwargs['n_scenarios']}")
    print(f"Files modified: {len(kwargs['modified'])}")
    print(f"Files generated: {len(kwargs['generated'])}")
    print("Re-simulation: RECOMMENDED if POI/shuttle WKT changed")
    print("=" * 60)


def main() -> int:
    ap = argparse.ArgumentParser(description="Finalize KumpulaCampus for paper")
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
    inv_csv = MAP_DATA / "KumpulaCampus_asset_inventory.csv"
    with inv_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asset_rows[0].keys()))
        w.writeheader()
        w.writerows(asset_rows)
    generated.append(str(inv_csv))

    meta = load_map_metadata(WKT_DIR / MAP_NAME)
    geom_rows = build_geometry_validation(meta)
    geom_csv = MAP_DATA / "KumpulaCampus_geometry_validation.csv"
    with geom_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(geom_rows[0].keys()))
        w.writeheader()
        w.writerows(geom_rows)
    generated.append(str(geom_csv))

    write_family_fit_report()
    generated.append(str(REPORTS / "KumpulaCampus_family_fit_report.md"))

    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copytree(WKT_DIR / MAP_NAME, WKT_DIR / f"_backup_kumpula_poi_{stamp}" / MAP_NAME, dirs_exist_ok=True)

    poi_val, poi_corr, poi_mod = audit_and_repair_map(
        MAP_NAME,
        apply=apply,
        install=False,
        ok_m=CAMPUS_OK_M,
        warn_m=CAMPUS_WARN_M,
    )
    modified.extend(poi_mod)
    poi_csv = MAP_DATA / "KumpulaCampus_poi_validation.csv"
    with poi_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(poi_val[0].keys()))
        w.writeheader()
        w.writerows(poi_val)
    if poi_corr:
        with (MAP_DATA / "KumpulaCampus_poi_corrections.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(poi_corr[0].keys()))
            w.writeheader()
            w.writerows(poi_corr)
    write_poi_report(
        MAP_NAME,
        poi_val,
        poi_corr,
        REPORTS / "KumpulaCampus_poi_report.md",
        ok_m=CAMPUS_OK_M,
        warn_m=CAMPUS_WARN_M,
        threshold_label="campus",
    )

    map_dir = WKT_DIR / MAP_NAME
    rng = random.Random(args.seed)
    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copytree(map_dir, WKT_DIR / f"_backup_kumpula_shuttle_{stamp}" / MAP_NAME, dirs_exist_ok=True)
    shuttle_corr = regenerate_shuttle(map_dir, rng, apply=apply)
    if apply:
        modified.append(f"maps/wkt/{MAP_NAME}/{SHUTTLE_FILE}")

    wx, wy = world_size_from_metadata(meta)
    rg, _, _ = load_road_graph(MAP_NAME)
    shuttle_path = map_dir / SHUTTLE_FILE
    shuttle_val = validate_shuttle_route(rg, shuttle_path, wx, wy) if shuttle_path.is_file() else {"status": "FAIL"}
    with (MAP_DATA / "KumpulaCampus_shuttle_route_validation.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(shuttle_val.keys()))
        w.writeheader()
        w.writerow(shuttle_val)
    with (MAP_DATA / "KumpulaCampus_shuttle_route_corrections.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(shuttle_corr[0].keys()))
        w.writeheader()
        w.writerows(shuttle_corr)
    (REPORTS / "KumpulaCampus_shuttle_route_report.md").write_text(
        f"# Shuttle route\n\n- **{shuttle_val.get('route_file')}**: {shuttle_val.get('status')} — {shuttle_val.get('notes', '')}\n",
        encoding="utf-8",
    )

    if apply and args.install:
        dst = DATA_DIR / MAP_NAME
        dst.mkdir(parents=True, exist_ok=True)
        for p in list_route_wkt_files(map_dir) + list_poi_wkt_files(map_dir):
            shutil.copy2(p, dst / p.name)

    audit_script = _SETUP / "audit_kumpula_campus_settings.py"
    cmd = [sys.executable, str(audit_script)]
    if apply:
        cmd += ["--rename-c4", "--cleanup-c6", "--apply"]
    subprocess.run(cmd, cwd=SCENARIOS_DIR.parent, check=False)

    settings_csv = MAP_DATA / "KumpulaCampus_campus_settings_audit.csv"
    settings_fails = 0
    if settings_csv.is_file():
        with settings_csv.open(encoding="utf-8") as f:
            settings_fails = sum(1 for r in csv.DictReader(f) if r.get("status") == "FAIL")

    write_validation_report(geom_rows, poi_val, shuttle_val, settings_fails)

    affected = build_affected_scenarios()
    with (MAP_DATA / "KumpulaCampus_affected_scenarios.csv").open("w", newline="", encoding="utf-8") as f:
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

    shuttle_fail = shuttle_val.get("status") == "FAIL"
    poi_block = any(r["status"] == "FIX_REQUIRED" and r.get("action") == "none" for r in poi_val)
    geom_fail = any(r["status"] == "FAIL" for r in geom_rows)
    global_pass = not (shuttle_fail or poi_block or geom_fail or settings_fails)

    print_summary(
        global_pass=global_pass,
        poi_reviewed=len(poi_val),
        poi_corrected=len(poi_corr),
        routes_reviewed=1,
        routes_corrected=len(shuttle_corr) if apply else 0,
        n_scenarios=len(affected),
        modified=modified,
        generated=generated,
    )
    return 0 if global_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
