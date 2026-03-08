# Figuras clave e informes

**Español** | [English](Figures)

---

Todas las figuras se generan con `run_analysis.py --phase figures` (y `outputs` para el heatmap de outputs). Están en **`scenarios/analysis/figures/`** (PNG y PDF). Los enlaces apuntan al repo; si la wiki se publica desde un clon, puedes subir estas imágenes a la wiki o usar las URLs raw.

**Ruta en el repo:** `scenarios/analysis/figures/`  
**URL raw:** `https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/<nombre>.png`

---

## 1. Heatmap — Pearson (vectores de features)

Matriz de correlación entre **vectores de features** de escenarios (70×70). Cada celda es el r de Pearson entre dos escenarios. Rojo = correlación positiva alta; azul = negativa. Valores altos fuera de la diagonal indican pares linealmente similares en el espacio de parámetros.

![Heatmap Pearson](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/heatmap_pearson.png)

*Fichero:* `heatmap_pearson.png` | [Ver en el repo](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/scenarios/analysis/figures/heatmap_pearson.png)

---

## 2. Heatmap — Spearman (vectores de features)

Igual que el anterior pero con correlación de **Spearman** (rangos). Útil para comprobar robustez ante relaciones monótonas no lineales.

![Heatmap Spearman](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/heatmap_spearman.png)

*Fichero:* `heatmap_spearman.png` | [Ver en el repo](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/scenarios/analysis/figures/heatmap_spearman.png)

---

## 3. Histograma — correlaciones Pearson

Distribución del **|r| de Pearson** entre todos los pares de escenarios (2415 pares). Muestra cuántos pares caen en cada intervalo. Objetivo: la mayor masa por debajo de 0,7.

![Histograma Pearson](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/histogram_correlations_pearson.png)

*Fichero:* `histogram_correlations_pearson.png` | [Ver en el repo](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/scenarios/analysis/figures/histogram_correlations_pearson.png)

---

## 4. Histograma — correlaciones Spearman

Distribución del **|r| de Spearman**. Comparar con Pearson para ver si la correlación de rangos se reparte de forma similar.

![Histograma Spearman](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/histogram_correlations_spearman.png)

*Fichero:* `histogram_correlations_spearman.png` | [Ver en el repo](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/scenarios/analysis/figures/histogram_correlations_spearman.png)

---

## 5. Scatter PCA — proyección 2D

**Primeras dos componentes principales** de la matriz de features normalizada Z. Cada punto es un escenario. Muestra la distribución en el espacio de features; se ven clusters y valores atípicos.

![Scatter PCA](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/scatter_pca_regression.png)

*Fichero:* `scatter_pca_regression.png` | [Ver en el repo](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/scenarios/analysis/figures/scatter_pca_regression.png)

---

## 6. Scatter — par con máximo |r|

Los **dos escenarios** con **mayor |r| de Pearson** (par más correlacionado). Features normalizados de un escenario en el eje x y del otro en el y. Puntos cerca de la diagonal indican fuerte acuerdo lineal.

![Scatter par max r](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/scatter_max_r_pair_regression.png)

*Fichero:* `scatter_max_r_pair_regression.png` | [Ver en el repo](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/scenarios/analysis/figures/scatter_max_r_pair_regression.png)

---

## 7. Heatmap — Pearson (métricas de salida)

Matriz de correlación entre **vectores de salida** de escenarios (delivery ratio, latency mean, overhead ratio, drop ratio del ONE). Muestra si el *comportamiento* (no solo los parámetros) es redundante.

![Heatmap outputs](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/heatmap_pearson_outputs.png)

*Fichero:* `heatmap_pearson_outputs.png` | [Ver en el repo](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/scenarios/analysis/figures/heatmap_pearson_outputs.png)

---

## Informes (analysis/reports/)

| Fichero | Descripción |
|---------|-------------|
| **correlation_report.txt** | Max \|r\|, media \|r\|, pares con \|r\| ≥ 0,7, resumen Spearman, distancias coseno/euclídea, criterios de diversidad, pares más correlacionados, FDR/Bonferroni. |
| **multiple_comparisons_report.txt** | Rechazos y pares con \|r\| alto significativo tras FDR y Bonferroni. |
| **clustering_report.txt** | Resumen del clustering Ward (p. ej. k=7), silhouette. |
| **outputs_correlation_report.txt** | Correlación y distancias sobre vectores de salida. |
| **scenarios_to_diversify.txt** | Lista de escenarios a diversificar (alta correlación o clusters densos). |
| **observaciones_correlacion.md** | Notas sobre correlación y criterios de benchmark. |
| **plan_radical_scenarios.md** | Plan de escenarios radicales (estructura espacial, TTL, buffer, etc.). |
| **cambios_diversificacion_top_pares.md** | Registro de cambios de diversificación en los pares top. |

Enlaces: [reports/ en el repo](https://github.com/Radega1993/the-one-scenario-corpus/tree/main/scenarios/analysis/reports)

---

## Datos (analysis/data/)

Principales CSV generados por el pipeline:

| Fichero | Descripción |
|---------|-------------|
| **features.csv** | Una fila por escenario, columnas = features (33). |
| **features_normalized.csv** | Features normalizados (z-score). |
| **normalization_params.csv** | Media y desv. típica por feature. |
| **correlation_pearson.csv**, **correlation_spearman.csv** | Matrices 70×70 (vectores de features). |
| **distance_cosine.csv**, **distance_euclidean.csv** | Matrices 70×70 de distancias. |
| **cluster_assignments.csv** | Escenario → cluster (Ward). |
| **output_metrics.csv** | Delivery ratio, latency mean, overhead ratio, drop ratio por escenario. |
| **correlation_pearson_outputs.csv**, **distance_*_outputs.csv** | Correlación/distancia sobre vectores de salida. |

Enlaces: [data/ en el repo](https://github.com/Radega1993/the-one-scenario-corpus/tree/main/scenarios/analysis/data)

---

## Ver también

- [Resumen de resultados](Results-overview-es) — Métricas principales e interpretación  
- [Metodología](Methodology-es) — Cómo se generan las figuras  
- [Quickstart](Quickstart-es) — Regenerar con `--phase figures` y `--phase outputs`  
