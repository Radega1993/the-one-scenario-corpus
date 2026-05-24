# Inventario detallado de `analysis/reports/`

**Generado:** 2026-05-24  
**Directorio:** `scenarios/analysis/reports/` — **46 ficheros** en subcarpetas temáticas (reorg aplicada 2026-05-24).  
**Corpus activo:** `corpus_v2` (720 simulaciones).  
**Propósito:** base para reorganizar informes sin perder trazabilidad paper.

---

## Resumen ejecutivo

| Métrica | Valor |
|---------|------:|
| Total ficheros | 46 |
| Markdown (`.md`) | 32 |
| Texto plano (`.txt`) | 12 |
| Referencia canónica única | [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md) |
| Gate freeze formal | [`paper_freeze_checklist.md`](paper_freeze_checklist.md) |
| Candidatos a archivar | ~8 (notas antiguas, duplicados, punteros) |

### Leyenda de etiquetas

| Etiqueta | Significado |
|----------|-------------|
| **FUENTE** | Redactado o mantenido a mano; versionar en git |
| **GENERADO** | Salida de script; regenerable |
| **CANÓNICO** | Referencia para el paper / tesis |
| **AUXILIAR** | Soporte operativo o exploración |
| **LEGACY** | Pre-freeze, superseded o nota puntual antigua |
| **DUPLICADO** | Contenido cubierto por otro informe más nuevo |

### Estructura aplicada (2026-05-24)

Ver [README.md](../README.md) y [reports_reorganization_report.md](reports_reorganization_report.md).  
Manifiesto CSV: [../../data/reports_reorganization_manifest.csv](../../data/reports_reorganization_manifest.csv).

---

## Índice por categoría recomendada

### A. Canónicos paper / tesis

| Fichero | Líneas | Etiqueta | Generador |
|---------|-------:|----------|-----------|
| [RESULTADOS_ACTUALES.md](RESULTADOS_ACTUALES.md) | 36 | GENERADO · **CANÓNICO** | `run_analysis.py` (fase correlation / freeze) |
| [traffic_profile_kpi_analysis.md](traffic_profile_kpi_analysis.md) | 191 | GENERADO · **CANÓNICO** | `analyze_traffic_profile_kpis.py` |
| [protocol_benchmark_kpi_policy.md](protocol_benchmark_kpi_policy.md) | 72 | GENERADO · **CANÓNICO** | `build_protocol_benchmark_kpi_policy.py` |
| [message_analysis_window_policy.md](message_analysis_window_policy.md) | 130 | GENERADO · **CANÓNICO** | `build_message_analysis_window_policy.py` |
| [spatial_vs_performance_analysis.md](spatial_vs_performance_analysis.md) | 46 | GENERADO · **CANÓNICO** | `analyze_spatial_vs_performance.py` |
| [corpus_v2_benchmark_validation.md](corpus_v2_benchmark_validation.md) | 135 | GENERADO · **CANÓNICO** | `validate_corpus_v2_benchmark.py` |

### B. Gate y readiness paper

| Fichero | Líneas | Etiqueta | Generador |
|---------|-------:|----------|-----------|
| [paper_freeze_checklist.md](paper_freeze_checklist.md) | 192 | GENERADO · **CANÓNICO** | `build_paper_freeze_checklist.py` |
| [paper_figures_tables_readiness.md](paper_figures_tables_readiness.md) | 88 | GENERADO | `build_paper_figures_tables_index.py` |
| [dashboard_readiness_report.md](dashboard_readiness_report.md) | 71 | GENERADO | `build_paper_figures_tables_index.py` / dashboard loaders |
| [paper_phase1_action_plan.md](paper_phase1_action_plan.md) | 57 | GENERADO | `build_wiki_research_reports.py` |

### C. Pipeline `run_analysis.py` (texto + enlaces a `data/`)

| Fichero | Líneas | Etiqueta | Fase / notas |
|---------|-------:|----------|----------------|
| [features_report.txt](features_report.txt) | 440 | GENERADO | `--phase features_report` |
| [features_report.md](features_report.md) | 140 | GENERADO | idem (versión MD) |
| [correlation_report.txt](correlation_report.txt) | 71 | GENERADO | `--phase correlation` (espacio 46) |
| [correlation_core23_report.txt](correlation_core23_report.txt) | 44 | GENERADO | core-23 |
| [feature_feature_correlation_report.txt](feature_feature_correlation_report.txt) | 7 | GENERADO | `--phase feature_correlation` |
| [ablation_report.txt](ablation_report.txt) | 8 | GENERADO | `--phase ablation` |
| [multiple_comparisons_report.txt](multiple_comparisons_report.txt) | 14 | GENERADO | FDR / Bonferroni |
| [outputs_correlation_report.txt](outputs_correlation_report.txt) | 18 | GENERADO | `--phase outputs` |
| [scenarios_to_diversify.txt](scenarios_to_diversify.txt) | 723 | GENERADO | lista escenarios \|r\|≥0.7 (46 feat) |
| [scenarios_to_diversify_core23.txt](scenarios_to_diversify_core23.txt) | 721 | GENERADO | idem core-23 |
| [clustering_report.txt](clustering_report.txt) | 736 | GENERADO | Ward k=7; muy largo (operativo) |
| [indirect_features_report.txt](indirect_features_report.txt) | 27 | GENERADO | `--phase indirects` |
| [indirect_features_report.md](indirect_features_report.md) | 34 | GENERADO | idem |

**Datos asociados (no en `reports/`):** `data/correlation_pearson.csv`, `data/ablation_metrics.csv`, `data/cluster_assignments.csv`, etc.

### D. Validación y auditoría de escenarios

| Fichero | Líneas | Etiqueta | Generador |
|---------|-------:|----------|-----------|
| [settings_audit.md](settings_audit.md) | 69 | GENERADO | `audit_settings.py` |
| [scenario_diagnosis.md](scenario_diagnosis.md) | 53 | GENERADO | `diagnose_scenarios.py` |
| [tp_validation_report.md](tp_validation_report.md) | 63 | GENERADO | `validate_traffic_profiles.py` |
| [message_creation_time_audit.md](message_creation_time_audit.md) | 77 | GENERADO | `analyze_message_creation_times.py` |
| [evaluation_metrics_review.md](evaluation_metrics_review.md) | 47 | GENERADO | `build_wiki_research_reports.py` |
| [current_results_review.md](current_results_review.md) | 69 | GENERADO | `build_wiki_research_reports.py` |

### E. Espacial y tiempo útil

| Fichero | Líneas | Etiqueta | Generador |
|---------|-------:|----------|-----------|
| [spatial_occupancy_report.md](spatial_occupancy_report.md) | 73 | FUENTE / GENERADO | Metodología; base `analyze_spatial_occupancy.py` |
| [spatial_occupancy_analysis_summary.md](spatial_occupancy_analysis_summary.md) | 5 | GENERADO · **LEGACY** | Puntero → `spatial_vs_performance_analysis.md` |
| [useful_simulation_time_report.md](useful_simulation_time_report.md) | 175 | GENERADO | `compute_useful_simulation_time.py` |
| [simulation_time_policy.md](simulation_time_policy.md) | 24 | GENERADO | `build_wiki_research_reports.py` + CSV |

### F. Corpus v2 revisión in-place

| Fichero | Líneas | Etiqueta | Generador |
|---------|-------:|----------|-----------|
| [corpus_v2_revision_plan.md](corpus_v2_revision_plan.md) | 165 | GENERADO | `build_corpus_v2_revision_plan.py` |
| [corpus_v2_revision_changelog.md](corpus_v2_revision_changelog.md) | 262 | GENERADO | `apply_corpus_v2_revision.py` |

### G. Wiki y documentación meta

| Fichero | Líneas | Etiqueta | Generador |
|---------|-------:|----------|-----------|
| [wiki_paper_rebuild_report.md](wiki_paper_rebuild_report.md) | 134 | FUENTE / GENERADO | Proceso rebuild round2 |
| [wiki_rebuild_summary.md](wiki_rebuild_summary.md) | 83 | GENERADO | `build_wiki_research_reports.py` |
| [wiki_new_index.md](wiki_new_index.md) | 26 | GENERADO | `build_wiki_research_reports.py` |
| [wiki_old_audit.md](wiki_old_audit.md) | 85 | GENERADO | `build_wiki_research_reports.py` |

### H. Proyecto / inventario

| Fichero | Líneas | Etiqueta | Generador |
|---------|-------:|----------|-----------|
| [project_reorganization_report.md](project_reorganization_report.md) | 200 | FUENTE | Informe reorganización repo |
| [inventory_update_report.md](inventory_update_report.md) | 31 | GENERADO | `build_inventory_update_report.py` |

### I. Legacy / notas puntuales (candidatos a `_archive/reports/`)

| Fichero | Líneas | Etiqueta | Notas |
|---------|-------:|----------|-------|
| [trace_realism_audit.md](trace_realism_audit.md) | 276 | LEGACY | 2026-05-19; auditoría estática v1+v2; sin script activo en `analysis/` |
| [check_tp12_d2.md](check_tp12_d2.md) | 32 | LEGACY | 2026-04-29; chequeo puntual D2/TP12 |
| [resumen_tp_excluyendo_no_contacto.md](resumen_tp_excluyendo_no_contacto.md) | 25 | LEGACY | 2026-04-29; tabla TP sin enc=0 |

---

## Ficha detallada por fichero (orden alfabético)

### `ablation_report.txt`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · pipeline |
| **Script** | `run_analysis.py --phase ablation` |
| **Contenido** | Métricas ablación reduced_17 / core_23 / full_46: max \|r\|, pares ≥0.7, silhouette |
| **Paper** | Methods — ablación; citado en `RESULTADOS_ACTUALES.md` |
| **CSV relacionado** | `data/ablation_metrics.csv` |
| **Reorganización** | → `pipeline/` |
| **Acción** | Mantener; regenerar con corpus_v2 |

---

### `check_tp12_d2.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | LEGACY · nota manual |
| **Fecha** | 2026-04-29 |
| **Contenido** | Verificación técnica TP12 en escenario D2 (grupos, hosts) |
| **Paper** | Solo si se discute TP12 partition en Methods |
| **Reorganización** | → `_archive/reports/notes/` o `reports/_archive_local/` |
| **Acción** | Archivar; extraer hechos únicos a wiki `04-Traffic-Profiles` si faltan |

---

### `clustering_report.txt`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · pipeline |
| **Script** | `run_analysis.py --phase correlation` (clustering Ward) |
| **Contenido** | Listado largo de escenarios por cluster (7 clusters); sugerencias diversificación |
| **Paper** | Supplementary / operativo interno |
| **CSV** | `data/cluster_assignments.csv` |
| **Reorganización** | → `pipeline/` |
| **Acción** | Mantener pero **no** enlazar desde README principal (demasiado verbose) |

---

### `corpus_v2_benchmark_validation.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · **CANÓNICO** |
| **Script** | `validate_corpus_v2_benchmark.py` |
| **Contenido** | Conteos validation_status, completitud 720, error_probable, recomendaciones splits |
| **Paper** | Methods (limitaciones), Discussion |
| **CSV** | `data/corpus_v2_benchmark_validation.csv` |
| **Reorganización** | → `canonical/` o `validation/` |
| **Acción** | Regenerar tras re-sims / cambios output_metrics |

---

### `corpus_v2_revision_changelog.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · histórico aplicado |
| **Script** | `apply_corpus_v2_revision.py` |
| **Contenido** | Log detallado de cambios .settings (mapas Manhattan, worldSize, etc.) |
| **Paper** | Methods — transparencia revisión corpus |
| **Reorganización** | → `project/` |
| **Acción** | Mantener; no regenerar salvo nueva revisión |

---

### `corpus_v2_revision_plan.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `build_corpus_v2_revision_plan.py` |
| **Contenido** | Plan priorizado P0/P1; acciones por escenario base |
| **CSV** | `data/corpus_v2_revision_prioritized.csv`, `manifest_revision.csv` |
| **Reorganización** | → `project/` |
| **Acción** | Mantener como documento de diseño; puede quedar parcialmente ejecutado |

---

### `correlation_core23_report.txt`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · pipeline |
| **Script** | `run_analysis.py --phase correlation` (core 23) |
| **Contenido** | max \|r\|, pares ≥0.7 en espacio core-23 (n=720) |
| **Paper** | **Principal** para diversidad Methods |
| **Duplicado parcial** | Resumido en `RESULTADOS_ACTUALES.md` |
| **Reorganización** | → `pipeline/` |
| **Acción** | Mantener |

---

### `correlation_report.txt`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · pipeline |
| **Script** | `run_analysis.py --phase correlation` (46 features) |
| **Contenido** | Estadísticos correlación espacio completo |
| **Paper** | Supplementary vs core-23 |
| **Reorganización** | → `pipeline/` |
| **Acción** | Mantener |

---

### `current_results_review.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · snapshot |
| **Script** | `build_wiki_research_reports.py` |
| **Contenido** | Conteos delivery=0, latencia vacía, etc. sobre `output_metrics.csv` |
| **Paper** | AUXILIAR — puede desactualizarse |
| **Duplicado** | Solapa con `corpus_v2_benchmark_validation.md` |
| **Reorganización** | → `validation/` o fusionar en benchmark validation |
| **Acción** | Regenerar o archivar si benchmark validation es suficiente |

---

### `dashboard_readiness_report.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `dashboard/data_loaders.write_dashboard_readiness_report()` vía `build_paper_figures_tables_index.py` |
| **Contenido** | Páginas dashboard ↔ datos paper |
| **Paper** | No en paper; herramienta exploración |
| **Reorganización** | → `paper_gate/` |
| **Acción** | Mantener junto a freeze checklist |

---

### `evaluation_metrics_review.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `build_wiki_research_reports.py` |
| **Contenido** | Definición métricas routing desde MessageStatsReport |
| **Paper** | Methods — métricas |
| **Duplicado parcial** | `protocol_benchmark_kpi_policy.md`, wiki `07-Output-Metrics` |
| **Reorganización** | → `policies/` o `validation/` |
| **Acción** | Mantener hasta unificar con protocol policy |

---

### `feature_feature_correlation_report.txt`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · pipeline |
| **Script** | `run_analysis.py --phase feature_correlation` |
| **Contenido** | Par alto mm_WDM ↔ mm_Bus (0.9393) |
| **Paper** | Methods — justificación core-23 |
| **Figura** | `figures/heatmap_feature_feature_core.png` |
| **Reorganización** | → `pipeline/` |
| **Acción** | Mantener |

---

### `features_report.md` / `features_report.txt`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · pipeline |
| **Script** | `run_analysis.py --phase features_report` |
| **Contenido** | Lista 46 features usados/descartados y origen en .settings |
| **Paper** | Methods — feature space |
| **Nota** | `.md` más legible; `.txt` es dump largo |
| **Reorganización** | → `pipeline/` (conservar ambos o solo `.md`) |
| **Acción** | Mantener `.md` como canónico; `.txt` opcional para diff |

---

### `indirect_features_report.md` / `.txt`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `run_analysis.py --phase indirects` |
| **Contenido** | Cobertura ConnectivityONEReport, encounters, contact_time |
| **CSV** | `data/indirect_features_diego.csv` |
| **Reorganización** | → `pipeline/` |
| **Acción** | Mantener `.md`; `.txt` redundante menor |

---

### `inventory_update_report.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `build_inventory_update_report.py` |
| **Contenido** | Conteos filesystem post-reorganización |
| **Reorganización** | → `project/` |
| **Acción** | Regenerar tras cada mv masivo |

---

### `message_analysis_window_policy.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · **CANÓNICO** |
| **Script** | `build_message_analysis_window_policy.py` |
| **Contenido** | Política ventana mensajes: full window primario; censura 10% opcional |
| **CSV** | `message_analysis_window_policy.csv`, `message_analysis_window_by_tp.csv` |
| **Paper** | Methods — obligatorio |
| **Reorganización** | → `policies/` |
| **Acción** | No sobrescribir con borradores wiki antiguos |

---

### `message_creation_time_audit.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `analyze_message_creation_times.py` |
| **Contenido** | Método replicación MessageEventGenerator; validación vs reports |
| **Paper** | Methods / Supplementary |
| **Enlace** | Complementa `message_analysis_window_policy.md` |
| **Reorganización** | → `traffic_profiles/` o `policies/` |
| **Acción** | Mantener |

---

### `multiple_comparisons_report.txt`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · pipeline |
| **Script** | `run_analysis.py --phase correlation` |
| **Contenido** | FDR y Bonferroni sobre pares correlacionados |
| **Paper** | Methods — rigor estadístico |
| **Reorganización** | → `pipeline/` |
| **Acción** | Mantener |

---

### `outputs_correlation_report.txt`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · pipeline |
| **Script** | `run_analysis.py --phase outputs` |
| **Contenido** | Correlación entre vectores de métricas de salida (alta colinealidad ~53% pares ≥0.7) |
| **Paper** | Discussion — outputs no independientes |
| **Reorganización** | → `pipeline/` |
| **Acción** | Mantener |

---

### `paper_figures_tables_readiness.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `build_paper_figures_tables_index.py` |
| **Contenido** | Estado lista/revisar figuras y tablas paper |
| **Enlace** | `figures/paper/FIGURES_AND_TABLES_INDEX.md` |
| **Reorganización** | → `paper_gate/` |
| **Acción** | Regenerar tras `figures_paper` |

---

### `paper_freeze_checklist.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · **CANÓNICO** gate |
| **Script** | `build_paper_freeze_checklist.py` |
| **CSV** | `data/paper_freeze_checklist.csv` |
| **Contenido** | 48 ítems DONE/PARTIAL/MISSING; recomendación READY_* |
| **Reorganización** | → `paper_gate/` (o raíz `reports/` por visibilidad) |
| **Acción** | Ejecutar antes de escribir tesis |

---

### `paper_phase1_action_plan.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · planificación |
| **Script** | `build_wiki_research_reports.py` |
| **Contenido** | Decisiones cerradas fase 1 paper (synthetic benchmark, corpus_v2) |
| **Reorganización** | → `paper_gate/` o `project/` |
| **Acción** | Mantener como histórico de decisiones; actualizar si cambia alcance |

---

### `project_reorganization_report.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | FUENTE · **CANÓNICO** operaciones |
| **Contenido** | mv a `_archive/`, backup tar, rutas activas |
| **Reorganización** | → `project/` |
| **Acción** | Ampliar con cada reorganización de `reports/` |

---

### `protocol_benchmark_kpi_policy.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · **CANÓNICO** |
| **Script** | `build_protocol_benchmark_kpi_policy.py` |
| **CSV** | `data/protocol_benchmark_kpi_definitions.csv` |
| **Contenido** | Core-4 KPIs, tiers main/stress/control, overlays protocolo |
| **Reorganización** | → `policies/` |
| **Acción** | Regenerar si cambian splits o KPIs TP |

---

### `RESULTADOS_ACTUALES.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · **REFERENCIA ÚNICA** |
| **Script** | `run_analysis.py` (actualización al final de pipeline) |
| **Contenido** | Números congelados diversidad core/full, enlaces a informes pipeline |
| **Paper** | Results — citar siempre desde aquí |
| **Reorganización** | → `canonical/` o **raíz** `reports/` |
| **Acción** | **No duplicar** cifras en otros MD sin actualizar este |

---

### `resumen_tp_excluyendo_no_contacto.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | LEGACY |
| **Fecha** | 2026-04-29 |
| **Contenido** | Tabla medias TP excluyendo total_encounters=0 |
| **Duplicado** | `traffic_profile_kpi_analysis.md` |
| **Reorganización** | → `_archive/reports/` |
| **Acción** | Archivar |

---

### `scenario_diagnosis.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `diagnose_scenarios.py` |
| **Contenido** | Flags P0/P1/P2, problem_flags por escenario |
| **CSV** | `data/scenario_diagnosis.csv` |
| **Paper** | Methods limitaciones; dashboard Diagnóstico |
| **Reorganización** | → `validation/` |
| **Acción** | Regenerar tras cambios settings |

---

### `scenarios_to_diversify.txt` / `scenarios_to_diversify_core23.txt`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · listas operativas |
| **Script** | `run_analysis.py --phase correlation` |
| **Contenido** | 720 escenarios con conteo pares \|r\|≥0.7 |
| **Paper** | No publicar listado completo |
| **Reorganización** | → `pipeline/lists/` |
| **Acción** | Mantener para investigación; opcional comprimir |

---

### `settings_audit.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `audit_settings.py` |
| **Contenido** | Resumen auditoría .settings (mapas, TP, hosts) |
| **CSV** | `data/settings_audit.csv` |
| **Reorganización** | → `validation/` |
| **Acción** | Regenerar si cambia corpus |

---

### `simulation_time_policy.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `build_wiki_research_reports.py` (+ CSV) |
| **Contenido** | Política endTime / worldSize (no confundir con ventana mensajes) |
| **CSV** | `data/simulation_time_policy.csv` |
| **Reorganización** | → `policies/` |
| **Acción** | Mantener; enlazar desde wiki `10-Simulation-Time-Policy` |

---

### `spatial_occupancy_analysis_summary.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · **LEGACY puntero** |
| **Script** | `analyze_spatial_occupancy.py` (reescrito por `analyze_spatial_vs_performance.py`) |
| **Contenido** | 5 líneas — redirige a informes nuevos |
| **Reorganización** | → `_archive_local/` o eliminar tras actualizar enlaces |
| **Acción** | Mantener solo como redirect; no regenerar contenido largo aquí |

---

### `spatial_occupancy_report.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | FUENTE metodológico |
| **Contenido** | Definición ocupación espacial, SpatialOccupancyReport, enlaces tiempo útil |
| **Paper** | Methods — spatial methodology |
| **Reorganización** | → `spatial/` |
| **Acción** | Mantener estable |

---

### `spatial_vs_performance_analysis.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · **CANÓNICO** |
| **Script** | `analyze_spatial_vs_performance.py` |
| **Contenido** | r cobertura vs delivery; medianas por familia |
| **Paper** | Results / Discussion spatial |
| **Reorganización** | → `spatial/` o `canonical/` |
| **Acción** | Regenerar si cambian CSVs espaciales |

---

### `tp_validation_report.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `validate_traffic_profiles.py` |
| **Contenido** | Integridad 720 settings vs intención TP01–TP12 |
| **CSV** | `tp_validation_settings.csv`, `tp_validation_summary.csv` |
| **Reorganización** | → `traffic_profiles/` |
| **Acción** | Mantener |

---

### `trace_realism_audit.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | LEGACY · auditoría estática |
| **Fecha** | 2026-05-19 |
| **Contenido** | Realismo trazas v1+v2 sin simular |
| **Paper** | Background / limitaciones (opcional) |
| **Reorganización** | → `_archive/reports/` |
| **Acción** | Archivar; extraer párrafo síntesis si hace falta |

---

### `traffic_profile_kpi_analysis.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO · **CANÓNICO** |
| **Script** | `analyze_traffic_profile_kpis.py` |
| **Contenido** | Stats por TP, rankings, validación vs TP01, perfiles stress |
| **CSV** | `traffic_profile_kpi_summary.csv`, `traffic_profile_stats.csv` |
| **Reorganización** | → `traffic_profiles/` o `canonical/` |
| **Acción** | Regenerar tras re-sims |

---

### `useful_simulation_time_report.md`

| Campo | Valor |
|-------|--------|
| **Tipo** | GENERADO |
| **Script** | `compute_useful_simulation_time.py` |
| **Contenido** | Metodología tiempo útil vs endTime; contactos |
| **CSV** | `useful_simulation_time_metrics.csv` |
| **Paper** | Methods / Supplementary |
| **Reorganización** | → `spatial/` (junto ocupación) |
| **Acción** | Mantener |

---

### `wiki_new_index.md` / `wiki_old_audit.md` / `wiki_paper_rebuild_report.md` / `wiki_rebuild_summary.md`

| Fichero | Rol |
|---------|-----|
| `wiki_paper_rebuild_report.md` | Informe completo rebuild round2 + round3 |
| `wiki_rebuild_summary.md` | Resumen ejecutivo wiki |
| `wiki_new_index.md` | Índice propuesto páginas |
| `wiki_old_audit.md` | Auditoría wiki pre-rebuild |

**Reorganización:** → `wiki_meta/`  
**Acción:** Mantener; no mezclar con informes paper en misma carpeta que `RESULTADOS_ACTUALES.md`

---

## Matriz script → informe

| Script | Informes que escribe |
|--------|----------------------|
| `run_analysis.py` | `RESULTADOS_ACTUALES.md`, `features_report.*`, `correlation_*.txt`, `ablation_report.txt`, `clustering_report.txt`, `multiple_comparisons_report.txt`, `outputs_correlation_report.txt`, `scenarios_to_diversify*.txt`, `feature_feature_correlation_report.txt`, `indirect_features_report.*` |
| `audit_settings.py` | `settings_audit.md` |
| `diagnose_scenarios.py` | `scenario_diagnosis.md` |
| `validate_traffic_profiles.py` | `tp_validation_report.md` |
| `validate_corpus_v2_benchmark.py` | `corpus_v2_benchmark_validation.md` |
| `analyze_traffic_profile_kpis.py` | `traffic_profile_kpi_analysis.md` |
| `build_message_analysis_window_policy.py` | `message_analysis_window_policy.md` |
| `analyze_message_creation_times.py` | `message_creation_time_audit.md` |
| `build_protocol_benchmark_kpi_policy.py` | `protocol_benchmark_kpi_policy.md` |
| `analyze_spatial_vs_performance.py` | `spatial_vs_performance_analysis.md` (+ puntero en `spatial_occupancy_analysis_summary.md`) |
| `analyze_spatial_occupancy.py` | (antes `spatial_occupancy_analysis_summary.md`) |
| `compute_useful_simulation_time.py` | `useful_simulation_time_report.md` |
| `build_corpus_v2_revision_plan.py` | `corpus_v2_revision_plan.md` |
| `apply_corpus_v2_revision.py` | `corpus_v2_revision_changelog.md` |
| `build_wiki_research_reports.py` | `wiki_*.md`, `current_results_review.md`, `evaluation_metrics_review.md`, `paper_phase1_action_plan.md`, `simulation_time_policy.md` |
| `build_paper_figures_tables_index.py` | `paper_figures_tables_readiness.md`, `dashboard_readiness_report.md` |
| `build_paper_freeze_checklist.py` | `paper_freeze_checklist.md` |
| `build_inventory_update_report.py` | `inventory_update_report.md` |
| (manual) | `project_reorganization_report.md`, `spatial_occupancy_report.md`, `trace_realism_audit.md`, `check_tp12_d2.md`, `resumen_tp_*.md` |

---

## Duplicados y conflictos a resolver en la reorganización

| Tema | Informes en conflicto | Resolución recomendada |
|------|------------------------|-------------------------|
| Diversidad numérica | `RESULTADOS_ACTUALES.md` vs extracts en wiki | Solo editar `RESULTADOS_ACTUALES.md` |
| Ventana mensajes | `message_analysis_window_policy.md` vs wiki 11 (ya alineada) | Policy MD canónico |
| Métricas routing | `evaluation_metrics_review.md` vs `protocol_benchmark_kpi_policy.md` | Fusionar en protocol policy a medio plazo |
| Resultados output | `current_results_review.md` vs `corpus_v2_benchmark_validation.md` | Benchmark validation como canónico |
| Espacial resumen | `spatial_occupancy_analysis_summary.md` vs `spatial_vs_performance_analysis.md` | Solo el segundo |
| Features | `features_report.txt` vs `.md` | `.md` canónico |
| TP agregados | `resumen_tp_excluyendo_no_contacto.md` vs `traffic_profile_kpi_analysis.md` | Archivar resumen |

---

## Enlaces externos que apuntan a `reports/`

Actualizar tras mover subcarpetas:

- [`scenarios/README.md`](../../README.md) — freeze checklist, protocol policy
- [`scenarios/INVENTARIO.md`](../../INVENTARIO.md) — listado parcial
- [`scenarios/analysis/README.md`](../README.md)
- [`scenarios/analysis/SCRIPTS_INDEX.md`](../SCRIPTS_INDEX.md)
- [`.wiki-clone/`](../.wiki-clone/) — muchos enlaces `../analysis/reports/...`
- [`dashboard/data_loaders.py`](../dashboard/data_loaders.py) — `list_markdown_reports()`

**Estrategia:** dejar en raíz `reports/` solo `RESULTADOS_ACTUALES.md`, `paper_freeze_checklist.md` y `README.md`; el resto en subcarpetas con rutas actualizadas en scripts (siguiente PR).

---

## Regeneración rápida

```bash
cd scenarios/analysis

# Pipeline núcleo + RESULTADOS
python run_analysis.py --corpus corpus_v2 --phase all

# Validación y KPIs
python audit_settings.py --corpus corpus_v2
python diagnose_scenarios.py
python validate_traffic_profiles.py --corpus corpus_v2
python validate_corpus_v2_benchmark.py
python analyze_traffic_profile_kpis.py

# Políticas
python build_message_analysis_window_policy.py
python build_protocol_benchmark_kpi_policy.py
python analyze_spatial_vs_performance.py

# Gate paper
python build_paper_figures_tables_index.py
python build_paper_freeze_checklist.py
python build_inventory_update_report.py
```

---

## Próximo paso sugerido

1. Crear subcarpetas vacías según esquema arriba.  
2. `mv` ficheros por categoría (registrar en `project_reorganization_report.md` §9).  
3. Añadir [`reports/README.md`](README.md) con tabla 1 línea por fichero + enlace a esta ficha.  
4. Actualizar `list_markdown_reports()` y wiki si se cambian rutas.

*Este inventario es FUENTE para la reorganización; regenerar manualmente o extender `build_inventory_update_report.py` si se desea automatizar el listado.*
