# Paper figures and tables index (corpus_v1)

Generated: 2026-05-27 18:12 UTC

**Corpus:** corpus_v1 — 540 simulations (diversity scope 540).
**Diversity validation:** PASS
**Benchmark outputs (570):** output_metrics=566 (OK)

| filename | type | data_source | generator_script | description | scientific_message | paper_section | status |
|----------|------|-------------|------------------|-------------|--------------------|---------------|--------|
| ablation_pairs_high_bar.png | main | ablation_metrics.csv | run_analysis.py --phase figures_paper | Bar chart: % scenario pairs with \|r\|≥0.7 for reduced_17, core_23, full_46. | Core-23 reduces redundant pairs vs full-46 without losing diversity. | Methods / Feature ablation | lista |
| ablation_silhouette_bar.png | main | ablation_metrics.csv | run_analysis.py --phase figures_paper | Silhouette (Ward k=7) per feature set in ablation. | Core-23 yields best cluster separation among ablated sets. | Methods / Feature ablation | lista |
| corpus_overview_paper.png | main | corpus_v1/manifest.csv | build_paper_figures_tables_index.py | Stacked bar: 540 simulations = 45 bases × 12 TPs across 6 environmental families. | Benchmark scale and family×TP factorial design of corpus_v1. | Methods / Benchmark design | lista |
| heatmap_feature_feature_core.png | main | feature_feature_correlation_core.csv | run_analysis.py --phase figures_paper | 23×23 heatmap of correlations between core features. | Within-feature redundancy is localized; core set is not orthogonal but manageable. | Supplementary / Feature redundancy | lista |
| histogram_correlations_pearson_paper.png | main | correlation_pearson.csv | run_analysis.py --phase figures_paper | Histogram of off-diagonal Pearson r between scenario Z-vectors (core feature space). | Most scenario pairs are weakly correlated; diversity criterion (few pairs \|r\|≥0.7) is met. | Methods / Corpus diversity | lista |
| outputs_boxplot_by_tp_paper.png | main | output_metrics.csv, manifest.csv | run_figures_aggregated.py (promoted) | Boxplots of delivery, latency, overhead, drop by Traffic Profile (12 TPs). | Traffic profiles induce distinct output regimes (stress vs baseline vs burst). | Results / Output metrics by TP | revisar |
| pca_by_cluster.png | main | features_normalized.csv, cluster_assignments.csv | run_analysis.py --phase figures_paper | PCA 2D colored by Ward clustering (k=7). | Unsupervised clusters align partially with families, supporting benchmark stratification. | Results / Clustering | lista |
| pca_by_family.png | main | features_normalized.csv, manifest family | run_analysis.py --phase figures_paper | PCA 2D of normalized features colored by scenario family. | Seven families occupy distinct regions of the input feature space. | Results / Feature space structure | lista |
| histogram_correlations_outputs_paper.png | supplementary | output_metrics.csv | run_analysis.py --phase figures_paper | Histogram of Pearson r between output metric vectors across scenarios. | Outputs are not trivially collinear across the benchmark scenarios. | Supplementary / Output diversity | lista |
| histogram_correlations_spearman_paper.png | supplementary | correlation_spearman.csv | run_analysis.py --phase figures_paper | Spearman rank correlation histogram between scenario vectors. | Robustness check: rank correlations show similar diversity pattern. | Supplementary / Correlation robustness | lista |
| message_creation_time_by_tp_paper.png | supplementary | message_creation_time_summary.csv | analyze_message_creation_times.py (promoted) | Boxplot of median normalized message creation time per TP. | TP07 concentrates traffic early; full-window TPs show ~uniform creation (median ~0.5). | Supplementary / Traffic timing | lista |
| protocol_comparison_placeholder.png | supplementary | N/A (future multi-protocol runs) | build_paper_figures_tables_index.py | Placeholder for routing-protocol comparison (not yet simulated). | Future work: compare Epidemic with PRoPHET, MaxProp, etc. on corpus_v1 splits. | Discussion / Future work | lista |
| spatial_coverage_by_family_paper.png | supplementary | spatial_occupancy_metrics.csv | run_figures_aggregated.py (promoted) | Spatial grid coverage distribution by family. | Mobility/map regimes differ in explored world fraction (WDM vs open map). | Supplementary / Spatial mobility | revisar |
| table_ablation_metrics_en.md | table | ablation_metrics.csv | run_analysis.py --phase tables_paper | Ablation 17 vs 23 vs 46 features. | Core-23 balances redundancy reduction and cluster quality. | Methods / Ablation | lista |
| table_ablation_metrics_es.md | table | ablation_metrics.csv | run_analysis.py --phase tables_paper | Spanish ablation table. | Same as EN. | Methods / Ablation (ES draft) | lista |
| table_core_vs_extended_en.md | table | internal/03-feature_fichas_tecnicas.md, features_normalized.csv | run_analysis.py --phase tables_paper | Core 23 vs extended features with category and rationale. | Transparent feature selection for scenario characterization. | Methods / Features | lista |
| table_core_vs_extended_es.md | table | internal/03-feature_fichas_tecnicas.md | run_analysis.py --phase tables_paper | Spanish version of core vs extended features. | Same as EN table. | Methods / Features (ES draft) | lista |
| table_diversity_criteria_en.md | table | analysis/data, reports/ | run_analysis.py --phase tables_paper | table_diversity_criteria_en |  | Methods | lista |
| table_diversity_metrics_en.md | table | correlation_report.txt, correlation_core23_report.txt, cluster_assignments*.csv | run_analysis.py --phase tables_paper | Diversity metrics for full_46 and core_23 spaces (n=540). | Quantitative evidence that the corpus meets diversity thresholds. | Results / Diversity | lista |
| table_diversity_metrics_es.md | table | correlation_report.txt, correlation_core23_report.txt | run_analysis.py --phase tables_paper | Spanish diversity metrics table. | Same as EN. | Results / Diversity (ES draft) | lista |
| table_families_en.md | table | .wiki-clone/04-Scenario-Families.md | run_analysis.py --phase tables_paper | Six environmental families + stress lab (base counts per family). | Taxonomy of mobility/traffic regimes in the benchmark. | Methods / Scenario families | lista |
| table_families_es.md | table | .wiki-clone/04-Scenario-Families.md | run_analysis.py --phase tables_paper | Spanish families table. | Same as EN. | Methods / Families (ES draft) | lista |

## Regeneration commands

```bash
scenarios/analysis/.venv/bin/python scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase figures_paper
scenarios/analysis/.venv/bin/python scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase tables_paper
scenarios/analysis/.venv/bin/python scenarios/analysis/run_figures_aggregated.py --corpus corpus_v1
scenarios/analysis/.venv/bin/python scenarios/analysis/build_paper_figures_tables_index.py
```

Canonical results: [`reports/RESULTADOS_ACTUALES.md`](../../reports/RESULTADOS_ACTUALES.md).
