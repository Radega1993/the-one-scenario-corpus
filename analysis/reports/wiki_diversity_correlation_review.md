# Wiki diversity and correlation — technical review

**Date:** 2026-05-28  
**Corpus:** `corpus_v1` (environmental only, `--no-stress`)  
**Scenarios analyzed:** **540** (6 environmental families × 12 Traffic Profiles)  
**Backup:** `scenarios/.wiki-clone/_backup_before_diversity_page_20260528_214741/`

## Commands executed

From repository root, using project virtualenv (`venv/bin/python`):

```bash
cd /home/raul/Documents/the-one
for phase in features features_report normalize correlation feature_correlation ablation figures figures_paper tables_paper; do
  venv/bin/python scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase "$phase"
done
```

**Note:** System `python3` lacks `pandas`; use `venv/bin/python` (see `requirements.txt`).

## Script fix (documented)

- **File:** `scenarios/analysis/run_analysis.py`
- **Change:** `_parse_ablation_line()` regex group indices for `pairs_ge`, `pct`, `silhouette` when CSV fallback parses `ablation_report.txt` (groups 4–6, not 5–7).
- **Reason:** Without `pandas`, `run_phase_results_actuales()` crashed after `--phase features`.

## Files regenerated

### Data (`scenarios/analysis/data/`)

All required CSVs present: `features.csv`, `features_normalized.csv`, `features_reduced.csv`, `features_core.csv`, `normalization_params.csv`, `correlation_pearson.csv`, `correlation_spearman.csv`, `distance_cosine.csv`, `distance_euclidean.csv`, `correlation_pearson_core23.csv`, `distance_cosine_core23.csv`, `feature_feature_correlation_core.csv`, `ablation_metrics.csv`, `cluster_assignments.csv`, `cluster_assignments_core23.csv`.

New: `diversity_correlation_wiki_summary.csv`, `wiki_diversity_correlation_review.csv`.

### Reports

| Report | Path |
|--------|------|
| Canonical summary | `scenarios/analysis/reports/RESULTADOS_ACTUALES.md` |
| Pipeline reports | `scenarios/analysis/reports/pipeline/*.txt`, `features_report.md` |

### Figures (PNG, wiki-linkable)

| Figure | Path |
|--------|------|
| Pearson histogram | `figures/histogram_correlations_pearson.png` |
| Spearman histogram | `figures/histogram_correlations_spearman.png` |
| Feature–feature heatmap | `figures/heatmap_feature_feature_core.png` |
| Block Pearson heatmap | `figures/aggregated/pearson_block_heatmap_ordered.png` |
| Core-23 heatmap | `figures/by_space/heatmap_pearson_core_23.png` |
| Ablation histogram compare | `figures/aggregated/correlation_ablation_histogram_compare.png` |
| Ablation bars | `figures/paper/main/ablation_pairs_high_bar.png`, `ablation_silhouette_bar.png` |
| PCA by family | `figures/paper/main/pca_by_family.png` |
| Paper Pearson histogram | `figures/paper/main/histogram_correlations_pearson_paper.png` |

### Figures not regenerated this run

- `figures/heatmap_pearson.png` — full N×N heatmap skipped when n=540 (`figures` phase default). Pre-existing file retained; wiki uses block/curated heatmaps instead.

## Main metrics by feature space

| Space | Features | max \|r\| | Pairs \|r\| ≥ 0.7 | % pairs | Silhouette (Ward k=7) |
|-------|----------|----------|-------------------|---------|----------------------|
| **Reduced-17** | 17 | 1.0 | 7 425 | 5.1% | 0.3355 |
| **Core-23** | 23 | 1.0 | 5 029 | 3.5% | 0.3045 |
| **Extended-46** | 46 | 1.0 | 3 346 | 2.3% | 0.2375 |

**Extended-46 global (Pearson / Spearman / geometry):**

- Pearson: mean \|r\| = 0.2208; 3 346 pairs ≥ 0.7 (2.3%); 97.7% of pairs below 0.7 (criterion met).
- Spearman: mean \|r\| = 0.2906; 7 452 pairs ≥ 0.7 — more high-similarity pairs than Pearson (rank-order redundancy).
- Cosine distance: min ≈ 0, mean 0.9974; 477 pairs with cos_dist &lt; 0.05.
- Euclidean: min 0, mean 7.2440.
- Clusters (Ward k=7): sizes 101, 24, 55, 56, 52, 12, 240.

**Feature–feature (core 23):** 1 pair with \|r\| ≥ 0.9 — `mm_WDM ↔ mm_Bus` (r = 0.9354).

**Known high-redundancy pattern:** TP06 (OneToMany) vs TP11 (ManyToOne) often \|r\| = 1.0 per base scenario (identical feature vectors in Z-space).

## Warnings

- `max |r| = 1.0` in all three spaces — near-duplicate scenario pairs exist; interpret diversity together with simulation outputs.
- Extended-46 silhouette (0.2375) below informal target 0.3; acceptable for a realistic benchmark (clusters are validation, not design goal).
- Feature–feature report prints `max |r| off-diagonal = nan` (pandas NaN propagation); actual max pair is documented above.

## Obsolete references detected (outside new wiki page)

| Location | Issue | Action |
|----------|-------|--------|
| `analysis/data/paper_freeze_checklist.csv` | FEAT-02 mentions n=720 | Report only; not updated (out of wiki scope) |
| `analysis/README.es.md` | Mentions 570 for diversity in one line | Report only |
| `06-Traffic-Profiles.md` | `msgTtl` value 7200 | Legitimate parameter, not corpus size |
| `Home.md`, `03-Installation.md` | Legacy notes for corpus_v2 / HelsinkiMedium | Intentional historical warnings |

**Not used as active facts:** corpus_v2, 720 scenarios, HelsinkiMedium, “seven environmental families”.

## Recommendation

| Question | Answer |
|----------|--------|
| Ready for wiki documentation? | **Yes** — metrics and figures regenerated on corpus_v1 (n=540). |
| Ready for paper? | **Yes with caveats** — use **Core-23** as primary interpretable space; cite Extended-46 for robustness; disclose TP06/TP11 perfect correlations and feature `mm_WDM`/`mm_Bus` dependency. |
| Pending before paper? | Cross-check simulation KPIs (delivery, overhead) complement geometric diversity; optional separate stress_controls analysis with `--include-stress`. |

## Wiki deliverables

- `scenarios/.wiki-clone/07-Diversity-and-Correlation-Demonstration.md` (new)
- `scenarios/.wiki-clone/Home.md` (navigation link)
- `scenarios/.wiki-clone/04-Usage.md` (analysis cross-link)
- Inventory: `scenarios/analysis/data/wiki_diversity_correlation_review.csv`
