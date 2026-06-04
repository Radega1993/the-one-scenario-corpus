# Settings audit (corpus_v1)

Generated: 2026-05-31 15:40 UTC

- Scenarios audited: **48**
- Unique scenario bases: **4**
- Traffic profiles (TP): **12** distinct

## Families

| family | count |
|--------|------:|
| `04_rural` | 12 |
| `05_disaster` | 12 |
| `06_social` | 24 |

## Map datasets

| map_dataset | count |
|-------------|------:|
| `unknown` | 48 |

## Movement models (per group entries)

| movement_model | count |
|----------------|------:|
| `G4:MapRouteMovement` | 48 |
| `G5:MapRouteMovement` | 36 |
| `G1:MapRouteMovement` | 36 |
| `G2:MapRouteMovement` | 36 |
| `G3:MapRouteMovement` | 36 |
| `G1:ShortestPathMapBasedMovement` | 12 |
| `G2:ShortestPathMapBasedMovement` | 12 |
| `G3:ShortestPathMapBasedMovement` | 12 |
| `G6:MapRouteMovement` | 12 |
| `G7:MapRouteMovement` | 12 |
| `G8:MapRouteMovement` | 12 |
| `G9:MapRouteMovement` | 12 |
| `G10:MapRouteMovement` | 12 |
| `G11:MapRouteMovement` | 12 |
| `G12:MapRouteMovement` | 12 |

## Traffic profiles

| TP | count |
|----|------:|
| `TP01` | 4 |
| `TP02` | 4 |
| `TP03` | 4 |
| `TP04` | 4 |
| `TP05` | 4 |
| `TP06` | 4 |
| `TP07` | 4 |
| `TP08` | 4 |
| `TP09` | 4 |
| `TP10` | 4 |
| `TP11` | 4 |
| `TP12` | 4 |

## Notes

- Full per-scenario table: `data/settings_audit.csv`.
- Mobility and map parameters are unchanged from corpus_v1 inside each base; TP overlays Events* and Group.msgTtl.
- Most v2 scenarios reference **HelsinkiMedium** WKT under `data/HelsinkiMedium/`.