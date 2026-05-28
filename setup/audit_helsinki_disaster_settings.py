#!/usr/bin/env python3
"""Audit 05_disaster .settings for HelsinkiDisrupted; fix D5 Group1 SPMM and comments."""

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
BASE_DISASTER = SCENARIOS_DIR / "base_scenarios" / "05_disaster"
CORPUS_DISASTER = SCENARIOS_DIR / "corpus_v1" / "05_disaster"

EXPECTED_WS = "2067, 2206"
EXPECTED_MAP = "data/HelsinkiDisrupted/roads.wkt"
D5_GLOB = "D5_UAVMule_FastRoute_HelsinkiDisrupted"

ROUTE_FILE_RE = re.compile(r"^Group\d*\.routeFile$")
ROUTE_TYPE_RE = re.compile(r"^Group\d*\.routeType$")
WRONG_MAPS = (
    "HelsinkiMedium",
    "HelsinkiDowntown",
    "ManhattanMidtownGrid",
    "NuuksioSparseTrails",
    "KumpulaCampus",
)


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

    for bad in WRONG_MAPS:
        if f"data/{bad}/" in text or bad in map1:
            issues.append(f"wrong map ref: {bad}")

    if map1 and map1 != EXPECTED_MAP:
        issues.append(f"mapFile1={map1}")
    if ws.replace(" ", "") != EXPECTED_WS.replace(" ", ""):
        issues.append(f"worldSize={ws}")

    legacy_bus = sum(
        1 for k, v in kv.items() if ROUTE_FILE_RE.match(k) and v and ("A_bus.wkt" in v or "B_bus.wkt" in v)
    )
    if legacy_bus:
        issues.append(f"{legacy_bus} legacy bus routeFile")

    g1_mm = kv.get("Group1.movementModel", "")
    g1_route = kv.get("Group1.routeFile", "")
    if D5_GLOB in path.name and g1_mm == "MapRouteMovement" and "roads.wkt" in g1_route:
        issues.append("D5 Group1 MapRouteMovement with roads.wkt (should be SPMM)")

    if "HelsinkiMedium" in text:
        issues.append("legacy HelsinkiMedium in comments")

    route_refs = {k: v for k, v in kv.items() if ROUTE_FILE_RE.match(k) and v}
    status = "PASS" if not issues else "FAIL"
    return {
        "settings_path": str(path.relative_to(SCENARIOS_DIR.parent)),
        "tree": tree,
        "scenario_name": scen,
        "map_file1": map1,
        "world_size": ws,
        "group1_movement": g1_mm,
        "group1_route_file": g1_route,
        "route_files": "; ".join(f"{k}={v}" for k, v in sorted(route_refs.items())),
        "legacy_bus_refs": legacy_bus,
        "issues": "; ".join(issues),
        "status": status,
    }


def fix_d5_group1_spmm(apply: bool) -> list[str]:
    changed: list[str] = []
    paths = [BASE_DISASTER / f"{D5_GLOB}.settings"]
    paths.extend(sorted(CORPUS_DISASTER.glob(f"{D5_GLOB}__TP*.settings")))

    for sp in paths:
        if not sp.is_file():
            continue
        lines_out: list[str] = []
        skip_prefixes = ("Group1.routeFile", "Group1.routeType")
        for raw in sp.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = raw.split("#", 1)[0].strip()
            if any(stripped.startswith(p) for p in skip_prefixes):
                continue
            if stripped == "Group1.movementModel = MapRouteMovement":
                lines_out.append("Group1.movementModel = ShortestPathMapBasedMovement")
                continue
            line = raw
            line = line.replace("Dataset: HelsinkiMedium", "Dataset: HelsinkiDisrupted")
            line = line.replace("# Dataset: HelsinkiMedium", "# Dataset: HelsinkiDisrupted")
            line = line.replace("use bus route as UAV route", "UAV on A_emergency_route.wkt")
            line = line.replace("mismo mapa Helsinki", "mapa HelsinkiDisrupted")
            lines_out.append(line)
        new_text = "\n".join(lines_out) + "\n"
        if apply:
            sp.write_text(new_text, encoding="utf-8")
        changed.append(str(sp.relative_to(SCENARIOS_DIR.parent)))
    return changed


def fix_helsinki_medium_comments(apply: bool) -> list[str]:
    """Fix HelsinkiMedium comments in non-D5 files if any."""
    changed: list[str] = []
    for root in (BASE_DISASTER, CORPUS_DISASTER):
        if not root.is_dir():
            continue
        for sp in sorted(root.glob("*.settings")):
            if D5_GLOB in sp.name:
                continue
            text = sp.read_text(encoding="utf-8", errors="replace")
            if "HelsinkiMedium" not in text:
                continue
            new_text = text.replace("HelsinkiMedium", "HelsinkiDisrupted")
            if apply and new_text != text:
                sp.write_text(new_text, encoding="utf-8")
            if new_text != text:
                changed.append(str(sp.relative_to(SCENARIOS_DIR.parent)))
    return changed


def write_report(rows: list[dict], d5_fixed: list[str], comment_fixed: list[str]) -> None:
    fails = [r for r in rows if r["status"] == "FAIL"]
    path = REPORTS / "HelsinkiDisrupted_disaster_settings_report.md"
    lines = [
        "# HelsinkiDisrupted — disaster settings audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"- Files audited: {len(rows)}",
        f"- FAIL: {len(fails)}",
        f"- D5 Group1 → SPMM fixes: {len(d5_fixed)}",
        f"- Comment fixes: {len(comment_fixed)}",
        "",
        "## D5 UAV mule",
        "",
        "Group1 (civilians/responders): `ShortestPathMapBasedMovement` on `roads.wkt` graph. "
        "Group2 (UAV): `MapRouteMovement` on `A_emergency_route.wkt`.",
        "",
        "## Route assets",
        "",
        "- `A_emergency_route.wkt` — emergency/UAV response path",
        "- `B_mule_route.wkt` — mule/backbone (figure asset; D2 uses SPMM mule without routeFile)",
        "",
    ]
    if fails:
        lines.extend(["## Failures", ""])
        for r in fails[:20]:
            lines.append(f"- `{r['settings_path']}`: {r['issues']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-d5-spmm", action="store_true")
    ap.add_argument("--fix-comments", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows: list[dict] = []
    for root in (BASE_DISASTER, CORPUS_DISASTER):
        if root.is_dir():
            for sp in sorted(root.glob("*.settings")):
                rows.append(audit_file(sp))

    d5_fixed: list[str] = []
    comment_fixed: list[str] = []
    if args.fix_d5_spmm:
        d5_fixed = fix_d5_group1_spmm(apply=args.apply)
    if args.fix_comments:
        comment_fixed = fix_helsinki_medium_comments(apply=args.apply)

    if args.apply and (d5_fixed or comment_fixed):
        rows = []
        for root in (BASE_DISASTER, CORPUS_DISASTER):
            if root.is_dir():
                for sp in sorted(root.glob("*.settings")):
                    rows.append(audit_file(sp))

    MAP_DATA.mkdir(parents=True, exist_ok=True)
    out_csv = MAP_DATA / "HelsinkiDisrupted_disaster_settings_audit.csv"
    if rows:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    write_report(rows, d5_fixed, comment_fixed)
    print(f"Wrote {out_csv} ({len(rows)} files)")
    if d5_fixed:
        print(f"D5 SPMM fixed: {len(d5_fixed)}")
    return 1 if any(r["status"] == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
