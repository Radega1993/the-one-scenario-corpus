"""Traffic profile KPI summary and aggregated simulation metrics."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.components import render_markdown_file, tp_bar_chart
from lib.report_paths import TRAFFIC_PROFILE_KPI_ANALYSIS

from dashboard.data_loaders import load_tp_kpi_summary


def render(filtered: pd.DataFrame, master: pd.DataFrame) -> None:
    st.header("KPIs benchmark por Traffic Profile")
    st.caption(
        "Resumen experimental por TP (`traffic_profile_kpi_summary.csv`). "
        "Comparación multi-protocolo: ver página **Protocolos**."
    )

    kpi = load_tp_kpi_summary()
    if kpi is None or kpi.empty:
        st.warning("Ejecuta `analyze_traffic_profile_kpis.py`.")
        return

    st.subheader("Definición KPI por perfil (12 filas)")
    show = [
        c
        for c in [
            "tp_id",
            "tp_name",
            "primary_kpi",
            "secondary_kpi",
            "validation_status",
            "paper_interpretation",
        ]
        if c in kpi.columns
    ]
    st.dataframe(kpi[show], use_container_width=True, height=360)

    for _, row in kpi.iterrows():
        tid = row.get("tp_id", "—")
        with st.expander(f"{tid} — {row.get('tp_name', '')} ({row.get('validation_status', '—')})"):
            st.markdown(f"**Intención:** {row.get('experimental_intent', '—')}")
            st.markdown(f"**Observado:** {row.get('observed_behavior', '—')}")
            st.markdown(f"**Paper:** {row.get('paper_interpretation', '—')}")

    pool = filtered if not filtered.empty else master
    if pool.empty or "traffic_profile_id" not in pool.columns:
        return

    st.subheader("Agregados de simulación (filtro sidebar)")
    for metric, title in [
        ("delivery_ratio", "Mediana delivery por TP"),
        ("overhead_ratio", "Mediana overhead por TP"),
        ("drop_ratio", "Mediana drop por TP"),
    ]:
        if metric in pool.columns:
            chart = tp_bar_chart(pool, metric, title=title)
            if chart is not None:
                st.altair_chart(chart, use_container_width=True)

    report = TRAFFIC_PROFILE_KPI_ANALYSIS
    with st.expander("Informe completo KPIs TP"):
        render_markdown_file(report, max_chars=14000)
