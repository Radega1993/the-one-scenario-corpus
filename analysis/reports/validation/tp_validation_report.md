# Traffic Profiles v1.0 — validation report

Generated: 2026-06-05 12:40 UTC

## Corpus integrity

- Settings files scanned: **540**
- Manifest rows: **540**
- Settings vs generator spec: **538/540 OK**
- Window table rows: **540**

## Simulation metrics coverage

- Rows in `output_metrics.csv`: **600**
- Scenarios with `total_encounters > 0`: **540**
- Disconnected control (`total_encounters = 0`): **0**

## Settings mismatches (action required)

**2** files differ from `lib/traffic_profile_generator.py`.

| scenario | mismatches |
|---|---|
| `U4_CongestionHotspot_HelsinkiDowntown__TP05_CriticalTTL` | Group.msgTtl: got='15' exp='5'; Group*.msgTtl inconsistent: 15 != 5 |
| `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP05_CriticalTTL` | Group.msgTtl: got='15' exp='5'; Group*.msgTtl inconsistent: 15 != 5 |

## Per-profile aggregates (global view)

| TP | n | mean delivery | std delivery | mean latency (s) | mean drop |
|---|---:|---:|---:|---:|---:|
| TP01 | 50 | 0.7241 | 0.2583 | 5066.1198 | 59.6773 |
| TP02 | 50 | 0.7543 | 0.2425 | 4555.9786 | 71.5082 |
| TP03 | 50 | 0.7309 | 0.2546 | 5420.6154 | 7.0702 |
| TP04 | 50 | 0.5159 | 0.229 | 5445.3977 | 396.4174 |
| TP05 | 50 | 0.0852 | 0.1326 | 124.4874 | 4.1127 |
| TP06 | 50 | 0.7742 | 0.1996 | 4351.0011 | 66.6671 |
| TP07 | 50 | 0.824 | 0.2466 | 6746.3055 | 97.0597 |
| TP08 | 50 | 0.6456 | 0.2324 | 4981.2968 | 238.3678 |
| TP09 | 50 | 0.5848 | 0.2174 | 5692.3503 | 341.7074 |
| TP10 | 50 | 0.3977 | 0.2825 | 1538.7094 | 46.6374 |
| TP11 | 50 | 0.7599 | 0.1982 | 4363.1533 | 48.0191 |
| TP12 | 50 | 0.7678 | 0.2463 | 4353.7822 | 66.9142 |

## Per-profile aggregates (connected only, `total_encounters > 0`)

| TP | n | mean delivery | std delivery | mean latency (s) | mean drop |
|---|---:|---:|---:|---:|---:|
| TP01 | 45 | 0.7239 | 0.2596 | 4962.4358 | 66.3072 |
| TP02 | 45 | 0.751 | 0.2448 | 4522.1744 | 79.4536 |
| TP03 | 45 | 0.7326 | 0.2537 | 5299.7922 | 7.8557 |
| TP04 | 45 | 0.5112 | 0.2246 | 5283.9131 | 426.8887 |
| TP05 | 45 | 0.0802 | 0.1334 | 127.2097 | 4.2369 |
| TP06 | 45 | 0.7769 | 0.2005 | 4308.5483 | 72.4529 |
| TP07 | 45 | 0.8234 | 0.2503 | 6485.889 | 107.7776 |
| TP08 | 45 | 0.6446 | 0.2316 | 4977.3029 | 254.7517 |
| TP09 | 45 | 0.5815 | 0.211 | 5575.0908 | 368.2834 |
| TP10 | 45 | 0.4011 | 0.2807 | 1555.5509 | 50.3221 |
| TP11 | 45 | 0.7593 | 0.2015 | 4258.1832 | 52.1606 |
| TP12 | 45 | 0.7627 | 0.2548 | 4397.608 | 72.8924 |

## Traffic-profile separation by base scenario

- Mean delivery spread across 12 TPs (max−min per base): **0.7886**
- Bases with spread < 0.05 (weak TP differentiation): **0** / 50

Full table: `data/tp_validation_by_base.csv`.

## Methodology pointers

- Closure document: `scenarios/internal/17-benchmark_methodology_closure.md`
- Profile rationale: `scenarios/internal/16-traffic_profiles_v1_justification.md`
- Generator (source of truth): `scenarios/analysis/lib/traffic_profile_generator.py`
