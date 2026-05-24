#!/usr/bin/env python3
"""Correlate spatial occupancy and useful simulation time with routing outputs."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import CORPUS_V2, DATA_DIR, REPORTS_ANALYSIS_DIR  # noqa: E402

DEFAULT_DATA = DATA_DIR
DEFAULT_REPORTS = REPORTS_ANALYSIS_DIR
DEFAULT_MANIFEST = CORPUS_V2 / "manifest.csv"

from lib.report_paths import (  # noqa: E402
    SPATIAL_OCCUPANCY_ANALYSIS_SUMMARY,
    SPATIAL_VS_PERFORMANCE_ANALYSIS,
)


def _scenario_col(df: pd.DataFrame) -> str:
    if "scenario" in df.columns:
        return "scenario"
    if "scenario_name" in df.columns:
        return "scenario_name"
    return df.columns[0]


def _pearson(x: pd.Series, y: pd.Series) -> tuple[float, int]:
    mask = x.notna() & y.notna()
    if mask.sum() < 3:
        return float("nan"), int(mask.sum())
    return float(x[mask].corr(y[mask])), int(mask.sum())


def build_merged(data_dir: Path, manifest: Path) -> pd.DataFrame:
    m = pd.read_csv(manifest)
    sc = _scenario_col(m)
    if sc != "scenario":
        m = m.rename(columns={sc: "scenario"})

    om = pd.read_csv(data_dir / "output_metrics.csv")
    sc2 = _scenario_col(om)
    if sc2 != "scenario":
        om = om.rename(columns={sc2: "scenario"})

    spat = pd.read_csv(data_dir / "spatial_occupancy_metrics.csv")
    sc3 = _scenario_col(spat)
    if sc3 != "scenario":
        spat = spat.rename(columns={sc3: "scenario"})

    cols_spat = ["scenario", "final_coverage_pct", "cells_visited_pct"]
    spat = spat[[c for c in cols_spat if c in spat.columns]]

    ut_path = data_dir / "useful_simulation_time_metrics.csv"
    ut = None
    if ut_path.is_file():
        ut = pd.read_csv(ut_path)
        sc4 = _scenario_col(ut)
        if sc4 != "scenario":
            ut = ut.rename(columns={sc4: "scenario"})
        ut = ut[["scenario", "useful_time_ratio"]]

    out = m.merge(om, on="scenario", how="inner", suffixes=("", "_om"))
    out = out.merge(spat, on="scenario", how="left")
    if ut is not None:
        out = out.merge(ut, on="scenario", how="left")
    return out


def write_report(path: Path, df: pd.DataFrame) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    n = len(df)
    del_col = "delivery_ratio"
    cov_col = "final_coverage_pct"
    useful_col = "useful_time_ratio"

    r_cov_del, n_cov = _pearson(
        pd.to_numeric(df[cov_col], errors="coerce"),
        pd.to_numeric(df[del_col], errors="coerce"),
    )
    r_useful_del = float("nan")
    n_use = 0
    if useful_col in df.columns:
        r_useful_del, n_use = _pearson(
            pd.to_numeric(df[useful_col], errors="coerce"),
            pd.to_numeric(df[del_col], errors="coerce"),
        )

    # Family medians
    fam_lines = []
    if "family" in df.columns and cov_col in df.columns:
        agg = (
            df.groupby("family", as_index=False)[[cov_col, del_col]]
            .median()
            .sort_values(cov_col)
        )
        fam_lines.append("| Family | median coverage % | median delivery |")
        fam_lines.append("|--------|------------------:|----------------:|")
        for _, row in agg.iterrows():
            fam_lines.append(
                f"| `{row['family']}` | {row[cov_col]:.2f} | {row[del_col]:.4g} |"
            )

    low_cov = df[pd.to_numeric(df[cov_col], errors="coerce") < 12] if cov_col in df.columns else df.iloc[:0]
    n_low = len(low_cov)

    lines = [
        "# Spatial occupancy vs routing performance (corpus_v2)",
        "",
        f"Generated: {ts}",
        "",
        "## Executive summary",
        "",
        f"- **Scenarios merged:** {n} (manifest + output_metrics + spatial_occupancy_metrics).",
        f"- **Pearson** `{cov_col}` vs `{del_col}` (all scenarios): **r = {r_cov_del:.4f}** (n={n_cov}).",
    ]
    if useful_col in df.columns:
        lines.append(
            f"- **Pearson** `{useful_col}` vs `{del_col}`: **r = {r_useful_del:.4f}** (n={n_use})."
        )
    lines.extend(
        [
            "- **Interpretation:** Low *world* grid coverage on map-based mobility (WDM, MAP_UNDERUSED) "
            "does not imply simulation failure; it reflects roads vs rectangular world bounds.",
            "- **Paper figure:** [`spatial_coverage_by_family_paper.png`](../figures/paper/supplementary/spatial_coverage_by_family_paper.png)",
            "",
            "## Global correlation",
            "",
            "| X | Y | r | n |",
            "|---|---|--:|--:|",
            f"| final_coverage_pct | delivery_ratio | {r_cov_del:.4f} | {n_cov} |",
        ]
    )
    if useful_col in df.columns:
        lines.append(f"| useful_time_ratio | delivery_ratio | {r_useful_del:.4f} | {n_use} |")

    lines.extend(["", "## Median by family", ""])
    lines.extend(fam_lines or ["*(no family column)*"])

    lines.extend(
        [
            "",
            "## Low spatial coverage scenarios",
            "",
            f"Scenarios with `{cov_col} < 12%`: **{n_low}** (typical urban WDM / MAP_UNDERUSED).",
            "",
            "Do not exclude these from the benchmark without documenting in Methods; "
            "stratify by `map_dataset` or family when comparing protocols.",
            "",
            "## Relation to useful simulation time",
            "",
            "`useful_time_ratio` measures contact activity duration; "
            "`final_coverage_pct` measures explored grid fraction. "
            "They are complementary — see [`useful_simulation_time_report.md`](useful_simulation_time_report.md) "
            "and [`message_analysis_window_policy.md`](message_analysis_window_policy.md).",
            "",
            "## Regeneration",
            "",
            "```bash",
            "python3 scenarios/analysis/analyze_spatial_vs_performance.py",
            "```",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Spatial vs performance analysis.")
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = ap.parse_args()

    df = build_merged(args.data_dir, args.manifest)
    out = (
        SPATIAL_VS_PERFORMANCE_ANALYSIS
        if args.reports_dir == DEFAULT_REPORTS
        else args.reports_dir / "spatial_vs_performance_analysis.md"
    )
    write_report(out, df)

    # Refresh stale summary pointer
    summary = SPATIAL_OCCUPANCY_ANALYSIS_SUMMARY
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(
        f"# Spatial occupancy analysis (pointer)\n\n"
        f"**Superseded:** use [spatial_vs_performance_analysis.md](../canonical/spatial_vs_performance_analysis.md) "
        f"and [spatial_occupancy_report.md](spatial_occupancy_report.md).\n\n"
        f"Last spatial pipeline run: {len(df)} scenarios in merged analysis ({datetime.now(timezone.utc).date()}).\n",
        encoding="utf-8",
    )
    print(f"Wrote {out} (n={len(df)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
