# Traffic Profile KPI Analysis (corpus_v1)

Generated: 2026-06-05 12:42 UTC

## Executive summary

- **Corpus:** corpus_v1 — 540 simulations (60 base scenarios × 12 Traffic Profiles).
- **Missing output metrics:** 0 scenario(s) (none).
- **Protocol:** Epidemic (current corpus); KPIs defined for future multi-protocol comparison.
- **Baseline:** TP01_Baseline — delivery median 0.856, overhead median 57.4.

## Per-TP distributional stats

| TP | delivery (med) | overhead (med) | drop (med) | latency (med) | n_created (med) | zero del | drop>50% |
|----|----------------|----------------|------------|---------------|-----------------|----------|----------|
| TP01 Baseline | 0.856 | 57.4 | 0.0 | 2766 | 482 | 0 | 5 |
| TP02 LowLoad | 0.875 | 51.5 | 0.0 | 2645 | 96 | 0 | 2 |
| TP03 ManySmall | 0.850 | 51.7 | 0.0 | 2987 | 2216 | 0 | 2 |
| TP04 FewLarge | 0.514 | 412.5 | 194.5 | 3591 | 180 | 1 | 35 |
| TP05 CriticalTTL | 0.027 | 43.1 | 2.0 | 127 | 482 | 1 | 0 |
| TP06 OneToMany | 0.861 | 71.3 | 9.6 | 2802 | 970 | 0 | 13 |
| TP07 BurstWindow | 1.000 | 52.0 | 0.0 | 3010 | 364 | 0 | 4 |
| TP08 HubTarget | 0.717 | 221.5 | 127.6 | 3093 | 970 | 0 | 30 |
| TP09 Bimodal | 0.619 | 307.2 | 156.5 | 3711 | 579 | 0 | 32 |
| TP10 Storm | 0.424 | 54.9 | 23.1 | 1673 | 6157 | 0 | 11 |
| TP11 ManyToOne | 0.820 | 57.0 | 2.6 | 2883 | 970 | 0 | 8 |
| TP12 GroupToGroup | 0.877 | 53.2 | 0.0 | 2939 | 489 | 2 | 6 |

Full statistics: [`traffic_profile_stats.csv`](../data/traffic_profile_stats.csv).

## Global rankings (by median across 60 bases)

### Delivery ratio (higher is better)

1. **TP07** 1.000
2. **TP12** 0.877
3. **TP02** 0.875
4. **TP06** 0.861
5. **TP01** 0.856
6. **TP03** 0.850
7. **TP11** 0.820
8. **TP08** 0.717
9. **TP09** 0.619
10. **TP04** 0.514
11. **TP10** 0.424
12. **TP05** 0.027

### Overhead ratio (lower is better)

1. **TP05** 43.1
2. **TP02** 51.5
3. **TP03** 51.7
4. **TP07** 52.0
5. **TP12** 53.2
6. **TP10** 54.9
7. **TP11** 57.0
8. **TP01** 57.4
9. **TP06** 71.3
10. **TP08** 221.5
11. **TP09** 307.2
12. **TP04** 412.5

### Drop ratio (lower is better)

1. **TP01** 0.0
2. **TP02** 0.0
3. **TP03** 0.0
4. **TP07** 0.0
5. **TP12** 0.0
6. **TP05** 2.0
7. **TP11** 2.6
8. **TP06** 9.6
9. **TP10** 23.1
10. **TP08** 127.6
11. **TP09** 156.5
12. **TP04** 194.5

### Latency mean (lower is better, delivered only)

1. **TP05** 127 s
2. **TP10** 1673 s
3. **TP02** 2645 s
4. **TP01** 2766 s
5. **TP06** 2802 s
6. **TP11** 2883 s
7. **TP12** 2939 s
8. **TP03** 2987 s
9. **TP07** 3010 s
10. **TP08** 3093 s
11. **TP04** 3591 s
12. **TP09** 3711 s

## Comparison vs TP01 (paired median relative delta)

| TP | Δ delivery | Δ overhead | Δ drop | Δ n_created | Δ t_median_frac |
|----|------------|------------|--------|-------------|-----------------|
| TP02 | +0.3% | +0.3% | -100.0% | -80.2% | -1.2% |
| TP03 | -0.2% | -0.5% | -100.0% | +358.7% | -0.1% |
| TP04 | -29.8% | +531.2% | -50.5% | -62.9% | +0.6% |
| TP05 | -95.3% | -13.8% | -98.9% | +0.0% | +0.0% |
| TP06 | +1.7% | +11.5% | -15.4% | +101.2% | -0.4% |
| TP07 | +9.2% | +0.3% | +40.4% | -25.1% | -51.9% |
| TP08 | -10.3% | +255.0% | -28.3% | +101.2% | -0.4% |
| TP09 | -21.6% | +428.0% | +37.2% | +19.8% | +0.0% |
| TP10 | -52.0% | +4.4% | -92.0% | +1174.2% | -0.1% |
| TP11 | -0.0% | +0.1% | -25.8% | +101.2% | -0.4% |
| TP12 | +1.0% | -0.1% | -0.5% | +0.8% | +0.7% |

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

- None flagged as blocked/needs_adjustment by intent rules.
- **R1_Rural_SparseSPMM**, **R11_SpeedExtremeLow:** zero delivery across many TPs (sparse/disconnected bases).
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

- **TP10** (`partial`): 0 zero-delivery, 0 missing output.

## Per-TP KPI summary

See [`traffic_profile_kpi_summary.csv`](../data/traffic_profile_kpi_summary.csv).

| TP | primary | secondary | cost | stress | validation |
|----|---------|-----------|------|--------|------------|
| TP01 | delivery_ratio | latency_mean | overhead_ratio | drop_ratio | validated |
| TP02 | n_created | delivery_ratio | overhead_ratio | drop_ratio | validated |
| TP03 | overhead_ratio | delivery_ratio | total_encounters | drop_ratio | validated |
| TP04 | drop_ratio | delivery_ratio | overhead_ratio | latency_mean | validated |
| TP05 | delivery_ratio | latency_mean | overhead_ratio | drop_ratio | validated |
| TP06 | delivery_ratio | latency_mean | overhead_ratio | popularity_top10_ratio | validated |
| TP07 | delivery_ratio | t_median_frac | overhead_ratio | latency_mean | validated |
| TP08 | popularity_top10_ratio | delivery_ratio | overhead_ratio | drop_ratio | validated |
| TP09 | drop_ratio | delivery_ratio | overhead_ratio | latency_mean | validated |
| TP10 | delivery_ratio | n_created | overhead_ratio | drop_ratio | partial |
| TP11 | delivery_ratio | overhead_ratio | latency_mean | drop_ratio | validated |
| TP12 | delivery_ratio | overhead_ratio | latency_mean | drop_ratio | validated |

## Cross-references

- [`tp_validation_report.md`](tp_validation_report.md)
- [`corpus_v1_benchmark_validation.md`](corpus_v1_benchmark_validation.md)
- [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)
- [`traffic_profile_stats.csv`](../data/traffic_profile_stats.csv)
