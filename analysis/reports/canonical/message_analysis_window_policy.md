# Message analysis window policy (corpus_v1)

Generated: 2026-05-27 13:53 UTC

Canonical policy for message-level metric aggregation. **Replaces** the earlier draft recommending 5% warmup + TTL cutoff (policy B+warmup).

See also: [message_creation_time_audit.md](message_creation_time_audit.md), [simulation_time_policy.md](simulation_time_policy.md) (endTime/worldSize only).

## Executive summary

- **Corpus:** corpus_v1 — 540 simulations (60 bases × 12 Traffic Profiles).
- **Primary policy:** report delivery, latency, overhead, and drop using **all messages** created during the simulation (`valid_start=0`, `valid_end=endTime`).
- **Optional supplementary analysis:** exclude messages with `creation_time ≥ 0.9×endTime`.
- **No global warmup** in primary message metrics (warmup 5% reserved for sensitivity appendix only).

## Interpretation of existing figures

### Boxplot (`figures/message_creation_time_boxplot_by_tp.png`)

Per-scenario **median** of `creation_time/endTime`, grouped by TP. The dashed red line at **0.9** marks the start of the last 10% of simulation time. Most TPs cluster near **0.5** (uniform generation over the full window). **TP07** is the clear outlier (~0.24): traffic is intentionally concentrated in an early burst, not near the end.

### Histograms (`figures/message_creation_time_hist_by_tp.png`)

Pooled normalized creation times per TP. Full-window profiles show roughly flat distributions on [0,1]. **TP07** shows a narrow peak at 20–28% of endTime. The ~10% tail mass near 1.0 in full-window TPs matches the expected fraction of messages born in the closing decile.

## Why late messages bias delivery_ratio

Messages created after `0.9×endTime` have at most 10% of remaining simulation time for routing, buffering, and delivery. Even with long TTL, short remaining contact opportunities depress `delivery_ratio` and inflate or distort `latency_mean` (many never delivered). `MessageStatsReport` aggregates over **all** created messages, so this censoring is embedded in current corpus_v1 metrics.

## Evidence in corpus_v1

- Scenarios with `pct_messages_last_10 > 12%`: **2** (`late_message_bias`).
- Scenarios with `pct_messages_last_10` in [10%, 12%]: **253** (`sensitivity_required`).
- Pearson correlation `pct_messages_last_10` vs `delivery_ratio` (connected scenarios, n=501): **r = -0.18**.

**Conclusion:** Late-message censoring is a **moderate structural effect** (~10% of messages in the last decile for full-window TPs), not a simulation bug. It is predictable from MessageEventGenerator semantics and should be disclosed, not silently corrected in primary results.

### Per-TP summary

| TP | window | med norm | % first 10 (mean) | % last 10 (mean) | decision |
|----|--------|----------|-------------------|------------------|----------|
| TP01 | full_simulation | 0.500 | 10.15 | 10.02 | complete_window |
| TP02 | full_simulation | 0.496 | 10.42 | 9.99 | sensitivity_required |
| TP03 | full_simulation | 0.500 | 9.97 | 9.99 | complete_window |
| TP04 | full_simulation | 0.504 | 9.64 | 9.77 | complete_window |
| TP05 | full_simulation | 0.500 | 10.15 | 10.02 | complete_window |
| TP06 | directional | 0.498 | 10.01 | 10.20 | sensitivity_required |
| TP07 | burst_only | 0.240 | 0.00 | 0.00 | burst_exception |
| TP08 | directional | 0.498 | 10.01 | 10.20 | sensitivity_required |
| TP09 | full_simulation | 0.501 | 9.82 | 10.00 | complete_window |
| TP10 | full_simulation | 0.500 | 10.08 | 9.93 | stress_profile |
| TP11 | directional | 0.498 | 10.01 | 10.20 | sensitivity_required |
| TP12 | directional | 0.504 | 9.86 | 9.60 | complete_window |

### Outlier scenarios (highest % last 10%)

| Scenario | TP | % last 10 | delivery_ratio |
|----------|-----|----------:|---------------:|
| `R5_MountainRescue__TP02_LowLoad` | TP02 | 12.1 | 0.7879 |
| `D7_HighLoad_TrafficStorm__TP02_LowLoad` | TP02 | 12.1 | 0.9697 |
| `C6_EmergencyDrill_Evacuation__TP02_LowLoad` | TP02 | 11.8 | 0.9412 |
| `R4_ParkRangers_NuuksioSparseTrails__TP02_LowLoad` | TP02 | 11.5 | 0.9479 |
| `R6_SparseLongRange__TP02_LowLoad` | TP02 | 11.5 | 0.9063 |
| `U2_SparseSuburb_HelsinkiDowntown__TP02_LowLoad` | TP02 | 11.3 | 0.3608 |
| `R2_VillagesTrails_ThreeClusters__TP02_LowLoad` | TP02 | 11.3 | 0.2474 |
| `R7_SparseTinyBuffer__TP02_LowLoad` | TP02 | 11.3 | 0.3711 |

## TP07 — burst exception

TP07 (`BurstWindow`) generates traffic only in **[0.20, 0.28]×endTime** (`burst_only`). `pct_messages_last_10 ≈ 0%` by design. Do **not** treat TP07 as late-message bias; do **not** apply the 0.9 cutoff as a bias correction. Compare TP07 on its own temporal regime.

## TP10 — storm / stress profile

TP10 (`Storm`) uses full simulation window but very high generation rate. Report in the **stress tier** alongside TP04/TP05/TP09, not as a normal traffic baseline.

## Official policy for the paper

### Primary (main text)

1. Compute delivery, latency, overhead, and drop on **all messages** in each scenario.
2. Do **not** apply a global mobility warmup to message outcome metrics.
3. Disclose that ~10% of messages in full-window TPs are created in the final 10% of simulation time.

### Optional (supplementary)

Recompute metrics excluding messages with `creation_time ≥ 0.9×Scenario.endTime`. Label as **censored-late** sensitivity analysis.

### Sensitivity appendix

| Analysis | Window | Purpose |
|----------|--------|---------|
| A (primary) | [0, endTime] | Official benchmark |
| B (supplementary) | [0, 0.9×endTime] | Late-message censoring |
| C (discarded draft) | [0.05×endTime, endTime−TTL] | Former B+warmup policy — not adopted |

## Declarable limitations

- Current pipeline reads aggregate `MessageStatsReport`; per-message filtering requires `CreatedMessagesReport` (not yet in default batch).
- TP05 short TTL interacts with late creation: some messages expire before delivery regardless of window.
- Disconnected bases (R1, R11, etc.) have zero contacts; window policy is moot.
- `simulation_time_policy` (5%/90% cutoffs) applies to **endTime/worldSize review**, not primary message KPIs.

## Final TP decision table

| TP | tp_decision | Rationale |
|----|-------------|-----------|
| TP01 Baseline | `complete_window` | Full simulation window; primary metrics use all messages. |
| TP02 LowLoad | `sensitivity_required` | Low load with extended generation; elevated late-message fraction (~10%). |
| TP03 ManySmall | `complete_window` | Full simulation window; primary metrics use all messages. |
| TP04 FewLarge | `complete_window` | Full simulation window; primary metrics use all messages. |
| TP05 CriticalTTL | `complete_window` | Full simulation window; primary metrics use all messages. |
| TP06 OneToMany | `sensitivity_required` | Directional fan-out; include censored sensitivity analysis. |
| TP07 BurstWindow | `burst_exception` | Early burst window (20-28% endTime); late cutoff not applicable. |
| TP08 HubTarget | `sensitivity_required` | Hub-target directional traffic; include censored sensitivity analysis. |
| TP09 Bimodal | `complete_window` | Full simulation window; primary metrics use all messages. |
| TP10 Storm | `stress_profile` | Storm/saturation stress tier; report separately from normal traffic profiles. |
| TP11 ManyToOne | `sensitivity_required` | Directional fan-in; include censored sensitivity analysis. |
| TP12 GroupToGroup | `complete_window` | Full simulation window; primary metrics use all messages. |

## Data files

- [`message_analysis_window_policy.csv`](../data/message_analysis_window_policy.csv) — per scenario
- [`message_analysis_window_by_tp.csv`](../data/message_analysis_window_by_tp.csv) — per TP
- [`message_creation_time_summary.csv`](../data/message_creation_time_summary.csv)
- [`traffic_profile_windows.csv`](../data/traffic_profile_windows.csv)

## Cross-references

- [traffic_profile_kpi_analysis.md](traffic_profile_kpi_analysis.md)
- [corpus_v1_benchmark_validation.md](corpus_v1_benchmark_validation.md)