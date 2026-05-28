# Validación de reorganización — `analysis/reports/`

**Fecha:** 2026-05-24  
**Auditor:** revisión post-reorg (plan corpus_v1)  
**Backup de referencia:** `analysis/reports_backup_20260524_145824.tar.gz`  
**Snapshot:** `analysis/reports/_reports_reorganization_before_20260524_145824.txt`

---

## Estado general: **PARTIAL**

La reorganización física y la wiki activa están en buen estado. Quedan **documentos de inventario desactualizados** (rutas planas y conteos antiguos) y **enlaces obsoletos en docs de `analysis/`** fuera de `.wiki-clone/`.

| Comprobación | Resultado |
|--------------|-----------|
| 1. Integridad vs backup/snapshot | **PASS** |
| 2. Raíz: `RESULTADOS_ACTUALES.md`, `paper_freeze_checklist.md` | **PASS** |
| 3. `reports/README.md` → informes movidos | **PASS** |
| 4. `.wiki-clone/` sin enlaces planos rotos | **PASS** |
| 5. Wiki menciona informes canónicos | **PASS** |
| 6. Wiki enlaza figuras mensajes / spatial | **PASS** |
| 7. Dashboard `list_markdown_reports()` recursivo | **PASS** |
| 8. `INVENTARIO.md` / `inventory_update_report.md` | **PARTIAL** |

---

## 1. Integridad de ficheros

- **Script:** `python3 scenarios/analysis/validate_reports_reorganization.py` → exit 0.
- **Basenames del snapshot (46):** todos presentes en el árbol nuevo.
- **Fichero adicional** (no en snapshot): `project/reports_reorganization_report.md` (esperado).
- **Backup tar:** presente (`reports_backup_20260524_145824.tar.gz`, ~74 KB).
- **Huérfanos:** ninguno detectado; `traffic_profiles/` vacía por diseño.

---

## 2. Raíz de `reports/`

| Fichero | Estado |
|---------|--------|
| `RESULTADOS_ACTUALES.md` | Presente |
| `paper_freeze_checklist.md` | Presente |
| `README.md` | Presente (índice 11 secciones) |

---

## 3. `reports/README.md`

Enlaces a informes **dentro del árbol `reports/`:** correctos (canonical, pipeline, validation, policies, paper_gate, spatial, wiki_meta, project, `_archive_local`).

Enlaces “externos” al directorio (válidos, no son errores de reorg):

- `../data/reports_reorganization_manifest.csv`
- `../SCRIPTS_INDEX.md`
- `../../.wiki-clone/`

---

## 4. Wiki `.wiki-clone/` — enlaces rotos

**Enlaces planos a informes movidos:** 0 en páginas activas.

Rutas canónicas verificadas:

| Informe | Páginas |
|---------|---------|
| `canonical/message_analysis_window_policy.md` | `11-Message-Analysis-Window.md`, `12-Benchmark-Protocol-Comparison.md` |
| `canonical/protocol_benchmark_kpi_policy.md` | `Home.md`, `12-Benchmark-Protocol-Comparison.md` |
| `canonical/traffic_profile_kpi_analysis.md` | `Home.md`, `04-Traffic-Profiles.md` |
| `canonical/spatial_vs_performance_analysis.md` | `08-Spatial-Occupancy.md` |
| `canonical/corpus_v1_benchmark_validation.md` | `Home.md` |

Raíz wiki: `RESULTADOS_ACTUALES.md`, `paper_freeze_checklist.md` — rutas correctas.

---

## 5. Figuras en wiki

| Recurso | Existe |
|---------|--------|
| `figures/message_creation_time_boxplot_by_tp.png` | Sí |
| `figures/message_creation_time_hist_by_tp.png` | Sí |
| `figures/aggregated/spatial_coverage_by_family.png` | Sí |

Referenciadas en `Home.md`; auditoría en `09-Message-Creation-Time.md` → `validation/message_creation_time_audit.md`.

---

## 6. Dashboard

[`dashboard/data_loaders.py`](../../dashboard/data_loaders.py) — `list_markdown_reports()`:

- Lista fijada vía `lib/report_paths` (rutas nuevas).
- **`REPORTS_ANALYSIS_DIR.rglob("*.md")`** para el resto de informes en subcarpetas.

*(Smoke test con pandas/Streamlit no ejecutado en este entorno.)*

---

## 7. Inventario

| Documento | Estado |
|-----------|--------|
| [`INVENTARIO.md`](../../../INVENTARIO.md) | **Parcial:** §3.4 sigue describiendo ficheros en **ruta plana** (`correlation_report.txt`, etc.) y cita **36 ficheros**; el árbol actual tiene **~47** ficheros con subcarpetas. Enlaces a `wiki_meta/` y `project/` en otras secciones sí actualizados. |
| [`inventory_update_report.md`](inventory_update_report.md) | **Desactualizado:** `analysis/reports/` files = **44** (pre-reorg); no menciona subcarpetas. |

Recomendado: regenerar `build_inventory_update_report.py` y actualizar §3.4 de `INVENTARIO.md` con el árbol de [`reports/README.md`](../README.md).

---

## Errores / enlaces rotos (activos, fuera de `_archive/`)

| Ubicación | Problema |
|-----------|----------|
| [`analysis/README.md`](../../README.md) | Rutas planas: `reports/features_report.md`, `reports/tp_validation_report.md`, `reports/protocol_benchmark_kpi_policy.md` |
| [`analysis/SCRIPTS_INDEX.md`](../../SCRIPTS_INDEX.md) | Salidas documentadas como `reports/correlation_report.txt`, `reports/features_report.md`, etc. (sin subcarpeta) |
| [`analysis/docs/README.md`](../../docs/README.md) | Enlaces a `../reports/correlation_report.txt`, `ablation_report.txt`, … (planos) |
| [`analysis/figures/README.md`](../../figures/README.md) | Cita `reports/correlation_report.txt` (plano) |

**No afectan** a scripts en ejecución (usan `lib/report_paths.py`). Sí confunden a lectores humanos.

---

## Ficheros huérfanos

Ninguno. Carpetas vacías: `traffic_profiles/` (reservada).

---

## Páginas wiki desactualizadas (contenido, no enlaces)

| Tema | Nota |
|------|------|
| `11-Limitations` dedicada | No existe; limitaciones repartidas en otras páginas |
| `12-Figures-and-Tables` | No existe; índice en `Home.md` → `FIGURES_AND_TABLES_INDEX.md` |
| `Home.md` — pending | Sigue listando tareas pre-freeze; coherente con `paper_freeze_checklist` |

No se detectaron referencias activas a `corpus_v3` como corpus en uso.

---

## Acciones recomendadas

1. **Actualizar §3.4 de [`INVENTARIO.md`](../../../INVENTARIO.md)** con subcarpetas y enlace a [`reports/README.md`](../README.md).
2. **Regenerar** [`inventory_update_report.md`](inventory_update_report.md) (`build_inventory_update_report.py`) tras contar ficheros post-reorg.
3. **Corregir rutas en** `analysis/README.md`, `SCRIPTS_INDEX.md`, `analysis/docs/README.md`, `analysis/figures/README.md` → `reports/pipeline/…`, `reports/canonical/…`, etc.
4. **Opcional:** añadir en `Home.md` enlace explícito a `paper_gate/paper_figures_tables_readiness.md`.
5. **Fuera de esta reorg:** re-simular `S1_StrongCommunities_SeparateClusters__TP03_ManySmall` sin overlays pesados para cerrar `error_probable` en benchmark (no bloquea validación de carpetas).

---

## Resumen ejecutivo

| Métrica | Valor |
|---------|-------|
| Ficheros perdidos | 0 |
| Wiki enlaces rotos (activa) | 0 |
| README reports (internos) | OK |
| Dashboard recursivo | OK |
| Docs inventario | Pendiente actualización |

**Veredicto:** la reorganización es **segura y trazable**; cerrar como **PASS** global requiere solo **actualizar inventario y docs de análisis** con las rutas nuevas.
