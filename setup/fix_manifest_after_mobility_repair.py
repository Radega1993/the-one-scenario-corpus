#!/usr/bin/env python3
"""Rebuild corpus_v1/manifest.csv to 540 rows after mobility repair."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
_SCENARIOS = _SETUP.parent
_REPO = _SCENARIOS.parent
_ANALYSIS = _SCENARIOS / "analysis"
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import build_combined_manifest_csv  # noqa: E402
from lib.traffic_profile_generator import (  # noqa: E402
    PROFILE_ORDER,
    infer_total_hosts,
    parse_simple_settings,
    profile_ttl_minutes,
)

OLD_BASES = {
    "S1_StrongCommunities_SeparateClusters",
    "S6_FamilyGroups_SmallPersistent",
    "D1_ShelterHotspots_Clusters",
    "R2_VillagesTrails_ThreeClusters",
}
NEW_BASES = {
    "S1_StrongCommunities_LimitedMixing",
    "S6_FamilyGroups_LocalRoutines",
    "D1_ShelterHotspots_EmergencyMobility",
    "R2_VillagesTrails_InterVillage",
}

MANIFEST = _SCENARIOS / "corpus_v1" / "manifest.csv"
BENCH = _ANALYSIS / "data" / "benchmark_definition.csv"

def row_from_settings(path: Path, family: str, base: str, tp_id: str, tp_label: str) -> dict:
    kv = parse_simple_settings(path.read_text(encoding="utf-8"))
    return {
        "family": family,
        "scenario_base": base,
        "scenario_name": f"{base}__{tp_id}_{tp_label}",
        "traffic_profile_id": tp_id,
        "traffic_profile_name": tp_label,
        "settings_file": str(path.relative_to(_REPO)),
        "n_hosts": infer_total_hosts(kv) or "",
        "Scenario.endTime": kv.get("Scenario.endTime", ""),
        "Group.msgTtl_minutes": profile_ttl_minutes(tp_id, base),
        "Events.nrof": "",
        "Events1.interval": "",
        "Events1.size": "",
        "note": "",
    }

def main() -> int:
    archives = sorted((_SCENARIOS / "_archive").glob("settings_backup_*/manifests/manifest.csv"))
    if not archives:
        raise SystemExit("No backup manifest")
    with archives[-1].open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        old_rows = [r for r in reader if r.get("scenario_base") not in OLD_BASES]

    new_rows: list[dict] = []
    for base in sorted(NEW_BASES):
        fam = "06_social" if base.startswith("S") else "05_disaster" if base.startswith("D") else "04_rural"
        for tp_id, tp_label in PROFILE_ORDER:
            p = _SCENARIOS / "corpus_v1" / fam / f"{base}__{tp_id}_{tp_label}.settings"
            new_rows.append(row_from_settings(p, fam, base, tp_id, tp_label))

    merged = old_rows + new_rows
    if len(merged) != 540:
        print(f"Warning: merged count {len(merged)} != 540")
    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(merged)

  # benchmark_definition
    if BENCH.is_file():
        with BENCH.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            bfn = reader.fieldnames or []
            kept = [
                r
                for r in reader
                if r.get("scenario_base") not in OLD_BASES
                and not any(
                    str(r.get("scenario_name", "")).startswith(o) for o in OLD_BASES
                )
            ]
        for r in new_rows:
            kept.append(
                {
                    "scenario_name": r["scenario_name"],
                    "family": r["family"],
                    "benchmark_split": "environmental",
                    "traffic_profile_id": r["traffic_profile_id"],
                    "include": "TRUE",
                    "deprecated": "FALSE",
                    "stress_only": "FALSE",
                    "notes": "",
                }
            )
        with BENCH.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=bfn, extrasaction="ignore")
            w.writeheader()
            w.writerows(kept)

    build_combined_manifest_csv()
    print(f"manifest rows: {len(merged)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())