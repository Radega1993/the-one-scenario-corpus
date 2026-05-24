# Results overview

**English** | [Español](Results-overview-es)

---

Summary of current analysis results for **corpus_v1** and latest scenario-fix status.  
Reference source: [`analysis/reports/RESULTADOS_ACTUALES.md`](../../analysis/reports/RESULTADOS_ACTUALES.md).

---

## Feature space

| Item | Value |
|------|--------|
| Scenarios (n) | 60 |
| Core features (diversity reference) | 23 |
| Extended features (exploration) | 46 |
| Normalisation | Z-score per feature (NaN -> 0 after z-score) |

---

## Correlation results (final optimized freeze)

### Core 23 (diversity reference)

| Metric | Value |
|--------|--------|
| max \|r\| | 0.9829 |
| Mean \|r\| | 0.2065 |
| Total pairs | 1770 |
| Pairs with \|r\| >= 0.7 | 58 (3.3%) |
| Pairs with \|r\| < 0.7 | 96.7% |
| Cosine distance (min) | 0.0152 |
| Silhouette (Ward k=7) | 0.2681 |

Source: `analysis/reports/correlation_core23_report.txt`.

### Full 46 features

| Metric | Value |
|--------|--------|
| max \|r\| | 0.9377 |
| Mean \|r\| | 0.1906 |
| Total pairs | 1770 |
| Pairs with \|r\| >= 0.7 | 46 (2.6%) |
| Pairs with \|r\| < 0.7 | 97.4% |
| Cosine distance (min) | 0.0620 |
| Silhouette (Ward k=7) | 0.2929 |
| Criterion (>=95% with \|r\| < 0.7) | Met |

Source: `analysis/reports/correlation_report.txt`.

---

## Ablation (17 vs 23 vs 46)

| Set | max \|r\| | mean \|r\| | pairs >= 0.7 | silhouette |
|-----|-----------|------------|---------------|------------|
| reduced_17 | 0.9863 | 0.2324 | 63 (3.6%) | 0.2215 |
| core_23 | 0.9829 | 0.2065 | 58 (3.3%) | 0.2681 |
| full_46 | 0.9377 | 0.1906 | 46 (2.6%) | 0.2929 |

Source: `analysis/reports/ablation_report.txt`.

---

## Baseline initial vs final optimized

| Metric | Initial baseline | Final optimized |
|--------|------------------|-----------------|
| Full-46 pairs with \|r\| >= 0.7 | 57 (3.2%) | 46 (2.6%) |
| Core-23 pairs with \|r\| >= 0.7 | 93 (5.3%) | 58 (3.3%) |
| Full-46 min cosine | 0.0585 | 0.0620 |
| Full-46 silhouette | 0.2924 | 0.2929 |

Freeze framing: this is a **stable, publishable baseline**, not an optimal final corpus.

---

## Declared limitations

- Residual high-correlation pairs remain in both spaces.
- Core-23 silhouette is moderate (`0.2681`) after optimization.
- A residual high feature-feature dependency remains: `mm_WDM <-> mm_Bus = 0.9393`.

---

## Scenario-fix status (map bounds)

Recent simulation errors caused by `Map node ... out of world bounds` were fixed by adjusting `MovementModel.worldSize` in map-based scenarios:

- `V1_TaxiLow_HelsinkiMedium` -> `8400, 7504`
- `V2_TaxiHigh_HelsinkiMedium` -> `8400, 7504`
- `V3_BusOnlyCarriers_HelsinkiMedium` -> `8400, 7504`
- `V4_CarOwnership_0_HelsinkiMedium` -> `8400, 7504`
- `R4_ParkRangers_HelsinkiMedium` -> `8400, 7504`
- `D5_UAVMule_FastRoute_HelsinkiMedium` -> `8400, 7504`

The last full user validation reported **56/60 OK, 4 failing** before the final updates of `V1`, `V2`, `V4`, and `R4`. Re-run full simulation to confirm final **60/60 OK**.

---

## See also

- [Final-frozen-results](Final-frozen-results)
- [Optimization-history](Optimization-history)
- [Feature-feature-analysis](Feature-feature-analysis)
- [Clustering-analysis](Clustering-analysis)
- [Output-space-analysis](Output-space-analysis)
- [Methodology](Methodology)
- [Figures](Figures)
- [Corpus overview](Corpus-overview)
