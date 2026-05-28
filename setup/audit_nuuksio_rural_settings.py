#!/usr/bin/env python3
"""Audit 04_rural .settings for NuuksioSparseTrails; fix A_bus paths and rename R1."""

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
BASE_RURAL = SCENARIOS_DIR / "base_scenarios" / "04_rural"
CORPUS_RURAL = SCENARIOS_DIR / "corpus_v1" / "04_rural"

EXPECTED_WS = "2848, 2945"
EXPECTED_MAP = "data/NuuksioSparseTrails/roads.wkt"
LEGACY_BUS = "data/NuuksioSparseTrails/A_bus.wkt"
PATROL_ROUTE = "data/NuuksioSparseTrails/A_ranger_patrol.wkt"
R1_OLD = "R1_Rural_RandomWaypoint"
R1_NEW = "R1_Rural_SparseSPMM"

ROUTE_FILE_RE = re.compile(r"^Group\d*\.routeFile$")
WRONG_MAPS = ("HelsinkiMedium", "HelsinkiDowntown", "ManhattanMidtownGrid", "KumpulaCampus")


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
        if f"data/{bad}/" in text or (bad in map1):
            issues.append(f"wrong map ref: {bad}")

    if map1 and map1 != EXPECTED_MAP:
        issues.append(f"mapFile1={map1}")
    if ws.replace(" ", "") != EXPECTED_WS.replace(" ", ""):
        issues.append(f"worldSize={ws}")

    legacy_bus = sum(
        1 for k, v in kv.items() if ROUTE_FILE_RE.match(k) and v and "A_bus.wkt" in v
    )
    if legacy_bus:
        issues.append(f"{legacy_bus} legacy A_bus routeFile")

    if R1_OLD in path.name or scen == R1_OLD:
        issues.append("R1 legacy name (should be R1_Rural_SparseSPMM)")

    route_refs = {k: v for k, v in kv.items() if ROUTE_FILE_RE.match(k) and v}
    mm = kv.get("Group.movementModel", "")
    g1_mm = kv.get("Group1.movementModel", "")

    status = "PASS" if not issues else "FAIL"
    return {
        "settings_path": str(path.relative_to(SCENARIOS_DIR.parent)),
        "tree": tree,
        "scenario_name": scen,
        "map_file1": map1,
        "world_size": ws,
        "group_movement": mm,
        "group1_movement": g1_mm,
        "route_files": "; ".join(f"{k}={v}" for k, v in sorted(route_refs.items())),
        "legacy_bus_refs": legacy_bus,
        "issues": "; ".join(issues),
        "status": status,
    }


def fix_legacy_bus_paths(apply: bool) -> list[str]:
    changed: list[str] = []
    for root in (BASE_RURAL, CORPUS_RURAL):
        if not root.is_dir():
            continue
        for sp in sorted(root.glob("*.settings")):
            text = sp.read_text(encoding="utf-8", errors="replace")
            if LEGACY_BUS not in text:
                continue
            new_text = text.replace(LEGACY_BUS, PATROL_ROUTE)
            new_text = new_text.replace("Dataset: HelsinkiMedium", "Dataset: NuuksioSparseTrails")
            new_text = new_text.replace("# Dataset: HelsinkiMedium", "# Dataset: NuuksioSparseTrails")
            new_text = new_text.replace("use bus route as \"trail\"", "ranger patrol route on trails")
            new_text = new_text.replace("mismo mapa Helsinki", "mapa NuuksioSparseTrails")
            if apply and new_text != text:
                sp.write_text(new_text, encoding="utf-8")
            if new_text != text:
                changed.append(str(sp.relative_to(SCENARIOS_DIR.parent)))
    return changed


def rename_r1(apply: bool) -> list[str]:
    changed: list[str] = []
    patterns: list[tuple[Path, Path]] = [
        (BASE_RURAL / f"{R1_OLD}.settings", BASE_RURAL / f"{R1_NEW}.settings"),
    ]
    for tp in sorted(CORPUS_RURAL.glob(f"{R1_OLD}__TP*.settings")):
        patterns.append((tp, CORPUS_RURAL / tp.name.replace(R1_OLD, R1_NEW)))

    for old, new in patterns:
        if not old.is_file():
            continue
        text = old.read_text(encoding="utf-8")
        text = text.replace(f"Scenario.name = {R1_OLD}", f"Scenario.name = {R1_NEW}")
        text = text.replace(R1_OLD, R1_NEW)
        text = text.replace("# R1 - Rural random waypoint", "# R1 - Rural sparse SPMM on trails")
        text = text.replace("RandomWaypoint.", "ShortestPathMapBasedMovement on sparse trails.")
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
        SCENARIOS_DIR / "corpus_v1" / "manifest_revision.csv",
    ):
        if not manifest.is_file():
            continue
        text = manifest.read_text(encoding="utf-8")
        new_text = text.replace(R1_OLD, R1_NEW)
        if apply and new_text != text:
            manifest.write_text(new_text, encoding="utf-8")


def write_report(rows: list[dict], bus_fixed: list[str], r1_renamed: list[str]) -> None:
    fails = [r for r in rows if r["status"] == "FAIL"]
    path = REPORTS / "NuuksioSparseTrails_rural_settings_report.md"
    lines = [
        "# NuuksioSparseTrails — rural settings audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"- Files audited: {len(rows)}",
        f"- FAIL: {len(fails)}",
        f"- Legacy A_bus fixes: {len(bus_fixed)}",
        f"- R1 renamed: {len(r1_renamed)}",
        "",
        "## Map and worldSize",
        "",
        f"All map-based rural scenarios: `{EXPECTED_MAP}`, `worldSize = {EXPECTED_WS}`.",
        "",
        "## R4 park rangers",
        "",
        "`Group.routeFile` unified to `A_ranger_patrol.wkt` (file `A_bus.wkt` absent on disk).",
        "",
        "## R1 rename",
        "",
        f"`{R1_OLD}` → `{R1_NEW}`: reflects ShortestPathMapBasedMovement, not RandomWaypoint.",
        "",
        "## Historical analysis CSVs",
        "",
        "Manifests updated; `output_metrics.csv` and other analysis artifacts may still "
        "reference the old R1 name until regenerated.",
        "",
    ]
    if fails:
        lines.extend(["## Failures", ""])
        for r in fails[:20]:
            lines.append(f"- `{r['settings_path']}`: {r['issues']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-legacy-bus", action="store_true")
    ap.add_argument("--rename-r1", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows: list[dict] = []
    for root in (BASE_RURAL, CORPUS_RURAL):
        if root.is_dir():
            for sp in sorted(root.glob("*.settings")):
                rows.append(audit_file(sp))

    bus_fixed: list[str] = []
    r1_renamed: list[str] = []
    if args.fix_legacy_bus:
        bus_fixed = fix_legacy_bus_paths(apply=args.apply)
    if args.rename_r1:
        r1_renamed = rename_r1(apply=args.apply)
        update_manifests(apply=args.apply)

    if args.apply and (bus_fixed or r1_renamed):
        rows = []
        for root in (BASE_RURAL, CORPUS_RURAL):
            if root.is_dir():
                for sp in sorted(root.glob("*.settings")):
                    rows.append(audit_file(sp))

    MAP_DATA.mkdir(parents=True, exist_ok=True)
    out_csv = MAP_DATA / "NuuksioSparseTrails_rural_settings_audit.csv"
    if rows:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    write_report(rows, bus_fixed, r1_renamed)
    print(f"Wrote {out_csv} ({len(rows)} files)")
    if bus_fixed:
        print(f"Fixed A_bus paths: {len(bus_fixed)}")
    if r1_renamed:
        print(f"R1 renamed: {len(r1_renamed)}")
    return 1 if any(r["status"] == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
