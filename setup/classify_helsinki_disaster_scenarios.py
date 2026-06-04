#!/usr/bin/env python3
"""Classify 05_disaster base scenarios for HelsinkiDisrupted."""

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
BASE_DISASTER = SCENARIOS_DIR / "base_scenarios" / "05_disaster"

CLASSIFICATION: dict[str, tuple[str, str]] = {
    "D1_ShelterHotspots_Clusters": (
        "disaster_realistic",
        "Shelter hotspots via ClusterMovement groups",
    ),
    "D2_PartitionedCity_MuleBridge": (
        "disaster_bridge_or_mule",
        "Two partitions + SPMM mule bridge (no B_mule_route in settings)",
    ),
    "D3_Aftershock_ErraticMobility": (
        "disaster_realistic",
        "Erratic SPMM after aftershock",
    ),
    "D4_MedicalTriage_TwoClasses": (
        "disaster_realistic",
        "Medical vs civilian groups; short TTL for med class",
    ),
    "D5_UAVMule_FastRoute_HelsinkiDisrupted": (
        "disaster_bridge_or_mule",
        "UAV on A_emergency_route; civilians SPMM on streets",
    ),
    "D6_ShortTtlCritical_5to10min": (
        "disaster_critical_ttl",
        "msgTtl 7 min; endTime 14400 — critical comms window",
    ),
    "D7_HighLoad_TrafficStorm": (
        "disaster_stress_control",
        "70 hosts, 16M buffer — load/congestion stress",
    ),
    "D8_InfrastructureReturns_BackboneLinks": (
        "disaster_realistic",
        "Infrastructure return via clusters (no route WKT in settings)",
    ),
    "D9_Critical_1minTTL": (
        "disaster_critical_ttl",
        "msgTtl 1 min — extreme critical control",
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
    route = kv.get("Group2.routeFile", kv.get("Group1.routeFile", kv.get("Group.routeFile", "")))
    n_groups = kv.get("Scenario.nrofHostGroups", "1")
    ttl = kv.get("Group.msgTtl", kv.get("Group1.msgTtl", ""))
    end_time = kv.get("Scenario.endTime", "")

    cat, notes = CLASSIFICATION.get(stem, ("needs_review", "unclassified"))
    uses_emergency = "A_emergency_route" in route
    uses_mule = "B_mule_route" in route
    uses_roads_as_route = "roads.wkt" in route and "MapRoute" in g1_mm

    return {
        "scenario_stem": stem,
        "scenario_name": scen,
        "category": cat,
        "role_notes": notes,
        "map_file1": map1,
        "uses_helsinki_disrupted": "HelsinkiDisrupted" in map1,
        "movement_model": mm,
        "group1_movement": g1_mm,
        "n_host_groups": n_groups,
        "msg_ttl_min": ttl,
        "end_time_s": end_time,
        "uses_emergency_route": uses_emergency,
        "uses_mule_route": uses_mule,
        "group1_roads_as_route": uses_roads_as_route,
    }

def write_md(rows: list[dict]) -> None:
    path = REPORTS / "HelsinkiDisrupted_disaster_scenario_classification.md"
    realistic = [r for r in rows if r["category"] == "disaster_realistic"]
    bridge = [r for r in rows if r["category"] == "disaster_bridge_or_mule"]
    ttl_ctrl = [r for r in rows if r["category"] == "disaster_critical_ttl"]
    stress = [r for r in rows if r["category"] == "disaster_stress_control"]
    lines = [
        "# HelsinkiDisrupted — disaster scenario classification",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"- Base scenarios: {len(rows)}",
        f"- `disaster_realistic`: {len(realistic)}",
        f"- `disaster_bridge_or_mule`: {len(bridge)}",
        f"- `disaster_critical_ttl`: {len(ttl_ctrl)}",
        f"- `disaster_stress_control`: {len(stress)}",
        "",
        "## Methodological note",
        "",
        "HelsinkiDisrupted is used as a degraded urban disaster map. Low delivery, high latency, "
        "and structural partitioning can be expected outcomes in specific scenarios and should not "
        "be interpreted as configuration errors by default.",
        "",
        "## Narrative scenarios",
        "",
        "| ID | Movement | Routes | Notes |",
        "|----|----------|--------|-------|",
    ]
    for r in realistic + bridge:
        routes = []
        if r["uses_emergency_route"]:
            routes.append("A_emergency")
        if r["uses_mule_route"]:
            routes.append("B_mule")
        lines.append(
            f"| {r['scenario_stem']} | {r['group1_movement']} | {', '.join(routes) or '—'} | {r['role_notes']} |"
        )
    lines.extend(
        [
            "",
            "## TTL / stress controls",
            "",
            "| ID | Category | Lever |",
            "|----|----------|-------|",
        ]
    )
    for r in ttl_ctrl + stress:
        lines.append(f"| {r['scenario_stem']} | {r['category']} | TTL/load — {r['role_notes']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()

    rows = [classify_base(sp) for sp in sorted(BASE_DISASTER.glob("D*.settings"))]
    MAP_DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    out_csv = MAP_DATA / "HelsinkiDisrupted_disaster_scenario_classification.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    write_md(rows)
    print(f"Wrote {out_csv} ({len(rows)} scenarios)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())