# Traffic Profiles v1.0 — validation report

Generated: 2026-05-27 09:42 UTC

## Corpus integrity

- Settings files scanned: **570**
- Manifest rows: **570**
- Settings vs generator spec: **568/570 OK**
- Window table rows: **570**

## Simulation metrics coverage

- Rows in `output_metrics.csv`: **720**
- Scenarios with `total_encounters > 0`: **672**
- Disconnected control (`total_encounters = 0`): **24**

## Settings mismatches (action required)

**2** files differ from `lib/traffic_profile_generator.py`.

| scenario | mismatches |
|---|---|
| `U4_CongestionHotspot_HelsinkiDowntown__TP05_CriticalTTL` | Group.msgTtl: got='15' exp='5'; Group*.msgTtl inconsistent: 15 != 5 |
| `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP05_CriticalTTL` | Group.msgTtl: got='15' exp='5'; Group*.msgTtl inconsistent: 15 != 5 |

## Per-profile aggregates (global view)

| TP | n | mean delivery | std delivery | mean latency (s) | mean drop |
|---|---:|---:|---:|---:|---:|
| TP01 | 60 | 0.2929 | 0.2879 | 11645.0267 | 9.1738 |
| TP02 | 60 | 0.3168 | 0.3121 | 12452.3599 | 22.0115 |
| TP03 | 60 | 0.2826 | 0.275 | 11874.7824 | 4.5896 |
| TP04 | 60 | 0.2097 | 0.2039 | 11907.7129 | 80.1263 |
| TP05 | 60 | 0.0275 | 0.0832 | 135.7232 | 2.2089 |
| TP06 | 60 | 0.2994 | 0.2974 | 10794.4054 | 18.7401 |
| TP07 | 60 | 0.3815 | 0.3445 | 13979.1743 | 14.3641 |
| TP08 | 60 | 0.2558 | 0.2584 | 11901.2166 | 28.049 |
| TP09 | 60 | 0.2352 | 0.2295 | 11397.8154 | 69.5018 |
| TP10 | 60 | 0.1 | 0.1738 | 1684.5441 | 12.6451 |
| TP11 | 60 | 0.319 | 0.3018 | 11256.6657 | 5.4493 |
| TP12 | 60 | 0.2807 | 0.3019 | 12326.3516 | 17.3613 |

## Per-profile aggregates (connected only, `total_encounters > 0`)

| TP | n | mean delivery | std delivery | mean latency (s) | mean drop |
|---|---:|---:|---:|---:|---:|
| TP01 | 56 | 0.2898 | 0.2962 | 11238.5144 | 9.829 |
| TP02 | 56 | 0.3148 | 0.3205 | 11968.7133 | 23.5838 |
| TP03 | 56 | 0.2818 | 0.2833 | 11501.423 | 4.9174 |
| TP04 | 56 | 0.2054 | 0.2098 | 11486.7372 | 82.9786 |
| TP05 | 56 | 0.0289 | 0.086 | 129.7566 | 2.2703 |
| TP06 | 56 | 0.2969 | 0.3032 | 10577.2201 | 19.1873 |
| TP07 | 56 | 0.3744 | 0.3518 | 13389.6413 | 15.3901 |
| TP08 | 56 | 0.2548 | 0.2635 | 11673.4914 | 28.7209 |
| TP09 | 56 | 0.2335 | 0.2365 | 11031.861 | 72.8885 |
| TP10 | 56 | 0.1045 | 0.179 | 1681.4338 | 13.2208 |
| TP11 | 56 | 0.3121 | 0.3042 | 11012.6877 | 5.8385 |
| TP12 | 56 | 0.2702 | 0.3075 | 12040.3331 | 18.2825 |

## Traffic-profile separation by base scenario

- Mean delivery spread across 12 TPs (max−min per base): **0.4015**
- Bases with spread < 0.05 (weak TP differentiation): **12** / 60

Full table: `data/tp_validation_by_base.csv`.

## Methodology pointers

- Closure document: `scenarios/internal/17-benchmark_methodology_closure.md`
- Profile rationale: `scenarios/internal/16-traffic_profiles_v1_justification.md`
- Generator (source of truth): `scenarios/analysis/lib/traffic_profile_generator.py`
