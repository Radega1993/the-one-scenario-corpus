# Current simulation results review

Generated: 2026-05-24 10:28 UTC

- Scenarios in `output_metrics.csv`: **720**
- `delivery_ratio == 0`: **65**
- `delivery_ratio >= 0.95`: **20**
- `latency_mean` empty/zero: **67**
- `overhead_ratio > 100`: **93**
- `drop_ratio > 50`: **57**
- `total_encounters == 0`: **24**

> **Caveat:** metrics may reflect settings before `apply_corpus_v1_revision.py`; re-simulation required.

## Top problematic scenarios (P0 from diagnosis)

| scenario | delivery | overhead | flags |
|----------|----------:|---------:|-------|
| `U1_CBD_Commuting_HelsinkiMedium__TP04_FewLarge` | 0.1955 | 299.7429 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U1_CBD_Commuting_HelsinkiMedium__TP06_OneToMany` | 0.6144 | 177.2198 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U1_CBD_Commuting_HelsinkiMedium__TP08_HubTarget` | 0.3258 | 421.9684 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U1_CBD_Commuting_HelsinkiMedium__TP09_Bimodal` | 0.3044 | 245.0447 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U1_CBD_Commuting_HelsinkiMedium__TP10_Storm` | 0.0599 | 113.4743 | `EXTREME_OVERHEAD|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U1_CBD_Commuting_HelsinkiMedium__TP12_GroupToGroup` | 0.5358 | 231.2939 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U2_SparseSuburb_HelsinkiMedium__TP08_HubTarget` | 0.1443 | 107.8286 | `EXTREME_OVERHEAD|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiMedium__TP01_Baseline` | 0.1019 | 3960.3265 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiMedium__TP02_LowLoad` | 0.3158 | 4303.1 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiMedium__TP03_ManySmall` | 0.2817 | 1035.8698 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiMedium__TP04_FewLarge` | 0.0166 | 6861.3333 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiMedium__TP06_OneToMany` | 0.4979 | 901.2112 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiMedium__TP07_BurstWindow` | 0.1766 | 3228.0 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiMedium__TP08_HubTarget` | 0.0608 | 5016.1695 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiMedium__TP09_Bimodal` | 0.1557 | 2550.0444 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_UNDERUSED|MAP_TOO_LARGE` |

## TP profiles (mean delivery std across bases)

| TP | mean delivery | std delivery | mean overhead | mean drops | n |
|----|--------------:|-------------:|--------------:|-----------:|--:|
| `TP01` | 0.2929 | 0.2904 | 113.7 | 9.2 | 60 |
| `TP02` | 0.3168 | 0.3148 | 132.4 | 22.0 | 60 |
| `TP03` | 0.2830 | 0.2796 | 55.7 | 4.7 | 60 |
| `TP04` | 0.2097 | 0.2056 | 467.2 | 80.1 | 60 |
| `TP05` | 0.0275 | 0.0839 | 47.0 | 2.2 | 60 |
| `TP06` | 0.2994 | 0.2999 | 81.7 | 18.7 | 60 |
| `TP07` | 0.3815 | 0.3474 | 103.1 | 14.4 | 60 |
| `TP08` | 0.2558 | 0.2606 | 177.2 | 28.0 | 60 |
| `TP09` | 0.2352 | 0.2314 | 283.7 | 69.5 | 60 |
| `TP10` | 0.1000 | 0.1752 | 91.4 | 12.6 | 60 |
| `TP11` | 0.3198 | 0.3069 | 57.0 | 5.5 | 60 |
| `TP12` | 0.2807 | 0.3045 | 80.7 | 17.4 | 60 |

## Families (mean delivery)

| family | mean delivery | mean encounters | n |
|--------|--------------:|----------------:|--:|
| `02_campus` | 0.6262 | 1719 | 72 |
| `03_vehicles` | 0.5079 | 5156 | 60 |
| `01_urban` | 0.2958 | 2851 | 84 |
| `04_rural` | 0.2223 | 232 | 144 |
| `05_disaster` | 0.1847 | 2045 | 108 |
| `06_social` | 0.1827 | 2176 | 72 |
| `07_` | 0.0798 | 72 | 180 |

## Interpretation

- **TP04** shows highest drops/overhead — stress profile, not main benchmark.
- **TP05** often zero delivery with short TTL — diagnostic.
- **TP12** zero cross-group delivery is structural when partition is valid.
- **04_rural** R1/R11: zero contacts — configuration or control extremes.