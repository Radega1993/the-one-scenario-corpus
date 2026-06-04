# NuuksioSparseTrails — validation report

Generated: 2026-05-28T18:15:32

## Blocking errors

- None

## Acceptable warnings

- Low trail coverage and partial map span are **methodological**, not defects
- Patrol route: WARNING — 1 stop(s) near border
- POI 50–120 m from trail: documented WARNING band

## Methodological decisions

- Single Nuuksio OSM extract for all `04_rural` scenarios.
- `A_bus.wkt` → `A_ranger_patrol.wkt` in settings; no urban bus semantics.
- R1 renamed to `R1_Rural_SparseSPMM` (SPMM, not RandomWaypoint).

- Settings audit FAIL count: 0