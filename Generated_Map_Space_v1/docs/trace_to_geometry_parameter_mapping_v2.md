# Trace statistic → generator parameter → topology (v2)

**Status:** methodological_audit  
**Code:** `map_generation.traces.extractors.map_extracted_to_generator_params`  
**Table:** [`../data/trace_statistic_to_generator_parameter_v2.csv`](../data/trace_statistic_to_generator_parameter_v2.csv)

## Principle

Real traces supply **contact / encounter / GPS summary statistics**. They do **not** supply street centreline geometry. Overlay only snaps **discrete generator knobs** whose change is expected to move topology counts (`n_nodes`, `n_edges`, cluster structure). Anything else is `not_mapped` or `under_specified`.

## Active extractors

| Extractor | Typical inputs | Geometry claim |
|-----------|----------------|----------------|
| `standard_events_contact_summary_v1` | ONE CONN up/down | Parameterize configured generators only |
| `rollernet_contacts_v1` | RollerNet contacts.dat | Corridor length heuristic from duration |
| `sassy_encounters_v1` | Social encounter CSV | Cluster counts from agent count |
| `locshare_encounters_v1` | LocShare encounters | Campus / cluster scale proxies |
| `gps_trace_summary_v1` | GPS points | OSM anchor support only (no generator overlay) |
| `metadata_only_v1` | Registry metadata | Provenance only |

## Mapping highlights

### Haggle / Oviedo (`standard_events_*`)

- `n_nodes` → `clustered_communities.{n_clusters,nodes_per_cluster}` and `density_proxy` → `intra_density`.
- `n_nodes` → `conference_event_compact.{hall_count,rooms_per_hall}` (minimal documented rule; **contacts ≠ rooms**).
- `n_nodes` → `sparse_rural.n_nodes`, `disrupted_grid.{grid_rows,grid_cols}`, `partitioned_bridge.nodes_per_partition`.
- **Not inferred:** contact count as road-edge count; duration as map metres (except RollerNet).

### RollerNet

- `duration_seconds` → `corridor.length_m` in [2000, 8000].
- `width_m` / `branch_prob` currently **under_specified** (static defaults documented in CSV).

### Sassy / LocShare

- Agent count drives cluster / building discrete knobs.
- Mean contact duration → `intra_density` remains **under_specified** (proposed percentile rule; not coded).

## Under-specified → explicit minimum rules (documented)

| Case | Rule (this phase) | Regenerating pool? |
|------|-------------------|--------------------|
| Haggle → conference halls/rooms | `hall_count≈n/16`, `rooms≈√n`, nearest discrete | No (engineering pool frozen until OSM go) |
| Haggle density → intra_density | `0.4 + min(0.5, 2·density_proxy)` | No |
| Oviedo → disrupted grid size | `side≈√n_nodes` for rows/cols | No |
| RollerNet width/branches | Keep static; mark under_specified | No |
| Sassy duration → density | Proposed only | No |

## Semantic smoke

Tests in `tests/scenarios/map_generation/test_trace_overlay_semantics_v2.py` assert that the same generator mid-defaults **with** vs **without** a real overlay differ in at least one topology-relevant parameter (or fail explicitly if overlay is a no-op when a mapped statistic is present).
