#!/usr/bin/env python3
"""
Apply family map policy to base_scenarios/ (structural scenarios without Traffic Profiles).

Reuses migration logic from migrate_corpus_maps.py on scenarios/base_scenarios/.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASE_DIR = REPO_ROOT / "scenarios" / "base_scenarios"
BACKUP_DIR = BASE_DIR / "_backup_pre_migration"
ANALYSIS_DATA = REPO_ROOT / "scenarios" / "analysis" / "data"

# Import migration helpers from sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from migrate_corpus_maps import (  # noqa: E402
    FAMILY_MAP,
    migrate_file,
    post_validate,
    rename_file,
)

BASE_FAMILIES = (
    "01_urban",
    "02_campus",
    "03_vehicles",
    "04_rural",
    "05_disaster",
    "06_social",
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Migrate base_scenarios maps.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Populate base_scenarios from this directory first (e.g. legacy corpus)",
    )
    args = ap.parse_args()

    if args.source:
        src = args.source if args.source.is_absolute() else REPO_ROOT / args.source
        if not src.is_dir():
            print(f"ERROR: source not found: {src}")
            return 1
        if BASE_DIR.exists():
            shutil.rmtree(BASE_DIR)
        BASE_DIR.mkdir(parents=True)
        for fam in BASE_FAMILIES:
            sdir = src / fam
            if not sdir.is_dir():
                print(f"WARNING: missing family {fam} in {src}")
                continue
            ddir = BASE_DIR / fam
            ddir.mkdir(parents=True)
            for sf in sorted(sdir.glob("*.settings")):
                shutil.copy2(sf, ddir / sf.name)
        print(f"Copied base families from {src} -> {BASE_DIR}")

    if not BASE_DIR.is_dir():
        print(f"ERROR: {BASE_DIR} not found")
        return 1

    for fam, pol in FAMILY_MAP.items():
        if fam not in BASE_FAMILIES:
            continue
        roads = REPO_ROOT / pol["data_dir"] / "roads.wkt"
        if not roads.exists():
            print(f"ERROR: Map not installed: {roads}")
            return 1

    if not BACKUP_DIR.exists() and not args.dry_run:
        BACKUP_DIR.mkdir(parents=True)
        for fam in BASE_FAMILIES:
            sdir = BASE_DIR / fam
            if not sdir.is_dir():
                continue
            dst = BACKUP_DIR / fam
            dst.mkdir(exist_ok=True)
            for sf in sdir.glob("*.settings"):
                shutil.copy2(sf, dst / sf.name)
        n = sum(1 for _ in BACKUP_DIR.rglob("*.settings"))
        print(f"Backup: {n} files -> {BACKUP_DIR}")

    records: list[dict] = []
    renamed = 0
    for fam_name in BASE_FAMILIES:
        policy = FAMILY_MAP[fam_name]
        fam_dir = BASE_DIR / fam_name
        if not fam_dir.is_dir():
            continue
        for sf in sorted(fam_dir.glob("*.settings")):
            rec = migrate_file(sf, fam_name, policy, args.dry_run)
            records.append(rec)
            if not args.dry_run:
                new_path = rename_file(sf, policy)
                if new_path:
                    rec["scenario_name"] = new_path.stem
                    renamed += 1

    csv_path = ANALYSIS_DATA / "base_scenarios_map_migration.csv"
    ANALYSIS_DATA.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys()) if records else []
    if fieldnames:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(records)
        print(f"Wrote {csv_path}")

    fail = 0
    for fam_name in BASE_FAMILIES:
        policy = FAMILY_MAP[fam_name]
        fam_dir = BASE_DIR / fam_name
        if not fam_dir.is_dir():
            continue
        for sf in sorted(fam_dir.glob("*.settings")):
            issues = post_validate(sf, policy)
            if issues:
                fail += 1
                print(f"  [FAIL] {sf.name}: {issues}")

    print(f"Migrated {len(records)} base scenarios, {renamed} renamed")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
