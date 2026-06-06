# Settings audit (corpus_v1)

Generated: 2026-06-05 12:40 UTC

- Scenarios audited: **540**
- Unique scenario bases: **45**
- Traffic profiles (TP): **12** distinct

## Families

| family | count |
|--------|------:|
| `01_urban` | 84 |
| `02_campus` | 72 |
| `03_vehicles` | 60 |
| `04_rural` | 144 |
| `05_disaster` | 108 |
| `06_social` | 72 |

## Map datasets

| map_dataset | count |
|-------------|------:|
| `unknown` | 396 |
| `HelsinkiMedium` | 84 |
| `Manhattan` | 60 |

## Movement models (per group entries)

| movement_model | count |
|----------------|------:|
| `G1:ShortestPathMapBasedMovement` | 324 |
| `G1:BusMovement` | 120 |
| `G2:WorkingDayMovement` | 108 |
| `G1:MapRouteMovement` | 72 |
| `G2:MapRouteMovement` | 48 |
| `G4:MapRouteMovement` | 48 |
| `G3:MapRouteMovement` | 36 |
| `G2:ShortestPathMapBasedMovement` | 36 |
| `G5:MapRouteMovement` | 36 |
| `G3:ShortestPathMapBasedMovement` | 24 |
| `G1:ClusterMovement` | 24 |
| `G2:ClusterMovement` | 24 |
| `G2:BusMovement` | 12 |
| `G6:MapRouteMovement` | 12 |
| `G7:MapRouteMovement` | 12 |

## Traffic profiles

| TP | count |
|----|------:|
| `TP01` | 45 |
| `TP02` | 45 |
| `TP03` | 45 |
| `TP04` | 45 |
| `TP05` | 45 |
| `TP06` | 45 |
| `TP07` | 45 |
| `TP08` | 45 |
| `TP09` | 45 |
| `TP10` | 45 |
| `TP11` | 45 |
| `TP12` | 45 |

## Notes

- Full per-scenario table: `data/settings_audit.csv`.
- Mobility and map parameters are unchanged from corpus_v1 inside each base; TP overlays Events* and Group.msgTtl.
- Most v2 scenarios reference **HelsinkiMedium** WKT under `data/HelsinkiMedium/`.
