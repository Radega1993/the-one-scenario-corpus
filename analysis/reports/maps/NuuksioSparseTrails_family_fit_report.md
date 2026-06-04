# NuuksioSparseTrails — family fit (04_rural)

Generated as part of rural map finalization.

## Why this map fits 04_rural

| Criterion | NuuksioSparseTrails |
|-----------|---------------------|
| Geographic scale | Nuuksio National Park OSM (EPSG:3067), sim window **2848 × 2945 m** |
| Network | Sparse trail graph (~326 segments, ~122 nodes); **low spatial coverage (~12%)** |
| Mobility | SPMM, ClusterMovement, MapRouteMovement (ranger patrol) |
| Methodological value | Scarce contacts, long routes, partial partitions, high delay |
| vs urban/campus | No dense grid or pedestrian campus; trails not streets |
| vs vehicles | No taxi/bus grid routes |
| vs stress grid | Real OSM trails, not synthetic `` |

## Expected outcomes (not errors)

> NuuksioSparseTrails is used as a sparse rural trail map. Low spatial coverage, low encounter rates, and low delivery ratios are expected outcomes in this family and should not be interpreted as configuration errors by default.

## Scenario mapping (R1–R12)

| ID | Category | Movement | Patrol route |
|----|----------|----------|--------------|
| R1 Rural_SparseSPMM | realistic | SPMM | no |
| R2 VillagesTrails | realistic | 3× ClusterMovement | no |
| R3 WildlifeTracking | realistic | SPMM | no |
| R4 ParkRangers | realistic | MapRouteMovement | **A_ranger_patrol** |
| R5 MountainRescue | realistic | SPMM | no |
| R6–R7, R9–R12 | extreme control | SPMM (+ levers) | no |
| R8 IntermittentPower | realistic (tech) | SPMM | no |

See `NuuksioSparseTrails_rural_scenario_classification.md` for full notes.