# Route usage by scenario

Generated: 2026-05-28 15:37 UTC

## Summary

- Rows with routeFile: **208**
- WorkingDayMovement rows: **117**
- ShortestPathMapBasedMovement rows: **0**
- ClusterMovement rows: **0**
- Scenarios relying mainly on roads.wkt (SPMM, no route): **0** distinct scenario names (approx.)

## Bus / MapRoute carriers

Scenarios using `BusMovement` or `MapRouteMovement` reference `GroupN.routeFile` (`*_bus.wkt`). Movement between stops uses the road graph (Dijkstra), not the straight chord in preview figures.

## ClusterMovement

Cluster scenarios use `roads.wkt` for map bounds and optional cluster areas; community structure is parameter-driven, not from bus routes.

## Missing files

- None detected.
