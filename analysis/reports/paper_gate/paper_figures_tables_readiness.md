# Paper figures and tables readiness (corpus_v2)

Generated: 2026-05-24 12:09 UTC

## Executive summary

- **Corpus:** corpus_v2, N=720 simulations.
- **Data validation:** correlation_pearson=720, output_metrics=720.
- **Policy:** All figures must trace to current `analysis/data/*.csv` (720 rows), not corpus_v1 or 60-scenario pilots.

## Figures ready (main)

- `ablation_pairs_high_bar.png` — Methods / Feature ablation
- `ablation_silhouette_bar.png` — Methods / Feature ablation
- `corpus_overview_paper.png` — Methods / Benchmark design
- `heatmap_feature_feature_core.png` — Supplementary / Feature redundancy
- `histogram_correlations_pearson_paper.png` — Methods / Corpus diversity
- `outputs_boxplot_by_tp_paper.png` — Results / Output metrics by TP
- `pca_by_cluster.png` — Results / Clustering
- `pca_by_family.png` — Results / Feature space structure

## Figures to review or regenerate (main)


## Figures ready (supplementary)

- `histogram_correlations_outputs_paper.png` — Supplementary / Output diversity
- `histogram_correlations_spearman_paper.png` — Supplementary / Correlation robustness
- `message_creation_time_by_tp_paper.png` — Supplementary / Traffic timing
- `protocol_comparison_placeholder.png` — Discussion / Future work

## Figures to review (supplementary)

- `spatial_coverage_by_family_paper.png` — **revisar**

## Tables ready

- `table_ablation_metrics_en.md`
- `table_ablation_metrics_es.md`
- `table_core_vs_extended_en.md`
- `table_core_vs_extended_es.md`
- `table_diversity_metrics_en.md`
- `table_diversity_metrics_es.md`
- `table_families_en.md`
- `table_families_es.md`

## Tables to regenerate


## Commands to regenerate

```bash
cd scenarios/analysis
.venv/bin/python run_analysis.py --corpus corpus_v2 --phase tables_paper
.venv/bin/python run_analysis.py --corpus corpus_v2 --phase figures_paper
.venv/bin/python run_figures_aggregated.py --corpus corpus_v2
.venv/bin/python build_paper_figures_tables_index.py
```

## Still missing for paper closure

1. **Routing protocol comparison** — placeholder only (`protocol_comparison_placeholder`); requires new simulations.
2. **Optional:** promote additional aggregated heatmaps (`outputs_heatmap_base_x_tp_*`) if space allows.
3. **README cleanup** — ensure all docs reference `corpus_v2`, not `corpus_v1`.

## Closure checklist

- [ ] 8–10 main figures (PNG+PDF) — current count: 8 indexed
- [ ] 4+ supplementary figures
- [ ] 4 EN tables regenerated with n=720 diversity metrics
- [ ] `FIGURES_AND_TABLES_INDEX.md` committed
- [ ] Cross-check numbers vs `RESULTADOS_ACTUALES.md`

## Promotion log

- Copied outputs_boxplot_by_tp.png -> figures/paper/main/outputs_boxplot_by_tp_paper.png
- Copied outputs_boxplot_by_tp.pdf -> figures/paper/main/outputs_boxplot_by_tp_paper.pdf
- Copied spatial_coverage_by_family.png -> figures/paper/supplementary/spatial_coverage_by_family_paper.png
- Copied spatial_coverage_by_family.pdf -> figures/paper/supplementary/spatial_coverage_by_family_paper.pdf
- Copied message_creation_time_boxplot_by_tp.png -> figures/paper/supplementary/message_creation_time_by_tp_paper.png
- Generated corpus_overview_paper
- Generated protocol_comparison_placeholder

## Cross-references

- [`FIGURES_AND_TABLES_INDEX.md`](../figures/paper/FIGURES_AND_TABLES_INDEX.md)
- [`figures/README.md`](../figures/README.md)
- [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)
