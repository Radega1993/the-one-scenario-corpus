# map_generation_error_analysis_v1.md

## Totals
- total_candidates: 2000
- FAIL_BUILD_OSM: 20
- FAIL_BUILD_SYNTHETIC_DEGENERATE: 103
- FAIL_DOWNLOAD_TRANSIENT: 406
- OK: 1405
- SKIPPED_EXISTING_OK: 66

## Failures by anchor_id
- (none): 103
- manhattan_midtown: 35
- tampere_suburban: 35
- dieselnet_amherst: 31
- helsinki_downtown: 28
- cambridge_haggle: 27
- helsinki_archipelago: 27
- helsinki_disrupted: 27
- kallio_community: 27
- kumpula_campus: 27
- lapland_rural_sparse: 27
- london_industrial_corridor: 27
- mit_campus_reality: 27
- nuuksio_sparse_trails: 27
- sf_cabspotting_downtown: 27
- sf_mission_corridor: 27

## Failures by window_size_m
- 1000.0: 124
- 2500.0: 108
- 1500.0: 68
- 5000.0: 64
- 500.0: 62

## Failures by network_type
- drive: 237
- all: 189
- synthetic: 103

## Interpretation
- `FAIL_DOWNLOAD_TRANSIENT`: Overpass/network; retry with `--acquire-osm --retry-transient`.
- `FAIL_DOWNLOAD_PERMANENT`: empty bbox / no OSM network; do not retry.
- `FAIL_BUILD_SYNTHETIC_DEGENERATE`: generator produced insufficient graph; check `synthetic_validation` in metadata.
- `FAIL_BUILD_OSM`: cached graph could not be converted to WKT.

