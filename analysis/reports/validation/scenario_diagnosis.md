# Scenario diagnosis (corpus_v2)

- Scenarios: **720**
- With any flag: **392**
- Priority P0: **181**
- Thresholds: `realism_thresholds.yaml`

## Flag counts

| flag | count |
|------|------:|
| `TP_NOT_DIFFERENTIATING` | 216 |
| `EXTREME_OVERHEAD` | 92 |
| `ZERO_DELIVERY` | 86 |
| `MAP_UNDERUSED` | 84 |
| `MAP_TOO_LARGE` | 84 |
| `EXTREME_DROPS` | 53 |
| `ZERO_CONTACTS` | 24 |
| `SATURATED_DELIVERY` | 20 |
| `STRUCTURAL_PARTITION_VALID` | 9 |

## Top P0 examples (delivery=0, non-structural)

| scenario | delivery | overhead | flags |
|----------|----------:|---------:|-------|
| `U4_CongestionHotspot_HelsinkiMedium__TP05_CriticalTTL` | 0.0 | nan | `ZERO_DELIVERY|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP05_CriticalTTL` | 0.0 | nan | `ZERO_DELIVERY|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `R10_TinyRange_5m__TP02_LowLoad` | 0.0 | nan | `ZERO_DELIVERY|TP_NOT_DIFFERENTIATING` |
| `R10_TinyRange_5m__TP04_FewLarge` | 0.0 | nan | `ZERO_DELIVERY|TP_NOT_DIFFERENTIATING` |
| `R10_TinyRange_5m__TP05_CriticalTTL` | 0.0 | nan | `ZERO_DELIVERY|TP_NOT_DIFFERENTIATING` |
| `R11_SpeedExtremeLow__TP01_Baseline` | 0.0 | nan | `ZERO_DELIVERY|ZERO_CONTACTS|TP_NOT_DIFFERENTIATING` |
| `R11_SpeedExtremeLow__TP02_LowLoad` | 0.0 | nan | `ZERO_DELIVERY|ZERO_CONTACTS|TP_NOT_DIFFERENTIATING` |
| `R11_SpeedExtremeLow__TP03_ManySmall` | 0.0 | nan | `ZERO_DELIVERY|ZERO_CONTACTS|TP_NOT_DIFFERENTIATING` |
| `R11_SpeedExtremeLow__TP04_FewLarge` | 0.0 | nan | `ZERO_DELIVERY|ZERO_CONTACTS|TP_NOT_DIFFERENTIATING` |
| `R11_SpeedExtremeLow__TP05_CriticalTTL` | 0.0 | nan | `ZERO_DELIVERY|ZERO_CONTACTS|TP_NOT_DIFFERENTIATING` |

## By family (P0 count)

| family | P0 |
|--------|---:|
| `04_rural` | 45 |
| `05_disaster` | 36 |
| `01_urban` | 33 |
| `07_traffic` | 28 |
| `02_campus` | 16 |
| `06_social` | 13 |
| `03_vehicles` | 10 |

## Notes

- `STRUCTURAL_PARTITION_VALID` marks intentional zero delivery (e.g. TP12 cross-group).
- `MAP_UNDERUSED` uses `coverage_world_ratio` < threshold; WDM on large worlds often ~8–10%.
- Full table: `data/scenario_diagnosis.csv`.
