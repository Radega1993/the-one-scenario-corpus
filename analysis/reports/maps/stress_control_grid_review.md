# Control Compact Grid — stress map review

## Summary

**ControlCompactGrid** (family `07_stress_controls`) is a **synthetic** 12×10 block grid (150 m spacing, local CRS). It is **outside the 540-scenario environmental core** and used only in `stress_controls/` (30 scenarios).

## Route semantics

| Legacy | Semantic |
|--------|----------|
| `A_bus.wkt` | `A_control_route.wkt` |

Single horizontal control route on the synthetic grid (no `routeFile` in stress `.settings`). Asset supports validation figures and package consistency.

## Variables

- Controlled topology — no geographic bias.
- Fixed `worldSize` from grid generator.
- Label figures as **synthetic control**, not OSM.

## Paper wording

> Protocol stress experiments use a synthetic rectangular grid map isolated from geographic extracts; optional control-route waypoints exist for asset validation only.
