# Before / after — mobility repair (S1, S6, D1, R2)

| Field | S1 | S6 | D1 | R2 |
|-------|----|----|----|-----|
| **Old name** | StrongCommunities_SeparateClusters | FamilyGroups_SmallPersistent | ShelterHotspots_Clusters | VillagesTrails_ThreeClusters |
| **New name** | StrongCommunities_LimitedMixing | FamilyGroups_LocalRoutines | ShelterHotspots_EmergencyMobility | VillagesTrails_InterVillage |
| **Old movement** | 4× ClusterMovement | 12× ClusterMovement | 3× Cluster + 5× SPMM | 3× ClusterMovement |
| **New movement** | 4× MapRoute + bridge MapRoute | 12× MapRoute + civic MapRoute | 3× SPMM + 2× MapRoute mule | 3× MapRoute village + inter-village MapRoute |

## Spatial metrics (legacy simulations, pre-repair)

From `data/problematic_scenarios_pre_repair_metrics.csv` (old scenario names, TP01 exemplar where available):

| scenario (legacy) | coverage_world_pct | coverage_map_bbox_pct | coverage_road_cells_pct |
|-------------------|-------------------:|----------------------:|------------------------:|
| S1 … TP01 | ~40 | ~68 | ~94 |
| S6 … TP01 | low world % | higher bbox | road-aligned after repair (re-sim pending) |
| D1 … TP01 | disaster-scale | — | — |
| R2 … TP01 | low rural world % | — | — |

**Post-repair:** re-run simulations per [`problematic_scenarios_resim_commands.md`](problematic_scenarios_resim_commands.md), then refresh `spatial_occupancy_metrics.csv` and compare `coverage_road_cells_pct` (primary paper metric).

## Protocol metrics (legacy)

Delivery and contact counts in `output_metrics.csv` under **old** scenario names remain valid for historical comparison until the 48 runs are re-simulated.

## Interpretation

- **Before:** occupancy heatmaps showed circular blobs decoupled from `roads.wkt`; world % was misleadingly low on large `worldSize` panels.
- **After (design):** nodes follow WKT routes or shortest-path on the road graph; communities/villages/shelters remain narratively distinct with limited cross-group mixing via bridge/mule/civic routes.
- **Pending:** full before/after numeric table after batch re-simulation.