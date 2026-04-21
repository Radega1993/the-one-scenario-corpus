# Resultados actuales del corpus (referencia única)

**Corpus:** 60 escenarios en `corpus_v1/`.
**Umbral |r|:** 0.7
---
## Métricas en espacio CORE (23 features)
| Métrica | Valor |
|---|---|
| max |r| | 0.9829 |
| Pares con |r| ≥ 0.7 | 58 (3.3%) |

Total pares (i<k): 1770
---
## Métricas en espacio completo (46 features)
| Métrica | Valor |
|---|---|
| max |r| | 0.9377 |
| Pares con |r| ≥ 0.7 | 46 (2.6%) |

Distancia coseno mínima (geom): 0.0620
Silhouette (Ward k=7): 0.2929
---
## Ablación y validación de correlación
## Ablación (17 vs 23 vs 46, umbral |r|≥0.7)
- reduced_17: max|r|=0.9998, pares≥=0.7=92, silhouette=0.3269
- core_23: max|r|=0.9829, pares≥=0.7=58, silhouette=0.2681
- full_46: max|r|=0.9377, pares≥=0.7=46, silhouette=0.2929

## Informes en este directorio (`reports/`)

| Informe | Contenido |
|---|---|
| [correlation_core23_report.txt](correlation_core23_report.txt) | Pares con |r|≥umbral en core 23 |
| [correlation_report.txt](correlation_report.txt) | Correlación en espacio completo (46 features) |
| [ablation_report.txt](ablation_report.txt) | Ablación 17 vs 23 vs 46 |
| [multiple_comparisons_report.txt](multiple_comparisons_report.txt) | FDR y Bonferroni |
| [features_report.md](features_report.md) / [features_report.txt](features_report.txt) | Features usados / descartados |
| [feature_feature_correlation_report.txt](feature_feature_correlation_report.txt) | Correlación feature–feature (core 23) |