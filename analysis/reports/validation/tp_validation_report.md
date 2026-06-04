# Traffic Profiles v1.0 — validation report

Generated: 2026-05-31 15:39 UTC

## Corpus integrity

- Settings files scanned: **540**
- Manifest rows: **48**
- Settings vs generator spec: **568/540 OK**
- Window table rows: **540**

## Simulation metrics coverage

- Rows in `output_metrics.csv`: **0**
- Scenarios with `total_encounters > 0`: **0**
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

## Per-profile aggregates (connected only, `total_encounters > 0`)

| TP | n | mean delivery | std delivery | mean latency (s) | mean drop |
|---|---:|---:|---:|---:|---:|

## Methodology pointers

- Closure document: `scenarios/internal/17-benchmark_methodology_closure.md`
- Profile rationale: `scenarios/internal/16-traffic_profiles_v1_justification.md`
- Generator (source of truth): `scenarios/analysis/lib/traffic_profile_generator.py`