# Resultados actuales del corpus (referencia única)

**Corpus:** 720 escenarios en `corpus_v2/`.
**Umbral |r|:** 0.7
---
## Métricas en espacio CORE (23 features)
| Métrica | Valor |
|---|---|
| max |r| | 1.0 |
| Pares con |r| ≥ 0.7 | 11325 (4.4%) |

Total pares (i<k): 258840
---
## Métricas en espacio completo (46 features)
| Métrica | Valor |
|---|---|
| max |r| | 1.0 |
| Pares con |r| ≥ 0.7 | 8356 (3.2%) |

Silhouette (Ward k=7): 0.2680
---
## Ablación y validación de correlación
## Ablación (17 vs 23 vs 46, umbral |r|≥0.7)
- reduced_17: max|r|=1.0000, pares≥=0.7=15410, silhouette=0.2318
- core_23: max|r|=1.0000, pares≥=0.7=11325, silhouette=0.3451
- full_46: max|r|=1.0000, pares≥=0.7=8356, silhouette=0.2680

## Informes en este directorio (`reports/`)

| Informe | Contenido |
|---|---|
| [correlation_core23_report.txt](correlation_core23_report.txt) | Pares con |r|≥umbral en core 23 |
| [correlation_report.txt](correlation_report.txt) | Correlación en espacio completo (46 features) |
| [ablation_report.txt](ablation_report.txt) | Ablación 17 vs 23 vs 46 |
| [multiple_comparisons_report.txt](multiple_comparisons_report.txt) | FDR y Bonferroni |
| [features_report.md](features_report.md) / [features_report.txt](features_report.txt) | Features usados / descartados |
| [feature_feature_correlation_report.txt](feature_feature_correlation_report.txt) | Correlación feature–feature (core 23) |