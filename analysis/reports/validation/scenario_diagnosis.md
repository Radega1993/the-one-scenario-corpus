# Scenario diagnosis (corpus_v1)

- Scenarios: **540**
- With any flag: **371**
- Priority P0: **175**
- Thresholds: `realism_thresholds.yaml`

## Flag counts

| flag | count |
|------|------:|
| `EXTREME_OVERHEAD` | 171 |
| `EXTREME_DROPS` | 148 |
| `MAP_TOO_LARGE` | 144 |
| `MAP_UNDERUSED` | 116 |
| `SATURATED_DELIVERY` | 90 |
| `ZERO_DELIVERY` | 2 |
| `STRUCTURAL_PARTITION_VALID` | 2 |

## Top P0 examples (delivery=0, non-structural)

| scenario | delivery | overhead | flags |
|----------|----------:|---------:|-------|
| `U5_WorkdayShort_HelsinkiDowntown__TP05_CriticalTTL` | 0.0 | nan | `ZERO_DELIVERY|MAP_TOO_LARGE` |
| `R7_SparseTinyBuffer__TP04_FewLarge` | 0.0 | nan | `ZERO_DELIVERY` |

## By family (P0 count)

| family | P0 |
|--------|---:|
| `06_social` | 45 |
| `01_urban` | 38 |
| `05_disaster` | 34 |
| `04_rural` | 29 |
| `02_campus` | 18 |
| `03_vehicles` | 11 |

## Notes

- `STRUCTURAL_PARTITION_VALID` marks intentional zero delivery (e.g. TP12 cross-group).
- `MAP_UNDERUSED` uses `coverage_road_ratio` when available (else world); see `realism_thresholds.yaml`.
- Full table: `data/scenario_diagnosis.csv`.
