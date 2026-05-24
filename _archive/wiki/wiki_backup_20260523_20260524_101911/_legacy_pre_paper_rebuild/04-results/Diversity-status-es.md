# Estado de diversidad

**Español** | [English](Diversity-status)

---

Estado actual de los **criterios de diversidad** y acciones realizadas para reducir la correlación entre escenarios.

---

## Criterios (recordatorio)

- **|r| < 0,7** en ≥95 % de pares (Pearson sobre vectores de features).
- **Distancia coseno mínima > 0,05** (no pares casi idénticos).
- **Silhouette > 0,3** (Ward k=7).

---

## Estado actual (freeze final optimizado)

| Criterio | Estado |
|----------|--------|
| Pares con \|r\| < 0,7 (core 23) | **96,7 %** |
| Pares con \|r\| ≥ 0,7 (core 23) | 58 (3,3 %) |
| Distancia coseno mínima (core 23) | **0,0152** |
| Silhouette (k=7, core 23) | **0,2681** |
| Pares con \|r\| ≥ 0,7 (46 features) | 46 (2,6 %) |

**Ablación (17 vs 23 vs 46):** 17: 63 pares (3,6 %), silhouette 0,2215; 23: 58 pares (3,3 %), silhouette 0,2681; 46: 46 pares (2,6 %), silhouette 0,2929. Ver `analysis/reports/ablation_report.txt` y `data/ablation_metrics.csv`.

---

## Baseline inicial vs final optimizado

- Core-23 pares altos: `93 -> 58`.
- Full-46 pares altos: `57 -> 46`.
- Full-46 silhouette: `0,2924 -> 0,2929`.
- Full-46 coseno mínimo: `0,0585 -> 0,0620`.

---

## Limitaciones declaradas

- Persisten pares con correlación alta.
- El silhouette del core-23 es moderado en el freeze final (`0,2681`).
- Se mantiene una dependencia feature-feature alta: `mm_WDM <-> mm_Bus = 0,9393`.

---

## Pares demasiado correlacionados

Hay **93 pares** con |r| ≥ 0,7 en core 23 (lista completa en `analysis/reports/correlation_core23_report.txt`).

---

## Escenarios a diversificar / decisiones tomadas

- La lista de escenarios que aparecen en pares con |r| alto en el core está en **`analysis/reports/scenarios_to_diversify_core23.txt`**.
- **Diversificación** = modificar los `.settings` (speed, waitTime, transmitRange, workDayLength, TTL, buffer, nrOfOffices, nrOfMeetingSpots, etc.) para alejar el escenario en el espacio de features.
- Estado metodológico: **freeze con limitaciones declaradas**. Es un baseline publicable, no un corpus óptimo final.

---

## Ver también

- [Resumen de resultados](Results-overview-es) — Números completos de correlación y distancia  
- [Metodología](Methodology-es) — Criterios de diversidad  
- [Visión del corpus](Corpus-overview-es) — Familias y diseño  
