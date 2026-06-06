# Current simulation results review

Generated: 2026-06-05 12:40 UTC

- Scenarios in `output_metrics.csv`: **600**
- `delivery_ratio == 0`: **4**
- `delivery_ratio >= 0.95`: **105**
- `latency_mean` empty/zero: **4**
- `overhead_ratio > 100`: **182**
- `drop_ratio > 50`: **157**
- `total_encounters == 0`: **0**

> **Caveat:** metrics may reflect settings before `apply_corpus_v1_revision.py`; re-simulation required.

## Top problematic scenarios (P0 from diagnosis)

| scenario | delivery | overhead | flags |
|----------|----------:|---------:|-------|
| `U1_CBD_Commuting_HelsinkiDowntown__TP04_FewLarge` | 0.3296 | 697.8305 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_TOO_LARGE` |
| `U1_CBD_Commuting_HelsinkiDowntown__TP05_CriticalTTL` | 0.0081 | 102.25 | `EXTREME_OVERHEAD|MAP_TOO_LARGE` |
| `U1_CBD_Commuting_HelsinkiDowntown__TP06_OneToMany` | 0.6495 | 106.1413 | `EXTREME_OVERHEAD|MAP_TOO_LARGE` |
| `U1_CBD_Commuting_HelsinkiDowntown__TP08_HubTarget` | 0.3876 | 359.0957 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_TOO_LARGE` |
| `U1_CBD_Commuting_HelsinkiDowntown__TP09_Bimodal` | 0.3588 | 480.7251 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_TOO_LARGE` |
| `U1_CBD_Commuting_HelsinkiDowntown__TP10_Storm` | 0.0899 | 247.5018 | `EXTREME_OVERHEAD|MAP_TOO_LARGE` |
| `U2_SparseUrban_HelsinkiDowntown__TP04_FewLarge` | 0.2376 | 165.6279 | `EXTREME_OVERHEAD|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U2_SparseUrban_HelsinkiDowntown__TP09_Bimodal` | 0.2674 | 118.6753 | `EXTREME_OVERHEAD|MAP_UNDERUSED|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiDowntown__TP01_Baseline` | 0.1143 | 6331.0727 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiDowntown__TP02_LowLoad` | 0.4316 | 8144.4634 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiDowntown__TP03_ManySmall` | 0.3193 | 896.8057 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiDowntown__TP04_FewLarge` | 0.0989 | 2113.6667 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiDowntown__TP05_CriticalTTL` | 0.0042 | 342.5 | `EXTREME_OVERHEAD|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiDowntown__TP06_OneToMany` | 0.5619 | 1084.011 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_TOO_LARGE` |
| `U3_MicroMobility_HelsinkiDowntown__TP07_BurstWindow` | 0.2283 | 3464.9643 | `EXTREME_OVERHEAD|EXTREME_DROPS|MAP_TOO_LARGE` |

## TP profiles (mean delivery std across bases)

| TP | mean delivery | std delivery | mean overhead | mean drops | n |
|----|--------------:|-------------:|--------------:|-----------:|--:|
| `TP01` | 0.7241 | 0.2609 | 235.8 | 59.7 | 50 |
| `TP02` | 0.7543 | 0.2449 | 216.9 | 71.5 | 50 |
| `TP03` | 0.7309 | 0.2572 | 68.7 | 7.1 | 50 |
| `TP04` | 0.5159 | 0.2313 | 1022.0 | 396.4 | 50 |
| `TP05` | 0.0852 | 0.1340 | 52.8 | 4.1 | 50 |
| `TP06` | 0.7742 | 0.2017 | 134.8 | 66.7 | 50 |
| `TP07` | 0.8240 | 0.2491 | 203.7 | 97.1 | 50 |
| `TP08` | 0.6456 | 0.2348 | 454.4 | 238.4 | 50 |
| `TP09` | 0.5848 | 0.2196 | 679.8 | 341.7 | 50 |
| `TP10` | 0.3977 | 0.2854 | 132.2 | 46.6 | 50 |
| `TP11` | 0.7599 | 0.2002 | 111.3 | 48.0 | 50 |
| `TP12` | 0.7678 | 0.2488 | 151.5 | 66.9 | 50 |

## Families (mean delivery)

| family | mean delivery | mean encounters | n |
|--------|--------------:|----------------:|--:|
| `02_campus` | 0.7126 | 2702 | 72 |
| `06_social` | 0.7109 | 13595 | 72 |
| `05_disaster` | 0.6987 | 7423 | 108 |
| `04_rural` | 0.6649 | 4056 | 144 |
| `03_vehicles` | 0.6410 | 4738 | 60 |
| `01_urban` | 0.3275 | 3300 | 84 |

## Interpretation

- **TP04** shows highest drops/overhead — stress profile, not main benchmark.
- **TP05** often zero delivery with short TTL — diagnostic.
- **TP12** zero cross-group delivery is structural when partition is valid.
- **04_rural** R1/R11: zero contacts — configuration or control extremes.
