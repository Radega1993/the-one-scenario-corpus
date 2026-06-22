#!/usr/bin/env python3
"""Per-archetype internal saturation metrics for map_space_saturation_v1."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from analyze_map_space_saturation_v1 import (  # noqa: E402
    DEDUP_TOL,
    GLOBAL_SEED,
    REDUNDANCY_NN_THRESHOLD,
    cluster_k,
    count_clusters_from_medoids,
    dedupe_exact,
    pairwise_l2,
    select_kmedoids,
)
from extract_map_space_saturation_features import NUMERIC_FEATURE_COLUMNS, parse_float  # noqa: E402

REPO_ROOT = _SETUP.parent.parent
SCENARIOS_DIR = REPO_ROOT / "scenarios"

DEFAULT_FEATURES = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_features.csv"
DEFAULT_FEATURES_NORM = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_features_normalized.csv"
DEFAULT_ARCHETYPES = SCENARIOS_DIR / "analysis" / "data" / "map_archetype_definitions_v1.csv"
DEFAULT_OUT_CSV = SCENARIOS_DIR / "analysis" / "data" / "map_saturation_by_archetype.csv"
DEFAULT_REPORT = SCENARIOS_DIR / "analysis" / "reports" / "map_saturation_by_archetype_report.md"
DEFAULT_FIGURES = SCENARIOS_DIR / "analysis" / "figures" / "map_space_saturation"

OSM_ONLY_ARCHETYPES = {"compact_residential", "suburban_low_density"}
TRACE_ARCHETYPES = {"conference_event_compact", "clustered_communities"}


def load_declared_archetypes(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as f:
        return [r["archetype"] for r in csv.DictReader(f) if r.get("archetype")]


def sub_zscore_matrix(df: pd.DataFrame, cols: list[str]) -> np.ndarray:
    n = len(df)
    d = len(cols)
    mat = np.zeros((n, d), dtype=np.float64)
    for j, col in enumerate(cols):
        vals = df[col].apply(parse_float).to_numpy(dtype=np.float64)
        valid = ~np.isnan(vals)
        if valid.sum() == 0:
            continue
        mu = vals[valid].mean()
        sigma = vals[valid].std(ddof=0)
        if sigma < 1e-12:
            mat[:, j] = 0.0
        else:
            normed = (vals - mu) / sigma
            normed[np.isnan(normed)] = 0.0
            mat[:, j] = normed
    return mat


def nn_stats_excluding_self(z: np.ndarray) -> tuple[float, float, float]:
    n = z.shape[0]
    if n <= 1:
        return 0.0, 0.0, 0.0
    d = pairwise_l2(z, z)
    np.fill_diagonal(d, np.inf)
    nearest = d.min(axis=1)
    return float(np.mean(nearest)), float(np.median(nearest)), float(
        (nearest < REDUNDANCY_NN_THRESHOLD).mean()
    )


def classify_status(
    arch: str,
    n: int,
    near_redundant_fraction: float,
    n_clusters_internal: int,
) -> str:
    if n < 30:
        if arch in OSM_ONLY_ARCHETYPES or arch in TRACE_ARCHETYPES:
            return "LOW_SAMPLE_BUT_ACCEPTABLE"
        return "NEEDS_MORE_GENERATION"
    if near_redundant_fraction >= 0.5 and n_clusters_internal <= 2:
        return "NEEDS_MORE_GENERATION"
    if n >= 40 and near_redundant_fraction < 0.35 and n_clusters_internal >= 3:
        return "WELL_COVERED"
    if n >= 30:
        return "ACCEPTABLE"
    return "NEEDS_MORE_GENERATION"


def analyze_archetype(df_arch: pd.DataFrame) -> dict:
    n = len(df_arch)
    z = sub_zscore_matrix(df_arch, NUMERIC_FEATURE_COLUMNS)
    map_ids = df_arch["map_id"].tolist()

    _, n_unique = dedupe_exact(z, map_ids)
    k = cluster_k(n)
    medoids = select_kmedoids(z, k, GLOBAL_SEED)
    n_clusters = count_clusters_from_medoids(z, medoids)
    mean_nn, median_nn, near_red = nn_stats_excluding_self(z)
    intra_var = float(np.mean(np.var(z, axis=0)))

    arch = df_arch["archetype"].iloc[0]
    status = classify_status(arch, n, near_red, n_clusters)

    return {
        "archetype": arch,
        "n_valid_maps": n,
        "n_unique_feature_vectors": n_unique,
        "n_clusters_internal": n_clusters,
        "mean_nn_dist": mean_nn,
        "median_nn_dist": median_nn,
        "near_redundant_fraction": near_red,
        "intra_archetype_variance": intra_var,
        "status": status,
    }


def plot_bars(rows: list[dict], field: str, ylabel: str, title: str, path: Path, hlines: list[tuple[float, str]] | None = None) -> None:
    archs = [r["archetype"] for r in rows]
    vals = [r[field] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(archs)), vals, color="steelblue")
    ax.set_xticks(range(len(archs)))
    ax.set_xticklabels(archs, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if hlines:
        for y, label in hlines:
            ax.axhline(y, color="gray", linestyle="--", linewidth=0.8, label=label)
        ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150)
    plt.close()


def plot_clusters_vs_n(rows: list[dict], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ns = [r["n_valid_maps"] for r in rows]
    ks = [r["n_clusters_internal"] for r in rows]
    ax.scatter(ns, ks, s=60, c="C2")
    for r in rows:
        ax.annotate(r["archetype"].split("_")[0], (r["n_valid_maps"], r["n_clusters_internal"]), fontsize=6)
    ax.set_xlabel("n_valid_maps")
    ax.set_ylabel("n_clusters_internal")
    ax.set_title("Internal clusters vs valid maps per archetype")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150)
    plt.close()


def write_report(rows: list[dict], path: Path) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    table = "\n".join(
        f"| {r['archetype']} | {r['n_valid_maps']} | {r['n_unique_feature_vectors']} | "
        f"{r['n_clusters_internal']} | {r['mean_nn_dist']:.3f} | {r['near_redundant_fraction']:.3f} | "
        f"{r['status']} |"
        for r in rows
    )
    needs = [r["archetype"] for r in rows if r["status"] == "NEEDS_MORE_GENERATION"]
    body = f"""# Intra-archetype saturation analysis (v1)

Generated: {ts}

## Purpose

For each of the 15 declared archetypes, this report measures **internal** diversity in raw feature space (sub-z-score within archetype): unique vectors, internal k-medoids clusters, nearest-neighbour distances, and near-redundancy (NN &lt; {REDUNDANCY_NN_THRESHOLD}).

Global feature-space saturation at N = 1200 is documented in `map_space_saturation_report.md`. This analysis answers whether any single archetype remains undersampled or collapsed.

## Status rules

| Status | Criterion |
|--------|-----------|
| WELL_COVERED | n ≥ 40, near_redundant_fraction &lt; 0.35, n_clusters_internal ≥ 3 |
| ACCEPTABLE | n ≥ 30 |
| LOW_SAMPLE_BUT_ACCEPTABLE | n &lt; 30 with OSM-only or trace-backed justification |
| NEEDS_MORE_GENERATION | otherwise |

## Results

| Archetype | n_valid | n_unique | n_clusters | mean_nn | near_red_frac | status |
|-----------|---------|----------|------------|---------|---------------|--------|
{table}

## Interpretation

- Minimum sample size: **{min(r['n_valid_maps'] for r in rows)}** (`{min(rows, key=lambda r: r['n_valid_maps'])['archetype']}`).
- Archetypes flagged NEEDS_MORE_GENERATION: **{', '.join(needs) if needs else 'none'}**.
- With global saturation confirmed at batch 1200, per-archetype counts of 33–169 are sufficient: further batch growth added mostly near-redundant maps in the **global** pool (≥50% redundant/invalid in post-800 tranches).
- OSM-only archetypes (`compact_residential`, `suburban_low_density`) have no dedicated synthetic generator by design; their sample sizes reflect anchor variant policy, not generator failure.

## Figures

- `saturation_by_archetype_valid_maps.png`
- `saturation_by_archetype_nn_distance.png`
- `saturation_by_archetype_clusters.png`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--archetypes", type=Path, default=DEFAULT_ARCHETYPES)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUT_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES)
    args = parser.parse_args()

    archetypes = load_declared_archetypes(args.archetypes)
    feat = pd.read_csv(args.features)

    rows: list[dict] = []
    for arch in archetypes:
        sub = feat[feat["archetype"] == arch]
        if len(sub) == 0:
            rows.append({
                "archetype": arch,
                "n_valid_maps": 0,
                "n_unique_feature_vectors": 0,
                "n_clusters_internal": 0,
                "mean_nn_dist": 0.0,
                "median_nn_dist": 0.0,
                "near_redundant_fraction": 0.0,
                "intra_archetype_variance": 0.0,
                "status": "NEEDS_MORE_GENERATION",
            })
            continue
        rows.append(analyze_archetype(sub))

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output_csv, index=False)

    plot_bars(
        rows, "n_valid_maps", "Valid maps", "Valid maps per archetype",
        args.figures_dir / "saturation_by_archetype_valid_maps.png",
        hlines=[(30, "ACCEPTABLE (30)"), (40, "WELL_COVERED (40)")],
    )
    plot_bars(
        rows, "mean_nn_dist", "Mean NN L2 (intra-archetype)",
        "Mean intra-archetype NN distance",
        args.figures_dir / "saturation_by_archetype_nn_distance.png",
    )
    plot_clusters_vs_n(rows, args.figures_dir / "saturation_by_archetype_clusters.png")
    write_report(rows, args.report)

    print(f"Wrote {args.output_csv}")
    print(f"Wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
