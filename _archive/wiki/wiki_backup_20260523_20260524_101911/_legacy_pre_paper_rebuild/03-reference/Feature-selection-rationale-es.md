# Justificación de selección de features

Propósito: resumir cómo se seleccionaron y clasificaron las features.

## Criterios de selección

- Relevancia estructural para la identidad del escenario.
- Utilidad transversal por familias (comportamiento corpus-wide).
- Interpretabilidad para revisión y reproducibilidad.
- Control de redundancia dentro del conjunto core.

## Patrón final de decisión

- Mantener core compacto (`core23`) para claridad metodológica.
- Mantener extendido (`full46`) para diagnóstico más rico y análisis complementario.
- Registrar dependencias residuales de forma explícita (sin ocultarlas).
