"""
Helpers to locate spatial occupancy CSVs produced by The ONE (SpatialOccupancyReport)
and optional NodePositionReport outputs under reports/.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict


class SpatialOccupancyPaths(TypedDict):
    grid: Path | None
    coverage_timeseries: Path | None
    summary: Path | None
    node_positions: Path | None


def default_paths_for_scenario(reports_dir: Path, scenario_name: str) -> SpatialOccupancyPaths:
    """Expected filenames: ``{scenario}_spatial_occupancy_grid.csv``, etc."""
    d = Path(reports_dir)
    return {
        "grid": d / f"{scenario_name}_spatial_occupancy_grid.csv",
        "coverage_timeseries": d / f"{scenario_name}_spatial_coverage_timeseries.csv",
        "summary": d / f"{scenario_name}_spatial_occupancy_summary.csv",
        "node_positions": d / f"{scenario_name}_NodePositionReport.csv",
    }


def resolve_existing(paths: SpatialOccupancyPaths) -> SpatialOccupancyPaths:
    """Return the same dict with paths set to None where the file does not exist."""
    return {k: (p if p is not None and p.is_file() else None) for k, p in paths.items()}  # type: ignore[misc]


def find_spatial_artifacts(reports_dir: Path, scenario_name: str) -> SpatialOccupancyPaths:
    """
    Resolve default paths; if the grid file is missing, try a loose glob
    ``*{scenario}*spatial_occupancy_grid.csv`` under reports_dir.
    """
    d = Path(reports_dir)
    p = default_paths_for_scenario(d, scenario_name)
    if p["grid"] is not None and p["grid"].is_file():
        return resolve_existing(p)
    matches = sorted(d.glob(f"*{scenario_name}*spatial_occupancy_grid.csv"))
    if not matches:
        return resolve_existing(p)
    fn = matches[0].stem
    suffix = "_spatial_occupancy_grid"
    if fn.endswith(suffix):
        stem = fn[: -len(suffix)]
    else:
        stem = scenario_name
    return resolve_existing(default_paths_for_scenario(d, stem))
