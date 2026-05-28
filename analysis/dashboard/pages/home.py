"""Corpus overview and pipeline health."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.components import kpi_row, render_markdown_file
from dashboard.data_loaders import list_markdown_reports, load_csv, pipeline_status
from lib.paths import ANALYSIS_DIR
from lib.report_paths import DASHBOARD_READINESS_REPORT, RESULTADOS_ACTUALES


def render(filtered: pd.DataFrame, master: pd.DataFrame) -> None:
    st.header("Resumen corpus_v1")

    n = len(master)
    n_bases = master["scenario_base"].nunique() if "scenario_base" in master.columns else 0
    n_tp = master["traffic_profile_id"].nunique() if "traffic_profile_id" in master.columns else 0
    n_fam = master["family"].nunique() if "family" in master.columns else 0
    n_metrics = int(master["has_metrics"].sum()) if "has_metrics" in master.columns else 0

    kpi_row(
        [
            ("Simulaciones", n, "manifest 570"),
            ("Escenarios base", n_bases, "45+15 stress"),
            ("Perfiles TP", n_tp, "TP01–TP12"),
            ("Familias", n_fam, "6+stress"),
            ("Con métricas", n_metrics, f"{n - n_metrics} sin output"),
        ]
    )

    if "family" in master.columns and "traffic_profile_id" in master.columns:
        st.subheader("Composición familia × TP")
        comp = (
            master.groupby(["family", "traffic_profile_id"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
        )
        chart = (
            alt.Chart(comp)
            .mark_bar()
            .encode(
                x=alt.X("family:N", title="Familia"),
                y="count:Q",
                color="traffic_profile_id:N",
                tooltip=["family", "traffic_profile_id", "count"],
            )
        )
        st.altair_chart(chart, use_container_width=True)

    st.subheader("Estado del pipeline")
    status = pipeline_status()
    rows = [{"artifact": k.replace("_", " "), "ok": ok} for k, ok in status.items()]
    sdf = pd.DataFrame(rows)
    for _, r in sdf.iterrows():
        icon = "🟢" if r["ok"] else "🔴"
        st.write(f"{icon} **{r['artifact']}**")

    st.subheader("Enlaces canónicos")
    for label, path in [
        ("Resultados actuales", REPORTS_ANALYSIS_DIR / "RESULTADOS_ACTUALES.md"),
        ("Índice figuras paper", ANALYSIS_DIR / "figures" / "paper" / "FIGURES_AND_TABLES_INDEX.md"),
        ("Dashboard readiness", DASHBOARD_READINESS_REPORT),
    ]:
        if path.is_file():
            with st.expander(label):
                render_markdown_file(path, max_chars=6000)

    st.subheader("Otros informes")
    for label, path in list_markdown_reports():
        if path.name in ("RESULTADOS_ACTUALES.md", "FIGURES_AND_TABLES_INDEX.md", "dashboard_readiness_report.md"):
            continue
        with st.expander(label):
            render_markdown_file(path, max_chars=5000)

    tp_sum = load_csv("tp_validation_summary.csv")
    if tp_sum is not None:
        with st.expander("Resumen validación TP"):
            st.dataframe(tp_sum, use_container_width=True, height=240)

    if len(filtered) != len(master):
        st.caption(f"Vista filtrada: {len(filtered)} / {len(master)} escenarios (sidebar).")
