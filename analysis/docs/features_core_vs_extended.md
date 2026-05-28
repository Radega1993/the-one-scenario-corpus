# Core vs extended features — freeze final (core 23)

**Estado:** versión vigente para documentación pública y paper.  
**Referencia canónica:** `analysis/reports/RESULTADOS_ACTUALES.md`.  
**Scope de diversidad:** `corpus_v1` — **540** escenarios (sin `stress_controls`).

## 1) Criterio de diseño

Se mantiene una separación metodológica:

- **Core 23**: conjunto principal para diversidad y narrativa del paper.
- **Extended 46**: cobertura completa para exploración, dashboard y material suplementario.
- **Reduced 17**: versión compacta para ablación.

Regla de inclusión en core:

1. aporta dimensión estructural del escenario (no solo detalle de implementación),
2. es interpretable para revisión científica,
3. evita redundancia fuerte dentro del núcleo,
4. mantiene cobertura corpus-wide (sin sesgo excesivo a una sola familia).

## 2) Lista core vigente (23)

`world_area`, `aspect_ratio`, `N`, `nrofHostGroups`, `speed_mean`, `wait_mean`, `mm_WDM`, `mm_RWP`, `mm_MapRoute`, `mm_Cluster`, `mm_Bus`, `mm_Linear`, `transmitRange`, `bufferSize`, `transmitSpeed`, `msgTtl`, `event_interval_mean`, `event_size_mean`, `nrof_event_generators`, `pattern_burst`, `pattern_hub_target`, `workDayLength`, `ownCarProb`.

**Decisión final destacada:** `clusterRange_mean` pasa a extended por cobertura baja y aporte marginal no robusto en el freeze final.

## 3) Política NaN y normalización

- Se normaliza por columna (z-score) **ignorando NaN** en media y desviación.
- Luego se imputa NaN a `0` **solo en espacio estandarizado**.
- Esta decisión es metodológica (comparabilidad en espacio común), no ontológica (no implica que “no aplica” sea valor medio físico).

## 4) Snapshot final (freeze corpus_v1, n=540)

| Espacio | max \|r\| | pares \|r\|≥0.7 | % pares | Silhouette (Ward k=7) |
|---------|----------:|------------------:|--------:|----------------------:|
| reduced_17 | 1.0 | 7425 | 5.1% | 0.3355 |
| core_23 | 1.0 | 5029 | 3.5% | 0.3045 |
| full_46 | 1.0 | 3378 | 2.3% | 0.2354 |

- **Feature–feature core:** `mm_WDM ↔ mm_Bus = 0.9354` (dependencia residual documentada).
- **Pares totales:** C(540,2) = 145 530.

## 5) Framing de paper

La versión actual se presenta como **baseline mejorado, estable y publicable**, con limitaciones declaradas (pares altos residuales TP06↔TP11, silhouette moderado en full-46, dependencia `mm_WDM ↔ mm_Bus`).  
No se presenta como corpus óptimo final.

**Stress controls:** los 30 escenarios de `stress_controls/` no entran en este freeze de diversidad; se reportan como laboratorio aparte.

## 6) Artefactos canónicos (diversidad)

| Artefacto | Ruta |
|-----------|------|
| Features raw | `data/features.csv` |
| Extended (46) | `data/features_normalized.csv` |
| Core (23) | `data/features_core.csv` |
| Reduced (17) | `data/features_reduced.csv` |
| Pearson / Spearman / distances | `data/correlation_*.csv`, `data/distance_*.csv` |
| Ablation | `data/ablation_metrics.csv` |
| Feature–feature | `data/feature_feature_correlation_core.csv` |
| Informe único | `reports/RESULTADOS_ACTUALES.md` |
| Figuras paper | `figures/paper/main/`, `figures/paper/supplementary/` |
| Tablas paper | `figures/paper/tables/` |

Regeneración: `run_analysis.py --corpus corpus_v1 --no-stress --phase <features|normalize|correlation|...>`.

## 7) Metodología de diversidad (escenarios → vectores)

Cada escenario `.settings` se convierte en un **vector numérico** de features (46 en extended). La diversidad del corpus se evalúa comparando esos vectores entre escenarios (no narrativamente).

| Métrica | Qué mide | Artefacto |
|---------|----------|-----------|
| **Pearson r** | Correlación lineal entre vectores z-score de dos escenarios | `correlation_pearson.csv` |
| **Spearman ρ** | Correlación de rangos (robustez a no-linealidad leve) | `correlation_spearman.csv` |
| **Distancia coseno** | 1 − similitud angular entre vectores (magnitud normalizada) | `distance_cosine.csv` |
| **Distancia euclídea** | Distancia L2 en espacio z-score | `distance_euclidean.csv` |
| **Clustering Ward (k=7)** | Agrupación jerárquica sobre distancia coseno entre escenarios | `cluster_assignments.csv`, `reports/pipeline/clustering_report.txt` |
| **Silhouette** | Calidad de separación de clusters (mayor = mejor separación) | `ablation_metrics.csv`, barras en `figures/paper/main/` |
| **Feature–feature (core)** | Redundancia entre columnas del espacio core-23 | `feature_feature_correlation_core.csv` |
| **Ablación 17/23/46** | Trade-off parsimonia vs diversidad al reducir dimensiones | `ablation_metrics.csv` |

**Umbral de diversidad (paper):** pares con \|r\| ≥ 0.7 se consideran redundantes; el criterio operativo es mantener una fracción baja de tales pares (ver `table_diversity_criteria_en.md`).

**Corrección múltiple:** `reports/pipeline/multiple_comparisons_report.txt` (FDR/Bonferroni sobre m = C(540,2) comparaciones).

## 8) Limitaciones declarables en el paper

- Escenarios y tráfico son **sintéticos/semi-sintéticos**; no es un trace empírico urbano.
- Pares TP06↔TP11 pueden alcanzar \|r\| = 1.0 (redundancia documentada).
- `mm_WDM ↔ mm_Bus` correlaciona fuertemente en core-23 (0.9354).
- Silhouette moderado en full-46; core-23 es el espacio narrativo principal.
- `stress_controls` (30) quedan **fuera** del freeze de diversidad de inputs.

## 9) Validación automatizada

```bash
python3 scenarios/analysis/scripts/paper/validate_diversity_readiness.py
```

Salidas: `reports/diversity_validation_readiness.md`, `data/diversity_validation_checklist.csv`.
