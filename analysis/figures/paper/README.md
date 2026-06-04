## Paper figures package (corpus_v1)

Generado con:

```bash
cd scenarios/analysis
.venv/bin/python run_analysis.py --corpus corpus_v1 --phase figures_paper
.venv/bin/python run_figures_aggregated.py --corpus corpus_v1
.venv/bin/python build_paper_figures_tables_index.py
```

Índice maestro: [`FIGURES_AND_TABLES_INDEX.md`](FIGURES_AND_TABLES_INDEX.md).

Regla: **no sobrescribe** nada en `scenarios/analysis/figures/` raíz (solo escribe en `paper/`).

### Main (`main/`)

- `histogram_correlations_pearson_paper.(png|pdf)`  
  Histograma de correlaciones Pearson con anotación de `n_pares` y `% |r|≥umbral`.
- `pca_by_family.(png|pdf)`  
  PCA 2D coloreado por familia (sin etiquetas por punto).
- `pca_by_cluster.(png|pdf)`  
  PCA 2D coloreado por cluster Ward k=7 (sin etiquetas por punto).
- `ablation_pairs_high_bar.(png|pdf)`  
  Ablación: % de pares con `|r|≥umbral` para `reduced_17`, `core_23`, `full_46`.
- `ablation_silhouette_bar.(png|pdf)`  
  Ablación: silhouette (Ward k=7) para `reduced_17`, `core_23`, `full_46`.
- `heatmap_feature_feature_core.(png|pdf)`  
  Heatmap feature–feature del core 23.

### Supplementary (`supplementary/`)

- `histogram_correlations_spearman_paper.(png|pdf)`  
  Histograma Spearman (robustez).
- `histogram_correlations_outputs_paper.(png|pdf)`  
  Distribución de correlaciones Pearson entre vectores de salida (delivery, latency, overhead, drops).
- `heatmap_pearson_outputs_paper.(png|pdf)`  
  Solo con `--include-full-heatmaps` y fase `outputs` previa (N×N; depuración).

### Trazabilidad a artefactos

Las figuras se generan exclusivamente a partir de:

- `analysis/data/correlation_pearson.csv`
- `analysis/data/correlation_spearman.csv` (si existe)
- `analysis/data/features_normalized.csv`
- `analysis/data/cluster_assignments.csv` (si existe)
- `analysis/data/ablation_metrics.csv` (si existe)
- `analysis/data/output_metrics.csv` (si existe)
- `analysis/data/feature_feature_correlation_core.csv` (si existe)
