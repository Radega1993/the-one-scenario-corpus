# Resultados actuales del corpus (referencia única)

**Corpus:** 60 escenarios en `corpus_v1/`.
**Umbral |r|:** 0.7
---
## Métricas en espacio CORE (24 features)
| Métrica | Valor |
|---|---|
| max |r| | 0.9712 |
| Pares con |r| ≥ 0.7 | 93 (5.3%) |

Total pares (i<k): 1770
---
## Métricas en espacio completo (46 features)
| Métrica | Valor |
|---|---|
| max |r| | 0.9364 |
| Pares con |r| ≥ 0.7 | 57 (3.2%) |

Distancia coseno mínima (geom): 0.0585
Silhouette (Ward k=7): 0.2924
---
## Ablación y validación de correlación
## Ablación (17 vs 24 vs 46, umbral |r|≥0.7)
- reduced_17: max|r|=0.9800, pares≥=0.7=97, silhouette=0.2727
- core_24: max|r|=0.9712, pares≥=0.7=93, silhouette=0.3174
- full_46: max|r|=0.9364, pares≥=0.7=57, silhouette=0.2924

## Informes en este directorio (`reports/`)

| Informe | Contenido |
|---|---|
| [correlation_core24_report.txt](correlation_core24_report.txt) | Pares con |r|≥umbral en core 24 |
| [correlation_report.txt](correlation_report.txt) | Correlación en espacio completo (46 features) |
| [ablation_report.txt](ablation_report.txt) | Ablación 17 vs 24 vs 46 |
| [multiple_comparisons_report.txt](multiple_comparisons_report.txt) | FDR y Bonferroni |
| [features_report.md](features_report.md) / [features_report.txt](features_report.txt) | Features usados / descartados |
| [feature_feature_correlation_report.txt](feature_feature_correlation_report.txt) | Correlación feature–feature (core 24) |