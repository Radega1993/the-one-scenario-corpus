# Scenario catalog

**English** | [Español](Scenario-catalog-es)

---

Index of all **70 scenarios** in corpus_v1. Each scenario is one `.settings` file. Detailed per-scenario pages (ID, name, family, purpose, key parameters, .settings path) can be added over time.

---

## By family

| Family | Count | Scenario IDs | Folder |
|--------|-------|---------------|--------|
| Urban | 12 | U1–U12 | corpus_v1/01_urban/ |
| Campus | 8 | C1–C8 | corpus_v1/02_campus/ |
| Vehicles | 8 | V1–V8 | corpus_v1/03_vehicles/ |
| Rural | 12 | R1–R12 | corpus_v1/04_rural/ |
| Disaster | 9 | D1–D9 | corpus_v1/05_disaster/ |
| Social | 6 | S1–S6 | corpus_v1/06_social/ |
| Traffic | 15 | T1–T15 | corpus_v1/07_traffic/ |

---

## Family pages (with scenario tables)

- [Urban scenarios](Urban-scenarios)
- [Campus scenarios](Campus-scenarios)
- [Vehicle scenarios](Vehicle-scenarios)
- [Rural scenarios](Rural-scenarios)
- [Disaster scenarios](Disaster-scenarios)
- [Social scenarios](Social-scenarios)
- [Traffic scenarios](Traffic-scenarios)

---

## Per-scenario template (for future pages)

When adding a page per scenario, include:

- **Scenario ID** (e.g. U1, D2)
- **Name** (e.g. U1_CBD_Commuting_HelsinkiMedium)
- **Family**
- **Purpose** — What the scenario models
- **Mobility model** — e.g. WorkingDayMovement, RandomWaypoint
- **Key parameters** — speed, waitTime, transmitRange, workDayLength, TTL, buffer, etc.
- **Traffic profile** — interval, size, TTL
- **Resource constraints** — buffer, transmit speed
- **Settings file** — path in repo (e.g. `corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings`)

---

## See also

- [Corpus overview](Corpus-overview)
- [Quickstart](Quickstart) — How to run a single scenario or all
