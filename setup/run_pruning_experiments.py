#!/usr/bin/env python3
"""
Run pruning sensitivity experiments for scenario_space_v1.

Modes:
  matrix          — feature_set × threshold grid → pruning_experiment_summary.*
  seed-stability  — multiple shuffle seeds for fixed (feature_set, threshold)

Reuses a shared features cache to avoid re-parsing 100800 .settings files.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SETUP = REPO / "scenarios" / "setup"
SPACE_V1 = REPO / "scenarios" / "scenario_space_v1"
PRUNING_ROOT = SPACE_V1 / "pruning"
SHARED_FEATURES = PRUNING_ROOT / "_shared" / "features.csv"

FEATURE_SETS = ("reduced17", "core23", "full46")
THRESHOLDS = (0.65, 0.70, 0.75, 0.80, 0.85)


def ensure_shared_features(workers: int, manifest: Path, force: bool) -> Path:
    if SHARED_FEATURES.exists() and not force:
        print(f"Reusing shared features: {SHARED_FEATURES}")
        return SHARED_FEATURES

    SHARED_FEATURES.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(SETUP))
    from prune_scenario_space_v1 import extract_features_to_df  # noqa: E402

    manifest_df = pd.read_csv(manifest)
    extract_features_to_df(manifest_df, workers=workers, features_output=SHARED_FEATURES)
    return SHARED_FEATURES


def run_one(
    feature_set: str,
    threshold: float,
    out_dir: Path,
    shuffle_seed: int,
    manifest: Path,
    features_input: Path,
) -> dict:
    sys.path.insert(0, str(SETUP))
    from prune_scenario_space_v1 import run  # noqa: E402

    return run(
        manifest_path=manifest,
        out_dir=out_dir,
        threshold=threshold,
        feature_set=feature_set,
        workers=1,
        limit=None,
        shuffle_seed=shuffle_seed,
        policy="strict",
        features_input=features_input,
        write_features=False,
        progress_every=0,
    )


def run_matrix(workers: int, manifest: Path, force_features: bool) -> pd.DataFrame:
    features = ensure_shared_features(workers, manifest, force_features)
    rows: list[dict] = []
    for fs in FEATURE_SETS:
        for th in THRESHOLDS:
            th_label = f"{th:.2f}".replace(".", "")
            out_dir = PRUNING_ROOT / f"{fs}_r{th_label}"
            row = run_one(fs, th, out_dir, shuffle_seed=42, manifest=manifest, features_input=features)
            rows.append(row)
    return pd.DataFrame(rows)


def run_seed_stability(
    feature_set: str,
    threshold: float,
    seeds: range,
    workers: int,
    manifest: Path,
    force_features: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = ensure_shared_features(workers, manifest, force_features)
    th_label = f"{threshold:.2f}".replace(".", "")
    rows: list[dict] = []
    for seed in seeds:
        out_dir = PRUNING_ROOT / f"{feature_set}_r{th_label}" / f"seed_{seed:03d}"
        row = run_one(feature_set, threshold, out_dir, shuffle_seed=seed, manifest=manifest, features_input=features)
        rows.append(row)
    detail = pd.DataFrame(rows)
    s = detail["selected"]
    summary = pd.DataFrame(
        [
            {
                "feature_set": feature_set,
                "threshold": threshold,
                "n_seeds": len(seeds),
                "min_selected": int(s.min()),
                "max_selected": int(s.max()),
                "mean_selected": float(s.mean()),
                "std_selected": float(s.std(ddof=0)),
                "best_seed": int(detail.loc[s.idxmax(), "shuffle_seed"]),
                "worst_seed": int(detail.loc[s.idxmin(), "shuffle_seed"]),
            }
        ]
    )
    return detail, summary


def write_summary_md(df: pd.DataFrame, path: Path, title: str) -> None:
    lines = [f"# {title}", "", f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}", ""]
    cols = [c for c in df.columns if c != "out_dir"]
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("| " + " | ".join("---" for _ in cols) + " |")
    for row in df.itertuples(index=False):
        vals = []
        for c in cols:
            v = getattr(row, c)
            if isinstance(v, float):
                vals.append(f"{v:.4f}" if abs(v) < 1000 else f"{v:.2f}")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Pruning sensitivity experiments for scenario_space_v1")
    p.add_argument("--manifest", type=Path, default=SPACE_V1 / "manifest.csv")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--force-features", action="store_true", help="Re-extract shared features.csv")
    sub = p.add_subparsers(dest="mode", required=True)

    sub.add_parser("matrix", help="Run feature_set × threshold grid")

    sp = sub.add_parser("seed-stability", help="Run multiple shuffle seeds")
    sp.add_argument("--feature-set", default="core23")
    sp.add_argument("--threshold", type=float, default=0.70)
    sp.add_argument("--seeds", type=int, default=100, help="Run seeds 0..N-1")

    sp_all = sub.add_parser("all", help="Run matrix + seed stability for core23 and full46 at 0.7")
    sp_all.add_argument("--seeds", type=int, default=100)

    args = p.parse_args()
    # Global flags must appear before subcommand name, e.g.:
    #   run_pruning_experiments.py --workers 8 all

    if args.mode == "matrix":
        df = run_matrix(args.workers, args.manifest, args.force_features)
        out_csv = PRUNING_ROOT / "pruning_experiment_summary.csv"
        out_md = PRUNING_ROOT / "pruning_experiment_summary.md"
        df.to_csv(out_csv, index=False)
        write_summary_md(df, out_md, "Pruning experiment summary (feature_set × threshold)")
        print(f"Written {out_csv} and {out_md}")

    elif args.mode == "seed-stability":
        detail, summary = run_seed_stability(
            args.feature_set,
            args.threshold,
            range(args.seeds),
            args.workers,
            args.manifest,
            args.force_features,
        )
        th_label = f"{args.threshold:.2f}".replace(".", "")
        detail.to_csv(PRUNING_ROOT / f"seed_stability_{args.feature_set}_r{th_label}_detail.csv", index=False)
        summary.to_csv(PRUNING_ROOT / f"seed_stability_{args.feature_set}_r{th_label}_summary.csv", index=False)
        write_summary_md(summary, PRUNING_ROOT / f"seed_stability_{args.feature_set}_r{th_label}_summary.md", "Seed stability summary")
        print(summary.to_string(index=False))

    elif args.mode == "all":
        df = run_matrix(args.workers, args.manifest, args.force_features)
        df.to_csv(PRUNING_ROOT / "pruning_experiment_summary.csv", index=False)
        write_summary_md(df, PRUNING_ROOT / "pruning_experiment_summary.md", "Pruning experiment summary (feature_set × threshold)")

        seed_summaries = []
        for fs in ("core23", "full46"):
            _detail, summ = run_seed_stability(fs, 0.70, range(args.seeds), args.workers, args.manifest, False)
            th_label = "070"
            _detail.to_csv(PRUNING_ROOT / f"seed_stability_{fs}_r{th_label}_detail.csv", index=False)
            summ.to_csv(PRUNING_ROOT / f"seed_stability_{fs}_r{th_label}_summary.csv", index=False)
            seed_summaries.append(summ)
        seed_all = pd.concat(seed_summaries, ignore_index=True)
        seed_all.to_csv(PRUNING_ROOT / "seed_stability_summary.csv", index=False)
        write_summary_md(seed_all, PRUNING_ROOT / "seed_stability_summary.md", "Seed stability (core23 & full46 @ 0.70)")
        print("All experiments complete.")


if __name__ == "__main__":
    main()
