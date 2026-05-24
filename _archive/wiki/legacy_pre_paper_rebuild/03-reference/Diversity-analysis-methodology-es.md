# Metodología de análisis de diversidad

Propósito: definir cómo se evalúa la diversidad de escenarios.

## Métricas principales

- Correlación de Pearson (vectores de escenario en espacio estandarizado).
- Correlación de Spearman (robustez basada en rangos).
- Distancia coseno (separación angular en espacio descriptor).
- Clustering Ward (`k=7`) y silhouette para cohesión/separación estructural.

## Principio

La diversidad no se evalúa con una sola métrica; se interpreta de forma conjunta en correlación, geometría y clustering.
