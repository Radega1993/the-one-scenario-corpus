#!/usr/bin/env python3
"""Build base_scenarios/manifest.csv from structural .settings files."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASE_DIR = REPO_ROOT / "scenarios" / "base_scenarios"
OUT = BASE_DIR / "manifest.csv"

sys.path.insert(0, str(REPO_ROOT / "scenarios" / "setup"))
from regenerate_manifests import infer_hosts, parse_settings  # noqa: E402

from migrate_corpus_maps import FAMILY_MAP  # noqa: E402

def movement_models(kv: dict[str, str]) -> str:
    models: list[str] = []
    for key, val in kv.items():
        if key.endswith(".movementModel") or key == "Group.movementModel":
            models.append(val)
    return "|".join(sorted(set(models)))

def map_profile(kv: dict[str, str], family: str) -> str:
    mf = kv.get("MapBasedMovement.mapFile1", "")
    if mf:
        return Path(mf).parts[1] if mf.startswith("data/") else mf
    return FAMILY_MAP.get(family, {}).get("map_name", "")

def main() -> int:
    rows: list[dict] = []
    for fam_dir in sorted(BASE_DIR.iterdir()):
        if not fam_dir.is_dir() or fam_dir.name.startswith("_"):
            continue
        for sf in sorted(fam_dir.glob("*.settings")):
            text = sf.read_text(encoding="utf-8", errors="replace")
            kv = parse_settings(text)
            base = kv.get("Scenario.name", sf.stem)
            ws = kv.get("MovementModel.worldSize", "")
            rows.append(
                {
                    "family": fam_dir.name,
                    "scenario_base": base,
                    "settings_file": f"scenarios/base_scenarios/{fam_dir.name}/{sf.name}",
                    "source_tp_template": "TP01_Baseline",
                    "n_hosts": infer_hosts(kv),
                    "map_profile": map_profile(kv, fam_dir.name),
                    "movement_models": movement_models(kv),
                    "world_size": ws,
                    "Scenario.endTime": kv.get("Scenario.endTime", ""),
                    "notes": "structural base; traffic block is scenario-specific (not TP overlay)",
                }
            )
    cols = list(rows[0].keys()) if rows else []
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT} ({len(rows)} rows)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())