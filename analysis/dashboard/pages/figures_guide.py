"""Figures catalog and curated galleries."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from dashboard.components import render_markdown_file
from dashboard.data_loaders import FIGURES_DIR

AGG_DIR = FIGURES_DIR / "aggregated"
PAPER_MAIN = FIGURES_DIR / "paper" / "main"
PAPER_SUPP = FIGURES_DIR / "paper" / "supplementary"


def _show_images(directory: Path, pattern: str = "*.png", caption_prefix: str = "") -> int:
    if not directory.is_dir():
        st.caption(f"No existe `{directory}`.")
        return 0
    files = sorted(directory.glob(pattern))
    n = 0
    for f in files:
        st.image(str(f), caption=f"{caption_prefix}{f.name}", use_container_width=True)
        n += 1
    return n


def render(filtered, master) -> None:
    st.header("Figuras del análisis")
    st.caption(
        "Catálogo en `figures/README.md`. Con 720 escenarios evite heatmaps N×N; "
        "use `aggregated/` y `paper/main/`."
    )

    readme = FIGURES_DIR / "README.md"
    with st.expander("Guía completa (README)", expanded=False):
        render_markdown_file(readme, max_chars=50000)

    tab_rec, tab_tp, tab_spatial, tab_legacy = st.tabs(
        ["Recomendadas", "Validación TP", "Espacial", "Legacy / depuración"]
    )

    with tab_rec:
        st.subheader("Paper (`figures/paper/main/`)")
        n1 = _show_images(PAPER_MAIN)
        st.subheader("Agregadas (`figures/aggregated/`)")
        n2 = _show_images(AGG_DIR)
        if n1 + n2 == 0:
            st.info(
                "Ejecuta `python3 run_analysis.py --phase figures_paper` y "
                "`python3 run_figures_aggregated.py --corpus corpus_v2`."
            )

    with tab_tp:
        for name in (
            "message_creation_time_hist_by_tp.png",
            "message_creation_time_boxplot_by_tp.png",
        ):
            p = FIGURES_DIR / name
            if p.is_file():
                st.image(str(p), caption=name, use_container_width=True)
            else:
                st.caption(f"Falta `{name}` — `analyze_message_creation_times.py`.")

    with tab_spatial:
        curves = FIGURES_DIR / "spatial_occupancy_curves_by_family.png"
        if curves.is_file():
            st.image(str(curves), caption=curves.name, use_container_width=True)
        cov = AGG_DIR / "spatial_coverage_by_family.png"
        if cov.is_file():
            st.image(str(cov), caption=cov.name, use_container_width=True)
        st.subheader("Galerías por familia")
        _show_images(AGG_DIR, "spatial_gallery_*.png", "gallery: ")

    with tab_legacy:
        st.warning(
            "Heatmaps 720×720 y PCA con etiquetas por escenario: solo depuración. "
            "Preferir histogramas y figuras agregadas."
        )
        for name in (
            "histogram_correlations_pearson.png",
            "histogram_correlations_outputs.png",
            "heatmap_feature_feature_core.png",
            "scatter_max_r_pair_regression.png",
        ):
            p = FIGURES_DIR / name
            if p.is_file():
                st.image(str(p), caption=name, use_container_width=True)
        hm = FIGURES_DIR / "heatmap_pearson.png"
        if hm.is_file():
            st.image(str(hm), caption=f"{hm.name} (ilegible a escala completa)", use_container_width=True)
