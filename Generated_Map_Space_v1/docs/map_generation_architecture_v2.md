# Map generation architecture v2

**Status:** engineering_validated — Phase B OSM complete; revalidation GO; stratified saturation decision **BALANCED_1600** (GMS-v1 still open)  
**Baseline (frozen/archived):** `map_design_space_saturation_v1` → `scenarios/_archive/map_space_phase1_baseline/map_space_saturation_v1/`  
**Revised:** `map_design_space_revised_v2` → `scenarios/Generated_Map_Space_v1/`

## Pool role

`map_space_revised_v2` has passed **engineering validation** and **pool revalidation**.  
Stratified saturation ([`map_space_revised_v2_saturation_report.md`](map_space_revised_v2_saturation_report.md)) recommends **balanced expansion to 1600** — **GMS-v1 is not frozen**; **SMS-v1 remains blocked**.

- Protocol (pre-registered): [`saturation_protocol.yaml`](../config/saturation_protocol.yaml)
- Freeze snapshot: [`map_space_revised_v2_pool_freeze.json`](../data/map_space_revised_v2_pool_freeze.json)
- Revalidation: [`map_space_revised_v2_pool_revalidation_attrition.md`](map_space_revised_v2_pool_revalidation_attrition.md)
- `target_total_default: 1200` = `initial_engineering_target`
- Global fractions 0.45 / 0.40 / 0.15 are soft engineering targets vs [`archetype_source_allocation.yaml`](../config/archetype_source_allocation.yaml).

## Design principle

Three construction sources are first-class and explicit:

| source_type | Builder | Trace role involvement |
|-------------|---------|------------------------|
| `osm` | `builders.osm_builder` | Optional `osm_anchor_support` → `provenance.trace_support[]` |
| `synthetic` | `builders.synthetic_builder` | None (`trace_id` empty) |
| `trace_reference_synthetic` | `builders.trace_builder` | `parameterize_generator` + extractor |

Trace **roles** are not source types. Roles live in
[`trace_to_map_generation_policy.yaml`](../config/trace_to_map_generation_policy.yaml).

Rejected as source types (for now): `trace_derived_geometry`, `trace_anchored_osm`
(see revised YAML `source_types.rejected_for_now`).

## Seed policy

- `global_seed_default: 42` is **not scientifically optimized**; it makes stochastic generation deterministic and auditable.
- Candidate seed:
  `SHA256(global_seed :: map_id :: archetype :: source_type :: trace_id :: generator_type)[:8]`.
- Inserting an extra candidate must not change seeds of existing maps with the same identity fields.

## Trace → geometry

Documented mapping:
[`trace_to_geometry_parameter_mapping_v2.md`](trace_to_geometry_parameter_mapping_v2.md) +
[`trace_statistic_to_generator_parameter_v2.csv`](../data/trace_statistic_to_generator_parameter_v2.csv).
Contacts ≠ streets; overlays only snap discrete generator knobs.

## Package layout

```text
scenarios/Generated_Map_Space_v1/
  config/                 design space, protocol, allocation, trace policy
  scripts/
    generate.py           GMS CLI
    map_generation/       planner, executor, builders, traces, validation
    validate.py / extract_features.py / analyze_*.py
    watch_osm_progress.sh / run_osm_until_ok.sh
  docs/ data/ figures/ ops/
  batch_*/ previews/ osm_cache/ manifest_maps_all.csv
```

Shared geometry helpers remain in `scenarios/setup/` (`map_space_osm_builder`, `map_space_topology`, …).

Legacy CLI shim (forwards to `scripts/generate.py`):
[`scenarios/setup/generate_map_space_saturation_v1.py`](../../setup/generate_map_space_saturation_v1.py)

```bash
python scenarios/Generated_Map_Space_v1/scripts/generate.py \
  --config scenarios/Generated_Map_Space_v1/config/map_design_space.yaml \
  --dry-run --write-plan --target-total 90 --seed 42
```

Dry-run: no OSM download, no WKT write, no raw-trace copy. Exit code ≠ 0 on CRITICAL issues.

## Provenance

Every planned candidate carries `config_hash`, `seed`, `builder`, `source_type`,
and source-specific fields (`anchor_id` / `trace_id` / `generator_type` /
`extracted_parameters`). See `provenance_for_candidate()`.

## Synthetic generators (13 configured + 1 orphan)

Configured: grid, jittered_grid, radial_city, hub_and_spoke, corridor,
tree_trails, sparse_rural, clustered_communities, partitioned_bridge,
disrupted_grid, conference_event_compact, campus_compact, bus_route_corridor.

Implemented but not in YAML: `multi_component_with_bridges`.

**Note:** `partitioned_bridge` connects partitions with bridge edges (typically
1 component). The intended signal is partition/community structure, not
`n_components >= 2`.

## Degenerate synthetic policy

Failed synthetic builds remain in `manifest_maps_all.csv` as
`FAIL_BUILD_SYNTHETIC_DEGENERATE` (see
[`synthetic_generation_failure_analysis_v2.md`](synthetic_generation_failure_analysis_v2.md)).
Do not silently regenerate until PASS without recording attempts (survival bias).

## Safety

- Does not write into `map_space_saturation_v1/` or `selected_map_space_v1/`.
- Does not redistribute CRAWDAD raw payloads.
- Full pool generation is enabled via `--generate` into `map_space_revised_v2/`.
- OSM acquisition is bounded by `--max-downloads` (continue only after methodological go).
