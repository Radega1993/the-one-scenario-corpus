# Estado de diversidad

**Español** | [English](Diversity-status)

---

Estado actual de los **criterios de diversidad** y acciones realizadas para reducir la correlación entre escenarios.

---

## Criterios (recordatorio)

- **|r| < 0,7** en ≥95 % de pares (Pearson sobre vectores de features).
- **Distancia coseno mínima > 0,05** (no pares casi idénticos).
- **Ningún par con cos_dist < 0,05** ✓ (actualmente 0).
- **Silhouette > 0,3** (opcional; actual 0,00).

---

## Estado actual

| Criterio | Estado |
|----------|--------|
| Pares con \|r\| < 0,7 | 93,7 % (objetivo ≥95 %) — **no cumplido** |
| Pares con cos_dist < 0,05 | 0 ✓ |
| Distancia coseno mínima | 0,0534 > 0,05 ✓ |

---

## Pares demasiado correlacionados

Hay **153 pares** con |r| ≥ 0,7. Ejemplos (lista completa en `analysis/reports/correlation_report.txt`):

- V4_MixedBusPed ↔ V5_RushHourBusDensity (r = 0,9475)
- U3_NightlifeClusters ↔ C5_Festival_MultiHotspots (r = 0,9420)
- T10_HighRateLowSpeed ↔ T15_TransmitSpeed_256k (r = 0,9397)
- … y 150 más.

---

## Escenarios a diversificar / decisiones tomadas

- La lista de escenarios que aparecen en pares con |r| alto o en clusters densos está en **`analysis/reports/scenarios_to_diversify.txt`**.
- **Diversificación** = modificar los `.settings` (speed, waitTime, transmitRange, workDayLength, TTL, buffer, nrOfOffices, nrOfMeetingSpots, etc.) para alejar el escenario en el espacio de features.
- Se añadieron **escenarios radicales** (R9–R12, T11–T15, D9, etc.) para aumentar la diversidad; se han aplicado clustering y diversificación por pares en pasos previos (ver [ROADMAP](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/ROADMAP.md)).

*(Actualizar esta sección cuando se completen nuevos pasos de diversificación.)*

---

## Ver también

- [Resumen de resultados](Results-overview-es) — Números completos de correlación y distancia  
- [Metodología](Methodology-es) — Criterios de diversidad  
- [Visión del corpus](Corpus-overview-es) — Familias y diseño  
