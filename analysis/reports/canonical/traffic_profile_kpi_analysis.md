# Traffic Profile KPI Analysis (corpus_v2)

Generated: 2026-05-24 12:07 UTC

## Executive summary

- **Corpus:** corpus_v2 — 720 simulations (60 base scenarios × 12 Traffic Profiles).
- **Missing output metrics:** 1 scenario(s) (S1_StrongCommunities_SeparateClusters__TP03_ManySmall).
- **Protocol:** Epidemic (current corpus); KPIs defined for future multi-protocol comparison.
- **Baseline:** TP01_Baseline — delivery median 0.235, overhead median 44.4.

## Per-TP distributional stats

| TP | delivery (med) | overhead (med) | drop (med) | latency (med) | n_created (med) | zero del | drop>50% |
|----|----------------|----------------|------------|---------------|-----------------|----------|----------|
| TP01 Baseline | 0.235 | 44.4 | 0.0 | 13038 | 482 | 0 | 2 |
| TP02 LowLoad | 0.224 | 45.8 | 0.0 | 13532 | 96 | 5 | 1 |
| TP03 ManySmall | 0.233 | 35.2 | 0.0 | 14704 | 2217 | 1 | 1 |
| TP04 FewLarge | 0.187 | 59.7 | 0.7 | 13460 | 180 | 6 | 13 |
| TP05 CriticalTTL | 0.004 | 38.7 | 1.1 | 114 | 482 | 25 | 0 |
| TP06 OneToMany | 0.191 | 37.9 | 0.2 | 10947 | 970 | 8 | 7 |
| TP07 BurstWindow | 0.309 | 45.1 | 0.0 | 15949 | 364 | 0 | 2 |
| TP08 HubTarget | 0.181 | 51.1 | 0.0 | 13438 | 970 | 2 | 9 |
| TP09 Bimodal | 0.212 | 43.3 | 0.8 | 13316 | 579 | 0 | 13 |
| TP10 Storm | 0.033 | 43.7 | 1.7 | 1754 | 6157 | 2 | 3 |
| TP11 ManyToOne | 0.246 | 35.4 | 0.0 | 11016 | 970 | 8 | 2 |
| TP12 GroupToGroup | 0.136 | 46.9 | 0.0 | 12152 | 489 | 9 | 4 |

Full statistics: [`traffic_profile_stats.csv`](../data/traffic_profile_stats.csv).

## Global rankings (by median across 60 bases)

### Delivery ratio (higher is better)

1. **TP07** 0.309
2. **TP11** 0.246
3. **TP01** 0.235
4. **TP03** 0.233
5. **TP02** 0.224
6. **TP09** 0.212
7. **TP06** 0.191
8. **TP04** 0.187
9. **TP08** 0.181
10. **TP12** 0.136
11. **TP10** 0.033
12. **TP05** 0.004

### Overhead ratio (lower is better)

1. **TP03** 35.2
2. **TP11** 35.4
3. **TP06** 37.9
4. **TP05** 38.7
5. **TP09** 43.3
6. **TP10** 43.7
7. **TP01** 44.4
8. **TP07** 45.1
9. **TP02** 45.8
10. **TP12** 46.9
11. **TP08** 51.1
12. **TP04** 59.7

### Drop ratio (lower is better)

1. **TP01** 0.0
2. **TP02** 0.0
3. **TP03** 0.0
4. **TP08** 0.0
5. **TP07** 0.0
6. **TP12** 0.0
7. **TP11** 0.0
8. **TP06** 0.2
9. **TP04** 0.7
10. **TP09** 0.8
11. **TP05** 1.1
12. **TP10** 1.7

### Latency mean (lower is better, delivered only)

1. **TP05** 114 s
2. **TP10** 1754 s
3. **TP06** 10947 s
4. **TP11** 11016 s
5. **TP12** 12152 s
6. **TP01** 13038 s
7. **TP09** 13316 s
8. **TP08** 13438 s
9. **TP04** 13460 s
10. **TP02** 13532 s
11. **TP03** 14704 s
12. **TP07** 15949 s

## Comparison vs TP01 (paired median relative delta)

| TP | Δ delivery | Δ overhead | Δ drop | Δ n_created | Δ t_median_frac |
|----|------------|------------|--------|-------------|-----------------|
| TP02 | +3.2% | +3.2% | -100.0% | -80.2% | -1.2% |
| TP03 | -2.1% | -9.8% | -100.0% | +359.6% | -0.1% |
| TP04 | -26.4% | +30.5% | -56.8% | -62.7% | +0.7% |
| TP05 | -99.2% | -15.5% | -55.4% | +0.0% | +0.0% |
| TP06 | +0.1% | -8.5% | +10.7% | +100.8% | -0.4% |
| TP07 | +40.7% | +1.1% | +33.6% | -24.9% | -51.9% |
| TP08 | -8.9% | +1.3% | +12.3% | +100.8% | -0.4% |
| TP09 | -15.7% | -0.5% | -0.2% | +19.8% | +0.2% |
| TP10 | -85.5% | -4.3% | -45.8% | +1173.2% | -0.1% |
| TP11 | +6.7% | -19.4% | -19.0% | +100.8% | -0.4% |
| TP12 | -0.8% | +1.8% | +5.9% | +0.8% | +0.6% |

## Profile classification

### Favorable profiles

- **TP07 BurstWindow:** highest delivery median; burst window confirmed (t_median_frac ≈ 0.24).
- **TP02 LowLoad:** reduced n_created (~5× below TP01); delivery can exceed baseline (less congestion).

### Stress profiles

- **TP04 FewLarge:** drop mean ~80% (13 scenarios >50%); stresses buffer/transmission.
- **TP05 CriticalTTL:** delivery median ~0.004; latency ~114 s when delivered.
- **TP09 Bimodal:** high drop from large-message component.
- **TP10 Storm:** delivery median ~0.10; high generation rate.

### Directional profiles

- **TP06 OneToMany**, **TP08 HubTarget**, **TP11 ManyToOne**, **TP12 GroupToGroup:** asymmetric traffic patterns; use popularity/overhead alongside delivery.

### Problematic / review before freeze

- **TP03 ManySmall** — status: `blocked`
- **S1_StrongCommunities_SeparateClusters** TP03/TP11: missing output (re-simulate).
- **R1_Rural_RandomWaypoint**, **R11_SpeedExtremeLow:** zero delivery across all TPs (disconnected bases).
- **TP12** urban WDM scenarios: extreme overhead in some bases (document or fix worldSize).

## Recommended KPIs for routing benchmark

### Main paper (core-4)

1. **delivery_ratio** — primary effectiveness.
2. **overhead_ratio** — replication cost.
3. **latency_mean** — conditioned on delivery > 0.
4. **drop_ratio** — buffer/transmission stress.

### Paper (profile-specific context)

| Profile | Extra KPI | Rationale |
|---------|-----------|-----------|
| TP02 | n_created | Load normalization |
| TP03 | total_encounters | Copy spread under many small messages |
| TP07 | t_median_frac | Burst timing validation |
| TP08 | popularity_top10_ratio | Hub concentration |
| TP06/TP11/TP12 | overhead + delivery | Directional asymmetry |

### Supplementary material

- contact_time_per_min, contact_time_mean_s, total_encounters
- ratio_contact_nodes, spatial final_coverage_pct
- useful_time_ratio, message creation time distribution (pct_last_10pct_sim)
- Full indirect features and per-base spread (`tp_validation_by_base.csv`)

## Profiles requiring adjustment before freeze

- **TP03** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP04** (`partial`): 6 zero-delivery, 0 missing output.
- **TP06** (`partial`): 8 zero-delivery, 0 missing output.
- **TP11** (`partial`): 8 zero-delivery, 0 missing output.

## Per-TP KPI summary

See [`traffic_profile_kpi_summary.csv`](../data/traffic_profile_kpi_summary.csv).

| TP | primary | secondary | cost | stress | validation |
|----|---------|-----------|------|--------|------------|
| TP01 | delivery_ratio | latency_mean | overhead_ratio | drop_ratio | validated |
| TP02 | n_created | delivery_ratio | overhead_ratio | drop_ratio | validated |
| TP03 | overhead_ratio | delivery_ratio | total_encounters | drop_ratio | blocked |
| TP04 | drop_ratio | delivery_ratio | overhead_ratio | latency_mean | partial |
| TP05 | delivery_ratio | latency_mean | overhead_ratio | drop_ratio | validated |
| TP06 | delivery_ratio | latency_mean | overhead_ratio | popularity_top10_ratio | partial |
| TP07 | delivery_ratio | t_median_frac | overhead_ratio | latency_mean | validated |
| TP08 | popularity_top10_ratio | delivery_ratio | overhead_ratio | drop_ratio | validated |
| TP09 | drop_ratio | delivery_ratio | overhead_ratio | latency_mean | validated |
| TP10 | delivery_ratio | n_created | overhead_ratio | drop_ratio | validated |
| TP11 | delivery_ratio | overhead_ratio | latency_mean | drop_ratio | partial |
| TP12 | delivery_ratio | overhead_ratio | latency_mean | drop_ratio | validated |

## Cross-references

- [`tp_validation_report.md`](tp_validation_report.md)
- [`corpus_v2_benchmark_validation.md`](corpus_v2_benchmark_validation.md)
- [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)
- [`traffic_profile_stats.csv`](../data/traffic_profile_stats.csv)
