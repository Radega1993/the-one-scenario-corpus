# Roadmap — the-one-scenario-corpus

Líneas de continuación del proyecto tras la versión inicial. Objetivo de benchmark: corpus de escenarios **sin correlación lineal** entre ellos para estudiar protocolos de enrutamiento OppNet (ver [analysis/reports/observaciones_correlacion.md](analysis/reports/observaciones_correlacion.md)).

**Diagnóstico:** El problema no es estadístico (potencia baja con n=d=33) sino **geométrico**: muchos escenarios ocupan un subespacio pequeño (mismo mapa, mismo modelo WDM+HelsinkiMedium, misma estructura). Variar solo TTL, rate o tamaño de mensaje no cambia la estructura del grafo dinámico → alta correlación.

**Estrategia:** No añadir más escenarios del mismo estilo; **diferenciar** los que ya hay y añadir unos pocos **radicalmente distintos** (estructura espacial, régimen dinámico, régimen de recursos).

**Estado actual:** Corpus **corpus_v1** con **70** escenarios. Pasos 4.1 (clusterización), 4.2 (diversificación) y 4.3 (~10 escenarios radicales) realizados. Siguiente prioridad: documentación bilingüe (sección 1).

---

## 1. Documentación en inglés y castellano

**Objetivo:** Tener la documentación clave en ambos idiomas para alcance internacional y uso local; el principal es en inglés.

| Tarea | Descripción |
|-------|--------------|
| README bilingüe | Mantener `README.es.md` en castellano; `README.md` con versión en inglés del resumen del proyecto, estructura, comandos rápidos y enlace a la guía de configuración. |
| Guía .settings | Decidir si la guía larga (secciones 1–15) se duplica en inglés (`README.en.md` o `docs/configuration.en.md`) o solo se traduce el índice y las secciones más consultadas. |
| analysis/README | Mismo criterio: `analysis/README.es.md` en castellano; `analysis/README.md` en inglés con resumen del pipeline, fases y dashboard. |
| Comentarios en código | Opcional: docstrings y comentarios en `run_analysis.py` / `dashboard.py` en inglés para estándar de código. |

**Orden sugerido:** README principal (EN) → analysis/README (EN) → guía .settings (EN) si hace falta.

---

## 2. Wiki de GitHub (documentación fácil de buscar)

**Objetivo:** Wiki del repositorio con página principal del proyecto y una página por escenario (o por familia) para documentación navegable y buscable.

| Tarea | Descripción |
|-------|-------------|
| Página principal Wiki | Crear *Home* de la Wiki: nombre del proyecto, objetivo, enlace al corpus, al análisis y al dashboard, tabla de familias de escenarios con enlaces. |
| Página por familia | Una página por familia (Urban, Campus, Vehicles, Rural, Disaster, Social, Traffic): lista de escenarios, idea de cada uno, palancas principales. Enlazar a los `.settings` en el repo. |
| Página por escenario (opcional) | Si la Wiki lo permite, una página por escenario (ej. `U1-CBD-Commuting`) con: nombre, familia, idea, parámetros clave, enlace al fichero `.settings`. Útil para 70 escenarios si se genera con script. |
| Generación automática | Script (p. ej. `scenarios/scripts/generate_wiki_pages.py`) que lea `corpus_v1/`, `analysis/data/features.csv` y genere los Markdown de la Wiki para subirlos a GitHub. |
| Cómo publicar | Las Wikis de GitHub se editan en el repo (pestaña Wiki) o clonando el repo `*.wiki.git`. El script puede escribir en una carpeta `wiki/` en el repo y tú copias a la Wiki. |

**Orden sugerido:** Home + una página por familia (manual o script) → después automatizar páginas por escenario si quieres.

---

## 3. Diversidad del corpus: criterios y objetivos

**Criterios de diversidad (no solo |r|):**
- **|r| < 0,7** en ≥95% de pares (o 100% si se exige).
- **dist_coseno mínima > 0,05** (ningún par casi idéntico).
- **Ningún par con cos_dist < 0,05**.
- **Silhouette > 0,3** si se hace clustering (espacios bien separados).

**Objetivos realistas tras diversificar:** max |r| < 0,85; pares con |r| ≥ 0,7 **< 3%**; cos_dist mín > 0,05.

**Tres ejes para romper correlación:** (1) Estructura espacial: mapa distinto, clusters, partición, mule, grafo esparso vs completo. (2) Régimen dinámico: estacionario, periódico, burst, cambio de fase. (3) Régimen de recursos: extremos (buffer 256KB vs 200MB, rango 5m vs 200m, velocidad 0,2 vs 15 m/s).

## 4. Plan en tres pasos (escenarios) — realizados

| Paso | Acción | Estado |
|------|--------|--------|
| **4.1 Clusterizar** | Ward sobre Z → `cluster_assignments.csv`, `clustering_report.txt`. Por cluster: 3–4 representantes; modificar el resto (solo .settings) para empujarlos fuera. | Hecho |
| **4.2 Diversificar** | `scenarios_to_diversify.txt`: tocar .settings (speed, waitTime, transmitRange, nrOfOffices, nrOfMeetingSpots, workDayLength, timeDiffSTD, probGoShoppingAfterWork, TTL, buffer). | Hecho |
| **4.3 Añadir ~10 radicales** | Ver [plan_radical_scenarios.md](analysis/reports/plan_radical_scenarios.md): partición, mule único, rango masivo, TTL extremos, buffer microscópico, velocidad extrema, super-hubs, micro-comunidades, movilidad determinista. | Hecho |

Tras 4.1–4.3: ejecutar `run_analysis.py --corpus corpus_v1 --phase all` para actualizar métricas e informes.
