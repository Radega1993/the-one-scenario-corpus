# HelsinkiDisrupted — family fit (05_disaster)

Generated as part of disaster map finalization.

## Why this map fits 05_disaster

| Criterion | HelsinkiDisrupted |
|-----------|-------------------|
| Geographic scale | Kalasatama / Sörnäinen OSM (EPSG:3067), sim window **2067 × 2206 m** |
| Network | Urban drive network (~8398 segments, ~3142 nodes); partial connectivity |
| Mobility | ClusterMovement, SPMM, MapRouteMovement (emergency/UAV) |
| Methodological value | Degraded comms, hotspots, partitions, mule bridges, critical TTL |
| vs HelsinkiDowntown | Normal urban commuting — not disaster-degraded |
| vs stress grid | Real OSM harbour/industrial fabric, not synthetic |

## Expected outcomes (not errors)

> HelsinkiDisrupted is used as a degraded urban disaster map. Low delivery, high latency, and structural partitioning can be expected outcomes in specific scenarios and should not be interpreted as configuration errors by default.

## Scenario mapping (D1–D9)

| ID | Category | Role |
|----|----------|------|
| D1 | realistic | Shelter hotspots (clusters) |
| D2 | bridge/mule | Partitioned city + SPMM mule |
| D3–D4, D8 | realistic | Aftershock, triage, infrastructure return |
| D5 | bridge/mule | UAV on A_emergency_route; civilians SPMM |
| D6, D9 | critical TTL | Short / 1 min TTL controls |
| D7 | stress control | High load traffic storm |

See `HelsinkiDisrupted_disaster_scenario_classification.md` for full notes.
