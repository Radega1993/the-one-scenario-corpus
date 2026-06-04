# KallioCommunityCompact — social scenario classification

Generated: 2026-05-28T18:25:19

## ClusterMovement note

In scenarios based on ClusterMovement (S1, S6), community structure is explicitly imposed through cluster centers and ranges. The road network is **not** used as a path constraint; the compact urban map provides spatial context and a consistent coordinate system.

- Cluster-based (S1, S6): 2
- Map-based SPMM (S2–S5): 4

## Scenarios

| ID | Category | Movement | Map-constrained | Hosts | Notes |
|----|----------|----------|-----------------|-------|-------|
| S1_StrongCommunities_SeparateClusters | social_strong_communities | ClusterMovement | no | 110 | 4 separated clusters; no bridge; low inter-community delivery expected (TP12) |
| S2_WeakCommunities_HighMixing | social_weak_communities | ShortestPathMapBasedMovement | yes | 80 | 80 hosts SPMM; high mixing on compact map |
| S3_PeriodicMeetings_RegularRhythm | social_periodic_meetings | ShortestPathMapBasedMovement | yes | 50 | Long waitTime; regular rhythm by mobility params, not scheduled events |
| S4_RandomMixing_NoHotspots | social_random_mixing_control | ShortestPathMapBasedMovement | yes | 60 | No cluster/POI attractors; map paths only |
| S5_TwoLayer_StudentsStaff | social_two_layer_population | ShortestPathMapBasedMovement | yes | 75 | Students vs staff speed/wait; heterogeneous social layers |
| S6_FamilyGroups_SmallPersistent | social_persistent_family_groups | ClusterMovement | no | 42 | 12 microclusters; persistent family-scale communities |