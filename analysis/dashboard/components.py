"""Reusable Streamlit UI helpers."""

from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from lib.paths import REPO_ROOT

def tp_bar_chart(
    df: pd.DataFrame,
    metric: str,
    *,
    title: str,
    tp_col: str = "traffic_profile_id",
) -> alt.Chart | None:
    """Median metric by traffic profile (bar chart)."""
    if df is None or df.empty or metric not in df.columns or tp_col not in df.columns:
        return None
    sub = df[[tp_col, metric]].copy()
    sub[metric] = pd.to_numeric(sub[metric], errors="coerce")
    agg = (
        sub.groupby(tp_col, as_index=False)[metric]
        .median()
        .sort_values(tp_col)
    )
    return (
        alt.Chart(agg)
        .mark_bar()
        .encode(
            x=alt.X(f"{tp_col}:N", title="Traffic Profile", sort=None),
            y=alt.Y(f"{metric}:Q", title=f"Mediana {metric}"),
            tooltip=[tp_col, alt.Tooltip(f"{metric}:Q", format=".3f")],
        )
        .properties(title=title)
    )

def kpi_row(items: list[tuple[str, str | int | float, str | None]]) -> None:
    """items: (label, value, delta_or_help)"""
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        with col:
            st.metric(label, value, help=help_text)

def render_markdown_file(path: Path, *, max_chars: int | None = None) -> None:
    if not path.is_file():
        st.caption(f"No encontrado: {path}")
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if max_chars and len(text) > max_chars:
        st.markdown(text[:max_chars] + "\n\n… *(truncado)*")
    else:
        st.markdown(text)

def scenario_picker(
    df: pd.DataFrame,
    *,
    key: str = "scenario_pick",
    label: str = "Escenario",
) -> str | None:
    if df is None or df.empty or "scenario" not in df.columns:
        st.info("No hay escenarios en el filtro actual.")
        return None
    options = sorted(df["scenario"].astype(str).unique())
    default_idx = 0
    sel = st.session_state.get("selected_scenario")
    if sel in options:
        default_idx = options.index(sel)
    choice = st.selectbox(label, options, index=default_idx, key=key)
    st.session_state["selected_scenario"] = choice
    return choice

def go_to_detail_button(scenario: str) -> None:
    st.session_state["selected_scenario"] = scenario
    st.session_state["nav_page"] = "Detalle escenario"
    st.rerun()

def show_heatmap(scenario: str, heatmap_path: Path) -> None:
    p = heatmap_path / f"{scenario}.png"
    if p.is_file():
        st.image(str(p), caption=str(p.name), use_container_width=True)
    else:
        st.info(
            "Sin heatmap. Genera con:\n"
            "`python3 scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py`"
        )

def settings_link(settings_file: str | None) -> None:
    if not settings_file:
        st.caption("Ruta .settings no disponible.")
        return
    p = Path(settings_file)
    if not p.is_absolute():
        p = REPO_ROOT / settings_file
    if p.is_file():
        st.code(str(p.relative_to(REPO_ROOT) if REPO_ROOT in p.parents else p), language=None)
    else:
        st.caption(f"No encontrado: {settings_file}")

def dataframe_scenarios(
    df: pd.DataFrame,
    *,
    columns: list[str] | None = None,
    height: int = 420,
) -> None:
    if df is None or df.empty:
        st.info("Sin datos.")
        return
    show = df
    if columns:
        cols = [c for c in columns if c in show.columns]
        if cols:
            show = show[cols]
    st.dataframe(show, use_container_width=True, height=height)

def preview_text_file(path: Path, *, max_lines: int = 300) -> None:
    if not path.is_file():
        st.warning(f"No existe: {path}")
        return
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) <= max_lines:
        st.text("\n".join(lines))
    else:
        st.text("\n".join(lines[:max_lines]))
        st.caption(f"Mostrando {max_lines}/{len(lines)} líneas.")