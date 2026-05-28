# Scripts organization report (2026-05-24)

**Estado:** PASS

Auditoría de reorganización de `scenarios/analysis/` según plan `analysis_scripts_organization`. No se modificaron datos numéricos ni `.settings` del corpus.

---

## Backup previo

| Artefacto | Ruta |
|-----------|------|
| Inventario | `reports/project/scripts_inventory_before_20260524_184900.txt` |
| Tar (scripts raíz + overlays) | `analysis/scripts_backup_20260524_184900.tar.gz` |

---

## Scripts eliminados

| Script | Motivo |
|--------|--------|
| `validate_reports_reorganization.py` | Auditoría one-off; entregable en `reports/project/reports_reorganization_validation.md` |
| `generate_corpus_v1_traffic.py` | Corpus_v2 ya generado (720); lógica TP → `lib/traffic_profile_generator.py` |
| `apply_corpus_v1_revision.py` | Revisión in-place ya aplicada |
| `build_corpus_v1_revision_plan.py` | Plan ejecutado; changelog en `reports/project/corpus_v1_revision_changelog.md` |

---

## Ficheros movidos

| Antes | Después |
|-------|---------|
| `diego17_reports_overrides.txt` | `overlays/diego17_reports_overrides.txt` |
| `spatial_occupancy_reports_overrides.txt` | `overlays/spatial_occupancy_reports_overrides.txt` |
| `created_messages_report_overrides.txt` | `overlays/created_messages_report_overrides.txt` |
| `selection_example.txt` | `examples/selection_example.txt` |
| `validate_traffic_profiles.py` | `scripts/validation/validate_traffic_profiles.py` |
| `validate_corpus_v1_benchmark.py` | `scripts/validation/validate_corpus_v1_benchmark.py` |
| `audit_settings.py` | `scripts/validation/audit_settings.py` |
| `diagnose_scenarios.py` | `scripts/validation/diagnose_scenarios.py` |
| `compute_useful_simulation_time.py` | `scripts/validation/compute_useful_simulation_time.py` |
| `analyze_message_creation_times.py` | `scripts/validation/analyze_message_creation_times.py` |
| `analyze_spatial_occupancy.py` | `scripts/validation/analyze_spatial_occupancy.py` |
| `analyze_traffic_profile_kpis.py` | `scripts/paper/analyze_traffic_profile_kpis.py` |
| `build_protocol_benchmark_kpi_policy.py` | `scripts/paper/build_protocol_benchmark_kpi_policy.py` |
| `build_message_analysis_window_policy.py` | `scripts/paper/build_message_analysis_window_policy.py` |
| `analyze_spatial_vs_performance.py` | `scripts/paper/analyze_spatial_vs_performance.py` |
| `build_paper_figures_tables_index.py` | `scripts/paper/build_paper_figures_tables_index.py` |
| `build_paper_freeze_checklist.py` | `scripts/paper/build_paper_freeze_checklist.py` |
| `build_inventory_update_report.py` | `scripts/paper/build_inventory_update_report.py` |
| `populate_wiki_paper.py` | `scripts/wiki/populate_wiki_paper.py` |
| `build_wiki_research_reports.py` | `scripts/wiki/build_wiki_research_reports.py` |

**Raíz (núcleo):** `run_analysis.py`, `run_all_scenarios.py`, `run_figures_aggregated.py`, `dashboard.py`, `analysis_menu.py`

**Código:** `lib/paths.py` actualizado (`DIEGO17_OVERLAY`, `SPATIAL_OVERLAY`, `SELECTION_EXAMPLE`).

---

## Mapa menú → script

| Menú | Script |
|------|--------|
| 1 | `run_all_scenarios.py` |
| 2 | `run_all_scenarios.py` (selección) |
| 3 | `run_analysis.py` |
| 4a | `scripts/validation/validate_traffic_profiles.py` |
| 4b | `run_analysis.py --phase output_metrics` |
| 4c | `scripts/validation/validate_corpus_v1_benchmark.py` |
| 4d | `scripts/paper/analyze_traffic_profile_kpis.py` |
| 4e | `scripts/paper/build_protocol_benchmark_kpi_policy.py` |
| 4f | `scripts/paper/build_message_analysis_window_policy.py` |
| 4g | `scripts/paper/analyze_spatial_vs_performance.py` |
| 4h | `scripts/paper/build_paper_figures_tables_index.py` |
| 4i | `scripts/paper/build_paper_freeze_checklist.py` |
| 4j | `scripts/validation/audit_settings.py` |
| 4k | `scripts/validation/diagnose_scenarios.py` |
| 4l | `scripts/wiki/populate_wiki_paper.py` |
| 4m | `scripts/wiki/build_wiki_research_reports.py` |
| 4n | `scripts/paper/build_inventory_update_report.py` |
| 5 | `scripts/validation/compute_useful_simulation_time.py` |
| 6 | `scripts/validation/analyze_message_creation_times.py` |
| 7 | `scripts/validation/analyze_spatial_occupancy.py` |
| 8 | `dashboard.py` |
| 9 | `run_figures_aggregated.py` (+ opcional `figures_paper`) |

Documentación menú: [MENU.md](../../MENU.md).

---

## Scripts activos solo CLI (fuera del menú principal)

Ninguno obligatorio: todos los secundarios paper/validación/wiki están en submenú 4 o en opciones 5–7.

---

## Validación

- `python3 -m py_compile` en `analysis_menu.py`, `lib/traffic_profile_generator.py`, y todos los `.py` bajo `scripts/` → OK
- `lib/paths.py`: overlays resuelven a ficheros existentes
- Referencias planas a scripts eliminados actualizadas en SCRIPTS_INDEX, README, MENU, INVENTARIO, corpus_v1/README

**Pendiente menor (no bloqueante):** algunos informes históricos en `reports/project/` aún citan rutas antiguas; wiki `populate_wiki_paper.py` puede mencionar el generador histórico en plantillas.
