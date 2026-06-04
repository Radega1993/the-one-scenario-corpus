# Traffic Profile KPI Analysis (corpus_v1)

Generated: 2026-05-27 13:55 UTC

## Executive summary

- **Corpus:** corpus_v1 — 540 simulations (60 base scenarios × 12 Traffic Profiles).
- **Missing output metrics:** 15 scenario(s) (U4_CongestionHotspot_HelsinkiDowntown__TP03_ManySmall, U5_WorkdayShort_HelsinkiDowntown__TP03_ManySmall, U5_WorkdayShort_HelsinkiDowntown__TP06_OneToMany, U5_WorkdayShort_HelsinkiDowntown__TP07_BurstWindow, S1_StrongCommunities_SeparateClusters__TP03_ManySmall, S1_StrongCommunities_SeparateClusters__TP06_OneToMany, S1_StrongCommunities_SeparateClusters__TP07_BurstWindow, S1_StrongCommunities_SeparateClusters__TP08_HubTarget, S1_StrongCommunities_SeparateClusters__TP09_Bimodal, S1_StrongCommunities_SeparateClusters__TP10_Storm, S1_StrongCommunities_SeparateClusters__TP11_ManyToOne, S1_StrongCommunities_SeparateClusters__TP12_GroupToGroup, S2_WeakCommunities_HighMixing__TP01_Baseline, S2_WeakCommunities_HighMixing__TP02_LowLoad, S2_WeakCommunities_HighMixing__TP03_ManySmall).
- **Protocol:** Epidemic (current corpus); KPIs defined for future multi-protocol comparison.
- **Baseline:** TP01_Baseline — delivery median 0.808, overhead median 54.6.

## Per-TP distributional stats

| TP | delivery (med) | overhead (med) | drop (med) | latency (med) | n_created (med) | zero del | drop>50% |
|----|----------------|----------------|------------|---------------|-----------------|----------|----------|
| TP01 Baseline | 0.808 | 54.6 | 0.0 | 2842 | 483 | 1 | 4 |
| TP02 LowLoad | 0.872 | 50.3 | 0.0 | 2752 | 96 | 1 | 2 |
| TP03 ManySmall | 0.850 | 48.0 | 0.0 | 2987 | 2216 | 4 | 2 |
| TP04 FewLarge | 0.475 | 443.9 | 194.5 | 3591 | 180 | 1 | 34 |
| TP05 CriticalTTL | 0.027 | 44.8 | 2.3 | 125 | 483 | 0 | 0 |
| TP06 OneToMany | 0.834 | 72.2 | 14.5 | 2561 | 970 | 2 | 15 |
| TP07 BurstWindow | 1.000 | 52.0 | 0.0 | 3064 | 364 | 2 | 4 |
| TP08 HubTarget | 0.660 | 209.6 | 101.9 | 3035 | 970 | 1 | 26 |
| TP09 Bimodal | 0.588 | 348.5 | 165.4 | 3705 | 579 | 1 | 31 |
| TP10 Storm | 0.354 | 59.8 | 23.9 | 1565 | 6157 | 1 | 12 |
| TP11 ManyToOne | 0.729 | 54.0 | 0.3 | 2656 | 970 | 1 | 8 |
| TP12 GroupToGroup | 0.816 | 52.9 | 0.0 | 3179 | 489 | 5 | 6 |

Full statistics: [`traffic_profile_stats.csv`](../data/traffic_profile_stats.csv).

## Global rankings (by median across 60 bases)

### Delivery ratio (higher is better)

1. **TP07** 1.000
2. **TP02** 0.872
3. **TP03** 0.850
4. **TP06** 0.834
5. **TP12** 0.816
6. **TP01** 0.808
7. **TP11** 0.729
8. **TP08** 0.660
9. **TP09** 0.588
10. **TP04** 0.475
11. **TP10** 0.354
12. **TP05** 0.027

### Overhead ratio (lower is better)

1. **TP05** 44.8
2. **TP03** 48.0
3. **TP02** 50.3
4. **TP07** 52.0
5. **TP12** 52.9
6. **TP11** 54.0
7. **TP01** 54.6
8. **TP10** 59.8
9. **TP06** 72.2
10. **TP08** 209.6
11. **TP09** 348.5
12. **TP04** 443.9

### Drop ratio (lower is better)

1. **TP01** 0.0
2. **TP02** 0.0
3. **TP03** 0.0
4. **TP07** 0.0
5. **TP12** 0.0
6. **TP11** 0.3
7. **TP05** 2.3
8. **TP06** 14.5
9. **TP10** 23.9
10. **TP08** 101.9
11. **TP09** 165.4
12. **TP04** 194.5

### Latency mean (lower is better, delivered only)

1. **TP05** 125 s
2. **TP10** 1565 s
3. **TP06** 2561 s
4. **TP11** 2656 s
5. **TP02** 2752 s
6. **TP01** 2842 s
7. **TP03** 2987 s
8. **TP08** 3035 s
9. **TP07** 3064 s
10. **TP12** 3179 s
11. **TP04** 3591 s
12. **TP09** 3705 s

## Comparison vs TP01 (paired median relative delta)

| TP | Δ delivery | Δ overhead | Δ drop | Δ n_created | Δ t_median_frac |
|----|------------|------------|--------|-------------|-----------------|
| TP02 | +0.7% | +0.2% | -100.0% | -80.2% | -1.2% |
| TP03 | -0.2% | -0.5% | -100.0% | +358.7% | -0.1% |
| TP04 | -28.6% | +605.5% | -57.9% | -62.8% | +0.8% |
| TP05 | -95.1% | -12.8% | -98.7% | +0.0% | +0.0% |
| TP06 | +1.4% | +13.5% | -14.8% | +100.8% | -0.4% |
| TP07 | +7.0% | +0.2% | -10.3% | -25.1% | -51.9% |
| TP08 | -11.5% | +232.3% | -29.6% | +100.8% | -0.4% |
| TP09 | -20.2% | +463.7% | +11.8% | +19.8% | +0.0% |
| TP10 | -52.0% | +3.3% | -91.3% | +1172.3% | -0.1% |
| TP11 | -0.0% | -0.1% | -18.1% | +100.8% | -0.4% |
| TP12 | +0.3% | +1.0% | -1.8% | +0.8% | +0.6% |

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

- **TP01 Baseline** — status: `blocked`
- **TP02 LowLoad** — status: `blocked`
- **TP03 ManySmall** — status: `blocked`
- **TP04 FewLarge** — status: `blocked`
- **TP05 CriticalTTL** — status: `blocked`
- **TP06 OneToMany** — status: `blocked`
- **TP07 BurstWindow** — status: `blocked`
- **TP08 HubTarget** — status: `blocked`
- **TP09 Bimodal** — status: `blocked`
- **TP10 Storm** — status: `blocked`
- **TP11 ManyToOne** — status: `blocked`
- **TP12 GroupToGroup** — status: `blocked`
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

- **TP01** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP02** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP03** (`blocked`): 4 zero-delivery, 4 missing output.
- **TP04** (`blocked`): 1 zero-delivery, 0 missing output.
- **TP05** (`blocked`): 0 zero-delivery, 0 missing output.
- **TP06** (`blocked`): 2 zero-delivery, 2 missing output.
- **TP07** (`blocked`): 2 zero-delivery, 2 missing output.
- **TP08** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP09** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP10** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP11** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP12** (`blocked`): 5 zero-delivery, 1 missing output.

## Per-TP KPI summary

See [`traffic_profile_kpi_summary.csv`](../data/traffic_profile_kpi_summary.csv).

| TP | primary | secondary | cost | stress | validation |
|----|---------|-----------|------|--------|------------|
| TP01 | delivery_ratio | latency_mean | overhead_ratio | drop_ratio | blocked |
| TP02 | n_created | delivery_ratio | overhead_ratio | drop_ratio | blocked |
| TP03 | overhead_ratio | delivery_ratio | total_encounters | drop_ratio | blocked |
| TP04 | drop_ratio | delivery_ratio | overhead_ratio | latency_mean | blocked |
| TP05 | delivery_ratio | latency_mean | overhead_ratio | drop_ratio | blocked |
| TP06 | delivery_ratio | latency_mean | overhead_ratio | popularity_top10_ratio | blocked |
| TP07 | delivery_ratio | t_median_frac | overhead_ratio | latency_mean | blocked |
| TP08 | popularity_top10_ratio | delivery_ratio | overhead_ratio | drop_ratio | blocked |
| TP09 | drop_ratio | delivery_ratio | overhead_ratio | latency_mean | blocked |
| TP10 | delivery_ratio | n_created | overhead_ratio | drop_ratio | blocked |
| TP11 | delivery_ratio | overhead_ratio | latency_mean | drop_ratio | blocked |
| TP12 | delivery_ratio | overhead_ratio | latency_mean | drop_ratio | blocked |

## Cross-references

- [`tp_validation_report.md`](tp_validation_report.md)
- [`corpus_v1_benchmark_validation.md`](corpus_v1_benchmark_validation.md)
- [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)
- [`traffic_profile_stats.csv`](../data/traffic_profile_stats.csv)