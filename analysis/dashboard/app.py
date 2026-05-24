"""Streamlit app entry: navigation + global filters."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure scenarios/analysis is on path when run as streamlit script
_ANALYSIS = Path(__file__).resolve().parent.parent
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

import streamlit as st

from dashboard.data_loaders import build_master_table, render_sidebar_filters
from dashboard.pages import (
    analysis_pipeline,
    benchmark_kpis,
    corpus_audit,
    figures_guide,
    home,
    message_window,
    protocols,
    raw_reports,
    scenario_detail,
    scenario_explorer,
    spatial,
    traffic_profiles,
    useful_time,
)

PAGES = {
    "Resumen corpus": home,
    "Explorador": scenario_explorer,
    "KPIs benchmark": benchmark_kpis,
    "Perfiles TP": traffic_profiles,
    "Ventana mensajes": message_window,
    "Tiempo útil": useful_time,
    "Espacial": spatial,
    "Diagnóstico": corpus_audit,
    "Protocolos": protocols,
    "Detalle escenario": scenario_detail,
    "Figuras": figures_guide,
    "Pipeline clásico": analysis_pipeline,
    "Reportes crudos": raw_reports,
}


def main() -> None:
    st.set_page_config(
        page_title="Análisis corpus_v2 — The ONE",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    master = build_master_table()
    if master.empty:
        st.error(
            "No se encontró `scenarios/corpus_v2/manifest.csv`. "
            "Genera el corpus o revisa la ruta."
        )
        st.stop()

    filtered = render_sidebar_filters(master)

    st.title("Benchmark corpus_v2")
    st.caption("720 escenarios · 12 perfiles TP · datos en `scenarios/analysis/data/`")

    page_names = list(PAGES.keys())
    default_page = st.session_state.get("nav_page", page_names[0])
    if default_page not in page_names:
        default_page = page_names[0]
    page = st.sidebar.radio(
        "Navegación",
        page_names,
        index=page_names.index(default_page),
        key="nav_radio",
    )
    st.session_state["nav_page"] = page

    mod = PAGES[page]
    mod.render(filtered, master)


if __name__ == "__main__":
    main()
