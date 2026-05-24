# Fórmulas de extracción

Propósito: resumir fórmulas clave de descriptores usadas en el pipeline.

## Ejemplos core

- `world_area = Wx * Wy`
- `aspect_ratio = min(Wx, Wy) / max(Wx, Wy)`
- `event_interval_mean = mean(Events*.interval)`
- `event_size_mean = mean(Events*.size)`

## Notas

- La implementación completa está en `analysis/run_analysis.py`.
- La política de normalización está documentada en [NaN-and-normalization-policy-es](NaN-and-normalization-policy-es).
