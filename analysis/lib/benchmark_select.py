"""Select scenarios by benchmark tier using benchmark_definition.csv.

Uses only stdlib csv (no pandas) to keep the runner lightweight.
"""

from __future__ import annotations

import csv
from pathlib import Path

_VALID_BENCHMARKS = ("core", "stress", "all")


def select_by_benchmark(
    csv_path: Path,
    benchmark: str,
    *,
    exclude_deprecated: bool = True,
) -> set[str]:
    """Return scenario_name values matching the requested benchmark tier.

    benchmark:
        "core"   -> included_in_core == TRUE
        "stress" -> included_in_stress == TRUE
        "all"    -> included_in_core == TRUE OR included_in_stress == TRUE
    """
    if benchmark not in _VALID_BENCHMARKS:
        raise ValueError(
            f"benchmark must be one of {_VALID_BENCHMARKS}, got {benchmark!r}"
        )
    names: set[str] = set()
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if exclude_deprecated and row.get("deprecated", "").strip().upper() == "TRUE":
                continue
            core = row.get("included_in_core", "").strip().upper() == "TRUE"
            stress = row.get("included_in_stress", "").strip().upper() == "TRUE"
            if benchmark == "core" and core:
                names.add(row["scenario_name"])
            elif benchmark == "stress" and stress:
                names.add(row["scenario_name"])
            elif benchmark == "all" and (core or stress):
                names.add(row["scenario_name"])
    return names


def load_endtimes(manifest_path: Path) -> dict[str, int]:
    """Return {scenario_name: endTime_seconds} from manifest.csv."""
    endtimes: dict[str, int] = {}
    with open(manifest_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row.get("scenario_name", "").strip()
            raw = row.get("Scenario.endTime", "").strip()
            if name and raw:
                try:
                    endtimes[name] = int(raw)
                except ValueError:
                    pass
    return endtimes
