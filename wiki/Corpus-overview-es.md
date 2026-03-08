# Visión del corpus

**Español** | [English](Corpus-overview)

---

El corpus **corpus_v1** contiene **70 escenarios** en **7 familias**. Cada escenario es un fichero `.settings` para el simulador [The ONE](https://akeranen.github.io/the-one/). Las familias se han elegido para cubrir distintos **regímenes de movilidad**, **patrones de tráfico** y **condiciones de recursos**, de modo que los protocolos de enrutamiento se evalúen en un benchmark diverso.

---

## Por qué 7 familias

- **Urban** — Movilidad urbana basada en mapa (p. ej. Helsinki), rutinas diarias, commuting, retail, ocio. Alta densidad, rango corto; modela peatones y tráfico mixto en ciudad.
- **Campus** — Eventos, clases, exámenes, estadios, festivales, conferencias. Patrones de contacto periódicos o en ráfagas.
- **Vehicles** — Taxis, buses, bus+peatón. Mayor velocidad, rutas; prueba protocolos bajo movilidad vehicular.
- **Rural** — Nodos dispersos, mundo grande, rango largo o muy corto, velocidades extremas. Baja conectividad, tolerante al retardo.
- **Disaster** — Refugios, zonas particionadas, mules, UAVs, movilidad errática, TTL crítico. Escenarios de estrés para resiliencia.
- **Social** — Comunidades (fuertes/débiles), reuniones periódicas, mezcla aleatoria, dos capas (p. ej. estudiantes+staff). Prueba el comportamiento del protocolo con estructura comunitaria.
- **Traffic** — Extremos de mensajes y recursos: muchos pequeños vs pocos grandes, TTL corto/largo, estrés de buffer, alta tasa + baja velocidad. Enfocado en diversidad de tráfico y recursos más que en movilidad.

En conjunto evitan un único escenario “válido para todo” y obligan a los protocolos a rendir en regímenes distintos.

---

## Escenarios por familia

| Familia | Carpeta | Cantidad | IDs |
|---------|---------|----------|-----|
| **Urban** | 01_urban | 12 | U1–U12 |
| **Campus** | 02_campus | 8 | C1–C8 |
| **Vehicles** | 03_vehicles | 8 | V1–V8 |
| **Rural** | 04_rural | 12 | R1–R12 |
| **Disaster** | 05_disaster | 9 | D1–D9 |
| **Social** | 06_social | 6 | S1–S6 |
| **Traffic** | 07_traffic | 15 | T1–T15 |
| **Total** | — | **70** | — |

---

## Papel en la evaluación de routing

- **Urban / Campus / Vehicles:** A menudo basados en mapa (p. ej. Helsinki); difieren en velocidad, tiempos de espera, jornada, meeting spots, bus vs peatón. Sirven para probar la sensibilidad del protocolo al **patrón de movilidad** y a la **tasa de contacto**.
- **Rural:** Disperso, rango largo o parámetros extremos (5 m / 200 m, velocidad muy baja/alta). Prueba **tolerancia al retardo** y **gestión de buffer**.
- **Disaster:** Partición, mules, TTL crítico. Prueba **alcanzabilidad** y **entrega time-critical**.
- **Social:** Estructura comunitaria y mezcla. Prueba el **reenvío** en presencia de clusters y puentes.
- **Traffic:** Misma o similar movilidad con distinto **tamaño de mensaje**, **TTL**, **buffer**, **tasa**. Prueba el **comportamiento del protocolo bajo carga y estrés de recursos**.

---

## Familias de escenarios (enlaces a páginas por familia)

*(Una página por familia con tabla de escenarios y descripción breve de cada uno.)*

- [Escenarios urbanos](Urban-scenarios-es) — U1–U12  
- [Escenarios campus](Campus-scenarios-es) — C1–C8  
- [Escenarios vehículos](Vehicle-scenarios-es) — V1–V8  
- [Escenarios rurales](Rural-scenarios-es) — R1–R12  
- [Escenarios desastre](Disaster-scenarios-es) — D1–D9  
- [Escenarios sociales](Social-scenarios-es) — S1–S6  
- [Escenarios tráfico](Traffic-scenarios-es) — T1–T15  

---

## Catálogo de escenarios

Para el **listado detallado y fichas por escenario** (ID, nombre, familia, propósito, parámetros clave, ruta .settings): ver [Catálogo de escenarios](Scenario-catalog-es).

---

## Ver también

- [Metodología](Methodology-es) — Cómo se diseñan escenarios y features  
- [Resumen de resultados](Results-overview-es) — Correlación y diversidad  
- [Quickstart](Quickstart-es) — Cómo ejecutar escenarios y análisis  
