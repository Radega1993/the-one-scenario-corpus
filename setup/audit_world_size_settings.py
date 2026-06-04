#!/usr/bin/env python3
"""Verify active .settings worldSize matches world_size_calibration.csv."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CAL_CSV = REPO / "scenarios" / "analysis" / "data" / "world_size_calibration.csv"
RE_WORLD = re.compile(r"^MovementModel\.worldSize\s*=\s*(\d+)\s*,\s*(\d+)", re.MULTILINE)

LEGACY = {
    (2093, 1838),
    (1793, 1539),
    (1793, 1538),
    (1228, 1116),
    (1227, 1116),
    (2200, 2066),
    (2199, 2066),
    (2550, 2645),
    (2550, 2644),
    (1791, 1954),
    (1790, 1953),
    (1204, 1229),
    (1203, 1228),
    (2500, 2366),
    (2848, 2945),
    (2067, 2206),
    (1458, 1529),
}


def expected_by_family() -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    with CAL_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["family"]] = (int(row["world_size_x"]), int(row["world_size_y"]))
    return out


def main() -> int:
    if not CAL_CSV.is_file():
        print(f"Missing {CAL_CSV}")
        return 1
    expected = expected_by_family()
    fam_map = {
        "01_urban": expected["01_urban"],
        "02_campus": expected["02_campus"],
        "03_vehicles": expected["03_vehicles"],
        "04_rural": expected["04_rural"],
        "05_disaster": expected["05_disaster"],
        "06_social": expected["06_social"],
    }
    errors: list[str] = []
    legacy_hits: list[str] = []
    ok = 0
    roots = [
        REPO / "scenarios" / "corpus_v1",
        REPO / "scenarios" / "base_scenarios",
    ]
    for root in roots:
        for sf in sorted(root.rglob("*.settings")):
            if any(p.startswith("_backup") for p in sf.parts):
                continue
            fam = sf.parent.name
            if fam not in fam_map:
                continue
            text = sf.read_text(encoding="utf-8", errors="replace")
            m = RE_WORLD.search(text)
            if not m:
                errors.append(f"{sf}: no worldSize")
                continue
            ws = (int(m.group(1)), int(m.group(2)))
            if ws in LEGACY:
                legacy_hits.append(f"{sf}: legacy {ws}")
            if ws != fam_map[fam]:
                errors.append(f"{sf}: {ws} != expected {fam_map[fam]}")
            else:
                ok += 1
    print(f"OK: {ok} settings files")
    if legacy_hits:
        print(f"LEGACY worldSize ({len(legacy_hits)}):")
        for line in legacy_hits[:10]:
            print(f"  {line}")
        if len(legacy_hits) > 10:
            print(f"  ... +{len(legacy_hits) - 10} more")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for line in errors[:20]:
            print(f"  {line}")
        return 1
    if legacy_hits:
        return 1
    print("All active settings match calibration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
