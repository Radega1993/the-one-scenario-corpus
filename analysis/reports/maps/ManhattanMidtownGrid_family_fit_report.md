# ManhattanMidtownGrid — family fit (03_vehicles)

Generated as part of vehicle map finalization.

## Why this map fits 03_vehicles

| Criterion | ManhattanMidtownGrid |
|-----------|-------------------|
| Geographic scale | OSM Midtown Manhattan grid (EPSG:32618), sim window **2500 × 2366 m** |
| Network | Regular street grid — ideal for taxis, bus carriers, car-ownership contrasts |
| Coverage | ~12% road length / worldSize (large window, sparse relative to bbox) |
| vs campus | No SPMM pedestrian focus; vehicle speeds and route-following |
| vs urban | Helsinki uses integrated bus WDM; Manhattan isolates **vehicle mobility** levers |
| vs rural | Dense grid vs trail networks |

## Visual rotation (UTM → sim frame)

The sim transform (mirror Y + translate from WKT metadata) can **visually tilt** the Manhattan grid in figures. **Street topology is preserved** — acceptable for paper figures.

## Scenario mapping (V1–V5)

| Scenario | Movement | Routes | POI | Role |
|----------|----------|--------|-----|------|
| V1 TaxiLow | MapRouteMovement | Group1 → A_vehicle | No | Few taxis, high speed |
| V2 TaxiHigh | MapRouteMovement | Group1 → A_vehicle | No | Many taxis |
| V3 BusCarriers | BusMovement | A + B vehicle routes | No | Two carrier groups |
| V4 CarOwnership 0% | WDM + bus (`busControlSystemNr = -1`) | A_vehicle | Yes | No private cars |
| V5 CarOwnership 100% | WDM + bus | A_vehicle | Yes | Full car ownership |

## Route semantics

- **A_vehicle_route.wkt** — longitudinal axis (N–S dominant on grid).
- **B_vehicle_route.wkt** — transversal axis (E–W dominant).
- Legacy **`A_bus.wkt`** removed from disk; settings unified to `A_vehicle_route.wkt`.

## Difference from other families

- **01_urban (HelsinkiDowntown):** pedestrian WDM, semantic bus lines A/B/C, smaller effective density.
- **02_campus (Kumpula):** SPMM, optional shuttle figure only.
- **04_rural (Nuuksio):** ranger patrol on trails, not grid taxis.