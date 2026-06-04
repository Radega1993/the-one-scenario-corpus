# Resultados actuales del corpus (referencia única)

**Corpus:** 540 escenarios en `corpus_v1/`. (sin ; laboratorio stress documentado aparte)
**Umbral |r|:** 0.7
**Pares totales (i<k):** 145530 (= C(540,2))

---
## Resumen comparativo (17 / 23 / 46 features)

| Espacio | n features | max |r| | Pares |r| ≥ 0.7 | % pares | Silhouette (Ward k=7) |
|---------|----------:|----------|-------------------:|--------:|----------------------:|
| **Reduced** | 17 | 1.0 | 7425 | 5.1% | 0.3355 |
| **Core** | 23 | 1.0 | 5029 | 3.5% | 0.3045 |
| **Extended (full)** | 46 | 1.0 | 3346 | 2.3% | 0.2375 |

**Feature–feature (core 23):** `mm_WDM ↔ mm_Bus = 0.9354` (dependencia residual documentada).

---
## Métricas en espacio REDUCED (17 features)
| Métrica | Valor |
|---|---|
| max |r| | 1.0 |
| Pares con |r| ≥ 0.7 | 7425 (5.1%) |
| Silhouette (Ward k=7) | 0.3355 |

Versión compacta para ablación; mayor silhouette que core/full, pero más pares con |r| alto.

---
## Métricas en espacio CORE (23 features)
| Métrica | Valor |
|---|---|
| max |r| | 1.0 |
| Pares con |r| ≥ 0.7 | 5029 (3.5%) |
| Silhouette (Ward k=7) | 0.3045 |

Espacio **principal** para diversidad y narrativa del paper.

---
## Métricas en espacio completo (46 features)
| Métrica | Valor |
|---|---|
| max |r| | 1.0 |
| Pares con |r| ≥ 0.7 | 3346 (2.3%) |
| Silhouette (Ward k=7) | 0.2375 |

---
## Ablación y validación de correlación

Detalle numérico (fuente: `data/ablation_metrics.csv`):

- **reduced_17:** max|r|=1.0000, pares≥=0.7=7425 (5.1%), silhouette=0.3355
- **core_23:** max|r|=1.0000, pares≥=0.7=5029 (3.5%), silhouette=0.3045
- **full_46:** max|r|=1.0000, pares≥=0.7=3346 (2.3%), silhouette=0.2375

**Interpretación:** core-23 equilibra interpretabilidad y separación (silhouette > full-46, menos pares |r|≥0.7 que reduced-17).

## Informes en este directorio (`reports/`)

| Informe | Contenido |
|---|---|
| [correlation_core23_report.txt](pipeline/correlation_core23_report.txt) | Pares con |r|≥umbral en core 23 |
| [correlation_report.txt](pipeline/correlation_report.txt) | Correlación en espacio completo (46 features) |
| [ablation_report.txt](pipeline/ablation_report.txt) | Ablación 17 vs 23 vs 46 |
| [multiple_comparisons_report.txt](pipeline/multiple_comparisons_report.txt) | FDR y Bonferroni |
| [features_report.md](pipeline/features_report.md) / [features_report.txt](pipeline/features_report.txt) | Features usados / descartados |
| [feature_feature_correlation_report.txt](pipeline/feature_feature_correlation_report.txt) | Correlación feature–feature (core 23) |