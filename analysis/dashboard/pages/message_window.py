"""Message analysis window policy exploration."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.components import render_markdown_file
from lib.report_paths import MESSAGE_ANALYSIS_WINDOW_POLICY

from dashboard.data_loaders import FIGURES_DIR, load_csv

def render(filtered: pd.DataFrame, master: pd.DataFrame) -> None:
    st.header("Ventana de análisis de mensajes")
    st.caption(
        "Política canónica: métricas primarias en ventana completa; "
        "análisis opcional sin último 10%. Ver informe MD."
    )

    policy = load_csv("message_analysis_window_policy.csv")
    if policy is None or policy.empty:
        st.warning("Ejecuta `build_message_analysis_window_policy.py`.")
        return

    if filtered is not None and not filtered.empty and "scenario" in policy.columns:
        scen = set(filtered["scenario"].astype(str))
        policy = policy[policy["scenario"].astype(str).isin(scen)]

    st.subheader("Distribución % mensajes en último 10% sim")
    col = "pct_messages_last_10" if "pct_messages_last_10" in policy.columns else "pct_last_10pct_sim"
    tp_col = "traffic_profile_id" if "traffic_profile_id" in policy.columns else "traffic_profile"
    if col in policy.columns and tp_col in policy.columns:
        plot_df = policy.dropna(subset=[col, tp_col]).copy()
        plot_df[col] = pd.to_numeric(plot_df[col], errors="coerce")
        hist = (
            alt.Chart(plot_df)
            .mark_bar(opacity=0.85)
            .encode(
                alt.X(f"{col}:Q", bin=alt.Bin(maxbins=25), title="% mensajes último 10%"),
                y="count()",
                color=f"{tp_col}:N",
                column=f"{tp_col}:N",
            )
            .properties(height=180)
        )
        st.altair_chart(hist, use_container_width=True)

    st.subheader("Estado de política por escenario")
    tp_show = "traffic_profile_id" if "traffic_profile_id" in policy.columns else "traffic_profile"
    status_cols = [
        c
        for c in [
            "scenario",
            tp_show,
            "policy_status",
            "pct_messages_last_10",
            "pct_messages_first_10",
            "median_creation_time_norm",
            "notes",
        ]
        if c in policy.columns
    ]
    st.dataframe(policy[status_cols], use_container_width=True, height=400)

    if "policy_status" in policy.columns:
        flagged = policy[
            policy["policy_status"].astype(str).isin(
                ["late_message_bias", "burst_exception", "stress_tier"]
            )
        ]
        if not flagged.empty:
            st.subheader("Excepciones / sesgo tardío")
            st.dataframe(flagged[status_cols], use_container_width=True, height=220)

    box_png = FIGURES_DIR / "paper" / "message_creation_time_by_tp_paper.png"
    if not box_png.is_file():
        box_png = FIGURES_DIR / "message_creation_time_boxplot_by_tp.png"
    if box_png.is_file():
        st.subheader("Figura estática")
        st.image(str(box_png), caption=box_png.name, use_container_width=True)

    report = MESSAGE_ANALYSIS_WINDOW_POLICY
    with st.expander("Política metodológica (MD)"):
        render_markdown_file(report, max_chars=16000)

    st.info(
        "**Tiempo útil de simulación** (contactos/movilidad) es distinto de esta ventana de mensajes — "
        "véase página **Tiempo útil**."
    )