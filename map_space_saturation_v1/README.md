# Map space saturation candidates (v1)

This directory contains *roads-only* candidate maps generated from the saturation spec.

## Output layout
- `batch_XXXX/`: per-stage candidate storage
- `previews/`: preview PNGs (one per map_id)
- `manifest_maps_all.csv`: global manifest

## Run parameters
- target_total: 2000
- seed: 42

## Notes
- This phase does not generate POIs, routes, or traffic profiles.

