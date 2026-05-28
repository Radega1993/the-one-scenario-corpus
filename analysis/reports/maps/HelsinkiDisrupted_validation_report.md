# HelsinkiDisrupted — validation report

Generated: 2026-05-28T18:21:19

## Blocking errors

- None

## Acceptable warnings

- Low delivery / partition in D2 is **methodological**
- Route origin/border WARNING documented
- POI 40–100 m from road: documented WARNING band

## Methodological decisions

- Single Kalasatama OSM extract for all `05_disaster` scenarios.
- D5 Group1: MapRouteMovement+roads.wkt → ShortestPathMapBasedMovement.
- `A_emergency_route` / `B_mule_route` (not legacy bus names).

- Settings audit FAIL count: 0
- Route A_emergency_route.wkt: WARNING — 1 stop(s) near border
- Route B_mule_route.wkt: WARNING — 1 stop(s) near border
