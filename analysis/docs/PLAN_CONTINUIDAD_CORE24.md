# Plan de continuidad — Core 24 como referencia de la investigación

Las **24 features core** son la referencia única para evaluar diversidad del corpus y para basar la investigación (tesis/paper). Los resultados y las decisiones de diversificación se miden en el **espacio de las 24 core**, no en el de las 46 extendidas.

**Objetivos del proyecto:** (1) Que cada escenario aporte **información única** para que investigadores puedan simular sus protocolos y obtener resultados en cada tipo de escenario. (2) **Correlación lineal baja** entre escenarios (umbral <5% pares con |r|≥0.7); si no, podemos considerar que es el mismo escenario y se duplicarían tests sin aportar nada.

---

## 1. Decisión de referencia

- **Métricas de diversidad:** Todas se calculan sobre vectores de **24 dimensiones** (core).
- **Correlación entre escenarios:** r(S_i, S_k) = Pearson entre filas de **Z_core** (matriz n×24).
- **Lista de escenarios a diversificar:** La que importa es la generada en espacio core 24.
- **Extended (46):** Se usan solo para análisis exploratorio, dashboard y material suplementario; no para definir si el corpus es diverso ni para los resultados principales.

**Dónde está la lista de las 24 core:** `docs/features_core_vs_extended.md` §1 (tabla) y en código `run_analysis.py` → `FEATURES_CORE_24`.

---

## 2. Estado actual en espacio CORE 24

Fuente: `reports/correlation_core24_report.txt` y `data/ablation_metrics.csv`.

| Métrica | Valor | Objetivo / nota |
|--------|--------|------------------|
| Escenarios | 60 | 10 en corpus_dropped_v1: C6, V4, U2, V5, C5, U3, U4, U6, U10, V8. |
| Features | 24 (core) | — |
| **max \|r\|** | **0.9708** | Corpus 60; peor par U11↔U12. |
| **Distancia coseno mínima** | **0.0295** | Sin pares casi idénticos. |
| media \|r\| | 0.2135 | — |
| **Pares con \|r\| ≥ 0.7** | **88 (5.0%)** | En el umbral del objetivo <5%; 10 escenarios eliminados (U3,U4,U6,U10,V8 + anteriores). |
| Silhouette (Ward k=7) | 0.3227 | Estructura de clusters en core 24. |

### 2.1 ~~Duplicados exactos (r = 1.0)~~ Resuelto (Fase A)

- **U1** ↔ **U2** y **U11** ↔ **U3** tenían r = 1.0 en core 24. Se varió **workDayLength** (core) para que los cuatro tengan valores distintos: **U1 = 28800** (8h), **U2 = 25200** (7h), **U11 = 27000** (7.5h), **U3 = 30600** (8.5h). Tras los cambios: max \|r\| = 0.9994, dist. coseno mín = 0.0005; ya no hay vectores idénticos.

### 2.2 Puntos muy cercanos (r > 0.99) en core 24 — tras Fase B

Tras Fase B los peores pares son (orden aproximado):

- U1 ↔ U3 (0.9926), U8 ↔ V6 (0.9878), U3 ↔ C5 (0.9862)
- U12 ↔ U1 (0.9847), U12 ↔ U8 (0.9809), U8 ↔ V8 (0.9778)
- U4 ↔ V6, U1 ↔ C5, U12 ↔ U3, C5 ↔ C6 (0.97–0.98)

**Causa:** Mismo mundo (HelsinkiMedium), mismo modelo (WDM + Bus), mismo N; las variaciones en workDayLength, bufferSize, transmitRange y Events1 reducen algo la correlación pero muchos pares siguen muy altos. Para bajar a <5% haría falta una ronda más (U4, U6, U12, V4, V5 con Events1/bufferSize/transmitRange más distintos).

---

## 3. Dónde encontrar resultados y listas (core 24)

| Qué | Dónde |
|-----|--------|
| Métricas y pares con \|r\| ≥ 0.7 en core 24 | `reports/correlation_core24_report.txt` |
| **Lista de escenarios a diversificar (prioridad por nº de pares malos)** | **`reports/scenarios_to_diversify_core24.txt`** |
| Matriz de correlación entre escenarios (24D) | `data/correlation_pearson_core24.csv` |
| Distancias coseno en 24D | `data/distance_cosine_core24.csv` |
| Asignación a clusters en espacio core 24 | `data/cluster_assignments_core24.csv` |
| Ablación 17 vs 24 vs 46 (resumen) | `reports/ablation_report.txt`, `data/ablation_metrics.csv` |
| Correlación entre features (24×24) | `reports/feature_feature_correlation_report.txt`, `data/feature_feature_correlation_core.csv` |

---

## 4. Escenarios con más impacto (core 24)

Los que más contribuyen a pares con \|r\| ≥ 0.7 en core 24 (ordenados por número de pares “malos”):

1. **V4_MixedBusPed_HelsinkiMedium**, **U1_CBD_Commuting_HelsinkiMedium**, **U2_RetailHeavy_HelsinkiMedium**, **V6_CarOwnership_0_HelsinkiMedium**, **U12_HighTimeVariance_HelsinkiMedium**, **C5_Festival_MultiHotspots_HelsinkiMedium** (17 pares cada uno)
2. U3_NightlifeClusters, U11_OfficeWaitHeavyTail, V8_RoadClosure, U6_DenseDowntown, U8_CongestionHotspot, C6_Conference_Networking (16 pares)
3. U4_RainyDay_SlowMobility (15); U9_WorkdayShort, V5_RushHourBusDensity (14); etc.

**Conclusión:** La mayoría son escenarios **Urban / Campus / Vehicle** sobre **HelsinkiMedium** con **WDM + Bus**. Para diferenciarlos en core 24 hay que variar dimensiones que sí están en el core: por ejemplo **workDayLength**, **ownCarProb**, **speed_mean**, **wait_mean**, **transmitRange**, **bufferSize**, **transmitSpeed**, **msgTtl**, **event_interval_mean**, **event_size_mean**, **pattern_burst** / **pattern_hub_target**, o **nrofHostGroups** (si se puede justificar otro grupo con otro movimiento).

---

## 5. Cómo continuar el proyecto (prioridades)

### Fase A — ~~Duplicados (r = 1.0)~~ Hecho

1. **Resueltos los dos pares con r = 1.0** variando **workDayLength** (core) en U2, U11 y U3:
   - **U2_RetailHeavy:** workDayLength 28800 → **25200** (7h).
   - **U11_OfficeWaitHeavyTail:** workDayLength 25200 → **27000** (7.5h).
   - **U3_NightlifeClusters:** workDayLength 25200 → **30600** (8.5h). U1 se mantiene en 28800 (8h).
2. **Comprobado:** max \|r\| = 0.9994 (< 1), dist_coseno mínima = 0.0005 (> 0). Pares \|r\| ≥ 0.7: 206 (8.5%).

### Fase B — Reducir pares con \|r\| ≥ 0.7 (objetivo < 5%) — En curso

**Hecho (primera ronda):** 206 → 200 pares (8.5% → 8.3%). Cambios aplicados solo en parámetros core 24:

- **workDayLength:** V6=25200, V8=30600, V4=23400, U8=27900, U12=29700, C5=31500, C6=32400.
- **bufferSize / transmitSpeed / Events1:** U2=35M, 1.5M, interval 40–60 size 80k–180k; U11=65M, 2.5M, interval 20–30 size 30k–80k; U3=40M; U1=45M, transmitRange 11, Events1 35–45 y 80k–120k; U12=55M; U8=48M; C5=40M, C6=60M; V6=45M, V8=55M. U3 transmitRange 7, Events1 18–28 y 40k–100k.

**Segunda ronda (recomendados) aplicada:** Variados **U4, U6, U12, V4, V5** en core 24:
- **U4:** bufferSize 42M, Events1 50–70 s, 100k–200k (lluvia = menos frecuente, mensajes más grandes).
- **U6:** bufferSize 52M, Events1 15–25 s, 30k–70k (downtown = más frecuente, más pequeños).
- **U12:** transmitRange 9, Events1 32–42 s, 70k–130k.
- **V4:** bufferSize 48M (Events1 ya distintos).
- **V5:** bufferSize 58M (Events1 ya distintos).

Tras re-ejecutar pipeline: **Pares con \|r\| ≥ 0.7 siguen en 200 (8.3%)**. El clic Urban/Campus/Vehicle (U1, U3, U8, U12, C5, C6, V6, V8) sigue generando la mayoría de pares altos.

**Tercera ronda aplicada:** Variados **U1, U3, U8, U12, C5, C6, V6, V8** en transmitSpeed, msgTtl y Events1:
- **U1:** transmitSpeed 2.25M, msgTtl 10000.
- **U3:** transmitSpeed 1.75M, msgTtl 7200.
- **U8:** transmitSpeed 2.5M, Events1 28–38 s, 60k–140k.
- **U12:** transmitSpeed 1.5M.
- **C5:** transmitSpeed 2.25M, Events1 22–32 s, 60k–120k.
- **C6:** transmitSpeed 1.75M, Events1 38–48 s, 90k–160k.
- **V6:** transmitSpeed 2.5M, Events1 20–30 s, 40k–100k.
- **V8:** transmitSpeed 1.5M, Events1 30–40 s, 80k–140k.
Resultado: **198 pares (8,2%)**, max |r| 0.9896 (U8↔V6). Dist. coseno mín 0.0109.

**Rondas 4–8 (peores pares en cada una):**
- **R4:** U8↔V6 (0.99) → U8 transmitSpeed 2.75M, msgTtl 5400; V6 2.25M, msgTtl 7200; U11 transmitSpeed 1.9M, msgTtl 5400. Tras pipeline: peor R8↔T6.
- **R5:** R8↔T6, U1↔C5, U12↔V8 → R8 buffer 42M, 1.75M; T6 58M, 2.25M; U1 2.5M, C5 2M; U12 msgTtl 6000, V8 msgTtl 8000. Peor: C4↔T8.
- **R6:** C4↔T8, U12↔V8 → C4 45M, 2.25M; T8 55M, 1.75M; U12 buffer 50M. Peor: U12↔U3.
- **R7:** U12↔U3 → U12 msgTtl 5000, transmitSpeed 1.6M, transmitRange 8; U3 msgTtl 9000, 1.85M, transmitRange 6. Peor: U3↔C5.
- **R8:** U3↔C5 → U3 buffer 38M, C5 buffer 42M. Sigue U3↔C5 ≈ 0.978.
- **R9:** U3↔C5, D9↔T4, C4↔T8, U11↔U12, C5↔C6, S3↔T5, T1↔T9, C3↔C7. Cambios: U3 Events1 16–26/35k–95k; C5 msgTtl 6000, transmitRange 13; C6 msgTtl 9000; D9 buffer 22M, 2.25M; T4 buffer 8M, 1.75M; C4 msgTtl 7200; T8 msgTtl 3600; U11 transmitRange 7; U12 msgTtl 4500; S3 38M, 2.25M, range 11; T5 52M, 1.75M, range 14; T1 12M, 2.25M, range 11; T9 4M, 1.75M, range 7; C3 48M, msgTtl 3600, 2.25M; C7 52M, msgTtl 7200, 1.75M. Resultado: 197 pares (8,2%), max |r| 0,9539 (U11↔U12), dist_coseno mín 0,0468.

- **R10:** msgTtl explícito en U2 (3600), U4 (3000), U9 (1800), V4 (4200). Resultado: 196 pares (8,1%), max |r| 0,9615.
- **R11 (todos los pares con |r|≥0,9):** Variados U12, U2, U11, V4, U3, C5, C4, T8, U8, V6, U9, C6, U6, U7, U1, V8, V5, U4, C2, C3, C7, R7, T13 en bufferSize, msgTtl, transmitSpeed, transmitRange (y Group1/Group2 donde aplica). Ajuste fino U2↔V4, U11↔U12, V5↔V6 para separar más. Resultado: **196 pares (8,1%)**, **max |r| 0,9594** (U12↔U2). Pares &gt;0,9 reducidos; peores restantes: U12↔U2, U11↔U12, U3↔C6, V4↔V6, C4↔T8, etc.

**Reducción a 65 escenarios:** Movidos a `corpus_dropped_v1`: C6, V4, U2, V5, C5. Core 24: 132 pares (6,3%).

**Reducción a 60 escenarios:** Movidos además U3_NightlifeClusters, U4_RainyDay, U6_DenseDowntown, U10_WorkdayLong, V8_RoadClosure (pares más altos, redundantes con otros WDM Helsinki). Corpus: 60 escenarios. Core 24: **88 pares (5,0%)**, max |r| 0,9708 (U11↔U12). Espacio 46 feat: 54 pares (3,1%), max |r| 0,9357.

**Pendiente (opcional):** Para bajar de 5% en core 24 haría falta eliminar o separar más (p. ej. U11↔U12, U11↔V6, U1↔U8↔V6).

**Variedad con mapas (worldSize):** Ver **`docs/MAPAS_Y_VARIEDAD.md`**. En `data/` solo **HelsinkiMedium** tiene todo lo necesario para WDM+Bus (homes, offices, meetingspots, bus); **Manhattan** solo tiene roads y bus (faltan ubicaciones para WDM). Para dar variedad en core 24 se varió **MovementModel.worldSize** en los 8 escenarios que compartían 8495×7504 (U2, U3, U11, U10, V4, V1, V3, V7), asignando a cada uno un worldSize distinto (8000×7000, 8200×7200, …) para que **world_area** y **aspect_ratio** sean distintos. U1 se mantiene como referencia 8495×7504. Tras re-ejecutar pipeline: 200 pares (8.3%) se mantienen; la diversificación estructural evita duplicados en espacio/forma del mundo.

**Análisis diversidad vs comportamiento:** Ver **`docs/ANALISIS_DIVERSIDAD_VS_COMPORTAMIENTO.md`**.

1. **Usar** `reports/scenarios_to_diversify_core24.txt` como lista de trabajo (orden = prioridad).
2. **Por escenario:** Revisar su `.settings` y variar **solo parámetros que correspondan a las 24 core** (world_area, aspect_ratio, N, nrofHostGroups, speed_mean, wait_mean, mm_*, transmitRange, bufferSize, transmitSpeed, msgTtl, event_interval_mean, event_size_mean, nrof_event_generators, pattern_burst, pattern_hub_target, workDayLength, ownCarProb, clusterRange_mean). Cambios solo en extended no mejoran la diversidad en core 24.
3. **Estrategias útiles:** Variar workDayLength, bufferSize, transmitRange, transmitSpeed, event_interval_mean, event_size_mean entre escenarios WDM/Bus para que cada uno tenga una “firma” distinta en 24D.
4. **Iterar:** Tras cada ronda: `--phase features` → `--phase normalize` → `--phase correlation` y revisar `correlation_core24_report.txt` y `scenarios_to_diversify_core24.txt`.

### Fase C — Opcional: redundancia feature–feature

- En core 24 solo hay **un par** con \|r\| ≥ 0.9: **mm_WDM ↔ mm_Bus** (r ≈ 0.97). En el corpus actual casi siempre que hay WDM hay Bus (urban). Para la narrativa del paper se puede dejar así y documentarlo, o valorar si en algún escenario se desacopla (p. ej. WDM sin Bus) para que esa correlación baje. No es bloqueante para la diversidad entre escenarios.

### Fase D — Decisión clusterRange_mean

- Según `docs/features_core_vs_extended.md`, **clusterRange_mean** se mantiene en core de forma condicional. Tiene muchos NaN (~91% de escenarios sin Cluster). Cuando cierres la diversificación en core 24, conviene revisar si clusterRange_mean aporta en PCA/clustering; si no, se puede bajar a extended y pasar a **core 23** en la narrativa (documentar en el mismo informe).

---

## 6. Flujo de trabajo recomendado

1. **Referencia única:** Toda la evaluación de “corpus diverso” y “escenarios a diversificar” en **core 24**.
2. **Fuente de verdad para listas:** `reports/scenarios_to_diversify_core24.txt` y `reports/correlation_core24_report.txt`.
3. **Tras cada cambio en .settings:**  
   `run_analysis.py --corpus corpus_v1 --phase features` → `--phase normalize` → `--phase correlation`  
   y revisar de nuevo los informes core 24.
4. **Objetivos numéricos (core 24):**
   - max \|r\| < 1 (eliminar duplicados exactos).
   - Distancia coseno mínima > 0.
   - Pares con \|r\| ≥ 0.7 < 5% (≈ &lt; 121 de 2415).
   - Mantener Silhouette &gt; 0.35 si es posible (estructura de clusters clara).

---

## 7. Resumen

- **Investigación basada en las 24 core:** diversidad, resultados y narrativa se apoyan en el espacio de las 24 features.
- **Estado actual:** Corpus **60 escenarios** (10 en corpus_dropped_v1). **88 pares con \|r\|≥0.7 (5.0%)** en core 24 (en el umbral <5%). Peor par: U11↔U12 (0.9708).
- **Continuar:** (B) Segunda ronda: variar U4, U6, U12, V4, V5 (Events1, bufferSize, transmitRange) para acercar a <5%; (C) opcional mm_WDM–mm_Bus; (D) después decidir clusterRange_mean (core vs extended).
