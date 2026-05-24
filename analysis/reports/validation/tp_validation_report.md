# Traffic Profiles v1.0 — validation report

Generated: 2026-05-20 12:44 UTC

## Corpus integrity

- Settings files scanned: **720**
- Manifest rows: **720**
- Settings vs generator spec: **720/720 OK**
- Window table rows: **720**

## Simulation metrics coverage

- Rows in `output_metrics.csv`: **720**
- Scenarios with `total_encounters > 0`: **696**
- Disconnected control (`total_encounters = 0`): **24**

## Per-profile aggregates (global view)

| TP | n | mean delivery | std delivery | mean latency (s) | mean drop |
|---|---:|---:|---:|---:|---:|
| TP01 | 60 | 0.2681 | 0.2947 | 11241.2559 | 9.1738 |
| TP02 | 60 | 0.295 | 0.3195 | 12276.024 | 22.0115 |
| TP03 | 60 | 0.2612 | 0.2844 | 11786.8979 | 4.6673 |
| TP04 | 60 | 0.1407 | 0.1581 | 11779.5763 | 97.3827 |
| TP05 | 60 | 0.0262 | 0.083 | 110.6032 | 2.127 |
| TP06 | 60 | 0.2864 | 0.3027 | 10810.6376 | 16.6726 |
| TP07 | 60 | 0.3418 | 0.3489 | 13576.0822 | 14.3641 |
| TP08 | 60 | 0.2366 | 0.2619 | 11719.853 | 27.4986 |
| TP09 | 60 | 0.2137 | 0.2349 | 11068.5046 | 64.1202 |
| TP10 | 60 | 0.0973 | 0.1748 | 1662.1134 | 12.3885 |
| TP11 | 60 | 0.3037 | 0.3068 | 11242.9786 | 5.4493 |
| TP12 | 60 | 0.2576 | 0.3061 | 12052.638 | 17.5174 |

## Per-profile aggregates (connected only, `total_encounters > 0`)

| TP | n | mean delivery | std delivery | mean latency (s) | mean drop |
|---|---:|---:|---:|---:|---:|
| TP01 | 58 | 0.2773 | 0.2954 | 11241.2559 | 9.4901 |
| TP02 | 58 | 0.3052 | 0.3201 | 12276.024 | 22.7706 |
| TP03 | 58 | 0.2703 | 0.285 | 11786.8979 | 4.8311 |
| TP04 | 58 | 0.1455 | 0.1586 | 11779.5763 | 100.7407 |
| TP05 | 58 | 0.0271 | 0.0842 | 110.6032 | 2.166 |
| TP06 | 58 | 0.2962 | 0.303 | 10810.6376 | 17.2448 |
| TP07 | 58 | 0.3536 | 0.349 | 13576.0822 | 14.8595 |
| TP08 | 58 | 0.2447 | 0.2626 | 11719.853 | 28.4468 |
| TP09 | 58 | 0.2211 | 0.2355 | 11068.5046 | 66.3312 |
| TP10 | 58 | 0.1007 | 0.1768 | 1662.1134 | 12.7841 |
| TP11 | 58 | 0.3141 | 0.3068 | 11242.9786 | 5.6372 |
| TP12 | 58 | 0.2665 | 0.3075 | 12052.638 | 18.1214 |

## Traffic-profile separation by base scenario

- Mean delivery spread across 12 TPs (max−min per base): **0.3640**
- Bases with spread < 0.05 (weak TP differentiation): **16** / 60

Full table: `data/tp_validation_by_base.csv`.

## Methodology pointers

- Closure document: `scenarios/internal/17-benchmark_methodology_closure.md`
- Profile rationale: `scenarios/internal/16-traffic_profiles_v1_justification.md`
- Generator (source of truth): `scenarios/analysis/generate_corpus_v2_traffic.py`
