#!/usr/bin/env python3
"""Generate map_assets_final_validation.md from validation CSVs."""

from __future__ import annotations

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import SCENARIOS_DIR  # noqa: E402

REPORTS = SCENARIOS_DIR / "analysis" / "reports" / "maps"
DATA = SCENARIOS_DIR / "analysis" / "data"

def read_csv(name: str) -> list[dict]:
    p = DATA / name
    if not p.is_file():
        return []
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main() -> int:
    inv = read_csv("map_assets_inventory.csv")
    bus = read_csv("bus_route_validation.csv")
    poi = read_csv("map_poi_validation.csv")
    semantic = read_csv("map_route_semantic_inventory.csv")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Map assets — final validation",
        "",
        f"Generated: {ts}",
        "",
        "## Executive summary",
        "",
        f"- **Maps inventoried:** {len(inv)}",
        f"- **Bus routes validated:** {len(bus)} ({sum(1 for r in bus if r['status']=='PASS')} PASS, "
        f"{sum(1 for r in bus if r['status']=='WARNING')} WARNING, "
        f"{sum(1 for r in bus if r['status']=='FAIL')} FAIL)",
        f"- **POI files validated:** {len(poi)} ({sum(1 for r in poi if r['status']=='PASS')} PASS, "
        f"{sum(1 for r in poi if r['status']=='WARNING')} WARNING, "
        f"{sum(1 for r in poi if r['status']=='FAIL')} FAIL)",
        "",
        "Auxiliary route WKT files are **routeFile waypoints** for `MapRouteMovement`. "
        "The ONE routes carriers on the **road graph** between stops (Dijkstra). Wiki figures show a **solid resolved path** "
        "and a faint dotted stop-order reference.",
        "",
        "Routes were **regenerated per family** (2026-05-28) with semantic filenames, "
        "graph-coherent waypoints, and backups under `_backup_semantic_regen_*` / `_backup_route_rename_*`. "
        "Settings `routeFile` paths were updated only where already referenced.",
        "",
        "## Maps inventory",
        "",
        "| Map | Family | Source | Bus files | POI counts (H/O/M) | Status |",
        "|-----|--------|--------|-----------|-------------------|--------|",
    ]
    for r in inv:
        lines.append(
            f"| {r['map_name']} | {r['family']} | {r['map_source']} | {r['n_bus_routes']} | "
            f"{r['n_homes']}/{r['n_offices']}/{r['n_meetingspots']} | {r['status']} |"
        )

    if semantic:
        lines.extend(
            [
                "",
                "## Semantic route inventory",
                "",
                "| Map | Current | Recommended | Label | In settings | Action |",
                "|-----|---------|-------------|-------|-------------|--------|",
            ]
        )
        for r in semantic:
            lines.append(
                f"| {r['map_name']} | {r['current_file']} | {r['recommended_file']} | "
                f"{r['semantic_label']} | {r['in_settings']} | {r['action_required']} |"
            )

    lines.extend(["", "## Route files (geometry)", "", "| Map | Route | Status | Max dist (m) | Notes |", "|-----|-------|--------|--------------|-------|"])
    for r in bus:
        lines.append(
            f"| {r['map_name']} | {r['route_file']} | {r['status']} | {r['max_vertex_dist_m']} | {r.get('notes','')} |"
        )

    lines.extend(["", "## POIs", "", "| Map | File | Status | Inside WS % | Max dist (m) | Notes |", "|-----|------|--------|-------------|--------------|-------|"])
    for r in poi:
        lines.append(
            f"| {r['map_name']} | {r['poi_file']} | {r['status']} | {r['pct_inside_world_size']} | "
            f"{r['max_dist_to_road_m']} | {r.get('notes','')} |"
        )

    poi_fails = [r for r in poi if r["status"] == "FAIL"]
    lines.extend(
        [
            "",
            "## Known limitations",
            "",
            "- Some OSM-derived office/meeting POIs remain >50 m from the nearest road segment "
            "(WorkingDayMovement still uses them; see POI table). Rural Nuuksio offices are sparse by design.",
            "- Orphan bus files (e.g. `B_bus.wkt` on maps without `.settings` references) are kept for package consistency.",
            "- Re-simulation recommended for scenarios using repaired routes (urban, vehicles, R4, D5).",
            "",
            "## Reproduction commands",
            "",
            "```bash",
            "python3 scenarios/setup/build_map_route_semantic_inventory.py",
            "python3 scenarios/setup/regenerate_family_routes.py --all --dry-run",
            "python3 scenarios/setup/regenerate_family_routes.py --all --apply --install",
            "python3 scenarios/setup/rename_route_files_semantic.py --apply",
            "python3 scenarios/setup/build_map_assets_inventory.py --include-data",
            "python3 scenarios/setup/validate_maps.py",
            "python3 scenarios/setup/validate_bus_routes.py",
            "python3 scenarios/setup/validate_map_pois.py",
            "python3 scenarios/setup/audit_route_usage.py",
            "python3 scenarios/setup/repair_bus_routes.py --dry-run",
            "scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --validation",
            "```",
            "",
            "## Paper-ready statement",
            "",
            "The benchmark assigns **one fixed map per scenario family** (six OSM extracts in Helsinki and Midtown Manhattan, "
            "plus a synthetic grid for protocol stress controls). Street geometry is imported from OpenStreetMap, "
            "reprojected to metric coordinates, reduced to the largest connected component, and exported as WKT for The ONE. "
            "Auxiliary route files use **semantic names** per family (urban bus, vehicle route, ranger patrol, etc.). "
            "Waypoints sit on the road network; carriers follow shortest paths on the graph between stops. POI and route assets are checked against `worldSize` and road "
            "proximity before inclusion. The `` family uses ****, a synthetic topology "
            "isolated from geographic bias, only for extreme protocol stress experiments outside the 540-scenario environmental core.",
            "",
        ]
    )
    if poi_fails:
        lines.insert(
            lines.index("## Known limitations"),
            "## POI exceptions\n\n"
            + "\n".join(f"- `{r['map_name']}/{r['poi_file']}`: {r.get('notes','')}" for r in poi_fails)
            + "\n",
        )

    out = REPORTS / "map_assets_final_validation.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())