# ManhattanMidtownGrid — vehicle settings audit

Generated: 2026-05-28T18:06:11

- Files audited: 65
- FAIL: 0
- Legacy A_bus path fixes: 52

## Legacy Group.routeFile

`A_bus.wkt` does not exist on disk. Replaced with `A_vehicle_route.wkt` (and `B_bus` → `B_vehicle_route`) for WDM scenarios with `busControlSystemNr = -1`. V1/V2 MapRouteMovement uses `Group1.routeFile` only.

## Scenarios

| ID | Model | Routes | POI |
|----|-------|--------|-----|
| V1 | MapRouteMovement (taxis) | Group1 → A_vehicle | No |
| V2 | MapRouteMovement (taxis) | Group1 → A_vehicle | No |
| V3 | BusMovement | A + B vehicle | No |
| V4 | WDM + bus | A_vehicle | Yes |
| V5 | WDM + bus | A_vehicle | Yes |

