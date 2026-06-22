#!/usr/bin/env python3
"""
Prune scenario_space_v1 by pairwise Pearson correlation between scenario feature vectors.

Avoids materializing the full N×N correlation matrix (100800² ≈ 81 GB).
Pipeline:
  1. Extract reportable features from .settings (reuse run_analysis.py)
  2. Z-score per feature (corpus-wide)
  3. Drop exact duplicate feature vectors (audited in duplicate_groups.csv)
  4. Greedy correlation pruning: accept scenario i iff max_j |r(Z_i, Z_j)| < threshold

Policy modes:
  strict   — no selected pair may have |r| >= threshold (implemented)
  balanced — allow up to X% of pairs above threshold while maximizing coverage
             (planned; see scenarios/scenario_space_v1/pruning/POLICY.md)

Outputs under scenarios/scenario_space_v1/pruning/.
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SCENARIOS = REPO / "scenarios"
ANALYSIS = SCENARIOS / "analysis"
SPACE_V1 = SCENARIOS / "scenario_space_v1"
DEFAULT_MANIFEST = SPACE_V1 / "manifest.csv"
DEFAULT_OUT = SPACE_V1 / "pruning"
SHARED_FEATURES = DEFAULT_OUT / "_shared" / "features.csv"

sys.path.insert(0, str(ANALYSIS))

from run_analysis import (  # noqa: E402
    FEATURES_CORE_23,
    FEATURES_REDUCED_17,
    load_settings,
    settings_to_reportable_features,
    zscore_normalize_per_feature,
)

COVERAGE_DIMENSIONS = [
    "map_id",
    "movement_model_primary",
    "group_structure",
    "n_hosts",
    "n_hosts_bin",
    "density_bin",
    "transmit_range_m",
    "buffer_size",
    "scenario_class",
]

N_HOSTS_BIN_EDGES = [0, 60, 100, 150, 200, 10_000]
N_HOSTS_BIN_LABELS = ["<=60", "61-100", "101-150", "151-200", ">200"]
DENSITY_BIN_EDGES = [0, 50, 200, 1_000, 10_000]
DENSITY_BIN_LABELS = ["very_low", "low", "medium", "high"]


def _extract_features(path_str: str) -> tuple[str, dict]:
    path = Path(path_str)
    label = path.stem
    feats = settings_to_reportable_features(load_settings(path))
    return label, feats


def pearson_rows_vs_selected(candidates: np.ndarray, selected: np.ndarray) -> np.ndarray:
    """
    Pearson r between each row of candidates (n×d) and each row of selected (m×d).
    Returns (n, m) with NaN where norm is zero.
    """
    if selected.size == 0:
        return np.zeros((candidates.shape[0], 0), dtype=np.float64)
    c = candidates.astype(np.float64, copy=False)
    s = selected.astype(np.float64, copy=False)
    c = np.nan_to_num(c, nan=0.0)
    s = np.nan_to_num(s, nan=0.0)
    c_c = c - c.mean(axis=1, keepdims=True)
    s_c = s - s.mean(axis=1, keepdims=True)
    c_norm = np.linalg.norm(c_c, axis=1, keepdims=True)
    s_norm = np.linalg.norm(s_c, axis=1, keepdims=True)
    denom = c_norm * s_norm.T
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (c_c @ s_c.T) / denom
    r[denom == 0] = np.nan
    return r


def greedy_prune_by_correlation(
    Z: np.ndarray,
    threshold: float,
    progress_every: int = 10000,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Greedy correlation pruning: accept scenario i iff
    max_j |r(Z_i, Z_j)| < threshold for all j already selected.
    Returns (selected_indices, rejected_indices, max_abs_r_when_rejected).
    """
    n, _d = Z.shape
    selected: list[int] = []
    rejected: list[int] = []
    max_r_rejected: list[float] = []
    z_sel = np.zeros((n, _d), dtype=np.float64)
    m_sel = 0

    for i in range(n):
        if m_sel == 0:
            selected.append(i)
            z_sel[0] = Z[i]
            m_sel = 1
            continue

        r_vec = pearson_rows_vs_selected(Z[i : i + 1], z_sel[:m_sel])[0]
        mr = float(np.nanmax(np.abs(r_vec))) if r_vec.size else 0.0
        if np.isnan(mr) or mr < threshold:
            selected.append(i)
            z_sel[m_sel] = Z[i]
            m_sel += 1
        else:
            rejected.append(i)
            max_r_rejected.append(mr)

        if progress_every and (i + 1) % progress_every == 0:
            print(f"  greedy {i + 1}/{n}: selected={m_sel}, rejected={len(rejected)}")

    return (
        np.array(selected, dtype=np.int64),
        np.array(rejected, dtype=np.int64),
        np.array(max_r_rejected, dtype=np.float64),
    )


def validate_selected_pairs(Z: np.ndarray, selected_idx: np.ndarray, threshold: float) -> dict[str, Any]:
    """Upper-triangle max |r| over the pruned set (O(|S|²), feasible when |S| is moderate)."""
    Zs = np.nan_to_num(Z[selected_idx].astype(np.float64), nan=0.0)
    m = Zs.shape[0]
    if m < 2:
        return {"n_pairs": 0, "max_abs_r": 0.0, "n_above_threshold": 0}
    max_abs = 0.0
    n_above = 0
    n_pairs = m * (m - 1) // 2
    block = 512
    for i0 in range(0, m, block):
        i1 = min(i0 + block, m)
        A = Zs[i0:i1]
        A_c = A - A.mean(axis=1, keepdims=True)
        A_norm = np.linalg.norm(A_c, axis=1, keepdims=True)
        for j0 in range(i0, m, block):
            j1 = min(j0 + block, m)
            B = Zs[j0:j1]
            B_c = B - B.mean(axis=1, keepdims=True)
            B_norm = np.linalg.norm(B_c, axis=1, keepdims=True)
            with np.errstate(invalid="ignore", divide="ignore"):
                r = (A_c @ B_c.T) / (A_norm * B_norm.T)
            for ii in range(A.shape[0]):
                gi = i0 + ii
                for jj in range(B.shape[0]):
                    gj = j0 + jj
                    if gj <= gi:
                        continue
                    val = abs(float(r[ii, jj])) if not np.isnan(r[ii, jj]) else 0.0
                    max_abs = max(max_abs, val)
                    if val >= threshold:
                        n_above += 1
    return {"n_pairs": n_pairs, "max_abs_r": max_abs, "n_above_threshold": n_above}


def feature_columns(feature_set: str, all_cols: list[str]) -> list[str]:
    if feature_set == "full46":
        return all_cols
    if feature_set == "core23":
        return [c for c in FEATURES_CORE_23 if c in all_cols]
    if feature_set == "reduced17":
        return [c for c in FEATURES_REDUCED_17 if c in all_cols]
    raise ValueError(f"Unknown feature set: {feature_set}")


def _feature_key_frame(Z: pd.DataFrame) -> pd.Series:
    return Z.round(8).astype(str).agg("|".join, axis=1)


def build_duplicate_groups(
    manifest: pd.DataFrame,
    Z_full: pd.DataFrame,
    feature_set: str,
) -> pd.DataFrame:
    """Map every duplicate scenario to its representative (first in manifest order)."""
    key = _feature_key_frame(Z_full.reset_index(drop=True))
    m = manifest.reset_index(drop=True).copy()
    m["_feat_key"] = key.values
    reps = (
        m.drop_duplicates("_feat_key", keep="first")[["_feat_key", "scenario_name", "candidate_id"]]
        .rename(
            columns={
                "scenario_name": "representative_scenario",
                "candidate_id": "representative_candidate_id",
            }
        )
    )
    dups = m[m.duplicated("_feat_key", keep="first")]
    out = dups[["scenario_name", "candidate_id", "_feat_key"]].merge(reps, on="_feat_key", how="left")
    out = out.rename(
        columns={
            "scenario_name": "duplicate_scenario",
            "candidate_id": "duplicate_candidate_id",
        }
    )
    out["feature_set"] = feature_set
    return out[
        [
            "duplicate_scenario",
            "duplicate_candidate_id",
            "representative_scenario",
            "representative_candidate_id",
            "feature_set",
        ]
    ]


def _bin_series(values: pd.Series, edges: list[float], labels: list[str]) -> pd.Series:
    return pd.cut(values, bins=edges, labels=labels, right=True, include_lowest=True)


def enrich_manifest_for_coverage(manifest: pd.DataFrame, feat_df: pd.DataFrame | None) -> pd.DataFrame:
    """Add derived audit columns used in coverage reports."""
    out = manifest.copy()
    out["movement_model_primary"] = out["movement_model"]
    out["scenario_class"] = out["map_id"].astype(str) + "|" + out["movement_model"].astype(str)
    out["n_hosts_bin"] = _bin_series(out["n_hosts"].astype(float), N_HOSTS_BIN_EDGES, N_HOSTS_BIN_LABELS)

    if feat_df is not None and "density" in feat_df.columns:
        out["density"] = out["scenario_name"].map(feat_df["density"])
        out["density_bin"] = _bin_series(out["density"].astype(float), DENSITY_BIN_EDGES, DENSITY_BIN_LABELS)
    else:
        out["density"] = np.nan
        out["density_bin"] = "unknown"

    if "transmit_range_m" in out.columns:
        out["transmit_range"] = out["transmit_range_m"]
    return out


def build_coverage_audit(
    full_manifest: pd.DataFrame,
    selected_manifest: pd.DataFrame,
    feat_df: pd.DataFrame | None,
) -> tuple[pd.DataFrame, str]:
    """Compare category counts: full design space vs correlation-pruned subset."""
    full_e = enrich_manifest_for_coverage(full_manifest, feat_df)
    sel_e = enrich_manifest_for_coverage(selected_manifest, feat_df)

    rows: list[dict[str, Any]] = []
    for dim in COVERAGE_DIMENSIONS:
        if dim not in full_e.columns:
            continue
        full_counts = full_e[dim].value_counts(dropna=False)
        sel_counts = sel_e[dim].value_counts(dropna=False)
        for value in full_counts.index.union(sel_counts.index):
            full_n = int(full_counts.get(value, 0))
            sel_n = int(sel_counts.get(value, 0))
            rows.append(
                {
                    "dimension": dim,
                    "value": str(value),
                    "full_count": full_n,
                    "selected_count": sel_n,
                    "retention_pct": (100.0 * sel_n / full_n) if full_n else 0.0,
                }
            )

    audit_df = pd.DataFrame(rows).sort_values(["dimension", "value"]).reset_index(drop=True)

    md_lines = [
        "# Coverage audit — correlation-pruned subset vs full manifest",
        "",
        f"- Full manifest scenarios: **{len(full_manifest):,}**",
        f"- Selected scenarios: **{len(selected_manifest):,}**",
        "",
        "Counts by design-space dimension (full vs selected).",
        "",
    ]
    for dim in COVERAGE_DIMENSIONS:
        sub = audit_df[audit_df["dimension"] == dim]
        if sub.empty:
            continue
        md_lines.append(f"## {dim}")
        md_lines.append("")
        md_lines.append("| value | full | selected | retention % |")
        md_lines.append("|-------|-----:|---------:|------------:|")
        for row in sub.itertuples():
            md_lines.append(
                f"| {row.value} | {row.full_count:,} | {row.selected_count:,} | {row.retention_pct:.2f} |"
            )
        md_lines.append("")

    return audit_df, "\n".join(md_lines) + "\n"


def extract_features_to_df(
    manifest: pd.DataFrame,
    workers: int,
    features_output: Path | None = None,
) -> pd.DataFrame:
    paths = [str(SCENARIOS / row.settings_file) for row in manifest.itertuples()]
    labels = [Path(p).stem for p in paths]
    n_manifest = len(manifest)

    print(f"Extracting features ({workers} workers)...")
    rows: list[dict] = []
    t_feat = time.time()
    if workers <= 1:
        for p in paths:
            _, feats = _extract_features(p)
            rows.append(feats)
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_extract_features, p): i for i, p in enumerate(paths)}
            results: list[dict | None] = [None] * n_manifest
            done = 0
            for fut in as_completed(futures):
                _lb, feats = fut.result()
                results[futures[fut]] = feats
                done += 1
                if done % 10000 == 0:
                    print(f"  {done}/{n_manifest} features extracted")
            rows = [r for r in results if r is not None]
    print(f"Features done in {time.time() - t_feat:.1f}s")

    feat_df = pd.DataFrame(rows, index=labels)
    feat_df.index.name = "scenario"
    if features_output is not None:
        features_output.parent.mkdir(parents=True, exist_ok=True)
        feat_df.to_csv(features_output)
        print(f"Written {features_output} shape={feat_df.shape}")
    return feat_df


def run(
    manifest_path: Path,
    out_dir: Path,
    threshold: float,
    feature_set: str,
    workers: int,
    limit: int | None,
    shuffle_seed: int | None,
    policy: str = "strict",
    features_input: Path | None = None,
    write_features: bool = True,
    progress_every: int = 10000,
) -> dict[str, Any]:
    if policy != "strict":
        raise NotImplementedError(
            f"Policy '{policy}' is not implemented yet. See {SPACE_V1 / 'pruning' / 'POLICY.md'}."
        )

    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = pd.read_csv(manifest_path)
    if limit is not None:
        manifest = manifest.head(limit).copy()
    n_manifest = len(manifest)
    print(f"Manifest: {n_manifest} scenarios ({manifest_path})")

    if features_input and features_input.exists():
        feat_df = pd.read_csv(features_input, index_col=0)
        if limit is not None:
            keep = manifest["scenario_name"].tolist()
            feat_df = feat_df.loc[[s for s in keep if s in feat_df.index]]
        print(f"Loaded features from {features_input} shape={feat_df.shape}")
    else:
        feat_df = extract_features_to_df(manifest, workers=workers, features_output=None)

    if write_features:
        feat_df.to_csv(out_dir / "features.csv")
        print(f"Written {out_dir / 'features.csv'} shape={feat_df.shape}")

    cols = feature_columns(feature_set, feat_df.columns.tolist())
    if not cols:
        raise RuntimeError(f"No columns for feature set {feature_set}")
    print(f"Feature set {feature_set}: d={len(cols)}")
    X = feat_df[cols].copy()

    Z_full, params = zscore_normalize_per_feature(X, impute_nan_zero=True)
    Z_full.to_csv(out_dir / "features_normalized.csv")
    params.to_csv(out_dir / "normalization_params.csv", index=False)

    dup_groups = build_duplicate_groups(manifest, Z_full, feature_set)
    dup_groups.to_csv(out_dir / "duplicate_groups.csv", index=False)
    print(f"Written {out_dir / 'duplicate_groups.csv'} ({len(dup_groups)} duplicate rows)")

    dup_mask = Z_full.duplicated(keep="first")
    n_dup = int(dup_mask.sum())
    unique_idx = np.where(~dup_mask.values)[0]
    Z_unique = Z_full.values[unique_idx]
    manifest_unique = manifest.iloc[unique_idx].reset_index(drop=True)
    print(f"Unique feature vectors: {len(unique_idx)} (dropped {n_dup} exact duplicates)")

    order = np.arange(len(unique_idx))
    if shuffle_seed is not None:
        rng = np.random.default_rng(shuffle_seed)
        order = rng.permutation(order)
        Z_work = Z_unique[order]
        manifest_work = manifest_unique.iloc[order].reset_index(drop=True)
    else:
        Z_work = Z_unique
        manifest_work = manifest_unique

    print(f"Greedy correlation pruning (threshold |r| < {threshold}, policy={policy})...")
    t_prune = time.time()
    sel_local, rej_local, max_r_rej = greedy_prune_by_correlation(
        Z_work, threshold, progress_every=progress_every
    )
    print(f"Pruning done in {time.time() - t_prune:.1f}s: kept {len(sel_local)}, rejected {len(rej_local)}")

    pruned_manifest = manifest_work.iloc[sel_local].reset_index(drop=True)
    pruned_manifest.to_csv(out_dir / "pruned_manifest.csv", index=False)

    selected_names = pruned_manifest["scenario_name"].tolist()
    (out_dir / "selected_scenarios.txt").write_text("\n".join(selected_names) + "\n", encoding="utf-8")
    (out_dir / "selected_candidate_ids.txt").write_text(
        "\n".join(pruned_manifest["candidate_id"].astype(str)) + "\n", encoding="utf-8"
    )

    if len(rej_local):
        rej_stats = pd.DataFrame(
            {
                "scenario_name": manifest_work.iloc[rej_local]["scenario_name"].values,
                "candidate_id": manifest_work.iloc[rej_local]["candidate_id"].values,
                "max_abs_r_vs_selected": max_r_rej,
            }
        )
        rej_stats.to_csv(out_dir / "rejected_max_r_summary.csv", index=False)

    validation = validate_selected_pairs(Z_work, sel_local, threshold)

    coverage_df, coverage_md = build_coverage_audit(manifest, pruned_manifest, feat_df)
    coverage_df.to_csv(out_dir / "coverage_audit.csv", index=False)
    (out_dir / "coverage_audit.md").write_text(coverage_md, encoding="utf-8")
    print(f"Written {out_dir / 'coverage_audit.csv'} and coverage_audit.md")

    elapsed = time.time() - t0
    retention_manifest = 100.0 * len(sel_local) / n_manifest
    retention_unique = 100.0 * len(sel_local) / len(unique_idx) if len(unique_idx) else 0.0

    report = [
        "=== scenario_space_v1 — pairwise Pearson correlation pruning ===",
        f"Manifest scenarios: {n_manifest}",
        f"Feature set: {feature_set} (d={len(cols)})",
        f"Policy: {policy}",
        f"Threshold: |r| < {threshold} (greedy vs selected set)",
        f"Exact duplicate feature vectors removed: {n_dup}",
        f"Unique before pruning: {len(unique_idx)}",
        f"Selected (pairwise correlation-pruned subset): {len(sel_local)}",
        f"Rejected by correlation: {len(rej_local)}",
        f"Retention (selected/manifest): {retention_manifest:.2f}%",
        f"Retention (selected/unique): {retention_unique:.2f}%",
        "",
        "Validation on pruned set (all pairs among selected):",
        f"  pairs: {validation['n_pairs']}",
        f"  max |r|: {validation['max_abs_r']:.6f}",
        f"  pairs with |r| >= {threshold}: {validation['n_above_threshold']}",
        "",
        f"Shuffle seed (greedy order): {shuffle_seed if shuffle_seed is not None else 'none (manifest order)'}",
        f"Elapsed: {elapsed:.1f}s",
        "",
        "Outputs:",
        f"  {out_dir / 'features.csv'}",
        f"  {out_dir / 'features_normalized.csv'}",
        f"  {out_dir / 'duplicate_groups.csv'}",
        f"  {out_dir / 'pruned_manifest.csv'}",
        f"  {out_dir / 'coverage_audit.csv'}",
        f"  {out_dir / 'coverage_audit.md'}",
        f"  {out_dir / 'selected_scenarios.txt'}",
    ]
    if len(rej_local):
        report.append(f"  {out_dir / 'rejected_max_r_summary.csv'}")
    report_text = "\n".join(report) + "\n"
    (out_dir / "pruning_report.txt").write_text(report_text, encoding="utf-8")
    print(report_text)

    return {
        "feature_set": feature_set,
        "threshold": threshold,
        "policy": policy,
        "shuffle_seed": shuffle_seed,
        "manifest_scenarios": n_manifest,
        "duplicates_removed": n_dup,
        "unique_vectors": len(unique_idx),
        "selected": len(sel_local),
        "retention_manifest_pct": retention_manifest,
        "retention_unique_pct": retention_unique,
        "max_abs_r": validation["max_abs_r"],
        "pairs_above_threshold": validation["n_above_threshold"],
        "elapsed_s": elapsed,
        "out_dir": str(out_dir),
    }


def main() -> None:
    p = argparse.ArgumentParser(
        description="Prune scenario_space_v1 by pairwise Pearson correlation (greedy)."
    )
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--threshold", type=float, default=0.7, help="Keep scenario if max |r| vs selected < threshold")
    p.add_argument(
        "--feature-set",
        choices=("core23", "full46", "reduced17"),
        default="core23",
        help="Feature columns for correlation (default: core23, aligned with corpus_v1 diversity)",
    )
    p.add_argument(
        "--policy",
        choices=("strict", "balanced"),
        default="strict",
        help="strict: no pair >= threshold among selected; balanced: planned (see POLICY.md)",
    )
    p.add_argument("--workers", type=int, default=8, help="Parallel workers for feature extraction")
    p.add_argument("--limit", type=int, default=None, help="Process only first N manifest rows (smoke test)")
    p.add_argument(
        "--shuffle-seed",
        type=int,
        default=42,
        help="Shuffle unique scenarios before greedy prune (reproducible). Use -1 for manifest order.",
    )
    p.add_argument(
        "--features-input",
        type=Path,
        default=None,
        help="Reuse pre-extracted features.csv (skips .settings parsing)",
    )
    p.add_argument(
        "--no-write-features",
        action="store_true",
        help="Do not copy features.csv to out-dir (use with --features-input in batch runs)",
    )
    args = p.parse_args()
    seed = None if args.shuffle_seed < 0 else args.shuffle_seed
    run(
        manifest_path=args.manifest,
        out_dir=args.out_dir,
        threshold=args.threshold,
        feature_set=args.feature_set,
        workers=args.workers,
        limit=args.limit,
        shuffle_seed=seed,
        policy=args.policy,
        features_input=args.features_input,
        write_features=not args.no_write_features,
    )


if __name__ == "__main__":
    main()
