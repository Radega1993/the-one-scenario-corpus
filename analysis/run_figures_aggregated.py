#!/usr/bin/env python3
"""
Figuras agregadas legibles para corpus_v1 (familia, TP, base×TP).

Salida: scenarios/analysis/figures/aggregated/

Requiere: manifest.csv, output_metrics.csv; opcional correlation_pearson.csv,
spatial_occupancy_metrics.csv, features_reduced/core/normalized for ablation hist.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FIGURES_AGG = HERE / "figures" / "aggregated"
DATA_DIR = HERE / "data"
SPATIAL_HEATMAPS = HERE / "figures" / "spatial_heatmaps"

TP_ORDER = [f"TP{i:02d}" for i in range(1, 13)]
FAMILY_ORDER = [
    "01_urban",
    "02_campus",
    "03_vehicles",
    "04_rural",
    "05_disaster",
    "06_social",
]
FAMILY_SHORT = {
    "01_urban": "Urban",
    "02_campus": "Campus",
    "03_vehicles": "Vehicles",
    "04_rural": "Rural",
    "05_disaster": "Disaster",
    "06_social": "Social",
}

GALLERY_TPS = ["TP01", "TP07", "TP10", "TP02", "TP03", "TP04", "TP05", "TP06",
               "TP08", "TP09", "TP11", "TP12"]

def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".png"), dpi=150, bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), dpi=150, bbox_inches="tight")
    plt.close(fig)

def load_manifest(corpus: str) -> pd.DataFrame:
    p = HERE.parent / corpus / "manifest.csv"
    if not p.is_file():
        p = Path(corpus) / "manifest.csv"
    if not p.is_file():
        raise FileNotFoundError(f"manifest not found: {p}")
    m = pd.read_csv(p)
    m["traffic_profile_id"] = m["traffic_profile_id"].astype(str)
    return m

def merge_outputs(manifest: pd.DataFrame) -> pd.DataFrame:
    om = DATA_DIR / "output_metrics.csv"
    if not om.is_file():
        raise FileNotFoundError(f"Missing {om}; run run_analysis.py --phase output_metrics")
    out = pd.read_csv(om)
    df = manifest.merge(out, left_on="scenario_name", right_on="scenario", how="inner")
    return df

def plot_outputs_boxplot_by_tp(df: pd.DataFrame, out_dir: Path) -> None:
    metrics = [
        ("delivery_ratio", "Delivery ratio"),
        ("latency_mean", "Latency mean (s)"),
        ("overhead_ratio", "Overhead ratio"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, (col, title) in zip(axes, metrics):
        if col not in df.columns:
            continue
        data = [df.loc[df["traffic_profile_id"] == tp, col].dropna().values for tp in TP_ORDER]
        ax.boxplot(data, tick_labels=TP_ORDER, showfliers=False)
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45, labelsize=7)
        ax.grid(True, alpha=0.25, axis="y")
    fig.suptitle("Métricas de salida por perfil TP (todo el corpus)", fontsize=11)
    fig.tight_layout()
    _save(fig, out_dir / "outputs_boxplot_by_tp")

def plot_outputs_boxplot_faceted(df: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(3, 3, figsize=(14, 10))
    axes_flat = axes.flatten()
    for i, fam in enumerate(FAMILY_ORDER):
        ax = axes_flat[i]
        sub = df[df["family"] == fam]
        if sub.empty:
            ax.set_visible(False)
            continue
        data = [
            sub.loc[sub["traffic_profile_id"] == tp, "delivery_ratio"].dropna().values
            for tp in TP_ORDER
        ]
        ax.boxplot(data, tick_labels=TP_ORDER, showfliers=False)
        ax.set_title(FAMILY_SHORT.get(fam, fam), fontsize=9)
        ax.tick_params(axis="x", rotation=90, labelsize=6)
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.25, axis="y")
    for j in range(len(FAMILY_ORDER), len(axes_flat)):
        axes_flat[j].set_visible(False)
    fig.suptitle("Delivery ratio por TP y familia", fontsize=11)
    fig.tight_layout()
    _save(fig, out_dir / "outputs_boxplot_by_tp_faceted")

def _heatmap_base_tp(sub: pd.DataFrame, title: str, path: Path) -> None:
    if sub.empty:
        return
    pivot = sub.pivot_table(
        index="scenario_base",
        columns="traffic_profile_id",
        values="delivery_ratio",
        aggfunc="first",
    )
    pivot = pivot.reindex(columns=[c for c in TP_ORDER if c in pivot.columns])
    pivot = pivot.sort_index()
    nr, nc = pivot.shape
    if nr == 0 or nc == 0:
        return
    fig_h = max(4, min(24, 0.22 * nr + 2))
    fig_w = max(6, 0.45 * nc + 2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    im = ax.imshow(pivot.values, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(nc))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(nr))
    labels = [b[:28] + "…" if len(b) > 29 else b for b in pivot.index]
    ax.set_yticklabels(labels, fontsize=6)
    plt.colorbar(im, ax=ax, label="delivery_ratio")
    ax.set_title(title)
    fig.tight_layout()
    _save(fig, path)

def plot_heatmaps_base_tp(df: pd.DataFrame, out_dir: Path) -> None:
    _heatmap_base_tp(
        df,
        "Delivery ratio: escenario base × TP (corpus completo)",
        out_dir / "outputs_heatmap_base_x_tp_delivery",
    )
    for fam in FAMILY_ORDER:
        sub = df[df["family"] == fam]
        if sub.empty:
            continue
        slug = fam.replace("/", "_")
        _heatmap_base_tp(
            sub,
            f"Delivery ratio: base × TP — {FAMILY_SHORT.get(fam, fam)}",
            out_dir / f"outputs_heatmap_base_x_tp_{slug}",
        )

def plot_correlation_hist_by_family(manifest: pd.DataFrame, out_dir: Path) -> None:
    path_r = DATA_DIR / "correlation_pearson.csv"
    if not path_r.is_file():
        print(f"Skip correlation_hist_by_family: {path_r} missing")
        return
    R = pd.read_csv(path_r, index_col=0)
    scen_to_fam = dict(zip(manifest["scenario_name"], manifest["family"]))
    fig, axes = plt.subplots(3, 3, figsize=(12, 10))
    axes_flat = axes.flatten()
    for i, fam in enumerate(FAMILY_ORDER):
        ax = axes_flat[i]
        scens = [s for s in R.index if scen_to_fam.get(s) == fam]
        if len(scens) < 2:
            ax.set_visible(False)
            continue
        sub = R.loc[scens, scens].values
        n = len(scens)
        triu = np.triu_indices(n, k=1)
        r_flat = sub[triu[0], triu[1]]
        ax.hist(r_flat, bins=30, color="steelblue", edgecolor="black", alpha=0.75)
        ax.axvline(0.7, color="red", linestyle="--", linewidth=1)
        ax.axvline(-0.7, color="red", linestyle="--", linewidth=1)
        ax.set_title(FAMILY_SHORT.get(fam, fam), fontsize=9)
        ax.set_xlabel("r", fontsize=8)
        ax.grid(True, alpha=0.2)
    for j in range(len(FAMILY_ORDER), len(axes_flat)):
        axes_flat[j].set_visible(False)
    fig.suptitle("Distribución de correlaciones Pearson intra-familia (features Z)", fontsize=11)
    fig.tight_layout()
    _save(fig, out_dir / "correlation_hist_by_family")

def plot_tp12_median_offdiag(manifest: pd.DataFrame, out_dir: Path) -> None:
    path_r = DATA_DIR / "correlation_pearson.csv"
    if not path_r.is_file():
        return
    R = pd.read_csv(path_r, index_col=0)
    medians = []
    bases = []
    for base, grp in manifest.groupby("scenario_base"):
        scens = [s for s in grp["scenario_name"] if s in R.index]
        if len(scens) < 3:
            continue
        sub = R.loc[scens, scens].values
        n = len(scens)
        triu = np.triu_indices(n, k=1)
        vals = np.abs(sub[triu[0], triu[1]])
        medians.append(float(np.median(vals)) if len(vals) else np.nan)
        bases.append(base)
    if not bases:
        return
    order = np.argsort(medians)
    bases = [bases[i] for i in order]
    medians = [medians[i] for i in order]
    fig, ax = plt.subplots(figsize=(10, max(5, 0.15 * len(bases))))
    y = range(len(bases))
    ax.barh(y, medians, color="steelblue", edgecolor="black", height=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels([b[:40] for b in bases], fontsize=5)
    ax.axvline(0.7, color="red", linestyle="--", label="|r| = 0.7")
    ax.set_xlabel("Mediana |r| entre los 12 TP de la misma base")
    ax.set_title("Separación TP en espacio de features (por escenario base)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.25, axis="x")
    fig.tight_layout()
    _save(fig, out_dir / "correlation_tp12_median_offdiag_by_base")

def plot_tp06_tp11_redundancy(manifest: pd.DataFrame, out_dir: Path) -> None:
    path_r = DATA_DIR / "correlation_pearson.csv"
    if not path_r.is_file():
        return
    R = pd.read_csv(path_r, index_col=0)
    rs = []
    bases = []
    for base, grp in manifest.groupby("scenario_base"):
        s06 = grp.loc[grp["traffic_profile_id"] == "TP06", "scenario_name"]
        s11 = grp.loc[grp["traffic_profile_id"] == "TP11", "scenario_name"]
        if len(s06) != 1 or len(s11) != 1:
            continue
        a, b = s06.iloc[0], s11.iloc[0]
        if a not in R.index or b not in R.index:
            continue
        rs.append(float(R.loc[a, b]))
        bases.append(base)
    if not bases:
        return
    fig, ax = plt.subplots(figsize=(10, max(4, 0.12 * len(bases))))
    colors = ["crimson" if abs(r) >= 0.99 else "steelblue" for r in rs]
    ax.barh(range(len(bases)), rs, color=colors, edgecolor="black", height=0.75)
    ax.set_yticks(range(len(bases)))
    ax.set_yticklabels([b[:36] for b in bases], fontsize=5)
    ax.axvline(0.7, color="gray", linestyle="--", alpha=0.7)
    ax.set_xlabel("r Pearson TP06 vs TP11 (misma base)")
    ax.set_title("Redundancia conocida TP06 (OneToMany) ↔ TP11 (ManyToOne)")
    fig.tight_layout()
    _save(fig, out_dir / "correlation_tp06_tp11_redundancy")

def plot_ablation_histogram_compare(out_dir: Path, threshold: float = 0.7) -> None:
    spaces = [
        ("reduced_17", DATA_DIR / "features_reduced.csv", "reduced (17)"),
        ("core_23", DATA_DIR / "features_core.csv", "core (23)"),
        ("full_46", DATA_DIR / "features_normalized.csv", "full (46)"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    any_plot = False
    for ax, (_name, path, label) in zip(axes, spaces):
        if not path.is_file():
            ax.set_visible(False)
            continue
        Z = pd.read_csv(path, index_col=0).values
        n = Z.shape[0]
        if n < 2:
            ax.set_visible(False)
            continue
        Rs = np.corrcoef(Z)
        triu = np.triu_indices(n, k=1)
        r_flat = Rs[triu[0], triu[1]]
        ax.hist(r_flat, bins=30, color="steelblue", edgecolor="black", alpha=0.75)
        ax.axvline(threshold, color="red", linestyle="--")
        ax.axvline(-threshold, color="red", linestyle="--")
        pct = 100.0 * np.sum(np.abs(r_flat) >= threshold) / len(r_flat) if len(r_flat) else 0
        ax.set_title(f"{label}\n| r |≥{threshold}: {pct:.1f}%")
        ax.set_xlabel("Pearson r")
        ax.grid(True, alpha=0.2)
        any_plot = True
    if not any_plot:
        plt.close(fig)
        return
    fig.suptitle("Ablación de espacios de features", fontsize=11)
    fig.tight_layout()
    _save(fig, out_dir / "correlation_ablation_histogram_compare")

def plot_spatial_coverage(df: pd.DataFrame, out_dir: Path) -> None:
    sp_path = DATA_DIR / "spatial_occupancy_metrics.csv"
    if not sp_path.is_file():
        print(f"Skip spatial_coverage: {sp_path} missing")
        return
    sp = pd.read_csv(sp_path)
    if "cells_visited_pct" not in sp.columns or "family" not in sp.columns:
        return
    fams = [f for f in FAMILY_ORDER if f in sp["family"].values]
    data = [sp.loc[sp["family"] == f, "cells_visited_pct"].dropna().values for f in fams]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.boxplot(data, tick_labels=[FAMILY_SHORT.get(f, f) for f in fams], showfliers=False)
    ax.set_ylabel("cells_visited_pct")
    ax.set_title("Cobertura espacial por familia (escenarios con reporte)")
    ax.grid(True, alpha=0.25, axis="y")
    fig.tight_layout()
    _save(fig, out_dir / "spatial_coverage_by_family")

def plot_spatial_galleries(manifest: pd.DataFrame, out_dir: Path) -> None:
    if not SPATIAL_HEATMAPS.is_dir():
        print(f"Skip spatial galleries: {SPATIAL_HEATMAPS} missing")
        return
    for fam in FAMILY_ORDER:
        sub = manifest[manifest["family"] == fam]
        if sub.empty:
            continue
        base = sub["scenario_base"].iloc[0]
        grp = sub[sub["scenario_base"] == base]
        paths = []
        labels = []
        for tp in GALLERY_TPS:
            row = grp[grp["traffic_profile_id"] == tp]
            if row.empty:
                continue
            scen = row["scenario_name"].iloc[0]
            png = SPATIAL_HEATMAPS / f"{scen}.png"
            if png.is_file():
                paths.append(png)
                labels.append(tp)
        if not paths:
            continue
        n = len(paths)
        ncols = 4
        nrows = (n + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3.5 * nrows))
        axes_flat = np.atleast_1d(axes).flatten()
        for ax, png, lab in zip(axes_flat, paths, labels):
            img = plt.imread(png)
            ax.imshow(img)
            ax.set_title(lab, fontsize=9)
            ax.axis("off")
        for ax in axes_flat[len(paths):]:
            ax.axis("off")
        fig.suptitle(
            f"{FAMILY_SHORT.get(fam, fam)} — {base[:50]}",
            fontsize=10,
        )
        fig.tight_layout()
        slug = fam.replace("/", "_")
        _save(fig, out_dir / f"spatial_gallery_{slug}")

def plot_block_heatmap(manifest: pd.DataFrame, out_dir: Path) -> None:
    path_r = DATA_DIR / "correlation_pearson.csv"
    if not path_r.is_file():
        return
    R = pd.read_csv(path_r, index_col=0)
    order_df = manifest.sort_values(["family", "scenario_base", "traffic_profile_id"])
    scens = [s for s in order_df["scenario_name"] if s in R.index]
    if len(scens) < 2:
        return
    M = R.loc[scens, scens].values
    fams = order_df.set_index("scenario_name").loc[scens, "family"].values
    uniq_fams = []
    for f in fams:
        if f not in uniq_fams:
            uniq_fams.append(f)
    fam_to_i = {f: i for i, f in enumerate(uniq_fams)}
    cmap_fam = plt.get_cmap("tab10")
    fig, ax = plt.subplots(figsize=(10, 10))
    im = ax.imshow(M, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    plt.colorbar(im, ax=ax, label="Pearson r", fraction=0.046)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"Correlación ordenada por familia/base/TP (n={len(scens)}, sin etiquetas)")
    # family color bands on left margin
    for i, f in enumerate(fams):
        ax.add_patch(
            plt.Rectangle(
                (-0.8, i - 0.5),
                0.4,
                1,
                color=cmap_fam(fam_to_i[f] % 10),
                clip_on=False,
                transform=ax.transData,
            )
        )
    fig.tight_layout()
    _save(fig, out_dir / "pearson_block_heatmap_ordered")

def main() -> int:
    ap = argparse.ArgumentParser(description="Figuras agregadas por familia/TP/base")
    ap.add_argument("--corpus", default="corpus_v1")
    ap.add_argument("--threshold", type=float, default=0.7)
    ap.add_argument(
        "--include-block-heatmap",
        action="store_true",
        help="Generar pearson_block_heatmap_ordered.png (720×720)",
    )
    args = ap.parse_args()

    try:
        manifest = load_manifest(args.corpus)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 1

    out_dir = FIGURES_AGG
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Writing aggregated figures to {out_dir}")

    df = merge_outputs(manifest)
    plot_outputs_boxplot_by_tp(df, out_dir)
    plot_outputs_boxplot_faceted(df, out_dir)
    plot_heatmaps_base_tp(df, out_dir)
    plot_correlation_hist_by_family(manifest, out_dir)
    plot_tp12_median_offdiag(manifest, out_dir)
    plot_tp06_tp11_redundancy(manifest, out_dir)
    plot_ablation_histogram_compare(out_dir, threshold=args.threshold)
    plot_spatial_coverage(df, out_dir)
    plot_spatial_galleries(manifest, out_dir)
    if args.include_block_heatmap:
        plot_block_heatmap(manifest, out_dir)

    n_png = len(list(out_dir.glob("*.png")))
    print(f"Done. {n_png} PNG files in {out_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())