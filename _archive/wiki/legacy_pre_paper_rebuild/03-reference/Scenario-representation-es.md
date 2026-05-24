# Representación de escenarios

Propósito: definir cómo un escenario `.settings` se convierte en una unidad de análisis.

Artefactos relacionados: `analysis/data/features.csv`, `analysis/data/features_normalized.csv`.

## Flujo de representación

1. Parsear cada archivo `.settings`.
2. Extraer un vector descriptor fijo (full-46 features).
3. Construir espacios reducidos de análisis (`core23`, `reduced17`).
4. Normalizar por feature (política NaN-aware).
5. Comparar escenarios en espacio descriptor y en espacio de outputs.

## Por qué importa

Desacopla el análisis de etiquetas narrativas y permite chequeos cuantitativos de diversidad reproducibles.
