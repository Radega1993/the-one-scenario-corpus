# Map generation audit v2

**Status:** under_review  
**Date:** 2026-07-23  
**Scope:** documentation, configuration, and code for map generation under `scenarios/`  
**Baseline output (do not overwrite):** `scenarios/map_space_saturation_v1/`  
**Revised design (this work):** `map_design_space_revised_v2` + `scenarios/setup/map_generation/`

## 1. Executive verdict

In the baseline pipeline, **`trace_reference_synthetic` does not read real traces**.

The planner maps four YAML anchors with `anchor_type: trace_reference_not_map` to synthetic `generator_id` values, then builds geometry with the same procedural path as pure synthetics. The string `source_type=trace_reference_synthetic` is a **label**, not a data dependency.

No map-generation module imports `scenarios/external_traces/`, `real_trace_inventory`, or `StandardEventsReader`. Those exist only in the separate external-traces ingest/validation tooling.

## 2. Baseline flow (as implemented)

```text
map_design_space_saturation_v1.yaml
        |
        v
generate_map_space_saturation_v1.py :: compute_plan()
  ├─ OSM fraction (osm_fraction only; synthetic_fraction ignored)
  │    → bbox + hardcoded cardinal offsets/windows
  │    → OSMnx Overpass → GraphML cache → roads.wkt
  └─ else synthetic path
       ├─ if generator mapped from a trace-only anchor
       │     → source_type = trace_reference_synthetic
       │     → anchor_id = label only (no file I/O)
       └─ else source_type = synthetic
             → GENERATORS[generator_type](params, rng) → roads.wkt
        |
        v
metadata.json + preview + manifest_maps_all.csv
        |
        v
validate → extract features → saturation analysis (separate scripts)
```

### Entry point modes

[`scenarios/setup/generate_map_space_saturation_v1.py`](../../setup/generate_map_space_saturation_v1.py)

| Flag | Behaviour |
|------|-----------|
| `--estimate-only` | Plan in memory; print OSM vs synthetic counts |
| `--plan-only` | Write planned manifest / OSM queue; no download/build |
| `--acquire-osm` | Bounded OSM downloads into cache |
| `--build` | Build WKT from cache or synthetics |
| `--generate` | Plan + build (download only if `--max-downloads > 0`) |

Defaults: `--target-total 800`, `--seed 42`.

## 3. Canonical vs non-canonical artefacts

| Path | Function | Apparent version | Status | Recommendation |
|------|----------|------------------|--------|----------------|
| `analysis/config/map_design_space_saturation_v1.yaml` | Baseline design spec | 1.0 | **baseline** / under_review | Keep frozen; do not treat as revised truth |
| `analysis/config/map_design_space_revised_v2.yaml` | Revised design | 2.0 | **canonical** (revised) | Use for future regeneration |
| `analysis/config/trace_to_map_generation_policy_v1.yaml` | Trace → generation roles | 1.0 | **canonical** | Required for planner |
| `setup/generate_map_space_saturation_v1.py` | Baseline orchestrator | v1 | **baseline** + wrapper | Keep CLI; delegate v2 dry-run |
| `setup/map_space_osm_builder.py` | OSM acquire/convert | v1 | **baseline** reusable | Called by v2 OSM builder |
| `setup/map_space_synthetic.py` | 14 generators (13 in YAML) | v1 | **baseline** reusable | Keep all 13; document orphan |
| `setup/map_space_synthetic_builder.py` | Synthetic build/validate | v1 | **baseline** reusable | Reuse from v2 |
| `map_space_saturation_v1/` | Generated pool | executed | **baseline** | Never overwrite in this task |
| `selected_map_space_v1/` | Phase-2 selection | closed | **baseline** | Untouched |
| `external_traces/` | Real-trace registry + raw | v1 | **canonical** for traces | Connect via inventory/policy |
| `analysis/reports/INDEX_MAP_GENERATION_PHASE1_FINAL.md` | Phase-1 index | final | **canonical** Phase-1 narrative | Historical |
| `analysis/reports/map_space_saturation_methodology_final.md` | Methodology | final | **canonical** Phase-1 | Historical |
| `analysis/reports/map_design_space_saturation_v1.md` | Early design doc | early | **superseded** as run status | Keep as history |
| `internal/map_generation_phase1_inventory_v1_UPDATED.md` | Phase-1 inventory | updated | **duplicate** naming | Links to missing non-`_UPDATED` |
| `internal/map_*_UPDATED.md` | Spanish narratives | updated | **duplicate** | Do not delete; prefer non-suffix when consolidating later |
| `analysis/reports/map_archetype_justification_v1.md` | 15-archetype justification | v1 | **canonical** EN | Expand with v2 pointer only |
| `internal/map_archetype_justification_v1.md` | Spanish parallel | v1 | **duplicate** | Link to EN |

## 4. What documentation claims vs what code does

| Claim | Reality |
|-------|---------|
| Trace references parameterize synthetics from contact traces | **False for data I/O.** Mapping is hard-coded anchor→generator; parameters come from YAML discrete grids, not from trace files |
| `trace_reference_synthetic` is a distinct construction source | Only distinct as a **manifest label**; build path identical to `synthetic` |
| YAML seed formulas (sha256 of anchor/variant/…) | Python uses `global_seed + map_id` (and attempt) via `stable_seed` |
| `synthetic_fraction` / `batch_sizes` / `variants_per_batch` drive composition | Mostly **not read**; batches hard-coded `[100…2000]`; only `osm_fraction` used |
| `--archetype-csv` constrains generation | File existence checked; CSV **never loaded** by generator |
| `partitioned_bridge` yields ≥2 components | Generator **adds bridges** → typically 1 connected component |
| YAML `status: specification_only` | Pool already generated up to N≈2000 robustness |

## 5. Source types in baseline

Operational values: `osm`, `synthetic`, `trace_reference_synthetic`.

| source_type | Input consumed | Output | Validation |
|-------------|----------------|--------|------------|
| `osm` | Anchor bbox/place + Overpass | GraphML + `roads.wkt` + metadata | Topology/world-size checks in OSM builder |
| `synthetic` | Generator id + discrete params + seed | `roads.wkt` + metadata | ≥20 nodes/edges, length, world axis |
| `trace_reference_synthetic` | Same as synthetic + trace-only `anchor_id` label | Same as synthetic | Same as synthetic |

**Decision for revised v2:** keep these three source types. Do **not** add `trace_derived_geometry` or `trace_anchored_osm` as source types. Trace **roles** (`osm_anchor_support`, `parameterize_generator`, …) attach provenance without duplicating the source-type taxonomy.

## 6. Synthetic generators

Implemented in [`map_space_synthetic.py`](../../setup/map_space_synthetic.py) `GENERATORS`:

`grid`, `jittered_grid`, `radial_city`, `hub_and_spoke`, `corridor`, `tree_trails`, `clustered_communities`, `partitioned_bridge`, `disrupted_grid`, `sparse_rural`, `conference_event_compact`, `campus_compact`, `bus_route_corridor`, plus orphan **`multi_component_with_bridges`** (code yes, YAML no).

## 7. Real traces

Canonical registry: [`external_traces/registry/real_trace_inventory_v1.csv`](../../external_traces/registry/real_trace_inventory_v1.csv) — **18** packages.

Only `haggle_one_cambridge_city_complete` is validated StandardEventsReader (52 nodes, 10873 contacts, 987529 s). Dartmouth campus packages are README-only. Staging under `map_space_v1/external_traces/` is already ingested; no uningested package found at audit time.

## 8. Findings

### CRITICAL

| ID | Finding | Evidence | Impact | Fix in this task? |
|----|---------|----------|--------|-------------------|
| C1 | `trace_reference_synthetic` is label-only | `generate_map_space_saturation_v1.py` L332–342, L482–495; synthetic builder never opens trace files | Paper claim of “real-trace-supported construction” is unsupported by code | **Yes** — policy + extractors + planner provenance |
| C2 | Map pipeline disconnected from `external_traces` | No imports/usages in `scenarios/setup/*map*` | New IEEE DataPort inventory unused by generation | **Yes** |

### HIGH

| ID | Finding | Evidence | Impact | Fix now? |
|----|---------|----------|--------|----------|
| H1 | `rollernet_trace.archetype: corridor` ≠ `corridor_linear` | YAML L284 | ID mismatch vs 15-archetype contract | **Yes** in v2 config |
| H2 | YAML seed formulas ≠ Python | YAML L466–469, L492–495 vs synthetic builder `stable_seed` | Reproducibility docs wrong | **Yes** — document & implement explicit seed policy in v2 |
| H3 | Many YAML batch/composition fields ignored | Hardcoded `BATCH_TARGETS`; only `osm_fraction` | Spec ≠ execution | **Yes** — v2 planner reads declared policy |
| H4 | Dartmouth campus marked downloaded but empty | ~2 KB README only | False campus evidence | **Yes** — policy `unsupported_for_generation` |

### MEDIUM

| ID | Finding | Fix now? |
|----|---------|----------|
| M1 | `--archetype-csv` unused | Document; v2 validates archetypes from config list |
| M2 | `partitioned_bridge` vs `n_components_min: 2` | Document in architecture; do not change generator silently |
| M3 | Duplicate `_UPDATED` internal docs / broken links | Inventory only; no deletes |
| M4 | Ingest summary 17 vs registry 18 | Documented (Haggle ONE pre-existing) |

### LOW / INFO

| ID | Finding | Fix now? |
|----|---------|----------|
| L1 | `multi_component_with_bridges` orphan | Document; keep code |
| I1 | No unit tests for map generation | **Yes** — add `tests/scenarios/map_generation/` |
| I2 | Phase-1 narratives remain valid as baseline history | Pointers only |

## 9. What this task delivers next

1. Revised config + trace policy for all 18 traces  
2. `scenarios/setup/map_generation/` with planners/builders/extractors  
3. Dry-run / write-plan without network or pool overwrite  
4. Tests proving OSM, synthetic, and `trace_reference_synthetic` are explicitly connected  

**Out of scope:** full pool regeneration, saturation recomputation, SMS reselection, mass ONE conversion of all CRAWDAD packages.
