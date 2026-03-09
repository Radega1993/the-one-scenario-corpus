#!/usr/bin/env python3
"""
Dashboard interactivo del análisis de escenarios (The ONE).
Muestra resultados por fase, por escenario y comparación entre escenarios.
Filtros, tooltips en columnas y menos ruido en terminal (API actualizada).

Ejecutar desde la raíz del repo o desde scenarios/analysis:
  streamlit run scenarios/analysis/dashboard.py
  cd scenarios/analysis && streamlit run dashboard.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
FIGURES_DIR = BASE / "figures"
REPORTS_DIR = BASE / "reports"

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
    "transmitRange": "Rango de transmisión (m)",
    "contact_rate_proxy": "Proxy tasa de contacto (relativo)",
    "event_interval_mean": "Intervalo medio entre mensajes (s)",
    "event_size_mean": "Tamaño medio de mensaje (bytes)",
    "msgTtl": "TTL de mensajes (min)",
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
        "figures": (FIGURES_DIR / "heatmap_pearson.png").exists(),
        "output_metrics": (DATA_DIR / "output_metrics.csv").exists(),
        "outputs": (DATA_DIR / "correlation_pearson_outputs.csv").exists(),
    }


def _dataframe_config(df: pd.DataFrame, help_map: dict | None = None, numeric_cols: set | None = None) -> dict:
    """Construye column_config con tooltips (help) para st.dataframe."""
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
    """Filtra filas donde la primera columna (escenario) contiene filter_text (case-insensitive)."""
    if not filter_text or df is None or df.empty:
        return df
    col0 = df.columns[0]
    mask = df[col0].astype(str).str.lower().str.contains(filter_text.lower(), na=False)
    return df.loc[mask]


def view_resumen():
    st.header("Resumen del análisis")
    status = phase_status()
    cols = st.columns(3)
    for i, (phase, ok) in enumerate(status.items()):
        cols[i % 3].metric(phase.replace("_", " ").title(), "✓" if ok else "—")
    st.caption("✓ = datos disponibles para esta fase.")

    st.subheader("Informes de texto")
    for name, path in [
        ("Correlación (parámetros)", REPORTS_DIR / "correlation_report.txt"),
        ("Comparaciones múltiples", REPORTS_DIR / "multiple_comparisons_report.txt"),
        ("Outputs (métricas de simulación)", REPORTS_DIR / "outputs_correlation_report.txt"),
    ]:
        if path.exists():
            with st.expander(name):
                st.text(path.read_text(encoding="utf-8", errors="replace"))
        else:
            st.caption(f"{name}: no generado aún.")

    st.subheader("Figuras")
    if FIGURES_DIR.exists():
        for fname in sorted(FIGURES_DIR.glob("*.png")):
            st.image(str(fname), caption=fname.name, width="stretch")


def view_por_fase():
    st.header("Resultados por fase")
    phase = st.selectbox(
        "Fase",
        ["features", "normalize", "correlation", "figures", "output_metrics", "outputs"],
        format_func=lambda x: x.replace("_", " ").title(),
    )
    filter_scenario = st.text_input("🔍 Filtrar por nombre de escenario", key="filter_phase", placeholder="Ej: U1_, D2_, Campus")
    if phase == "features":
        df = load_csv_safe(DATA_DIR / "features.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(
                df,
                width="stretch",
                height=400,
                column_config=_dataframe_config(df, FEATURE_HELP),
            )
            st.caption(f"Escenarios: {len(df)}, features: {len(df.columns) - 1}")
        else:
            st.info("Ejecuta `run_analysis.py --phase features` para generar features.csv.")
    elif phase == "normalize":
        df = load_csv_safe(DATA_DIR / "features_normalized.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(
                df,
                width="stretch",
                height=400,
                column_config=_dataframe_config(df, FEATURE_HELP),
            )
            st.caption(f"Vectores Z (z-score por feature). Filas: {len(df)}.")
        else:
            st.info("Ejecuta `run_analysis.py --phase normalize`.")
    elif phase == "correlation":
        df = load_csv_safe(DATA_DIR / "correlation_pearson.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(df, width="stretch", height=400)
            if (REPORTS_DIR / "correlation_report.txt").exists():
                st.text(REPORTS_DIR.joinpath("correlation_report.txt").read_text(encoding="utf-8", errors="replace"))
            fig = FIGURES_DIR / "heatmap_pearson.png"
            if fig.exists():
                st.image(str(fig), width="stretch")
        else:
            st.info("Ejecuta `run_analysis.py --phase correlation`.")
    elif phase == "figures":
        if FIGURES_DIR.exists():
            for png in sorted(FIGURES_DIR.glob("*.png")):
                st.image(str(png), caption=png.name, width="stretch")
        else:
            st.info("Ejecuta `run_analysis.py --phase figures`.")
    elif phase == "output_metrics":
        df = load_csv_safe(DATA_DIR / "output_metrics.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(
                df,
                width="stretch",
                height=400,
                column_config=_dataframe_config(df, OUTPUT_HELP, {"delivery_ratio", "latency_mean", "overhead_ratio", "drop_ratio"}),
            )
            st.caption("Métricas de salida por escenario (MessageStatsReport).")
        else:
            st.info("Ejecuta `run_analysis.py --phase output_metrics` o rellena data/output_metrics.csv.")
    elif phase == "outputs":
        df = load_csv_safe(DATA_DIR / "correlation_pearson_outputs.csv")
        if df is not None:
            df = _filter_df_by_scenario(df, filter_scenario)
            st.dataframe(df, width="stretch", height=400)
            if (REPORTS_DIR / "outputs_correlation_report.txt").exists():
                st.text(REPORTS_DIR.joinpath("outputs_correlation_report.txt").read_text(encoding="utf-8", errors="replace"))
            fig = FIGURES_DIR / "heatmap_pearson_outputs.png"
            if fig.exists():
                st.image(str(fig), width="stretch")
        else:
            st.info("Ejecuta `run_analysis.py --phase outputs` (requiere output_metrics.csv).")


def view_por_escenario():
    st.header("Detalle por escenario")
    features = load_csv_safe(DATA_DIR / "features.csv")
    outputs = load_csv_safe(DATA_DIR / "output_metrics.csv")
    pearson = load_csv_safe(DATA_DIR / "correlation_pearson.csv")
    if features is None and outputs is None:
        st.warning("No hay datos. Ejecuta al menos `--phase features` o `--phase output_metrics`.")
        return
    scenarios_feat = list(features.iloc[:, 0].astype(str)) if features is not None else []
    scenarios_out = list(outputs.iloc[:, 0].astype(str)) if outputs is not None else []
    all_scenarios = sorted(set(scenarios_feat) | set(scenarios_out))
    filter_text = st.text_input("🔍 Filtrar lista de escenarios", key="filter_escenario", placeholder="Ej: U1, Campus, D2")
    if filter_text:
        all_scenarios = [s for s in all_scenarios if filter_text.lower() in s.lower()]
    if not all_scenarios:
        st.warning("Ningún escenario coincide con el filtro.")
        return
    scenario = st.selectbox("Escenario", all_scenarios)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Features (parámetros)")
        if features is not None and scenario in features.iloc[:, 0].astype(str).values:
            row = features[features.iloc[:, 0].astype(str) == scenario].iloc[0]
            st.json(row.to_dict())
        else:
            st.caption("Sin datos de features para este escenario.")
    with c2:
        st.subheader("Métricas de salida")
        if outputs is not None and scenario in outputs.iloc[:, 0].astype(str).values:
            row = outputs[outputs.iloc[:, 0].astype(str) == scenario].iloc[0]
            st.json(row.to_dict())
        else:
            st.caption("Sin datos de outputs para este escenario.")
    if pearson is not None and scenario in pearson.columns:
        st.subheader("Correlación con otros escenarios (Pearson)")
        idx = list(pearson.columns).index(scenario)
        row_vals = pearson.iloc[idx].drop(scenario, errors="ignore")
        # Asegurar numérico para ordenar (evita error con columnas leídas como string)
        corr_series = pd.to_numeric(row_vals, errors="coerce").sort_values(ascending=False)
        st.dataframe(
            corr_series.to_frame("r"),
            width="stretch",
            height=300,
            column_config={"r": st.column_config.NumberColumn("r", help="Correlación de Pearson", format="%.4f")},
        )


def view_comparar():
    st.header("Comparar escenarios")
    features = load_csv_safe(DATA_DIR / "features.csv")
    outputs = load_csv_safe(DATA_DIR / "output_metrics.csv")
    pearson = load_csv_safe(DATA_DIR / "correlation_pearson.csv")
    if features is None and outputs is None:
        st.warning("No hay datos para comparar.")
        return
    scenarios_feat = list(features.iloc[:, 0].astype(str)) if features is not None else []
    scenarios_out = list(outputs.iloc[:, 0].astype(str)) if outputs is not None else []
    all_scenarios = sorted(set(scenarios_feat) | set(scenarios_out))
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
        st.dataframe(
            feat_sub.T,
            width="stretch",
            column_config=_dataframe_config(feat_sub.T, FEATURE_HELP),
        )
    if outputs is not None:
        st.subheader("Métricas de salida")
        out_sub = outputs[outputs.iloc[:, 0].astype(str).isin(selected)].set_index(outputs.columns[0])
        st.dataframe(
            out_sub.T,
            width="stretch",
            column_config=_dataframe_config(out_sub.T, OUTPUT_HELP, {"delivery_ratio", "latency_mean", "overhead_ratio", "drop_ratio"}),
        )
    if pearson is not None and len(selected) >= 2:
        st.subheader("Correlación Pearson entre seleccionados")
        sub = pearson.set_index(pearson.columns[0]).reindex(columns=selected, index=selected)
        # Asegurar numérico
        sub = sub.apply(pd.to_numeric, errors="coerce")
        st.dataframe(sub, width="stretch")
        r_vals = []
        for i, a in enumerate(selected):
            for b in selected[i + 1 :]:
                try:
                    r = sub.loc[a, b]
                    r_vals.append(f"{a} ↔ {b}: r = {r:.4f}" if pd.notna(r) else f"{a} ↔ {b}: —")
                except Exception:
                    pass
        if r_vals:
            for line in r_vals:
                st.code(line)


def main():
    st.set_page_config(page_title="Análisis de escenarios — The ONE", layout="wide")
    st.title("Análisis de escenarios (corpus)")
    st.caption("Resultados del pipeline run_analysis.py: features, correlación, outputs. Usa los filtros y pasa el ratón sobre las columnas para ver descripciones.")

    vista = st.sidebar.radio(
        "Vista",
        ["Resumen", "Por fase", "Por escenario", "Comparar escenarios"],
        label_visibility="collapsed",
    )
    if vista == "Resumen":
        view_resumen()
    elif vista == "Por fase":
        view_por_fase()
    elif vista == "Por escenario":
        view_por_escenario()
    else:
        view_comparar()


if __name__ == "__main__":
    main()
