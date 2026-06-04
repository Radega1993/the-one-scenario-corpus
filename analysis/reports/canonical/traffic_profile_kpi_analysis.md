# Traffic Profile KPI Analysis (corpus_v1)

Generated: 2026-06-04 10:26 UTC

## Executive summary

- **Corpus:** corpus_v1 — 540 simulations (60 base scenarios × 12 Traffic Profiles).
- **Missing output metrics:** 10 scenario(s) (R2_VillagesTrails_InterVillage__TP01_Baseline, R2_VillagesTrails_InterVillage__TP02_LowLoad, R2_VillagesTrails_InterVillage__TP03_ManySmall, R2_VillagesTrails_InterVillage__TP04_FewLarge, R2_VillagesTrails_InterVillage__TP06_OneToMany, R2_VillagesTrails_InterVillage__TP07_BurstWindow, R2_VillagesTrails_InterVillage__TP09_Bimodal, R2_VillagesTrails_InterVillage__TP10_Storm, R2_VillagesTrails_InterVillage__TP11_ManyToOne, R2_VillagesTrails_InterVillage__TP12_GroupToGroup).
- **Protocol:** Epidemic (current corpus); KPIs defined for future multi-protocol comparison.
- **Baseline:** TP01_Baseline — delivery median 0.856, overhead median 58.7.

## Per-TP distributional stats

| TP | delivery (med) | overhead (med) | drop (med) | latency (med) | n_created (med) | zero del | drop>50% |
|----|----------------|----------------|------------|---------------|-----------------|----------|----------|
| TP01 Baseline | 0.856 | 58.7 | 0.0 | 3185 | 482 | 1 | 5 |
| TP02 LowLoad | 0.875 | 52.2 | 0.0 | 3202 | 96 | 1 | 2 |
| TP03 ManySmall | 0.849 | 51.9 | 0.0 | 3139 | 2214 | 1 | 2 |
| TP04 FewLarge | 0.503 | 394.8 | 168.2 | 3964 | 180 | 2 | 33 |
| TP05 CriticalTTL | 0.027 | 43.1 | 2.0 | 126 | 482 | 1 | 0 |
| TP06 OneToMany | 0.847 | 74.0 | 12.1 | 2836 | 970 | 1 | 11 |
| TP07 BurstWindow | 1.000 | 55.0 | 0.0 | 3323 | 362 | 1 | 4 |
| TP08 HubTarget | 0.684 | 215.3 | 105.1 | 3102 | 970 | 0 | 27 |
| TP09 Bimodal | 0.618 | 305.9 | 143.3 | 3859 | 579 | 1 | 30 |
| TP10 Storm | 0.404 | 53.9 | 22.4 | 1670 | 6160 | 1 | 9 |
| TP11 ManyToOne | 0.795 | 56.2 | 1.6 | 2928 | 970 | 1 | 8 |
| TP12 GroupToGroup | 0.849 | 58.7 | 0.0 | 3179 | 489 | 3 | 6 |

Full statistics: [`traffic_profile_stats.csv`](../data/traffic_profile_stats.csv).

## Global rankings (by median across 60 bases)

### Delivery ratio (higher is better)

1. **TP07** 1.000
2. **TP02** 0.875
3. **TP01** 0.856
4. **TP12** 0.849
5. **TP03** 0.849
6. **TP06** 0.847
7. **TP11** 0.795
8. **TP08** 0.684
9. **TP09** 0.618
10. **TP04** 0.503
11. **TP10** 0.404
12. **TP05** 0.027

### Overhead ratio (lower is better)

1. **TP05** 43.1
2. **TP03** 51.9
3. **TP02** 52.2
4. **TP10** 53.9
5. **TP07** 55.0
6. **TP11** 56.2
7. **TP12** 58.7
8. **TP01** 58.7
9. **TP06** 74.0
10. **TP08** 215.3
11. **TP09** 305.9
12. **TP04** 394.8

### Drop ratio (lower is better)

1. **TP01** 0.0
2. **TP02** 0.0
3. **TP03** 0.0
4. **TP07** 0.0
5. **TP12** 0.0
6. **TP11** 1.6
7. **TP05** 2.0
8. **TP06** 12.1
9. **TP10** 22.4
10. **TP08** 105.1
11. **TP09** 143.3
12. **TP04** 168.2

### Latency mean (lower is better, delivered only)

1. **TP05** 126 s
2. **TP10** 1670 s
3. **TP06** 2836 s
4. **TP11** 2928 s
5. **TP08** 3102 s
6. **TP03** 3139 s
7. **TP12** 3179 s
8. **TP01** 3185 s
9. **TP02** 3202 s
10. **TP07** 3323 s
11. **TP09** 3859 s
12. **TP04** 3964 s

## Comparison vs TP01 (paired median relative delta)

| TP | Δ delivery | Δ overhead | Δ drop | Δ n_created | Δ t_median_frac |
|----|------------|------------|--------|-------------|-----------------|
| TP02 | +1.0% | +0.2% | -100.0% | -80.2% | -0.8% |
| TP03 | -0.4% | -0.5% | -100.0% | +358.5% | -0.0% |
| TP04 | -29.8% | +444.6% | -50.5% | -62.8% | +0.9% |
| TP05 | -95.3% | -12.9% | -98.9% | +0.0% | +0.0% |
| TP06 | +1.2% | +11.6% | -15.4% | +101.0% | -0.5% |
| TP07 | +11.0% | +0.1% | +40.4% | -25.2% | -51.9% |
| TP08 | -11.4% | +243.6% | -28.3% | +101.0% | -0.5% |
| TP09 | -21.5% | +315.8% | +37.2% | +19.8% | +0.0% |
| TP10 | -52.1% | +3.3% | -92.0% | +1174.7% | -0.1% |
| TP11 | -0.5% | +0.0% | -25.8% | +101.0% | -0.5% |
| TP12 | +0.8% | +0.3% | -0.5% | +0.9% | +0.6% |

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
- **TP06 OneToMany** — status: `blocked`
- **TP07 BurstWindow** — status: `blocked`
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
- **TP03** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP04** (`blocked`): 2 zero-delivery, 1 missing output.
- **TP06** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP07** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP09** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP10** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP11** (`blocked`): 1 zero-delivery, 1 missing output.
- **TP12** (`blocked`): 3 zero-delivery, 1 missing output.

## Per-TP KPI summary

See [`traffic_profile_kpi_summary.csv`](../data/traffic_profile_kpi_summary.csv).

| TP | primary | secondary | cost | stress | validation |
|----|---------|-----------|------|--------|------------|
| TP01 | delivery_ratio | latency_mean | overhead_ratio | drop_ratio | blocked |
| TP02 | n_created | delivery_ratio | overhead_ratio | drop_ratio | blocked |
| TP03 | overhead_ratio | delivery_ratio | total_encounters | drop_ratio | blocked |
| TP04 | drop_ratio | delivery_ratio | overhead_ratio | latency_mean | blocked |
| TP05 | delivery_ratio | latency_mean | overhead_ratio | drop_ratio | validated |
| TP06 | delivery_ratio | latency_mean | overhead_ratio | popularity_top10_ratio | blocked |
| TP07 | delivery_ratio | t_median_frac | overhead_ratio | latency_mean | blocked |
| TP08 | popularity_top10_ratio | delivery_ratio | overhead_ratio | drop_ratio | validated |
| TP09 | drop_ratio | delivery_ratio | overhead_ratio | latency_mean | blocked |
| TP10 | delivery_ratio | n_created | overhead_ratio | drop_ratio | blocked |
| TP11 | delivery_ratio | overhead_ratio | latency_mean | drop_ratio | blocked |
| TP12 | delivery_ratio | overhead_ratio | latency_mean | drop_ratio | blocked |

## Cross-references

- [`tp_validation_report.md`](tp_validation_report.md)
- [`corpus_v1_benchmark_validation.md`](corpus_v1_benchmark_validation.md)
- [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)
- [`traffic_profile_stats.csv`](../data/traffic_profile_stats.csv)
