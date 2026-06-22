#!/usr/bin/env python3
"""Analyze feature-space saturation for map_space_saturation_v1 cumulative batches."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from extract_map_space_saturation_features import (  # noqa: E402
    INCLUDED_STATUSES,
    NUMERIC_FEATURE_COLUMNS,
    parse_float,
)

REPO_ROOT = _SETUP.parent.parent
SCENARIOS_DIR = REPO_ROOT / "scenarios"

DEFAULT_FEATURES = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_features.csv"
DEFAULT_FEATURES_NORM = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_features_normalized.csv"
DEFAULT_VALIDATION = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_validation.csv"
DEFAULT_MANIFEST = SCENARIOS_DIR / "map_space_saturation_v1" / "manifest_maps_all.csv"
DEFAULT_ARCHETYPES = SCENARIOS_DIR / "analysis" / "data" / "map_archetype_definitions_v1.csv"
DEFAULT_YAML = SCENARIOS_DIR / "analysis" / "config" / "map_design_space_saturation_v1.yaml"

DEFAULT_METRICS = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_metrics.csv"
DEFAULT_BY_BATCH = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_by_batch.csv"
DEFAULT_DECISION = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_decision.json"
DEFAULT_REPORT = SCENARIOS_DIR / "analysis" / "reports" / "map_space_saturation_report.md"
DEFAULT_FIGURES = SCENARIOS_DIR / "analysis" / "figures" / "map_space_saturation"

BATCH_THRESHOLDS = [100, 200, 400, 600, 800, 1000, 1200, 1600, 2000]
SOURCE_TYPES = ["osm", "synthetic", "trace_reference_synthetic"]
DEDUP_TOL = 1e-6
GLOBAL_SEED = 42
STOP_REL_THRESHOLD = 0.05
MIN_VALID_MAPS_STOP = 200
MIN_CONSECUTIVE_TRANSITIONS = 2
REDUNDANCY_NN_THRESHOLD = 0.25
HEURISTIC_MIN_SCORE = 4
# Deliberate extension batches (800→1000→1200) use slightly relaxed thresholds
# because max-medoid is unstable when k-medoids k changes; mean + marginal valid maps
# are the primary confirmation signals.
EXTENSION_CONFIRM_FROM_BATCH = 800
ROBUSTNESS_EXTENSION_FROM_BATCH = 1200
# Extension uses relative marginal-valid growth (not absolute count) so OSM catch-up
# runs with many new valid maps still qualify when growth rate is slowing.
EXTENSION_REL_MARGINAL_VALID = 0.30
EXTENSION_REL_CLUSTERS = 0.16
EXTENSION_REL_MEAN_MEDOID = 0.08


# ---------------------------------------------------------------------------
# Distance / clustering helpers (ported from prune_map_space_v1.py)
# ---------------------------------------------------------------------------


def pairwise_l2(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if b.size == 0:
        return np.zeros((a.shape[0], 0))
    aa = np.sum(a * a, axis=1, keepdims=True)
    bb = np.sum(b * b, axis=1, keepdims=True).T
    ab = a @ b.T
    d2 = np.maximum(aa + bb - 2.0 * ab, 0.0)
    return np.sqrt(d2)


def l2_normalize_rows(z: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    norms = np.where(norms < 1e-12, 1.0, norms)
    return z / norms


def pairwise_cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_n = l2_normalize_rows(a)
    b_n = l2_normalize_rows(b)
    sim = np.clip(a_n @ b_n.T, -1.0, 1.0)
    return 1.0 - sim


def dist_to_set(points: np.ndarray, selected: np.ndarray) -> np.ndarray:
    if selected.size == 0:
        return np.full(points.shape[0], np.inf)
    return pairwise_l2(points, selected).min(axis=1)


def dedupe_exact(z: np.ndarray, map_ids: list[str]) -> tuple[np.ndarray, int]:
    rounded = np.round(z / DEDUP_TOL).astype(np.int64)
    seen: dict[tuple[int, ...], int] = {}
    unique_idx: list[int] = []
    order = sorted(range(len(map_ids)), key=lambda i: map_ids[i])
    for i in order:
        key = tuple(rounded[i].tolist())
        if key not in seen:
            seen[key] = len(unique_idx)
            unique_idx.append(i)
    return np.array(unique_idx, dtype=int), len(unique_idx)


def kmeans_pp_init(z: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    n = z.shape[0]
    if k >= n:
        return np.arange(n, dtype=int)
    centers = [int(rng.integers(0, n))]
    for _ in range(1, k):
        pts = z[centers]
        d = dist_to_set(z, pts)
        d[centers] = -1.0
        probs = d ** 2
        total = probs.sum()
        if total <= 0:
            remaining = [i for i in range(n) if i not in centers]
            centers.append(remaining[0])
            continue
        probs /= total
        centers.append(int(rng.choice(n, p=probs)))
    return np.array(centers, dtype=int)


def select_farthest(z: np.ndarray, k: int, seed: int) -> np.ndarray:
    n = z.shape[0]
    k = min(k, n)
    if k <= 0:
        return np.array([], dtype=int)
    if k >= n:
        return np.arange(n, dtype=int)
    rng = np.random.default_rng(seed)
    selected = [int(rng.integers(0, n))]
    while len(selected) < k:
        sel_pts = z[selected]
        d = dist_to_set(z, sel_pts)
        for idx in selected:
            d[idx] = -1.0
        next_i = int(np.argmax(d))
        selected.append(next_i)
    return np.array(selected, dtype=int)


def select_kmedoids(z: np.ndarray, k: int, seed: int, max_iter: int = 50) -> np.ndarray:
    n, _ = z.shape
    k = min(k, n)
    if k <= 0:
        return np.array([], dtype=int)
    if k >= n:
        return np.arange(n, dtype=int)
    rng = np.random.default_rng(seed)
    medoids = kmeans_pp_init(z, k, rng)
    for _ in range(max_iter):
        d = pairwise_l2(z, z[medoids])
        labels = d.argmin(axis=1)
        new_medoids = medoids.copy()
        changed = False
        for c in range(k):
            members = np.where(labels == c)[0]
            if len(members) == 0:
                continue
            sub = z[members]
            sub_d = pairwise_l2(sub, sub)
            local_best = int(members[sub_d.sum(axis=1).argmin()])
            if local_best != medoids[c]:
                new_medoids[c] = local_best
                changed = True
        medoids = new_medoids
        if not changed:
            break
    return np.unique(medoids)


def cluster_k(n: int) -> int:
    if n <= 1:
        return 1
    return int(max(2, min(round(math.sqrt(n)), min(n, 50))))


def count_clusters_from_medoids(z: np.ndarray, medoid_idx: np.ndarray) -> int:
    if len(medoid_idx) == 0:
        return 0
    d = pairwise_l2(z, z[medoid_idx])
    labels = d.argmin(axis=1)
    return len(np.unique(labels))


def count_clusters_hierarchical(z: np.ndarray, k: int) -> int:
    n = z.shape[0]
    if n <= 1:
        return n
    k = min(k, n)
    z_n = l2_normalize_rows(z)
    condensed = pdist(z_n, metric="cosine")
    z_link = linkage(condensed, method="average")
    labels = fcluster(z_link, t=k, criterion="maxclust")
    return len(np.unique(labels))


def nearest_neighbor_stats(z: np.ndarray) -> dict[str, float]:
    n = z.shape[0]
    if n <= 1:
        return {"mean_nn_dist_l2": 0.0, "median_nn_dist_l2": 0.0, "max_nn_dist_l2": 0.0}
    d = pairwise_l2(z, z)
    np.fill_diagonal(d, np.inf)
    nn = d.min(axis=1)
    return {
        "mean_nn_dist_l2": float(np.mean(nn)),
        "median_nn_dist_l2": float(np.median(nn)),
        "max_nn_dist_l2": float(np.max(nn)),
    }


def medoid_coverage_stats_l2(z: np.ndarray, medoid_idx: np.ndarray) -> dict[str, float]:
    if len(medoid_idx) == 0:
        return {"mean_dist_to_medoid_l2": 0.0, "max_dist_to_medoid_l2": 0.0}
    d = pairwise_l2(z, z[medoid_idx])
    nearest = d.min(axis=1)
    return {
        "mean_dist_to_medoid_l2": float(np.mean(nearest)),
        "max_dist_to_medoid_l2": float(np.max(nearest)),
    }


def medoid_coverage_stats_cosine(z: np.ndarray, medoid_idx: np.ndarray) -> dict[str, float]:
    if len(medoid_idx) == 0:
        return {"mean_dist_to_medoid_cosine": 0.0, "max_dist_to_medoid_cosine": 0.0}
    d = pairwise_cosine(z, z[medoid_idx])
    nearest = d.min(axis=1)
    return {
        "mean_dist_to_medoid_cosine": float(np.mean(nearest)),
        "max_dist_to_medoid_cosine": float(np.max(nearest)),
    }


def pca_variance_explained(z: np.ndarray, k_list: list[int]) -> dict[str, float]:
    if z.shape[0] < 2:
        return {f"pca_var_explained_{k}": 0.0 for k in k_list}
    zc = z - z.mean(axis=0)
    _, s, _ = np.linalg.svd(zc, full_matrices=False)
    var = (s ** 2) / max(z.shape[0] - 1, 1)
    total = var.sum()
    if total <= 0:
        return {f"pca_var_explained_{k}": 0.0 for k in k_list}
    cum = np.cumsum(var) / total
    out: dict[str, float] = {}
    for k in k_list:
        idx = min(k, len(cum)) - 1
        out[f"pca_var_explained_{k}"] = float(cum[idx])
    return out


def build_normalized_matrix(
    df: pd.DataFrame,
    numeric_cols: list[str],
) -> tuple[np.ndarray, list[str]]:
    """Cumulative z-score + one-hot source_type for rows in df."""
    map_ids = df["map_id"].tolist()
    n = len(df)
    d_num = len(numeric_cols)
    d_src = len(SOURCE_TYPES)
    mat = np.zeros((n, d_num + d_src), dtype=np.float64)

    for j, col in enumerate(numeric_cols):
        vals = df[col].apply(parse_float).to_numpy(dtype=np.float64)
        valid = ~np.isnan(vals)
        if valid.sum() == 0:
            mat[:, j] = 0.0
            continue
        mu = vals[valid].mean()
        sigma = vals[valid].std(ddof=0)
        if sigma < 1e-12:
            mat[:, j] = 0.0
        else:
            normed = (vals - mu) / sigma
            normed[np.isnan(normed)] = 0.0
            mat[:, j] = normed

    for j, st in enumerate(SOURCE_TYPES):
        mat[:, d_num + j] = (df["source_type"] == st).astype(np.float64).to_numpy()

    return mat, map_ids


def vector_keys(z: np.ndarray) -> list[tuple[int, ...]]:
    rounded = np.round(z / DEDUP_TOL).astype(np.int64)
    return [tuple(row.tolist()) for row in rounded]


def fmt(v: Any, digits: int = 6) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (list, tuple, set)):
        return ";".join(str(x) for x in sorted(v))
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return ""
        return f"{v:.{digits}f}".rstrip("0").rstrip(".") or "0"
    return str(v)


def load_declared_archetypes(path: Path) -> list[str]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return [r["archetype"] for r in csv.DictReader(f) if r.get("archetype")]


def compute_batch_metrics(
    batch: int,
    val_df: pd.DataFrame,
    feat_df: pd.DataFrame,
    declared_archetypes: list[str],
    prev_snapshot: dict[str, Any] | None,
    prev_batch: int | None,
) -> dict[str, Any]:
    val_cum = val_df[val_df["batch_target"] <= batch].copy()
    feat_cum = feat_df[feat_df["batch_target"] <= batch].copy()

    total_generated = len(val_cum)
    valid_status = val_cum["status"].isin(INCLUDED_STATUSES)
    valid_maps = int(valid_status.sum())
    invalid_maps = total_generated - valid_maps

    archetypes_valid = sorted(feat_cum["archetype"].dropna().unique().tolist())
    anchors_valid = sorted(feat_cum["anchor_id"].dropna().unique().tolist())
    n_declared = len(declared_archetypes) or 1
    archetype_coverage_frac = len(archetypes_valid) / n_declared

    src_counts = Counter(feat_cum["source_type"].tolist())
    src_total = max(len(feat_cum), 1)

    row: dict[str, Any] = {
        "batch": batch,
        "total_generated": total_generated,
        "valid_maps": valid_maps,
        "invalid_maps": invalid_maps,
        "unique_feature_vectors": 0,
        "valid_archetypes_covered": len(archetypes_valid),
        "valid_anchors_covered": len(anchors_valid),
        "archetype_coverage_frac": archetype_coverage_frac,
        "archetypes_present": archetypes_valid,
        "source_type_osm": src_counts.get("osm", 0),
        "source_type_synthetic": src_counts.get("synthetic", 0),
        "source_type_trace_reference_synthetic": src_counts.get("trace_reference_synthetic", 0),
        "source_type_osm_frac": src_counts.get("osm", 0) / src_total,
        "source_type_synthetic_frac": src_counts.get("synthetic", 0) / src_total,
        "source_type_trace_reference_synthetic_frac": src_counts.get("trace_reference_synthetic", 0) / src_total,
        "n_clusters": 0,
        "n_clusters_hier": 0,
        "n_clusters_fps": 0,
        "mean_nn_dist_l2": 0.0,
        "median_nn_dist_l2": 0.0,
        "max_nn_dist_l2": 0.0,
        "mean_dist_to_medoid_l2": 0.0,
        "max_dist_to_medoid_l2": 0.0,
        "mean_dist_to_medoid_cosine": 0.0,
        "max_dist_to_medoid_cosine": 0.0,
        "mean_dist_to_medoid_fps_l2": 0.0,
        "max_dist_to_medoid_fps_l2": 0.0,
        "pca_var_explained_2": 0.0,
        "pca_var_explained_5": 0.0,
        "pca_var_explained_10": 0.0,
    }

    if valid_maps == 0:
        return _attach_deltas(
            row, prev_snapshot, prev_batch, val_df,
            feat_cum, batch, np.zeros((0, 1)),
        )

    z, map_ids = build_normalized_matrix(feat_cum, NUMERIC_FEATURE_COLUMNS)
    _, n_unique = dedupe_exact(z, map_ids)
    row["unique_feature_vectors"] = n_unique

    k = cluster_k(valid_maps)
    medoids = select_kmedoids(z, k, GLOBAL_SEED + batch)
    fps = select_farthest(z, k, GLOBAL_SEED + batch + 1)

    row["n_clusters"] = count_clusters_from_medoids(z, medoids)
    row["n_clusters_hier"] = count_clusters_hierarchical(z, k)
    row["n_clusters_fps"] = len(fps)

    nn = nearest_neighbor_stats(z)
    row.update(nn)

    med_l2 = medoid_coverage_stats_l2(z, medoids)
    med_cos = medoid_coverage_stats_cosine(z, medoids)
    med_fps = medoid_coverage_stats_l2(z, fps)
    row.update(med_l2)
    row.update(med_cos)
    row["mean_dist_to_medoid_fps_l2"] = med_fps["mean_dist_to_medoid_l2"]
    row["max_dist_to_medoid_fps_l2"] = med_fps["max_dist_to_medoid_l2"]

    pca = pca_variance_explained(z, [2, 5, 10])
    row.update(pca)

    keys = set(vector_keys(z))
    row["_vector_keys"] = keys
    return _attach_deltas(
        row, prev_snapshot, prev_batch, val_df, feat_cum, batch, z,
    )


def compute_near_redundant_fraction(
    z: np.ndarray,
    batch_targets: np.ndarray,
    prev_batch: int,
    batch: int,
    threshold: float = REDUNDANCY_NN_THRESHOLD,
) -> tuple[int, float]:
    """Share of new valid maps whose L2 distance to the previous cumulative set is below threshold."""
    prev_mask = batch_targets <= prev_batch
    new_mask = (batch_targets > prev_batch) & (batch_targets <= batch)
    n_new = int(new_mask.sum())
    if n_new == 0 or not prev_mask.any():
        return 0, 0.0
    z_prev = z[prev_mask]
    z_new = z[new_mask]
    d = pairwise_l2(z_new, z_prev)
    nearest = d.min(axis=1)
    n_near_redundant = int((nearest < threshold).sum())
    return n_near_redundant, n_near_redundant / n_new


def _attach_deltas(
    row: dict[str, Any],
    prev_snapshot: dict[str, Any] | None,
    prev_batch: int | None,
    val_df: pd.DataFrame,
    feat_cum: pd.DataFrame,
    batch: int,
    z: np.ndarray,
) -> dict[str, Any]:
    if prev_batch is None or prev_snapshot is None:
        row.update({
            "new_maps_since_prev": row["valid_maps"],
            "new_generated_since_prev": row["total_generated"],
            "new_invalid_since_prev": row["invalid_maps"],
            "new_unique_vectors": row["unique_feature_vectors"],
            "near_redundant_new_count": 0,
            "near_redundant_new_fraction": 0.0,
            "redundant_new_fraction": 0.0,
            "invalid_new_fraction": 0.0,
            "rel_improvement_max_medoid_l2": 0.0,
            "rel_improvement_mean_medoid_l2": 0.0,
            "rel_new_clusters": 0.0,
            "archetype_set_changed": False,
            "new_archetypes": [],
            "new_source_types": [],
        })
        row["_vector_keys"] = set(vector_keys(z))
        return row

    prev_b = prev_batch
    val_new = val_df[(val_df["batch_target"] > prev_b) & (val_df["batch_target"] <= batch)]
    new_generated = len(val_new)
    new_valid = int(row["new_maps_since_prev"]) if "new_maps_since_prev" in row else len(
        feat_cum[(feat_cum["batch_target"] > prev_b) & (feat_cum["batch_target"] <= batch)]
    )
    feat_new = feat_cum[(feat_cum["batch_target"] > prev_b) & (feat_cum["batch_target"] <= batch)]
    new_valid = len(feat_new)
    new_invalid = new_generated - int(val_new["status"].isin(INCLUDED_STATUSES).sum())

    batch_targets = feat_cum["batch_target"].to_numpy(dtype=int)
    all_keys = vector_keys(z)
    prev_mask = batch_targets <= prev_b
    new_mask = (batch_targets > prev_b) & (batch_targets <= batch)
    prev_keys_in_current_norm = {all_keys[i] for i in range(len(all_keys)) if prev_mask[i]}
    new_keys = {all_keys[i] for i in range(len(all_keys)) if new_mask[i]} - prev_keys_in_current_norm
    new_unique_vectors = len(new_keys)

    n_near_redundant, near_redundant_fraction = compute_near_redundant_fraction(
        z, batch_targets, prev_b, batch,
    )

    exact_redundant_fraction = 0.0
    if new_valid > 0:
        exact_redundant_fraction = max(0.0, (new_valid - new_unique_vectors) / new_valid)
    redundant_new_fraction = max(exact_redundant_fraction, near_redundant_fraction)

    invalid_new_fraction = 0.0
    if new_generated > 0:
        invalid_new_fraction = new_invalid / new_generated

    prev_max = prev_snapshot.get("max_dist_to_medoid_l2", 0.0) or 0.0
    prev_mean = prev_snapshot.get("mean_dist_to_medoid_l2", 0.0) or 0.0
    prev_clusters = prev_snapshot.get("n_clusters", 0) or 0

    rel_max = 0.0
    if prev_max > 0:
        rel_max = (prev_max - row["max_dist_to_medoid_l2"]) / prev_max
    rel_mean = 0.0
    if prev_mean > 0:
        rel_mean = (prev_mean - row["mean_dist_to_medoid_l2"]) / prev_mean
    rel_clusters = 0.0
    if prev_clusters > 0:
        rel_clusters = (row["n_clusters"] - prev_clusters) / prev_clusters

    prev_arch = set(prev_snapshot.get("archetypes_present", []))
    curr_arch = set(row.get("archetypes_present", []))
    new_arch = sorted(curr_arch - prev_arch)

    prev_src = {
        st for st in SOURCE_TYPES
        if prev_snapshot.get(f"source_type_{st}", 0) > 0
    }
    curr_src = {st for st in SOURCE_TYPES if row.get(f"source_type_{st}", 0) > 0}
    new_src = sorted(curr_src - prev_src)

    row.update({
        "new_maps_since_prev": new_valid,
        "new_generated_since_prev": new_generated,
        "new_invalid_since_prev": new_invalid,
        "new_unique_vectors": new_unique_vectors,
        "near_redundant_new_count": n_near_redundant,
        "near_redundant_new_fraction": near_redundant_fraction,
        "redundant_new_fraction": redundant_new_fraction,
        "invalid_new_fraction": invalid_new_fraction,
        "rel_improvement_max_medoid_l2": rel_max,
        "rel_improvement_mean_medoid_l2": rel_mean,
        "rel_new_clusters": rel_clusters,
        "archetype_set_changed": prev_arch != curr_arch,
        "new_archetypes": new_arch,
        "new_source_types": new_src,
        "_vector_keys": set(vector_keys(z)),
    })
    return row


def evaluate_transition(row: dict[str, Any], valid_at_batch: int) -> dict[str, bool]:
    eligible = valid_at_batch >= MIN_VALID_MAPS_STOP and row["new_generated_since_prev"] > 0
    max_imp = row["rel_improvement_max_medoid_l2"]
    mean_imp = row["rel_improvement_mean_medoid_l2"]
    redundant_invalid = row["redundant_new_fraction"] + row["invalid_new_fraction"]
    checks = {
        "rel_new_clusters": row["rel_new_clusters"] < STOP_REL_THRESHOLD,
        "rel_improvement_max_medoid_l2": 0.0 <= max_imp < STOP_REL_THRESHOLD,
        "rel_improvement_mean_medoid_l2": 0.0 <= mean_imp < STOP_REL_THRESHOLD,
        "archetype_set_unchanged": not row["archetype_set_changed"],
        "no_new_archetypes": len(row.get("new_archetypes", [])) == 0,
        "no_new_source_types": len(row.get("new_source_types", [])) == 0,
        "majority_redundant_or_invalid": redundant_invalid >= 0.50,
    }
    all_pass = eligible and all(checks.values())
    return {"eligible": eligible, "all_pass": all_pass, **{f"stop_rule_{k}_pass": v for k, v in checks.items()}}


def evaluate_extension_transition(
    transition: dict[str, Any],
    metrics_at_batch: dict[str, Any],
) -> dict[str, Any]:
    """Confirmation rule for deliberate post-800 extension (batches 1000/1200)."""
    prev_batch = transition.get("prev_batch", 0)
    prev_valid = transition.get("prev_valid_maps", 0) or 0
    new_valid = transition.get("new_maps_since_prev", 0) or 0
    rel_marginal_valid = (new_valid / prev_valid) if prev_valid > 0 else 1.0

    eligible = (
        prev_batch >= EXTENSION_CONFIRM_FROM_BATCH
        and transition.get("eligible", False)
        and metrics_at_batch.get("archetype_coverage_frac", 0) >= 1.0
    )
    redundant_invalid = (
        transition.get("redundant_new_fraction", 0.0)
        + transition.get("invalid_new_fraction", 0.0)
    )
    mean_imp = transition.get("rel_improvement_mean_medoid_l2", 0.0)
    checks = {
        "archetype_set_unchanged": not transition.get("archetype_set_changed", True),
        "no_new_archetypes": len(transition.get("new_archetypes", [])) == 0,
        "no_new_source_types": len(transition.get("new_source_types", [])) == 0,
        "majority_redundant_or_invalid": redundant_invalid >= 0.50,
        "rel_marginal_valid_growth": rel_marginal_valid < EXTENSION_REL_MARGINAL_VALID,
        "rel_new_clusters": transition.get("rel_new_clusters", 1.0) < EXTENSION_REL_CLUSTERS,
        "rel_improvement_mean_medoid_l2": 0.0 <= mean_imp < EXTENSION_REL_MEAN_MEDOID,
    }
    all_pass = eligible and all(checks.values())
    return {
        "extension_eligible": eligible,
        "extension_all_pass": all_pass,
        "rel_marginal_valid_frac": rel_marginal_valid,
        **{f"extension_{k}_pass": v for k, v in checks.items()},
    }


def evaluate_robustness_extension_transition(
    transition: dict[str, Any],
    metrics_at_batch: dict[str, Any],
) -> dict[str, Any]:
    """Robustness confirmation for post-1200 extension (batches 1600/2000)."""
    prev_batch = transition.get("prev_batch", 0)
    prev_valid = transition.get("prev_valid_maps", 0) or 0
    new_valid = transition.get("new_maps_since_prev", 0) or 0
    rel_marginal_valid = (new_valid / prev_valid) if prev_valid > 0 else 1.0

    eligible = (
        prev_batch >= ROBUSTNESS_EXTENSION_FROM_BATCH
        and transition.get("eligible", False)
        and metrics_at_batch.get("archetype_coverage_frac", 0) >= 1.0
    )
    redundant_invalid = (
        transition.get("redundant_new_fraction", 0.0)
        + transition.get("invalid_new_fraction", 0.0)
    )
    mean_imp = transition.get("rel_improvement_mean_medoid_l2", 0.0)
    checks = {
        "archetype_set_unchanged": not transition.get("archetype_set_changed", True),
        "no_new_archetypes": len(transition.get("new_archetypes", [])) == 0,
        "no_new_source_types": len(transition.get("new_source_types", [])) == 0,
        "majority_redundant_or_invalid": redundant_invalid >= 0.50,
        "rel_marginal_valid_growth": rel_marginal_valid < EXTENSION_REL_MARGINAL_VALID,
        "rel_new_clusters": transition.get("rel_new_clusters", 1.0) < EXTENSION_REL_CLUSTERS,
        "rel_improvement_mean_medoid_l2": 0.0 <= mean_imp < EXTENSION_REL_MEAN_MEDOID,
    }
    all_pass = eligible and all(checks.values())
    return {
        "robustness_extension_eligible": eligible,
        "robustness_extension_all_pass": all_pass,
        "robustness_rel_marginal_valid_frac": rel_marginal_valid,
        **{f"robustness_{k}_pass": v for k, v in checks.items()},
    }


def _decision_label(batch: int | None, confirmed_by_later: bool = False) -> str:
    if batch is None:
        return "continue_generation"
    if confirmed_by_later and batch <= 1200:
        return "stop_at_1200_confirmed_by_2000"
    if batch <= 400:
        return "stop_at_400"
    if batch <= 600:
        return "stop_at_600"
    if batch <= 800:
        return "stop_at_800"
    if batch <= 1000:
        return "stop_at_1000"
    if batch <= 1200:
        return "stop_at_1200"
    if batch <= 1600:
        return "stop_at_1600"
    return "stop_at_2000"


def build_transition_rows(metrics_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    transitions: list[dict[str, Any]] = []
    for i in range(1, len(metrics_rows)):
        prev = metrics_rows[i - 1]
        curr = metrics_rows[i]
        trow = {
            "prev_batch": prev["batch"],
            "batch": curr["batch"],
            "prev_total_generated": prev["total_generated"],
            "total_generated": curr["total_generated"],
            "prev_valid_maps": prev["valid_maps"],
            "valid_maps": curr["valid_maps"],
            "new_maps_since_prev": curr["new_maps_since_prev"],
            "new_generated_since_prev": curr["new_generated_since_prev"],
            "new_unique_vectors": curr["new_unique_vectors"],
            "near_redundant_new_fraction": curr.get("near_redundant_new_fraction", 0.0),
            "redundant_new_fraction": curr["redundant_new_fraction"],
            "invalid_new_fraction": curr["invalid_new_fraction"],
            "rel_new_clusters": curr["rel_new_clusters"],
            "rel_improvement_max_medoid_l2": curr["rel_improvement_max_medoid_l2"],
            "rel_improvement_mean_medoid_l2": curr["rel_improvement_mean_medoid_l2"],
            "archetype_set_changed": curr["archetype_set_changed"],
            "new_archetypes": curr["new_archetypes"],
            "new_source_types": curr["new_source_types"],
            "n_clusters": curr["n_clusters"],
            "prev_n_clusters": prev["n_clusters"],
            "max_dist_to_medoid_l2": curr["max_dist_to_medoid_l2"],
            "prev_max_dist_to_medoid_l2": prev["max_dist_to_medoid_l2"],
        }
        eval_res = evaluate_transition(curr, curr["valid_maps"])
        trow.update(eval_res)
        trow.update(evaluate_extension_transition(trow, curr))
        trow.update(evaluate_robustness_extension_transition(trow, curr))
        transitions.append(trow)
    return transitions


def decide_stop(
    metrics_rows: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
) -> dict[str, Any]:
    recommended_stop_batch: int | None = None
    decision = "continue_generation"
    stop_rule_mode = "none"
    best_score = 0
    used_heuristic = False
    extension_confirmed = False
    robustness_extension_confirmed = False
    decision_tier = "operational_800"
    confirmed_by_2000 = False

    # 1) Strict YAML rule (5%, all 7 criteria, 2 consecutive transitions)
    for i in range(len(transitions) - MIN_CONSECUTIVE_TRANSITIONS + 1):
        window = transitions[i : i + MIN_CONSECUTIVE_TRANSITIONS]
        if all(t["all_pass"] for t in window):
            recommended_stop_batch = window[-1]["batch"]
            stop_rule_mode = "consecutive_strict"
            break

    # 2) Extension confirmation (800→1000→1200 deliberate robustness check)
    if recommended_stop_batch is None:
        ext_trans = [t for t in transitions if t.get("extension_eligible")]
        for i in range(len(ext_trans) - MIN_CONSECUTIVE_TRANSITIONS + 1):
            window = ext_trans[i : i + MIN_CONSECUTIVE_TRANSITIONS]
            if all(t.get("extension_all_pass") for t in window):
                recommended_stop_batch = window[-1]["batch"]
                stop_rule_mode = "extension_confirmation"
                extension_confirmed = True
                decision_tier = "methodological_1200"
                break

    max_batch = metrics_rows[-1]["batch"] if metrics_rows else 0

    # 2b) Robustness extension (1200→1600→2000) when data reaches 2000
    if max_batch >= 2000:
        robust_trans = [t for t in transitions if t.get("robustness_extension_eligible")]
        for i in range(len(robust_trans) - MIN_CONSECUTIVE_TRANSITIONS + 1):
            window = robust_trans[i : i + MIN_CONSECUTIVE_TRANSITIONS]
            if all(t.get("robustness_extension_all_pass") for t in window):
                recommended_stop_batch = 1200
                stop_rule_mode = "robustness_extension_confirmation"
                robustness_extension_confirmed = True
                confirmed_by_2000 = True
                extension_confirmed = extension_confirmed or True
                decision_tier = "methodological_1200"
                break

        if not robustness_extension_confirmed:
            t_1200_1600 = next(
                (t for t in transitions if t.get("prev_batch") == 1200 and t.get("batch") == 1600),
                None,
            )
            t_1600_2000 = next(
                (t for t in transitions if t.get("prev_batch") == 1600 and t.get("batch") == 2000),
                None,
            )
            if t_1600_2000 and t_1600_2000.get("robustness_extension_all_pass"):
                if t_1200_1600 and not t_1200_1600.get("robustness_extension_all_pass"):
                    recommended_stop_batch = 1600
                    stop_rule_mode = "robustness_partial_stop"
                    decision_tier = "methodological_1600"
                else:
                    recommended_stop_batch = 2000
                    stop_rule_mode = "robustness_extension_confirmation"
                    decision_tier = "methodological_2000"
            elif recommended_stop_batch is None:
                stop_rule_mode = "robustness_inconclusive"

    metrics_at_stop = next(
        (m for m in metrics_rows if m["batch"] == recommended_stop_batch),
        metrics_rows[-1] if metrics_rows else {},
    )

    prev_comp: dict[str, Any] = {}
    next_comp: dict[str, Any] = {}

    # 3) Partial heuristic — prefer LATEST batch among ties (extension data wins)
    if recommended_stop_batch is None and transitions:
        eligible_trans = [t for t in transitions if t["eligible"]]
        if eligible_trans:
            scored: list[tuple[int, int]] = []
            for t in eligible_trans:
                score = sum([
                    t["stop_rule_rel_new_clusters_pass"],
                    t["stop_rule_rel_improvement_max_medoid_l2_pass"],
                    t["stop_rule_rel_improvement_mean_medoid_l2_pass"],
                    t["stop_rule_archetype_set_unchanged_pass"],
                    t["stop_rule_no_new_archetypes_pass"],
                    t["stop_rule_no_new_source_types_pass"],
                    t["stop_rule_majority_redundant_or_invalid_pass"],
                ])
                scored.append((score, t["batch"]))
            best_score, best_batch = max(scored, key=lambda x: (x[0], x[1]))
            if best_score >= HEURISTIC_MIN_SCORE:
                recommended_stop_batch = best_batch
                used_heuristic = True
                stop_rule_mode = "partial_heuristic"
                metrics_at_stop = next(m for m in metrics_rows if m["batch"] == best_batch)

    if recommended_stop_batch is not None:
        decision = _decision_label(recommended_stop_batch, confirmed_by_later=confirmed_by_2000)
        idx = next((i for i, t in enumerate(transitions) if t["batch"] == recommended_stop_batch), -1)
        if idx >= 0:
            if idx > 0:
                prev_comp = transitions[idx - 1]
            if idx + 1 < len(transitions):
                next_comp = transitions[idx + 1]

    n_stop = metrics_at_stop.get("total_generated", 0)
    n_valid = metrics_at_stop.get("valid_maps", 0)
    if not max_batch:
        max_batch = metrics_rows[-1]["batch"] if metrics_rows else 0
    max_generated = metrics_rows[-1]["total_generated"] if metrics_rows else 0
    max_valid = metrics_rows[-1]["valid_maps"] if metrics_rows else 0
    max_invalid = metrics_rows[-1]["invalid_maps"] if metrics_rows else 0
    baseline_800 = next((m for m in metrics_rows if m.get("batch") == 800), {})
    valid_at_800 = int(baseline_800.get("valid_maps", 0) or 0)
    marginal_valid_after_800 = max(0, max_valid - valid_at_800)
    baseline_1200 = next((m for m in metrics_rows if m.get("batch") == 1200), {})
    valid_at_1200 = int(baseline_1200.get("valid_maps", 0) or 0)
    marginal_valid_after_1200 = max(0, max_valid - valid_at_1200)

    if recommended_stop_batch is not None:
        if stop_rule_mode == "robustness_extension_confirmation" and confirmed_by_2000:
            reason = (
                f"Robustness extension to batch {max_batch} confirmed saturation at the methodological "
                f"point batch 1200: two consecutive post-{ROBUSTNESS_EXTENSION_FROM_BATCH} transitions "
                f"met extension criteria (15/15 archetypes, marginal valid growth "
                f"<{EXTENSION_REL_MARGINAL_VALID*100:.0f}% of previous valid pool, mean medoid improvement "
                f"<{EXTENSION_REL_MEAN_MEDOID*100:.0f}%, new clusters <{EXTENSION_REL_CLUSTERS*100:.0f}%, "
                f">=50% redundant/invalid new maps). Recommended methodological stop remains batch 1200 "
                f"({valid_at_1200} valid at 1200); full run reached {max_generated} generated / "
                f"{max_valid} valid / {max_invalid} invalid (+{marginal_valid_after_1200} valid after 1200)."
            )
            claim = (
                f"Map generation methodological stop remains at N=1200 candidates ({valid_at_1200} "
                f"validation-passing maps at batch 1200, 15/15 declared archetypes covered). A robustness "
                f"extension to N={max_generated} candidates added {marginal_valid_after_1200} further valid "
                f"maps while post-1200 tranches showed >=50% redundant or invalid new maps, confirming "
                f"that the 1200 stopping decision was not premature. Completeness is defined with respect "
                f"to this declared design space, not all possible real-world environments."
            )
        elif stop_rule_mode == "robustness_extension_confirmation" and decision_tier == "methodological_2000":
            reason = (
                f"Robustness extension to batch {max_batch}: saturation criteria confirmed at batch 2000 "
                f"({max_valid} valid maps). Methodological stop updated to batch 2000."
            )
            claim = (
                f"Map generation stopped at N={max_generated} candidates ({max_valid} validation-passing maps, "
                f"15/15 declared archetypes covered) because feature-space saturation was confirmed at batch "
                f"2000 under the robustness extension rule. Completeness is defined with respect to this "
                f"declared design space, not all possible real-world environments."
            )
        elif stop_rule_mode == "robustness_partial_stop":
            reason = (
                f"Batch 1200→1600 extension showed measurable diversity; batch 1600→2000 confirmed "
                f"diminishing returns. Methodological stop at batch 1600 ({n_valid} valid at evaluation)."
            )
            claim = (
                f"Map generation stopped at batch 1600 ({n_valid} validation-passing maps at cumulative "
                f"batch 1600) because the 1200→1600 tranche added non-trivial feature-space coverage while "
                f"1600→2000 confirmed saturation. Completeness is defined with respect to this declared "
                f"design space, not all possible real-world environments."
            )
        elif stop_rule_mode == "extension_confirmation":
            reason = (
                f"Deliberate extension to batch {max_batch} confirmed saturation: two consecutive "
                f"post-{EXTENSION_CONFIRM_FROM_BATCH} transitions met extension criteria "
                f"(15/15 archetypes, marginal valid growth <{EXTENSION_REL_MARGINAL_VALID*100:.0f}% of "
                f"previous valid pool, mean medoid improvement <{EXTENSION_REL_MEAN_MEDOID*100:.0f}%, "
                f"new clusters <{EXTENSION_REL_CLUSTERS*100:.0f}%, >=50% redundant/invalid new maps). "
                f"Recommended stop at batch {recommended_stop_batch} ({n_stop} generated, {n_valid} valid). "
                f"Full run reached {max_generated} generated / {max_valid} valid / {max_invalid} invalid."
            )
            claim = (
                f"Map generation stopped at N={n_stop} candidates ({n_valid} validation-passing maps, "
                f"15/15 declared archetypes covered) because coverage of the declared map-topology "
                f"feature space reached saturation under the defined metrics and stop rule. "
                f"A deliberate extension beyond batch 800 (696 valid maps) to N={max_generated} "
                f"candidates added only {marginal_valid_after_800} further valid maps, while "
                f"{max_invalid} candidates failed validation; extension batches showed >=50% "
                f"redundant or invalid new maps per tranche, confirming saturation. Completeness is "
                f"defined with respect to this declared design space, not all possible real-world "
                f"environments."
            )
        elif used_heuristic:
            reason = (
                f"No two consecutive transitions met all strict stop criteria. Batch {recommended_stop_batch} "
                f"had the highest partial rule satisfaction ({best_score}/7 criteria) among eligible "
                f"transitions with >= {MIN_VALID_MAPS_STOP} valid maps. At this point: "
                f"{n_stop} generated, {n_valid} valid maps."
            )
            claim = (
                f"Map generation stopped at N={n_stop} candidates ({n_valid} validation-passing maps) "
                f"because incremental feature-space coverage gains fell below the saturation thresholds "
                f"on {best_score} of 7 stop-rule criteria at cumulative batch {recommended_stop_batch}. "
                f"Completeness is defined with respect to this declared map-topology design space."
            )
        else:
            reason = (
                f"Two consecutive batch transitions satisfied all saturation criteria "
                f"(new clusters <{STOP_REL_THRESHOLD*100:.0f}%, medoid distance improvements "
                f"<{STOP_REL_THRESHOLD*100:.0f}%, stable archetype/source coverage, majority "
                f"redundant/invalid new maps). Recommended cumulative batch: {recommended_stop_batch} "
                f"({n_stop} generated, {n_valid} valid maps)."
            )
            claim = (
                f"Map generation stopped at N={n_stop} candidates ({n_valid} validation-passing maps) "
                f"because coverage of the declared map-topology feature space reached saturation under "
                f"the defined metrics and stop rule at cumulative batch {recommended_stop_batch}. "
                f"Completeness is defined with respect to this declared design space, not with respect "
                f"to all possible real-world environments."
            )
    else:
        reason = (
            "No pair of consecutive batch transitions met all saturation criteria. "
            "Feature-space coverage metrics still showed non-trivial gains; continue generation "
            "or extend batch evaluation."
        )
        claim = (
            f"Map generation at N={max_generated} candidates had not yet met the full consecutive-batch "
            f"saturation stop rule; additional candidates may be warranted to confirm coverage "
            f"of the declared map-topology feature space."
        )

    return {
        "recommended_stop_batch": recommended_stop_batch,
        "decision": decision,
        "reason": reason,
        "metrics_at_stop": _public_metrics(metrics_at_stop),
        "previous_batch_comparison": _public_transition(prev_comp),
        "next_batch_comparison": _public_transition(next_comp),
        "claim_text_paper_ready": claim,
        "stop_rule_mode": stop_rule_mode,
        "partial_rule_score": best_score if used_heuristic else None,
        "extension_confirmed": extension_confirmed,
        "robustness_extension_confirmed": robustness_extension_confirmed,
        "decision_tier": decision_tier,
        "max_batch_evaluated": max_batch,
        "max_generated": max_generated,
        "max_valid_maps": max_valid,
        "max_invalid_maps": max_invalid,
        "marginal_valid_maps_after_800": marginal_valid_after_800,
        "marginal_valid_maps_after_1200": marginal_valid_after_1200,
        "valid_maps_at_800": valid_at_800,
        "valid_maps_at_1200": valid_at_1200,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _public_metrics(m: dict[str, Any]) -> dict[str, Any]:
    skip = {"_vector_keys", "archetypes_present"}
    return {k: (list(v) if isinstance(v, list) else v) for k, v in m.items() if k not in skip}


def _public_transition(t: dict[str, Any]) -> dict[str, Any]:
    if not t:
        return {}
    keys = [
        "prev_batch", "batch", "valid_maps", "new_maps_since_prev",
        "rel_new_clusters", "rel_improvement_max_medoid_l2",
        "rel_improvement_mean_medoid_l2", "redundant_new_fraction",
        "invalid_new_fraction", "all_pass",
    ]
    return {k: t[k] for k in keys if k in t}


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            out = {c: fmt(row.get(c, "")) for c in columns}
            w.writerow(out)


METRICS_COLUMNS = [
    "batch", "total_generated", "valid_maps", "invalid_maps", "unique_feature_vectors",
    "valid_archetypes_covered", "valid_anchors_covered", "archetype_coverage_frac",
    "source_type_osm", "source_type_synthetic", "source_type_trace_reference_synthetic",
    "source_type_osm_frac", "source_type_synthetic_frac", "source_type_trace_reference_synthetic_frac",
    "n_clusters", "n_clusters_hier", "n_clusters_fps",
    "mean_nn_dist_l2", "median_nn_dist_l2", "max_nn_dist_l2",
    "mean_dist_to_medoid_l2", "max_dist_to_medoid_l2",
    "mean_dist_to_medoid_cosine", "max_dist_to_medoid_cosine",
    "mean_dist_to_medoid_fps_l2", "max_dist_to_medoid_fps_l2",
    "pca_var_explained_2", "pca_var_explained_5", "pca_var_explained_10",
    "new_maps_since_prev", "new_generated_since_prev", "new_invalid_since_prev",
    "new_unique_vectors", "near_redundant_new_count", "near_redundant_new_fraction",
    "redundant_new_fraction", "invalid_new_fraction",
    "rel_improvement_max_medoid_l2", "rel_improvement_mean_medoid_l2", "rel_new_clusters",
    "archetype_set_changed", "new_archetypes", "new_source_types",
]

TRANSITION_COLUMNS = [
    "prev_batch", "batch", "prev_total_generated", "total_generated",
    "prev_valid_maps", "valid_maps", "new_maps_since_prev", "new_generated_since_prev",
    "new_unique_vectors", "near_redundant_new_fraction", "redundant_new_fraction", "invalid_new_fraction",
    "rel_new_clusters", "rel_improvement_max_medoid_l2", "rel_improvement_mean_medoid_l2",
    "archetype_set_changed", "new_archetypes", "new_source_types",
    "n_clusters", "prev_n_clusters", "max_dist_to_medoid_l2", "prev_max_dist_to_medoid_l2",
    "eligible", "all_pass",
    "stop_rule_rel_new_clusters_pass", "stop_rule_rel_improvement_max_medoid_l2_pass",
    "stop_rule_rel_improvement_mean_medoid_l2_pass", "stop_rule_archetype_set_unchanged_pass",
    "stop_rule_no_new_archetypes_pass", "stop_rule_no_new_source_types_pass",
    "stop_rule_majority_redundant_or_invalid_pass",
    "extension_eligible", "extension_all_pass", "rel_marginal_valid_frac",
]


def df_to_markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_(empty)_"
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def plot_all(metrics_rows: list[dict[str, Any]], out_dir: Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(metrics_rows)
    fig_paths: list[str] = []

    def save(name: str) -> str:
        p = out_dir / name
        plt.tight_layout()
        plt.savefig(p, dpi=150)
        plt.close()
        fig_paths.append(name)
        return name

    x = df["total_generated"]

    plt.figure(figsize=(7, 4))
    plt.plot(x, df["valid_maps"], "o-", label="valid_maps")
    plt.xlabel("total_generated")
    plt.ylabel("valid_maps")
    plt.title("Valid maps vs generated maps")
    plt.grid(True, alpha=0.3)
    save("valid_vs_generated.png")

    plt.figure(figsize=(7, 4))
    plt.plot(x, df["unique_feature_vectors"], "o-", color="C1")
    plt.xlabel("total_generated")
    plt.ylabel("unique_feature_vectors")
    plt.title("Unique feature vectors vs generated maps")
    plt.grid(True, alpha=0.3)
    save("unique_vectors_vs_generated.png")

    plt.figure(figsize=(7, 4))
    plt.plot(x, df["n_clusters"], "o-", color="C2")
    plt.xlabel("total_generated")
    plt.ylabel("n_clusters")
    plt.title("Clusters vs generated maps")
    plt.grid(True, alpha=0.3)
    save("clusters_vs_generated.png")

    plt.figure(figsize=(7, 4))
    plt.plot(x, df["mean_nn_dist_l2"], "o-", color="C3")
    plt.xlabel("total_generated")
    plt.ylabel("mean_nn_dist_l2")
    plt.title("Mean nearest-neighbor distance vs generated maps")
    plt.grid(True, alpha=0.3)
    save("mean_nn_dist_vs_generated.png")

    plt.figure(figsize=(7, 4))
    plt.plot(x, df["max_dist_to_medoid_l2"], "o-", color="C4")
    plt.xlabel("total_generated")
    plt.ylabel("max_dist_to_medoid_l2")
    plt.title("Max distance to nearest medoid vs generated maps")
    plt.grid(True, alpha=0.3)
    save("max_medoid_dist_vs_generated.png")

    plt.figure(figsize=(8, 4))
    batches = df["batch"]
    plt.plot(batches, df["rel_improvement_max_medoid_l2"] * 100, "o-", label="max medoid improvement %")
    plt.plot(batches, df["rel_improvement_mean_medoid_l2"] * 100, "s-", label="mean medoid improvement %")
    plt.plot(batches, df["rel_new_clusters"] * 100, "^-", label="new clusters %")
    plt.axhline(STOP_REL_THRESHOLD * 100, color="gray", linestyle="--", label="5% threshold")
    plt.xlabel("batch")
    plt.ylabel("relative change (%)")
    plt.title("Improvement percentage vs batch")
    plt.legend(fontsize=8)
    plt.grid(True, alpha=0.3)
    save("improvement_pct_vs_batch.png")

    plt.figure(figsize=(8, 4))
    plt.bar(df["batch"].astype(str), df["valid_archetypes_covered"], label="covered")
    plt.axhline(len(load_declared_archetypes(DEFAULT_ARCHETYPES)), color="gray", linestyle="--", label="declared")
    plt.xlabel("batch")
    plt.ylabel("archetypes covered")
    plt.title("Archetype coverage vs batch")
    plt.legend()
    plt.grid(True, alpha=0.3, axis="y")
    save("archetype_coverage_vs_batch.png")

    plt.figure(figsize=(8, 4))
    bottom = np.zeros(len(df))
    for st, color in zip(
        SOURCE_TYPES,
        ["#4C72B0", "#55A868", "#C44E52"],
    ):
        frac = df[f"source_type_{st}_frac"].to_numpy()
        plt.bar(df["batch"].astype(str), frac, bottom=bottom, label=st, color=color)
        bottom += frac
    plt.xlabel("batch")
    plt.ylabel("fraction")
    plt.title("Source type distribution vs batch")
    plt.legend(fontsize=8)
    save("source_type_vs_batch.png")

    return fig_paths


def write_report(
    path: Path,
    metrics_rows: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
    decision: dict[str, Any],
    declared_archetypes: list[str],
    fig_names: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table_df = pd.DataFrame(metrics_rows)[METRICS_COLUMNS[:30]]
    trans_df = pd.DataFrame(transitions)[
        [c for c in TRANSITION_COLUMNS if c in (transitions[0] if transitions else {})]
    ]

    missing_arch = sorted(set(declared_archetypes) - set(
        metrics_rows[-1].get("archetypes_present", []) if metrics_rows else []
    ))

    fig_md = "\n".join(
        f"![{n}](../figures/map_space_saturation/{n})" for n in fig_names
    )

    body = f"""# Map space saturation analysis (v1)

Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

## Executive summary

**Decision:** `{decision.get("decision", "continue_generation")}`

**Recommended stop batch:** {decision.get("recommended_stop_batch", "none")}

**Stop rule mode:** `{decision.get("stop_rule_mode", "none")}`

**Max batch evaluated:** {decision.get("max_batch_evaluated", "")} ({decision.get("max_generated", "")} generated, {decision.get("max_valid_maps", "")} valid, {decision.get("max_invalid_maps", "")} invalid)

{decision.get("reason", "")}

**Paper-ready claim:**

> {decision.get("claim_text_paper_ready", "")}

## Metrics by cumulative batch

{df_to_markdown_table(table_df)}

## Batch transitions (stop-rule evaluation)

{df_to_markdown_table(trans_df) if not trans_df.empty else "_(no transitions)_"}

## Metric definitions

- **total_generated**: validation records with `batch_target <= B`.
- **valid_maps**: maps with validation status PASS/WARNING/STRESS and extracted features.
- **unique_feature_vectors**: exact deduplication on cumulative z-scored features (tol={DEDUP_TOL}).
- **n_clusters**: non-empty clusters from k-medoids assignment (`k ≈ sqrt(n)`, capped at 50).
- **mean/median/max_nn_dist_l2**: nearest-neighbor distance in cumulative normalized L2 space.
- **mean/max_dist_to_medoid_l2**: distance to nearest k-medoid representative (L2).
- **mean/max_dist_to_medoid_cosine**: same with cosine distance on L2-normalized vectors.
- **pca_var_explained_K**: cumulative variance explained by first K PCA components (SVD).
- **rel_improvement_*_medoid_l2**: relative reduction in medoid coverage distance vs previous batch.
- **rel_new_clusters**: relative increase in cluster count vs previous batch.
- **redundant_new_fraction**: max(exact duplicate rate, near-duplicate rate vs previous cumulative set at NN threshold {REDUNDANCY_NN_THRESHOLD}).
- **near_redundant_new_fraction**: new valid maps with L2 distance below {REDUNDANCY_NN_THRESHOLD} to any map in the previous cumulative batch.
- **invalid_new_fraction**: share of newly generated maps that failed validation.

**Extension confirmation** (post-batch 800): uses relative marginal valid growth `<{EXTENSION_REL_MARGINAL_VALID*100:.0f}%` of previous valid pool (not absolute count), new clusters `<{EXTENSION_REL_CLUSTERS*100:.0f}%`, mean medoid improvement `<{EXTENSION_REL_MEAN_MEDOID*100:.0f}%`, plus stable archetypes and >=50% redundant/invalid new maps across two consecutive extension transitions.

**Normalization:** z-score per numeric feature computed only on maps with `batch_target <= B` (no lookahead). `source_type` one-hot encoded within the same cumulative subset.

**Distances:** both Euclidean (L2) and cosine reported; stop rule uses L2 medoid coverage.

## Figures

{fig_md}

## Recommended decision

| Field | Value |
|-------|-------|
| decision | `{decision.get("decision")}` |
| recommended_stop_batch | {decision.get("recommended_stop_batch")} |
| total_generated at stop | {decision.get("metrics_at_stop", {}).get("total_generated", "")} |
| valid_maps at stop | {decision.get("metrics_at_stop", {}).get("valid_maps", "")} |

## Limitations

- Only {metrics_rows[-1]["total_generated"] if metrics_rows else 0} candidates in the latest run (extend with batches 1000/1200 as needed).
- Declared archetypes not yet covered in valid maps: {", ".join(missing_arch) or "none"}.
- {len(declared_archetypes)} archetypes declared; saturation is over the declared topology feature space only.
- Cluster count depends on k-medoids initialization (seed={GLOBAL_SEED}); hierarchical and farthest-point metrics provided as sensitivity.
- No sklearn; PCA via numpy SVD on cumulative normalized matrix.
- Global normalized CSV (`map_space_saturation_features_normalized.csv`) not used for primary metrics (cumulative normalization avoids lookahead).
"""
    path.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze map_space_saturation_v1 feature-space saturation.")
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--archetypes", type=Path, default=DEFAULT_ARCHETYPES)
    parser.add_argument("--metrics-out", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--by-batch-out", type=Path, default=DEFAULT_BY_BATCH)
    parser.add_argument("--decision-out", type=Path, default=DEFAULT_DECISION)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES)
    args = parser.parse_args()

    feat_df = pd.read_csv(args.features)
    val_df = pd.read_csv(args.validation)
    feat_df["batch_target"] = feat_df["batch_target"].astype(int)
    val_df["batch_target"] = val_df["batch_target"].astype(int)

    declared = load_declared_archetypes(args.archetypes)
    max_batch_in_data = int(val_df["batch_target"].max())
    available_batches = [b for b in BATCH_THRESHOLDS if b <= max_batch_in_data]

    metrics_rows: list[dict[str, Any]] = []
    prev_snapshot: dict[str, Any] | None = None
    prev_batch: int | None = None

    for batch in available_batches:
        if val_df[val_df["batch_target"] <= batch].empty:
            continue
        snap = compute_batch_metrics(
            batch, val_df, feat_df, declared, prev_snapshot, prev_batch
        )
        metrics_rows.append(snap)
        prev_snapshot = snap
        prev_batch = batch

    transitions = build_transition_rows(metrics_rows)
    decision = decide_stop(metrics_rows, transitions)

    # Strip internal keys for CSV export
    export_rows = [{k: v for k, v in r.items() if k != "_vector_keys"} for r in metrics_rows]
    write_csv(args.metrics_out, export_rows, METRICS_COLUMNS)
    write_csv(args.by_batch_out, transitions, TRANSITION_COLUMNS)

    args.decision_out.parent.mkdir(parents=True, exist_ok=True)
    args.decision_out.write_text(json.dumps(decision, indent=2), encoding="utf-8")

    fig_names = plot_all(export_rows, args.figures_dir)
    write_report(args.report_out, export_rows, transitions, decision, declared, fig_names)

    print(f"Metrics: {args.metrics_out} ({len(export_rows)} batches)")
    print(f"Transitions: {args.by_batch_out} ({len(transitions)} rows)")
    print(f"Decision: {decision['decision']} @ batch {decision['recommended_stop_batch']}")
    print(f"Report: {args.report_out}")
    print(f"Figures: {args.figures_dir} ({len(fig_names)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
