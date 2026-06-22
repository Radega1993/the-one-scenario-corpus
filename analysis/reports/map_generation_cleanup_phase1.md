# Map Generation Cleanup Phase 1

Date: 2026-06-16  
Scope: `scenarios/` map-generation cleanup and legacy freeze.

## Summary

This phase removed generated `map_space_v1` outputs and froze the previous methodology as legacy.  
The repository is now prepared for a new batch-generation pipeline with feature-space saturation stopping criteria.

## What was removed

- Generated outputs under `scenarios/map_space_v1/`:
  - `real_osm/`
  - `synthetic/`
  - `selected_maps/`
  - `previews_validation/`
  - `_archive/` (internal to removed output tree)
  - `manifest_maps.csv`
  - `generation_config_used.yaml`
- Derived analysis data:
  - `scenarios/analysis/data/map_space_v1_validation.csv`
  - `scenarios/analysis/data/map_space_v1_features.csv`

`scenarios/map_space_v1/README.md` was recreated as a minimal placeholder for the redesign phase.

## What was archived

### Reports archived

Moved to `scenarios/analysis/reports/_archive/map_space_v1_phase1/`:

- `map_space_v1_phase0_audit.md`
- `map_space_v1_design.md`
- `map_space_v1_generation_report.md`
- `map_space_v1_validation_report.md`
- `map_space_v1_features_report.md`
- `map_space_v1_selected_maps.md`
- `map_space_v1_pruning_methodology.md`
- `map_generation_refactor_v1.md`
- `scenario_generation_with_selected_maps.md`

### Config archived

Moved to `scenarios/analysis/config/_archive/map_space_v1_phase1/`:

- `map_design_space_v1.yaml`

### Scripts archived

Moved to `scenarios/setup/_legacy/map_space_v1_phase1/`:

- `generate_map_space_v1.py`
- `map_space_synthetic.py`
- `validate_map_space_v1.py`
- `extract_map_features_v1.py`
- `prune_map_space_v1.py`
- `prune_legacy_map_pool_v1.py`
- `install_selected_maps_v1.py`
- `map_asset_generator_v1.py`
- `seed_osm_cache_from_legacy.py`

### Migration docs archived

Moved under:

- `scenarios/scenario_space_v1/migration/_archive_map_space_v1_phase1/`

Archived entries include previous phase tracking (`phase0`–`phase3`) and `legacy_pool_cleanup.md`.

## Script classification

| Script | Classification | Notes |
|---|---|---|
| `scenarios/setup/map_geometry.py` | keep_active | Shared geometry and world-size utilities |
| `scenarios/setup/map_space_topology.py` | keep_active | Core topology/feature logic (reused in redesign) |
| `scenarios/setup/repair_map_pois.py` | keep_active | Reusable POI repair utility |
| `scenarios/setup/validate_bus_routes.py` | keep_active | Reusable route validation utility |
| `scenarios/setup/generate_scenario_space_v1.py` | refactor_needed | Supports manifest mode but depends on removed v1 pipeline artifacts |
| `scenarios/setup/map_config.py` | legacy_only | Six-map corpus configuration |
| `scenarios/setup/prepare_maps.py` | legacy_only | Legacy six-map preparation |
| `scenarios/setup/download_maps.sh` | legacy_only | Legacy six-map download (now explicitly marked LEGACY) |
| `scenarios/setup/bootstrap_maps.sh` | legacy_only | Legacy six-map bootstrap |
| `scenarios/setup/validate_maps.py` | legacy_only | Legacy six-map validation |
| `scenarios/setup/validate_map_pois.py` | legacy_only | Uses `ACTIVE_MAPS` assumptions |
| `scenarios/setup/build_map_assets_inventory.py` | legacy_only | Six-map inventory path |
| `scenarios/setup/calibrate_world_size_per_map.py` | legacy_only | Six-map calibration assumptions |
| `scenarios/setup/_legacy/map_space_v1_phase1/*` | remove_from_pipeline_but_keep_archived | Frozen reference implementation from old methodology |

## Legacy marks applied

`legacy_only` headers were verified/added in:

- `scenarios/setup/prepare_maps.py`
- `scenarios/setup/download_maps.sh`
- `scenarios/setup/bootstrap_maps.sh`

## Folders kept for reproducibility

These were intentionally preserved:

- `scenarios/maps/wkt/` (6 canonical maps needed by `corpus_v1`)
- `scenarios/maps/raw/` (legacy raw map sources)
- `scenarios/corpus_v1/`
- `scenarios/base_scenarios/`
- top-level `reports/` simulation results

## Risks in previous generation approach

- Fixed/preset generation targets encouraged a static corpus rather than adaptive saturation.
- Legacy OSM cache reuse could produce duplicated topology under different IDs.
- Mixed methodology outputs and stale reports made provenance harder to audit.
- Pipeline intent (exploratory map-space) became conflated with benchmark-corpus reproducibility.

## Proposed new pipeline (v2)

1. Batch candidate generation from justified anchors/config.
2. Per-map validation.
3. Topology feature extraction.
4. Coverage/saturation measurement in normalized feature space.
5. Stop when marginal gain stays below threshold for N consecutive batches.

## Integrity confirmation

No direct edits were made in:

- `scenarios/corpus_v1/`
- `scenarios/base_scenarios/`
- `scenarios/maps/wkt/`

Verification command used at end of phase:

```bash
git status --short scenarios/corpus_v1 scenarios/base_scenarios scenarios/maps/wkt
```
