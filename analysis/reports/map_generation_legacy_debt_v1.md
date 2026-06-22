# Map generation technical debt (saturation v1 refactor)

## Legacy dependency removed from main pipeline

`generate_map_space_saturation_v1.py` no longer imports `_legacy/map_space_v1_phase1/generate_map_space_v1.py`.

## Functions migrated to active modules

| Legacy function | New module |
|-----------------|------------|
| `_download_osm_graph`, `graph_from_bbox_compat`, `_graph_to_edges` | `map_space_osm_builder.py` |
| `generate_synthetic_map`, `GENERATORS` | `map_space_synthetic_builder.py` + `map_space_synthetic.py` |
| `render_preview` | `map_space_preview.py` |

## Remaining legacy artifacts (read-only reference)

- `scenarios/setup/_legacy/map_space_v1_phase1/` — kept for historical comparison; not used by saturation v1 pipeline.

## Not yet ported

- `iter_all_candidates` / anchor YAML loader from legacy v1 design space (saturation v1 uses embedded anchors in design-space YAML).
- GeoJSON export in OSM queue (`raw_geojson_path` column reserved).
