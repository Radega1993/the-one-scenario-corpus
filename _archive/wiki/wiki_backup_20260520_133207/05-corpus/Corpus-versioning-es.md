# Versionado del corpus

Propósito: explicar cómo evolucionó el corpus y cuál es el conjunto oficial congelado.

## Versión oficial actual

- **`corpus_v1`** es el conjunto oficial congelado para el baseline del paper.
- Contiene **60 escenarios** en 7 familias.

## Lógica de evolución

- La generación inicial priorizó cobertura temática amplia.
- Las rondas iterativas de diversificación redujeron redundancia alta entre pares.
- El freeze final mantiene un compromiso práctico: baseline publicable con limitaciones declaradas.

## Regla de versionado

Si futuras revisiones modifican contenido o composición del corpus, deben publicarse bajo un nuevo identificador (por ejemplo `corpus_v2`) manteniendo `corpus_v1` para reproducibilidad.
