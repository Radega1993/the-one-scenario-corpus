# ManhattanMidtownGrid — re-simulation plan

Generated: 2026-05-28T18:06:11

## Recommendation

- **Re-run 03_vehicles simulations** if vehicle route WKT or POI files changed before publishing new KPIs.
- **Settings path fix** (`A_bus` → `A_vehicle_route`) corrects broken `Group.routeFile` for WDM groups; MapRouteMovement (V1/V2) primarily uses `Group1.routeFile`.

## Scope

- Affected settings files: **65** (5 base + 60 TP variants).
- Traffic Profile blocks (`Events*`) not modified.

## Priority

1. V3 (dual bus carriers on A/B routes)
2. V4, V5 (WDM + POI + vehicle route)
3. V1, V2 (taxi MapRouteMovement)
