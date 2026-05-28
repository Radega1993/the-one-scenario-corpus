"""Scenario diagnosis and benchmark validation."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.components import render_markdown_file
from dashboard.data_loaders import load_csv
from lib.report_paths import (
    CORPUS_BENCHMARK_VALIDATION,
    CORPUS_V2_REVISION_CHANGELOG,
    SCENARIO_DIAGNOSIS,
)


def render(filtered: pd.DataFrame, master: pd.DataFrame) -> None:
    st.header("Diagnóstico del corpus")

    pool = filtered if not filtered.empty else master

    bench = load_csv("corpus_benchmark_validation.csv")
    if bench is not None and not bench.empty:
        st.subheader("Validación benchmark (corpus_v1)")
        b = bench.copy()
        sc = "scenario" if "scenario" in b.columns else "scenario_name"
        if sc != "scenario":
            b = b.rename(columns={sc: "scenario"})
        if pool is not None and not pool.empty:
            scen = set(pool["scenario"].astype(str))
            b = b[b["scenario"].astype(str).isin(scen)]

        statuses = sorted(b["validation_status"].dropna().astype(str).unique()) if "validation_status" in b.columns else []
        sel = st.multiselect(
            "validation_status",
            statuses,
            default=statuses,
            key="audit_bench_status",
        )
        if sel and "validation_status" in b.columns:
            b = b[b["validation_status"].astype(str).isin(sel)]

        show_b = [
            c
            for c in [
                "scenario",
                "traffic_profile",
                "delivery_ratio",
                "validation_status",
                "reason",
                "recommended_action",
            ]
            if c in b.columns
        ]
        st.dataframe(b[show_b], use_container_width=True, height=320)

        if "validation_status" in b.columns:
            vc = b["validation_status"].value_counts().reset_index()
            vc.columns = ["status", "count"]
            st.altair_chart(
                alt.Chart(vc).mark_bar().encode(x="count:Q", y=alt.Y("status:N", sort="-x")),
                use_container_width=True,
            )

    st.subheader("Diagnóstico escenarios (flags)")
    diag = load_csv("scenario_diagnosis.csv")
    if diag is None or diag.empty:
        st.warning("Ejecuta `diagnose_scenarios.py`.")
    else:
        d = diag.copy()
        if pool is not None and not pool.empty and "scenario" in d.columns:
            scen = set(pool["scenario"].astype(str))
            d = d[d["scenario"].astype(str).isin(scen)]

        c1, c2 = st.columns(2)
        with c1:
            priorities = st.multiselect(
                "Prioridad",
                sorted(d["priority"].dropna().astype(str).unique()) if "priority" in d.columns else [],
                default=None,
            )
        with c2:
            flag_filter = st.text_input("Filtrar problem_flags", placeholder="MAP_UNDERUSED")

        if priorities and "priority" in d.columns:
            d = d[d["priority"].astype(str).isin(priorities)]
        if flag_filter.strip() and "problem_flags" in d.columns:
            d = d[
                d["problem_flags"]
                .astype(str)
                .str.contains(flag_filter.strip(), case=False, na=False)
            ]

        st.caption(f"Filas: {len(d)}")
        show_cols = [
            c
            for c in [
                "scenario",
                "family",
                "scenario_base",
                "traffic_profile_id",
                "map_dataset",
                "delivery_ratio",
                "total_encounters",
                "priority",
                "problem_flags",
                "recommended_action_hint",
            ]
            if c in d.columns
        ]
        st.dataframe(d[show_cols], use_container_width=True, height=360)

        if "problem_flags" in d.columns:
            flags = (
                d["problem_flags"]
                .astype(str)
                .str.split("|")
                .explode()
                .value_counts()
                .head(12)
                .reset_index()
            )
            flags.columns = ["flag", "count"]
            chart = alt.Chart(flags).mark_bar().encode(x="count:Q", y=alt.Y("flag:N", sort="-x"))
            st.altair_chart(chart, use_container_width=True)

    rev = load_csv("corpus_v1_revision_prioritized.csv")
    if rev is not None:
        with st.expander("Plan de revisión corpus_v1"):
            st.dataframe(rev.head(80), use_container_width=True, height=280)

    for label, p in [
        ("Validación benchmark", CORPUS_BENCHMARK_VALIDATION),
        ("Diagnóstico", SCENARIO_DIAGNOSIS),
        ("Changelog revisión", CORPUS_V2_REVISION_CHANGELOG),
    ]:
        if p.is_file():
            with st.expander(label):
                render_markdown_file(p, max_chars=10000)
