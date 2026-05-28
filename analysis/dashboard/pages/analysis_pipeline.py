"""Classic run_analysis pipeline views (features, correlation, compare)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.components import render_markdown_file
from lib.report_paths import ABLATION_REPORT_TXT, CORRELATION_REPORT_TXT

from dashboard.data_loaders import DATA_DIR, FIGURES_DIR, load_csv

FEATURE_HELP = {
    "world_area": "Área del mundo Wx×Wy (m²)",
    "N": "Número total de nodos",
    "density": "Densidad de nodos",
    "speed_mean": "Velocidad media (m/s)",
    "transmitRange": "Rango de transmisión (m)",
    "msgTtl": "TTL de mensajes",
    "Scenario.endTime": "Duración simulación (s)",
}

OUTPUT_HELP = {
    "delivery_ratio": "Probabilidad de entrega",
    "latency_mean": "Latencia media (s)",
    "overhead_ratio": "Réplicas por entrega",
    "drop_ratio": "Mensajes descartados / creados",
}


def _filter_scenario(df: pd.DataFrame, text: str) -> pd.DataFrame:
    if not text or df is None or df.empty:
        return df
    col = "scenario" if "scenario" in df.columns else df.columns[0]
    return df[df[col].astype(str).str.lower().str.contains(text.lower(), na=False)]


def render(filtered: pd.DataFrame, _master: pd.DataFrame) -> None:
    st.header("Pipeline clásico (avanzado)")
    tab_phase, tab_compare = st.tabs(["Por fase", "Comparar escenarios"])

    with tab_phase:
        _view_by_phase()

    with tab_compare:
        _view_compare(filtered)


def _view_by_phase() -> None:
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
            "figures_aggregated",
            "indirects",
            "output_metrics",
            "outputs",
        ],
        format_func=lambda x: x.replace("_", " ").title(),
    )
    filt = st.text_input("Filtrar escenario", key="pipeline_filter")

    if phase == "features":
        df = load_csv("features.csv")
        if df is not None:
            st.dataframe(_filter_scenario(df, filt), use_container_width=True, height=400)
        else:
            st.info("Ejecuta `run_analysis.py --phase features`.")

    elif phase == "normalize":
        df = load_csv("features_normalized.csv")
        if df is not None:
            st.dataframe(_filter_scenario(df, filt), use_container_width=True, height=400)

    elif phase == "correlation":
        df = load_csv("correlation_pearson.csv")
        if df is not None:
            st.dataframe(_filter_scenario(df, filt), use_container_width=True, height=360)
            render_markdown_file(REPORTS_ANALYSIS_DIR / "correlation_report.txt")
            st.info(
                "Heatmap 720×720 omitido por defecto. Ver página **Figuras** o "
                "`figures/README.md`; use `histogram_correlations_pearson.png`."
            )
            hist = FIGURES_DIR / "histogram_correlations_pearson.png"
            if hist.is_file():
                st.image(str(hist), caption=hist.name, use_container_width=True)

    elif phase == "feature_correlation":
        df = load_csv("feature_feature_correlation_core.csv")
        if df is not None:
            st.dataframe(df, use_container_width=True, height=360)
            fig = FIGURES_DIR / "heatmap_feature_feature_core.png"
            if fig.is_file():
                st.image(str(fig), use_container_width=True)

    elif phase == "ablation":
        df = load_csv("ablation_metrics.csv")
        if df is not None:
            st.dataframe(df, use_container_width=True, height=260)
            render_markdown_file(ABLATION_REPORT_TXT)

    elif phase == "figures":
        for f in sorted(FIGURES_DIR.glob("*.png")):
            if f.parent == FIGURES_DIR:
                st.image(str(f), caption=f.name, use_container_width=True)

    elif phase == "figures_by_space":
        by_space = FIGURES_DIR / "by_space"
        if by_space.is_dir():
            metric = st.selectbox(
                "Tipo",
                ["heatmap_pearson", "histogram_correlations_pearson", "scatter_pca_regression"],
            )
            for sname in ["reduced_17", "core_23", "full_46"]:
                f = by_space / f"{metric}_{sname}.png"
                if f.is_file():
                    st.image(str(f), caption=f.name, use_container_width=True)

    elif phase == "figures_paper":
        paper = FIGURES_DIR / "paper"
        if paper.is_dir():
            render_markdown_file(paper / "README.md")
            for sub in ("main", "supplementary"):
                d = paper / sub
                if d.is_dir():
                    st.subheader(sub)
                    for f in sorted(d.glob("*.png")):
                        st.image(str(f), caption=f.name, use_container_width=True)

    elif phase == "figures_aggregated":
        agg = FIGURES_DIR / "aggregated"
        render_markdown_file(FIGURES_DIR / "README.md", max_chars=8000)
        if agg.is_dir():
            for f in sorted(agg.glob("*.png")):
                st.image(str(f), caption=f.name, use_container_width=True)
        else:
            st.info("Ejecuta `python3 run_figures_aggregated.py --corpus corpus_v1`.")

    elif phase == "indirects":
        df = load_csv("indirect_features_diego.csv")
        if df is not None:
            st.dataframe(_filter_scenario(df, filt), use_container_width=True, height=400)

    elif phase == "output_metrics":
        df = load_csv("output_metrics.csv")
        if df is not None:
            st.dataframe(_filter_scenario(df, filt), use_container_width=True, height=400)

    elif phase == "outputs":
        df = load_csv("correlation_pearson_outputs.csv")
        if df is not None:
            st.dataframe(_filter_scenario(df, filt), use_container_width=True, height=360)
            hist = FIGURES_DIR / "histogram_correlations_outputs.png"
            if hist.is_file():
                st.image(str(hist), caption=hist.name, use_container_width=True)
            else:
                st.caption("Ejecuta `--phase outputs` para histograma de correlaciones en salidas.")


def _view_compare(filtered: pd.DataFrame) -> None:
    features = load_csv("features.csv")
    outputs = load_csv("output_metrics.csv")
    indirects = load_csv("indirect_features_diego.csv")
    pearson = load_csv("correlation_pearson.csv")

    pool = filtered["scenario"].astype(str).tolist() if not filtered.empty else []
    if pool:
        all_scenarios = sorted(pool)
    else:
        sets = []
        for df in (features, outputs, indirects):
            if df is not None and not df.empty:
                col = "scenario" if "scenario" in df.columns else df.columns[0]
                sets.extend(df[col].astype(str).tolist())
        all_scenarios = sorted(set(sets))

    selected = st.multiselect("Elegir 2–8 escenarios", all_scenarios, max_selections=8)
    if len(selected) < 2:
        st.info("Selecciona al menos 2 escenarios.")
        return

    def _subset(df: pd.DataFrame | None) -> pd.DataFrame | None:
        if df is None:
            return None
        col = "scenario" if "scenario" in df.columns else df.columns[0]
        return df[df[col].astype(str).isin(selected)]

    if features is not None:
        sub = _subset(features)
        if sub is not None and not sub.empty:
            st.subheader("Features")
            idx_col = "scenario" if "scenario" in sub.columns else sub.columns[0]
            st.dataframe(sub.set_index(idx_col).T, use_container_width=True)

    if outputs is not None:
        sub = _subset(outputs)
        if sub is not None and not sub.empty:
            st.subheader("Métricas de salida")
            idx_col = "scenario" if "scenario" in sub.columns else sub.columns[0]
            st.dataframe(sub.set_index(idx_col).T, use_container_width=True)

    if indirects is not None:
        sub = _subset(indirects)
        if sub is not None and not sub.empty:
            st.subheader("Indirectas Diego")
            st.dataframe(sub, use_container_width=True)

    if pearson is not None and len(selected) >= 2:
        col0 = pearson.columns[0]
        p = pearson.set_index(col0)
        sub = p.reindex(columns=selected, index=selected)
        st.subheader("Correlación Pearson")
        st.dataframe(sub.apply(pd.to_numeric, errors="coerce"), use_container_width=True)
