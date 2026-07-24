# Map generation v2 dry-run plan

- config_hash: `2150301fb651c754`
- seed: `42`
- candidates: **90** (enabled 90)
- critical issues: **0**

## Counts by source_type

- `osm`: 40
- `synthetic`: 33
- `trace_reference_synthetic`: 17

## Counts by archetype

- `bus_route_urban_suburban`: 8
- `campus_compact`: 9
- `clustered_communities`: 9
- `compact_residential`: 3
- `conference_event_compact`: 5
- `corridor_linear`: 6
- `dense_urban_irregular`: 12
- `hub_and_spoke`: 2
- `industrial_disrupted`: 10
- `island_or_partitioned`: 7
- `radial_city`: 2
- `rural_roads`: 6
- `sparse_trails`: 4
- `suburban_low_density`: 2
- `urban_grid`: 5

## Issues

- none

## Provenance samples

### v2_osm_cambridge_haggle_exact_500m_0m_seed
```json
{
  "anchor_id": "cambridge_haggle",
  "archetype": "dense_urban_irregular",
  "builder": "osm",
  "config_hash": "2150301fb651c754",
  "input_reference": "osm_anchor:cambridge_haggle",
  "map_id": "v2_osm_cambridge_haggle_exact_500m_0m_seed",
  "osm_query": {
    "bbox": null,
    "network_type": "all",
    "offset_m": 0,
    "place": null,
    "variant_type": "exact",
    "window_size_m": 500
  },
  "seed": 3242687280,
  "source_type": "osm",
  "trace_support": []
}
```

### v2_osm_dieselnet_amherst_exact_500m_0m_seed
```json
{
  "anchor_id": "dieselnet_amherst",
  "archetype": "bus_route_urban_suburban",
  "builder": "osm",
  "config_hash": "2150301fb651c754",
  "input_reference": "osm_anchor:dieselnet_amherst",
  "map_id": "v2_osm_dieselnet_amherst_exact_500m_0m_seed",
  "osm_query": {
    "bbox": null,
    "network_type": "drive",
    "offset_m": 0,
    "place": null,
    "variant_type": "exact",
    "window_size_m": 500
  },
  "seed": 1963491001,
  "source_type": "osm",
  "trace_support": [
    "umass_diesel_20080914"
  ]
}
```

### v2_osm_helsinki_archipelago_exact_500m_0m_seed
```json
{
  "anchor_id": "helsinki_archipelago",
  "archetype": "island_or_partitioned",
  "builder": "osm",
  "config_hash": "2150301fb651c754",
  "input_reference": "osm_anchor:helsinki_archipelago",
  "map_id": "v2_osm_helsinki_archipelago_exact_500m_0m_seed",
  "osm_query": {
    "bbox": null,
    "network_type": "all",
    "offset_m": 0,
    "place": null,
    "variant_type": "exact",
    "window_size_m": 500
  },
  "seed": 587897237,
  "source_type": "osm",
  "trace_support": []
}
```

## Trace activation (this plan)

- parameterize → TRS maps: `haggle_one_cambridge_city_complete`, `oviedo_asturies_er_20160808`, `st_andrews_locshare_20111012`, `st_andrews_sassy_20110603`, `upmc_rollernet_20090202`
- osm_anchor_support attached: `coppe_ufrj_riobuses_20180319`, `dartmouth_wardriving_20060602`, `epfl_mobility_20090224`, `roma_taxi_20140717`, `umass_diesel_20080914`

evidence_only / future_candidate / unsupported traces do not appear as enabled map rows.

