# Protocol benchmark KPI policy (corpus_v1)

Generated: 2026-06-04 10:26 UTC

## Executive summary

- **Corpus:** corpus_v1 — 720 simulations (Epidemic reference router).
- **Comparison scope:** same mobility, map, Traffic Profile; only `Group.router` changes via overlays.
- **Primary metrics window:** full simulation (`valid_start=0`, `valid_end=endTime`) per [message_analysis_window_policy.md](message_analysis_window_policy.md).
- **Optional sensitivity:** exclude messages with `creation_time >= 0.9 * endTime` (appendix only).

## Core-4 KPIs (all protocol comparisons)

| KPI | Direction | Role |
|-----|-----------|------|
| `delivery_ratio` | maximize | Primary routing effectiveness |
| `overhead_ratio` | minimize | Replication cost |
| `latency_mean` | minimize | Delivery delay (delivered messages only) |
| `drop_ratio` | minimize | Buffer/transmission stress |

## Benchmark splits (`manifest_revision.csv`)

| Split | Scenarios |
|-------|----------:|
| `control` | 53 |
| `main` | 130 |
| `stress` | 189 |

## Tier reporting rules

1. **main** — Primary claims and protocol rankings (TP01–TP08, viable bases).
2. **stress** — TP04/05/09/10 and extreme load; never mix with main-tier medians without label.
3. **control** — TP12 cross-group partition; document partition behavior, not delivery leaderboard.

## Exclusions before ranking

- `validation_status == error_probable` (missing or corrupt simulation output).
- `validation_status == configuracion_sospechosa` unless explicitly included in sensitivity appendix.
- Zero-contact disconnected bases (document as `valido_extremo`, exclude from latency rankings).

- Traffic profiles blocked in KPI summary: **12** (re-check after re-simulation).

## Protocols and overlays

| Protocol | Status | Overlay / notes |
|----------|--------|-----------------|
| Epidemic | measured | Current corpus_v1 router in all 720 .settings |
| PRoPHET | pending | Overlay: protocol_overlays/router_prophet.txt |
| MaxProp | pending | Overlay: protocol_overlays/router_maxprop.txt |
| SprayAndWait | pending | Overlay: protocol_overlays/router_sprayandwait.txt |

## Per-TP KPI guidance

Use [`traffic_profile_kpi_summary.csv`](../data/traffic_profile_kpi_summary.csv) for profile-specific primary/secondary KPIs when interpreting Epidemic baseline. Protocol comparison should still report core-4 on the same scenario subset.

## Aggregation

- Report **median** per TP and per family; show IQR or bootstrap CI if seeds available.
- Paired comparison: same `scenario_base` + TP across protocols (720-row join on scenario key).

## Artifacts

- Definitions: [`protocol_benchmark_kpi_definitions.csv`](../data/protocol_benchmark_kpi_definitions.csv)
- Traffic profiles: [`traffic_profile_kpi_analysis.md`](traffic_profile_kpi_analysis.md)
- Window policy: [`message_analysis_window_policy.md`](message_analysis_window_policy.md)
- Validation: [`corpus_v1_benchmark_validation.md`](corpus_v1_benchmark_validation.md)

## Regeneration

```bash
python3 scenarios/analysis/build_protocol_benchmark_kpi_policy.py
```
