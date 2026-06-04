#!/usr/bin/env python3
"""Classify 06_social base scenarios for KallioCommunityCompact."""

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
BASE_SOCIAL = SCENARIOS_DIR / "base_scenarios" / "06_social"

CLASSIFICATION: dict[str, tuple[str, str, str]] = {
    "S1_StrongCommunities_SeparateClusters": (
        "social_strong_communities",
        "ClusterMovement",
        "4 separated clusters; no bridge; low inter-community delivery expected (TP12)",
    ),
    "S2_WeakCommunities_HighMixing": (
        "social_weak_communities",
        "ShortestPathMapBasedMovement",
        "80 hosts SPMM; high mixing on compact map",
    ),
    "S3_PeriodicMeetings_RegularRhythm": (
        "social_periodic_meetings",
        "ShortestPathMapBasedMovement",
        "Long waitTime; regular rhythm by mobility params, not scheduled events",
    ),
    "S4_RandomMixing_NoHotspots": (
        "social_random_mixing_control",
        "ShortestPathMapBasedMovement",
        "No cluster/POI attractors; map paths only",
    ),
    "S5_TwoLayer_StudentsStaff": (
        "social_two_layer_population",
        "ShortestPathMapBasedMovement",
        "Students vs staff speed/wait; heterogeneous social layers",
    ),
    "S6_FamilyGroups_SmallPersistent": (
        "social_persistent_family_groups",
        "ClusterMovement",
        "12 microclusters; persistent family-scale communities",
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
    cat, mm, notes = CLASSIFICATION.get(stem, ("needs_review", "", "unclassified"))
    n_groups = int(kv.get("Scenario.nrofHostGroups", "1") or "1")
    cluster_groups = sum(
        1 for k, v in kv.items() if k.endswith(".movementModel") and v == "ClusterMovement"
    )
    spmm_groups = sum(
        1 for k, v in kv.items() if k.endswith(".movementModel") and v == "ShortestPathMapBasedMovement"
    )
    map_constrained = cluster_groups == 0
    hosts = sum(int(kv.get(f"Group{i}.nrofHosts", "0") or "0") for i in range(1, n_groups + 1))
    if hosts == 0:
        hosts = int(kv.get("Group.nrofHosts", "0") or "0")

    return {
        "scenario_stem": stem,
        "scenario_name": kv.get("Scenario.name", stem),
        "category": cat,
        "primary_movement": mm,
        "role_notes": notes,
        "map_file1": kv.get("MapBasedMovement.mapFile1", ""),
        "n_host_groups": n_groups,
        "n_cluster_groups": cluster_groups,
        "n_spmm_groups": spmm_groups,
        "map_constrained": map_constrained,
        "total_hosts": hosts,
        "uses_community_routes_in_settings": "no",
    }

def write_md(rows: list[dict]) -> None:
    path = REPORTS / "KallioCommunityCompact_social_scenario_classification.md"
    cluster = [r for r in rows if not r["map_constrained"]]
    mapbased = [r for r in rows if r["map_constrained"]]
    lines = [
        "# KallioCommunityCompact — social scenario classification",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## ClusterMovement note",
        "",
        "In scenarios based on ClusterMovement (S1, S6), community structure is explicitly "
        "imposed through cluster centers and ranges. The road network is **not** used as a "
        "path constraint; the compact urban map provides spatial context and a consistent "
        "coordinate system.",
        "",
        f"- Cluster-based (S1, S6): {len(cluster)}",
        f"- Map-based SPMM (S2–S5): {len(mapbased)}",
        "",
        "## Scenarios",
        "",
        "| ID | Category | Movement | Map-constrained | Hosts | Notes |",
        "|----|----------|----------|-----------------|-------|-------|",
    ]
    for r in rows:
        mc = "yes" if r["map_constrained"] else "no"
        lines.append(
            f"| {r['scenario_stem']} | {r['category']} | {r['primary_movement']} | {mc} | {r['total_hosts']} | {r['role_notes']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()

    rows = [classify_base(sp) for sp in sorted(BASE_SOCIAL.glob("S*.settings"))]
    MAP_DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    out_csv = MAP_DATA / "KallioCommunityCompact_social_scenario_classification.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    write_md(rows)
    print(f"Wrote {out_csv} ({len(rows)} scenarios)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())