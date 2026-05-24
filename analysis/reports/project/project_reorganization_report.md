# Informe de reorganización del subproyecto `scenarios/`

**Fecha:** 2026-05-24  
**Objetivo:** Organizar el repositorio sin borrar artefactos, separando material histórico/obsoleto del pipeline activo para `corpus_v2` (720 escenarios) y la redacción del paper.

**Restricciones respetadas:**
- No se creó `corpus_v3/`.
- Solo `mkdir` + `mv` (sin `rm`).
- `corpus_v1/`, `corpus_v2/`, `corpus_dropped_v1/` intactos.
- `.wiki-clone/` activa sin cambios; `_legacy_pre_paper_rebuild/` no movido.

---

## 1. Comandos ejecutados

```bash
cd /home/raul/Documents/the-one/scenarios

mkdir -p _archive/{wiki,reports,docs,scripts,data}

# Wiki backups
mv wiki_backup_20260520_133207 _archive/wiki/
mv wiki_backup_20260520_133832 _archive/wiki/

# Reports históricos / v3 / obsoletos
mv analysis/reports/piloto_corpus_v2_30_resultados.md _archive/reports/
mv analysis/reports/piloto_corpus_v2_36_resultados.md _archive/reports/
mv analysis/reports/go_no_go_corpus_v2_12perfiles.md _archive/reports/
mv analysis/reports/corpus_v2_720_resultados.md _archive/reports/
mv analysis/reports/corpus_v3_design.md _archive/reports/
mv analysis/reports/corpus_v3_recommendation.md _archive/reports/
mv analysis/reports/mobility_realism_review.md _archive/reports/
mv analysis/reports/traffic_profile_review.md _archive/reports/
mv analysis/reports/realism_rules.md _archive/reports/
mv analysis/reports/map_realism_review.md _archive/reports/
mv analysis/reports/data_inventory.md _archive/reports/

# Docs pre-freeze y map profiles v3
mv analysis/docs/PLAN_CONTINUIDAD_CORE24.md _archive/docs/
mv analysis/docs/GUIA_ESTADO_Y_RESULTADOS.md _archive/docs/
mv maps/map_profiles.md _archive/docs/

# Scripts legacy corpus_v3
mv analysis/recommend_corpus_v3.py _archive/scripts/
mv analysis/compare_corpus_versions.py _archive/scripts/

# Data propuesta v3
mv analysis/data/corpus_v3_plan.csv _archive/data/
mv analysis/data/map_profile_plan.csv _archive/data/
```

---

## 2. Qué se movió y por qué

| Origen | Destino | Motivo |
|--------|---------|--------|
| `wiki_backup_20260520_133207/` | `_archive/wiki/` | Snapshot duplicado pre–paper-rebuild |
| `wiki_backup_20260520_133832/` | `_archive/wiki/` | Snapshot oficial wiki antigua (conservado) |
| `analysis/reports/piloto_corpus_v2_30_resultados.md` | `_archive/reports/` | Piloto 30 escenarios pre-freeze |
| `analysis/reports/piloto_corpus_v2_36_resultados.md` | `_archive/reports/` | Piloto 36 escenarios |
| `analysis/reports/go_no_go_corpus_v2_12perfiles.md` | `_archive/reports/` | Gate piloto 12 TP |
| `analysis/reports/corpus_v2_720_resultados.md` | `_archive/reports/` | Volcado temprano de resultados |
| `analysis/reports/corpus_v3_design.md` | `_archive/reports/` | Propuesta corpus_v3 no implementada |
| `analysis/reports/corpus_v3_recommendation.md` | `_archive/reports/` | Idem |
| `analysis/reports/mobility_realism_review.md` | `_archive/reports/` | Auditoría v3 |
| `analysis/reports/traffic_profile_review.md` | `_archive/reports/` | Auditoría v3 |
| `analysis/reports/realism_rules.md` | `_archive/reports/` | Reglas propuestas v3 |
| `analysis/reports/map_realism_review.md` | `_archive/reports/` | Auditoría mapas v3 |
| `analysis/reports/data_inventory.md` | `_archive/reports/` | Inventario auto obsoleto → `INVENTARIO.md` |
| `analysis/docs/PLAN_CONTINUIDAD_CORE24.md` | `_archive/docs/` | Pre-freeze core 24 |
| `analysis/docs/GUIA_ESTADO_Y_RESULTADOS.md` | `_archive/docs/` | Pre-freeze 70 escenarios |
| `maps/map_profiles.md` | `_archive/docs/` | Especificación map profiles v3 |
| `analysis/recommend_corpus_v3.py` | `_archive/scripts/` | Script legacy; propone corpus_v3 |
| `analysis/compare_corpus_versions.py` | `_archive/scripts/` | Diff v2/v3 (esqueleto) |
| `analysis/data/corpus_v3_plan.csv` | `_archive/data/` | Plan v3 no aplicado |
| `analysis/data/map_profile_plan.csv` | `_archive/data/` | Plan mapas v3 |

**Total ficheros en `_archive/`:** 465 (incluye 447 MD de los dos árboles wiki).

---

## 3. Referencias actualizadas

| Fichero | Cambio |
|---------|--------|
| `analysis/build_wiki_research_reports.py` | `BACKUP` → `_archive/wiki/wiki_backup_20260520_133832`; deja de regenerar `data_inventory.md` y `map_realism_review.md` |
| `analysis/docs/README.md` | Solo docs vigentes; enlace a `_archive/docs/` |
| `analysis/README.md` | Rutas legacy y wiki backup → `_archive/` |
| `corpus_v2/README.md` | Enlaces pilotos → `_archive/reports/` |
| `maps/README.md` | **Nuevo** — puntero a `map_profiles.md` archivado |
| `analysis/reports/wiki_old_audit.md` | Ruta backup actualizada |
| `analysis/reports/wiki_rebuild_summary.md` | Ruta backup + inventario |
| `analysis/reports/paper_phase1_action_plan.md` | Ruta backup actualizada |
| `INVENTARIO.md` | Secciones 2, 3.7, 5, 6 reflejan archivado |

**Sin cambiar (texto histórico en wiki):** `populate_wiki_paper.py` y páginas ya publicadas en `.wiki-clone/`.

---

## 4. Fuente canónica (activo)

| Área | Ubicación |
|------|-----------|
| Corpus benchmark | `corpus_v2/` (720 `.settings`, `manifest.csv`, `manifest_revision.csv`) |
| Corpus referencia | `corpus_v1/` (60), `corpus_dropped_v1/` (10) |
| Resultados freeze | `analysis/reports/RESULTADOS_ACTUALES.md` |
| Pipeline principal | `run_analysis.py`, `run_all_scenarios.py`, `run_figures_aggregated.py` |
| Análisis espacial / mensajes | `analyze_spatial_occupancy.py`, `analyze_message_creation_times.py` |
| Auditoría / diagnóstico | `audit_settings.py`, `diagnose_scenarios.py`, `validate_traffic_profiles.py` |
| Revisión v2 (trazabilidad) | `build_corpus_v2_revision_plan.py`, `apply_corpus_v2_revision.py` |
| Wiki paper | `.wiki-clone/` (19 páginas EN raíz) |
| Metodología vigente | `analysis/docs/features_core_vs_extended.md`, `features_decision.md`, … |
| Figuras paper | `analysis/figures/paper/` |
| Mapa del repo | `INVENTARIO.md` |
| Notas privadas | `internal/` (gitignored) |

**Scripts oficiales en `analysis/` (16):**  
`analysis_menu.py`, `analyze_message_creation_times.py`, `analyze_spatial_occupancy.py`, `apply_corpus_v2_revision.py`, `audit_settings.py`, `build_corpus_v2_revision_plan.py`, `build_wiki_research_reports.py`, `compute_useful_simulation_time.py`, `dashboard.py`, `diagnose_scenarios.py`, `generate_corpus_v2_traffic.py`, `populate_wiki_paper.py`, `run_all_scenarios.py`, `run_analysis.py`, `run_figures_aggregated.py`, `validate_traffic_profiles.py`

---

## 5. Generado (regenerable)

| Área | Contenido |
|------|-----------|
| `analysis/data/*.csv` | 37 CSV activos (features, correlaciones, outputs, espacial, TP, revisión v2) |
| `analysis/reports/` | ~23 informes MD/TXT del pipeline (correlación, ablación, auditorías operativas) |
| `analysis/figures/` | Heatmaps, agregados, paper, 720 spatial PNG |
| `../../reports/` | Salidas de simulación The ONE (costosas de regenerar) |

---

## 6. Histórico

| Área | Ubicación |
|------|-----------|
| Archivo centralizado | `_archive/` (wiki, pilotos, v3, pre-freeze) |
| Corpus v1 / dropped | `corpus_v1/`, `corpus_dropped_v1/` |
| Wiki legacy embebida | `.wiki-clone/_legacy_pre_paper_rebuild/` |
| Metodología tesis | `internal/` |

---

## 7. Ficheros ambiguos (no movidos)

| Fichero | Motivo para mantener en `analysis/reports/` |
|---------|-----------------------------------------------|
| `check_tp12_d2.md` | Chequeo puntual TP12; aún referenciado desde `corpus_v2/README.md` |
| `resumen_tp_excluyendo_no_contacto.md` | Resumen operativo TP |
| `build_corpus_v2_revision_plan.py` / `apply_corpus_v2_revision.py` | Trazabilidad revisión **v2 in-place** (decisión explícita) |
| `corpus_v2_revision_plan.md`, `corpus_v2_revision_changelog.md` | Plan y log de revisión aplicada |
| `wiki_old_audit.md`, `wiki_new_index.md`, `wiki_rebuild_summary.md` | Trazabilidad rebuild wiki paper |

---

## 8. Resumen final

| Categoría | Ubicación |
|-----------|-----------|
| **Corpus activo** | `corpus_v2/` — 720 escenarios |
| **Wiki activa** | `.wiki-clone/` — 19 páginas EN (paper-oriented) |
| **Scripts oficiales** | `analysis/*.py` — 16 scripts + `lib/` + `dashboard/` |
| **Reports oficiales** | `analysis/reports/` — ~23 ficheros (incl. `RESULTADOS_ACTUALES.md`) |
| **Mapa del proyecto** | `INVENTARIO.md` |
| **Artefactos archivados** | `_archive/` — 465 ficheros |

### Verificación post-reorganización

```
test ! -f analysis/recommend_corpus_v3.py          → OK (archivado)
test -f corpus_v2/manifest.csv                     → OK
test -f analysis/reports/RESULTADOS_ACTUALES.md    → OK
test -d .wiki-clone                                → OK
test -d _archive/wiki/wiki_backup_20260520_133832  → OK
```

---

## 7. Backup pre-freeze (2026-05-24, round 2)

| Item | Value |
|------|-------|
| Archive | `/home/raul/Documents/the-one/scenarios_backup_20260524_pre_freeze.tar.gz` |
| SHA-256 | `443560f6e4ea20c1d309b41202c2ba536afd9f16cd5e8a46bee7e34b926b577a` |
| Size | ~416 MB |
| Excludes | `.git`, `analysis/.venv`, `.wiki-clone/.git` |

## 8. Archivo adicional (2026-05-24, round 2)

| Origen | Destino | Etiqueta |
|--------|---------|----------|
| `corpus_dropped_v1/` | `_archive/corpus_dropped_v1/` | HISTÓRICO (10 escenarios v1 redundantes) |
| `.wiki-clone/_legacy_pre_paper_rebuild/` | `_archive/wiki/legacy_pre_paper_rebuild/` | LEGACY (wiki pre-round2) |

**Nota:** `corpus_v1/` y `corpus_v2/` permanecen en raíz; no se eliminó ningún fichero (`rm`).

---

*Generado como parte de la reorganización segura descrita en `INVENTARIO.md` §6.*
