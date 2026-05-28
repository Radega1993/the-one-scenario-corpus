# Settings audit (corpus_v1)

Generated: 2026-05-20 10:58 UTC

- Scenarios audited: **720**
- Unique scenario bases: **60**
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
| `07_stress_controls` | 180 |

## Map datasets

| map_dataset | count |
|-------------|------:|
| `unknown` | 552 |
| `HelsinkiMedium` | 168 |

## Movement models (per group entries)

| movement_model | count |
|----------------|------:|
| `G1:RandomWaypoint` | 468 |
| `G1:BusMovement` | 120 |
| `G2:WorkingDayMovement` | 108 |
| `G1:ClusterMovement` | 72 |
| `G2:ClusterMovement` | 72 |
| `G1:MapRouteMovement` | 48 |
| `G3:ClusterMovement` | 48 |
| `G2:RandomWaypoint` | 24 |
| `G4:ClusterMovement` | 24 |
| `G1:LinearMovement` | 12 |
| `G2:BusMovement` | 12 |
| `G4:RandomWaypoint` | 12 |
| `G3:RandomWaypoint` | 12 |
| `G2:MapRouteMovement` | 12 |
| `G5:ClusterMovement` | 12 |

## Traffic profiles

| TP | count |
|----|------:|
| `TP01` | 60 |
| `TP02` | 60 |
| `TP03` | 60 |
| `TP04` | 60 |
| `TP05` | 60 |
| `TP06` | 60 |
| `TP07` | 60 |
| `TP08` | 60 |
| `TP09` | 60 |
| `TP10` | 60 |
| `TP11` | 60 |
| `TP12` | 60 |

## Notes

- Full per-scenario table: `data/settings_audit.csv`.
- Mobility and map parameters are unchanged from corpus_v1 inside each base; TP overlays Events* and Group.msgTtl.
- Most v2 scenarios reference **HelsinkiMedium** WKT under `data/HelsinkiMedium/`.
