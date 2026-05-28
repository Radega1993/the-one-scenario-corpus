#!/usr/bin/env python3
"""
Analyze Traffic Profile KPIs for corpus_v1 (720 simulations, 60 bases × 12 TPs).

Outputs:
  data/traffic_profile_stats.csv       — per-TP distributional stats + pathology counts
  data/traffic_profile_kpi_summary.csv — per-TP KPI recommendations + validation
  reports/traffic_profile_kpi_analysis.md — human-readable benchmark report
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import CORPUS_V1_DIR, DATA_DIR, REPORTS_ANALYSIS_DIR  # noqa: E402
from lib.report_paths import TRAFFIC_PROFILE_KPI_ANALYSIS  # noqa: E402
from lib.traffic_profile_generator import PROFILE_ORDER  # noqa: E402

DEFAULT_CORPUS = CORPUS_V1_DIR
DEFAULT_MANIFEST = DEFAULT_CORPUS / "manifest.csv"
DEFAULT_DATA = DATA_DIR
DEFAULT_REPORTS = REPORTS_ANALYSIS_DIR

PROFILE_IDS = [tp for tp, _ in PROFILE_ORDER]
PROFILE_NAMES = dict(PROFILE_ORDER)

DROP_EXTREME_MIN = 50.0
SPATIAL_LOW_PCT = 12.0

CORE_METRICS = [
    "delivery_ratio",
    "latency_mean",
    "overhead_ratio",
    "drop_ratio",
    "n_created",
    "t_median_frac",
    "pct_last_10pct_sim",
    "contact_time_per_min",
    "total_encounters",
    "ratio_contact_nodes",
    "popularity_top10_ratio",
    "final_coverage_pct",
    "useful_time_ratio",
]

STAT_SUFFIXES = ("mean", "median", "std", "iqr", "min", "max")

TP_INTENT: dict[str, str] = {
    "TP01": "Reference traffic: moderate rate, mixed message sizes, full simulation window.",
    "TP02": "Low load: sparse message generation (long intervals, smaller sizes).",
    "TP03": "Many small messages: high generation rate with small payloads.",
    "TP04": "Few large messages: stress buffer, transmission, and drop under large payloads.",
    "TP05": "Critical TTL: short message lifetime (5 min default) with moderate traffic.",
    "TP06": "One-to-many: single sender to many destinations (directional fan-out).",
    "TP07": "Burst window: concentrated traffic in 20–28% of simulation time.",
    "TP08": "Hub target: traffic concentrated toward a hub/sink node.",
    "TP09": "Bimodal mix: two event generators with small + very large messages.",
    "TP10": "Storm/saturation: very high generation rate with medium-large payloads.",
    "TP11": "Many-to-one: many senders to a single sink (directional fan-in).",
    "TP12": "Group-to-group: cross-community traffic between partition groups.",
}

TP_KPI_SPEC: dict[str, dict[str, str]] = {
    "TP01": {
        "primary_kpi": "delivery_ratio",
        "secondary_kpi": "latency_mean",
        "cost_kpi": "overhead_ratio",
        "stress_kpi": "drop_ratio",
    },
    "TP02": {
        "primary_kpi": "n_created",
        "secondary_kpi": "delivery_ratio",
        "cost_kpi": "overhead_ratio",
        "stress_kpi": "drop_ratio",
    },
    "TP03": {
        "primary_kpi": "overhead_ratio",
        "secondary_kpi": "delivery_ratio",
        "cost_kpi": "total_encounters",
        "stress_kpi": "drop_ratio",
    },
    "TP04": {
        "primary_kpi": "drop_ratio",
        "secondary_kpi": "delivery_ratio",
        "cost_kpi": "overhead_ratio",
        "stress_kpi": "latency_mean",
    },
    "TP05": {
        "primary_kpi": "delivery_ratio",
        "secondary_kpi": "latency_mean",
        "cost_kpi": "overhead_ratio",
        "stress_kpi": "drop_ratio",
    },
    "TP06": {
        "primary_kpi": "delivery_ratio",
        "secondary_kpi": "latency_mean",
        "cost_kpi": "overhead_ratio",
        "stress_kpi": "popularity_top10_ratio",
    },
    "TP07": {
        "primary_kpi": "delivery_ratio",
        "secondary_kpi": "t_median_frac",
        "cost_kpi": "overhead_ratio",
        "stress_kpi": "latency_mean",
    },
    "TP08": {
        "primary_kpi": "popularity_top10_ratio",
        "secondary_kpi": "delivery_ratio",
        "cost_kpi": "overhead_ratio",
        "stress_kpi": "drop_ratio",
    },
    "TP09": {
        "primary_kpi": "drop_ratio",
        "secondary_kpi": "delivery_ratio",
        "cost_kpi": "overhead_ratio",
        "stress_kpi": "latency_mean",
    },
    "TP10": {
        "primary_kpi": "delivery_ratio",
        "secondary_kpi": "n_created",
        "cost_kpi": "overhead_ratio",
        "stress_kpi": "drop_ratio",
    },
    "TP11": {
        "primary_kpi": "delivery_ratio",
        "secondary_kpi": "overhead_ratio",
        "cost_kpi": "latency_mean",
        "stress_kpi": "drop_ratio",
    },
    "TP12": {
        "primary_kpi": "delivery_ratio",
        "secondary_kpi": "overhead_ratio",
        "cost_kpi": "latency_mean",
        "stress_kpi": "drop_ratio",
    },
}

STRESS_TPS = frozenset({"TP04", "TP05", "TP09", "TP10"})
DIRECTIONAL_TPS = frozenset({"TP06", "TP08", "TP11", "TP12"})
FAVORABLE_TPS = frozenset({"TP02", "TP07"})


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _is_nan(x: Any) -> bool:
    return x is None or (isinstance(x, float) and np.isnan(x))


def _safe_rel_delta(delta: float, base: float) -> float:
    if _is_nan(delta) or _is_nan(base):
        return float("nan")
    if abs(base) < 1e-12:
        return float("nan") if abs(delta) < 1e-12 else float("inf") * np.sign(delta)
    return delta / base


def _series_stats(s: pd.Series) -> dict[str, float]:
    s = s.dropna()
    if s.empty:
        return {k: float("nan") for k in STAT_SUFFIXES}
    q25 = float(s.quantile(0.25))
    q75 = float(s.quantile(0.75))
    return {
        "mean": float(s.mean()),
        "median": float(s.median()),
        "std": float(s.std(ddof=0)),
        "iqr": q75 - q25,
        "min": float(s.min()),
        "max": float(s.max()),
    }


def load_and_merge(manifest_path: Path, data_dir: Path) -> pd.DataFrame:
    m = pd.read_csv(manifest_path)

    def _read(name: str) -> pd.DataFrame:
        p = data_dir / name
        if not p.is_file():
            raise FileNotFoundError(p)
        return pd.read_csv(p)

    out = _read("output_metrics.csv").rename(columns={"scenario": "scenario_name"})
    sp = _read("spatial_occupancy_metrics.csv").rename(columns={"scenario": "scenario_name"})
    ind = _read("indirect_features_diego.csv").rename(columns={"scenario": "scenario_name"})
    msg = _read("message_creation_time_summary.csv").rename(columns={"scenario": "scenario_name"})
    use = _read("useful_simulation_time_metrics.csv").rename(columns={"scenario": "scenario_name"})
    settings = _read("tp_validation_settings.csv")
    windows = _read("traffic_profile_windows.csv")

    bench_path = data_dir / "corpus_benchmark_validation.csv"
    bench = pd.read_csv(bench_path) if bench_path.is_file() else pd.DataFrame()

    df = m.copy()
    df = df.merge(
        out[["scenario_name", "delivery_ratio", "latency_mean", "overhead_ratio", "drop_ratio"]],
        on="scenario_name",
        how="left",
    )
    df = df.merge(
        ind[
            [
                "scenario_name",
                "contact_time_mean_s",
                "contact_time_per_min",
                "total_encounters",
                "ratio_contact_nodes",
                "popularity_top10_ratio",
            ]
        ],
        on="scenario_name",
        how="left",
    )
    df = df.merge(sp[["scenario_name", "final_coverage_pct"]], on="scenario_name", how="left")
    df = df.merge(
        msg[
            [
                "scenario_name",
                "n_created",
                "t_median",
                "Scenario.endTime",
                "pct_last_10pct_sim",
            ]
        ],
        on="scenario_name",
        how="left",
        suffixes=("", "_msg"),
    )
    df = df.merge(
        use[["scenario_name", "useful_time_ratio", "classification"]],
        on="scenario_name",
        how="left",
    )
    df = df.merge(
        settings[["scenario_name", "status"]].rename(columns={"status": "settings_status"}),
        on="scenario_name",
        how="left",
    )
    df = df.merge(
        windows[["scenario_name", "traffic_gen_fraction", "traffic_gen_note"]],
        on="scenario_name",
        how="left",
    )
    if not bench.empty:
        df = df.merge(
            bench[["scenario_name", "validation_status", "reason"]].rename(
                columns={
                    "validation_status": "bench_status",
                    "reason": "bench_reason",
                }
            ),
            on="scenario_name",
            how="left",
        )

    end_col = "Scenario.endTime_msg" if "Scenario.endTime_msg" in df.columns else "Scenario.endTime"
    if end_col not in df.columns and "Scenario.endTime" in df.columns:
        end_col = "Scenario.endTime"
    df["t_median_frac"] = np.where(
        (df[end_col].notna()) & (df["t_median"].notna()) & (df[end_col] > 0),
        df["t_median"] / df[end_col],
        np.nan,
    )

    df["_missing_output"] = df["delivery_ratio"].isna()
    df["_latency_valid"] = df["latency_mean"].notna() & (df["latency_mean"] > 0)
    df["_delivery_zero"] = df["delivery_ratio"].isna() | (df["delivery_ratio"] == 0)
    df["_latency_empty"] = df["delivery_ratio"].notna() & (df["delivery_ratio"] > 0) & ~df["_latency_valid"]
    df["_drop_extreme"] = df["drop_ratio"].notna() & (df["drop_ratio"] > DROP_EXTREME_MIN)
    df["_zero_contacts"] = df["total_encounters"].isna() | (df["total_encounters"] == 0)
    df["_low_spatial"] = df["final_coverage_pct"].notna() & (df["final_coverage_pct"] < SPATIAL_LOW_PCT)

    return df


def compute_tp_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for tp_id in PROFILE_IDS:
        sub = df[df["traffic_profile_id"] == tp_id]
        row: dict[str, Any] = {
            "tp_id": tp_id,
            "tp_name": PROFILE_NAMES[tp_id],
            "n_scenarios": len(sub),
            "n_missing_output": int(sub["_missing_output"].sum()),
            "n_delivery_zero": int(sub["_delivery_zero"].sum()),
            "n_latency_empty": int(sub["_latency_empty"].sum()),
            "n_drop_extreme": int(sub["_drop_extreme"].sum()),
            "n_zero_contacts": int(sub["_zero_contacts"].sum()),
            "n_low_spatial": int(sub["_low_spatial"].sum()),
            "n_latency_valid": int(sub["_latency_valid"].sum()),
            "pct_latency_valid": round(100.0 * sub["_latency_valid"].mean(), 2),
        }
        for metric in CORE_METRICS:
            if metric == "latency_mean":
                vals = sub.loc[sub["_latency_valid"], metric]
            else:
                vals = sub[metric]
            stats = _series_stats(vals)
            for suffix, val in stats.items():
                row[f"{metric}_{suffix}"] = round(val, 6) if not _is_nan(val) else val
        rows.append(row)
    return pd.DataFrame(rows)


def compute_paired_deltas(df: pd.DataFrame) -> pd.DataFrame:
    """Paired comparison vs TP01 per scenario_base."""
    compare_metrics = [
        "delivery_ratio",
        "latency_mean",
        "overhead_ratio",
        "drop_ratio",
        "n_created",
        "t_median_frac",
        "popularity_top10_ratio",
    ]
    tp01 = df[df["traffic_profile_id"] == "TP01"].set_index("scenario_base")
    rows: list[dict[str, Any]] = []
    for tp_id in PROFILE_IDS:
        sub = df[df["traffic_profile_id"] == tp_id].set_index("scenario_base")
        row: dict[str, Any] = {"tp_id": tp_id}
        for metric in compare_metrics:
            deltas: list[float] = []
            rel_deltas: list[float] = []
            for base in tp01.index:
                if base not in sub.index:
                    continue
                v_tp = sub.at[base, metric]
                v_baseline = tp01.at[base, metric]
                if metric == "latency_mean":
                    if not (sub.at[base, "_latency_valid"] and tp01.at[base, "_latency_valid"]):
                        continue
                if _is_nan(v_tp) or _is_nan(v_baseline):
                    continue
                d = float(v_tp) - float(v_baseline)
                deltas.append(d)
                rd = _safe_rel_delta(d, float(v_baseline))
                if not _is_nan(rd) and np.isfinite(rd):
                    rel_deltas.append(rd)
            row[f"{metric}_delta_mean"] = round(float(np.mean(deltas)), 6) if deltas else float("nan")
            row[f"{metric}_delta_median"] = round(float(np.median(deltas)), 6) if deltas else float("nan")
            row[f"{metric}_rel_delta_median"] = (
                round(float(np.median(rel_deltas)), 6) if rel_deltas else float("nan")
            )
        rows.append(row)
    return pd.DataFrame(rows)


def compute_rankings(stats: pd.DataFrame) -> dict[str, list[str]]:
    """Rank TPs by median of core metrics (higher delivery better; lower others better)."""
    rankings: dict[str, list[str]] = {}
    rankings["delivery_ratio"] = stats.sort_values("delivery_ratio_median", ascending=False)["tp_id"].tolist()
    rankings["overhead_ratio"] = stats.sort_values("overhead_ratio_median", ascending=True)["tp_id"].tolist()
    rankings["drop_ratio"] = stats.sort_values("drop_ratio_median", ascending=True)["tp_id"].tolist()
    rankings["latency_mean"] = stats.sort_values("latency_mean_median", ascending=True)["tp_id"].tolist()
    return rankings


def _stat(stats: pd.DataFrame, tp_id: str, col: str) -> float:
    row = stats.loc[stats["tp_id"] == tp_id, col]
    if row.empty:
        return float("nan")
    return float(row.iloc[0])


def validate_tp_intent(
    tp_id: str,
    stats: pd.DataFrame,
    deltas: pd.DataFrame,
    df: pd.DataFrame,
) -> tuple[str, list[str]]:
    """Return (validation_status, list of check notes)."""
    notes: list[str] = []
    tp01_stats = stats[stats["tp_id"] == "TP01"].iloc[0]
    tp_stats = stats[stats["tp_id"] == tp_id].iloc[0]
    tp_delta = deltas[deltas["tp_id"] == tp_id].iloc[0] if tp_id in deltas["tp_id"].values else None

    n_missing = int(tp_stats["n_missing_output"])
    n_zero = int(tp_stats["n_delivery_zero"])
    n_total = int(tp_stats["n_scenarios"])
    error_probable = 0
    if "bench_status" in df.columns:
        sub = df[(df["traffic_profile_id"] == tp_id) & (df["bench_status"] == "error_probable")]
        error_probable = len(sub)

    if error_probable > 0 or n_missing > n_total * 0.1:
        return "blocked", [f"{error_probable} error_probable sim(s); {n_missing} missing output"]

    passed = 0
    total_checks = 0

    def check(ok: bool, msg: str) -> None:
        nonlocal passed, total_checks
        total_checks += 1
        if ok:
            passed += 1
            notes.append(f"OK: {msg}")
        else:
            notes.append(f"FAIL: {msg}")

    if tp_id == "TP01":
        return "validated", ["Reference profile"]

    if tp_id == "TP02":
        ratio = _stat(stats, "TP02", "n_created_median") / max(_stat(stats, "TP01", "n_created_median"), 1)
        check(ratio <= 0.35, f"n_created median ratio vs TP01 = {ratio:.2f} (target ≤0.35)")
        oh_ratio = _stat(stats, "TP02", "overhead_ratio_median") / max(_stat(stats, "TP01", "overhead_ratio_median"), 1)
        check(oh_ratio <= 1.10, f"overhead median ratio vs TP01 = {oh_ratio:.2f} (target ≤1.10)")

    elif tp_id == "TP03":
        ratio = _stat(stats, "TP03", "n_created_median") / max(_stat(stats, "TP01", "n_created_median"), 1)
        check(ratio >= 3.0, f"n_created median ratio vs TP01 = {ratio:.2f} (target ≥3.0)")
        drop_diff = _stat(stats, "TP03", "drop_ratio_mean") - _stat(stats, "TP01", "drop_ratio_mean")
        check(drop_diff <= 0.05, f"drop mean diff vs TP01 = {drop_diff:.3f} (target ≤0.05)")

    elif tp_id == "TP04":
        check(_stat(stats, "TP04", "drop_ratio_mean") >= 50.0, f"drop mean {_stat(stats, 'TP04', 'drop_ratio_mean'):.1f} (target ≥50)")
        check(int(tp_stats["n_drop_extreme"]) >= 10, f"n_drop_extreme={int(tp_stats['n_drop_extreme'])} (target ≥10)")
        oh_ratio = _stat(stats, "TP04", "overhead_ratio_median") / max(_stat(stats, "TP01", "overhead_ratio_median"), 1)
        check(oh_ratio >= 2.0, f"overhead median ratio vs TP01 = {oh_ratio:.2f} (target ≥2.0)")

    elif tp_id == "TP05":
        check(_stat(stats, "TP05", "delivery_ratio_median") <= 0.05, "delivery median ≤0.05")
        check(_stat(stats, "TP05", "latency_mean_median") <= 500.0, "latency median ≤500 s (delivered)")

    elif tp_id == "TP06":
        settings_ok = df[df["traffic_profile_id"] == "TP06"]["settings_status"].eq("ok").all()
        check(settings_ok, "settings validation ok for all TP06 scenarios")
        if tp_delta is not None:
            check(
                _stat(stats, "TP06", "delivery_ratio_median") >= _stat(stats, "TP01", "delivery_ratio_median") * 0.85,
                "delivery median within 85% of TP01",
            )

    elif tp_id == "TP07":
        frac = _stat(stats, "TP07", "t_median_frac_median")
        check(0.18 <= frac <= 0.30, f"t_median/endTime median = {frac:.3f} (target 0.18–0.30)")
        pct_diff = _stat(stats, "TP07", "pct_last_10pct_sim_median") - _stat(stats, "TP01", "pct_last_10pct_sim_median")
        check(pct_diff < -3.0, f"pct_last_10pct diff vs TP01 = {pct_diff:.1f}pp (target <−3pp)")

    elif tp_id == "TP08":
        pop_diff = _stat(stats, "TP08", "popularity_top10_ratio_median") - _stat(stats, "TP01", "popularity_top10_ratio_median")
        check(pop_diff >= -0.02, f"popularity_top10 diff vs TP01 = {pop_diff:.3f}")
        oh_ratio = _stat(stats, "TP08", "overhead_ratio_median") / max(_stat(stats, "TP01", "overhead_ratio_median"), 1)
        check(oh_ratio >= 0.9, f"overhead median ratio vs TP01 = {oh_ratio:.2f}")

    elif tp_id == "TP09":
        check(_stat(stats, "TP09", "drop_ratio_mean") >= 30.0, f"drop mean {_stat(stats, 'TP09', 'drop_ratio_mean'):.1f} (target ≥30)")
        events2 = df[df["traffic_profile_id"] == "TP09"]["Events.nrof"].astype(str).eq("2").all()
        check(events2, "Events.nrof=2 in all TP09 settings")

    elif tp_id == "TP10":
        ratio = _stat(stats, "TP10", "n_created_median") / max(_stat(stats, "TP01", "n_created_median"), 1)
        check(ratio >= 2.0, f"n_created median ratio vs TP01 = {ratio:.2f} (target ≥2.0)")
        check(_stat(stats, "TP10", "delivery_ratio_median") <= 0.15, "delivery median ≤0.15")

    elif tp_id == "TP11":
        settings_ok = df[df["traffic_profile_id"] == "TP11"]["settings_status"].eq("ok").all()
        check(settings_ok, "settings validation ok for all TP11 scenarios")
        oh_ratio = _stat(stats, "TP11", "overhead_ratio_median") / max(_stat(stats, "TP01", "overhead_ratio_median"), 1)
        check(oh_ratio >= 0.95, f"overhead median ratio vs TP01 = {oh_ratio:.2f}")

    elif tp_id == "TP12":
        settings_ok = df[df["traffic_profile_id"] == "TP12"]["settings_status"].eq("ok").all()
        check(settings_ok, "settings validation ok for all TP12 scenarios")
        oh_iqr = _stat(stats, "TP12", "overhead_ratio_iqr")
        oh_iqr01 = _stat(stats, "TP01", "overhead_ratio_iqr")
        check(oh_iqr >= oh_iqr01 * 0.8, f"overhead IQR TP12={oh_iqr:.1f} vs TP01={oh_iqr01:.1f}")

    if total_checks == 0:
        return "validated", notes

    ratio_pass = passed / total_checks
    if ratio_pass >= 1.0:
        status = "validated"
    elif ratio_pass >= 0.5:
        status = "partial"
    else:
        status = "needs_adjustment"

    if n_zero > 15 and tp_id not in STRESS_TPS:
        status = "needs_adjustment"
        notes.append(f"WARN: {n_zero} scenarios with zero delivery (may include disconnected bases)")

    return status, notes


def _fmt_val(v: float, metric: str) -> str:
    if _is_nan(v):
        return "n/a"
    if metric in ("delivery_ratio", "drop_ratio", "t_median_frac", "popularity_top10_ratio", "useful_time_ratio"):
        if metric == "t_median_frac":
            return f"{v:.3f}"
        return f"{v:.3f}" if metric == "delivery_ratio" else f"{v:.2f}"
    if metric == "n_created":
        return f"{v:.0f}"
    return f"{v:.1f}"


def build_observed_behavior(tp_id: str, stats: pd.DataFrame, deltas: pd.DataFrame) -> str:
    s = stats[stats["tp_id"] == tp_id].iloc[0]
    d = deltas[deltas["tp_id"] == tp_id].iloc[0] if tp_id in deltas["tp_id"].values else None
    parts = [
        f"delivery median {_fmt_val(s['delivery_ratio_median'], 'delivery_ratio')}",
        f"overhead median {_fmt_val(s['overhead_ratio_median'], 'overhead_ratio')}",
        f"drop median {_fmt_val(s['drop_ratio_median'], 'drop_ratio')}",
    ]
    if tp_id != "TP01" and d is not None:
        rel = d.get("delivery_ratio_rel_delta_median", float("nan"))
        if not _is_nan(rel) and np.isfinite(rel):
            parts.append(f"delivery vs TP01: {rel:+.1%} paired median")
    if tp_id in ("TP02", "TP03", "TP10"):
        parts.append(f"n_created median {_fmt_val(s['n_created_median'], 'n_created')}")
    if tp_id == "TP07":
        parts.append(f"burst t_median_frac {_fmt_val(s['t_median_frac_median'], 't_median_frac')}")
    if tp_id == "TP05":
        parts.append(f"latency median {_fmt_val(s['latency_mean_median'], 'latency_mean')} s")
    return "; ".join(parts) + "."


def build_paper_interpretation(tp_id: str, status: str) -> str:
    kpi = TP_KPI_SPEC[tp_id]
    primary = kpi["primary_kpi"]
    if tp_id == "TP01":
        return (
            "Use as baseline reference: compare protocol delivery and overhead against TP01 "
            "before interpreting stress or directional profiles."
        )
    if tp_id in STRESS_TPS:
        return (
            f"Stress tier: prioritize {primary} and {kpi['stress_kpi']} to expose buffer/TTL/saturation limits; "
            "exclude zero-delivery disconnected bases from latency rankings."
        )
    if tp_id in DIRECTIONAL_TPS:
        return (
            f"Directional tier: report {primary} with {kpi['secondary_kpi']} to capture routing asymmetry "
            "(fan-out, hub, fan-in, or cross-group)."
        )
    if tp_id == "TP02":
        return (
            "Load control: compare protocols on n_created-normalized overhead; delivery may exceed baseline "
            "due to reduced congestion."
        )
    if tp_id == "TP07":
        return (
            "Temporal burst: compare delivery under synchronized load; latency may rise due to queueing "
            "during the burst window."
        )
    if status == "needs_adjustment":
        return f"Review before freeze: validation incomplete; still report {primary} if included in benchmark."
    return f"Report {primary} as primary outcome; use {kpi['cost_kpi']} for resource cost comparison."


def build_kpi_summary(stats: pd.DataFrame, deltas: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for tp_id, tp_name in PROFILE_ORDER:
        status, _notes = validate_tp_intent(tp_id, stats, deltas, df)
        kpi = TP_KPI_SPEC[tp_id]
        rows.append(
            {
                "tp_id": tp_id,
                "tp_name": tp_name,
                "experimental_intent": TP_INTENT[tp_id],
                "primary_kpi": kpi["primary_kpi"],
                "secondary_kpi": kpi["secondary_kpi"],
                "cost_kpi": kpi["cost_kpi"],
                "stress_kpi": kpi["stress_kpi"],
                "expected_behavior": TP_INTENT[tp_id],
                "observed_behavior": build_observed_behavior(tp_id, stats, deltas),
                "validation_status": status,
                "paper_interpretation": build_paper_interpretation(tp_id, status),
            }
        )
    return pd.DataFrame(rows)


def _rank_str(rankings: dict[str, list[str]], tp_id: str) -> str:
    parts = []
    for metric, order in rankings.items():
        if tp_id in order:
            parts.append(f"{metric}=#{order.index(tp_id) + 1}")
    return ", ".join(parts)


def write_report(
    path: Path,
    df: pd.DataFrame,
    stats: pd.DataFrame,
    deltas: pd.DataFrame,
    summary: pd.DataFrame,
    rankings: dict[str, list[str]],
) -> None:
    n_total = len(df)
    n_missing = int(df["_missing_output"].sum())
    tp01 = stats[stats["tp_id"] == "TP01"].iloc[0]

    lines: list[str] = [
        "# Traffic Profile KPI Analysis (corpus_v1)",
        "",
        f"Generated: {_utc()}",
        "",
        "## Executive summary",
        "",
        f"- **Corpus:** corpus_v1 — {n_total} simulations (60 base scenarios × 12 Traffic Profiles).",
        f"- **Missing output metrics:** {n_missing} scenario(s) "
        f"({', '.join(df.loc[df['_missing_output'], 'scenario_name'].tolist()) or 'none'}).",
        "- **Protocol:** Epidemic (current corpus); KPIs defined for future multi-protocol comparison.",
        "- **Baseline:** TP01_Baseline — delivery median "
        f"{tp01['delivery_ratio_median']:.3f}, overhead median {tp01['overhead_ratio_median']:.1f}.",
        "",
        "## Per-TP distributional stats",
        "",
        "| TP | delivery (med) | overhead (med) | drop (med) | latency (med) | n_created (med) | zero del | drop>50% |",
        "|----|----------------|----------------|------------|---------------|-----------------|----------|----------|",
    ]

    for _, s in stats.iterrows():
        lines.append(
            f"| {s['tp_id']} {s['tp_name']} | {s['delivery_ratio_median']:.3f} | "
            f"{s['overhead_ratio_median']:.1f} | {s['drop_ratio_median']:.1f} | "
            f"{s['latency_mean_median']:.0f} | {s['n_created_median']:.0f} | "
            f"{int(s['n_delivery_zero'])} | {int(s['n_drop_extreme'])} |"
        )

    lines.extend(
        [
            "",
            "Full statistics: [`traffic_profile_stats.csv`](../data/traffic_profile_stats.csv).",
            "",
            "## Global rankings (by median across 60 bases)",
            "",
            "### Delivery ratio (higher is better)",
            "",
        ]
    )
    for i, tp in enumerate(rankings["delivery_ratio"], 1):
        lines.append(f"{i}. **{tp}** {_stat(stats, tp, 'delivery_ratio_median'):.3f}")

    lines.extend(["", "### Overhead ratio (lower is better)", ""])
    for i, tp in enumerate(rankings["overhead_ratio"], 1):
        lines.append(f"{i}. **{tp}** {_stat(stats, tp, 'overhead_ratio_median'):.1f}")

    lines.extend(["", "### Drop ratio (lower is better)", ""])
    for i, tp in enumerate(rankings["drop_ratio"], 1):
        lines.append(f"{i}. **{tp}** {_stat(stats, tp, 'drop_ratio_median'):.1f}")

    lines.extend(["", "### Latency mean (lower is better, delivered only)", ""])
    for i, tp in enumerate(rankings["latency_mean"], 1):
        lines.append(f"{i}. **{tp}** {_stat(stats, tp, 'latency_mean_median'):.0f} s")

    lines.extend(
        [
            "",
            "## Comparison vs TP01 (paired median relative delta)",
            "",
            "| TP | Δ delivery | Δ overhead | Δ drop | Δ n_created | Δ t_median_frac |",
            "|----|------------|------------|--------|-------------|-----------------|",
        ]
    )
    for tp_id in PROFILE_IDS:
        if tp_id == "TP01":
            continue
        d = deltas[deltas["tp_id"] == tp_id].iloc[0]
        lines.append(
            f"| {tp_id} | {d['delivery_ratio_rel_delta_median']:+.1%} | "
            f"{d['overhead_ratio_rel_delta_median']:+.1%} | "
            f"{d['drop_ratio_rel_delta_median']:+.1%} | "
            f"{d['n_created_rel_delta_median']:+.1%} | "
            f"{d['t_median_frac_rel_delta_median']:+.1%} |"
        )

    lines.extend(
        [
            "",
            "## Profile classification",
            "",
            "### Favorable profiles",
            "",
            "- **TP07 BurstWindow:** highest delivery median; burst window confirmed (t_median_frac ≈ 0.24).",
            "- **TP02 LowLoad:** reduced n_created (~5× below TP01); delivery can exceed baseline (less congestion).",
            "",
            "### Stress profiles",
            "",
            "- **TP04 FewLarge:** drop mean ~80% (13 scenarios >50%); stresses buffer/transmission.",
            "- **TP05 CriticalTTL:** delivery median ~0.004; latency ~114 s when delivered.",
            "- **TP09 Bimodal:** high drop from large-message component.",
            "- **TP10 Storm:** delivery median ~0.10; high generation rate.",
            "",
            "### Directional profiles",
            "",
            "- **TP06 OneToMany**, **TP08 HubTarget**, **TP11 ManyToOne**, **TP12 GroupToGroup:** "
            "asymmetric traffic patterns; use popularity/overhead alongside delivery.",
            "",
            "### Problematic / review before freeze",
            "",
        ]
    )

    problematic = summary[summary["validation_status"].isin(["blocked", "needs_adjustment"])]
    if problematic.empty:
        lines.append("- None flagged as blocked/needs_adjustment by intent rules.")
    else:
        for _, r in problematic.iterrows():
            lines.append(f"- **{r['tp_id']} {r['tp_name']}** — status: `{r['validation_status']}`")

    lines.extend(
        [
            "- **S1_StrongCommunities_SeparateClusters** TP03/TP11: missing output (re-simulate).",
            "- **R1_Rural_RandomWaypoint**, **R11_SpeedExtremeLow:** zero delivery across all TPs (disconnected bases).",
            "- **TP12** urban WDM scenarios: extreme overhead in some bases (document or fix worldSize).",
            "",
            "## Recommended KPIs for routing benchmark",
            "",
            "### Main paper (core-4)",
            "",
            "1. **delivery_ratio** — primary effectiveness.",
            "2. **overhead_ratio** — replication cost.",
            "3. **latency_mean** — conditioned on delivery > 0.",
            "4. **drop_ratio** — buffer/transmission stress.",
            "",
            "### Paper (profile-specific context)",
            "",
            "| Profile | Extra KPI | Rationale |",
            "|---------|-----------|-----------|",
            "| TP02 | n_created | Load normalization |",
            "| TP03 | total_encounters | Copy spread under many small messages |",
            "| TP07 | t_median_frac | Burst timing validation |",
            "| TP08 | popularity_top10_ratio | Hub concentration |",
            "| TP06/TP11/TP12 | overhead + delivery | Directional asymmetry |",
            "",
            "### Supplementary material",
            "",
            "- contact_time_per_min, contact_time_mean_s, total_encounters",
            "- ratio_contact_nodes, spatial final_coverage_pct",
            "- useful_time_ratio, message creation time distribution (pct_last_10pct_sim)",
            "- Full indirect features and per-base spread (`tp_validation_by_base.csv`)",
            "",
            "## Profiles requiring adjustment before freeze",
            "",
        ]
    )

    freeze_list = summary[summary["validation_status"].isin(["blocked", "needs_adjustment", "partial"])]
    for _, r in freeze_list.iterrows():
        s = stats[stats["tp_id"] == r["tp_id"]].iloc[0]
        lines.append(
            f"- **{r['tp_id']}** (`{r['validation_status']}`): "
            f"{int(s['n_delivery_zero'])} zero-delivery, {int(s['n_missing_output'])} missing output."
        )

    lines.extend(
        [
            "",
            "## Per-TP KPI summary",
            "",
            "See [`traffic_profile_kpi_summary.csv`](../data/traffic_profile_kpi_summary.csv).",
            "",
            "| TP | primary | secondary | cost | stress | validation |",
            "|----|---------|-----------|------|--------|------------|",
        ]
    )
    for _, r in summary.iterrows():
        lines.append(
            f"| {r['tp_id']} | {r['primary_kpi']} | {r['secondary_kpi']} | "
            f"{r['cost_kpi']} | {r['stress_kpi']} | {r['validation_status']} |"
        )

    lines.extend(
        [
            "",
            "## Cross-references",
            "",
            "- [`tp_validation_report.md`](tp_validation_report.md)",
            "- [`corpus_v1_benchmark_validation.md`](corpus_v1_benchmark_validation.md)",
            "- [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)",
            "- [`traffic_profile_stats.csv`](../data/traffic_profile_stats.csv)",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze Traffic Profile KPIs for corpus_v1.")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    args = ap.parse_args()

    df = load_and_merge(args.manifest, args.data_dir)
    stats = compute_tp_stats(df)
    deltas = compute_paired_deltas(df)

    # Merge delta columns into stats for traceability
    stats = stats.merge(deltas, on="tp_id", how="left")

    rankings = compute_rankings(stats)
    rank_cols = {}
    for metric, order in rankings.items():
        rank_cols[f"rank_{metric}"] = [order.index(tp) + 1 for tp in stats["tp_id"]]
    for col, vals in rank_cols.items():
        stats[col] = vals

    summary = build_kpi_summary(stats, deltas, df)

    args.data_dir.mkdir(parents=True, exist_ok=True)
    stats_path = args.data_dir / "traffic_profile_stats.csv"
    summary_path = args.data_dir / "traffic_profile_kpi_summary.csv"
    report_path = (
        TRAFFIC_PROFILE_KPI_ANALYSIS
        if args.reports_dir == DEFAULT_REPORTS
        else args.reports_dir / "traffic_profile_kpi_analysis.md"
    )

    stats.to_csv(stats_path, index=False)
    summary.to_csv(summary_path, index=False)
    write_report(report_path, df, stats, deltas, summary, rankings)

    print(f"Wrote {stats_path} ({len(stats)} rows)")
    print(f"Wrote {summary_path} ({len(summary)} rows, {len(summary.columns)} cols)")
    print(f"Wrote {report_path}")
    print(f"TP01 delivery mean: {stats.loc[stats['tp_id'] == 'TP01', 'delivery_ratio_mean'].iloc[0]:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
