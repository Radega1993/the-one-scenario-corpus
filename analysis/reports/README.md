# Informes de análisis (`analysis/reports/`)

Repositorio temático de informes Markdown y texto del benchmark combinado del paper (**540 simulaciones**: 540 `corpus_v1` + 30 ``). La reorganización de 2026-05-24 agrupa artefactos por función sin borrar ningún fichero.

## 1. Overview

| Elemento | Ubicación |
|----------|-----------|
| **Referencia numérica principal** | [RESULTADOS_ACTUALES.md](RESULTADOS_ACTUALES.md) (raíz) |
| **Gate freeze paper** | [paper_freeze_checklist.md](paper_freeze_checklist.md) (raíz) |
| Informes canónicos metodológicos | [`canonical/`](canonical/) |
| Salidas pipeline `run_analysis.py` | [`pipeline/`](pipeline/) |
| Auditorías y validación | [`validation/`](validation/) |
| Políticas metodológicas | [`policies/`](policies/) |
| Readiness figuras/dashboard | [`paper_gate/`](paper_gate/) |
| Espacial y tiempo útil | [`spatial/`](spatial/) |
| Meta wiki / proyecto | [`wiki_meta/`](wiki_meta/), [`project/`](project/) |
| Notas legacy locales | [`_archive_local/`](_archive_local/) |

**Advertencia:** no edites cifras en estos informes a mano. `RESULTADOS_ACTUALES.md` concentra las métricas congeladas de diversidad; los scripts regeneran el resto desde `analysis/data/`.

Inventario detallado por fichero: [project/REPORTS_INVENTORY.md](project/REPORTS_INVENTORY.md).  
Manifiesto de movimientos: [../data/reports_reorganization_manifest.csv](../data/reports_reorganization_manifest.csv).

## 2. Canonical reports for the paper

| Informe | Descripción |
|---------|-------------|
| [canonical/traffic_profile_kpi_analysis.md](canonical/traffic_profile_kpi_analysis.md) | KPIs por TP01–TP12 |
| [canonical/protocol_benchmark_kpi_policy.md](canonical/protocol_benchmark_kpi_policy.md) | Métricas para comparar protocolos |
| [canonical/message_analysis_window_policy.md](canonical/message_analysis_window_policy.md) | Ventana de análisis de mensajes |
| [canonical/spatial_vs_performance_analysis.md](canonical/spatial_vs_performance_analysis.md) | Ocupación espacial vs rendimiento |
| [canonical/corpus_benchmark_validation.md](canonical/corpus_benchmark_validation.md) | Validación benchmark combinado (540) |

## 3. Pipeline reports

Generados por `run_analysis.py` (fases features, correlation, ablation, …):

- [pipeline/features_report.md](pipeline/features_report.md), [pipeline/features_report.txt](pipeline/features_report.txt)
- [pipeline/correlation_report.txt](pipeline/correlation_report.txt), [pipeline/correlation_core23_report.txt](pipeline/correlation_core23_report.txt)
- [pipeline/ablation_report.txt](pipeline/ablation_report.txt)
- [pipeline/feature_feature_correlation_report.txt](pipeline/feature_feature_correlation_report.txt)
- [pipeline/multiple_comparisons_report.txt](pipeline/multiple_comparisons_report.txt)
- [pipeline/outputs_correlation_report.txt](pipeline/outputs_correlation_report.txt)
- [pipeline/scenarios_to_diversify.txt](pipeline/scenarios_to_diversify.txt), [pipeline/scenarios_to_diversify_core23.txt](pipeline/scenarios_to_diversify_core23.txt)
- [pipeline/clustering_report.txt](pipeline/clustering_report.txt)
- [pipeline/indirect_features_report.md](pipeline/indirect_features_report.md)

## 4. Validation reports

| Informe | Script |
|---------|--------|
| [validation/settings_audit.md](validation/settings_audit.md) | `audit_settings.py` |
| [validation/scenario_diagnosis.md](validation/scenario_diagnosis.md) | `diagnose_scenarios.py` |
| [validation/tp_validation_report.md](validation/tp_validation_report.md) | `validate_traffic_profiles.py` |
| [validation/message_creation_time_audit.md](validation/message_creation_time_audit.md) | `analyze_message_creation_times.py` |
| [validation/evaluation_metrics_review.md](validation/evaluation_metrics_review.md) | `build_wiki_research_reports.py` |
| [validation/current_results_review.md](validation/current_results_review.md) | `build_wiki_research_reports.py` |

## 5. Methodological policies

| Informe | Tema |
|---------|------|
| [policies/simulation_time_policy.md](policies/simulation_time_policy.md) | Duración de simulación y warmup |

(Ventana de mensajes y KPIs de protocolo están en `canonical/`.)

## 6. Spatial analysis

| Informe | Notas |
|---------|-------|
| [spatial/spatial_occupancy_report.md](spatial/spatial_occupancy_report.md) | Metodología ocupación |
| [spatial/useful_simulation_time_report.md](spatial/useful_simulation_time_report.md) | Tiempo útil de simulación |
| [spatial/spatial_occupancy_analysis_summary.md](spatial/spatial_occupancy_analysis_summary.md) | Puntero → análisis canónico |

## 7. Traffic profile analysis

La validación de overlays TP está en [validation/tp_validation_report.md](validation/tp_validation_report.md).  
El análisis KPI canónico por perfil está en [canonical/traffic_profile_kpi_analysis.md](canonical/traffic_profile_kpi_analysis.md).  
La carpeta [`traffic_profiles/`](traffic_profiles/) se reserva para extensiones futuras (vacía tras reorg).

## 8. Wiki and documentation metadata

| Informe | Uso |
|---------|-----|
| [wiki_meta/wiki_paper_rebuild_report.md](wiki_meta/wiki_paper_rebuild_report.md) | Log rebuild wiki |
| [wiki_meta/wiki_rebuild_summary.md](wiki_meta/wiki_rebuild_summary.md) | Resumen |
| [wiki_meta/wiki_new_index.md](wiki_meta/wiki_new_index.md) | Índice propuesto |
| [wiki_meta/wiki_old_audit.md](wiki_meta/wiki_old_audit.md) | Auditoría wiki antigua |

Wiki activa: [`scenarios/.wiki-clone/`](../../.wiki-clone/).

## 9. Archived local notes

Superseded o notas puntuales (2026-04); conservados sin borrar:

- [_archive_local/trace_realism_audit.md](_archive_local/trace_realism_audit.md)
- [_archive_local/check_tp12_d2.md](_archive_local/check_tp12_d2.md)
- [_archive_local/resumen_tp_excluyendo_no_contacto.md](_archive_local/resumen_tp_excluyendo_no_contacto.md)

## 10. Regeneration commands

Desde `scenarios/analysis/` (corpus activo: `corpus_v1`):

```bash
# Pipeline diversidad + RESULTADOS_ACTUALES
python run_analysis.py --corpus corpus_v1 --phase correlation
python run_analysis.py --corpus corpus_v1 --phase ablation

# Validación y canónicos
python scripts/validation/validate_corpus_benchmark.py
python analyze_traffic_profile_kpis.py
python build_protocol_benchmark_kpi_policy.py
python build_message_analysis_window_policy.py
python analyze_spatial_vs_performance.py

# Gate paper
python build_paper_figures_tables_index.py
python build_paper_freeze_checklist.py
```

Índice completo de scripts: [../SCRIPTS_INDEX.md](../SCRIPTS_INDEX.md).

## 11. Maintenance policy

- **No borrar** informes; archivar en `_archive_local/` si quedan obsoletos.
- **No editar** resultados numéricos a mano en informes generados.
- Tras mover o renombrar, actualizar `lib/report_paths.py` y enlaces en wiki/README.
- Nuevos informes canónicos → `canonical/`; salidas `run_analysis` → `pipeline/`.
- Backup antes de reorg masiva: `analysis/reports_backup_YYYYMMDD_HHMMSS.tar.gz`.