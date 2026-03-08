# Catálogo de escenarios

**Español** | [English](Scenario-catalog)

---

Índice de los **70 escenarios** de corpus_v1. Cada escenario es un fichero `.settings`. Las fichas detalladas por escenario (ID, nombre, familia, propósito, parámetros clave, ruta .settings) se pueden ir añadiendo con el tiempo.

---

## Por familia

| Familia | Cantidad | IDs | Carpeta |
|---------|----------|-----|---------|
| Urban | 12 | U1–U12 | corpus_v1/01_urban/ |
| Campus | 8 | C1–C8 | corpus_v1/02_campus/ |
| Vehicles | 8 | V1–V8 | corpus_v1/03_vehicles/ |
| Rural | 12 | R1–R12 | corpus_v1/04_rural/ |
| Disaster | 9 | D1–D9 | corpus_v1/05_disaster/ |
| Social | 6 | S1–S6 | corpus_v1/06_social/ |
| Traffic | 15 | T1–T15 | corpus_v1/07_traffic/ |

---

## Páginas por familia (con tablas de escenarios)

- [Escenarios urbanos](Urban-scenarios-es)
- [Escenarios campus](Campus-scenarios-es)
- [Escenarios vehículos](Vehicle-scenarios-es)
- [Escenarios rurales](Rural-scenarios-es)
- [Escenarios desastre](Disaster-scenarios-es)
- [Escenarios sociales](Social-scenarios-es)
- [Escenarios tráfico](Traffic-scenarios-es)

---

## Plantilla por escenario (para páginas futuras)

Al añadir una página por escenario, incluir:

- **ID** (p. ej. U1, D2)
- **Nombre** (p. ej. U1_CBD_Commuting_HelsinkiMedium)
- **Familia**
- **Propósito** — Qué modela el escenario
- **Modelo de movilidad** — p. ej. WorkingDayMovement, RandomWaypoint
- **Parámetros clave** — speed, waitTime, transmitRange, workDayLength, TTL, buffer, etc.
- **Perfil de tráfico** — interval, size, TTL
- **Restricciones de recursos** — buffer, transmit speed
- **Fichero .settings** — ruta en el repo (p. ej. `corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings`)

---

## Ver también

- [Visión del corpus](Corpus-overview-es)
- [Quickstart](Quickstart-es) — Cómo ejecutar un escenario o todos
