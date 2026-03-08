# Corpus overview

**English** | [Español](Corpus-overview-es)

---

The corpus **corpus_v1** contains **70 scenarios** in **7 families**. Each scenario is one `.settings` file for the [The ONE](https://akeranen.github.io/the-one/) simulator. The families are chosen to cover different **mobility regimes**, **traffic patterns**, and **resource conditions** so that routing protocols can be evaluated on a diverse benchmark.

---

## Why 7 families?

- **Urban** — Map-based urban mobility (e.g. Helsinki), daily routines, commuting, retail, nightlife. High density, short range; models city pedestrian and mixed traffic.
- **Campus** — Events, classes, exams, stadiums, festivals, conferences. Periodic or bursty contact patterns.
- **Vehicles** — Taxis, buses, mixed bus+pedestrian. Higher speed, routes; tests protocols under vehicular mobility.
- **Rural** — Sparse nodes, large world, long range or very short range, extreme speeds. Low connectivity, delay-tolerant.
- **Disaster** — Shelters, partitioned areas, mules, UAVs, erratic mobility, critical TTL. Stress scenarios for resilience.
- **Social** — Communities (strong/weak), periodic meetings, random mixing, two-layer (e.g. students+staff). Tests protocol behaviour under community structure.
- **Traffic** — Message and resource extremes: many small vs few huge messages, short vs long TTL, buffer stress, high rate + low speed. Focus on traffic and resource diversity rather than mobility.

Together they avoid a single “one size fits all” scenario and force protocols to perform across different regimes.

---

## Scenarios per family

| Family | Folder | Count | IDs |
|--------|--------|-------|-----|
| **Urban** | 01_urban | 12 | U1–U12 |
| **Campus** | 02_campus | 8 | C1–C8 |
| **Vehicles** | 03_vehicles | 8 | V1–V8 |
| **Rural** | 04_rural | 12 | R1–R12 |
| **Disaster** | 05_disaster | 9 | D1–D9 |
| **Social** | 06_social | 6 | S1–S6 |
| **Traffic** | 07_traffic | 15 | T1–T15 |
| **Total** | — | **70** | — |

---

## Role in routing evaluation

- **Urban / Campus / Vehicles:** Often map-based (e.g. Helsinki); differ in speed, wait times, workday length, meeting spots, bus vs pedestrian. Good for testing protocol sensitivity to **mobility pattern** and **contact rate**.
- **Rural:** Sparse, long range or extreme parameters (5 m / 200 m range, very low/high speed). Tests **delay tolerance** and **buffer management**.
- **Disaster:** Partitioning, mules, critical TTL. Tests **reachability** and **time-critical delivery**.
- **Social:** Community structure and mixing. Tests **forwarding** in the presence of clusters and bridges.
- **Traffic:** Same or similar mobility with different **message size**, **TTL**, **buffer**, **rate**. Tests **protocol behaviour under load and resource stress**.

---

## Scenario families (links to family pages)

*(One page per family with scenario table and short description of each.)*

- [Urban scenarios](Urban-scenarios) — U1–U12  
- [Campus scenarios](Campus-scenarios) — C1–C8  
- [Vehicle scenarios](Vehicle-scenarios) — V1–V8  
- [Rural scenarios](Rural-scenarios) — R1–R12  
- [Disaster scenarios](Disaster-scenarios) — D1–D9  
- [Social scenarios](Social-scenarios) — S1–S6  
- [Traffic scenarios](Traffic-scenarios) — T1–T15  

---

## Scenario catalog

For a **detailed list and per-scenario pages** (ID, name, family, purpose, key parameters, .settings path): see [Scenario catalog](Scenario-catalog).

---

## See also

- [Methodology](Methodology) — How scenarios and features are designed  
- [Results overview](Results-overview) — Correlation and diversity results  
- [Quickstart](Quickstart) — How to run scenarios and analysis  
