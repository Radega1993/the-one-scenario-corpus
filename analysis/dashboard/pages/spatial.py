"""Spatial occupancy heatmaps and coverage."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.components import dataframe_scenarios, scenario_picker, show_heatmap
from dashboard.data_loaders import SPATIAL_HEATMAP_DIR, load_csv

def render(filtered: pd.DataFrame, master: pd.DataFrame) -> None:
    st.header("Ocupación espacial")

    spatial = load_csv("spatial_occupancy_metrics.csv")
    n_heat = int(master["has_heatmap"].sum()) if "has_heatmap" in master.columns else 0
    st.caption(f"Heatmaps generados: **{n_heat}** / {len(master)}")

    pool = filtered if not filtered.empty else master
    scenario = scenario_picker(pool, key="spatial_scenario")
    if scenario:
        show_heatmap(scenario, SPATIAL_HEATMAP_DIR)

    if spatial is not None and not spatial.empty:
        st.subheader("Métricas de cobertura")
        cov_col = (
            "coverage_road_cells_pct"
            if "coverage_road_cells_pct" in spatial.columns
            else "coverage_world_pct"
            if "coverage_world_pct" in spatial.columns
            else "final_coverage_pct"
        )
        cols = [
            "scenario",
            "traffic_profile_id",
            "map_dataset",
            cov_col,
            "coverage_world_pct",
            "coverage_map_bbox_pct",
            "time_to_50pct",
        ]
        cols = [c for c in cols if c in spatial.columns]
        dataframe_scenarios(spatial, columns=cols, height=300)

        if cov_col in spatial.columns:
            sp = spatial.dropna(subset=[cov_col])
            if "traffic_profile_id" in sp.columns and not sp.empty:
                chart = (
                    alt.Chart(sp)
                    .mark_bar(opacity=0.7)
                    .encode(
                        x=alt.X("traffic_profile_id:N", title="TP"),
                        y=alt.Y(f"mean({cov_col}):Q", title="Cobertura road cells %"),
                        color="map_dataset:N",
                    )
                )
                st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Ejecuta `analyze_spatial_occupancy.py` para métricas y heatmaps.")

    if filtered is not None and "has_heatmap" in filtered.columns:
        missing = filtered[~filtered["has_heatmap"].astype(bool)]
        if not missing.empty:
            with st.expander(f"Sin heatmap ({len(missing)} escenarios filtrados)"):
                st.dataframe(
                    missing[["scenario", "traffic_profile_id", "map_dataset"]].head(50),
                    use_container_width=True,
                )