# Kumpula Campus — map and route review

## Summary

**KumpulaCampus** (family `02_campus`) is a compact university area (OSM `all`, EPSG:3067). Corpus scenarios use **ShortestPathMapBasedMovement** without `GroupN.routeFile`.

## Shuttle asset

| File | Purpose |
|------|---------|
| `A_campus_shuttle.wkt` | Optional documentation / figure asset |
| Legacy `A_bus.wkt` | Removed after semantic regeneration |

**No `.settings` changes** — shuttle is not wired into the 540-scenario core by design.

## Route shape

Generator produces a **near-circular tour** on campus road nodes (angular ordering + graph nearest-neighbor), suitable for a low-frequency campus shuttle figure.

## Paper wording

> Campus scenarios rely on shortest-path movement on the pedestrian-capable campus graph without a fixed transit route in simulation settings; an optional shuttle waypoint file is provided for map figures only.