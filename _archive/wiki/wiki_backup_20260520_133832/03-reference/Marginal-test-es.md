# Test marginal

Propósito: explicar la lógica de evaluación add/remove por feature.

## Qué evalúa

Un test marginal mide si añadir o quitar una dimensión descriptora cambia de forma relevante los indicadores de diversidad.

## Por qué es útil

- Detecta dimensiones poco informativas o muy condicionales.
- Aporta evidencia empírica, sin sustituir el juicio semántico/metodológico.

## Interpretación de salida

Los cambios se leen en contexto de:

- pares con \|r\| alto,
- comportamiento de silhouette,
- cobertura y condicionalidad de la feature.
