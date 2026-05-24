# Menú interactivo de análisis (`analysis_menu.py`)

Guía rápida en español. Lanza scripts con `subprocess` desde la raíz del repositorio ONE.

```bash
python3 scenarios/analysis/analysis_menu.py
```

**Corpus activo:** `corpus_v2` (720 escenarios, congelado). No se regenera desde el menú.

---

## Menú principal

| # | Acción | Script / destino |
|---|--------|------------------|
| 1 | Simular corpus completo (batch) | `run_all_scenarios.py` |
| 2 | Simular selección (familia, TP, lista, GUI) | `run_all_scenarios.py` |
| 3 | Pipeline por fases | `run_analysis.py` |
| 4 | **Paper y validación** (submenú 4a–4n) | Ver tabla siguiente |
| 5 | Tiempo útil de simulación | `scripts/validation/compute_useful_simulation_time.py` |
| 6 | Tiempos de creación de mensajes | `scripts/validation/analyze_message_creation_times.py` |
| 7 | Ocupación espacial / heatmaps | `scripts/validation/analyze_spatial_occupancy.py` |
| 8 | Dashboard Streamlit | `dashboard.py` |
| 9 | Figuras agregadas / paper | `run_figures_aggregated.py` + opcional `figures_paper` |
| 0 | Salir | — |

Presets de reportes en simulación (opciones 1–2): overlays en `overlays/routing_contact_reports_overrides.txt` y `overlays/spatial_occupancy_reports_overrides.txt`.

---

## Submenú 4 — Paper y validación

| Sub | Script | Salidas principales |
|-----|--------|---------------------|
| 4a | `scripts/validation/validate_traffic_profiles.py` | `data/tp_validation_*`, `reports/validation/tp_validation_report.md` |
| 4b | `run_analysis.py --phase output_metrics` | `data/output_metrics.csv` |
| 4c | `scripts/validation/validate_corpus_v2_benchmark.py` | `data/corpus_v2_benchmark_validation.csv` |
| 4d | `scripts/paper/analyze_traffic_profile_kpis.py` | `data/traffic_profile_*`, informe KPI TP |
| 4e | `scripts/paper/build_protocol_benchmark_kpi_policy.py` | política KPI protocolos |
| 4f | `scripts/paper/build_message_analysis_window_policy.py` | ventana análisis mensajes |
| 4g | `scripts/paper/analyze_spatial_vs_performance.py` | espacial vs delivery |
| 4h | `scripts/paper/build_paper_figures_tables_index.py` | índice figuras/tablas paper |
| 4i | `scripts/paper/build_paper_freeze_checklist.py` | gate freeze paper |
| 4j | `scripts/validation/audit_settings.py` | `data/settings_audit.csv` |
| 4k | `scripts/validation/diagnose_scenarios.py` | `data/scenario_diagnosis.csv` |
| 4l | `scripts/wiki/populate_wiki_paper.py` | `scenarios/.wiki-clone/` |
| 4m | `scripts/wiki/build_wiki_research_reports.py` | `reports/wiki_meta/`, validación aux |
| 4n | `scripts/paper/build_inventory_update_report.py` | `reports/project/inventory_update_report.md` |

Cada opción muestra 2–3 líneas de propósito antes de ejecutar.

---

## Archivos de apoyo

| Ruta | Uso |
|------|-----|
| `overlays/*.txt` | `--extra-settings` en simulaciones |
| `examples/selection_example.txt` | Ejemplo `--select-file` |
| `lib/traffic_profile_generator.py` | Definiciones canónicas TP01–TP12 |

Índice completo de scripts: [SCRIPTS_INDEX.md](SCRIPTS_INDEX.md).
