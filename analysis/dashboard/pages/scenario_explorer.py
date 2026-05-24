"""Filterable scenario table."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.components import dataframe_scenarios, go_to_detail_button

DEFAULT_COLUMNS = [
    "scenario",
    "family",
    "scenario_base",
    "traffic_profile_id",
    "map_dataset",
    "delivery_ratio",
    "latency_mean",
    "drop_ratio",
    "total_encounters",
    "priority",
    "problem_flags",
    "final_coverage_pct",
    "bench_validation_status",
    "policy_status",
    "useful_time_ratio",
    "t_median_norm",
    "tp_validation_status",
    "has_heatmap",
    "has_metrics",
]


def render(filtered: pd.DataFrame, _master: pd.DataFrame) -> None:
    st.header("Explorador de escenarios")
    if filtered.empty:
        st.warning("Ningún escenario coincide con los filtros.")
        return

    st.caption("Filtros globales en la barra lateral (delivery, drop, cobertura, validación).")

    quick = st.columns(3)
    with quick[0]:
        if st.button("Solo error_probable", help="Benchmark validation"):
            if "bench_validation_status" in filtered.columns:
                st.session_state["_explorer_bench"] = ["error_probable"]
    with quick[1]:
        if st.button("Sin métricas"):
            if "has_metrics" in filtered.columns:
                st.session_state["_explorer_no_metrics"] = True
    with quick[2]:
        if st.button("Limpiar filtros rápidos"):
            st.session_state.pop("_explorer_bench", None)
            st.session_state.pop("_explorer_no_metrics", None)

    show = filtered.copy()
    if st.session_state.get("_explorer_bench") and "bench_validation_status" in show.columns:
        show = show[show["bench_validation_status"].isin(st.session_state["_explorer_bench"])]
    if st.session_state.get("_explorer_no_metrics") and "has_metrics" in show.columns:
        show = show[~show["has_metrics"]]

    dataframe_scenarios(show, columns=DEFAULT_COLUMNS, height=480)

    st.download_button(
        "Descargar CSV filtrado",
        show.to_csv(index=False).encode("utf-8"),
        file_name="scenarios_filtered.csv",
        mime="text/csv",
    )

    st.subheader("Ir al detalle")
    scenarios = sorted(show["scenario"].astype(str).unique())
    pick = st.selectbox("Escenario", scenarios, key="explorer_pick_detail")
    if st.button("Ver detalle", type="primary"):
        go_to_detail_button(pick)
