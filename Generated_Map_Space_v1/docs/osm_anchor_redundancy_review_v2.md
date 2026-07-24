# OSM anchor redundancy review v2

**Anchors reviewed:** 17 (geographic OSM only; trace-only SMS anchors excluded).
**Phase decision:** keep all anchors unless severe overlap is documented below.
**No deletions in this phase.**

## Inventory

| anchor_id | archetype | bbox (S,W,N,E) | trace_support | decision |
|-----------|-----------|----------------|---------------|----------|
| `cambridge_haggle` | `dense_urban_irregular` | `52.198,0.108,52.212,0.132` | — | keep |
| `dieselnet_amherst` | `bus_route_urban_suburban` | `42.365,-72.545,42.395,-72.505` | umass_diesel_20080914 | keep |
| `helsinki_archipelago` | `island_or_partitioned` | `60.145,24.88,60.175,24.96` | — | keep |
| `helsinki_disrupted` | `industrial_disrupted` | `60.18,24.965,60.196,24.995` | — | keep |
| `helsinki_downtown` | `dense_urban_irregular` | `60.165,24.925,60.178,24.955` | — | keep |
| `kallio_community` | `compact_residential` | `60.179,24.938,60.189,24.957` | — | keep |
| `kumpula_campus` | `campus_compact` | `60.2025,24.958,60.2115,24.978` | — | keep |
| `lapland_rural_sparse` | `rural_roads` | `66.48,25.68,66.52,25.78` | — | keep |
| `london_industrial_corridor` | `industrial_disrupted` | `51.505,-0.04,51.525,0.01` | — | keep |
| `manhattan_midtown` | `urban_grid` | `40.748,-73.993,40.766,-73.968` | — | keep |
| `mit_campus_reality` | `campus_compact` | `42.355,-71.095,42.365,-71.085` | dartmouth_wardriving_20060602 | keep |
| `nuuksio_sparse_trails` | `sparse_trails` | `60.31,24.49,60.335,24.535` | — | keep |
| `rio_centro_buses` | `bus_route_urban_suburban` | `-22.92,-43.26,-22.88,-43.2` | coppe_ufrj_riobuses_20180319 | keep (GPS-justified) |
| `roma_centro` | `dense_urban_irregular` | `41.88,12.47,41.91,12.51` | roma_taxi_20140717 | keep (GPS-justified) |
| `sf_cabspotting_downtown` | `dense_urban_irregular` | `37.775,-122.425,37.795,-122.395` | epfl_mobility_20090224 | keep |
| `sf_mission_corridor` | `corridor_linear` | `37.748,-122.43,37.768,-122.4` | — | keep |
| `tampere_suburban` | `suburban_low_density` | `61.46,23.72,61.49,23.78` | — | keep |

## Bbox overlaps (IoU > 0)

| IoU | A | B | archetypes | assessment |
|----:|---|---|------------|------------|
| 0.120 | `helsinki_downtown` | `helsinki_archipelago` | dense_urban_irregular / island_or_partitioned | minor — keep |

## GPS-justified anchors

- `roma_centro`: justified by `roma_taxi_20140717` GPS summary → dense urban irregular.
- `rio_centro_buses`: justified by `coppe_ufrj_riobuses_20180319` GPS summary → bus route urban/suburban.

## Conclusion

No severe bbox redundancy. **Keep all 17 OSM anchors** for Phase B completion.

