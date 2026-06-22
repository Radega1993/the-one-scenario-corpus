# INDEX_MAP_GENERATION_REDESIGN

**Phase 1 closure (final):** [`INDEX_MAP_GENERATION_PHASE1_FINAL.md`](INDEX_MAP_GENERATION_PHASE1_FINAL.md) — N=1200, saturation confirmed, reviewer-facing artefacts.

## Phase 1 — Cleanup and Legacy Freeze (completed)

- [`map_generation_cleanup_phase1.md`](map_generation_cleanup_phase1.md)

## Current active baseline

- Keep active utilities:
  - `scenarios/setup/map_geometry.py`
  - `scenarios/setup/map_space_topology.py`
  - `scenarios/setup/repair_map_pois.py`
  - `scenarios/setup/validate_bus_routes.py`
- Active anchor/policy config:
  - `scenarios/analysis/config/real_map_anchors_v1.yaml`
  - `scenarios/analysis/config/map_asset_policy_v1.yaml`

## Legacy frozen (do not use for new methodology)

- Archived scripts:
  - `scenarios/setup/_legacy/map_space_v1_phase1/`
- Legacy six-map pipeline:
  - `scenarios/setup/download_maps.sh`
  - `scenarios/setup/prepare_maps.py`
  - `scenarios/setup/bootstrap_maps.sh`
- Archived reports/config:
  - `scenarios/analysis/reports/_archive/map_space_v1_phase1/`
  - `scenarios/analysis/config/_archive/map_space_v1_phase1/`
- Archived migration trace:
  - `scenarios/scenario_space_v1/migration/_archive_map_space_v1_phase1/`

## Redesign roadmap

### Phase 2 — Saturation design space (specification complete)

- Config: `scenarios/analysis/config/map_design_space_saturation_v1.yaml`
- Methodology: [`map_design_space_saturation_v1.md`](map_design_space_saturation_v1.md)
- Archetypes: `scenarios/analysis/data/map_archetype_definitions_v1.csv`
- **No maps generated in this phase** — batch runner is next implementation step.

### Phase 3 (planned) — Batch generation + validation

- Batch-oriented generator runner wired to saturation YAML.
- Reuse topology core from `map_space_topology.py`.
- Persist per-batch quality gates and provenance.

### Phase 4 (planned) — Saturation monitoring

- Monitor normalized feature-space coverage over batches.
- Stop when marginal gain remains below threshold for N consecutive batches.

### Phase 5 (planned) — Scenario integration

- Couple only validated, non-duplicate selected maps to scenario generation.
- Keep traffic-profile application out of this structural phase.
