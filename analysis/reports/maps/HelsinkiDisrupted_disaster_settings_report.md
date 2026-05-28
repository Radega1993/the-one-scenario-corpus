# HelsinkiDisrupted — disaster settings audit

Generated: 2026-05-28T18:21:19

- Files audited: 117
- FAIL: 0
- D5 Group1 → SPMM fixes: 13
- Comment fixes: 0

## D5 UAV mule

Group1 (civilians/responders): `ShortestPathMapBasedMovement` on `roads.wkt` graph. Group2 (UAV): `MapRouteMovement` on `A_emergency_route.wkt`.

## Route assets

- `A_emergency_route.wkt` — emergency/UAV response path
- `B_mule_route.wkt` — mule/backbone (figure asset; D2 uses SPMM mule without routeFile)

