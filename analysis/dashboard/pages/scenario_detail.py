"""Single-scenario drill-down."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.components import (
    preview_text_file,
    scenario_picker,
    settings_link,
    show_heatmap,
)
from dashboard.data_loaders import SPATIAL_HEATMAP_DIR, list_raw_report_types, raw_report_path
from lib.paths import REPO_ROOT

def _row_dict(df: pd.DataFrame, scenario: str) -> dict:
    if df is None or df.empty or "scenario" not in df.columns:
        return {}
    m = df["scenario"].astype(str) == scenario
    if not m.any():
        return {}
    return df.loc[m].iloc[0].to_dict()

def render(filtered: pd.DataFrame, master: pd.DataFrame) -> None:
    st.header("Detalle de escenario")
    pool = filtered if not filtered.empty else master
    scenario = scenario_picker(pool, key="detail_scenario")
    if not scenario:
        return

    row = _row_dict(master, scenario)
    if not row:
        st.warning("Escenario no encontrado en master.")
        return

    st.subheader(scenario)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Delivery", _fmt(row.get("delivery_ratio")))
    c2.metric("Latencia media (s)", _fmt(row.get("latency_mean")))
    c3.metric("Drop ratio", _fmt(row.get("drop_ratio")))
    c4.metric("Encounters", _fmt(row.get("total_encounters")))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Cobertura final %", _fmt(row.get("final_coverage_pct")))
    c6.metric("TP", str(row.get("traffic_profile_id", "—")))
    c7.metric("Mapa", str(row.get("map_dataset", "—")))
    c8.metric("Prioridad", str(row.get("priority", "—")))

    c9, c10, c11 = st.columns(3)
    c9.metric("Bench validation", str(row.get("bench_validation_status", "—")))
    c10.metric("Policy mensajes", str(row.get("policy_status", "—")))
    c11.metric("Útil time ratio", _fmt(row.get("useful_time_ratio")))

    tab_cfg, tab_diag, tab_spat, tab_time, tab_rep = st.tabs(
        ["Configuración", "Diagnóstico", "Espacial", "Tráfico temporal", "Reportes ONE"]
    )

    with tab_cfg:
        st.markdown(f"**Base:** `{row.get('scenario_base', '—')}` · **Familia:** `{row.get('family', '—')}`")
        settings_link(row.get("settings_path") or row.get("settings_file"))
        cfg_cols = [
            "movement_models",
            "n_hosts",
            "msg_ttl",
            "world_x",
            "world_y",
            "router",
            "Group.msgTtl_minutes",
        ]
        cfg = {k: row.get(k) for k in cfg_cols if k in row and pd.notna(row.get(k))}
        if cfg:
            st.json(cfg)
        else:
            st.caption("Sin datos de settings_audit.")

    with tab_diag:
        st.write(f"**Flags:** {row.get('problem_flags', '—')}")
        st.write(f"**Acción sugerida:** {row.get('recommended_action_hint', '—')}")
        if row.get("bench_reason"):
            st.write(f"**Benchmark reason:** {row.get('bench_reason')}")
        if row.get("bench_recommended_action"):
            st.write(f"**Benchmark action:** {row.get('bench_recommended_action')}")
        if row.get("delivery_std_by_base") is not None:
            st.write(f"**Std delivery (base):** {row.get('delivery_std_by_base')}")

    with tab_spat:
        show_heatmap(scenario, SPATIAL_HEATMAP_DIR)
        spat = {k: row.get(k) for k in ("cells_visited_pct", "time_to_50pct", "time_to_80pct", "grid_size") if k in row}
        if spat:
            st.json(spat)

    with tab_time:
        time_cols = {
            "n_created": row.get("n_created"),
            "t_median_norm": row.get("t_median_norm"),
            "pct_last_10pct_sim": row.get("pct_last_10pct_sim"),
            "pct_messages_last_10": row.get("pct_messages_last_10"),
            "policy_status": row.get("policy_status"),
            "useful_time_ratio": row.get("useful_time_ratio"),
            "classification": row.get("classification"),
            "data_source": row.get("data_source"),
        }
        st.json({k: v for k, v in time_cols.items() if v is not None and pd.notna(v)})
        if row.get("t_median_norm") is not None:
            try:
                tn = float(row["t_median_norm"])
                if tn < 0.35:
                    st.info("Creación concentrada al inicio/medio (típico TP07 BurstWindow).")
                elif 0.45 <= tn <= 0.55:
                    st.success("Creación repartida en el tiempo (típico TP01–TP06 uniforme).")
            except (TypeError, ValueError):
                pass

    with tab_rep:
        types = list_raw_report_types()
        if not types:
            st.warning(f"No hay reportes en {REPO_ROOT / 'reports'}")
        else:
            rtype = st.selectbox("Tipo de reporte", types, key="detail_report_type")
            path_s = raw_report_path(scenario, rtype)
            if path_s:
                from pathlib import Path

                preview_text_file(Path(path_s))
            else:
                st.warning(f"No existe `{scenario}_{rtype}.txt` (nombre antiguo o sim no ejecutada).")

def _fmt(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    try:
        return f"{float(v):.4g}"
    except (TypeError, ValueError):
        return str(v)