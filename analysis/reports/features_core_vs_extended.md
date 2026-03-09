# Core vs extended features — frozen candidate version

**Estado:** Candidata metodológica congelada para wiki y borrador de paper/tesis. No se declara **versión final** hasta completar: correlación feature–feature (24×24), ablación 17 vs 24 vs 46, política de NaN cerrada en código/método, y decisión empírica sobre clusterRange_mean (core vs extended).

**Pipeline:** El script `run_analysis.py` implementa esta metodología: extracción con `world_area` y `aspect_ratio` (§2.1), política NaN en `--phase normalize` (§4), salidas `features_core.csv` (24) y `features_reduced.csv` (17), `--phase feature_correlation` (matriz 24×24, §5), `--phase ablation` (17 vs 24 vs 46, §6). Ver [../README.md](../README.md).

**Objetivo:** Definir un **conjunto core** de **24 features** para la validación principal de diversidad y el paper, y mantener las **46 como conjunto extendido** para análisis exploratorio, dashboard y material suplementario. Así se responde a la crítica de “demasiadas features” y se mejora interpretabilidad y control metodológico.

**Criterios para core:**
- Define de verdad el escenario (decisión científica si cambia).
- Poco redundante con otras del core (no misma variable latente).
- Interpretable y ligado a hipótesis de red (movilidad, contacto, tráfico, recursos).
- Justificable una a una ante un revisor.
- **Corpus-wide:** evita sobrerrepresentar una sola familia (p. ej. WDM).

**Regla:** Si quitar la feature no cambia una dimensión real del escenario sino solo un matiz de implementación, va a **extended**.

---

## 1. Lista CORE única (24 features) — versión cerrada

Una sola lista de referencia. Las tablas intermedias y el texto coinciden con esta lista.

| # | Feature | Dimensión | Origen / nota |
|---|---------|-----------|----------------|
| 1 | world_area | Espacio | Wx×Wy (m²); más interpretable que Wx,Wy por separado. |
| 2 | aspect_ratio | Espacio | min(Wx,Wy) / max(Wx,Wy) ∈ (0,1]; forma rectangular, estable e interpretable. |
| 3 | N | Espacio / carga | Número total de nodos. |
| 4 | nrofHostGroups | Estructura | 1 vs 2+ grupos; modularidad, partición, mezcla. |
| 5 | speed_mean | Movilidad | Velocidad típica (m/s); peatón vs vehículo. |
| 6 | wait_mean | Movilidad | Tiempo medio de pausa (s); ritmo de movilidad. |
| 7 | mm_WDM | Movimiento | WorkingDayMovement (0/1). |
| 8 | mm_RWP | Movimiento | RandomWaypoint (0/1). |
| 9 | mm_MapRoute | Movimiento | MapRouteMovement (0/1). |
| 10 | mm_Cluster | Movimiento | ClusterMovement (0/1). |
| 11 | mm_Bus | Movimiento | BusMovement (0/1). |
| 12 | mm_Linear | Movimiento | LinearMovement (0/1). |
| 13 | transmitRange | Conectividad | Rango de transmisión (m); grafo de contacto. |
| 14 | bufferSize | Recursos | Tamaño de buffer (bytes). |
| 15 | transmitSpeed | Recursos | Velocidad de transmisión (bytes/s). |
| 16 | msgTtl | Tráfico | TTL de mensajes (s). Su contribución se evaluará con correlación feature–feature, loadings en PCA y sensibilidad en clustering (§2.6, §5). |
| 17 | event_interval_mean | Tráfico | Intervalo medio entre mensajes (s). |
| 18 | event_size_mean | Tráfico | Tamaño medio de mensaje (bytes). |
| 19 | nrof_event_generators | Tráfico | 1 vs 2 flujos (tráfico multimodal). |
| 20 | pattern_burst | Tráfico | Patrón por ventanas temporales (0/1). |
| 21 | pattern_hub_target | Tráfico | Patrón dirigido a hubs (0/1). Uniforme = referencia implícita. |
| 22 | workDayLength | WDM | Duración jornada (s); NaN si no WDM. Solo 1–2 WDM en core para no sesgar. |
| 23 | ownCarProb | WDM | Prob. coche (0–1); NaN si no WDM. |
| 24 | clusterRange_mean | Cluster | Radio medio de clusters (m); NaN si no Cluster. Condición en §2. |

**Implementación:** `world_area` = Wx×Wy (m²). `aspect_ratio` = min(Wx, Wy) / max(Wx, Wy), acotado en (0, 1], independiente de orientación “más ancho que alto”. No se usan Wx, Wy por separado en el core para evitar ruido y mejorar interpretabilidad científica.

---

## 2. Decisiones metodológicas (resumen)

### 2.1 Espacio: world_area y aspect_ratio en lugar de Wx, Wy

- **Problema:** Wx y Wy por separado son poco interpretables como dimensión científica si la anisotropía no es central.
- **Solución:** **world_area** = Wx×Wy (tamaño total). **aspect_ratio** = min(Wx, Wy) / max(Wx, Wy) ∈ (0, 1] (forma rectangular, estable, sin depender de orientación). Más interpretables y evitan redundancia con N.

### 2.2 nrofHostGroups en core

- Cambiar de 1 a 2 o más grupos afecta estructura de contactos, modularidad y partición. No es matiz de implementación → **core**.

### 2.3 WDM: solo 2 features en core

- **Riesgo:** Si el core incluye muchas features WDM (workDayLength, nrOfOffices, ownCarProb, nrOfMeetingSpots…), el núcleo queda sesgado hacia escenarios urbanos/WDM y deja de ser corpus-wide (rural, disaster, social, traffic, RWP, cluster).
- **Decisión:** En core solo **workDayLength** y **ownCarProb**. **nrOfOffices**, nrOfMeetingSpots, timeDiffSTD, probGoShoppingAfterWork, etc. → **extended**.

### 2.4 clusterRange_mean: congelación condicionada a la ablación

- **Regla:** Si ClusterMovement aparece en **&lt; ~10–15%** del corpus, clusterRange_mean tiene muchos NaN y aporta poco al núcleo → candidata a **extended**.
- **En nuestro corpus:** 6 escenarios con Cluster (D1, D2, D8, S1, S6, R2) ≈ **9%**. Es el punto más discutible del core.
- **Decisión actual:** Se mantiene en **core** de forma provisional porque representa una dimensión estructural clara (tight vs villages) para Social, Disaster, Rural. **La congelación definitiva depende de los resultados de la ablación:** si no mejora diversidad, introduce problemas por NaN o apenas pesa en PCA/clustering, se bajará a **extended**. Hasta entonces no se declara versión final. Documentar en el paper la proporción de NaN y la justificación empírica (o el paso a extended).

### 2.5 pattern_uniform fuera del core

- Con **pattern_burst** y **pattern_hub_target** en core, “uniforme” actúa como **categoría de referencia implícita** (ninguno de los dos = uniforme). Evita dummy redundante y simplifica → **extended** pattern_uniform.

### 2.6 msgTtl en core

- Se mantiene en core (relevancia temporal del mensaje). Su contribución se evaluará de forma explícita mediante correlación feature–feature (§5), loadings en PCA y análisis de sensibilidad en clustering, para comprobar que no queda dominada por otras variables en el corpus.

---

## 3. Redundancias y variables latentes (46 actuales)

### 3.1 Derivadas / redundantes → extended

- **density** = N / world_area (o N/(Wx×Wy)). Se excluye del core **de forma intencionada**: es función determinista de N y world_area; incluirla introduciría información redundante y colinealidad. N y world_area en el core bastan para recuperar la noción de densidad cuando haga falta.  
- **contact_rate_proxy** = f(density, transmitRange, speed); derivado → **extended**.  
- **pause_ratio** = f(waitTime); redundante con wait_mean → **extended**.

### 3.2 Bloques por variable latente

- **Shopping (WDM):** probGoShoppingAfterWork, nrOfShops, shopSize, shoppingWaitTime_mean, afterShoppingStopTime_mean → en core ninguna (o solo una si se sube probGoShoppingAfterWork); aquí todas **extended** para no inflar WDM en core.
- **Oficina (WDM):** nrOfOffices, officeSize, officeWaitTime_mean → **nrOfOffices** podría estar en core en un corpus muy urbano; en versión corpus-wide **extended**.
- **Evening (WDM):** eveningGroupSize_mean, eveningWaitTime_mean → **extended**.
- **Tráfico segundo flujo:** event2_interval_mean, event2_size_mean; nrof_event_generators ya indica 1 vs 2 → **extended** event2_*.
- **Movimiento poco frecuente:** mm_ShortestPath, mm_External → **extended**.

### 3.3 Conjunto EXTENDED (resto hasta 46)

Todas las que no están en la lista core de 24:

- Wx, Wy (usados para derivar world_area, aspect_ratio), density, pause_ratio, contact_rate_proxy  
- mm_ShortestPath, mm_External  
- event2_interval_mean, event2_size_mean  
- pattern_uniform  
- timeDiffSTD, probGoShoppingAfterWork, nrOfMeetingSpots, **nrOfOffices**, officeSize, nrOfShops, shopSize  
- officeWaitTime_mean, shoppingWaitTime_mean, eveningGroupSize_mean, eveningWaitTime_mean, afterShoppingStopTime_mean  
- Scenario.endTime, has_active_times  

Uso extended: análisis exploratorio, clustering fino, dashboard, apéndice y material suplementario.

---

## 4. Tratamiento de NaN — política adoptada

Muchas features del core son **condicionales** (WDM, Cluster): tienen valor numérico solo en parte del corpus y NaN en el resto.

**Política única (método operativo):**

*Features were normalized column-wise using only non-NaN values (mean and standard deviation per feature over scenarios where the feature is defined). Afterwards, NaNs were imputed as 0 in the standardized space, so that conditional features (e.g. workDayLength, ownCarProb, clusterRange_mean) act as neutral descriptors outside their valid scenario family when computing correlation between scenario vectors.*

En resumen: normalización por columnas ignorando NaN; luego imputación a 0 en el espacio estandarizado. Las features condicionales quedan en “valor neutro” (0 tras z-score) para escenarios donde no aplican (p. ej. no-WDM en workDayLength). Esto debe quedar implementado y documentado igual en el código y en la sección de método del paper; sin una política única cerrada, un revisor puede cuestionar la validez de la correlación.

---

## 5. Colinealidad entre features (feature–feature)

**Recomendación:** Construir matriz de correlación **entre las 24 features del core** (sobre los 70 escenarios, con NaN manejados como en §4).

- **Objetivo:** Demostrar que el core no está muy colineado. Si aparecen pares con |r| muy alto (p. ej. N vs density, wait_mean vs pause_ratio), se reafirman los descartes (esas en extended).
- **Salida:** Heat map 24×24 (Pearson o Spearman) en material suplementario o en método; una frase tipo: “No pairs of core features showed |r| > 0.9, supporting low redundancy of the core set.”

---

## 6. Ablation: 17 vs 24 (core) vs 46 (extended)

**Objetivo:** Argumento empírico para el tamaño del core.

- **Comparar** los mismos indicadores con tres vectores:
  - **Reducido (17):** p. ej. conjunto tipo tesis (o subconjunto mínimo razonable).
  - **Core (24):** la lista de esta sección.
  - **Extended (46):** todas las actuales.
- **Métricas:** max |r| entre escenarios, media |r|, nº pares con |r| ≥ 0.7, Silhouette (clustering), estabilidad de clusters, interpretabilidad (narrativa).
- **Frase para el paper:** *“The 24-feature core offered the best trade-off between expressiveness, redundancy control, and interpretability.”* (si los resultados lo apoyan).

---

## 7. Narrativa para el paper

Sugerencia de redacción:

*“To avoid feature inflation and improve interpretability, we distinguish between a **core feature set** (24 features) used for diversity validation and corpus design, and an **extended descriptor set** (46 features) used for supplementary analysis and dashboard exploration. The core set was chosen to be corpus-wide, minimally redundant, and interpretable; conditional features (e.g. workDayLength, ownCarProb, clusterRange_mean) are documented with their NaN policy and coverage.”*

---

## 8. Resumen ejecutivo

| Conjunto | Nº | Uso |
|----------|----|-----|
| **Core** | 24 | Correlación principal, diversidad del corpus, resultados del paper, justificación ante revisor. Corpus-wide; WDM limitado a 2 features. |
| **Extended** | 46 | Repositorio, dashboard, análisis exploratorio, material suplementario. |

**Cambios en esta frozen candidate:** (1) Título y estado: “frozen candidate”; no “final” hasta ablación, NaN en código y decisión sobre clusterRange_mean. (2) aspect_ratio definida de forma única: min(Wx,Wy)/max(Wx,Wy). (3) Política de NaN única en §4 (normalizar ignorando NaN, imputar 0 en espacio estandarizado). (4) clusterRange_mean condicionada a resultados de ablación (mantener o bajar a extended). (5) msgTtl: redacción formal (evaluación vía correlación, PCA, clustering). (6) Exclusión explícita de density del core por redundancia con N y world_area. (7) Checklist “qué falta” y orden recomendado.

**Ideas ya congeladas como base:** separación core/extended, core de 24, world_area y aspect_ratio (aspect_ratio = min(Wx,Wy)/max(Wx,Wy)), nrofHostGroups en core, WDM reducido a 2 features, pattern_uniform fuera del core, extended como capa suplementaria, necesidad de correlación feature–feature y ablación.

**Qué falta para declarar “versión final”:**
1. ~~Política de NaN en código~~ Hecho: `run_analysis.py` normaliza ignorando NaN e imputa 0 (§4).
2. ~~aspect_ratio en código~~ Hecho: `min(Wx,Wy)/max(Wx,Wy)` en la extracción.
3. ~~Correlación feature–feature y ablación~~ Hecho: fases `feature_correlation` y `ablation`; ver `reports/feature_feature_correlation_report.txt` y `reports/ablation_report.txt`.
4. Según resultados de ablación: mantener clusterRange_mean en core o bajarla a extended (decisión empírica pendiente).

**Orden recomendado ahora:** (1)–(3) ya implementados en el pipeline. (4) Decidir clusterRange_mean (core vs extended) según ablación y declarar versión final.
