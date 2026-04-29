# Resumen por TP excluyendo escenarios sin contacto

Generado: 2026-04-29 12:55

Se excluyen filas con `total_encounters = 0` (casos desconectados, p.ej. `R1`).

| TP | n escenarios considerados | media delivery_ratio | media latency_mean (s) | media drop_ratio |
|---|---:|---:|---:|---:|
| TP01 | 2 | 0.4352 | 9634.7 | 0.0000 |
| TP02 | 2 | 0.5765 | 13381.9 | 0.0000 |
| TP03 | 2 | 0.4258 | 10521.7 | 0.0000 |
| TP04 | 2 | 0.2414 | 9572.7 | 59.9909 |
| TP05 | 2 | 0.0072 | 92.9 | 1.4986 |
| TP06 | 2 | 0.5283 | 8272.1 | 32.5562 |
| TP07 | 2 | 0.5131 | 15545.4 | 0.0000 |
| TP08 | 2 | 0.3649 | 10169.6 | 57.8505 |
| TP09 | 2 | 0.3188 | 9917.5 | 69.2420 |
| TP10 | 2 | 0.1286 | 1943.9 | 10.3796 |
| TP11 | 2 | 0.5804 | 8895.4 | 0.0000 |
| TP12 | 2 | 0.2679 | 13412.2 | 39.9325 |

## Notas

- Este resumen representa mejor el efecto de los perfiles de trafico en escenarios con oportunidades reales de contacto.
- Para benchmark final se recomienda publicar siempre dos vistas: **global** y **excluyendo no-contacto**.
