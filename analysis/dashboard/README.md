# Dashboard corpus_v2 (Streamlit)

Exploración interactiva del benchmark **720 simulaciones** (60 bases × 12 Traffic Profiles).

## Arranque

```bash
# desde la raíz del repo (venv con streamlit, pandas, altair)
streamlit run scenarios/analysis/dashboard.py
```

## Páginas (orden paper-first)

| Página | Datos principales |
|--------|-------------------|
| Resumen corpus | manifest, `pipeline_status`, informes MD |
| Explorador | tabla maestra filtrable + CSV export |
| KPIs benchmark | `traffic_profile_kpi_summary.csv` |
| Perfiles TP | `tp_validation_*` |
| Ventana mensajes | `message_analysis_window_policy.csv` |
| Tiempo útil | `useful_simulation_time_metrics.csv` |
| Espacial | `spatial_occupancy_metrics.csv`, heatmaps |
| Diagnóstico | `scenario_diagnosis.csv`, `corpus_v2_benchmark_validation.csv` |
| Protocolos | placeholder multi-protocolo |
| Detalle escenario | fila master + reportes ONE |
| Figuras / Pipeline / Reportes | auxiliares |

## Filtros globales (sidebar)

- Familia, escenario base, TP, mapa, búsqueda texto
- Rangos: `delivery_ratio`, `drop_ratio`, `final_coverage_pct`
- Validación: `bench_validation_status`, `policy_status` (ventana mensajes)

## CSVs unidos en `data_loaders.build_master_table()`

Obligatorio: `scenarios/corpus_v2/manifest.csv`

Opcionales en `scenarios/analysis/data/`: `output_metrics.csv`, `scenario_diagnosis.csv`, `settings_audit.csv`, `spatial_occupancy_metrics.csv`, `message_creation_time_summary.csv`, `tp_validation_settings.csv`, `useful_simulation_time_metrics.csv`, `message_analysis_window_policy.csv`, `corpus_v2_benchmark_validation.csv`, `traffic_profile_kpi_summary.csv` (join por TP), `indirect_features_diego.csv`.

`features.csv` / `features_core.csv` se cargan bajo demanda (`load_features_table`), no en la tabla maestra.

## Informe de readiness

`scenarios/analysis/reports/paper_gate/dashboard_readiness_report.md` — regenerado al ejecutar `build_paper_figures_tables_index.py` o:

```bash
python -c "from dashboard.data_loaders import write_dashboard_readiness_report; write_dashboard_readiness_report()"
```

(desde `scenarios/analysis/` con streamlit instalado).
