# NuuksioSparseTrails — rural settings audit

Generated: 2026-05-28T18:15:32

- Files audited: 156
- FAIL: 0
- Legacy A_bus fixes: 0
- R1 renamed: 0

## Map and worldSize

All map-based rural scenarios: `data/NuuksioSparseTrails/roads.wkt`, `worldSize = 2848, 2945`.

## R4 park rangers

`Group.routeFile` unified to `A_ranger_patrol.wkt` (file `A_bus.wkt` absent on disk).

## R1 rename

`R1_Rural_RandomWaypoint` → `R1_Rural_SparseSPMM`: reflects ShortestPathMapBasedMovement, not RandomWaypoint.

## Historical analysis CSVs

Manifests updated; `output_metrics.csv` and other analysis artifacts may still reference the old R1 name until regenerated.
