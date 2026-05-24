# Auditoría de tiempos de creación de mensajes (corpus_v2)

## Método

- **Fuente:** replicación determinista de `MessageEventGenerator` (The ONE) a partir de cada `.settings` de `corpus_v2`, con RNG compatible con Java (`prefix.hashCode()`).
- **Validación:** contrastado con `CreatedMessagesReport` cuando existe en `reports/`.
- **Nota:** el primer mensaje **no** se crea en `t=0` salvo que `Events*.time` lo fije; el constructor programa el primer evento en `t0 + interval_min + U(0, interval_max-interval_min)`.

### Validación empírica

- U1_CBD_Commuting_HelsinkiMedium__TP07_BurstWindow: OK (n=366)
- U1_CBD_Commuting_HelsinkiMedium__TP01_Baseline: OK (n=492)

---

## Respuestas explícitas

### ¿Los mensajes se lanzan todos al inicio?

**No.** En las 720 simulaciones, el porcentaje máximo de mensajes con `creation_time ≤ 0` es **0.00%**; solo **0** escenarios tienen >0.1% en t≈0. El generador espacia el primer mensaje al menos `interval_min` segundos después del inicio de la ventana (o después de `Events*.time` inferior en TP07 y similares).

### ¿Los perfiles TP generan tráfico temporalmente distinto?

**Sí.** La mediana de `creation_time` normalizada por `Scenario.endTime` difiere claramente entre perfiles (p. ej. TP02 LowLoad con mediana alta, TP07 concentrado ~0.20–0.28, TP05/TP10 con ventanas efectivas cortas por TTL).

| TP | Mediana media (s) | Mediana media / endTime | % en último 10% sim (media) |
|----|------------------:|------------------------:|----------------------------:|
| TP01 | 20586.5 | 0.501 | 10.00 |
| TP02 | 20349.7 | 0.495 | 10.08 |
| TP03 | 20513.4 | 0.499 | 10.01 |
| TP04 | 20711.1 | 0.504 | 9.82 |
| TP05 | 20586.5 | 0.501 | 10.00 |
| TP06 | 20479.2 | 0.498 | 10.20 |
| TP07 | 9884.6 | 0.240 | 0.00 |
| TP08 | 20480.6 | 0.498 | 10.19 |
| TP09 | 20592.7 | 0.501 | 9.96 |
| TP10 | 20537.3 | 0.500 | 9.93 |
| TP11 | 20479.2 | 0.498 | 10.20 |
| TP12 | 20687.7 | 0.503 | 9.62 |

### ¿TP07 realmente concentra tráfico en una ventana?

**Sí.** TP07 define `Events1.time ≈ [0.20×endTime, 0.28×endTime]`. Medias agregadas: `t_min` ≈ **8232 s** (20.0% de endTime), `t_max` ≈ **11502 s** (28.0%). No hay generación fuera de esa ventana (salvo redondeo entero en `Events1.time`).

### ¿Hay perfiles que generan demasiados mensajes cerca del final?

El perfil con mayor fracción media en el **último 10%** de la simulación es **TP06** (10.2% de mensajes). TP02 (LowLoad) e intervalos largos producen creaciones que se extienden hasta cerca del final; TP07 concentra en el medio, no al cierre.

Escenarios con mayor `%` en último 10%:

| Escenario | TP | % último 10% | t_max (s) | endTime |
|-----------|-----|-------------:|----------:|--------:|
| `R5_MountainRescue__TP02_LowLoad` | TP02 | 12.1 | 14321 | 14400 |
| `D7_HighLoad_TrafficStorm__TP02_LowLoad` | TP02 | 12.1 | 14321 | 14400 |
| `C6_EmergencyDrill_Evacuation__TP02_LowLoad` | TP02 | 11.8 | 7166 | 7200 |
| `R4_ParkRangers_HelsinkiMedium__TP02_LowLoad` | TP02 | 11.5 | 43190 | 43200 |
| `R6_SparseLongRange__TP02_LowLoad` | TP02 | 11.5 | 43172 | 43200 |
| `T11_TTL_1min__TP02_LowLoad` | TP02 | 11.5 | 43060 | 43200 |
| `T13_Buffer_256k__TP02_LowLoad` | TP02 | 11.5 | 43060 | 43200 |
| `U2_SparseSuburb_Manhattan__TP02_LowLoad` | TP02 | 11.3 | 43011 | 43200 |

### ¿Qué implicación tiene esto para el benchmark?

1. **Las métricas de `MessageStatsReport` integran mensajes creados a lo largo de toda la simulación**, no solo en t=0.
2. **Comparar protocolos por TP es válido en régimen temporal distinto** (carga sostenida vs ráfaga vs baja carga).
3. **TP07** aísla estrés de creación en una ventana; el retardo de entrega puede medirse en fase post-ráfaga.
4. **TP02 / intervalos largos:** muchos mensajes nacen en el tramo final — conviene reportar `Scenario.endTime` y considerar si el TTL permite entrega.
5. Para auditorías futuras con trazas empíricas por mensaje, añadir `CreatedMessagesReport` al pipeline (`created_messages_report_overrides.txt`).

## Figuras

- `figures/message_creation_time_hist_by_tp.png`
- `figures/message_creation_time_boxplot_by_tp.png`

## Datos

- `data/message_creation_time_summary.csv`
