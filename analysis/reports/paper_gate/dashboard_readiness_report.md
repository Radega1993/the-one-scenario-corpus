# Dashboard readiness report (corpus_v1)

Generated: automated from `build_paper_figures_tables_index.py` / dashboard loaders.

## Executive summary

- **Corpus:** corpus_v1 — **720** simulations in master table.
- **Launch:** `streamlit run scenarios/analysis/dashboard.py`
- **Reference:** [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)

## Pages and data sources

| Page | Primary data | Paper utility |
|------|--------------|---------------|
| Resumen corpus | manifest, pipeline_status | Corpus design, data availability |
| Explorador | master table (all joins) | Scenario tables, export CSV |
| KPIs benchmark | traffic_profile_kpi_summary, output_metrics | TP comparison, paper KPIs |
| Perfiles TP | tp_validation_*, message_creation_time_summary | TP validation |
| Ventana mensajes | message_analysis_window_policy | Message window methodology |
| Tiempo útil | useful_simulation_time_metrics | Simulation time vs mobility |
| Espacial | spatial_occupancy_metrics, heatmaps/ | Spatial coverage, WDM |
| Diagnóstico | scenario_diagnosis, corpus_v1_benchmark_validation | Problem scenarios |
| Protocolos | placeholder | Future routing comparison |
| Detalle escenario | master row, raw reports/ | Deep dive per scenario |
| Figuras / Pipeline / Reportes | figures/, reports/ | Auxiliary exploration |

## Pipeline file status

| Artifact | Available |
|----------|-----------|
| `manifest` | yes |
| `features` | yes |
| `features_core` | yes |
| `output_metrics` | yes |
| `indirects` | yes |
| `diagnosis` | yes |
| `settings_audit` | yes |
| `tp_validation` | yes |
| `msg_creation_time` | yes |
| `spatial_metrics` | yes |
| `correlation` | yes |
| `spatial_heatmaps_dir` | yes |
| `useful_time` | yes |
| `msg_window_policy` | yes |
| `tp_kpi_summary` | yes |
| `bench_validation` | yes |

## Issues found

- **1** scenarios without `output_metrics` (e.g. S1 TP03/TP11 re-simulate).
- **1** scenarios with `error_probable` benchmark validation.
- `protocol_benchmark_kpi_definitions.csv` not present — protocols page uses placeholder.
- Feature matrices (720×720) intentionally excluded from UI.

## Pending improvements

- Multi-protocol simulation and comparison charts.
- Optional PCA on features in-dashboard (load on demand).
- Cache clear button when CSVs regenerated.

## Paper section mapping

| Paper section | Dashboard page |
|---------------|----------------|
| Methods — benchmark design | Resumen corpus |
| Methods — traffic profiles | Perfiles TP, KPIs benchmark |
| Methods — message window | Ventana mensajes |
| Results — diversity | Pipeline clásico / Figuras (external) |
| Results — delivery by TP | KPIs benchmark, Explorador |
| Results — spatial | Espacial |
| Discussion — limitations | Diagnóstico, Protocolos |
