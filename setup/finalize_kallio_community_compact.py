#!/usr/bin/env python3
"""Finalize KallioCommunityCompact map for paper-ready 06_social corpus."""

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
from kallio_community_routes import (  # noqa: E402
    ROUTE_FILES,
    load_all_poi_sim,
    regenerate_community_routes,
    validate_community_route,
)
from repair_map_pois import audit_and_repair_map, write_poi_report  # noqa: E402

MAP_NAME = "KallioCommunityCompact"
MAP_DATA = SCENARIOS_DIR / "analysis" / "data" / "maps"
REPORTS = SCENARIOS_DIR / "analysis" / "reports" / "maps"
BASE_SOCIAL = SCENARIOS_DIR / "base_scenarios" / "06_social"
CORPUS_SOCIAL = SCENARIOS_DIR / "corpus_v1" / "06_social"

SOCIAL_OK_M = 40.0
SOCIAL_WARN_M = 100.0

EXPECTED_FILES = (
    "roads.wkt",
    "A_homes.wkt",
    "A_offices.wkt",
    "A_meetingspots.wkt",
    "A_community_route.wkt",
    "B_community_route.wkt",
)

LEGACY_ROUTE_NAMES = ("A_bus.wkt", "B_bus.wkt")


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
                "legacy_bus_wkt_on_disk": legacy_on_disk,
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
    path = REPORTS / "KallioCommunityCompact_family_fit_report.md"
    path.write_text(
        """# KallioCommunityCompact — family fit (06_social)

Generated as part of social map finalization.

## Why this map fits 06_social

| Criterion | KallioCommunityCompact |
|-----------|------------------------|
| Geographic scale | OSM Kallio, Helsinki (EPSG:3067), sim window **1458 × 1529 m** |
| Network | Compact urban neighbourhood (~7204 segments, ~2741 nodes) |
| Mobility | ClusterMovement (S1, S6) and ShortestPathMapBasedMovement (S2–S5) |
| Methodological value | Dense residential fabric for community contact and mixing studies |
| vs HelsinkiDowntown | Commute-scale CBD — not neighbourhood community dynamics |
| vs campus / rural | Institutional or sparse trail context — not urban barrio |

## Paper-ready statement

> KallioCommunityCompact is a compact urban-community map derived from OSM Kallio. It provides a realistic spatial backdrop for social DTN scenarios: dense street fabric and POI layers for map-constrained mobility (S2–S5), while ClusterMovement scenarios (S1, S6) impose community structure through cluster centers and ranges rather than path constraints on the road network.

## ClusterMovement vs map context

In scenarios based on **ClusterMovement** (S1, S6), community structure is explicitly imposed through `clusterCenter` and `clusterRange`. The road network is **not** used as a path constraint; the map supplies spatial context and a consistent coordinate frame only.

| Mode | Scenarios | Path constraint |
|------|-----------|-----------------|
| Cluster-based | S1 (4 clusters), S6 (12 microclusters) | No — cluster geometry only |
| Map-based | S2–S5 | Yes — SPMM on `roads.wkt` |

## Scenario mapping (S1–S6)

| ID | Category | Movement |
|----|----------|----------|
| S1 | social_strong_communities | ClusterMovement ×4 |
| S2 | social_weak_communities | SPMM |
| S3 | social_periodic_meetings | SPMM |
| S4 | social_random_mixing_control | SPMM |
| S5 | social_two_layer_population | SPMM |
| S6 | social_persistent_family_groups | ClusterMovement ×12 |

See `KallioCommunityCompact_social_scenario_classification.md` for full notes.
""",
        encoding="utf-8",
    )


def write_runtime_risk_report() -> None:
    path = REPORTS / "KallioCommunityCompact_social_runtime_risk.md"
    path.write_text(
        """# KallioCommunityCompact — social runtime risk

Generated as part of social map finalization.

## High-contact scenarios

### S1 — Strong communities (4 clusters, 110 hosts)

- **Movement:** ClusterMovement ×4, no inter-cluster bridge in base design.
- **Router:** EpidemicRouter on all groups.
- **Risk:** Dense clusters + epidemic forwarding → very high intra-cluster contacts and message copies, especially under TP03/TP06/TP07/TP09/TP10 (shorter intervals, larger messages, more hosts).
- **Interpretation:** Stress benchmark for community isolation and overload — not a map geometry error.

### S6 — Family groups (12 microclusters)

- **Movement:** ClusterMovement ×12, `clusterRange=16` (tight microclusters).
- **Risk:** Frequent intra-cluster pairwise contact; persistent family-scale structure.
- **Interpretation:** Tests long-lived small communities; timeouts under heavy TP are protocol/TP limits, not WKT defects.

## Map-based scenarios (S2–S5)

- SPMM on compact Kallio graph: moderate path diversity, realistic urban mixing.
- S4 explicitly avoids POI/cluster attractors — control for “no hotspots”.
- S5 two-layer (students vs staff) increases heterogeneity without cluster geometry.

## Recommendations

1. **Keep EpidemicRouter** as the social-family stress benchmark unless methodology explicitly requires another router.
2. Document simulation **timeouts** as Traffic Profile / protocol limitations when they occur under TP stress — not as map misconfiguration.
3. **Do not** reduce `nrofHosts` or `clusterRange` without methodological justification; changes would break cross-scenario comparability.
4. Community routes (`A_community_route.wkt`, `B_community_route.wkt`) are **figure assets only** — no `routeFile` in settings; they do not affect runtime mobility.

## Excluded from runtime scope

- Assigning `routeFile` to social scenarios.
- Modifying `Events*` traffic profile blocks during map finalization.
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
    path = REPORTS / "KallioCommunityCompact_validation_report.md"
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
            "- Route origin/border WARNING (sim frame SW corner)",
            "- POI 40–100 m from road: documented WARNING band (social thresholds)",
            "- Low delivery in S1 under heavy TP: methodological (cluster isolation)",
            "",
            "## Methodological decisions",
            "",
            "- Single OSM Kallio extract for all `06_social` scenarios.",
            "- ClusterMovement (S1, S6): map context only, not path constraint.",
            "- Community routes optional for figures; no `routeFile` in corpus.",
            "",
            f"- Settings audit FAIL count: {settings_fails}",
        ]
    )
    for r in route_vals:
        lines.append(f"- Route {r['route_file']}: {r.get('status')} — {r.get('notes', '')}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_affected_scenarios() -> list[dict]:
    rows: list[dict] = []
    for root, tree in ((BASE_SOCIAL, "base_scenarios"), (CORPUS_SOCIAL, "corpus_v1")):
        if not root.is_dir():
            continue
        for sp in sorted(root.glob("*.settings")):
            rows.append(
                {
                    "scenario_settings": sp.name,
                    "tree": tree,
                    "reason": "social_map_wkt_or_poi",
                    "resimulation_recommended": "yes_if_wkt_or_poi_changed",
                }
            )
    return rows


def write_resimulation_plan(n: int) -> None:
    path = REPORTS / "KallioCommunityCompact_resimulation_plan.md"
    path.write_text(
        f"""# {MAP_NAME} — re-simulation plan

Generated: {datetime.now().isoformat(timespec='seconds')}

## Recommendation

- **Re-run 06_social simulations** if POI or community route WKT changed before publishing new KPIs.
- **No movement-model changes** expected in this finalization — comparability preserved.

## Scope

- Affected settings files: **{n}** (6 base × 12 TP + corpus variants).
- Traffic Profile blocks (`Events*`) not modified.

## Priority

1. S1, S6 (ClusterMovement + Epidemic stress scenarios)
2. S2–S5 (SPMM) if comparing POI snap before/after
3. TP variants with short intervals / large messages (TP03, TP06, TP07, TP09, TP10)
""",
        encoding="utf-8",
    )


def write_final_decision(global_pass: bool, map_based: int, cluster_based: int) -> None:
    path = REPORTS / "KallioCommunityCompact_final_decision.md"
    status = "PASS — paper-ready" if global_pass else "FAIL — see validation_report"
    path.write_text(
        f"""# KallioCommunityCompact — final decision

**Status:** {status}

Generated: {datetime.now().isoformat(timespec='seconds')}

## Summary

KallioCommunityCompact is the sole map for **06_social**. Finalization covers POI audit (40/100 m),
community route validation/regeneration (figure assets), settings audit (78 files), scenario classification,
runtime risk documentation, figures, and wiki.

## Scenario classification

- Map-based SPMM (S2–S5): {map_based} base scenarios
- Cluster-based (S1, S6): {cluster_based} base scenarios

## ClusterMovement note

In scenarios based on ClusterMovement (S1, S6), community structure is explicitly imposed through cluster centers and ranges. The road network is not used as a path constraint; the compact urban map provides spatial context and a consistent coordinate system.

## Reproducibility

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_kallio_community_compact.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_kallio_community_compact.py --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps KallioCommunityCompact --validation
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps KallioCommunityCompact --paper-ready
bash scenarios/setup/bootstrap_maps.sh --install
```

## Artifacts

| Artifact | Path |
|----------|------|
| Asset inventory | `analysis/data/maps/KallioCommunityCompact_asset_inventory.csv` |
| Classification | `analysis/data/maps/KallioCommunityCompact_social_scenario_classification.csv` |
| POI report | `analysis/reports/maps/KallioCommunityCompact_poi_report.md` |
| Routes | `analysis/data/maps/KallioCommunityCompact_route_validation.csv` |
| Settings audit | `analysis/data/maps/KallioCommunityCompact_social_settings_audit.csv` |
| Runtime risk | `analysis/reports/maps/KallioCommunityCompact_social_runtime_risk.md` |
| Validation figure | `analysis/figures/maps/KallioCommunityCompact_validation.png` |
| Paper figure | `analysis/figures/paper/maps/KallioCommunityCompact_paper_ready.png` |
| Wiki | `.wiki-clone/11-Social-Family.md` |

## Excluded

Other map families; OSM full regen; Traffic Profile changes; `routeFile` assignment; automatic re-simulation.
""",
        encoding="utf-8",
    )


def print_summary(**kwargs) -> None:
    print("\n" + "=" * 60)
    print(f"GLOBAL: {'PASS' if kwargs['global_pass'] else 'FAIL'}")
    print(f"POIs reviewed: {kwargs['poi_reviewed']}")
    print(f"POIs corrected: {kwargs['poi_corrected']}")
    print(f"Community routes reviewed: {kwargs['routes_reviewed']}")
    print(f"Community routes corrected: {kwargs['routes_corrected']}")
    print(f"Map-based scenarios (S2–S5): {kwargs.get('map_based', 0)}")
    print(f"Cluster-based scenarios (S1, S6): {kwargs.get('cluster_based', 0)}")
    print(f"Social scenarios (settings): {kwargs['n_scenarios']}")
    print(f"Files modified: {len(kwargs['modified'])}")
    print(f"Files generated: {len(kwargs['generated'])}")
    print("Re-simulation: RECOMMENDED if POI/route WKT changed")
    print("=" * 60)


def main() -> int:
    ap = argparse.ArgumentParser(description="Finalize KallioCommunityCompact for paper")
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
    inv_csv = MAP_DATA / "KallioCommunityCompact_asset_inventory.csv"
    with inv_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asset_rows[0].keys()))
        w.writeheader()
        w.writerows(asset_rows)
    generated.append(str(inv_csv))

    meta = load_map_metadata(WKT_DIR / MAP_NAME)
    geom_rows = build_geometry_validation(meta)
    geom_csv = MAP_DATA / "KallioCommunityCompact_geometry_validation.csv"
    with geom_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(geom_rows[0].keys()))
        w.writeheader()
        w.writerows(geom_rows)
    generated.append(str(geom_csv))

    write_family_fit_report()
    generated.append(str(REPORTS / "KallioCommunityCompact_family_fit_report.md"))

    write_runtime_risk_report()
    generated.append(str(REPORTS / "KallioCommunityCompact_social_runtime_risk.md"))

    classify_script = _SETUP / "classify_kallio_social_scenarios.py"
    subprocess.run([sys.executable, str(classify_script)], cwd=SCENARIOS_DIR.parent, check=False)

    map_based = cluster_based = 0
    class_csv = MAP_DATA / "KallioCommunityCompact_social_scenario_classification.csv"
    if class_csv.is_file():
        with class_csv.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("map_constrained", "").lower() in ("true", "1", "yes"):
                    map_based += 1
                else:
                    cluster_based += 1

    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copytree(
            WKT_DIR / MAP_NAME,
            WKT_DIR / f"_backup_kallio_poi_{stamp}" / MAP_NAME,
            dirs_exist_ok=True,
        )

    poi_val, poi_corr, poi_mod = audit_and_repair_map(
        MAP_NAME,
        apply=apply,
        install=False,
        ok_m=SOCIAL_OK_M,
        warn_m=SOCIAL_WARN_M,
    )
    modified.extend(poi_mod)
    poi_csv = MAP_DATA / "KallioCommunityCompact_poi_validation.csv"
    with poi_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(poi_val[0].keys()))
        w.writeheader()
        w.writerows(poi_val)
    if poi_corr:
        with (MAP_DATA / "KallioCommunityCompact_poi_corrections.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(poi_corr[0].keys()))
            w.writeheader()
            w.writerows(poi_corr)
    write_poi_report(
        MAP_NAME,
        poi_val,
        poi_corr,
        REPORTS / "KallioCommunityCompact_poi_report.md",
        ok_m=SOCIAL_OK_M,
        warn_m=SOCIAL_WARN_M,
        threshold_label="social",
    )

    map_dir = WKT_DIR / MAP_NAME
    rng = random.Random(args.seed)
    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copytree(
            map_dir,
            WKT_DIR / f"_backup_kallio_community_routes_{stamp}" / MAP_NAME,
            dirs_exist_ok=True,
        )
    route_corr = regenerate_community_routes(map_dir, rng, apply=apply)
    if apply:
        for rf in ROUTE_FILES:
            modified.append(f"maps/wkt/{MAP_NAME}/{rf}")

    wx, wy = world_size_from_metadata(meta)
    rg, roads_path, _ = load_road_graph(MAP_NAME)
    poi_pts = load_all_poi_sim(map_dir)
    stops_by_file: dict[str, list] = {}
    from kallio_community_routes import _route_stops_sim

    route_vals: list[dict] = []
    for rf in ROUTE_FILES:
        p = map_dir / rf
        if p.is_file():
            stops_by_file[rf] = _route_stops_sim(p, roads_path)

    for rf in ROUTE_FILES:
        p = map_dir / rf
        other_key = "B_community_route.wkt" if rf == "A_community_route.wkt" else "A_community_route.wkt"
        other = stops_by_file.get(other_key)
        if p.is_file():
            route_vals.append(
                validate_community_route(rg, p, wx, wy, other_stops=other, poi_pts=poi_pts, roads_path=roads_path)
            )
        else:
            route_vals.append({"route_file": rf, "status": "FAIL", "notes": "missing"})

    val_csv = MAP_DATA / "KallioCommunityCompact_route_validation.csv"
    with val_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(route_vals[0].keys()))
        w.writeheader()
        w.writerows(route_vals)
    with (MAP_DATA / "KallioCommunityCompact_route_corrections.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(route_corr[0].keys()))
        w.writeheader()
        w.writerows(route_corr)
    notes = "; ".join(f"{r['route_file']}: {r.get('status')} — {r.get('notes', '')}" for r in route_vals)
    (REPORTS / "KallioCommunityCompact_route_report.md").write_text(
        f"# Community routes\n\n{notes}\n", encoding="utf-8"
    )

    if apply and args.install:
        dst = DATA_DIR / MAP_NAME
        dst.mkdir(parents=True, exist_ok=True)
        for p in list_route_wkt_files(map_dir) + list_poi_wkt_files(map_dir):
            shutil.copy2(p, dst / p.name)

    audit_script = _SETUP / "audit_kallio_social_settings.py"
    subprocess.run([sys.executable, str(audit_script)], cwd=SCENARIOS_DIR.parent, check=False)

    settings_csv = MAP_DATA / "KallioCommunityCompact_social_settings_audit.csv"
    settings_fails = 0
    if settings_csv.is_file():
        with settings_csv.open(encoding="utf-8") as f:
            settings_fails = sum(1 for r in csv.DictReader(f) if r.get("status") == "FAIL")

    write_validation_report(geom_rows, poi_val, route_vals, settings_fails)

    affected = build_affected_scenarios()
    if affected:
        with (MAP_DATA / "KallioCommunityCompact_affected_scenarios.csv").open("w", newline="", encoding="utf-8") as f:
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

    write_final_decision(global_pass, map_based, cluster_based)

    print_summary(
        global_pass=global_pass,
        poi_reviewed=len(poi_val),
        poi_corrected=len(poi_corr),
        routes_reviewed=len(route_vals),
        routes_corrected=len(route_corr) if apply else 0,
        map_based=map_based,
        cluster_based=cluster_based,
        n_scenarios=len(affected),
        modified=modified,
        generated=generated,
    )
    return 0 if global_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
