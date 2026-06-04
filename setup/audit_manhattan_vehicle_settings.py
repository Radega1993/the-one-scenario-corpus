#!/usr/bin/env python3
"""Audit 03_vehicles .settings for ManhattanMidtownGrid; fix legacy A_bus routeFile paths."""

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
BASE_VEH = SCENARIOS_DIR / "base_scenarios" / "03_vehicles"
CORPUS_VEH = SCENARIOS_DIR / "corpus_v1" / "03_vehicles"

EXPECTED_WS = "2500, 2366"
EXPECTED_MAP = "data/ManhattanMidtownGrid/roads.wkt"
LEGACY_BUS = "data/ManhattanMidtownGrid/A_bus.wkt"
VEHICLE_A = "data/ManhattanMidtownGrid/A_vehicle_route.wkt"
VEHICLE_B = "data/ManhattanMidtownGrid/B_vehicle_route.wkt"

ROUTE_FILE_RE = re.compile(r"^Group\d*\.routeFile$")

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
    text = path.read_text(encoding="utf-8", errors="replace")

    scen = kv.get("Scenario.name", path.stem)
    map1 = kv.get("MapBasedMovement.mapFile1", "")
    ws = kv.get("MovementModel.worldSize", "")

    for bad in ("HelsinkiMedium", "HelsinkiDowntown", "KumpulaCampus", "HelsinkiDowntown"):
        if bad in text and (bad in map1 or f"data/{bad}" in text):
            issues.append(f"wrong map: {bad}")

    if map1 and map1 != EXPECTED_MAP:
        issues.append(f"mapFile1={map1}")
    if ws.replace(" ", "") != EXPECTED_WS.replace(" ", ""):
        issues.append(f"worldSize={ws}")

    route_refs = {k: v for k, v in kv.items() if ROUTE_FILE_RE.match(k) and v}
    legacy_bus = sum(1 for v in route_refs.values() if "A_bus.wkt" in v or "B_bus.wkt" in v)
    if legacy_bus:
        issues.append(f"{legacy_bus} legacy A_bus/B_bus routeFile refs")

    g1_route = kv.get("Group1.routeFile", "")
    g2_route = kv.get("Group2.routeFile", "")

    status = "PASS" if not issues else "FAIL"
    return {
        "settings_path": str(path.relative_to(SCENARIOS_DIR.parent)),
        "tree": tree,
        "scenario_name": scen,
        "map_file1": map1,
        "world_size": ws,
        "group_movement": kv.get("Group.movementModel", ""),
        "group1_movement": kv.get("Group1.movementModel", ""),
        "group1_route_file": g1_route,
        "group2_route_file": g2_route,
        "legacy_bus_route_refs": legacy_bus,
        "uses_poi_files": any(
            k.endswith("LocationsFile") or k.endswith("SpotsFile") for k in kv if kv[k]
        ),
        "issues": "; ".join(issues),
        "status": status,
    }

def fix_legacy_bus_paths(apply: bool) -> list[str]:
    changed: list[str] = []
    for root in (BASE_VEH, CORPUS_VEH):
        if not root.is_dir():
            continue
        for sp in sorted(root.glob("*.settings")):
            text = sp.read_text(encoding="utf-8", errors="replace")
            if LEGACY_BUS not in text and "B_bus.wkt" not in text:
                continue
            new_text = text.replace(LEGACY_BUS, VEHICLE_A).replace(
                "data/ManhattanMidtownGrid/B_bus.wkt", VEHICLE_B
            )
            new_text = new_text.replace("Dataset: HelsinkiMedium", "Dataset: ManhattanMidtownGrid")
            new_text = new_text.replace("# Dataset: HelsinkiMedium", "# Dataset: ManhattanMidtownGrid")
            if apply and new_text != text:
                sp.write_text(new_text, encoding="utf-8")
            if new_text != text:
                changed.append(str(sp.relative_to(SCENARIOS_DIR.parent)))
    return changed

def write_report(rows: list[dict], fixed: list[str]) -> None:
    fails = [r for r in rows if r["status"] == "FAIL"]
    path = REPORTS / "ManhattanMidtownGrid_vehicle_settings_report.md"
    lines = [
        "# ManhattanMidtownGrid — vehicle settings audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"- Files audited: {len(rows)}",
        f"- FAIL: {len(fails)}",
        f"- Legacy A_bus path fixes: {len(fixed)}",
        "",
        "## Legacy Group.routeFile",
        "",
        "`A_bus.wkt` does not exist on disk. Replaced with `A_vehicle_route.wkt` (and `B_bus` → `B_vehicle_route`) "
        "for WDM scenarios with `busControlSystemNr = -1`. V1/V2 MapRouteMovement uses `Group1.routeFile` only.",
        "",
        "## Scenarios",
        "",
        "| ID | Model | Routes | POI |",
        "|----|-------|--------|-----|",
        "| V1 | MapRouteMovement (taxis) | Group1 → A_vehicle | No |",
        "| V2 | MapRouteMovement (taxis) | Group1 → A_vehicle | No |",
        "| V3 | BusMovement | A + B vehicle | No |",
        "| V4 | WDM + bus | A_vehicle | Yes |",
        "| V5 | WDM + bus | A_vehicle | Yes |",
        "",
    ]
    if fails:
        lines.extend(["## Failures", ""])
        for r in fails[:15]:
            lines.append(f"- `{r['settings_path']}`: {r['issues']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-legacy-bus", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows: list[dict] = []
    for root in (BASE_VEH, CORPUS_VEH):
        if root.is_dir():
            for sp in sorted(root.glob("*.settings")):
                rows.append(audit_file(sp))

    fixed: list[str] = []
    if args.fix_legacy_bus:
        fixed = fix_legacy_bus_paths(apply=args.apply)

    if args.apply and fixed:
        rows = []
        for root in (BASE_VEH, CORPUS_VEH):
            if root.is_dir():
                for sp in sorted(root.glob("*.settings")):
                    rows.append(audit_file(sp))

    MAP_DATA.mkdir(parents=True, exist_ok=True)
    out_csv = MAP_DATA / "ManhattanMidtownGrid_vehicle_settings_audit.csv"
    if rows:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    write_report(rows, fixed)
    print(f"Wrote {out_csv} ({len(rows)} files)")
    if fixed:
        print(f"Fixed legacy bus paths: {len(fixed)} files")
    return 1 if any(r["status"] == "FAIL" for r in rows) else 0

if __name__ == "__main__":
    raise SystemExit(main())