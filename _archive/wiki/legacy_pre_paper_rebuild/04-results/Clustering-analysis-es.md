# Análisis de clustering

Propósito: resumir la interpretación de estructura de clusters en el baseline congelado.

## Método

- Clustering jerárquico Ward (`k=7`) sobre espacio descriptor estandarizado.
- Silhouette como indicador compacto de calidad estructural.

## Lectura actual

- `full46` mantiene estructura moderada y usable (`silhouette 0.2929`).
- `core23` mantiene interpretabilidad pero con separación más moderada (`0.2681`) tras optimización.

## Posicionamiento

El clustering se interpreta junto con correlación y distancia, no como criterio único de aceptación.
