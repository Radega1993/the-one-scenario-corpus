# NuuksioSparseTrails — rural scenario classification

Generated: 2026-05-28T18:15:32

- Base scenarios: 12
- `rural_realistic`: 6
- `rural_extreme_control`: 6

## Methodological note

All R1–R12 scenarios use `NuuksioSparseTrails` as the map. Low delivery and encounter rates are **expected** for this family; extreme-control scenarios (R6–R7, R9–R12) stress range, buffer, or speed.

## Realistic scenarios

| ID | Movement | Patrol route | Notes |
|----|----------|--------------|-------|
| R1_Rural_SparseSPMM | ShortestPathMapBasedMovement | no | Sparse SPMM on trails; few hosts; renamed from RandomWaypoint misnomer |
| R2_VillagesTrails_ThreeClusters | ClusterMovement | no | Three ClusterMovement villages on trail graph |
| R3_WildlifeTracking | ShortestPathMapBasedMovement | no | Dispersed wildlife/sensor nodes; SPMM |
| R4_ParkRangers_NuuksioSparseTrails | MapRouteMovement | yes | Anchor scenario: MapRouteMovement on A_ranger_patrol.wkt |
| R5_MountainRescue | ShortestPathMapBasedMovement | no | Mountain rescue proxy; SPMM on sparse trails |
| R8_IntermittentPower | ShortestPathMapBasedMovement | no | Rural technology: intermittent connectivity/power |

## Parametric controls

| ID | Lever | Notes |
|----|-------|-------|
| R10_TinyRange_5m | range/buffer/speed | Sensitivity: 5 m range; low delivery expected by design |
| R11_SpeedExtremeLow | range/buffer/speed | Sensitivity: very low movement speed |
| R12_SpeedExtremeHigh | range/buffer/speed | Sensitivity: very high movement speed on trails |
| R6_SparseLongRange | range/buffer/speed | Sensitivity: elevated transmitRange in sparse environment |
| R7_SparseTinyBuffer | range/buffer/speed | Sensitivity: minimal buffer in sparse environment |
| R9_ExtremeRange_200m | range/buffer/speed | Sensitivity: 200 m range (extreme for rural radio) |