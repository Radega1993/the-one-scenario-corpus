#!/usr/bin/env python3
"""Audit 01_urban .settings for HelsinkiDowntown coherence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import SCENARIOS_DIR  # noqa: E402

MAP_DATA = SCENARIOS_DIR / "analysis" / "data" / "maps"
REPORTS = SCENARIOS_DIR / "analysis" / "reports" / "maps"
BASE_URBAN = SCENARIOS_DIR / "base_scenarios" / "01_urban"
CORPUS_URBAN = SCENARIOS_DIR / "corpus_v1" / "01_urban"
EXPECTED_WS = "2093, 1838"
EXPECTED_MAP = "data/HelsinkiDowntown/roads.wkt"

U2_OLD = "U2_SparseSuburb_HelsinkiDowntown"
U2_NEW = "U2_SparseUrban_HelsinkiDowntown"

ROUTE_FILE_RE = re.compile(r"^Group\d*\.routeFile$")
POI_KEYS = ("homeLocationsFile", "officeLocationsFile", "meetingSpotsFile")

def load_kv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def audit_file(path: Path) -> dict:
    kv = load_kv(path)
    issues: list[str] = []
    tree = "corpus_v1" if "corpus_v1" in path.parts else "base_scenarios"

    scen = kv.get("Scenario.name", path.stem)
    map1 = kv.get("MapBasedMovement.mapFile1", "")
    ws = kv.get("MovementModel.worldSize", "")

    if "HelsinkiMedium" in path.read_text(encoding="utf-8", errors="replace"):
        if "HelsinkiMedium" in map1 or any("HelsinkiMedium" in kv.get(k, "") for k in kv if "File" in k):
            issues.append("HelsinkiMedium in active path")
    if map1 and map1 != EXPECTED_MAP:
        issues.append(f"mapFile1={map1}")
    if ws.replace(" ", "") != EXPECTED_WS.replace(" ", ""):
        issues.append(f"worldSize={ws}")
    if map1 and map1.startswith("/"):
        issues.append("absolute path")

    route_files = [f"{k}={v}" for k, v in kv.items() if ROUTE_FILE_RE.match(k)]
    poi_paths = [v for k, v in kv.items() if k.endswith("LocationsFile") or k.endswith("SpotsFile")]
    for k, v in kv.items():
        if ("File" in k or "routeFile" in k) and v and "HelsinkiDowntown" not in v and "data/" in v:
            issues.append(f"{k} wrong map")

    mm = kv.get("Group.movementModel", kv.get("Group2.movementModel", ""))
    bus_route = kv.get("Group.routeFile", "")
    g2_route = kv.get("Group2.routeFile", "")

    status = "PASS" if not issues else "FAIL"
    return {
        "settings_path": str(path.relative_to(SCENARIOS_DIR.parent)),
        "tree": tree,
        "scenario_name": scen,
        "map_file1": map1,
        "world_size": ws,
        "movement_model": mm,
        "route_file_entries": len(route_files),
        "group_route_file": bus_route,
        "group2_route_file": g2_route,
        "poi_files_ok": all("HelsinkiDowntown" in v for v in poi_paths if v),
        "issues": "; ".join(issues),
        "status": status,
    }

def rename_u2_settings(apply: bool) -> list[str]:
    changed: list[str] = []
    patterns = [
        (BASE_URBAN / f"{U2_OLD}.settings", BASE_URBAN / f"{U2_NEW}.settings"),
    ]
    for tp in sorted(CORPUS_URBAN.glob(f"{U2_OLD}__TP*.settings")):
        new_name = tp.name.replace(U2_OLD, U2_NEW)
        patterns.append((tp, CORPUS_URBAN / new_name))

    for old, new in patterns:
        if not old.is_file():
            continue
        text = old.read_text(encoding="utf-8")
        text = text.replace(f"Scenario.name = {U2_OLD}", f"Scenario.name = {U2_NEW}")
        text = text.replace(U2_OLD, U2_NEW)
        text = text.replace("Sparse suburb", "Sparse urban")
        text = text.replace("Dataset: HelsinkiMedium", "Dataset: HelsinkiDowntown")
        if apply:
            if new.exists():
                new.unlink()
            old.rename(new)
            new.write_text(text, encoding="utf-8")
        changed.append(str(new.relative_to(SCENARIOS_DIR.parent)))
    return changed

def update_manifests(apply: bool) -> None:
    for manifest in (
        SCENARIOS_DIR / "base_scenarios" / "manifest.csv",
        SCENARIOS_DIR / "corpus_v1" / "manifest.csv",
    ):
        if not manifest.is_file():
            continue
        text = manifest.read_text(encoding="utf-8")
        new_text = text.replace(U2_OLD, U2_NEW)
        if apply and new_text != text:
            manifest.write_text(new_text, encoding="utf-8")

def write_settings_report(rows: list[dict], u2_renamed: list[str], path: Path) -> None:
    fails = [r for r in rows if r["status"] == "FAIL"]
    lines = [
        "# HelsinkiDowntown — urban settings audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"- Files audited: {len(rows)}",
        f"- FAIL: {len(fails)}",
        f"- U2 renamed files: {len(u2_renamed)}",
        "",
        "## routeFile on WorkingDayMovement",
        "",
        "Urban scenarios use `Group.busControlSystemNr = -1` so pedestrians use the bus system. "
        "`Group.routeFile` and `Group2.routeFile` must point at `A_bus.wkt` so `getBusStops()` is "
        "initialized (otherwise NPE). This is required by The ONE, not an optional bus overlay.",
        "",
        "## U2 rename",
        "",
        f"`{U2_OLD}` → `{U2_NEW}`: low-density urban scenario on the same downtown map "
        "(fewer hosts/offices), not a geographic suburb.",
        "",
    ]
    if fails:
        lines.extend(["## Failures", ""])
        for r in fails[:20]:
            lines.append(f"- `{r['settings_path']}`: {r['issues']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rename-u2", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows: list[dict] = []
    for root in (BASE_URBAN, CORPUS_URBAN):
        if root.is_dir():
            for sp in sorted(root.glob("*.settings")):
                if "HelsinkiDowntown" in sp.name or U2_OLD in sp.name or U2_NEW in sp.name:
                    rows.append(audit_file(sp))

    u2_renamed: list[str] = []
    if args.rename_u2:
        u2_renamed = rename_u2_settings(apply=args.apply)
        update_manifests(apply=args.apply)

    MAP_DATA.mkdir(parents=True, exist_ok=True)
    out_csv = MAP_DATA / "HelsinkiDowntown_urban_settings_audit.csv"
    if rows:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    write_settings_report(rows, u2_renamed, REPORTS / "HelsinkiDowntown_urban_settings_report.md")
    print(f"Wrote {out_csv} ({len(rows)} files)")
    if u2_renamed:
        print(f"U2 renamed: {len(u2_renamed)} files")
    return 1 if any(r["status"] == "FAIL" for r in rows) else 0

if __name__ == "__main__":
    raise SystemExit(main())