#!/usr/bin/env python3
"""
prune_map_space_v1.py — Select a diverse subset of map_space_v1 candidates by topology features.

Usage:
    scenarios/analysis/.venv/bin/python scenarios/setup/prune_map_space_v1.py
    scenarios/analysis/.venv/bin/python scenarios/setup/prune_map_space_v1.py --compare-all
    scenarios/analysis/.venv/bin/python scenarios/setup/prune_map_space_v1.py --method kmedoids --target-n 60 --seed 42
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_space_topology import discover_maps  # noqa: E402

SCENARIOS_DIR = _SETUP.parent
MAP_SPACE_ROOT = SCENARIOS_DIR / "map_space_v1"
DEFAULT_FEATURES = SCENARIOS_DIR / "analysis" / "data" / "map_space_v1_features.csv"
DEFAULT_VALIDATION = SCENARIOS_DIR / "analysis" / "data" / "map_space_v1_validation.csv"
DEFAULT_MANIFEST = MAP_SPACE_ROOT / "manifest_maps.csv"
DEFAULT_OUT = MAP_SPACE_ROOT / "selected_maps"
METHODOLOGY_REPORT = SCENARIOS_DIR / "analysis" / "reports" / "map_space_v1_pruning_methodology.md"
SELECTED_REPORT = SCENARIOS_DIR / "analysis" / "reports" / "map_space_v1_selected_maps.md"

VALID_CLASSES = {"valid", "valid_partitioned", "stress"}

TOPOLOGY_V1_FEATURES = [
    "n_nodes", "n_edges", "total_road_length_m", "road_density", "world_area",
    "useful_area", "useful_area_ratio", "avg_degree", "max_degree", "dead_end_ratio",
    "n_components", "largest_component_ratio", "bridge_edges", "articulation_points",
    "orientation_entropy", "gridness_score", "corridor_score", "radial_score",
    "partition_score", "graph_diameter_approx", "avg_shortest_path_approx", "circuity_approx",
]

TOPOLOGY_V1_OPTIONAL = ["community_score"]

COVERAGE_CELLS: dict[str, list[str]] = {
    "dense_urban": ["dense_urban_irregular"],
    "grid": ["urban_grid", "grid", "jittered_grid", "disrupted_grid"],
    "campus": ["campus_compact"],
    "rural": ["rural_roads", "sparse_rural", "suburban_low_density"],
    "sparse_trails": ["sparse_trails", "tree_trails"],
    "corridor": ["corridor_linear", "corridor"],
    "radial": ["radial_city"],
    "hub_and_spoke": ["hub_and_spoke"],
    "partitioned": ["island_or_partitioned", "partitioned_bridge", "multi_component_with_bridges"],
    "disrupted": ["industrial_disrupted", "disrupted_grid"],
    "clustered_communities": ["clustered_communities"],
}

ALL_METHODS = ("strict", "kmedoids", "cluster_medoids", "farthest", "clustering", "epsilon-cover")
COMPARE_METHODS = ("strict", "kmedoids", "farthest", "epsilon-cover")
METHOD_ALIASES = {"cluster_medoids": "kmedoids", "epsilon_cover": "epsilon-cover"}
DEDUP_TOL = 1e-9

ANCHOR_QUOTAS: dict[str, int] = {
    "helsinki_downtown": 1,
    "kumpula_campus": 1,
    "manhattan_midtown": 1,
    "sf_cabspotting_downtown": 1,
    "dieselnet_amherst": 1,
    "cambridge_haggle": 1,
    "infocom_event_compact": 1,
    "nuuksio_sparse_trails": 1,
}


def df_to_markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_(empty)_"
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def feature_columns(feature_set: str, df: pd.DataFrame | None = None) -> list[str]:
    if feature_set in ("topology_v1", "map_topology_v1"):
        cols = list(TOPOLOGY_V1_FEATURES)
        if df is not None:
            for c in TOPOLOGY_V1_OPTIONAL:
                if c in df.columns:
                    cols.append(c)
        return cols
    raise ValueError(f"Unknown feature set: {feature_set}")


def zscore_matrix(X: np.ndarray, feature_names: list[str]) -> tuple[np.ndarray, pd.DataFrame]:
    mu = X.mean(axis=0)
    sigma = X.std(axis=0, ddof=0)
    sigma_safe = np.where(sigma < 1e-12, 1.0, sigma)
    Z = (X - mu) / sigma_safe
    Z[:, sigma < 1e-12] = 0.0
    params = pd.DataFrame({"feature": feature_names, "mean": mu, "std": sigma})
    return Z, params


def pairwise_l2(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """L2 distance from each row of a (n×d) to each row of b (m×d) → (n,m)."""
    if b.size == 0:
        return np.zeros((a.shape[0], 0))
    aa = np.sum(a * a, axis=1, keepdims=True)
    bb = np.sum(b * b, axis=1, keepdims=True).T
    ab = a @ b.T
    d2 = np.maximum(aa + bb - 2.0 * ab, 0.0)
    return np.sqrt(d2)


def dist_to_set(points: np.ndarray, selected: np.ndarray) -> np.ndarray:
    """Min L2 distance from each point to nearest selected (length n)."""
    if selected.size == 0:
        return np.full(points.shape[0], np.inf)
    d = pairwise_l2(points, selected)
    return d.min(axis=1)


def dedupe_exact(Z: np.ndarray, map_ids: list[str]) -> tuple[np.ndarray, list[dict[str, str]]]:
    rounded = np.round(Z / DEDUP_TOL).astype(np.int64)
    seen: dict[tuple[int, ...], int] = {}
    unique_idx: list[int] = []
    dup_groups: list[dict[str, str]] = []
    order = sorted(range(len(map_ids)), key=lambda i: map_ids[i])
    for i in order:
        key = tuple(rounded[i].tolist())
        if key in seen:
            rep = unique_idx[seen[key]]
            dup_groups.append({
                "duplicate_map_id": map_ids[i],
                "representative_map_id": map_ids[rep],
            })
        else:
            seen[key] = len(unique_idx)
            unique_idx.append(i)
    return np.array(unique_idx, dtype=int), dup_groups


def kmeans_pp_init(Z: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    n = Z.shape[0]
    if k >= n:
        return np.arange(n, dtype=int)
    centers = [int(rng.integers(0, n))]
    for _ in range(1, k):
        pts = Z[centers]
        d = dist_to_set(Z, pts)
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


def select_farthest(Z: np.ndarray, k: int, seed: int) -> np.ndarray:
    n = Z.shape[0]
    k = min(k, n)
    if k <= 0:
        return np.array([], dtype=int)
    if k >= n:
        return np.arange(n, dtype=int)
    rng = np.random.default_rng(seed)
    selected = [int(rng.integers(0, n))]
    while len(selected) < k:
        sel_pts = Z[selected]
        d = dist_to_set(Z, sel_pts)
        for idx in selected:
            d[idx] = -1.0
        next_i = int(np.argmax(d))
        selected.append(next_i)
    return np.array(selected, dtype=int)


def select_kmedoids(Z: np.ndarray, k: int, seed: int, max_iter: int = 50) -> np.ndarray:
    n, _ = Z.shape
    k = min(k, n)
    if k <= 0:
        return np.array([], dtype=int)
    if k >= n:
        return np.arange(n, dtype=int)
    rng = np.random.default_rng(seed)
    medoids = kmeans_pp_init(Z, k, rng)
    for _ in range(max_iter):
        d = pairwise_l2(Z, Z[medoids])
        labels = d.argmin(axis=1)
        new_medoids = medoids.copy()
        changed = False
        for c in range(k):
            members = np.where(labels == c)[0]
            if len(members) == 0:
                continue
            sub = Z[members]
            sub_d = pairwise_l2(sub, sub)
            local_best = int(members[sub_d.sum(axis=1).argmin()])
            if local_best != medoids[c]:
                new_medoids[c] = local_best
                changed = True
        medoids = new_medoids
        if not changed:
            break
    return np.unique(medoids)


def select_clustering(Z: np.ndarray, k: int, seed: int, max_iter: int = 30) -> np.ndarray:
    n = Z.shape[0]
    k = min(k, n)
    if k <= 0:
        return np.array([], dtype=int)
    if k >= n:
        return np.arange(n, dtype=int)
    rng = np.random.default_rng(seed)
    centroids_idx = kmeans_pp_init(Z, k, rng)
    centroids = Z[centroids_idx].copy()
    labels = np.zeros(n, dtype=int)
    for _ in range(max_iter):
        d = pairwise_l2(Z, centroids)
        new_labels = d.argmin(axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for c in range(k):
            members = np.where(labels == c)[0]
            if len(members) > 0:
                centroids[c] = Z[members].mean(axis=0)
    selected: list[int] = []
    for c in range(k):
        members = np.where(labels == c)[0]
        if len(members) == 0:
            continue
        sub_d = pairwise_l2(Z[members], centroids[c : c + 1]).ravel()
        selected.append(int(members[sub_d.argmin()]))
    return np.unique(np.array(selected, dtype=int))


def auto_epsilon(Z: np.ndarray, percentile: float = 25.0) -> float:
    n = Z.shape[0]
    if n < 2:
        return 0.0
    d = pairwise_l2(Z, Z)
    tri = d[np.triu_indices(n, k=1)]
    return float(np.percentile(tri, percentile))


def select_epsilon_cover(Z: np.ndarray, k: int, seed: int, epsilon: float | None) -> np.ndarray:
    n = Z.shape[0]
    k = min(k, n)
    if k <= 0:
        return np.array([], dtype=int)
    eps = epsilon if epsilon is not None else auto_epsilon(Z)
    rng = np.random.default_rng(seed)
    order = rng.permutation(n)
    selected: list[int] = []
    for i in order:
        if len(selected) >= k:
            break
        if not selected:
            selected.append(int(i))
            continue
        d = dist_to_set(Z[i : i + 1], Z[selected])[0]
        if d >= eps:
            selected.append(int(i))
    if len(selected) < k:
        remaining = [i for i in range(n) if i not in selected]
        rem_d = dist_to_set(Z[remaining], Z[selected]) if selected else np.full(len(remaining), np.inf)
        extra = np.argsort(-rem_d)[: k - len(selected)]
        selected.extend(int(remaining[j]) for j in extra)
    return np.array(selected[:k], dtype=int)


def select_strict(Z: np.ndarray, k: int, seed: int) -> np.ndarray:
    n = Z.shape[0]
    k = min(k, n)
    if k <= 0:
        return np.array([], dtype=int)
    tau = auto_epsilon(Z, percentile=50.0)
    rng = np.random.default_rng(seed)
    order = rng.permutation(n)
    selected: list[int] = []
    for i in order:
        if len(selected) >= k:
            break
        if not selected:
            selected.append(int(i))
            continue
        d = dist_to_set(Z[i : i + 1], Z[selected])[0]
        if d >= tau:
            selected.append(int(i))
    if len(selected) < k:
        remaining = [i for i in range(n) if i not in selected]
        rem_d = dist_to_set(Z[remaining], Z[selected])
        extra = np.argsort(-rem_d)[: k - len(selected)]
        selected.extend(int(remaining[j]) for j in extra)
    return np.array(selected[:k], dtype=int)


def run_selection(method: str, Z: np.ndarray, k: int, seed: int, epsilon: float | None) -> np.ndarray:
    method = METHOD_ALIASES.get(method, method)
    if method == "kmedoids":
        return select_kmedoids(Z, k, seed)
    if method == "farthest":
        return select_farthest(Z, k, seed)
    if method == "clustering":
        return select_clustering(Z, k, seed)
    if method == "epsilon-cover":
        return select_epsilon_cover(Z, k, seed, epsilon)
    if method == "strict":
        return select_strict(Z, k, seed)
    raise ValueError(f"Unknown method: {method}")


def coverage_counts(df: pd.DataFrame, selected_ids: set[str], column: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for val in df[column].dropna().unique():
        counts[str(val)] = int(df[df[column] == val]["map_id"].isin(selected_ids).sum())
    return counts


def build_coverage_audit(
    pool_df: pd.DataFrame,
    selected_ids: set[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for cell, declared_ids in COVERAGE_CELLS.items():
        in_pool = pool_df[
            pool_df["map_archetype"].isin(declared_ids) | pool_df["generator_type"].isin(declared_ids)
        ]
        n_pool = len(in_pool)
        n_sel = int(in_pool["map_id"].isin(selected_ids).sum())
        if n_sel > 0:
            status = "covered"
        elif n_pool > 0:
            status = "partial"
        else:
            status = "missing"
        rows.append({
            "cell": cell,
            "declared_ids": ";".join(declared_ids),
            "n_in_pool": n_pool,
            "n_selected": n_sel,
            "status": status,
        })
    return pd.DataFrame(rows)


def enforce_anchor_quotas(
    selected_idx: np.ndarray,
    pool_df: pd.DataFrame,
    Z: np.ndarray,
    k: int,
    seed: int,
) -> np.ndarray:
    """Ensure minimum anchor_id coverage by swapping distant selections."""
    rng = np.random.default_rng(seed)
    selected = list(selected_idx)
    selected_set = set(selected)
    anchor_col = "anchor_id" if "anchor_id" in pool_df.columns else None
    if not anchor_col:
        return np.array(selected[:k], dtype=int)

    for anchor_id, min_n in ANCHOR_QUOTAS.items():
        mask = pool_df[anchor_col] == anchor_id
        if not mask.any():
            continue
        pool_indices = pool_df.index[mask].tolist()
        n_sel = sum(1 for i in selected if pool_df.iloc[i][anchor_col] == anchor_id)
        if n_sel >= min_n:
            continue
        candidates = [i for i in pool_indices if i not in selected_set]
        if not candidates:
            continue
        add_idx = int(candidates[rng.integers(0, len(candidates))])
        if len(selected) >= k:
            sel_pts = Z[selected]
            d = dist_to_set(Z[selected], sel_pts)
            drop = int(selected[int(np.argmax(d))])
            selected_set.discard(drop)
            selected = [i for i in selected if i != drop]
        selected.append(add_idx)
        selected_set.add(add_idx)
    return np.array(selected[:k], dtype=int)


def compute_metrics(Z: np.ndarray, selected_idx: np.ndarray, map_ids: list[str]) -> dict[str, Any]:
    if len(selected_idx) == 0:
        return {
            "min_dist_to_selected": 0.0,
            "mean_dist_to_selected": 0.0,
            "max_dist_to_selected": 0.0,
        }
    sel_pts = Z[selected_idx]
    d_all = dist_to_set(Z, sel_pts)
    return {
        "min_dist_to_selected": round(float(d_all.min()), 6),
        "mean_dist_to_selected": round(float(d_all.mean()), 6),
        "max_dist_to_selected": round(float(d_all.max()), 6),
    }


def policy_summary_row(
    method: str,
    n_candidates: int,
    n_valid: int,
    n_unique: int,
    selected_idx: np.ndarray,
    Z: np.ndarray,
    pool_df: pd.DataFrame,
    map_ids: list[str],
) -> dict[str, Any]:
    selected_ids = {map_ids[i] for i in selected_idx}
    metrics = compute_metrics(Z, selected_idx, map_ids)
    arch_cov = coverage_counts(pool_df, selected_ids, "map_archetype")
    src_cov = coverage_counts(pool_df, selected_ids, "source_type")
    gen_cov = coverage_counts(pool_df, selected_ids, "generator_type")
    return {
        "method": method,
        "n_candidates": n_candidates,
        "n_valid": n_valid,
        "n_unique": n_unique,
        "n_selected": len(selected_idx),
        **metrics,
        "coverage_archetype_json": json.dumps(arch_cov),
        "coverage_source_type_json": json.dumps(src_cov),
        "coverage_generator_type_json": json.dumps(gen_cov),
    }


def materialize_wkt_symlinks(
    selected_ids: list[str],
    records_by_id: dict[str, Any],
    out_dir: Path,
) -> None:
    wkt_root = out_dir / "wkt"
    if wkt_root.is_dir():
        shutil.rmtree(wkt_root)
    wkt_root.mkdir(parents=True)
    for map_id in selected_ids:
        rec = records_by_id.get(map_id)
        if rec is None:
            continue
        link = wkt_root / map_id
        target = rec.wkt_dir.resolve()
        link.symlink_to(target, target_is_directory=True)


def write_map_pruning_report(
    path: Path,
    *,
    method: str,
    target_n: int,
    k_eff: int,
    n_candidates: int,
    n_valid: int,
    n_unique: int,
    n_dup: int,
    selected_ids: list[str],
    metrics: dict[str, Any],
    coverage_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    epsilon_used: float | None,
) -> None:
    lines = [
        "# map_space_v1 — Map pruning report",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Canonical method:** {method}",
        f"**Target n:** {target_n} (effective k={k_eff})",
        "",
        "## Pool statistics",
        "",
        f"- Candidates in features CSV: {n_candidates}",
        f"- Valid with features: {n_valid}",
        f"- Unique after dedup: {n_unique}",
        f"- Exact duplicates removed: {n_dup}",
        f"- Selected: {len(selected_ids)}",
        "",
        "## Distance metrics (L2 in z-scored feature space)",
        "",
        f"- Min distance to nearest selected: {metrics.get('min_dist_to_selected', 0)}",
        f"- Mean distance to nearest selected: {metrics.get('mean_dist_to_selected', 0)}",
        f"- Max distance to nearest selected: {metrics.get('max_dist_to_selected', 0)}",
        "",
    ]
    if epsilon_used is not None:
        lines.extend([f"- Epsilon (epsilon-cover): {epsilon_used:.6f}", ""])
    lines.extend([
        "## Design-space coverage audit",
        "",
        df_to_markdown_table(coverage_df),
        "",
        "## Policy comparison",
        "",
        df_to_markdown_table(summary_df),
        "",
        "## Claim",
        "",
        "Selected maps form an approximate ε-cover of the **declared map-topology design space**",
        "under L2 distance in normalized topology features — not all possible maps on Earth.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_selected_maps_report(
    path: Path,
    *,
    method: str,
    selected_df: pd.DataFrame,
    coverage_df: pd.DataFrame,
    metrics: dict[str, Any],
    summary_df: pd.DataFrame,
    n_candidates: int,
    target_n: int,
) -> None:
    lines = [
        "# map_space_v1 — Selected maps",
        "",
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        f"**Method:** {method}",
        f"**Pool:** {n_candidates} candidates → {len(selected_df)} selected (target {target_n})",
        "",
        "## Justification for scenario generation",
        "",
        "The selected maps are:",
        "",
        "1. **Valid** — passed hard validation checks (Fase 2b)",
        "2. **Diverse** — chosen by feature-space distance, not manual curation",
        "3. **Representative** — approximate ε-cover of the generated candidate pool",
        "",
        "They cover the **declared map-topology design space** to the extent of the",
        "current candidate pool. They do **not** claim coverage of all real-world maps.",
        "",
        "## Distance metrics",
        "",
        f"| Metric | Value |",
        f"|--------|------:|",
        f"| min_dist_to_selected | {metrics.get('min_dist_to_selected', 0)} |",
        f"| mean_dist_to_selected | {metrics.get('mean_dist_to_selected', 0)} |",
        f"| max_dist_to_selected | {metrics.get('max_dist_to_selected', 0)} |",
        "",
        "## Selected maps",
        "",
    ]
    cols = ["map_id", "map_archetype", "source_type", "generator_type", "selection_rank", "dist_to_nearest_selected"]
    show = [c for c in cols if c in selected_df.columns]
    lines.append(df_to_markdown_table(selected_df[show]))
    lines.extend([
        "",
        "## Coverage by archetype / source / generator",
        "",
        f"Archetypes in selection: {selected_df['map_archetype'].value_counts().to_dict()}",
        f"Source types: {selected_df['source_type'].value_counts().to_dict()}",
        f"Generators: {selected_df['generator_type'].value_counts().to_dict()}",
        "",
        "## Design-space cell audit",
        "",
        df_to_markdown_table(coverage_df),
        "",
        "## Policy comparison",
        "",
        df_to_markdown_table(summary_df),
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_methodology_report(path: Path) -> None:
    text = """# map_space_v1 — Pruning methodology

**Version:** 1.0  
**Script:** `scenarios/setup/prune_map_space_v1.py`

## Defensible claim

> The generated maps cover an explicitly defined map-topology design space.
> Completeness is defined with respect to that declared design space,
> not with respect to all possible real-world environments.

(Source: `map_design_space_v1.yaml` → `methodology.completeness_claim`)

**We do not claim** coverage of all possible maps on Earth.  
**We do claim** that the selected subset approximately covers the **declared**
map-topology design space under a chosen feature metric.

## Feature space

- **Feature set:** `topology_v1` (alias `map_topology_v1`) — 20 numeric topology features
- **Normalization:** z-score per feature over the candidate pool (μ=0, σ=1)
- **Distance:** Euclidean L2 in normalized space: \\( d(z_i, z_j) = \\|z_i - z_j\\|_2 \\)

## Selection policies

| Policy | Method | Description |
|--------|--------|-------------|
| A strict diversity | `strict` | Greedy: accept map \\(i\\) only if \\( \\min_{s \\in S} \\|z_i - z_s\\|_2 \\geq \\tau \\) with \\(\\tau\\) = median pairwise distance |
| B k-medoids | `kmedoids` | PAM-style: minimize sum of distances to nearest medoid; **canonical** method |
| C farthest point | `farthest` | Farthest-point sampling: iteratively add \\( \\arg\\max_i \\min_{s \\in S} \\|z_i - z_s\\|_2 \\) |
| D epsilon-cover | `epsilon-cover` | Greedy ε-cover: add \\(i\\) if \\( \\min_{s \\in S} \\|z_i - z_s\\|_2 \\geq \\varepsilon \\) |
| Clustering | `clustering` | k-means++ centroids → nearest real map per cluster |

## ε-cover (formal)

Given finite pool \\(P \\subset \\mathbb{R}^d\\) (z-scored features) and selection \\(S \\subset P\\),
\\(S\\) is an **ε-cover** of \\(P\\) if:

\\[
\\forall p \\in P,\\ \\exists s \\in S:\\ \\|z_p - z_s\\|_2 \\leq \\varepsilon
\\]

The reported `max_dist_to_selected` is the empirical ε for the pool: every candidate lies
within that L2 ball of some selected map. k-medoids and farthest-point sampling approximate
this objective when \\(|S| = k\\) is fixed.

## Preprocessing

1. Filter: `features_status=ok`, `validation_class ∈ {valid, valid_partitioned, stress}`
2. Drop exact duplicates in z-space (tolerance \\(10^{-9}\\))
3. Select \\(k = \\min(\\text{target\\_n}, n_{unique})\\)

## Limitations (current pool)

With only 26 maps generated (of 600 declared), selection retains all unique valid maps
and design-space cell coverage is **partial**. Re-run after full generation for target 60.

## Outputs

- `map_space_v1/selected_maps/manifest_maps_selected.csv`
- `map_space_v1/selected_maps/map_pruning_summary.csv`
- `analysis/reports/map_space_v1_selected_maps.md`
"""
    path.write_text(text, encoding="utf-8")


def write_readme(out_dir: Path, method: str, n_selected: int, target_n: int) -> None:
    text = f"""# selected_maps — Diverse map subset (Fase 3)

**Canonical method:** {method}  
**Selected:** {n_selected} maps (target {target_n})

## Contents

| File | Description |
|------|-------------|
| `manifest_maps_selected.csv` | Selected maps with selection metadata |
| `selected_map_ids.txt` | One map_id per line |
| `map_pruning_report.md` | Run summary and coverage audit |
| `map_pruning_summary.csv` | Comparison across selection policies |
| `coverage_audit.csv` | Design-space cell coverage |
| `wkt/{{map_id}}/` | Symlinks to source WKT dirs (not copies) |

## Reproduce

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/prune_map_space_v1.py --compare-all
```

## Note

WKT paths are **symlinks** to `../synthetic/wkt/` or `../real_osm/wkt/`. Do not delete
source maps without updating links.

## References

- Methodology: [`../../analysis/reports/map_space_v1_pruning_methodology.md`](../../analysis/reports/map_space_v1_pruning_methodology.md)
- Selected maps report: [`../../analysis/reports/map_space_v1_selected_maps.md`](../../analysis/reports/map_space_v1_selected_maps.md)
- Traceability: [`../../scenario_space_v1/migration/phase3_selection/README.md`](../../scenario_space_v1/migration/phase3_selection/README.md)
"""
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def run(
    *,
    method: str = "kmedoids",
    target_n: int = 60,
    feature_set: str = "topology_v1",
    seed: int = 42,
    epsilon: float | None = None,
    compare_all: bool = False,
    features_csv: Path = DEFAULT_FEATURES,
    validation_csv: Path = DEFAULT_VALIDATION,
    manifest_path: Path = DEFAULT_MANIFEST,
    map_space_root: Path = MAP_SPACE_ROOT,
    out_dir: Path = DEFAULT_OUT,
) -> dict[str, Any]:
    t0 = time.time()

    feat_df = pd.read_csv(features_csv)
    if manifest_path.is_file():
        man = pd.read_csv(manifest_path)
        merge_cols = [c for c in ("anchor_id", "anchor_label", "dataset_basis", "source_type") if c in man.columns]
        if merge_cols:
            feat_df = feat_df.merge(man[["map_id"] + merge_cols], on="map_id", how="left", suffixes=("", "_man"))
    cols = feature_columns(feature_set, feat_df)
    n_candidates = len(feat_df)

    valid_mask = (
        (feat_df["features_status"] == "ok")
        & (feat_df["validation_class"].isin(VALID_CLASSES))
    )
    pool_df = feat_df.loc[valid_mask].copy().reset_index(drop=True)
    n_valid = len(pool_df)

    if n_valid == 0:
        raise RuntimeError("No valid maps with features to select from")

    X = pool_df[cols].astype(float).values
    Z, norm_params = zscore_matrix(X, cols)
    map_ids = pool_df["map_id"].tolist()

    unique_idx, dup_groups = dedupe_exact(Z, map_ids)
    n_dup = n_valid - len(unique_idx)
    Z_u = Z[unique_idx]
    pool_u = pool_df.iloc[unique_idx].reset_index(drop=True)
    map_ids_u = [map_ids[i] for i in unique_idx]

    k_eff = min(target_n, len(unique_idx))
    eps_used = epsilon if method == "epsilon-cover" else None
    if method == "epsilon-cover" and eps_used is None:
        eps_used = auto_epsilon(Z_u)

    methods_to_run = list(COMPARE_METHODS) if compare_all else [method]
    if compare_all and method not in methods_to_run:
        methods_to_run.append(method)

    summary_rows: list[dict[str, Any]] = []
    selections: dict[str, np.ndarray] = {}
    for m in methods_to_run:
        eps_m = epsilon if m == "epsilon-cover" else None
        sel_idx = run_selection(m, Z_u, k_eff, seed, eps_m)
        if m == method or (compare_all and m == "kmedoids"):
            sel_idx = enforce_anchor_quotas(sel_idx, pool_u, Z_u, k_eff, seed)
        selections[m] = sel_idx
        summary_rows.append(
            policy_summary_row(m, n_candidates, n_valid, len(unique_idx), sel_idx, Z_u, pool_u, map_ids_u)
        )

    summary_df = pd.DataFrame(summary_rows)
    canonical_idx = selections[method]
    canonical_ids = [map_ids_u[i] for i in canonical_idx]

    sel_pts = Z_u[canonical_idx]
    d_all = dist_to_set(Z_u, sel_pts)
    metrics = compute_metrics(Z_u, canonical_idx, map_ids_u)

    manifest_full = pd.read_csv(manifest_path)
    records = discover_maps(map_space_root, manifest_path)
    records_by_id = {r.map_id: r for r in records}

    selected_rows: list[dict[str, Any]] = []
    for rank, (idx, map_id) in enumerate(zip(canonical_idx, canonical_ids, strict=True)):
        row = pool_u.iloc[idx].to_dict()
        man = manifest_full[manifest_full["map_id"] == map_id]
        if not man.empty:
            for c in man.iloc[0].to_dict():
                if c not in row or pd.isna(row.get(c)):
                    row[c] = man.iloc[0][c]
        row["selection_method"] = method
        row["selection_rank"] = rank + 1
        row["dist_to_nearest_selected"] = round(float(d_all[idx]), 6)
        rec = records_by_id.get(map_id)
        row["wkt_dir"] = str(rec.wkt_dir.relative_to(map_space_root)) if rec else ""
        selected_rows.append(row)

    selected_df = pd.DataFrame(selected_rows)
    coverage_df = build_coverage_audit(pool_u, set(canonical_ids))

    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.iterdir():
        if f.name == "wkt":
            continue
        if f.is_file():
            f.unlink()

    selected_df.to_csv(out_dir / "manifest_maps_selected.csv", index=False)
    (out_dir / "selected_map_ids.txt").write_text("\n".join(canonical_ids) + "\n", encoding="utf-8")
    summary_df.to_csv(out_dir / "map_pruning_summary.csv", index=False)
    coverage_df.to_csv(out_dir / "coverage_audit.csv", index=False)
    norm_params.to_csv(out_dir / "normalization_params.csv", index=False)
    if dup_groups:
        pd.DataFrame(dup_groups).to_csv(out_dir / "duplicate_groups.csv", index=False)
    else:
        pd.DataFrame(columns=["duplicate_map_id", "representative_map_id"]).to_csv(
            out_dir / "duplicate_groups.csv", index=False
        )

    write_map_pruning_report(
        out_dir / "map_pruning_report.md",
        method=method,
        target_n=target_n,
        k_eff=k_eff,
        n_candidates=n_candidates,
        n_valid=n_valid,
        n_unique=len(unique_idx),
        n_dup=n_dup,
        selected_ids=canonical_ids,
        metrics=metrics,
        coverage_df=coverage_df,
        summary_df=summary_df,
        epsilon_used=eps_used,
    )
    write_readme(out_dir, method, len(canonical_ids), target_n)
    materialize_wkt_symlinks(canonical_ids, records_by_id, out_dir)

    write_methodology_report(METHODOLOGY_REPORT)
    write_selected_maps_report(
        SELECTED_REPORT,
        method=method,
        selected_df=selected_df,
        coverage_df=coverage_df,
        metrics=metrics,
        summary_df=summary_df,
        n_candidates=n_candidates,
        target_n=target_n,
    )

    elapsed = time.time() - t0
    print(f"Selected {len(canonical_ids)} maps ({method}) → {out_dir}")
    print(f"  unique pool: {len(unique_idx)}, duplicates removed: {n_dup}")
    print(f"  max_dist_to_selected (ε approx): {metrics['max_dist_to_selected']}")
    print(f"  elapsed: {elapsed:.1f}s")

    return {
        "method": method,
        "n_selected": len(canonical_ids),
        "selected_ids": canonical_ids,
        "metrics": metrics,
        "summary_df": summary_df,
        "coverage_df": coverage_df,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Select diverse map_space_v1 subset by topology features.")
    p.add_argument("--method", choices=ALL_METHODS, default="kmedoids",
                   help="cluster_medoids is alias for kmedoids")
    p.add_argument("--target-n", type=int, default=60)
    p.add_argument("--feature-set", default="topology_v1")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--epsilon", type=float, default=None, help="Radius for epsilon-cover (auto if omitted)")
    p.add_argument("--compare-all", action="store_true", help="Run policies A-D and write summary")
    p.add_argument("--features-csv", type=Path, default=DEFAULT_FEATURES)
    p.add_argument("--validation-csv", type=Path, default=DEFAULT_VALIDATION)
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--map-space", type=Path, default=MAP_SPACE_ROOT)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()
    if args.method in METHOD_ALIASES:
        args.method = METHOD_ALIASES[args.method]

    run(
        method=args.method,
        target_n=args.target_n,
        feature_set=args.feature_set,
        seed=args.seed,
        epsilon=args.epsilon,
        compare_all=args.compare_all,
        features_csv=args.features_csv,
        validation_csv=args.validation_csv,
        manifest_path=args.manifest,
        map_space_root=args.map_space,
        out_dir=args.out_dir,
    )


if __name__ == "__main__":
    main()
