# Trace → map generation review v1

**Inventory:** [`../../external_traces/registry/real_trace_inventory_v1.csv`](../../external_traces/registry/real_trace_inventory_v1.csv)  
**Policy:** [`../config/trace_to_map_generation_policy_v1.yaml`](../config/trace_to_map_generation_policy_v1.yaml)  
**Matrix:** [`../data/trace_to_archetype_generation_matrix_v1.csv`](../data/trace_to_archetype_generation_matrix_v1.csv)

## Rule

A real trace is **not** automatically a map. Each of the 18 registered packages
has exactly one primary `generation_role` in the policy.

## Classification summary

| Role | Count | Enabled |
|------|------:|--------:|
| parameterize_generator | 5 | 5 |
| osm_anchor_support | 3 | 3 |
| evidence_only | 5 | 0 |
| unsupported_for_generation | 2 | 0 |
| future_candidate | 3 | 0 |

### Enabled → `trace_reference_synthetic` maps

| trace_id | extractor | targets |
|----------|-----------|---------|
| haggle_one_cambridge_city_complete | standard_events_contact_summary_v1 | clustered_communities, conference_event_compact |
| upmc_rollernet_20090202 | static_parameters_v1 (provisional) | corridor |
| st_andrews_sassy_20110603 | static_parameters_v1 (provisional) | clustered_communities |
| st_andrews_locshare_20111012 | static_parameters_v1 (provisional) | campus_compact, clustered_communities |
| oviedo_asturies_er_20160808 | static_parameters_v1 (provisional) | sparse_rural, disrupted_grid, partitioned_bridge |

Haggle ONE extraction was verified against validated events:
**52 nodes / 10873 contacts / 987529 s**.

### Enabled → OSM provenance support only

| trace_id | OSM anchors |
|----------|-------------|
| epfl_mobility_20090224 | sf_cabspotting_downtown |
| umass_diesel_20080914 | dieselnet_amherst |
| dartmouth_wardriving_20060602 | mit_campus_reality (campus-family proxy) |

### Non-generative

- cambridge_haggle_* → evidence_only (Haggle ONE is the processed form)
- umass_diesel older → evidence_only
- - roma_taxi, RioBuses, vanlan → future_candidate (GPS/schema/anchor pending)

## Baseline contrast

In `map_design_space_saturation_v1`, four narrative anchors
(`infocom_*`, `rollernet_trace`, `haggle_contacts_only`) selected generators by
**label only**. Revised v2 binds generation to the real-trace inventory + policy
+ extractors.
