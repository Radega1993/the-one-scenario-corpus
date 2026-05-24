# Resumen de resultados

**Español** | [English](Results-overview)

---

Resumen de resultados actuales del análisis para **corpus_v1** y estado de correcciones de escenarios.  
Fuente de referencia: [`analysis/reports/RESULTADOS_ACTUALES.md`](../../analysis/reports/RESULTADOS_ACTUALES.md).

---

## Espacio de features

| Concepto | Valor |
|----------|-------|
| Escenarios (n) | 60 |
| Features core (referencia de diversidad) | 23 |
| Features extendidas (exploración) | 46 |
| Normalización | Z-score por feature (NaN -> 0 tras z-score) |

---

## Resultados de correlación (freeze final optimizado)

### Core 23 (referencia de diversidad)

| Métrica | Valor |
|---------|-------|
| max \|r\| | 0.9829 |
| media \|r\| | 0.2065 |
| Total de pares | 1770 |
| Pares con \|r\| >= 0.7 | 58 (3.3%) |
| Pares con \|r\| < 0.7 | 96.7% |
| Distancia coseno (mínima) | 0.0152 |
| Silhouette (Ward k=7) | 0.2681 |

Fuente: `analysis/reports/correlation_core23_report.txt`.

### Espacio completo de 46 features

| Métrica | Valor |
|---------|-------|
| max \|r\| | 0.9377 |
| media \|r\| | 0.1906 |
| Total de pares | 1770 |
| Pares con \|r\| >= 0.7 | 46 (2.6%) |
| Pares con \|r\| < 0.7 | 97.4% |
| Distancia coseno (mínima) | 0.0620 |
| Silhouette (Ward k=7) | 0.2929 |
| Criterio (>=95% con \|r\| < 0.7) | Cumplido |

Fuente: `analysis/reports/correlation_report.txt`.

---

## Ablación (17 vs 23 vs 46)

| Conjunto | max \|r\| | media \|r\| | pares >= 0.7 | silhouette |
|----------|-----------|-------------|---------------|------------|
| reduced_17 | 0.9863 | 0.2324 | 63 (3.6%) | 0.2215 |
| core_23 | 0.9829 | 0.2065 | 58 (3.3%) | 0.2681 |
| full_46 | 0.9377 | 0.1906 | 46 (2.6%) | 0.2929 |

Fuente: `analysis/reports/ablation_report.txt`.

---

## Baseline inicial vs final optimizado

| Métrica | Baseline inicial | Final optimizado |
|---------|------------------|------------------|
| Full-46 pares con \|r\| >= 0.7 | 57 (3.2%) | 46 (2.6%) |
| Core-23 pares con \|r\| >= 0.7 | 93 (5.3%) | 58 (3.3%) |
| Full-46 coseno mínimo | 0.0585 | 0.0620 |
| Full-46 silhouette | 0.2924 | 0.2929 |

Framing de freeze: **baseline mejorado, estable y publicable**, no corpus óptimo final.

---

## Limitaciones declaradas

- Persisten pares con correlación alta en ambos espacios.
- El silhouette en core-23 queda moderado (`0.2681`) tras la optimización.
- Persistencia de dependencia feature-feature en core: `mm_WDM <-> mm_Bus = 0.9393`.

---

## Estado de correcciones (map bounds)

Se corrigió el error `Map node ... out of world bounds` ajustando `MovementModel.worldSize` en escenarios basados en mapa:

- `V1_TaxiLow_HelsinkiMedium` -> `8400, 7504`
- `V2_TaxiHigh_HelsinkiMedium` -> `8400, 7504`
- `V3_BusOnlyCarriers_HelsinkiMedium` -> `8400, 7504`
- `V4_CarOwnership_0_HelsinkiMedium` -> `8400, 7504`
- `R4_ParkRangers_HelsinkiMedium` -> `8400, 7504`
- `D5_UAVMule_FastRoute_HelsinkiMedium` -> `8400, 7504`

La última validación completa reportada por el usuario quedó en **56/60 OK, 4 con fallo** antes del ajuste final de `V1`, `V2`, `V4` y `R4`. Ejecutar de nuevo la simulación completa para confirmar **60/60 OK**.

---

## Ver también

- [Final-frozen-results-es](Final-frozen-results-es)
- [Optimization-history-es](Optimization-history-es)
- [Feature-feature-analysis-es](Feature-feature-analysis-es)
- [Clustering-analysis-es](Clustering-analysis-es)
- [Output-space-analysis-es](Output-space-analysis-es)
- [Metodología](Methodology-es)
- [Figuras](Figures-es)
- [Visión del corpus](Corpus-overview-es)
