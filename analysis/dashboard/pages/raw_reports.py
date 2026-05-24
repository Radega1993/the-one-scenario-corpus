"""Browse raw ONE simulation reports in repo/reports."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from dashboard.components import preview_text_file
from lib.paths import REPORTS_DIR


def render(_filtered, _master) -> None:
    st.header("Reportes crudos (repo/reports)")
    if not REPORTS_DIR.is_dir():
        st.warning(f"No existe: {REPORTS_DIR}")
        return

    parsed: list[tuple[str, str, Path]] = []
    for f in sorted(REPORTS_DIR.glob("*.txt")):
        stem = f.stem
        if "_" not in stem:
            continue
        scenario, report_name = stem.rsplit("_", 1)
        parsed.append((scenario, report_name, f))

    if not parsed:
        st.info("No hay reportes .txt.")
        return

    scenarios = sorted({x[0] for x in parsed})
    report_types = sorted({x[1] for x in parsed})
    st.caption(f"Escenarios: {len(scenarios)} | Tipos: {len(report_types)} | Archivos: {len(parsed)}")

    c1, c2 = st.columns(2)
    with c1:
        scenario = st.selectbox("Escenario", scenarios, key="raw_scenario")
    with c2:
        rtype = st.selectbox("Tipo de reporte", report_types, key="raw_type")

    target = next((p for sc, rt, p in parsed if sc == scenario and rt == rtype), None)
    if target is None:
        st.warning("No se encontró ese reporte.")
        return

    st.caption(str(target.relative_to(REPORTS_DIR.parent)))
    show_all = st.checkbox("Archivo completo", value=False)
    if show_all:
        preview_text_file(target, max_lines=100000)
    else:
        preview_text_file(target, max_lines=300)
