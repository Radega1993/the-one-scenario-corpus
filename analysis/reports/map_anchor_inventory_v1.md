# Map anchor inventory (v1)

Generated: 2026-06-22 09:23 UTC

Source: `map_design_space_saturation_v1.yaml` (`real_anchors.anchors`)

## Summary

| Metric | Count |
|--------|-------|
| Declared anchors in YAML | **19** |
| OSM-downloadable (`osm_bbox` / `osm_place`) | **15** |
| Trace-only (`trace_reference_not_map`) | **4** |
| Anchors with ≥1 valid map (features CSV) | **19** |
| Valid maps without geographic anchor_id | **570** |

## Full inventory

| anchor_id | anchor_type | archetype | OSM | trace-only | n_valid_maps |
|-----------|-------------|-----------|-----|------------|--------------|
| helsinki_downtown | osm_bbox | dense_urban_irregular | yes | no | 41 |
| kumpula_campus | osm_bbox | campus_compact | yes | no | 41 |
| kallio_community | osm_bbox | compact_residential | yes | no | 41 |
| manhattan_midtown | osm_bbox | urban_grid | yes | no | 33 |
| sf_cabspotting_downtown | osm_bbox | dense_urban_irregular | yes | no | 41 |
| sf_mission_corridor | osm_bbox | corridor_linear | yes | no | 41 |
| dieselnet_amherst | osm_place | bus_route_urban_suburban | yes | no | 38 |
| cambridge_haggle | osm_bbox | dense_urban_irregular | yes | no | 42 |
| mit_campus_reality | osm_bbox | campus_compact | yes | no | 41 |
| infocom_event_compact | trace_reference_not_map | conference_event_compact | no | yes | 37 |
| infocom_2006_trace | trace_reference_not_map | conference_event_compact | no | yes | 38 |
| rollernet_trace | trace_reference_not_map | corridor | no | yes | 59 |
| haggle_contacts_only | trace_reference_not_map | clustered_communities | no | yes | 75 |
| nuuksio_sparse_trails | osm_bbox | sparse_trails | yes | no | 41 |
| lapland_rural_sparse | osm_bbox | rural_roads | yes | no | 41 |
| helsinki_disrupted | osm_bbox | industrial_disrupted | yes | no | 42 |
| helsinki_archipelago | osm_bbox | island_or_partitioned | yes | no | 42 |
| london_industrial_corridor | osm_bbox | industrial_disrupted | yes | no | 41 |
| tampere_suburban | osm_bbox | suburban_low_density | yes | no | 33 |

## Notes

- Trace-only anchors parametrize `trace_reference_synthetic` maps; they are **not** downloadable OSM geometries.
- `n_valid_maps` counts rows in `map_space_saturation_features.csv` with matching `anchor_id`.
- Canonical declared total: **19** (not 20).

## Output

- `map_anchor_inventory_v1.csv`
