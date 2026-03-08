# Resumen de resultados

**Español** | [English](Results-overview)

---

Resumen de los resultados principales y enlaces a páginas más detalladas. Todos los números corresponden a **corpus_v1** con **70 escenarios** y **33 features**.

---

## Espacio de features

| Concepto | Valor |
|----------|--------|
| Escenarios (n) | 70 |
| Features (d) | 33 |
| Normalización | Z-score por feature |

---

## Resultados de correlación (Pearson)

| Métrica | Valor |
|--------|--------|
| **max \|r\|** | 0,9475 |
| **media \|r\|** | 0,2842 |
| **Total pares** | 2415 |
| **Pares con \|r\| ≥ 0,7** | 153 (6,3 %) |
| **Pares con \|r\| < 0,7** | 93,7 % |
| **Objetivo** | ≥95 % con \|r\| < 0,7 |
| **¿Criterio cumplido?** | No (93,7 % < 95 %) |

---

## Spearman (correlación de rangos)

| Métrica | Valor |
|--------|--------|
| max \|r\| | 0,9980 |
| media \|r\| | 0,3920 |
| Pares con \|r\| ≥ 0,7 | 275 |

---

## Distancia y similitud

| Métrica | Valor |
|--------|--------|
| **Distancia coseno** | mín = 0,0534, media = 0,3003 |
| **Distancia euclídea** | mín = 0,8761, media = 6,8000 |
| **Pares con cos_dist < 0,05** | 0 (objetivo: 0) |
| **Objetivo mín. coseno** | > 0,05 ✓ |

---

## Clustering (Ward, k=7)

| Métrica | Valor |
|--------|--------|
| Silhouette | 0,0000 |
| Objetivo | > 0,3 |
| Uso | Asignaciones en `cluster_assignments.csv` |

---

## Comparaciones múltiples

- **FDR (Benjamini–Hochberg, α=0,05):** 609 rechazos; 153 pares con \|r\| ≥ 0,7 y significativos.
- **Bonferroni (α/2415):** 181 rechazos; 153 pares con \|r\| ≥ 0,7 y significativos.
- **Objetivo:** Ningún par con \|r\| alto y significativo tras corrección — **no cumplido** (153 pares).

---

## Pares más correlacionados (ejemplos)

*(De correlation_report.txt; se muestran 5.)*

1. V4_MixedBusPed ↔ V5_RushHourBusDensity — r = 0,9475  
2. U3_NightlifeClusters ↔ C5_Festival_MultiHotspots — r = 0,9420  
3. T10_HighRateLowSpeed ↔ T15_TransmitSpeed_256k — r = 0,9397  
4. U2_RetailHeavy ↔ V6_CarOwnership_0 — r = 0,9392  
5. S3_PeriodicMeetings ↔ T5_VeryLongTtl — r = 0,9354  

Lista completa y estado de diversificación: ver `analysis/reports/correlation_report.txt` y [Estado de diversidad](Diversity-status-es).

---

## Gráficos clave

Las 7 figuras (heatmaps Pearson/Spearman, histogramas Pearson/Spearman, scatter PCA, scatter par max-|r|, heatmap outputs) se listan y muestran con leyendas en **[Figuras](Figures-es)**. En el repo: `scenarios/analysis/figures/`.

| Figura | Fichero |
|--------|---------|
| Heatmap Pearson (features) | heatmap_pearson.png |
| Heatmap Spearman (features) | heatmap_spearman.png |
| Histograma Pearson | histogram_correlations_pearson.png |
| Histograma Spearman | histogram_correlations_spearman.png |
| Scatter PCA | scatter_pca_regression.png |
| Scatter par max-|r| | scatter_max_r_pair_regression.png |
| Heatmap Pearson (outputs) | heatmap_pearson_outputs.png |  

---

## Subpáginas (por desarrollar)

- [Resultados del espacio de features](Feature-space-results-es)  
- [Resultados de correlación](Correlation-results-es)  
- [Resultados de distancia y similitud](Distance-results-es)  
- [Resultados de clustering](Clustering-results-es)  
- [Resultados de métricas de salida](Output-metrics-results-es)  
- [Estado de diversidad](Diversity-status-es)  

---

## Ver también

- [Metodología](Methodology-es) — Cómo se obtienen estos resultados  
- [Quickstart](Quickstart-es) — Cómo regenerarlos  
- [Visión del corpus](Corpus-overview-es) — Familias de escenarios  
