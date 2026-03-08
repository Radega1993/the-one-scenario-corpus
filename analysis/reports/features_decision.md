# Decisión definitiva: settings en el análisis de escenarios (doctorado)

**Objetivo:** Fijar qué parámetros de los `.settings` forman parte del vector de features para correlación y diversidad, y cuáles se **descartan de forma definitiva** con justificación metodológica. Sin "posible extensión futura": cada setting queda **AÑADIDO** al análisis o **DESCARTADO** para esta fase de preparación del corpus.

---

## Criterios de decisión

- **AÑADIR:** Valor numérico o binario comparable entre escenarios; influye en movilidad, tráfico o recursos; ayuda a discriminar escenarios para diversidad.
- **DESCARTAR:** No comparable (rutas, IDs, coordenadas), sin variabilidad (constante en el corpus), redundante con otro feature, detalle de implementación no relevante para la investigación, o solo presente en 1 escenario sin aportar dimensión útil.

---

## 1. Settings que SÍ se usan (41 → 45 tras esta revisión)

Los 41 actuales se mantienen. Se **añaden** 4 features:

| Nuevo feature | Origen | Motivo |
|---------------|--------|--------|
| **mm_Linear** | Group*.movementModel = LinearMovement | Un escenario (C8) usa LinearMovement; discrimina movimiento direccional (evacuación). Binario 0/1. |
| **clusterRange_mean** | Group*.clusterRange (cuando ClusterMovement) | 6 escenarios (S1, S2, R2, D1, D2, D8) usan ClusterMovement con clusterRange numérico (m). Media por grupo discrimina "clusters tight" (60 m) vs "villages" (350 m). NaN si no Cluster. |
| **afterShoppingStopTime_mean** | Group*.minAfterShoppingStopTime, maxAfterShoppingStopTime | WDM: tiempo de parada tras compras. Variabilidad en el corpus; ya tenemos shoppingWaitTime_mean. |
| **event2_interval_mean**, **event2_size_mean** | Events2.interval, Events2.size (cuando Events.nrof ≥ 2) | 4 escenarios con dos generadores (T8, T3, D4, C4) tienen intervalo y tamaño del segundo flujo; D8 tiene Events2.filePath → NaN. Discrimina tráfico bimodal. |

**Total features tras decisión: 46** (41 existentes + mm_Linear, clusterRange_mean, afterShoppingStopTime_mean, event2_interval_mean, event2_size_mean).

---

## 2. DESCARTADOS DEFINITIVOS (con razón para la tesis)

### 2.1 Identificadores y configuración de salida (no son parámetro de escenario)

| Setting | Decisión | Razón |
|---------|----------|--------|
| Scenario.name | **DESCARTAR** | Identificador; no feature numérica. |
| Scenario.simulateConnections, Scenario.updateInterval | **DESCARTAR** | Parámetros de motor de simulación fijos en todo el corpus. |
| Events1.class, Events1.prefix, Events2.class, Events2.prefix | **DESCARTAR** | Tipo/identificador de generador; mismo valor o no comparable. |
| Group*.groupID | **DESCARTAR** | Identificador de grupo (b, p, t, v, f1…). |
| Report.* | **DESCARTAR** | Configuración de salida (reportDir, report1, report2); no definen el escenario. |
| bt0.type | **DESCARTAR** | Tipo de interfaz; mismo en todo el corpus. |

### 2.2 Rutas de fichero (no comparables numéricamente)

| Setting | Decisión | Razón |
|---------|----------|--------|
| MapBasedMovement.mapFile1, nrofMapFiles | **DESCARTAR** | Ruta/cantidad de ficheros; no se puede comparar entre mapas de forma numérica. |
| Group*.routeFile, Group*.homeLocationsFile, Group*.officeLocationsFile, Group*.meetingSpotsFile | **DESCARTAR** | Rutas; dependen del mapa y del dataset. |
| Events2.filePath | **DESCARTAR** | Tráfico desde fichero externo (D8); no extraemos número comparable (el segundo flujo queda capturado por nrof_event_generators=2). |

### 2.3 Coordenadas y posiciones (dependen del mapa)

| Setting | Decisión | Razón |
|---------|----------|--------|
| Group.LinearMovement.startLocation, endLocation | **DESCARTAR** | Coordenadas (x,y); no comparables entre escenarios con distintos worldSize/mapas. |
| Group1.LinearMovement.startLocation, endLocation | **DESCARTAR** | Idem. |
| Group*.clusterCenter | **DESCARTAR** | Centro (x,y) del cluster; depende del mapa y del mundo. Sí usamos clusterRange (radio en m). |

### 2.4 Referencias internas del simulador

| Setting | Decisión | Razón |
|---------|----------|--------|
| Group*.busControlSystemNr, Group1.busControlSystemNr, Group2.busControlSystemNr | **DESCARTAR** | Referencia interna al sistema de buses en el ONE. |
| Group*.eveningActivityControlSystemNr, shoppingControlSystemNr | **DESCARTAR** | Referencias internas a sistemas de control. |

### 2.5 Sin variabilidad útil o redundantes

| Setting | Decisión | Razón |
|---------|----------|--------|
| Group.router, Group1.router, Group2.router, … | **DESCARTAR** | Mismo en todo el corpus (EpidemicRouter). |
| Group.nrofInterfaces, Group1.nrofInterfaces, … | **DESCARTAR** | Casi siempre 1; sin variabilidad que aporte a la diversidad. |
| Events1.hosts | **DESCARTAR** | Rango de hosts; redundante con N (total de hosts). |
| MovementModel.rngSeed | **DESCARTAR** | Semilla aleatoria; no caracteriza el escenario de forma reproducible para comparación. |
| Group1.routeType, Group2.routeType | **DESCARTAR** | En el corpus solo aparece valor 1 (tipo de ruta de bus); sin variabilidad. |

### 2.6 Detalle fino de distribución (no priorizado en el diseño del vector)

| Setting | Decisión | Razón |
|---------|----------|--------|
| Group.officeWaitTimeParetoCoeff, Group2.officeWaitTimeParetoCoeff | **DESCARTAR** | Forma de la distribución de espera en oficina; ya usamos officeWaitTime_mean. No priorizado para diversidad. |
| Group.shoppingWaitTimeParetoCoeff, Group2.shoppingWaitTimeParetoCoeff | **DESCARTAR** | Idem; usamos shoppingWaitTime_mean. |
| Group.LinearMovement.initLocType, targetType | **DESCARTAR** | Solo 1 escenario (C8) con LinearMovement; valores 0/1 no aportan dimensión adicional respecto a mm_Linear. |

### 2.7 Opciones no usadas o sin uso en el corpus

| Setting | Decisión | Razón |
|---------|----------|--------|
| Group.okMaps | **DESCARTAR** | No utilizado de forma relevante en el corpus actual. |
| Events2.nrofPreload | **DESCARTAR** | Si existe, no define dimensión de diversidad prioritaria; Events2 ya cubierta por event2_interval_mean, event2_size_mean. |

### 2.8 Variantes Group2–Group12 (mismos criterios que Group/Group1)

Para **cualquier** clave que sea variante por grupo (Group2.*, Group3.*, … Group12.*):

- Si es **ruta, ID, referencia interna, router, routeType, nrofInterfaces**: **DESCARTAR** (misma razón que en Group/Group1).
- Si es **clusterCenter**: **DESCARTAR** (coordenadas).
- Si es **clusterRange**: **SÍ** se usa, vía el nuevo feature **clusterRange_mean** (agregado sobre todos los grupos con ClusterMovement).
- Si es **officeWaitTimeParetoCoeff, shoppingWaitTimeParetoCoeff, minAfterShoppingStopTime, maxAfterShoppingStopTime**: ya cubiertos por **officeWaitTime_mean**, **shoppingWaitTime_mean**, **afterShoppingStopTime_mean** (min/max de after-shopping se añaden).

---

## 3. Resumen ejecutivo

- **Features finales:** 46 (41 actuales + mm_Linear, clusterRange_mean, afterShoppingStopTime_mean, event2_interval_mean, event2_size_mean).
- **Todos los settings listados como "no utilizados"** quedan clasificados en este documento como **DESCARTADOS DEFINITIVOS** con razón, salvo los que pasan a formar parte de los 4 nuevos features.
- **Para la tesis:** Este documento es la referencia metodológica de qué se mide (y qué no) en la fase de preparación del corpus; evita ambigüedades tipo "posible extensión futura".

---

## 4. Próximo paso

Implementar en `run_analysis.py` los 4 nuevos features y actualizar `NOT_USED_REASONS` y el informe de features con las etiquetas **DESCARTADO: &lt;razón&gt;** según esta tabla.
