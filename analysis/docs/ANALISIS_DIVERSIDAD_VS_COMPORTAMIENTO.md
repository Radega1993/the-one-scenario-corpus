# Análisis: diversidad de escenarios vs. comportamiento de red

**Objetivo:** Aclarar qué mide actualmente la “diversidad” en el pipeline, cómo se relaciona con la definición de diversidad como *capacidad del corpus para representar una amplia gama de comportamientos de red y estructuras de conexión sin redundancia*, y qué implicaciones tiene **antes de seguir variando parámetros** en los escenarios Urban/Campus/Vehicle.

---

## 1. Definición de diversidad (contexto de la investigación)

En este contexto, **diversidad de escenarios** significa:

- Que el corpus represente una **amplitud de comportamientos de red** y **estructuras de conexión**.
- Evitar **redundancia**: no se trata solo de tener muchos escenarios, sino de que **cada uno aporte información única** sobre **cómo operaría un protocolo de enrutamiento**.

Por tanto, el criterio relevante es: *¿cada escenario aporta información distinta sobre el comportamiento del protocolo?*

---

## 2. Qué mide actualmente el pipeline (core 24)

### 2.1 Métrica actual: correlación en el espacio de **configuración** (inputs)

- Las **24 features core** son **parámetros de entrada** del escenario: tamaño y forma del mundo, N, tipos de movimiento, rango de transmisión, buffer, velocidad de transmisión, TTL, intervalo/tamaño de mensajes, workDayLength, etc.
- La “diversidad” se opera como: **correlación de Pearson entre vectores de escenario en el espacio Z_core (24D)**.
- Objetivos numéricos: sin duplicados (r=1), pocos pares con |r| ≥ 0.7 (<5% ideal).

**Conclusión:** Lo que medimos es **diversidad del espacio de configuración (inputs)** en 24 dimensiones, no diversidad de **comportamiento observado** ni de **estructura de contactos**.

### 2.2 Relación con el comportamiento del protocolo

- Los 24 parámetros **influyen** en el comportamiento (grafo de contactos, carga, pérdidas, retardos).
- Pero el comportamiento **no se observa** en este análisis: no usamos contactos, ni delivery ratio, ni latencia, ni estructura temporal de encuentros.
- Por tanto:
  - **Escenarios con vectores 24D muy parecidos** → es **plausible** que den comportamientos similares (mismos inputs ≈ mismo régimen).
  - **Escenarios con vectores 24D distintos** → **pueden** dar comportamientos distintos, pero no está garantizado (el comportamiento depende también de mapa concreto, semilla, distribución espacial no resumida en world_area/aspect_ratio, etc.).
- La correlación en 24D es así un **proxy de “potencial de redundancia”**, no una medida directa de “información única sobre el protocolo”.

---

## 3. Qué no capturamos (brecha metodológica)

| Dimensión | En core 24 | No capturado / no usado aquí |
|-----------|------------|------------------------------|
| **Estructura de contactos** | transmitRange, N, world_area, speed, wait | Topología real del grafo de contactos en el tiempo; distribución de inter-contact times; centralidad de nodos (p. ej. buses). |
| **Comportamiento del protocolo** | — | delivery_ratio, latency_mean, overhead_ratio, drop_ratio (existen en el pipeline como `--phase outputs` pero no definen la diversidad del corpus). |
| **Regime / tipo de escenario** | mm_*, nrofHostGroups | Identificación explícita de “regímenes” (urbano WDM+Bus, desastre, rural, social, tráfico extremo) y cobertura del espacio de regímenes. |
| **Detalle espacial/temporal** | world_area, aspect_ratio, workDayLength | Mapa concreto (Helsinki vs otro), rutas de bus, ubicación de oficinas/meeting spots; timeDiffSTD, nrOfOffices (en extended). |

- **Movimiento:** Tenemos *qué* modelo (WDM, Bus, RWP, etc.) pero no *cómo* se traduce en encuentros (p. ej. si dos escenarios WDM+Bus en el mismo mapa son realmente distintos en contacto o solo en un parámetro secundario).

---

## 4. Interpretación del bloque Urban/Campus/Vehicle (U1, U3, U8, U12, C5, C6, V4, V6, V8, …)

### 4.1 Por qué correlan tanto en 24D

- Comparten:
  - **Mismo régimen:** WDM + Bus sobre HelsinkiMedium.
  - **Mismo mundo:** mismo mapa (solo cambia worldSize en algunos), misma estructura de rutas/oficinas/meeting spots en la lógica del ONE.
  - **Mismo N** (o muy parecido): ~81 nodos (1 bus + 80 peatones en la mayoría).
  - **Mismas dimensiones binarias:** mm_WDM=1, mm_Bus=1, nrofHostGroups=2.

- Lo que hemos variado (workDayLength, bufferSize, transmitRange, Events1) son **variaciones dentro del mismo régimen**: mismo “tipo” de comportamiento de red (peatones + buses, mismo mapa), con distintos parámetros numéricos.

### 4.2 Redundancia de **configuración** vs. redundancia de **comportamiento**

- **Redundancia de configuración (24D):** Dos escenarios con r alto en 24D tienen inputs muy parecidos. Eso **sugiere** que podrían dar resultados de protocolo parecidos.
- **Redundancia de comportamiento:** Dos escenarios aportan **la misma información** sobre cómo se comporta el protocolo (p. ej. delivery ratio y latencia muy similares, o patrones de contacto equivalentes). Eso **no lo medimos** con la correlación en 24D.

- Variar bufferSize o event_interval_mean **diferencia el vector 24D** y puede bajar un poco la correlación, pero:
  - No cambia el **regime** (siguen siendo “urbano WDM+Bus”).
  - No sabemos sin simular si eso se traduce en **diferencias relevantes** en delivery, latencia o estructura de contactos.

Por tanto: **bajar |r| en 24D en este bloque no garantiza que cada escenario aporte “información única” sobre el comportamiento del protocolo**; solo que los vectores de entrada son más distintos.

---

## 5. Ablación 17 vs 24 vs 46 (recordatorio)

- En **espacio completo (46 features)** hay **92 pares (3,8%)** con |r| ≥ 0.7.
- En **core 24** hay **200 pares (8,3%)** con |r| ≥ 0.7.

Las 22 features extendidas (timeDiffSTD, nrOfOffices, officeWaitTime_mean, etc.) **sí separan** mejor los escenarios urbanos entre sí. Es decir: **hay información en la configuración que distingue escenarios y que hemos decidido no usar** como referencia de diversidad (para mantener el core corpus-wide e interpretable). Eso refuerza que:

- La “mala” diversidad en 24D del bloque Urban/Campus/Vehicle es en parte **por diseño** (pocas dimensiones WDM en core).
- Forzar más variación solo en las 24 core puede **mejorar el número** (menos pares con |r|≥0.7) sin que eso implique automáticamente **más diversidad de comportamiento**.

---

## 6. Recomendaciones antes de seguir variando parámetros

### 6.1 Dejar explícita la definición operativa de diversidad

- **Diversidad que medimos hoy:** Diversidad del **espacio de configuración** en 24D (inputs). Objetivo: evitar configuraciones casi idénticas (r=1) y reducir pares “muy similares” (|r|≥0.7).
- **Diversidad en sentido “información única sobre el protocolo”:** Requeriría, en general, considerar también **resultados de simulación** (delivery, latencia, overhead) o **estadísticas de contactos** (si se generan). El pipeline ya tiene `--phase outputs` para correlación en espacio de salida; no se usa como criterio principal de diversidad del corpus.

Recomendación: **Documentar en la metodología** (p. ej. en `docs/PLAN_CONTINUIDAD_CORE24.md` o en el documento de metodología del paper) que:
- La diversidad del corpus se evalúa en el **espacio de las 24 core (configuración)**.
- Se asume que **configuraciones más distintas en 24D tienden a dar comportamientos más distintos**, pero no se valida de forma explícita la diversidad en espacio de comportamiento salvo que se incorpore un análisis de outputs o de contactos.

### 6.2 Valorar “diversidad de regímenes” además de “diversidad en 24D”

- **Regime:** Tipo de escenario desde el punto de vista de red (urbano WDM+Bus, desastre, rural, RWP, tráfico extremo, etc.). Las mm_* y nrofHostGroups ya dan una proxy.
- El corpus **sí** cubre varios regímenes (Urban, Campus, Vehicle, Disaster, Social, Traffic, etc.). Donde hay “redundancia” es **dentro** del régimen Urban/Campus/Vehicle (muchos WDM+Bus HelsinkiMedium).
- Se puede:
  - **Aceptar** que dentro de ese régimen haya varios escenarios con vectores 24D parecidos y **documentarlo** como “variaciones de un mismo régimen urbano” (p. ej. para estudiar sensibilidad a workDayLength, bufferSize, etc.), en lugar de intentar que todos estén muy separados en 24D.
  - O **complementar** la métrica de pares |r|≥0.7 con una **cobertura de regímenes** (p. ej. que cada “cluster” o cada tipo mm_* esté representado) y con un techo razonable de escenarios “muy similares” por régimen.

### 6.3 Validación opcional con resultados de simulación

- Si se dispone de **output_metrics.csv** (delivery_ratio, latency_mean, overhead_ratio, drop_ratio) para muchos escenarios:
  - Ejecutar `--phase outputs` y revisar si los escenarios que están **muy correlacionados en 24D** están también **muy correlacionados en espacio de salida**. Si es así, la redundancia en 24D refleja redundancia en comportamiento.
  - Si dos escenarios tienen r alto en 24D pero **resultados de simulación muy distintos**, entonces la diversidad en 24D subestimaría la diversidad de comportamiento (otros factores —semilla, mapa— importan).
- El informe actual `outputs_correlation_report.txt` (63 escenarios, 48.7% pares con |r|≥0.7 en salida) indica que **también en resultados hay muchos pares similares**; sería útil cruzar qué pares son altos en 24D y cuáles en outputs.

### 6.4 Sobre seguir variando parámetros solo para bajar |r| en 24D

- **Pros:** Reduce la correlación en el espacio de referencia (24D), elimina duplicados y evita vectores casi idénticos.
- **Contras:**
  - No asegura que cada escenario aporte información **única sobre el comportamiento** del protocolo.
  - Puede generar escenarios “artificialmente” distintos en parámetros (p. ej. bufferSize 42M vs 48M vs 52M) que en la práctica se comporten de forma muy similar.
  - El bloque Urban/Campus/Vehicle seguirá siendo **el mismo régimen**; lo que se gana es más dispersión numérica en 24D, no necesariamente más variedad de comportamientos de red.

Recomendación: **Antes de una nueva ronda masiva de variación de parámetros**, decidir:

1. Si el objetivo prioritario es **cumplir un umbral numérico** (p. ej. <5% pares |r|≥0.7) por coherencia metodológica, o si es **maximizar la información única por escenario sobre el comportamiento del protocolo**.
2. Si se acepta que **varios escenarios del mismo régimen (WDM+Bus urbano) tengan vectores 24D relativamente cercanos**, documentándolo como “familia urbana” y justificando su presencia (p. ej. sensibilidad a parámetros, repetibilidad).
3. Si se quiere **complementar** la diversidad en 24D con:
   - un análisis de **outputs** (correlación 24D vs correlación en Y), o
   - una **narrativa por regímenes** (cobertura y tamaño de cada cluster comportamental).

---

## 7. Resumen

| Pregunta | Respuesta breve |
|----------|------------------|
| ¿Qué mide la “diversidad” actual? | Diversidad de **configuración** (vectores en 24D). No comportamiento ni estructura de contactos. |
| ¿Es lo mismo que “cada escenario aporte información única sobre el protocolo”? | No necesariamente. Es un **proxy**: configuraciones más distintas suelen poder dar comportamientos más distintos, pero no está verificado con datos de salida. |
| ¿Por qué U1, U3, U8, … correlan tanto? | Porque comparten **régimen** (WDM+Bus), **mapa** (HelsinkiMedium) y **N**; las 24 core tienen pocas dimensiones que los separen. |
| ¿Seguir variando bufferSize, Events1, etc. mejora “diversidad de comportamiento”? | Mejora dispersión en 24D; la mejora en diversidad de **comportamiento** es indirecta y no medida. |
| ¿Qué hacer antes de más variación? | (1) Dejar escrita la distinción diversidad de configuración vs. de comportamiento. (2) Decidir si se acepta 8% y “familia urbana” o se prioriza bajar a <5%. (3) Opcional: validar con `--phase outputs` o con estadísticas de contactos. (4) Considerar narrativa por regímenes además de métrica 24D. |

Este análisis sirve como base para decidir si conviene **seguir variando parámetros** con el único objetivo de bajar el % de pares |r|≥0.7, o **reorientar** el criterio hacia diversidad de regímenes y, si hay datos, hacia diversidad de resultados de protocolo.
