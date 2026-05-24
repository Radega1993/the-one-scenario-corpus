"""Cached CSV loaders and master scenario table for the dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from lib.paths import (
    ANALYSIS_DIR,
    DATA_DIR,
    DEFAULT_MANIFEST_V2,
    REPORTS_ANALYSIS_DIR,
    REPORTS_DIR,
    REPO_ROOT,
)
from lib.report_paths import (
    CORPUS_V2_BENCHMARK_VALIDATION,
    CORPUS_V2_REVISION_CHANGELOG,
    DASHBOARD_READINESS_REPORT,
    MESSAGE_ANALYSIS_WINDOW_POLICY,
    PAPER_FIGURES_TABLES_READINESS,
    RESULTADOS_ACTUALES,
    SCENARIO_DIAGNOSIS,
    SPATIAL_OCCUPANCY_ANALYSIS_SUMMARY,
    TP_VALIDATION_REPORT,
    TRAFFIC_PROFILE_KPI_ANALYSIS,
    USEFUL_SIMULATION_TIME_REPORT,
)

FIGURES_DIR = ANALYSIS_DIR / "figures"
SPATIAL_HEATMAP_DIR = FIGURES_DIR / "spatial_heatmaps"

# Optional CSV joins (scenario key = scenario from manifest)
_OPTIONAL_CSV: dict[str, tuple[str, list[str] | None]] = {
    "output_metrics": ("output_metrics.csv", None),
    "indirect": ("indirect_features_diego.csv", ["total_encounters"]),
    "diagnosis": ("scenario_diagnosis.csv", None),
    "settings_audit": (
        "settings_audit.csv",
        [
            "map_dataset",
            "movement_models",
            "n_hosts",
            "msg_ttl",
            "world_x",
            "world_y",
            "router",
            "settings_path",
        ],
    ),
    "spatial": (
        "spatial_occupancy_metrics.csv",
        [
            "final_coverage_pct",
            "cells_visited_pct",
            "time_to_50pct",
            "time_to_80pct",
            "grid_size",
        ],
    ),
    "msg_time": (
        "message_creation_time_summary.csv",
        [
            "n_created",
            "t_median",
            "pct_last_10pct_sim",
            "pct_first_10pct_sim",
            "data_source",
        ],
    ),
    "tp_validation": ("tp_validation_settings.csv", ["status"]),
    "useful_time": (
        "useful_simulation_time_metrics.csv",
        ["useful_time_ratio", "classification", "tail_time_ratio"],
    ),
    "msg_window": (
        "message_analysis_window_policy.csv",
        [
            "policy_status",
            "pct_messages_last_10",
            "pct_messages_first_10",
            "median_creation_time_norm",
        ],
    ),
    "bench_val": (
        "corpus_v2_benchmark_validation.csv",
        ["validation_status", "reason", "recommended_action"],
    ),
}


def _scenario_col(df: pd.DataFrame) -> str:
    if "scenario" in df.columns:
        return "scenario"
    if "scenario_name" in df.columns:
        return "scenario_name"
    return df.columns[0]


@st.cache_data(ttl=60)
def load_csv(name: str) -> pd.DataFrame | None:
    path = DATA_DIR / name
    if not path.is_file():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


@st.cache_data(ttl=60)
def load_features_table(core_only: bool = False) -> pd.DataFrame | None:
    name = "features_core.csv" if core_only else "features.csv"
    df = load_csv(name)
    if df is None or df.empty:
        return None
    if "scenario" not in df.columns and df.columns[0]:
        df = df.rename(columns={df.columns[0]: "scenario"})
    return df


@st.cache_data(ttl=60)
def load_manifest() -> pd.DataFrame:
    path = DEFAULT_MANIFEST_V2
    if not path.is_file():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "scenario_name" in df.columns:
        df = df.rename(columns={"scenario_name": "scenario"})
    if "scenario" not in df.columns:
        df["scenario"] = df.iloc[:, 0].astype(str)
    return df


@st.cache_data(ttl=60)
def load_tp_kpi_summary() -> pd.DataFrame | None:
    return load_csv("traffic_profile_kpi_summary.csv")


@st.cache_data(ttl=60)
def file_mtime(path_str: str) -> float | None:
    p = Path(path_str)
    if p.is_file():
        return p.stat().st_mtime
    return None


@st.cache_data(ttl=120)
def heatmap_exists(scenario: str) -> bool:
    return (SPATIAL_HEATMAP_DIR / f"{scenario}.png").is_file()


@st.cache_data(ttl=120)
def list_raw_report_types() -> list[str]:
    if not REPORTS_DIR.is_dir():
        return []
    types: set[str] = set()
    for f in REPORTS_DIR.glob("*.txt"):
        stem = f.stem
        if "_" in stem:
            types.add(stem.rsplit("_", 1)[-1])
    return sorted(types)


@st.cache_data(ttl=120)
def raw_report_path(scenario: str, report_type: str) -> str | None:
    p = REPORTS_DIR / f"{scenario}_{report_type}.txt"
    return str(p) if p.is_file() else None


def _merge_optional(master: pd.DataFrame, key: str) -> pd.DataFrame:
    spec = _OPTIONAL_CSV.get(key)
    if not spec:
        return master
    fname, cols = spec
    df = load_csv(fname)
    if df is None or df.empty:
        return master
    sc = _scenario_col(df)
    sub = df.copy()
    if sc != "scenario":
        sub = sub.rename(columns={sc: "scenario"})
    if cols:
        keep = ["scenario"] + [c for c in cols if c in sub.columns]
        sub = sub[keep]
        if key == "tp_validation" and "status" in sub.columns:
            sub = sub.rename(columns={"status": "tp_validation_status"})
        if key == "indirect" and "total_encounters" in sub.columns:
            sub = sub.rename(columns={"total_encounters": "total_encounters_indirect"})
        if key == "bench_val":
            renames = {
                "validation_status": "bench_validation_status",
                "reason": "bench_reason",
                "recommended_action": "bench_recommended_action",
            }
            sub = sub.rename(columns={k: v for k, v in renames.items() if k in sub.columns})
        if key == "msg_window" and "median_creation_time_norm" in sub.columns:
            if "median_creation_time_norm" in master.columns:
                sub = sub.rename(columns={"median_creation_time_norm": "msg_window_median_norm"})
    return master.merge(sub, on="scenario", how="left", suffixes=("", f"_{key}"))


def _merge_tp_kpi(master: pd.DataFrame) -> pd.DataFrame:
    kpi = load_tp_kpi_summary()
    if kpi is None or kpi.empty or "traffic_profile_id" not in master.columns:
        return master
    sub = kpi.copy()
    if "validation_status" in sub.columns:
        sub = sub.rename(columns={"validation_status": "tp_kpi_validation_status"})
    cols = [c for c in sub.columns if c != "tp_id" or c == "tp_id"]
    return master.merge(
        sub,
        left_on="traffic_profile_id",
        right_on="tp_id",
        how="left",
        suffixes=("", "_kpi"),
    )


@st.cache_data(ttl=60)
def build_master_table() -> pd.DataFrame:
    manifest = load_manifest()
    if manifest.empty:
        return pd.DataFrame()

    master = manifest.copy()
    if "scenario" not in master.columns:
        master["scenario"] = master.get("scenario_name", master.iloc[:, 0]).astype(str)

    for key in _OPTIONAL_CSV:
        master = _merge_optional(master, key)

    master = _merge_tp_kpi(master)

    if "total_encounters_indirect" in master.columns:
        if "total_encounters" not in master.columns:
            master["total_encounters"] = master["total_encounters_indirect"]
        else:
            master["total_encounters"] = master["total_encounters"].fillna(
                master["total_encounters_indirect"]
            )

    if "t_median" in master.columns and "Scenario.endTime" in master.columns:
        end = pd.to_numeric(master["Scenario.endTime"], errors="coerce")
        med = pd.to_numeric(master["t_median"], errors="coerce")
        master["t_median_norm"] = med / end.replace(0, pd.NA)

    if "pct_last_10pct_sim" in master.columns and "pct_messages_last_10" not in master.columns:
        master["pct_messages_last_10"] = master["pct_last_10pct_sim"]

    scenarios = master["scenario"].astype(str).tolist()
    master["has_heatmap"] = [heatmap_exists(s) for s in scenarios]
    master["has_metrics"] = master["delivery_ratio"].notna() if "delivery_ratio" in master.columns else False
    master["has_message_stats"] = [
        raw_report_path(s, "MessageStatsReport") is not None for s in scenarios
    ]

    return master


@st.cache_data(ttl=60)
def pipeline_status() -> dict[str, bool]:
    return {
        "manifest": DEFAULT_MANIFEST_V2.is_file(),
        "features": (DATA_DIR / "features.csv").is_file(),
        "features_core": (DATA_DIR / "features_core.csv").is_file(),
        "output_metrics": (DATA_DIR / "output_metrics.csv").is_file(),
        "indirects": (DATA_DIR / "indirect_features_diego.csv").is_file(),
        "diagnosis": (DATA_DIR / "scenario_diagnosis.csv").is_file(),
        "settings_audit": (DATA_DIR / "settings_audit.csv").is_file(),
        "tp_validation": (DATA_DIR / "tp_validation_settings.csv").is_file(),
        "msg_creation_time": (DATA_DIR / "message_creation_time_summary.csv").is_file(),
        "spatial_metrics": (DATA_DIR / "spatial_occupancy_metrics.csv").is_file(),
        "correlation": (DATA_DIR / "correlation_pearson.csv").is_file(),
        "spatial_heatmaps_dir": SPATIAL_HEATMAP_DIR.is_dir(),
        "useful_time": (DATA_DIR / "useful_simulation_time_metrics.csv").is_file(),
        "msg_window_policy": (DATA_DIR / "message_analysis_window_policy.csv").is_file(),
        "tp_kpi_summary": (DATA_DIR / "traffic_profile_kpi_summary.csv").is_file(),
        "bench_validation": (DATA_DIR / "corpus_v2_benchmark_validation.csv").is_file(),
    }


def _num_range(
    series: pd.Series,
    lo: float | None,
    hi: float | None,
) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    mask = s.notna()
    if lo is not None:
        mask &= s >= lo
    if hi is not None:
        mask &= s <= hi
    return mask


def apply_global_filters(
    df: pd.DataFrame,
    *,
    family: str | None = None,
    scenario_base: str | None = None,
    traffic_profile: str | None = None,
    map_dataset: str | None = None,
    text: str = "",
    delivery_min: float | None = None,
    delivery_max: float | None = None,
    drop_min: float | None = None,
    drop_max: float | None = None,
    coverage_min: float | None = None,
    coverage_max: float | None = None,
    bench_statuses: list[str] | None = None,
    policy_statuses: list[str] | None = None,
) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df
    if family and family != "(todas)" and "family" in out.columns:
        out = out[out["family"].astype(str) == family]
    if scenario_base and scenario_base != "(todos)" and "scenario_base" in out.columns:
        out = out[out["scenario_base"].astype(str) == scenario_base]
    if traffic_profile and traffic_profile != "(todos)" and "traffic_profile_id" in out.columns:
        out = out[out["traffic_profile_id"].astype(str) == traffic_profile]
    if map_dataset and map_dataset != "(todos)":
        col = "map_dataset" if "map_dataset" in out.columns else None
        if col:
            out = out[out[col].astype(str) == map_dataset]
    if text.strip() and "scenario" in out.columns:
        t = text.strip().lower()
        out = out[out["scenario"].astype(str).str.lower().str.contains(t, na=False)]
    if "delivery_ratio" in out.columns and (delivery_min is not None or delivery_max is not None):
        out = out[_num_range(out["delivery_ratio"], delivery_min, delivery_max)]
    if "drop_ratio" in out.columns and (drop_min is not None or drop_max is not None):
        out = out[_num_range(out["drop_ratio"], drop_min, drop_max)]
    if "final_coverage_pct" in out.columns and (coverage_min is not None or coverage_max is not None):
        out = out[_num_range(out["final_coverage_pct"], coverage_min, coverage_max)]
    if bench_statuses and "bench_validation_status" in out.columns:
        out = out[out["bench_validation_status"].astype(str).isin(bench_statuses)]
    if policy_statuses and "policy_status" in out.columns:
        out = out[out["policy_status"].astype(str).isin(policy_statuses)]
    return out


def _slider_range(
    label: str,
    col: pd.Series,
    default_lo: float,
    default_hi: float,
    *,
    max_hi: float | None = None,
) -> tuple[float | None, float | None]:
    s = pd.to_numeric(col, errors="coerce").dropna()
    if s.empty:
        return None, None
    lo_data = float(s.min())
    hi_data = float(s.max())
    hi_cap = max_hi if max_hi is not None else hi_data
    if hi_cap < hi_data:
        hi_data = hi_cap
    if lo_data >= hi_data:
        return lo_data, hi_data
    vals = st.sidebar.slider(
        label,
        min_value=float(lo_data),
        max_value=float(hi_data),
        value=(float(default_lo if default_lo >= lo_data else lo_data), float(default_hi if default_hi <= hi_data else hi_data)),
    )
    return vals[0], vals[1]


def render_sidebar_filters(master: pd.DataFrame) -> pd.DataFrame:
    """Global filters in sidebar; returns filtered master table."""
    st.sidebar.header("Filtros (corpus_v2)")
    mtime = file_mtime(str(DATA_DIR / "output_metrics.csv"))
    if mtime:
        from datetime import datetime

        st.sidebar.caption(
            f"Métricas: {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')}"
        )
    else:
        st.sidebar.warning("Sin `output_metrics.csv` — ejecuta fase output_metrics.")

    families = ["(todas)"]
    bases = ["(todos)"]
    tps = ["(todos)"]
    maps = ["(todos)"]
    if not master.empty:
        if "family" in master.columns:
            families += sorted(master["family"].dropna().astype(str).unique())
        if "scenario_base" in master.columns:
            bases += sorted(master["scenario_base"].dropna().astype(str).unique())
        if "traffic_profile_id" in master.columns:
            tps += sorted(master["traffic_profile_id"].dropna().astype(str).unique())
        if "map_dataset" in master.columns:
            maps += sorted(master["map_dataset"].dropna().astype(str).unique())

    family = st.sidebar.selectbox("Familia", families)
    scenario_base = st.sidebar.selectbox("Escenario base", bases)
    traffic_profile = st.sidebar.selectbox("Perfil TP", tps)
    map_dataset = st.sidebar.selectbox("Mapa", maps)
    text = st.sidebar.text_input("Buscar escenario", placeholder="U1_, Manhattan, TP07")

    delivery_min = delivery_max = drop_min = drop_max = cov_min = cov_max = None
    bench_statuses: list[str] | None = None
    policy_statuses: list[str] | None = None

    with st.sidebar.expander("Rangos numéricos", expanded=True):
        if "delivery_ratio" in master.columns:
            delivery_min, delivery_max = _slider_range(
                "Delivery ratio",
                master["delivery_ratio"],
                0.0,
                1.0,
            )
        if "drop_ratio" in master.columns:
            drop_min, drop_max = _slider_range(
                "Drop ratio",
                master["drop_ratio"],
                0.0,
                500.0,
                max_hi=500.0,
            )
        if "final_coverage_pct" in master.columns:
            cov_min, cov_max = _slider_range(
                "Cobertura espacial %",
                master["final_coverage_pct"],
                0.0,
                100.0,
            )

    with st.sidebar.expander("Estado validación", expanded=False):
        if "bench_validation_status" in master.columns:
            opts = sorted(master["bench_validation_status"].dropna().astype(str).unique())
            bench_statuses = st.multiselect(
                "Benchmark validation",
                opts,
                default=opts,
            )
        if "policy_status" in master.columns:
            popts = sorted(master["policy_status"].dropna().astype(str).unique())
            policy_statuses = st.multiselect(
                "Ventana mensajes (policy)",
                popts,
                default=popts,
            )

    filtered = apply_global_filters(
        master,
        family=family,
        scenario_base=scenario_base,
        traffic_profile=traffic_profile,
        map_dataset=map_dataset,
        text=text,
        delivery_min=delivery_min,
        delivery_max=delivery_max,
        drop_min=drop_min,
        drop_max=drop_max,
        coverage_min=cov_min,
        coverage_max=cov_max,
        bench_statuses=bench_statuses if bench_statuses else None,
        policy_statuses=policy_statuses if policy_statuses else None,
    )
    st.sidebar.caption(f"Escenarios visibles: **{len(filtered)}** / {len(master)}")
    return filtered


def list_markdown_reports() -> list[tuple[str, Path]]:
    pinned: list[tuple[str, Path]] = [
        ("Resultados actuales", RESULTADOS_ACTUALES),
        ("Validación TP", TP_VALIDATION_REPORT),
        ("KPIs por Traffic Profile", TRAFFIC_PROFILE_KPI_ANALYSIS),
        ("Ventana análisis mensajes", MESSAGE_ANALYSIS_WINDOW_POLICY),
        ("Validación benchmark", CORPUS_V2_BENCHMARK_VALIDATION),
        ("Figuras paper readiness", PAPER_FIGURES_TABLES_READINESS),
        ("Tiempos útiles simulación", USEFUL_SIMULATION_TIME_REPORT),
        ("Diagnóstico escenarios", SCENARIO_DIAGNOSIS),
        ("Revisión corpus v2", CORPUS_V2_REVISION_CHANGELOG),
        ("Ocupación espacial (puntero)", SPATIAL_OCCUPANCY_ANALYSIS_SUMMARY),
        ("Dashboard readiness", DASHBOARD_READINESS_REPORT),
    ]
    out: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for label, p in pinned:
        if p.is_file() and p not in seen:
            out.append((label, p))
            seen.add(p)
    for p in sorted(REPORTS_ANALYSIS_DIR.rglob("*.md")):
        if p in seen or p.name in ("README.md",):
            continue
        if p.parent == REPORTS_ANALYSIS_DIR and p.name in (
            "RESULTADOS_ACTUALES.md",
            "paper_freeze_checklist.md",
        ):
            continue
        rel = p.relative_to(REPORTS_ANALYSIS_DIR)
        label = f"{rel.parent}/" if rel.parent != Path(".") else ""
        label = f"{label}{p.stem}".strip("/")
        out.append((label, p))
        seen.add(p)
    fig_index = ANALYSIS_DIR / "figures" / "paper" / "FIGURES_AND_TABLES_INDEX.md"
    if fig_index.is_file():
        out.append(("Índice figuras paper", fig_index))
    return out


def write_dashboard_readiness_report(path: Path | None = None) -> Path:
    """Generate dashboard_readiness_report.md from current pipeline state."""
    path = path or DASHBOARD_READINESS_REPORT
    status = pipeline_status()
    master = build_master_table()
    n = len(master)

    pages_info = [
        ("Resumen corpus", "manifest, pipeline_status", "Corpus design, data availability"),
        ("Explorador", "master table (all joins)", "Scenario tables, export CSV"),
        ("KPIs benchmark", "traffic_profile_kpi_summary, output_metrics", "TP comparison, paper KPIs"),
        ("Perfiles TP", "tp_validation_*, message_creation_time_summary", "TP validation"),
        ("Ventana mensajes", "message_analysis_window_policy", "Message window methodology"),
        ("Tiempo útil", "useful_simulation_time_metrics", "Simulation time vs mobility"),
        ("Espacial", "spatial_occupancy_metrics, heatmaps/", "Spatial coverage, WDM"),
        ("Diagnóstico", "scenario_diagnosis, corpus_v2_benchmark_validation", "Problem scenarios"),
        ("Protocolos", "placeholder", "Future routing comparison"),
        ("Detalle escenario", "master row, raw reports/", "Deep dive per scenario"),
        ("Figuras / Pipeline / Reportes", "figures/, reports/", "Auxiliary exploration"),
    ]

    lines = [
        "# Dashboard readiness report (corpus_v2)",
        "",
        f"Generated: automated from `build_paper_figures_tables_index.py` / dashboard loaders.",
        "",
        "## Executive summary",
        "",
        f"- **Corpus:** corpus_v2 — **{n}** simulations in master table.",
        "- **Launch:** `streamlit run scenarios/analysis/dashboard.py`",
        "- **Reference:** [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)",
        "",
        "## Pages and data sources",
        "",
        "| Page | Primary data | Paper utility |",
        "|------|--------------|---------------|",
    ]
    for page, data, utility in pages_info:
        lines.append(f"| {page} | {data} | {utility} |")

    lines.extend(["", "## Pipeline file status", "", "| Artifact | Available |", "|----------|-----------|"])
    for k, ok in status.items():
        lines.append(f"| `{k}` | {'yes' if ok else '**no**'} |")

    lines.extend(
        [
            "",
            "## Issues found",
            "",
        ]
    )
    if "has_metrics" in master.columns:
        missing = int((~master["has_metrics"]).sum())
        lines.append(f"- **{missing}** scenarios without `output_metrics` (e.g. S1 TP03/TP11 re-simulate).")
    if "bench_validation_status" in master.columns:
        err = int((master["bench_validation_status"] == "error_probable").sum())
        lines.append(f"- **{err}** scenarios with `error_probable` benchmark validation.")
    lines.append("- `protocol_benchmark_kpi_definitions.csv` not present — protocols page uses placeholder.")
    lines.append("- Feature matrices (720×720) intentionally excluded from UI.")

    lines.extend(
        [
            "",
            "## Pending improvements",
            "",
            "- Multi-protocol simulation and comparison charts.",
            "- Optional PCA on features in-dashboard (load on demand).",
            "- Cache clear button when CSVs regenerated.",
            "",
            "## Paper section mapping",
            "",
            "| Paper section | Dashboard page |",
            "|---------------|----------------|",
            "| Methods — benchmark design | Resumen corpus |",
            "| Methods — traffic profiles | Perfiles TP, KPIs benchmark |",
            "| Methods — message window | Ventana mensajes |",
            "| Results — diversity | Pipeline clásico / Figuras (external) |",
            "| Results — delivery by TP | KPIs benchmark, Explorador |",
            "| Results — spatial | Espacial |",
            "| Discussion — limitations | Diagnóstico, Protocolos |",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
