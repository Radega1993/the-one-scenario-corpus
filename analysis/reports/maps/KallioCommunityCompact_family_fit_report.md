# KallioCommunityCompact — family fit (06_social)

Generated as part of social map finalization.

## Why this map fits 06_social

| Criterion | KallioCommunityCompact |
|-----------|------------------------|
| Geographic scale | OSM Kallio, Helsinki (EPSG:3067), sim window **1458 × 1529 m** |
| Network | Compact urban neighbourhood (~7204 segments, ~2741 nodes) |
| Mobility | ClusterMovement (S1, S6) and ShortestPathMapBasedMovement (S2–S5) |
| Methodological value | Dense residential fabric for community contact and mixing studies |
| vs HelsinkiDowntown | Commute-scale CBD — not neighbourhood community dynamics |
| vs campus / rural | Institutional or sparse trail context — not urban barrio |

## Paper-ready statement

> KallioCommunityCompact is a compact urban-community map derived from OSM Kallio. It provides a realistic spatial backdrop for social DTN scenarios: dense street fabric and POI layers for map-constrained mobility (S2–S5), while ClusterMovement scenarios (S1, S6) impose community structure through cluster centers and ranges rather than path constraints on the road network.

## ClusterMovement vs map context

In scenarios based on **ClusterMovement** (S1, S6), community structure is explicitly imposed through `clusterCenter` and `clusterRange`. The road network is **not** used as a path constraint; the map supplies spatial context and a consistent coordinate frame only.

| Mode | Scenarios | Path constraint |
|------|-----------|-----------------|
| Cluster-based | S1 (4 clusters), S6 (12 microclusters) | No — cluster geometry only |
| Map-based | S2–S5 | Yes — SPMM on `roads.wkt` |

## Scenario mapping (S1–S6)

| ID | Category | Movement |
|----|----------|----------|
| S1 | social_strong_communities | ClusterMovement ×4 |
| S2 | social_weak_communities | SPMM |
| S3 | social_periodic_meetings | SPMM |
| S4 | social_random_mixing_control | SPMM |
| S5 | social_two_layer_population | SPMM |
| S6 | social_persistent_family_groups | ClusterMovement ×12 |

See `KallioCommunityCompact_social_scenario_classification.md` for full notes.