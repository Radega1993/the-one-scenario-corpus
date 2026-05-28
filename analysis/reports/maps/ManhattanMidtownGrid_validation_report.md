# ManhattanMidtownGrid — validation report

Generated: 2026-05-28T18:06:11

## Blocking errors

- None

## Acceptable warnings

- POI offices/meetings >50 m: see poi_report (urban thresholds 30/75 m)
- Route A may show WARNING (origin frame / coverage); B should PASS
- Grid visual rotation in figures does not affect simulation topology

## Methodological decisions

- Single Midtown OSM extract for all `03_vehicles` scenarios.
- `Group.routeFile` legacy `A_bus.wkt` → `A_vehicle_route.wkt` (file absent on disk).
- Header comments `HelsinkiMedium` → `ManhattanMidtownGrid` (comments only).

- Settings audit FAIL count: 0
