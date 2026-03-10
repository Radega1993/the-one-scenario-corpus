# Guía: estado del proyecto, resultados, fórmulas y figuras

Documento de referencia para revisar la documentación, entender el estado actual del análisis del corpus de escenarios y decidir por dónde continuar.

---

## 1. Dónde está cada cosa (mapa rápido)

| Qué | Dónde |
|-----|--------|
| **Script principal** (extracción, normalización, correlación, figuras, ablación) | `scenarios/analysis/run_analysis.py` |
| **Datos crudos y derivados** | `scenarios/analysis/data/` |
| **Informes de texto** | `scenarios/analysis/reports/` |
| **Figuras (PNG/PDF)** | `scenarios/analysis/figures/` |
| **Metodología core vs extended (24 vs 46 features)** | `scenarios/analysis/docs/features_core_vs_extended.md` |
| **Decisión de features y settings no usados** | `scenarios/analysis/docs/features_decision.md`, `reports/features_report.md` |
| **README del análisis** | `scenarios/analysis/README.md` (EN), `README.es.md` (ES) |
| **Wiki (referencia pipeline, features, diversidad)** | `scenarios/.wiki-clone/` (03-reference, 04-results) |

---

## 2. Datos: qué hay y de dónde sale

### 2.1 Entrada

- **Corpus:** directorio con `.settings` (p. ej. `scenarios/corpus_v1`). Cada fichero = un escenario.
- **Número actual:** 70 escenarios, 46 features por escenario (tras sustituir Wx,Wy por world_area, aspect_ratio).

### 2.2 Archivos en `data/` (orden lógico del pipeline)

| Archivo | Origen | Contenido |
|---------|--------|-----------|
| `features.csv` | `--phase features` | Matriz **n×46**: una fila por escenario (índice = nombre), columnas = features en escala original (world_area, aspect_ratio, N, density, speed_mean, …). Valores NaN donde la feature no aplica (p. ej. workDayLength si no WDM). |
| `scenario_list.txt` | `--phase features` | Lista de rutas de los `.settings` procesados. |
| `features_normalized.csv` | `--phase normalize` | Matriz **n×46** en espacio z-score; **NaN sustituidos por 0** (política §4). |
| `normalization_params.csv` | `--phase normalize` | Por cada feature: `feature`, `mean`, `std` (media y desv. calculadas solo con no-NaN). |
| `features_core.csv` | `--phase normalize` | Submatriz **n×24** (solo las 24 features del core). Misma normalización (NaN→0). |
| `features_reduced.csv` | `--phase normalize` | Submatriz **n×17** (subconjunto mínimo para ablación). |
| `correlation_pearson.csv` | `--phase correlation` | Matriz **n×n**: correlación de Pearson **entre filas** (entre escenarios), r(S_i, S_k). |
| `correlation_pearson_core24.csv` | `--phase correlation` | Igual pero en espacio **core 24** (referencia investigación). |
| `correlation_core24_report.txt` | `--phase correlation` | Métricas y pares |r|≥0.7 **en core 24**. |
| `scenarios_to_diversify_core24.txt` | `--phase correlation` | Escenarios a diversificar **priorizados por core 24**. |
| `distance_cosine_core24.csv` | `--phase correlation` | Distancia coseno entre escenarios en espacio core 24. |
| `cluster_assignments_core24.csv` | `--phase correlation` | Cluster Ward k=7 en espacio core 24. |
| `correlation_spearman.csv` | `--phase correlation` | Idem con Spearman entre vectores de escenarios. |
| `correlation_pearson_pvalues.csv` | `--phase correlation` | Matriz n×n de p-values (H₀: ρ=0) para cada par. |
| `distance_cosine.csv` | `--phase correlation` | Matriz n×n: 1 − cos_sim entre filas de Z. |
| `distance_euclidean.csv` | `--phase correlation` | Matriz n×n: distancia euclídea entre filas de Z. |
| `cluster_assignments.csv` | `--phase correlation` | Columnas `scenario`, `cluster`: asignación Ward k=7. |
| `feature_feature_correlation_core.csv` | `--phase feature_correlation` | Matriz **24×24**: correlación **entre columnas** (entre features del core) sobre los n escenarios. |
| `ablation_metrics.csv` | `--phase ablation` | Una fila por conjunto (reduced_17, core_24, full_46): max_abs_r, mean_abs_r, pairs_r_above_threshold, total_pairs, pct_above, silhouette. |
| `output_metrics.csv` | manual o `--phase output_metrics` | Por escenario: delivery_ratio, latency_mean, overhead_ratio, drop_ratio (desde MessageStatsReport). |
| `output_metrics_normalized.csv` | `--phase outputs` | Esas métricas en z-score (para correlación entre vectores de salida). |
| `correlation_pearson_outputs.csv`, etc. | `--phase outputs` | Correlación/distancias entre escenarios usando vectores de **salida** (Y), no de features. |

---

## 3. Fórmulas y definiciones (implementadas en `run_analysis.py`)

### 3.1 Extracción de features

- **world_area** = Wx × Wy (m²), con Wx, Wy de `MovementModel.worldSize`.
- **aspect_ratio** = min(Wx, Wy) / max(Wx, Wy) ∈ (0, 1]. Si Wx o Wy no definidos → NaN.
- **density** = N / (Wx×Wy) × 10⁶ (proxy nodos/km²). No está en el core (redundante con N y world_area).
- Resto de features: ver `run_analysis.py` función `settings_to_reportable_features` y `FEATURE_METADATA`.

### 3.2 Normalización (política NaN según §4)

- Por cada columna j:
  - μ_j = media de la columna **solo sobre valores no-NaN**.
  - σ_j = desviación típica de la columna **solo sobre no-NaN**.
  - Z_{s,j} = (X_{s,j} − μ_j) / σ_j si σ_j > 0; si σ_j = 0 o NaN, Z_{s,j} = 0.
- **Después:** todos los NaN se sustituyen por **0** en Z (features condicionales = “neutras” fuera de su familia).
- Código: `zscore_normalize_per_feature()` en `run_analysis.py` (aprox. líneas 678–702).

### 3.3 Correlación entre escenarios (filas de Z)

- **Pearson r(S_i, S_k):** correlación lineal entre el vector fila i y el vector fila k (d componentes). Se usa la matriz Z ya con NaN→0; pandas `Z.T.corr()` (correlación entre columnas de Z.T = entre filas de Z).
- **Spearman:** misma idea sobre rangos de cada componente.
- **Distancia coseno:** para filas Z_i, Z_k:
  - cos_sim = (Z_i · Z_k) / (‖Z_i‖ ‖Z_k‖), normas L2 por fila; si norma = 0 se usa 1 para no dividir por cero.
  - **dist_coseno** = 1 − cos_sim (0 = idénticos, 2 = opuestos).
- **Distancia euclídea:** ‖Z_i − Z_k‖₂ (sobre el vector de d componentes; NaN ya son 0).

### 3.4 P-value para cada par (Pearson)

- Para un par (i, k) tenemos r y n = d (número de features).
- Bajo H₀: ρ = 0, el estadístico t = r √((n−2)/(1−r²)) sigue una t de Student con n−2 g.d.l.
- **p-value (bilateral)** = 2 (1 − F_t(|t|; n−2)). Código: `pearson_pvalue_from_r(r, n)`.

### 3.5 Corrección por comparaciones múltiples

- **FDR Benjamini–Hochberg:** se ordenan los m p-values; se rechaza H₀ para los k menores tales que p_(i) ≤ (i/m) α (α = 0.05 por defecto). Código: `benjamini_hochberg(pvalues_flat, alpha)`.
- **Bonferroni:** se rechaza H₀ si p < α/m (m = número de pares).

### 3.6 Silhouette (clustering)

- **Entrada:** matriz de distancias D (n×n) entre escenarios (en el código se usa `distance_cosine`) y etiquetas de cluster (Ward, k=7).
- Para cada punto i en cluster C:
  - a(i) = distancia media de i a los demás puntos **en el mismo cluster** (excluyendo i).
  - b(i) = distancia media de i al **cluster más cercano** distinto de C.
  - s(i) = (b(i) − a(i)) / max(a(i), b(i)); si el cluster tiene un solo punto, s(i) = 0.
- **Silhouette global** = media de s(i) sobre todos los puntos. Código: `silhouette_from_distance(D, labels)`.

### 3.7 Correlación feature–feature (core 24)

- **Entrada:** matriz Z_core de tamaño n×24 (filas = escenarios, columnas = 24 features del core).
- **Salida:** matriz 24×24 = correlación **entre columnas** (entre features) sobre los n escenarios. R_ff[j,k] = Pearson( columna j, columna k ). Código: `Z.corr()` en pandas sobre `features_core.csv`.

### 3.8 Ablación (17 vs 24 vs 46)

- Para cada conjunto de features (17, 24, 46) se toma la submatriz normalizada correspondiente (con NaN→0).
- Sobre esa matriz se calculan: **max |r|** entre pares de escenarios, **media |r|**, **número (y %) de pares con |r| ≥ 0.7**, y **Silhouette** (Ward k=7 sobre distancias coseno). No se usa correlación feature–feature aquí, solo correlación escenario–escenario.

---

## 4. Resultados numéricos actuales (referencia rápida)

- **Corpus:** 70 escenarios, 46 features (extended); core 24, reduced 17.
- **Correlación entre escenarios (full 46):**
  - max |r| = **0.9568**
  - media |r| = **0.2363**
  - Pares con |r| ≥ 0.7: **92 (3.8%)**; 96.2% con |r| < 0.7 → criterio ≥95% cumplido.
  - Distancia coseno: mín = **0.0402**, media = 1.006; **3 pares** con cos_dist < 0.05.
  - Silhouette (Ward k=7): **0.3329** (objetivo > 0.3 cumplido).
- **Feature–feature (core 24):** max |r| off-diagonal = **0.9651**; **1 par** con |r| ≥ 0.9: mm_WDM ↔ mm_Bus.
- **Ablación:**

| Conjunto   | d  | max\|r\| | media \|r\| | Pares \|r\|≥0.7 | Silhouette |
|------------|----|----------|-------------|-----------------|------------|
| reduced_17 | 17 | 1.0000   | 0.3070      | 245 (10.1%)     | 0.3839     |
| core_24    | 24 | 1.0000   | 0.2834      | 207 (8.6%)      | **0.4146** |
| full_46    | 46 | 0.9568   | 0.2363      | 92 (3.8%)       | 0.3329     |

*Fuente:* `reports/correlation_report.txt`, `reports/feature_feature_correlation_report.txt`, `reports/ablation_report.txt`, `data/ablation_metrics.csv`.

---

## 5. Figuras generadas (`--phase figures` y `feature_correlation`)

Todas en `scenarios/analysis/figures/`, en PNG y PDF salvo donde se indique.

| Figura | Cómo se genera | Para qué sirve |
|--------|----------------|----------------|
| **heatmap_pearson.png** | `imshow(R_pearson)` con colormap RdBu_r, vmin=-1, vmax=1; ejes = nombres de escenarios. R_pearson = correlación entre **filas** de Z (entre escenarios). | Ver qué pares de escenarios están más correlacionados (rojo/azul fuerte) y estructura global. |
| **heatmap_spearman.png** | Igual que la anterior con matriz de Spearman entre filas de Z. | Misma idea que Pearson pero robusto a no linealidad (rangos). |
| **histogram_correlations_pearson.png** | Histograma de los r de Pearson de todos los pares (triángulo superior de R); líneas verticales en ±0.7. | Ver distribución de correlaciones; cuántos pares caen por encima del umbral. |
| **histogram_correlations_spearman.png** | Igual para los r de Spearman. | Idem en versión Spearman. |
| **scatter_pca_regression.png** | SVD de Z centrado → PC1, PC2 por escenario; scatter (PC1, PC2) + recta de regresión PC2 ~ PC1; R² en leyenda. | Ver si los escenarios se alinean en una dirección (R² alto = mucho colineales); diversidad geométrica. |
| **scatter_max_r_pair_regression.png** | Se toma el **par de escenarios con mayor \|r\|**; eje X = valores del escenario i por feature, eje Y = valores del escenario k; scatter + recta de regresión. | Ilustrar el par más correlacionado: puntos sobre la recta = correlación lineal fuerte. |
| **heatmap_feature_feature_core.png** | Matriz 24×24 de correlación **entre features** del core (columnas de Z_core); ejes = nombres de features; RdBu_r. Generada en `--phase feature_correlation`. | Ver redundancia entre features del core (objetivo: no pares |r| > 0.9). |
| **heatmap_pearson_outputs.png** | Igual que heatmap_pearson pero sobre la matriz de **vectores de salida** Y (delivery_ratio, latency_mean, etc.). Generada en `--phase outputs`. | Ver si los resultados de simulación (outputs) están muy correlacionados entre escenarios. |

---

## 6. Informes de texto en `reports/`

| Informe | Contenido principal |
|---------|----------------------|
| `correlation_report.txt` | max/mean \|r\|, pares ≥0.7, Spearman, distancias coseno/euclídea, Silhouette, lista de pares con \|r\|≥0.7, criterio 95%, FDR/Bonferroni. |
| `multiple_comparisons_report.txt` | Resumen FDR y Bonferroni: rechazos y pares con \|r\| alto y significativos. |
| `feature_feature_correlation_report.txt` | max \|r\| off-diagonal en core 24, pares con \|r\|≥0.9. |
| `ablation_report.txt` | Tabla resumen 17 vs 24 vs 46: max\|r\|, mean\|r\|, % pares ≥0.7, Silhouette. |
| `clustering_report.txt` | Asignación Ward k=7, lista de escenarios por cluster (para diversificar). |
| `scenarios_to_diversify.txt` | Escenarios que aparecen en pares con \|r\|≥0.7, ordenados por número de “pares malos”. |
| `features_report.txt` / `features_report.md` | Lista de los 46 features (descripción, origen) y settings no usados con motivo. |
| `docs/features_core_vs_extended.md` | Metodología: core 24, extended 46, world_area/aspect_ratio, política NaN, ablación, decisión sobre clusterRange_mean. |
| `docs/features_decision.md` | Justificación de qué settings se descartan y por qué. |

---

## 7. Estado del proyecto (resumen)

- **Hecho:** Extracción con world_area y aspect_ratio; política NaN (normalizar ignorando NaN, imputar 0); core 24 y reduced 17; correlación escenario–escenario y feature–feature; ablación 17/24/46; figuras listadas; documentación en README, reports y wiki.
- **Criterios de diversidad (full 46):** 96.2% pares con \|r\|<0.7 ✓; Silhouette 0.33 > 0.3 ✓; 3 pares con cos_dist < 0.05 (objetivo era 0).
- **Pendiente (según docs/features_core_vs_extended.md):** Decisión empírica sobre **clusterRange_mean** (mantener en core o pasar a extended) según ablación/PCA; declarar “versión final” del método cuando se cierre eso.

---

## 8. Por dónde continuar (sugerencias)

1. **Revisar documentación:** Esta guía + `docs/features_core_vs_extended.md` + `README.md` + `reports/correlation_report.txt` y `reports/ablation_report.txt`.
2. **Revisar figuras:** En `figures/` (heatmaps, histogramas, PCA, par máximo r, feature–feature).
3. **Diversificación (referencia = core 24):** Usar **`reports/scenarios_to_diversify_core24.txt`** y **`reports/correlation_core24_report.txt`** para priorizar; plan detallado en **`docs/PLAN_CONTINUIDAD_CORE24.md`**. Opcional: `reports/scenarios_to_diversify.txt` (46) y `reports/clustering_report.txt`.
4. **clusterRange_mean:** Valorar con PCA/loadings o sensibilidad en clustering si conviene dejarla en core o pasarla a extended; actualizar `docs/features_core_vs_extended.md` y, si toca, la lista en `run_analysis.py`.
5. **Outputs:** Si tienes `output_metrics.csv`, ejecutar `--phase outputs` y revisar `outputs_correlation_report.txt` y `heatmap_pearson_outputs.png` para ver redundancia en resultados de simulación.
6. **Wiki:** Los cambios ya están en `scenarios/.wiki-clone`; si usas un wiki remoto, hacer commit y push desde ese directorio.

---

## 9. Comandos para reproducir todo

Desde la raíz del repo (con venv si aplica):

```bash
# Todo el pipeline de features y correlación (sin outputs)
./venv/bin/python scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all

# Fases sueltas por si solo quieres actualizar una parte
./venv/bin/python scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features
./venv/bin/python scenarios/analysis/run_analysis.py --phase normalize
./venv/bin/python scenarios/analysis/run_analysis.py --phase correlation
./venv/bin/python scenarios/analysis/run_analysis.py --phase feature_correlation
./venv/bin/python scenarios/analysis/run_analysis.py --phase ablation
./venv/bin/python scenarios/analysis/run_analysis.py --phase figures
```

Salidas relativas a `scenarios/analysis/` (data/, figures/, reports/).
