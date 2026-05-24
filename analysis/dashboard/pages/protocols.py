"""Future multi-protocol benchmark placeholder."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.data_loaders import DATA_DIR, load_csv


def render(filtered: pd.DataFrame, master: pd.DataFrame) -> None:
    st.header("Protocolos de routing")
    st.caption("Corpus actual: **Epidemic** únicamente (720 simulaciones).")

    st.subheader("Estado actual")
    if "router" in master.columns:
        routers = master["router"].dropna().astype(str).value_counts()
        st.dataframe(
            routers.reset_index().rename(columns={"index": "router", "count": "n"}),
            hide_index=True,
        )
    else:
        st.write("Columna `router` no disponible — ejecuta `audit_settings.py`.")

    defs_path = DATA_DIR / "protocol_benchmark_kpi_definitions.csv"
    defs = load_csv("protocol_benchmark_kpi_definitions.csv") if defs_path.is_file() else None

    st.subheader("KPIs planificados (comparación futura)")
    if defs is not None and not defs.empty:
        st.dataframe(defs, use_container_width=True)
    else:
        skeleton = pd.DataFrame(
            [
                {
                    "protocol": "Epidemic",
                    "kpi": "delivery_ratio",
                    "direction": "maximize",
                    "status": "measured",
                },
                {
                    "protocol": "Epidemic",
                    "kpi": "overhead_ratio",
                    "direction": "minimize",
                    "status": "measured",
                },
                {
                    "protocol": "Epidemic",
                    "kpi": "latency_mean",
                    "direction": "minimize",
                    "status": "measured",
                },
                {
                    "protocol": "Epidemic",
                    "kpi": "drop_ratio",
                    "direction": "minimize",
                    "status": "measured",
                },
                {
                    "protocol": "(futuro)",
                    "kpi": "delivery_ratio",
                    "direction": "maximize",
                    "status": "pending_simulation",
                },
            ]
        )
        st.dataframe(skeleton, use_container_width=True, hide_index=True)
        st.caption(
            "Cuando exista `protocol_benchmark_kpi_definitions.csv`, esta tabla se cargará automáticamente."
        )

    st.markdown(
        """
### Fase futura (sin simular desde el dashboard)

1. Definir protocolos candidatos (p. ej. PRoPHET, MaxProp) y variante de settings por escenario base.
2. Generar manifest multi-protocolo y ejecutar batch ONE.
3. Poblar `protocol_benchmark_kpi_definitions.csv` y figuras en `figures/paper/`.
4. Usar página **KPIs benchmark** para perfiles TP y esta página para contraste entre protocolos.

**Figura placeholder:** `figures/paper/protocol_comparison_placeholder.png` (si existe en índice paper).
        """
    )

    pool = filtered if not filtered.empty else master
    if not pool.empty and "delivery_ratio" in pool.columns:
        st.subheader("Baseline Epidemic (filtro actual)")
        agg = (
            pool.groupby("traffic_profile_id", as_index=False)["delivery_ratio"]
            .median()
            .sort_values("traffic_profile_id")
        )
        st.dataframe(agg, use_container_width=True, hide_index=True)
