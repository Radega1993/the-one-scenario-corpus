# Manhattan Midtown Grid — map and route review

## Summary

**ManhattanMidtownGrid** (family `03_vehicles`) uses OSM drive network in EPSG:32618 (UTM zone 18N). The street grid is **regular and defendible** for vehicle-routing benchmarks: orthogonal avenues and cross-streets dominate the largest connected component.

## Geometry

| Item | Value |
|------|--------|
| CRS | EPSG:32618 |
| Bbox (lat/lon) | 40.748–40.766 N, 73.993–73.968 W |
| Source | OpenStreetMap `drive` extract |
| Sim alignment | Mirror Y, translate min corner to origin (The ONE convention) |

Diagonal appearance in **old** preview PNGs came from (1) drawing straight chords between `routeFile` waypoints and (2) legacy stop ordering (`x+y` sort). Current figures use **resolved Dijkstra paths** (solid) plus dotted stop reference.

## Route semantics

- **Before:** `A_bus.wkt`, `B_bus.wkt` (misleading label for grid vehicles).
- **After:** `A_vehicle_route.wkt` (dominant N–S axis), `B_vehicle_route.wkt` (dominant E–W).
- **Settings:** `corpus_v1` vehicles scenarios reference `routeFile`; paths updated on semantic rename.

## Recommendation

| Option | When |
|--------|------|
| **Keep current OSM extract** | Default — grid quality sufficient for paper; regenerate routes only. |
| **Full OSM re-bootstrap** | Only if bbox/filters must change; see `scenarios/maps/map_generation_specs/manhattan_midtown.yml` (spec only; not executed in this pass). |

## Paper wording

> Midtown Manhattan is modelled as a dense orthogonal drive network (EPSG:32618). Vehicle groups follow two fixed longitudinal routes defined as waypoint sequences on the graph; movement between stops uses shortest-path routing on the road layer.