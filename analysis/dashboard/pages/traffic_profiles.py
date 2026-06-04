"""Traffic profile (TP01–TP12) validation."""

from __future__ import annotations

import streamlit as st

from dashboard.components import render_markdown_file, tp_bar_chart
from lib.report_paths import TP_VALIDATION_REPORT

from dashboard.data_loaders import load_csv, load_tp_kpi_summary

def render(filtered: pd.DataFrame, master: pd.DataFrame) -> None:
    st.header("Perfiles de tráfico (TP01–TP12)")
    st.caption(
        "Validación de settings y agregados por TP. "
        "KPIs experimentales: página **KPIs benchmark**. "
        "Ventana de mensajes: página **Ventana mensajes**."
    )

    kpi = load_tp_kpi_summary()
    if kpi is not None:
        with st.expander("Resumen KPI por TP (12 filas)"):
            st.dataframe(
                kpi[
                    [
                        c
                        for c in ["tp_id", "tp_name", "primary_kpi", "validation_status"]
                        if c in kpi.columns
                    ]
                ],
                use_container_width=True,
                height=280,
            )
        st.caption("Abre **KPIs benchmark** en el menú lateral para el informe completo.")

    tp_sum = load_csv("tp_validation_summary.csv")
    if tp_sum is not None:
        st.subheader("Agregados por TP (validación settings)")
        st.dataframe(tp_sum, use_container_width=True, height=300)

    by_base = load_csv("tp_validation_by_base.csv")
    if by_base is not None:
        with st.expander("Separación TP por escenario base"):
            st.dataframe(by_base, use_container_width=True, height=320)

    pool = filtered if not filtered.empty else master
    if "delivery_ratio" in pool.columns:
        st.subheader("Delivery por TP (simulación, filtro actual)")
        chart = tp_bar_chart(pool, "delivery_ratio", title="Mediana delivery por TP")
        if chart is not None:
            st.altair_chart(chart, use_container_width=True)

    val = load_csv("tp_validation_settings.csv")
    if val is not None:
        with st.expander("Detalle validación por escenario"):
            st.dataframe(val.head(100), use_container_width=True, height=280)

    report = TP_VALIDATION_REPORT
    with st.expander("Informe validación TP"):
        render_markdown_file(report, max_chars=12000)