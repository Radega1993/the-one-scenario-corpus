# Roadmap

**Español** | [English](Roadmap)

---

Roadmap del proyecto: documentación, wiki y criterios de diversidad. Versión completa en el repo: **[ROADMAP.md](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/ROADMAP.md)** (inglés), **[ROADMAP.es.md](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/ROADMAP.es.md)** (castellano).

---

## Estado actual

- **corpus_v1**: 70 escenarios. Pasos 4.1 (clusterización), 4.2 (diversificación) y 4.3 (~10 escenarios radicales) **hechos**.
- **Siguiente prioridad**: Documentación bilingüe (sección 1) y wiki (sección 2).

---

## 1. Documentación (EN/ES)

- README y analysis/README en inglés; castellano en `.es.md`.
- Opcional: guía .settings y comentarios en código en inglés.

---

## 2. Wiki de GitHub

- Home, Quickstart, Methodology, Results, Corpus overview, familias de escenarios, catálogo de escenarios.
- Opcional: generación automática de páginas wiki por escenario a partir del corpus y features.

---

## 3. Diversidad del corpus: criterios y objetivos

- **|r| < 0,7** en ≥95 % de pares (o 100 %).
- **Distancia coseno mínima > 0,05**; ningún par con cos_dist < 0,05.
- **Silhouette > 0,3** si se usa clustering.
- Objetivos: max |r| < 0,85; pares con |r| ≥ 0,7 **< 3 %**; cos_dist mín > 0,05.

---

## 4. Plan de escenarios (completado)

- **4.1** Cluster (Ward) — Hecho  
- **4.2** Diversificar (scenarios_to_diversify.txt) — Hecho  
- **4.3** Añadir ~10 escenarios radicales — Hecho  

Tras cambios: ejecutar `run_analysis.py --corpus corpus_v1 --phase all` para actualizar métricas.

---

## Mantenimiento de la wiki

- Mantener Home y Quickstart alineados con el repo.
- Actualizar Results y Diversity status al re-ejecutar el análisis.
- Añadir o ampliar catálogo de escenarios y páginas por familia según convenga.
