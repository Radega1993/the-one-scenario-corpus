#!/usr/bin/env python3
"""
Build message analysis window policy for corpus_v2.

Outputs:
  data/message_analysis_window_policy.csv   — per-scenario policy (720 rows)
  data/message_analysis_window_by_tp.csv    — per-TP summary (12 rows)
  reports/message_analysis_window_policy.md — canonical methodology report
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

from lib.paths import CORPUS_V2, DATA_DIR, REPORTS_ANALYSIS_DIR  # noqa: E402
from lib.report_paths import MESSAGE_ANALYSIS_WINDOW_POLICY  # noqa: E402
from lib.traffic_profile_generator import PROFILE_ORDER  # noqa: E402

DEFAULT_MANIFEST = CORPUS_V2 / "manifest.csv"
DEFAULT_DATA = DATA_DIR
DEFAULT_REPORTS = REPORTS_ANALYSIS_DIR

PROFILE_NAMES = dict(PROFILE_ORDER)
DIRECTIONAL_TPS = frozenset({"TP06", "TP08", "TP11", "TP12"})
SENSITIVITY_TPS = frozenset({"TP02", "TP06", "TP08", "TP11"})
LATE_BIAS_THRESHOLD = 12.0
SENSITIVITY_LOW = 10.0


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _window_type(tp_id: str, gen_note: str) -> str:
    if tp_id == "TP07" or gen_note == "burst_only":
        return "burst_only"
    if tp_id in DIRECTIONAL_TPS:
        return "directional"
    return "full_simulation"


def _tp_decision(tp_id: str) -> str:
    if tp_id == "TP07":
        return "burst_exception"
    if tp_id == "TP10":
        return "stress_profile"
    if tp_id in SENSITIVITY_TPS:
        return "sensitivity_required"
    return "complete_window"


def _policy_status(row: pd.Series) -> str:
    tp = str(row["traffic_profile"])
    if str(row.get("classification", "")) == "disconnected":
        return "disconnected"
    enc = row.get("total_encounters")
    if pd.notna(enc) and float(enc) == 0:
        return "disconnected"
    if tp == "TP07":
        return "burst_exception"
    if tp == "TP10":
        return "stress_profile"
    pct_last = float(row["pct_messages_last_10"])
    if pct_last > LATE_BIAS_THRESHOLD:
        return "late_message_bias"
    if SENSITIVITY_LOW <= pct_last <= LATE_BIAS_THRESHOLD:
        return "sensitivity_required"
    return "ok"


def _build_notes(row: pd.Series) -> str:
    parts: list[str] = []
    wtype = row["window_type"]
    parts.append(f"window={wtype}")
    if pd.notna(row.get("msg_ttl_seconds")):
        parts.append(f"ttl_s={int(row['msg_ttl_seconds'])}")
    parts.append("primary=full_window[0,1]")
    parts.append("optional_censored_end=0.9")
    if row["policy_status"] == "burst_exception":
        parts.append("do_not_apply_late_cutoff")
    if row["policy_status"] == "stress_profile":
        parts.append("report_in_stress_tier")
    return "; ".join(parts)


def load_merged(manifest_path: Path, data_dir: Path) -> pd.DataFrame:
    m = pd.read_csv(manifest_path)
    msg = pd.read_csv(data_dir / "message_creation_time_summary.csv").rename(
        columns={"scenario": "scenario_name"}
    )
    win = pd.read_csv(data_dir / "traffic_profile_windows.csv")
    use = pd.read_csv(data_dir / "useful_simulation_time_metrics.csv").rename(
        columns={"scenario": "scenario_name", "traffic_profile": "traffic_profile_use"}
    )
    out = pd.read_csv(data_dir / "output_metrics.csv").rename(columns={"scenario": "scenario_name"})
    ind = pd.read_csv(data_dir / "indirect_features_diego.csv").rename(columns={"scenario": "scenario_name"})

    df = m.rename(columns={"scenario_base": "base_scenario"}).merge(
        msg[
            [
                "scenario_name",
                "t_min",
                "t_median",
                "t_max",
                "pct_first_10pct_sim",
                "pct_last_10pct_sim",
            ]
        ],
        on="scenario_name",
        how="left",
    )
    df = df.merge(
        win[
            [
                "scenario_name",
                "traffic_gen_note",
                "msg_ttl_seconds",
                "traffic_gen_start_s",
                "traffic_gen_end_s",
            ]
        ],
        on="scenario_name",
        how="left",
    )
    df = df.merge(
        use[["scenario_name", "classification", "useful_time_ratio", "total_encounters"]],
        on="scenario_name",
        how="left",
    )
    df = df.merge(out[["scenario_name", "delivery_ratio"]], on="scenario_name", how="left")
    if "total_encounters" not in df.columns or df["total_encounters"].isna().all():
        df = df.merge(
            ind[["scenario_name", "total_encounters"]].rename(
                columns={"total_encounters": "total_encounters_ind"}
            ),
            on="scenario_name",
            how="left",
        )
        if "total_encounters_ind" in df.columns:
            df["total_encounters"] = df["total_encounters"].fillna(df["total_encounters_ind"])

    df["traffic_profile"] = df["traffic_profile_id"]
    df["scenario_end_time"] = pd.to_numeric(df["Scenario.endTime"], errors="coerce")
    end = df["scenario_end_time"].replace(0, np.nan)
    df["first_creation_time_norm"] = (df["t_min"] / end).round(6)
    df["median_creation_time_norm"] = (df["t_median"] / end).round(6)
    df["last_creation_time_norm"] = (df["t_max"] / end).round(6)
    df["pct_messages_first_10"] = pd.to_numeric(df["pct_first_10pct_sim"], errors="coerce").round(4)
    df["pct_messages_last_10"] = pd.to_numeric(df["pct_last_10pct_sim"], errors="coerce").round(4)
    df["recommended_valid_start_norm"] = 0.0
    df["recommended_valid_end_norm"] = 1.0
    df["cutoff_seconds"] = (end * 0.9).round(1)
    df["window_type"] = df.apply(
        lambda r: _window_type(str(r["traffic_profile"]), str(r.get("traffic_gen_note", ""))),
        axis=1,
    )
    df["policy_status"] = df.apply(_policy_status, axis=1)
    df["notes"] = df.apply(_build_notes, axis=1)
    return df


def build_scenario_csv(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "scenario_name",
        "base_scenario",
        "family",
        "traffic_profile",
        "scenario_end_time",
        "first_creation_time_norm",
        "median_creation_time_norm",
        "last_creation_time_norm",
        "pct_messages_first_10",
        "pct_messages_last_10",
        "recommended_valid_start_norm",
        "recommended_valid_end_norm",
        "cutoff_seconds",
        "policy_status",
        "notes",
    ]
    return df[cols].copy()


def build_tp_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for tp_id, tp_name in PROFILE_ORDER:
        sub = df[df["traffic_profile"] == tp_id]
        wtype = _window_type(tp_id, "burst_only" if tp_id == "TP07" else "full_simulation")
        decision = _tp_decision(tp_id)
        n_late = int((sub["policy_status"] == "late_message_bias").sum())
        n_sens = int((sub["policy_status"] == "sensitivity_required").sum())
        interp = {
            "TP07": "Early burst window (20-28% endTime); late cutoff not applicable.",
            "TP10": "Storm/saturation stress tier; report separately from normal traffic profiles.",
            "TP02": "Low load with extended generation; elevated late-message fraction (~10%).",
            "TP06": "Directional fan-out; include censored sensitivity analysis.",
            "TP08": "Hub-target directional traffic; include censored sensitivity analysis.",
            "TP11": "Directional fan-in; include censored sensitivity analysis.",
        }.get(tp_id, "Full simulation window; primary metrics use all messages.")
        rows.append(
            {
                "tp_id": tp_id,
                "tp_name": tp_name,
                "window_type": wtype,
                "median_first_norm": round(float(sub["first_creation_time_norm"].median()), 6),
                "median_median_norm": round(float(sub["median_creation_time_norm"].median()), 6),
                "median_last_norm": round(float(sub["last_creation_time_norm"].median()), 6),
                "mean_pct_first_10": round(float(sub["pct_messages_first_10"].mean()), 4),
                "mean_pct_last_10": round(float(sub["pct_messages_last_10"].mean()), 4),
                "max_pct_last_10": round(float(sub["pct_messages_last_10"].max()), 4),
                "tp_decision": decision,
                "n_late_bias": n_late,
                "n_sensitivity": n_sens,
                "interpretation": interp,
            }
        )
    return pd.DataFrame(rows)


def _correlation_stats(df: pd.DataFrame) -> dict[str, float]:
    sub = df[df["policy_status"] != "disconnected"].copy()
    sub = sub[sub["delivery_ratio"].notna() & sub["pct_messages_last_10"].notna()]
    if len(sub) < 3:
        return {"pearson_r": float("nan"), "n": len(sub)}
    r = float(sub["pct_messages_last_10"].corr(sub["delivery_ratio"]))
    return {"pearson_r": round(r, 4), "n": len(sub)}


def write_report(
    path: Path,
    df: pd.DataFrame,
    tp_summary: pd.DataFrame,
    corr: dict[str, float],
) -> None:
    n_late = int((df["policy_status"] == "late_message_bias").sum())
    n_sens = int((df["policy_status"] == "sensitivity_required").sum())
    high_last = df.nlargest(8, "pct_messages_last_10")[
        ["scenario_name", "traffic_profile", "pct_messages_last_10", "delivery_ratio"]
    ]

    lines = [
        "# Message analysis window policy (corpus_v2)",
        "",
        f"Generated: {_utc()}",
        "",
        "Canonical policy for message-level metric aggregation. **Replaces** the earlier draft "
        "recommending 5% warmup + TTL cutoff (policy B+warmup).",
        "",
        "See also: [message_creation_time_audit.md](message_creation_time_audit.md), "
        "[simulation_time_policy.md](simulation_time_policy.md) (endTime/worldSize only).",
        "",
        "## Executive summary",
        "",
        f"- **Corpus:** corpus_v2 — {len(df)} simulations (60 bases × 12 Traffic Profiles).",
        "- **Primary policy:** report delivery, latency, overhead, and drop using **all messages** "
        "created during the simulation (`valid_start=0`, `valid_end=endTime`).",
        "- **Optional supplementary analysis:** exclude messages with `creation_time ≥ 0.9×endTime`.",
        "- **No global warmup** in primary message metrics (warmup 5% reserved for sensitivity appendix only).",
        "",
        "## Interpretation of existing figures",
        "",
        "### Boxplot (`figures/message_creation_time_boxplot_by_tp.png`)",
        "",
        "Per-scenario **median** of `creation_time/endTime`, grouped by TP. The dashed red line at **0.9** "
        "marks the start of the last 10% of simulation time. Most TPs cluster near **0.5** (uniform generation "
        "over the full window). **TP07** is the clear outlier (~0.24): traffic is intentionally concentrated "
        "in an early burst, not near the end.",
        "",
        "### Histograms (`figures/message_creation_time_hist_by_tp.png`)",
        "",
        "Pooled normalized creation times per TP. Full-window profiles show roughly flat distributions on [0,1]. "
        "**TP07** shows a narrow peak at 20–28% of endTime. The ~10% tail mass near 1.0 in full-window TPs "
        "matches the expected fraction of messages born in the closing decile.",
        "",
        "## Why late messages bias delivery_ratio",
        "",
        "Messages created after `0.9×endTime` have at most 10% of remaining simulation time for routing, "
        "buffering, and delivery. Even with long TTL, short remaining contact opportunities depress "
        "`delivery_ratio` and inflate or distort `latency_mean` (many never delivered). "
        "`MessageStatsReport` aggregates over **all** created messages, so this censoring is embedded in "
        "current corpus_v2 metrics.",
        "",
        "## Evidence in corpus_v2",
        "",
        f"- Scenarios with `pct_messages_last_10 > 12%`: **{n_late}** (`late_message_bias`).",
        f"- Scenarios with `pct_messages_last_10` in [10%, 12%]: **{n_sens}** (`sensitivity_required`).",
        f"- Pearson correlation `pct_messages_last_10` vs `delivery_ratio` (connected scenarios, n={corr['n']}): "
        f"**r = {corr['pearson_r']}**.",
        "",
        "**Conclusion:** Late-message censoring is a **moderate structural effect** (~10% of messages in the "
        "last decile for full-window TPs), not a simulation bug. It is predictable from MessageEventGenerator "
        "semantics and should be disclosed, not silently corrected in primary results.",
        "",
        "### Per-TP summary",
        "",
        "| TP | window | med norm | % first 10 (mean) | % last 10 (mean) | decision |",
        "|----|--------|----------|-------------------|------------------|----------|",
    ]
    for _, r in tp_summary.iterrows():
        lines.append(
            f"| {r['tp_id']} | {r['window_type']} | {r['median_median_norm']:.3f} | "
            f"{r['mean_pct_first_10']:.2f} | {r['mean_pct_last_10']:.2f} | {r['tp_decision']} |"
        )

    lines.extend(
        [
            "",
            "### Outlier scenarios (highest % last 10%)",
            "",
            "| Scenario | TP | % last 10 | delivery_ratio |",
            "|----------|-----|----------:|---------------:|",
        ]
    )
    for _, r in high_last.iterrows():
        dr = r["delivery_ratio"]
        dr_s = f"{dr:.4f}" if pd.notna(dr) else "n/a"
        lines.append(
            f"| `{r['scenario_name']}` | {r['traffic_profile']} | {r['pct_messages_last_10']:.1f} | {dr_s} |"
        )

    lines.extend(
        [
            "",
            "## TP07 — burst exception",
            "",
            "TP07 (`BurstWindow`) generates traffic only in **[0.20, 0.28]×endTime** (`burst_only`). "
            "`pct_messages_last_10 ≈ 0%` by design. Do **not** treat TP07 as late-message bias; "
            "do **not** apply the 0.9 cutoff as a bias correction. Compare TP07 on its own temporal regime.",
            "",
            "## TP10 — storm / stress profile",
            "",
            "TP10 (`Storm`) uses full simulation window but very high generation rate. "
            "Report in the **stress tier** alongside TP04/TP05/TP09, not as a normal traffic baseline.",
            "",
            "## Official policy for the paper",
            "",
            "### Primary (main text)",
            "",
            "1. Compute delivery, latency, overhead, and drop on **all messages** in each scenario.",
            "2. Do **not** apply a global mobility warmup to message outcome metrics.",
            "3. Disclose that ~10% of messages in full-window TPs are created in the final 10% of simulation time.",
            "",
            "### Optional (supplementary)",
            "",
            "Recompute metrics excluding messages with `creation_time ≥ 0.9×Scenario.endTime`. "
            "Label as **censored-late** sensitivity analysis.",
            "",
            "### Sensitivity appendix",
            "",
            "| Analysis | Window | Purpose |",
            "|----------|--------|---------|",
            "| A (primary) | [0, endTime] | Official benchmark |",
            "| B (supplementary) | [0, 0.9×endTime] | Late-message censoring |",
            "| C (discarded draft) | [0.05×endTime, endTime−TTL] | Former B+warmup policy — not adopted |",
            "",
            "## Declarable limitations",
            "",
            "- Current pipeline reads aggregate `MessageStatsReport`; per-message filtering requires "
            "`CreatedMessagesReport` (not yet in default batch).",
            "- TP05 short TTL interacts with late creation: some messages expire before delivery regardless of window.",
            "- Disconnected bases (R1, R11, etc.) have zero contacts; window policy is moot.",
            "- `simulation_time_policy` (5%/90% cutoffs) applies to **endTime/worldSize review**, not primary message KPIs.",
            "",
            "## Final TP decision table",
            "",
            "| TP | tp_decision | Rationale |",
            "|----|-------------|-----------|",
        ]
    )
    for _, r in tp_summary.iterrows():
        lines.append(f"| {r['tp_id']} {r['tp_name']} | `{r['tp_decision']}` | {r['interpretation']} |")

    lines.extend(
        [
            "",
            "## Data files",
            "",
            "- [`message_analysis_window_policy.csv`](../data/message_analysis_window_policy.csv) — per scenario",
            "- [`message_analysis_window_by_tp.csv`](../data/message_analysis_window_by_tp.csv) — per TP",
            "- [`message_creation_time_summary.csv`](../data/message_creation_time_summary.csv)",
            "- [`traffic_profile_windows.csv`](../data/traffic_profile_windows.csv)",
            "",
            "## Cross-references",
            "",
            "- [traffic_profile_kpi_analysis.md](traffic_profile_kpi_analysis.md)",
            "- [corpus_v2_benchmark_validation.md](corpus_v2_benchmark_validation.md)",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build message analysis window policy for corpus_v2.")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    args = ap.parse_args()

    df = load_merged(args.manifest, args.data_dir)
    scenario_csv = build_scenario_csv(df)
    tp_summary = build_tp_summary(df)
    corr = _correlation_stats(df)

    policy_path = args.data_dir / "message_analysis_window_policy.csv"
    tp_path = args.data_dir / "message_analysis_window_by_tp.csv"
    report_path = (
        MESSAGE_ANALYSIS_WINDOW_POLICY
        if args.reports_dir == DEFAULT_REPORTS
        else args.reports_dir / "message_analysis_window_policy.md"
    )

    args.data_dir.mkdir(parents=True, exist_ok=True)
    scenario_csv.to_csv(policy_path, index=False)
    tp_summary.to_csv(tp_path, index=False)
    write_report(report_path, df, tp_summary, corr)

    print(f"Wrote {policy_path} ({len(scenario_csv)} rows)")
    print(f"Wrote {tp_path} ({len(tp_summary)} rows)")
    print(f"Wrote {report_path}")
    print(f"TP07 mean_pct_last_10: {tp_summary.loc[tp_summary.tp_id=='TP07', 'mean_pct_last_10'].iloc[0]}")
    print(f"Correlation r: {corr['pearson_r']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
