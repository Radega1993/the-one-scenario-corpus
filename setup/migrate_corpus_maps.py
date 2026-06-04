#!/usr/bin/env python3
"""
migrate_corpus_maps.py — Migrate corpus_v1 .settings to use one fixed map per family.

Performs:
  0. Backup all .settings to _backup_pre_migration/
  1. Update MovementModel.worldSize
  2. Add/update MapBasedMovement.nrofMapFiles + mapFile1
  3. Convert free-space models (RandomWaypoint, LinearMovement) to ShortestPathMapBasedMovement
  4. Replace data/HelsinkiMedium/ and data/Manhattan/ paths with family map paths
  5. Rescale ClusterMovement clusterCenter + clusterRange
  6. Update Scenario.name and rename files
  7. Generate map_policy_validation.csv
  8. Post-validation: check file references, bounds, clusterCenter

Usage:
  python3 scenarios/setup/migrate_corpus_maps.py [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CORPUS_DIR = REPO_ROOT / "scenarios" / "corpus_v1"
DATA_DIR = REPO_ROOT / "data"
ANALYSIS_DATA = REPO_ROOT / "scenarios" / "analysis" / "data"
BACKUP_DIR = CORPUS_DIR / "_backup_pre_migration"

# ── Family → map policy ────────────────────────────────────────────────────

FAMILY_MAP: dict[str, dict] = {
    "01_urban": {
        "map_name": "HelsinkiDowntown",
        "world_size": (2093, 1838),
        "data_dir": "data/HelsinkiDowntown",
    },
    "02_campus": {
        "map_name": "KumpulaCampus",
        "world_size": (1524, 1416),
        "data_dir": "data/KumpulaCampus",
    },
    "03_vehicles": {
        "map_name": "ManhattanMidtownGrid",
        "world_size": (2500, 2366),
        "data_dir": "data/ManhattanMidtownGrid",
    },
    "04_rural": {
        "map_name": "NuuksioSparseTrails",
        "world_size": (2848, 2945),
        "data_dir": "data/NuuksioSparseTrails",
    },
    "05_disaster": {
        "map_name": "HelsinkiDisrupted",
        "world_size": (2067, 2206),
        "data_dir": "data/HelsinkiDisrupted",
    },
    "06_social": {
        "map_name": "KallioCommunityCompact",
        "world_size": (1458, 1529),
        "data_dir": "data/KallioCommunityCompact",
    },
}

OLD_MAP_NAMES = {"HelsinkiMedium", "Manhattan"}

# Regex for single-pass replacement of old map names in text (longest first to
# avoid partial matches, e.g. "Manhattan" matching inside "ManhattanMidtownGrid").
_OLD_NAMES_RE = re.compile(
    "|".join(re.escape(n) for n in sorted(OLD_MAP_NAMES, key=len, reverse=True))
)

# Movement models that should become ShortestPathMapBasedMovement
FREE_SPACE_MODELS = {"RandomWaypoint", "LinearMovement"}

# ── Regex patterns ──────────────────────────────────────────────────────────

RE_WORLD_SIZE = re.compile(r"^(MovementModel\.worldSize\s*=\s*)(.+)$", re.MULTILINE)
RE_NROF_MAP = re.compile(r"^(MapBasedMovement\.nrofMapFiles\s*=\s*)(.+)$", re.MULTILINE)
RE_MAP_FILE = re.compile(r"^(MapBasedMovement\.mapFile\d+\s*=\s*)(.+)$", re.MULTILINE)
RE_SCENARIO_NAME = re.compile(r"^(Scenario\.name\s*=\s*)(.+)$", re.MULTILINE)
RE_MOVEMENT_MODEL = re.compile(
    r"^((?:Group\d*|Group)\.movementModel\s*=\s*)(\S+)\s*$", re.MULTILINE
)
RE_DATA_PATH = re.compile(r"data/(HelsinkiMedium|Manhattan)/(\S+)")
RE_CLUSTER_CENTER = re.compile(
    r"^(Group\d+\.clusterCenter\s*=\s*)(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*$",
    re.MULTILINE,
)
RE_CLUSTER_RANGE = re.compile(
    r"^(Group\d+\.clusterRange\s*=\s*)(\d+(?:\.\d+)?)\s*$", re.MULTILINE
)
RE_RNG_SEED_LINE = re.compile(r"^MovementModel\.rngSeed\s*=.*$", re.MULTILINE)

def _parse_world_size(text: str) -> tuple[int, int] | None:
    m = RE_WORLD_SIZE.search(text)
    if not m:
        return None
    parts = m.group(2).strip().split(",")
    return int(parts[0].strip()), int(parts[1].strip())

def _detect_old_map(text: str) -> str:
    if "data/Manhattan/" in text:
        return "Manhattan"
    if "data/HelsinkiMedium/" in text:
        return "HelsinkiMedium"
    return "none"

def _detect_movement_models(text: str) -> list[str]:
    return [m.group(2) for m in RE_MOVEMENT_MODEL.finditer(text)]

def _has_map_based(text: str) -> bool:
    return bool(RE_NROF_MAP.search(text))

def migrate_file(
    path: Path, family: str, policy: dict, dry_run: bool
) -> dict:
    """Migrate a single .settings file. Returns a validation record."""
    text = path.read_text()
    original = text
    notes: list[str] = []

    new_ws = policy["world_size"]
    new_data = policy["data_dir"]
    map_name = policy["map_name"]

    old_ws = _parse_world_size(text)
    old_map = _detect_old_map(text)
    old_models = _detect_movement_models(text)

    # A) worldSize
    text = RE_WORLD_SIZE.sub(
        rf"\g<1>{new_ws[0]}, {new_ws[1]}", text
    )

    # B) MapBasedMovement
    if _has_map_based(original):
        text = RE_NROF_MAP.sub(r"\g<1>1", text)
        text = RE_MAP_FILE.sub(rf"\g<1>{new_data}/roads.wkt", text)
        notes.append("updated existing MapBasedMovement")
    else:
        insert_block = (
            f"\nMapBasedMovement.nrofMapFiles = 1\n"
            f"MapBasedMovement.mapFile1 = {new_data}/roads.wkt\n"
        )
        m = RE_RNG_SEED_LINE.search(text)
        if m:
            text = text[: m.end()] + insert_block + text[m.end() :]
        else:
            m_ws = RE_WORLD_SIZE.search(text)
            if m_ws:
                text = text[: m_ws.end()] + insert_block + text[m_ws.end() :]
        notes.append("inserted MapBasedMovement block")

    # C) Movement model conversion
    new_models = []
    def _replace_model(m: re.Match) -> str:
        prefix = m.group(1)
        model = m.group(2)
        if model in FREE_SPACE_MODELS:
            new_models.append(("ShortestPathMapBasedMovement", model))
            return f"{prefix}ShortestPathMapBasedMovement"
        new_models.append((model, model))
        return m.group(0)

    text = RE_MOVEMENT_MODEL.sub(_replace_model, text)
    converted = [f"{old}->{new}" for new, old in new_models if new != old]
    if converted:
        notes.append(f"converted models: {', '.join(converted)}")

    # D) Data path replacement
    def _replace_path(m: re.Match) -> str:
        old_dataset = m.group(1)
        filename = m.group(2)
        if filename == "bus.wkt":
            filename = "A_bus.wkt"
        return f"{new_data}/{filename}"

    text = RE_DATA_PATH.sub(_replace_path, text)

    # E) Rescale clusterCenter + clusterRange
    if old_ws and old_ws != new_ws:
        scale_x = new_ws[0] / old_ws[0]
        scale_y = new_ws[1] / old_ws[1]
        scale_avg = (scale_x + scale_y) / 2

        def _rescale_center(m: re.Match) -> str:
            prefix = m.group(1)
            cx = float(m.group(2)) * scale_x
            cy = float(m.group(3)) * scale_y
            return f"{prefix}{int(round(cx))}, {int(round(cy))}"

        def _rescale_range(m: re.Match) -> str:
            prefix = m.group(1)
            r = float(m.group(2)) * scale_avg
            return f"{prefix}{int(round(r))}"

        centers_before = RE_CLUSTER_CENTER.findall(text)
        text = RE_CLUSTER_CENTER.sub(_rescale_center, text)
        text = RE_CLUSTER_RANGE.sub(_rescale_range, text)
        if centers_before:
            notes.append(f"rescaled {len(centers_before)} clusterCenter(s), scale=({scale_x:.3f},{scale_y:.3f})")

    # F) Scenario.name: replace old map name with new
    def _update_scenario_name(m: re.Match) -> str:
        prefix = m.group(1)
        name = m.group(2).strip()
        name = _OLD_NAMES_RE.sub(map_name, name)
        return f"{prefix}{name}"

    text = RE_SCENARIO_NAME.sub(_update_scenario_name, text)

    if not dry_run and text != original:
        path.write_text(text)

    # Build validation record
    new_models_list = _detect_movement_models(text)
    record = {
        "family": family,
        "scenario_name": path.stem,
        "old_map": old_map,
        "new_map": map_name,
        "old_worldSize": f"{old_ws[0]},{old_ws[1]}" if old_ws else "?",
        "new_worldSize": f"{new_ws[0]},{new_ws[1]}",
        "old_movementModel": ";".join(old_models),
        "new_movementModel": ";".join(new_models_list),
        "validation_status": "OK",
        "notes": "; ".join(notes) if notes else "",
    }
    return record

def rename_file(path: Path, policy: dict) -> Path | None:
    """Rename .settings file if it contains old map names. Returns new path or None."""
    name = path.name
    new_name = _OLD_NAMES_RE.sub(policy["map_name"], name)
    if new_name != name:
        new_path = path.parent / new_name
        path.rename(new_path)
        return new_path
    return None

def post_validate(path: Path, policy: dict) -> list[str]:
    """Validate a migrated .settings file. Returns list of issues."""
    issues = []
    text = path.read_text()
    new_ws = policy["world_size"]

    # Check all referenced files exist
    for m in re.finditer(r"(data/\S+\.wkt)", text):
        ref = REPO_ROOT / m.group(1)
        if not ref.exists():
            issues.append(f"BROKEN_REF: {m.group(1)}")

    # Check clusterCenter within bounds
    for m in RE_CLUSTER_CENTER.finditer(text):
        cx, cy = float(m.group(2)), float(m.group(3))
        if cx < 0 or cx > new_ws[0] or cy < 0 or cy > new_ws[1]:
            issues.append(f"CLUSTER_OOB: ({cx},{cy}) vs worldSize ({new_ws[0]},{new_ws[1]})")

    # Check no old map references remain
    for old in OLD_MAP_NAMES:
        if f"data/{old}/" in text:
            issues.append(f"STALE_REF: data/{old}/ still in file")

    return issues

def main() -> int:
    ap = argparse.ArgumentParser(description="Migrate corpus_v1 maps.")
    ap.add_argument("--dry-run", action="store_true", help="Don't write files")
    args = ap.parse_args()

    if not CORPUS_DIR.exists():
        print(f"ERROR: {CORPUS_DIR} not found")
        return 1

    # Verify maps installed
    for fam, pol in FAMILY_MAP.items():
        roads = REPO_ROOT / pol["data_dir"] / "roads.wkt"
        if not roads.exists():
            print(f"ERROR: Map not installed: {roads}")
            return 1

    # Step 0: Backup
    if not BACKUP_DIR.exists():
        print(f"Creating backup at {BACKUP_DIR}...")
        BACKUP_DIR.mkdir(parents=True)
        for fam_dir in sorted(CORPUS_DIR.iterdir()):
            if not fam_dir.is_dir() or fam_dir.name.startswith("_"):
                continue
            dst = BACKUP_DIR / fam_dir.name
            dst.mkdir(exist_ok=True)
            for sf in fam_dir.glob("*.settings"):
                shutil.copy2(sf, dst / sf.name)
        count = sum(1 for _ in BACKUP_DIR.rglob("*.settings"))
        print(f"  Backed up {count} files")
    else:
        print(f"Backup already exists at {BACKUP_DIR}, skipping")

    # Step 1: Migrate
    records: list[dict] = []
    total = 0
    renamed = 0

    for fam_name, policy in FAMILY_MAP.items():
        fam_dir = CORPUS_DIR / fam_name
        if not fam_dir.exists():
            print(f"  [SKIP] {fam_name}: directory not found")
            continue

        settings_files = sorted(fam_dir.glob("*.settings"))
        print(f"\n{'='*60}")
        print(f"  {fam_name}: {len(settings_files)} files -> {policy['map_name']}")
        print(f"  worldSize: {policy['world_size']}")
        print(f"{'='*60}")

        for sf in settings_files:
            rec = migrate_file(sf, fam_name, policy, args.dry_run)
            records.append(rec)
            total += 1

            if not args.dry_run:
                new_path = rename_file(sf, policy)
                if new_path:
                    rec["scenario_name"] = new_path.stem
                    rec["notes"] += f"; renamed to {new_path.name}"
                    renamed += 1

        print(f"  Processed {len(settings_files)} files")

    print(f"\nTotal: {total} files migrated, {renamed} renamed")

    # Step 2: Write CSV
    ANALYSIS_DATA.mkdir(parents=True, exist_ok=True)
    csv_path = ANALYSIS_DATA / "map_policy_validation.csv"
    fieldnames = [
        "family", "scenario_name", "old_map", "new_map",
        "old_worldSize", "new_worldSize",
        "old_movementModel", "new_movementModel",
        "validation_status", "notes",
    ]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(records)
    print(f"\nWrote {csv_path} ({len(records)} rows)")

    # Step 3: Post-validation
    print("\n--- Post-validation ---")
    fail_count = 0
    for fam_name, policy in FAMILY_MAP.items():
        fam_dir = CORPUS_DIR / fam_name
        if not fam_dir.exists():
            continue
        for sf in sorted(fam_dir.glob("*.settings")):
            issues = post_validate(sf, policy)
            if issues:
                fail_count += 1
                print(f"  [FAIL] {sf.name}")
                for iss in issues:
                    print(f"    - {iss}")
                for rec in records:
                    if rec["scenario_name"] == sf.stem:
                        rec["validation_status"] = "FAIL"
                        rec["notes"] += "; " + "; ".join(issues)

    if fail_count:
        print(f"\n*** {fail_count} file(s) failed post-validation ***")
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(records)
        print(f"Updated {csv_path}")
    else:
        print("  All files PASS post-validation.")

    if args.dry_run:
        print("\n(dry-run: no files were modified)")

    return 1 if fail_count else 0

if __name__ == "__main__":
    raise SystemExit(main())