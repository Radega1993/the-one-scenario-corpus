# Spatial occupancy: denominator validation

This note validates the **multi-denominator coverage** metrics produced by `lib/spatial_coverage.py` and `analyze_spatial_occupancy.py`. It explains why a single `worldSize` percentage is insufficient for papers and how to read the new CSV columns.

## Why `worldSize` alone is misleading

`SpatialOccupancyReport` (Java) counts visited cells over a fixed grid covering the full rectangle `MovementModel.worldSize` (`gridSize²` cells). That denominator includes:

- white margins around the map panel;
- water or empty areas outside the road network;
- interior courtyards and building footprints that nodes never cross.

A **low `coverage_world_pct`** therefore often means “low fraction of the simulation rectangle,” not “nodes failed to use the map.”

## Denominator families

| Metric | Denominator | Interpretation |
|--------|-------------|----------------|
| `coverage_world_pct` | All `gridSize²` cells | Same as Java `final_coverage_pct`; transparency / legacy comparison |
| `coverage_map_bbox_pct` | Cells whose **centre** lies inside the OSM-aligned bbox of `roads.wkt` (+ margin) | Excludes outer margins; still includes non-road interior |
| **`coverage_road_cells_pct`** | Cells intersecting rasterized **road segments** | **Primary paper metric** — share of the drivable grid used |
| `coverage_road_buffer_{10,15,25}m_pct` | Road cells dilated by 10 / 15 / 25 m | Sensitivity: wider corridor around the network |

**Visited cell:** `visit_count > 0` in the final occupancy grid (same rule as the simulator summary).

## Primary metric for the paper

Use **`coverage_road_cells_pct`** as the main spatial exploration statistic. Report `coverage_world_pct` only for transparency (Java default). Buffer variants (10 / 15 / 25 m) belong in supplementary material when discussing grid resolution or corridor width.

**Note on buffer percentages:** buffer masks are supersets of `road_cell`, so the numerator (visited buffer cells) is at least the road-cell numerator, but the denominator is larger. Buffer **percentages can be lower than road-cell %** even when exploration is good — that is expected, not a bug.

## Limitations

- Cell visited ≠ contact opportunity ≠ message delivery.
- Fixed grid (default 50 m); coarser grids underestimate thin roads.
- Buffer radius chooses an arbitrary corridor width in cell units after dilation.
- Map bbox uses cell **centres**, not geometric intersection with polygons.
- Timeseries enrichment for non-world metrics requires `NodePositionReport` replay; without it, only `coverage_world_pct` is populated per bin.

## Acceptance scenario: C1 campus

Scenario: `C1_Campus_ClassChange__TP08_HubTarget`  
Map: `KumpulaCampus` · `grid_size=50` · `--zoom-mode roads`

Regenerated with:

```bash
venv/bin/python scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py \
  --reports-dir reports --corpus corpus_v1 \
  --name-regex 'C1_Campus_ClassChange__TP08_HubTarget' \
  --zoom-mode roads
```

| Metric | Value | Comment |
|--------|------:|---------|
| `coverage_world_pct` | 40.24 | Low — large `worldSize` margins |
| `coverage_map_bbox_pct` | 67.88 | Higher — excludes outer white band |
| **`coverage_road_cells_pct`** | **94.04** | **Primary** — most road cells visited |
| `coverage_road_buffer_10m_pct` | 76.44 | Lower % — wider denominator |
| `coverage_road_buffer_15m_pct` | 76.44 | Same mask at 50 m resolution (1 cell ≈ 50 m) |
| `coverage_road_buffer_25m_pct` | 76.44 | idem |

Cell counts (final grid): road total 1057, road visited ~994; buffer-10 total 1316.

Heatmap: `scenarios/analysis/figures/spatial_heatmaps/C1_Campus_ClassChange__TP08_HubTarget.png`  
Backup before refactor: `scenarios/analysis/_backup_before_spatial_coverage_refactor_20260529_153500/`

## Related docs

- Methodology: [spatial_occupancy_report.md](spatial_occupancy_report.md)
- Wiki: [13-Spatial-Occupancy](../../../.wiki-clone/13-Spatial-Occupancy.md)
- Implementation: `scenarios/analysis/lib/spatial_coverage.py`
