# HelsinkiDowntown — urban settings audit

Generated: 2026-05-28T17:49:24

- Files audited: 91
- FAIL: 0
- U2 renamed files: 0

## routeFile on WorkingDayMovement

Urban scenarios use `Group.busControlSystemNr = -1` so pedestrians use the bus system. `Group.routeFile` and `Group2.routeFile` must point at `A_bus.wkt` so `getBusStops()` is initialized (otherwise NPE). This is required by The ONE, not an optional bus overlay.

## U2 rename

`U2_SparseSuburb_HelsinkiDowntown` → `U2_SparseUrban_HelsinkiDowntown`: low-density urban scenario on the same downtown map (fewer hosts/offices), not a geographic suburb.
