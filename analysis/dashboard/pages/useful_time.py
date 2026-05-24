"""Useful simulation time metrics."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.components import render_markdown_file, tp_bar_chart
from lib.report_paths import USEFUL_SIMULATION_TIME_REPORT

from dashboard.data_loaders import load_csv


def render(filtered: pd.DataFrame, master: pd.DataFrame) -> None:
    st.header("Tiempo útil de simulación")
    st.caption(
        "Ratio de tiempo con actividad de contacto útil (`useful_simulation_time_metrics.csv`). "
        "No confundir con la ventana de análisis de mensajes."
    )

    pool = filtered if not filtered.empty else master
    if "useful_time_ratio" not in pool.columns:
        ut = load_csv("useful_simulation_time_metrics.csv")
        if ut is None or ut.empty:
            st.warning("Ejecuta el pipeline de useful simulation time.")
            return
        sc = "scenario" if "scenario" in ut.columns else ut.columns[0]
        if sc != "scenario":
            ut = ut.rename(columns={sc: "scenario"})
        pool = pool.merge(
            ut[["scenario", "useful_time_ratio", "classification", "tail_time_ratio"]].drop_duplicates("scenario"),
            on="scenario",
            how="left",
        )

    if pool.empty:
        st.warning("Sin datos tras filtros.")
        return

    st.subheader("Distribución useful_time_ratio")
    sub = pool.dropna(subset=["useful_time_ratio"]).copy()
    sub["useful_time_ratio"] = pd.to_numeric(sub["useful_time_ratio"], errors="coerce")
    if not sub.empty:
        if "family" in sub.columns:
            chart = (
                alt.Chart(sub)
                .mark_boxplot()
                .encode(
                    x=alt.X("family:N", title="Familia"),
                    y=alt.Y("useful_time_ratio:Q", title="useful_time_ratio"),
                    color="family:N",
                )
            )
            st.altair_chart(chart, use_container_width=True)
        chart_tp = tp_bar_chart(sub, "useful_time_ratio", title="Mediana useful_time_ratio por TP")
        if chart_tp is not None:
            st.altair_chart(chart_tp, use_container_width=True)

    if "classification" in sub.columns:
        st.subheader("Clasificación")
        cls = sub["classification"].value_counts().reset_index()
        cls.columns = ["classification", "count"]
        st.altair_chart(
            alt.Chart(cls).mark_bar().encode(x="classification:N", y="count:Q"),
            use_container_width=True,
        )

    if "delivery_ratio" in sub.columns:
        st.subheader("Útil vs delivery")
        scatter = (
            alt.Chart(sub.dropna(subset=["delivery_ratio"]))
            .mark_circle(opacity=0.35, size=30)
            .encode(
                x=alt.X("useful_time_ratio:Q", title="useful_time_ratio"),
                y=alt.Y("delivery_ratio:Q", title="delivery_ratio"),
                color="traffic_profile_id:N" if "traffic_profile_id" in sub.columns else alt.value("steelblue"),
                tooltip=["scenario", "useful_time_ratio", "delivery_ratio"],
            )
        )
        st.altair_chart(scatter, use_container_width=True)

    show = [
        c
        for c in [
            "scenario",
            "family",
            "traffic_profile_id",
            "useful_time_ratio",
            "tail_time_ratio",
            "classification",
            "delivery_ratio",
        ]
        if c in sub.columns
    ]
    st.dataframe(sub[show], use_container_width=True, height=360)

    if USEFUL_SIMULATION_TIME_REPORT.is_file():
        with st.expander(USEFUL_SIMULATION_TIME_REPORT.stem):
            render_markdown_file(USEFUL_SIMULATION_TIME_REPORT, max_chars=12000)

    st.info("Ventana de mensajes: página **Ventana mensajes**.")
