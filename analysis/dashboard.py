#!/usr/bin/env python3
"""
Dashboard interactivo del análisis de escenarios (The ONE).
Incluye:
- data/reports/figures del pipeline de análisis
- figuras comparativas por espacio (17/23/46)
- paquete paper (figuras + tablas)
- reportes crudos de simulación en repo/reports
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
FIGURES_DIR = BASE / "figures"
REPORTS_DIR = BASE / "reports"
ROOT_REPORTS_DIR = BASE.parent.parent / "reports"

# Tooltips para columnas (hover en cabeceras)
FEATURE_HELP = {
    "world_area": "Área del mundo Wx×Wy (m²)",
    "aspect_ratio": "Relación de aspecto min(Wx,Wy)/max(Wx,Wy) ∈ (0,1]",
    "N": "Número total de nodos",
    "density": "Densidad de nodos (proxy nodos/km²)",
    "speed_mean": "Velocidad media de movimiento (m/s)",
    "pause_ratio": "Fracción tiempo en pausa (0–1)",
    "wait_mean": "Tiempo medio de espera entre waypoints (s)",
    "mm_WDM": "WorkingDayMovement (0/1)",
    "mm_RWP": "RandomWaypoint (0/1)",
    "mm_MapRoute": "MapRouteMovement (0/1)",
    "mm_Cluster": "ClusterMovement (0/1)",
    "mm_Bus": "BusMovement (0/1)",
    "mm_ShortestPath": "ShortestPathMapBasedMovement (0/1)",
    "mm_External": "External/ExternalPath movement (0/1)",
    "mm_Linear": "LinearMovement (0/1)",
    "transmitRange": "Rango de transmisión (m)",
    "contact_rate_proxy": "Proxy tasa de contacto (relativo)",
    "event_interval_mean": "Intervalo medio entre mensajes (s)",
    "event_size_mean": "Tamaño medio de mensaje (bytes)",
    "msgTtl": "TTL de mensajes",
    "pattern_uniform": "Tráfico uniforme (0/1)",
    "pattern_burst": "Tráfico en ventanas (0/1)",
    "pattern_hub_target": "Tráfico hacia pocos destinos (0/1)",
    "nrof_event_generators": "Número de generadores de eventos",
    "bufferSize": "Tamaño de buffer (bytes)",
    "transmitSpeed": "Velocidad de transmisión (bytes/s)",
    "Scenario.endTime": "Duración de simulación (s)",
    "nrofHostGroups": "Número de grupos de hosts",
    "has_active_times": "Nodos con intervalos de actividad (0/1)",
    "workDayLength": "Jornada laboral (s) — WDM",
    "timeDiffSTD": "Desviación despertar/horarios (s) — WDM",
    "probGoShoppingAfterWork": "Prob. actividad tras trabajo — WDM",
    "nrOfMeetingSpots": "Número de meeting spots — WDM",
    "nrOfOffices": "Número de oficinas — WDM",
}

OUTPUT_HELP = {
    "scenario": "Nombre del escenario",
    "delivery_ratio": "Probabilidad de entrega (delivered/created)",
    "latency_mean": "Latencia media (s)",
    "overhead_ratio": "Réplicas por entrega (relayed-delivered)/delivered",
    "drop_ratio": "Mensajes descartados / creados",
}


def load_csv_safe(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def phase_status() -> dict[str, bool]:
    """Indica qué fases tienen salida disponible."""
    return {
        "features": (DATA_DIR / "features.csv").exists(),
        "normalize": (DATA_DIR / "features_normalized.csv").exists(),
        "correlation": (DATA_DIR / "correlation_pearson.csv").exists(),
        "feature_correlation": (DATA_DIR / "feature_feature_correlation_core.csv").exists(),
        "ablation": (DATA_DIR / "ablation_metrics.csv").exists(),
        "figures": (FIGURES_DIR / "heatmap_pearson.png").exists(),
        "figures_by_space": (FIGURES_DIR / "by_space").exists(),
        "figures_paper": (FIGURES_DIR / "paper").exists(),
        "tables_paper": (FIGURES_DIR / "paper" / "tables").exists(),
        "indirects": (DATA_DIR / "indirect_features_diego.csv").exists(),
        "output_metrics": (DATA_DIR / "output_metrics.csv").exists(),
        "outputs": (DATA_DIR / "correlation_pearson_outputs.csv").exists(),
    }


def _dataframe_config(df: pd.DataFrame, help_map: dict | None = None, numeric_cols: set | None = None) -> dict:
    if help_map is None:
        help_map = {}
    if numeric_cols is None:
        numeric_cols = set()
    config = {}
    for c in df.columns:
        label = "Escenario" if (c == "" or (isinstance(c, str) and "unnamed" in c.lower())) else c
        h = help_map.get(c, "")
        if df[c].dtype.kind in "fciu" or c in numeric_cols:
            config[c] = st.column_config.NumberColumn(label, help=h if h else None, format="%.4g")
        else:
            config[c] = st.column_config.TextColumn(label, help=h if h else None)
    return config


def _filter_df_by_scenario(df: pd.DataFrame, filter_text: str) -> pd.DataFrame:
    if not filter_text or df is None or df.empty:
        return df
    col0 = df.columns[0]
    mask = df[col0].astype(str).str.lower().str.contains(filter_text.lower(), na=False)
    return df.loc[mask]


def _render_text_or_md(path: Path):
    if not path.exists():
        st.caption(f"No encontrado: {path}")
        return
    txt = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".md":
        st.markdown(txt)
    else:
        st.text(txt)


def _show_pngs(target_dir: Path, recursive: bool = False):
    if not target_dir.exists():
        st.caption(f"No existe: {target_dir}")
        return
    pattern = "**/*.png" if recursive else "*.png"
    files = sorted(target_dir.glob(pattern))
    if not files:
        st.caption("No hay figuras PNG.")
        return
    for f in files:
        rel = f.relative_to(FIGURES_DIR) if FIGURES_DIR in f.parents else f.name
        st.image(str(f), caption=str(rel), width="stretch")


def view_resumen():
    st.header("Resumen del análisis")
    status = phase_status()
    cols = st.columns(4)
    for i, (phase, ok) in enumerate(status.items()):
        cols[i % 4].metric(phase.replace("_", " ").title(), "✓" if ok else "—")
    st.caption("✓ = datos disponibles para esta fase.")

    st.subheader("Informes de análisis")
    report_list = [
        ("Correlación (full)", REPORTS_DIR / "correlation_report.txt"),
        ("Correlación (core23)", REPORTS_DIR / "correlation_core23_report.txt"),
        ("Feature-feature core", REPORTS_DIR / "feature_feature_correlation_report.txt"),
        ("Ablación 17/23/46", REPORTS_DIR / "ablation_report.txt"),
        ("Indirectas Diego", REPORTS_DIR / "indirect_features_report.txt"),
        ("Outputs (simulación)", REPORTS_DIR / "outputs_correlation_report.txt"),
        ("Resultados actuales", REPORTS_DIR / "RESULTADOS_ACTUALES.md"),
    ]
    for name, path in report_list:
        if path.exists():
            with st.expander(name):
                _render_text_or_md(path)

    st.subheader("Reportes crudos (repo/reports)")
    if ROOT_REPORTS_DIR.exists():
        txt_files = sorted(ROOT_REPORTS_DIR.glob("*.txt"))
        one_reports = sorted(ROOT_REPORTS_DIR.glob("*_Report.txt"))
        st.caption(f"Total .txt: {len(txt_files)} | *_Report.txt: {len(one_reports)}")
    else:
        st.caption("No existe repo/reports.")

    st.subheader("Figuras principales")
    _show_pngs(FIGURES_DIR, recursive=False)


def view_por_fase():
    st.header("Resultados por fase")
    phase = st.selectbox(
        "Fase",
        [
            "features",
            "normalize",
            "correlation",
            "feature_correlation",
            "ablation",
            "figures",
            "figures_by_space",
            "figures_paper",
            "tables_paper",
            "indirects",
            "output_metrics",
            "outputs",
        ],
        format_func=lambda x: x.replace("_", " ").title(),
    )
    filter_scenario = st.text_input("🔍 Filtrar por escenario", key="filter_phase", placeholder="Ej: U1_, D2_, Campus")

    if phase == "features":
        df = load_csv_safe(DATA_DIR / "features.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(df, width="stretch", height=420, column_config=_dataframe_config(df, FEATURE_HELP))
            st.caption(f"Escenarios: {len(df)}, features: {len(df.columns) - 1}")
        else:
            st.info("Ejecuta `run_analysis.py --phase features`.")

    elif phase == "normalize":
        df = load_csv_safe(DATA_DIR / "features_normalized.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(df, width="stretch", height=420, column_config=_dataframe_config(df, FEATURE_HELP))
        else:
            st.info("Ejecuta `run_analysis.py --phase normalize`.")

    elif phase == "correlation":
        df = load_csv_safe(DATA_DIR / "correlation_pearson.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(df, width="stretch", height=420)
            _render_text_or_md(REPORTS_DIR / "correlation_report.txt")
            fig = FIGURES_DIR / "heatmap_pearson.png"
            if fig.exists():
                st.image(str(fig), width="stretch")
        else:
            st.info("Ejecuta `run_analysis.py --phase correlation`.")

    elif phase == "feature_correlation":
        df = load_csv_safe(DATA_DIR / "feature_feature_correlation_core.csv")
        if df is not None:
            st.dataframe(df, width="stretch", height=420)
            _render_text_or_md(REPORTS_DIR / "feature_feature_correlation_report.txt")
            fig = FIGURES_DIR / "heatmap_feature_feature_core.png"
            if fig.exists():
                st.image(str(fig), width="stretch")
        else:
            st.info("Ejecuta `run_analysis.py --phase feature_correlation`.")

    elif phase == "ablation":
        df = load_csv_safe(DATA_DIR / "ablation_metrics.csv")
        if df is not None:
            st.dataframe(df, width="stretch", height=260)
            _render_text_or_md(REPORTS_DIR / "ablation_report.txt")
        else:
            st.info("Ejecuta `run_analysis.py --phase ablation`.")

    elif phase == "figures":
        _show_pngs(FIGURES_DIR, recursive=False)

    elif phase == "figures_by_space":
        by_space = FIGURES_DIR / "by_space"
        if not by_space.exists():
            st.info("Ejecuta `run_analysis.py --phase figures` para generar `figures/by_space`.")
        else:
            metric = st.selectbox("Tipo", ["heatmap_pearson", "histogram_correlations_pearson", "scatter_pca_regression"])
            spaces = ["reduced_17", "core_23", "full_46"]
            cols = st.columns(3)
            for i, sname in enumerate(spaces):
                with cols[i]:
                    st.markdown(f"**{sname}**")
                    f = by_space / f"{metric}_{sname}.png"
                    if f.exists():
                        st.image(str(f), width="stretch")
                    else:
                        st.caption(f"No existe {f.name}")

    elif phase == "figures_paper":
        paper_dir = FIGURES_DIR / "paper"
        if not paper_dir.exists():
            st.info("Ejecuta `run_analysis.py --phase figures_paper`.")
        else:
            _render_text_or_md(paper_dir / "README.md")
            st.subheader("Main")
            _show_pngs(paper_dir / "main", recursive=False)
            st.subheader("Supplementary")
            _show_pngs(paper_dir / "supplementary", recursive=False)

    elif phase == "tables_paper":
        tdir = FIGURES_DIR / "paper" / "tables"
        if not tdir.exists():
            st.info("Ejecuta `run_analysis.py --phase tables_paper`.")
        else:
            readme = tdir / "README.md"
            if readme.exists():
                _render_text_or_md(readme)
            for md in sorted(tdir.glob("*.md")):
                if md.name.lower() == "readme.md":
                    continue
                with st.expander(md.name):
                    _render_text_or_md(md)

    elif phase == "indirects":
        df = load_csv_safe(DATA_DIR / "indirect_features_diego.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(df, width="stretch", height=420)
            _render_text_or_md(REPORTS_DIR / "indirect_features_report.txt")
        else:
            st.info("Ejecuta `run_analysis.py --phase indirects`.")

    elif phase == "output_metrics":
        df = load_csv_safe(DATA_DIR / "output_metrics.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(
                df,
                width="stretch",
                height=420,
                column_config=_dataframe_config(df, OUTPUT_HELP, {"delivery_ratio", "latency_mean", "overhead_ratio", "drop_ratio"}),
            )
        else:
            st.info("Ejecuta `run_analysis.py --phase output_metrics`.")

    elif phase == "outputs":
        df = load_csv_safe(DATA_DIR / "correlation_pearson_outputs.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(df, width="stretch", height=420)
            _render_text_or_md(REPORTS_DIR / "outputs_correlation_report.txt")
            fig = FIGURES_DIR / "heatmap_pearson_outputs.png"
            if fig.exists():
                st.image(str(fig), width="stretch")
        else:
            st.info("Ejecuta `run_analysis.py --phase outputs`.")


def view_por_escenario():
    st.header("Detalle por escenario")
    features = load_csv_safe(DATA_DIR / "features.csv")
    outputs = load_csv_safe(DATA_DIR / "output_metrics.csv")
    pearson = load_csv_safe(DATA_DIR / "correlation_pearson.csv")
    indirects = load_csv_safe(DATA_DIR / "indirect_features_diego.csv")
    if features is None and outputs is None and indirects is None:
        st.warning("No hay datos. Ejecuta fases del pipeline.")
        return
    scenarios_feat = list(features.iloc[:, 0].astype(str)) if features is not None else []
    scenarios_out = list(outputs.iloc[:, 0].astype(str)) if outputs is not None else []
    scenarios_ind = list(indirects.iloc[:, 0].astype(str)) if indirects is not None else []
    all_scenarios = sorted(set(scenarios_feat) | set(scenarios_out) | set(scenarios_ind))

    filter_text = st.text_input("🔍 Filtrar lista de escenarios", key="filter_escenario", placeholder="Ej: U1, Campus, D2")
    if filter_text:
        all_scenarios = [s for s in all_scenarios if filter_text.lower() in s.lower()]
    if not all_scenarios:
        st.warning("Ningún escenario coincide con el filtro.")
        return

    scenario = st.selectbox("Escenario", all_scenarios)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Features")
        if features is not None and scenario in features.iloc[:, 0].astype(str).values:
            row = features[features.iloc[:, 0].astype(str) == scenario].iloc[0]
            st.json(row.to_dict())
    with c2:
        st.subheader("Outputs")
        if outputs is not None and scenario in outputs.iloc[:, 0].astype(str).values:
            row = outputs[outputs.iloc[:, 0].astype(str) == scenario].iloc[0]
            st.json(row.to_dict())
    with c3:
        st.subheader("Indirectas Diego")
        if indirects is not None and scenario in indirects.iloc[:, 0].astype(str).values:
            row = indirects[indirects.iloc[:, 0].astype(str) == scenario].iloc[0]
            st.json(row.to_dict())

    if pearson is not None and scenario in pearson.columns:
        st.subheader("Correlación con otros escenarios (Pearson)")
        idx = list(pearson.columns).index(scenario)
        row_vals = pearson.iloc[idx].drop(scenario, errors="ignore")
        corr_series = pd.to_numeric(row_vals, errors="coerce").sort_values(ascending=False)
        st.dataframe(
            corr_series.to_frame("r"),
            width="stretch",
            height=320,
            column_config={"r": st.column_config.NumberColumn("r", help="Correlación de Pearson", format="%.4f")},
        )


def view_comparar():
    st.header("Comparar escenarios")
    features = load_csv_safe(DATA_DIR / "features.csv")
    outputs = load_csv_safe(DATA_DIR / "output_metrics.csv")
    indirects = load_csv_safe(DATA_DIR / "indirect_features_diego.csv")
    pearson = load_csv_safe(DATA_DIR / "correlation_pearson.csv")
    if features is None and outputs is None and indirects is None:
        st.warning("No hay datos para comparar.")
        return
    scenarios_feat = list(features.iloc[:, 0].astype(str)) if features is not None else []
    scenarios_out = list(outputs.iloc[:, 0].astype(str)) if outputs is not None else []
    scenarios_ind = list(indirects.iloc[:, 0].astype(str)) if indirects is not None else []
    all_scenarios = sorted(set(scenarios_feat) | set(scenarios_out) | set(scenarios_ind))

    filter_text = st.text_input("🔍 Filtrar lista de escenarios", key="filter_compare", placeholder="Ej: U1, Traffic")
    if filter_text:
        all_scenarios = [s for s in all_scenarios if filter_text.lower() in s.lower()]
    selected = st.multiselect("Elegir 2 o más escenarios", all_scenarios, max_selections=8)
    if len(selected) < 2:
        st.info("Selecciona al menos 2 escenarios para comparar.")
        return

    if features is not None:
        st.subheader("Features (parámetros)")
        feat_sub = features[features.iloc[:, 0].astype(str).isin(selected)].set_index(features.columns[0])
        st.dataframe(feat_sub.T, width="stretch", column_config=_dataframe_config(feat_sub.T, FEATURE_HELP))

    if outputs is not None:
        st.subheader("Métricas de salida")
        out_sub = outputs[outputs.iloc[:, 0].astype(str).isin(selected)].set_index(outputs.columns[0])
        st.dataframe(
            out_sub.T,
            width="stretch",
            column_config=_dataframe_config(out_sub.T, OUTPUT_HELP, {"delivery_ratio", "latency_mean", "overhead_ratio", "drop_ratio"}),
        )

    if indirects is not None:
        st.subheader("Indirectas Diego")
        ind_sub = indirects[indirects.iloc[:, 0].astype(str).isin(selected)].set_index(indirects.columns[0])
        # No transponer: al transponer se mezcla texto (availability_note) con
        # columnas numéricas por escenario y Streamlit/Arrow emite warnings.
        st.dataframe(ind_sub, width="stretch")

    if pearson is not None and len(selected) >= 2:
        st.subheader("Correlación Pearson entre seleccionados")
        sub = pearson.set_index(pearson.columns[0]).reindex(columns=selected, index=selected)
        sub = sub.apply(pd.to_numeric, errors="coerce")
        st.dataframe(sub, width="stretch")


def view_reportes_raw():
    st.header("Reportes crudos de simulación (repo/reports)")
    if not ROOT_REPORTS_DIR.exists():
        st.warning(f"No existe: {ROOT_REPORTS_DIR}")
        return

    files = sorted(ROOT_REPORTS_DIR.glob("*.txt"))
    if not files:
        st.info("No hay reportes en repo/reports.")
        return

    parsed: list[tuple[str, str, Path]] = []
    for f in files:
        stem = f.stem
        if "_" not in stem:
            continue
        scenario, report_name = stem.rsplit("_", 1)
        parsed.append((scenario, report_name, f))

    scenarios = sorted({x[0] for x in parsed})
    report_types = sorted({x[1] for x in parsed})
    st.caption(f"Escenarios: {len(scenarios)} | Tipos de reporte: {len(report_types)} | Archivos: {len(files)}")

    col1, col2 = st.columns(2)
    with col1:
        scenario = st.selectbox("Escenario", scenarios)
    with col2:
        rtype = st.selectbox("Tipo de reporte", report_types)

    target = None
    for sc, rt, p in parsed:
        if sc == scenario and rt == rtype:
            target = p
            break

    if target is None:
        st.warning("No se encontró ese reporte para el escenario seleccionado.")
        return

    st.caption(str(target))
    txt = target.read_text(encoding="utf-8", errors="replace")
    lines = txt.splitlines()
    show_all = st.checkbox("Mostrar archivo completo", value=False)
    if show_all:
        st.text(txt)
    else:
        st.text("\n".join(lines[:300]))
        if len(lines) > 300:
            st.caption(f"Mostrando 300/{len(lines)} líneas.")


def main():
    st.set_page_config(page_title="Análisis de escenarios — The ONE", layout="wide")
    st.title("Análisis de escenarios (corpus)")
    st.caption("Pipeline visual: data + reports + figures + paper package + reportes crudos de simulación.")

    vista = st.sidebar.radio(
        "Vista",
        ["Resumen", "Por fase", "Por escenario", "Comparar escenarios", "Reportes crudos"],
        label_visibility="collapsed",
    )
    if vista == "Resumen":
        view_resumen()
    elif vista == "Por fase":
        view_por_fase()
    elif vista == "Por escenario":
        view_por_escenario()
    elif vista == "Reportes crudos":
        view_reportes_raw()
    else:
        view_comparar()


if __name__ == "__main__":
    main()
