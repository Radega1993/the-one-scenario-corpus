# Problematic mobility scenarios — review

Generated: 2026-05-31 15:38 UTC

Backup: `scenarios/_archive/settings_backup_20260531_173603`

## Decision

All four scenarios are **repaired and kept in the environmental core** (`corpus_v1`). `ClusterMovement` was replaced with map-aware models (`MapRouteMovement`, `ShortestPathMapBasedMovement`).

## S1: `S1_StrongCommunities_SeparateClusters` → `S1_StrongCommunities_LimitedMixing`

- **Map:** `KallioCommunityCompact`
- **worldSize:** 1458, 1529
- **Hosts:** 110
- **Movement (legacy):** ClusterMovement | ClusterMovement | ClusterMovement | ClusterMovement
- **ClusterMovement groups:** 4
- **transmitRange:** 10

**Spatial metrics (legacy name, if simulated):**
- world 2.2% · map bbox 1.0256% · road cells 1.0732%

**Weakness:** nodes moved in circular clusters off the road network; heatmaps showed isolated blobs; map was largely decorative for protocol evaluation.

**S1 note:** TP03/08/10/11 previously hit simulation timeouts (~10400s) under spatial overlay.

## S6: `S6_FamilyGroups_SmallPersistent` → `S6_FamilyGroups_LocalRoutines`

- **Map:** `KallioCommunityCompact`
- **worldSize:** 1458, 1529
- **Hosts:** 42
- **Movement (legacy):** ClusterMovement | ClusterMovement | ClusterMovement | ClusterMovement | ClusterMovement | ClusterMovement | ClusterMovement | ClusterMovement | ClusterMovement | ClusterMovement | ClusterMovement | ClusterMovement
- **ClusterMovement groups:** 12
- **transmitRange:** 10

**Spatial metrics (legacy name, if simulated):**
- world 2.0% · map bbox 1.6667% · road cells 2.0488%

**Weakness:** nodes moved in circular clusters off the road network; heatmaps showed isolated blobs; map was largely decorative for protocol evaluation.

**S1 note:** TP03/08/10/11 previously hit simulation timeouts (~10400s) under spatial overlay.

## D1: `D1_ShelterHotspots_Clusters` → `D1_ShelterHotspots_EmergencyMobility`

- **Map:** `HelsinkiDisrupted`
- **worldSize:** 2067, 2206
- **Hosts:** 80
- **Movement (legacy):** ClusterMovement | ClusterMovement | ClusterMovement | ShortestPathMapBasedMovement
- **ClusterMovement groups:** 3
- **transmitRange:** 10

**Spatial metrics (legacy name, if simulated):**
- world 26.76% · map bbox 37.0432% · road cells 62.3415%

**Weakness:** nodes moved in circular clusters off the road network; heatmaps showed isolated blobs; map was largely decorative for protocol evaluation.

**S1 note:** TP03/08/10/11 previously hit simulation timeouts (~10400s) under spatial overlay.

## R2: `R2_VillagesTrails_ThreeClusters` → `R2_VillagesTrails_InterVillage`

- **Map:** `NuuksioSparseTrails`
- **worldSize:** 2848, 2945
- **Hosts:** 36
- **Movement (legacy):** ClusterMovement | ClusterMovement | ClusterMovement
- **ClusterMovement groups:** 3
- **transmitRange:** 10

**Spatial metrics (legacy name, if simulated):**
- world 6.24% · map bbox 8.0579% · road cells 6.3776%

**Weakness:** nodes moved in circular clusters off the road network; heatmaps showed isolated blobs; map was largely decorative for protocol evaluation.

**S1 note:** TP03/08/10/11 previously hit simulation timeouts (~10400s) under spatial overlay.