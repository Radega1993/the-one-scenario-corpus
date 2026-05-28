#!/usr/bin/env python3
"""Classify 04_rural base scenarios for NuuksioSparseTrails."""

from __future__ import annotations

import argparse
import csv
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

# scenario stem -> (category, role notes)
CLASSIFICATION: dict[str, tuple[str, str]] = {
    "R1_Rural_SparseSPMM": (
        "rural_realistic",
        "Sparse SPMM on trails; few hosts; renamed from RandomWaypoint misnomer",
    ),
    "R1_Rural_RandomWaypoint": (
        "rural_realistic",
        "Legacy name: SPMM on Nuuksio (pending rename to R1_Rural_SparseSPMM)",
    ),
    "R2_VillagesTrails_ThreeClusters": (
        "rural_realistic",
        "Three ClusterMovement villages on trail graph",
    ),
    "R3_WildlifeTracking": (
        "rural_realistic",
        "Dispersed wildlife/sensor nodes; SPMM",
    ),
    "R4_ParkRangers_NuuksioSparseTrails": (
        "rural_realistic",
        "Anchor scenario: MapRouteMovement on A_ranger_patrol.wkt",
    ),
    "R5_MountainRescue": (
        "rural_realistic",
        "Mountain rescue proxy; SPMM on sparse trails",
    ),
    "R6_SparseLongRange": (
        "rural_extreme_control",
        "Sensitivity: elevated transmitRange in sparse environment",
    ),
    "R7_SparseTinyBuffer": (
        "rural_extreme_control",
        "Sensitivity: minimal buffer in sparse environment",
    ),
    "R8_IntermittentPower": (
        "rural_realistic",
        "Rural technology: intermittent connectivity/power",
    ),
    "R9_ExtremeRange_200m": (
        "rural_extreme_control",
        "Sensitivity: 200 m range (extreme for rural radio)",
    ),
    "R10_TinyRange_5m": (
        "rural_extreme_control",
        "Sensitivity: 5 m range; low delivery expected by design",
    ),
    "R11_SpeedExtremeLow": (
        "rural_extreme_control",
        "Sensitivity: very low movement speed",
    ),
    "R12_SpeedExtremeHigh": (
        "rural_extreme_control",
        "Sensitivity: very high movement speed on trails",
    ),
}


def load_kv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def classify_base(path: Path) -> dict:
    kv = load_kv(path)
    stem = path.stem
    scen = kv.get("Scenario.name", stem)
    map1 = kv.get("MapBasedMovement.mapFile1", "")
    mm = kv.get("Group.movementModel", "")
    g1_mm = kv.get("Group1.movementModel", mm)
    route = kv.get("Group1.routeFile", kv.get("Group.routeFile", ""))
    n_groups = kv.get("Scenario.nrofHostGroups", "1")
    hosts = kv.get("Group.nrofHosts", kv.get("Group1.nrofHosts", ""))
    rng = kv.get("bt0.transmitRange", "")

    cat, notes = CLASSIFICATION.get(stem, ("needs_review", "unclassified"))
    uses_nuuksio = "NuuksioSparseTrails" in map1
    uses_patrol = "A_ranger_patrol" in route

    return {
        "scenario_stem": stem,
        "scenario_name": scen,
        "category": cat,
        "role_notes": notes,
        "map_file1": map1,
        "uses_nuuksio_map": uses_nuuksio,
        "movement_model": mm,
        "group1_movement": g1_mm,
        "n_host_groups": n_groups,
        "n_hosts": hosts,
        "transmit_range_m": rng,
        "uses_ranger_patrol": uses_patrol,
        "route_file": route,
    }


def write_md(rows: list[dict]) -> None:
    path = REPORTS / "NuuksioSparseTrails_rural_scenario_classification.md"
    realistic = [r for r in rows if r["category"] == "rural_realistic"]
    controls = [r for r in rows if r["category"] == "rural_extreme_control"]
    lines = [
        "# NuuksioSparseTrails — rural scenario classification",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"- Base scenarios: {len(rows)}",
        f"- `rural_realistic`: {len(realistic)}",
        f"- `rural_extreme_control`: {len(controls)}",
        "",
        "## Methodological note",
        "",
        "All R1–R12 scenarios use `NuuksioSparseTrails` as the map. "
        "Low delivery and encounter rates are **expected** for this family; "
        "extreme-control scenarios (R6–R7, R9–R12) stress range, buffer, or speed.",
        "",
        "## Realistic scenarios",
        "",
        "| ID | Movement | Patrol route | Notes |",
        "|----|----------|--------------|-------|",
    ]
    for r in realistic:
        patrol = "yes" if r["uses_ranger_patrol"] else "no"
        lines.append(
            f"| {r['scenario_stem']} | {r['movement_model']} | {patrol} | {r['role_notes']} |"
        )
    lines.extend(
        [
            "",
            "## Parametric controls",
            "",
            "| ID | Lever | Notes |",
            "|----|-------|-------|",
        ]
    )
    for r in controls:
        lines.append(f"| {r['scenario_stem']} | range/buffer/speed | {r['role_notes']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()

    rows: list[dict] = []
    for sp in sorted(BASE_RURAL.glob("R*.settings")):
        rows.append(classify_base(sp))

    MAP_DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    out_csv = MAP_DATA / "NuuksioSparseTrails_rural_scenario_classification.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    write_md(rows)
    print(f"Wrote {out_csv} ({len(rows)} scenarios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
