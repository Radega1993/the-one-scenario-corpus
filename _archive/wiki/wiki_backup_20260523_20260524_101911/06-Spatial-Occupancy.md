# Spatial occupancy

**Status:** needs validation | **Updated:** 2026-05-20 11:41 UTC

## Purpose

Grid-based mobility coverage methodology.

## Content

**Reports:** `SpatialOccupancyReport` + `NodePositionReport` (see [spatial_occupancy_report.md](../analysis/reports/spatial_occupancy_report.md))

**Metrics** (`spatial_occupancy_metrics.csv`):
- `final_coverage_pct` — fraction of grid cells visited
- `time_to_50/80/90pct` — time to reach coverage milestones
- `coverage_accessible_ratio` — visited cells on road bbox vs full world

## Interpretation

| Observation | Meaning |
|-------------|---------|
| Low world coverage (~8–10%) on WDM | Nodes use **roads**, not full rectangle world |
| High accessible ratio | Visited area is on streets, not empty space |
| Low coverage ≠ low connectivity | Mobility can be active but world grid is oversized |

**Coverage partial:** ~99/720 scenarios have spatial CSVs — expand after full sim batch.

## Recommended actions

| Pattern | Action |
|---------|--------|
| MAP_UNDERUSED + Helsinki | Crop `MovementModel.worldSize` |
| Low coverage + RWP huge world | Reduce world or increase range |


## Internal links

[07-Simulation-Time-and-Warmup](07-Simulation-Time-and-Warmup), [map_realism_review.md](../analysis/reports/map_realism_review.md)

## Open questions

Full 720 spatial reports?

## Paper usage

Methods — spatial representativeness; Discussion.
