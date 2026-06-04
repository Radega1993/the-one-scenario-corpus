# corpus_v1 mobility repair changelog (2026-05-31)

## Summary

Repaired map-aware mobility for four environmental base scenarios and regenerated 48 `corpus_v1` TP variants.

## Renames

| Old base | New base |
|----------|----------|
| `S1_StrongCommunities_SeparateClusters` | `S1_StrongCommunities_LimitedMixing` |
| `S6_FamilyGroups_SmallPersistent` | `S6_FamilyGroups_LocalRoutines` |
| `D1_ShelterHotspots_Clusters` | `D1_ShelterHotspots_EmergencyMobility` |
| `R2_VillagesTrails_ThreeClusters` | `R2_VillagesTrails_InterVillage` |

## Mobility

- Removed `ClusterMovement` as primary model.
- Added route WKT under `data/KallioCommunityCompact/` (S1, S6) and `data/NuuksioSparseTrails/` (R2).
- D1: SPMM civilians + MapRoute emergency/mule groups (HelsinkiDisrupted routes).

## Artifacts

- Backup: `scenarios/_archive/settings_backup_20260531_173603/`
- Scripts: `mobility_repair_routes.py`, `regenerate_corpus_tp_from_base.py`, `fix_manifest_after_mobility_repair.py`, `validate_scenario_geometry.py`
- Reports: `problematic_mobility_scenarios_review.md`, `problematic_scenarios_geometry_validation.md`, `problematic_scenarios_tp_validation.md`, `problematic_scenarios_resim_commands.md`, `problematic_scenarios_before_after.md`, `problematic_scenarios_paper_note.md`
- Manifest: restored to **540** rows

## Not changed

- TP01–TP12 definitions (`lib/traffic_profile_generator.py`)
- Map WKT sources (only added auxiliary route files)
- Other 41 base scenarios

## Follow-up

Re-simulate 48 scenarios; refresh `output_metrics.csv`, spatial metrics, and diversity pipeline.