# Results overview

**English** | [Español](Results-overview-es)

---

Summary of the main results and links to more detailed pages. All numbers refer to **corpus_v1** with **70 scenarios** and **33 features**.

---

## Feature space

| Item | Value |
|------|--------|
| Scenarios (n) | 70 |
| Features (d) | 33 |
| Normalisation | Z-score per feature |

---

## Correlation results (Pearson)

| Metric | Value |
|--------|--------|
| **max \|r\|** | 0.9475 |
| **mean \|r\|** | 0.2842 |
| **Total pairs** | 2415 |
| **Pairs with \|r\| ≥ 0.7** | 153 (6.3%) |
| **Pairs with \|r\| < 0.7** | 93.7% |
| **Target** | ≥95% with \|r\| < 0.7 |
| **Criterion met?** | No (93.7% < 95%) |

---

## Spearman (rank correlation)

| Metric | Value |
|--------|--------|
| max \|r\| | 0.9980 |
| mean \|r\| | 0.3920 |
| Pairs with \|r\| ≥ 0.7 | 275 |

---

## Distance and similarity

| Metric | Value |
|--------|--------|
| **Cosine distance** | min = 0.0534, mean = 0.3003 |
| **Euclidean distance** | min = 0.8761, mean = 6.8000 |
| **Pairs with cos_dist < 0.05** | 0 (target: 0) |
| **Min cosine target** | > 0.05 ✓ |

---

## Clustering (Ward, k=7)

| Metric | Value |
|--------|--------|
| Silhouette | 0.0000 |
| Target | > 0.3 |
| Use | Cluster assignments in `cluster_assignments.csv` |

---

## Multiple comparisons

- **FDR (Benjamini–Hochberg, α=0.05):** 609 rejections; 153 pairs with \|r\| ≥ 0.7 and significant.
- **Bonferroni (α/2415):** 181 rejections; 153 pairs with \|r\| ≥ 0.7 and significant.
- **Goal:** No pair with high \|r\| and significant after correction — **not met** (153 such pairs).

---

## Top correlated pairs (examples)

*(From correlation_report.txt; max 5 shown.)*

1. V4_MixedBusPed ↔ V5_RushHourBusDensity — r = 0.9475  
2. U3_NightlifeClusters ↔ C5_Festival_MultiHotspots — r = 0.9420  
3. T10_HighRateLowSpeed ↔ T15_TransmitSpeed_256k — r = 0.9397  
4. U2_RetailHeavy ↔ V6_CarOwnership_0 — r = 0.9392  
5. S3_PeriodicMeetings ↔ T5_VeryLongTtl — r = 0.9354  

Full list and diversification status: see `analysis/reports/correlation_report.txt` and [Diversity status](Diversity-status).

---

## Key figures

All 7 figures (Pearson/Spearman heatmaps, Pearson/Spearman histograms, PCA scatter, max-|r| pair scatter, outputs heatmap) are listed and shown with captions on **[Figures](Figures)**. In the repo: `scenarios/analysis/figures/`.

| Figure | File |
|--------|------|
| Heatmap Pearson (features) | heatmap_pearson.png |
| Heatmap Spearman (features) | heatmap_spearman.png |
| Histogram Pearson | histogram_correlations_pearson.png |
| Histogram Spearman | histogram_correlations_spearman.png |
| PCA scatter | scatter_pca_regression.png |
| Scatter max-|r| pair | scatter_max_r_pair_regression.png |
| Heatmap Pearson (outputs) | heatmap_pearson_outputs.png |  

---

## Subpages (to be expanded)

- [Feature-space results](Feature-space-results) — Coverage, feature table  
- [Correlation results](Correlation-results) — Pearson, Spearman, interpretation  
- [Distance and similarity results](Distance-results) — Cosine, Euclidean  
- [Clustering results](Clustering-results) — Ward, clusters by family  
- [Output metrics results](Output-metrics-results) — Delivery, latency, overhead  
- [Diversity status](Diversity-status) — Pairs to diversify, actions taken  

---

## See also

- [Methodology](Methodology) — How these results are produced  
- [Quickstart](Quickstart) — How to regenerate them  
- [Corpus overview](Corpus-overview) — Scenario families  
