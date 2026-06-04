#!/usr/bin/env python3
"""Remove  rows from analysis CSVs and rebuild benchmark_definition."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import DATA_DIR, DEFAULT_MANIFEST_V1, COMBINED_MANIFEST_CSV, REPO_ROOT  # noqa: E402

STRESS_FAMILY = "07_"
STRESS_NAME_RE = re.compile(r"^T\d+_")

def _is_stress_row(row: dict, id_col: str = "scenario_name") -> bool:
    name = row.get(id_col) or row.get("scenario") or row.get("Scenario.name") or ""
    fam = row.get("family", "")
    if fam == STRESS_FAMILY:
        return True
    return bool(STRESS_NAME_RE.match(str(name)))

def _filter_csv(path: Path, id_col: str | None = None) -> int:
    if not path.is_file():
        return 0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return 0
        fields = list(reader.fieldnames)
        id_key = id_col
        if id_key is None:
            for c in ("scenario_name", "scenario", "Scenario.name"):
                if c in fields:
                    id_key = c
                    break
        rows = [r for r in reader if not _is_stress_row(r, id_key or "scenario_name")]
    removed = 0
    with path.open(newline="", encoding="utf-8") as f:
        removed = sum(1 for _ in csv.DictReader(f)) - len(rows)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return removed

def purge_benchmark_definition() -> int:
    path = DATA_DIR / "benchmark_definition.csv"
    if not path.is_file():
        return 0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = [c for c in reader.fieldnames or [] if c != "included_in_stress"]
        rows = []
        for row in reader:
            if _is_stress_row(row):
                continue
            row.pop("included_in_stress", None)
            if row.get("benchmark_group") == "stress_control":
                row["benchmark_group"] = "environmental"
            rows.append(row)
    before = sum(1 for _ in open(path, encoding="utf-8")) - 1
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return before - len(rows)

def main() -> int:
    import shutil

    n_bench = purge_benchmark_definition()
    print(f"benchmark_definition.csv: removed {n_bench} stress rows")

    if DEFAULT_MANIFEST_V1.is_file():
        COMBINED_MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DEFAULT_MANIFEST_V1, COMBINED_MANIFEST_CSV)
        print(f"copied manifest -> {COMBINED_MANIFEST_CSV.relative_to(REPO_ROOT)}")

    csv_globs = list(DATA_DIR.glob("*.csv"))
    total = 0
    for p in sorted(csv_globs):
        if p.name == "benchmark_definition.csv":
            continue
        n = _filter_csv(p)
        if n:
            print(f"  {p.name}: removed {n}")
            total += n
    print(f"Total rows removed from data/*.csv: {total + n_bench}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())