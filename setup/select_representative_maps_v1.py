#!/usr/bin/env python3
"""Select representative maps from the official @1200 pool (selected_map_space_v1)."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from analyze_map_space_saturation_v1 import (  # noqa: E402
    dist_to_set,
    pairwise_l2,
    select_farthest,
    select_kmedoids,
)
from map_selection_v1_common import (  # noqa: E402
    DEFAULT_DECISION,
    DEFAULT_EXPERIMENTS,
    DEFAULT_FIGURES,
    DEFAULT_MANIFEST,
    DEFAULT_POLICY,
    DEFAULT_SELECTED_ROOT,
    SCENARIOS_DIR,
    SOURCE_TYPES,
    build_selection_matrix,
    distances_to_selected,
    evaluate_selection,
    load_official_pool,
    load_policy,
    pool_centroid_idx,
    write_json,
    _json_default,
)

MAP_ROOT = SCENARIOS_DIR / "map_space_saturation_v1"
SIZE_DECISION_REPORT = SCENARIOS_DIR / "analysis" / "reports" / "selected_map_space_v1_size_decision.md"

EXPERIMENT_COLUMNS = [
    "method",
    "target_n",
    "epsilon",
    "n_selected",
    "mean_distance_to_selected",
    "median_distance_to_selected",
    "p95_distance_to_selected",
    "max_distance_to_selected",
    "mean_pairwise_selected_distance",
    "min_pairwise_selected_distance",
    "archetype_coverage",
    "source_type_coverage",
    "anchor_coverage",
    "min_maps_per_archetype",
    "max_single_archetype_fraction",
    "osm_fraction",
    "synthetic_fraction",
    "trace_reference_synthetic_fraction",
    "outlier_preservation",
    "redundancy_within_selected",
    "constraints_satisfied",
    "notes",
]

PAPER_CLAIM = (
    "The selected map set is a representative subset of the saturated map-design pool. "
    "It preserves categorical coverage of the declared archetypes while reducing "
    "feature-space redundancy through diversity-based selection."
)


def select_farthest_centroid_init(z: np.ndarray, k: int, seed: int) -> np.ndarray:
    n = z.shape[0]
    k = min(k, n)
    if k <= 0:
        return np.array([], dtype=int)
    if k >= n:
        return np.arange(n, dtype=int)
    selected = [pool_centroid_idx(z)]
    while len(selected) < k:
        sel_pts = z[selected]
        d = dist_to_set(z, sel_pts)
        for idx in selected:
            d[idx] = -1.0
        selected.append(int(np.argmax(d)))
    return np.array(selected, dtype=int)


def select_epsilon_cover(z: np.ndarray, epsilon: float, seed: int) -> np.ndarray:
    n = z.shape[0]
    if n == 0:
        return np.array([], dtype=int)
    rng = np.random.default_rng(seed)
    uncovered = set(range(n))
    selected: list[int] = []
    start = pool_centroid_idx(z)
    selected.append(start)
    uncovered.discard(start)

    while uncovered:
        sel_pts = z[selected]
        d = dist_to_set(z, sel_pts)
        max_d = max(d[i] for i in uncovered)
        if max_d <= epsilon:
            break
        candidates = [i for i in uncovered if d[i] >= epsilon * 0.95]
        if not candidates:
            candidates = list(uncovered)
        next_i = int(candidates[int(rng.integers(0, len(candidates)))])
        if d[next_i] < max_d * 0.5:
            next_i = int(max(uncovered, key=lambda i: d[i]))
        selected.append(next_i)
        to_remove = {i for i in uncovered if d[i] <= epsilon}
        uncovered -= to_remove
        uncovered.discard(next_i)
    return np.array(selected, dtype=int)


def archetype_quotas(
    pool: pd.DataFrame,
    z: np.ndarray,
    target_n: int,
    min_per: int,
) -> dict[str, int]:
    arch_groups = pool.groupby("archetype", sort=False)
    archetypes = list(arch_groups.groups.keys())
    n_arch = len(archetypes)
    base = {a: min(min_per, len(arch_groups.get_group(a))) for a in archetypes}
    allocated = sum(base.values())
    remaining = max(0, target_n - allocated)
    if remaining == 0:
        return base

    weights: dict[str, float] = {}
    for a in archetypes:
        idx = arch_groups.groups[a]
        sub = z[idx]
        var = float(np.var(sub)) if len(idx) > 1 else 1.0
        weights[a] = len(idx) * max(var, 1e-6)

    total_w = sum(weights.values()) or 1.0
    extra = {a: int(round(remaining * weights[a] / total_w)) for a in archetypes}
    for a in archetypes:
        cap = len(arch_groups.get_group(a)) - base[a]
        extra[a] = min(extra[a], cap)
    while sum(extra.values()) < remaining:
        for a in sorted(archetypes, key=lambda x: weights[x], reverse=True):
            if base[a] + extra[a] < len(arch_groups.get_group(a)):
                extra[a] += 1
                if sum(extra.values()) >= remaining:
                    break
    while sum(extra.values()) > remaining:
        for a in sorted(archetypes, key=lambda x: extra[x], reverse=True):
            if extra[a] > 0:
                extra[a] -= 1
                if sum(extra.values()) <= remaining:
                    break
    return {a: base[a] + extra[a] for a in archetypes}


def select_stratified_kmedoids(
    pool: pd.DataFrame,
    z: np.ndarray,
    target_n: int,
    seed: int,
    min_per: int = 2,
) -> tuple[np.ndarray, dict[int, str]]:
    quotas = archetype_quotas(pool, z, target_n, min_per)
    selected: list[int] = []
    roles: dict[int, str] = {}
    for arch, k in quotas.items():
        if k <= 0:
            continue
        idx = pool.index[pool["archetype"] == arch].to_numpy()
        sub_z = z[idx]
        medoids = select_kmedoids(sub_z, k, seed + hash(arch) % 10000)
        for m in medoids:
            global_i = int(idx[m])
            selected.append(global_i)
            roles[global_i] = "archetype_medoid"
    return np.unique(np.array(selected, dtype=int)), roles


def select_hybrid(
    pool: pd.DataFrame,
    z: np.ndarray,
    target_n: int,
    seed: int,
) -> tuple[np.ndarray, dict[int, str]]:
    min_per = 3 if target_n >= 45 else 2
    selected_list, roles = select_stratified_kmedoids(pool, z, target_n, seed, min_per=min_per)
    selected = set(selected_list.tolist())

    # topological outliers: farthest from current set
    n_outliers = max(3, target_n // 10)
    d = distances_to_selected(z, np.array(list(selected), dtype=int))
    outlier_order = np.argsort(-d)
    for i in outlier_order:
        if len(selected) >= target_n:
            break
        if int(i) not in selected:
            selected.add(int(i))
            roles[int(i)] = "topological_outlier"

    # balance source types via penalized FPS
    target_frac = pool["source_type"].value_counts(normalize=True).to_dict()
    while len(selected) < target_n:
        sel_idx = np.array(list(selected), dtype=int)
        d = distances_to_selected(z, sel_idx)
        for i in selected:
            d[i] = -1.0
        st_counts = pool.iloc[list(selected)]["source_type"].value_counts(normalize=True)
        best_score = -np.inf
        best_i = -1
        for cand in np.where(d > 0)[0]:
            st = pool.iloc[cand]["source_type"]
            frac = st_counts.get(st, 0.0)
            tgt = target_frac.get(st, 1.0 / 3)
            penalty = abs(frac - tgt)
            score = d[cand] * (1.0 + penalty)
            if score > best_score:
                best_score = score
                best_i = int(cand)
        if best_i < 0:
            break
        selected.add(best_i)
        roles[best_i] = roles.get(best_i, "source_type_balance")

    return np.array(sorted(selected)[:target_n], dtype=int), roles


def run_method(
    method: str,
    pool: pd.DataFrame,
    z: np.ndarray,
    policy: dict[str, Any],
    target_n: int | None = None,
    epsilon: float | None = None,
    seed: int = 42,
) -> tuple[np.ndarray, dict[int, str]]:
    roles: dict[int, str] = {}
    if method in ("kmedoids", "kmedoids_global"):
        k = target_n or 60
        idx = select_kmedoids(z, k, seed)
        roles = {int(i): "global_medoid" for i in idx}
        return idx, roles
    if method in ("farthest", "farthest_point_sampling"):
        k = target_n or 60
        idx = select_farthest_centroid_init(z, k, seed)
        roles = {int(i): "topological_outlier" for i in idx}
        return idx, roles
    if method in ("epsilon-cover", "epsilon_cover"):
        eps = epsilon if epsilon is not None else 0.35
        idx = select_epsilon_cover(z, eps, seed)
        roles = {int(i): "epsilon_cover_representative" for i in idx}
        return idx, roles
    if method in ("stratified-kmedoids", "stratified_kmedoids"):
        k = target_n or 60
        min_per = int(policy["constraints"].get("min_maps_per_archetype", 2))
        return select_stratified_kmedoids(pool, z, k, seed, min_per=min_per)
    if method in ("hybrid", "hybrid_stratified_diversity"):
        k = target_n or 75
        return select_hybrid(pool, z, k, seed)
    raise ValueError(f"Unknown method: {method}")


def metrics_row(
    method: str,
    target_n: int | None,
    epsilon: float | None,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    row = {
        "method": method,
        "target_n": target_n if target_n is not None else "",
        "epsilon": epsilon if epsilon is not None else "",
        "notes": metrics.get("constraint_notes", ""),
    }
    for col in EXPERIMENT_COLUMNS:
        if col in row:
            continue
        if col in metrics:
            row[col] = metrics[col]
    return row


def run_experiments(pool: pd.DataFrame, z: np.ndarray, policy: dict[str, Any], seed: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    sizes = policy.get("target_sizes", [30, 45, 60, 75, 90, 120])
    methods = [
        ("kmedoids", "target_n"),
        ("farthest", "target_n"),
        ("stratified-kmedoids", "target_n"),
        ("hybrid", "target_n"),
    ]
    for method, _ in methods:
        for n in sizes:
            idx, _ = run_method(method, pool, z, policy, target_n=n, seed=seed)
            m = evaluate_selection(z, idx, pool, policy)
            rows.append(metrics_row(method, n, None, m))

    for eps in policy.get("epsilon_grid", [0.20, 0.25, 0.30, 0.35, 0.40, 0.50]):
        idx, _ = run_method("epsilon-cover", pool, z, policy, epsilon=eps, seed=seed)
        m = evaluate_selection(z, idx, pool, policy)
        rows.append(metrics_row("epsilon-cover", None, eps, m))

    return pd.DataFrame(rows, columns=EXPERIMENT_COLUMNS)


def decide_official_selection(experiments: pd.DataFrame, policy: dict[str, Any]) -> dict[str, Any]:
    prefer = policy.get("official_selection", {}).get("prefer_method", "hybrid_stratified_diversity")
    fallback = policy.get("official_selection", {}).get("fallback_method", "stratified_kmedoids")
    threshold = float(policy.get("official_selection", {}).get("elbow_marginal_improvement_threshold", 0.05))
    sizes = sorted(policy.get("target_sizes", [30, 45, 60, 75, 90, 120]))

    method_map = {
        "hybrid_stratified_diversity": "hybrid",
        "stratified_kmedoids": "stratified-kmedoids",
    }
    primary = method_map.get(prefer, prefer)
    fb = method_map.get(fallback, fallback)

    def filter_method(mname: str) -> pd.DataFrame:
        sub = experiments[(experiments["method"] == mname) & (experiments["constraints_satisfied"] == True)].copy()  # noqa: E712
        sub = sub[sub["target_n"] != ""]
        sub["target_n"] = sub["target_n"].astype(int)
        return sub.sort_values("target_n")

    chosen_df = filter_method(primary)
    chosen_method = primary
    if chosen_df.empty:
        chosen_df = filter_method(fb)
        chosen_method = fb
    if chosen_df.empty:
        chosen_df = experiments[experiments["constraints_satisfied"] == True].copy()  # noqa: E712
        chosen_df = chosen_df[chosen_df["target_n"] != ""]
        chosen_df["target_n"] = chosen_df["target_n"].astype(int)
        chosen_method = str(chosen_df.iloc[0]["method"]) if len(chosen_df) else primary

    official_n = int(sizes[-1])
    reason_parts: list[str] = []

    if not chosen_df.empty:
        prev_max = None
        for n in sizes:
            row = chosen_df[chosen_df["target_n"] == n]
            if row.empty:
                continue
            max_d = float(row.iloc[0]["max_distance_to_selected"])
            if prev_max is not None:
                improvement = (prev_max - max_d) / prev_max if prev_max > 0 else 1.0
                if improvement < threshold:
                    official_n = n
                    reason_parts.append(
                        f"elbow at n={n}: marginal max_distance improvement {improvement:.3f} < {threshold}"
                    )
                    break
            prev_max = max_d
        else:
            official_n = int(chosen_df["target_n"].max())
            reason_parts.append(f"no elbow below threshold; using largest feasible n={official_n}")

    final_row = chosen_df[chosen_df["target_n"] == official_n]
    if final_row.empty and not chosen_df.empty:
        official_n = int(chosen_df.iloc[-1]["target_n"])
        final_row = chosen_df[chosen_df["target_n"] == official_n]

    coverage_metrics = {}
    if not final_row.empty:
        r = final_row.iloc[0]
        coverage_metrics = {c: r[c] for c in EXPERIMENT_COLUMNS if c in r and c not in ("method", "notes")}

    reason = "; ".join(reason_parts) or f"selected {chosen_method} n={official_n} with constraints satisfied"
    return {
        "official_method": chosen_method,
        "official_n": official_n,
        "reason": reason,
        "coverage_metrics": coverage_metrics,
        "constraints_satisfied": bool(final_row.iloc[0]["constraints_satisfied"]) if not final_row.empty else False,
        "paper_ready_claim": PAPER_CLAIM,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def plot_experiments(df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    sized = df[df["target_n"] != ""].copy()
    sized["target_n"] = sized["target_n"].astype(int)

    for metric, fname in [
        ("mean_distance_to_selected", "coverage_vs_n.png"),
        ("max_distance_to_selected", "max_distance_vs_n.png"),
        ("p95_distance_to_selected", "p95_distance_vs_n.png"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 5))
        for method in sized["method"].unique():
            sub = sized[sized["method"] == method].sort_values("target_n")
            ax.plot(sub["target_n"], sub[metric], marker="o", label=method)
        ax.set_xlabel("target_n")
        ax.set_ylabel(metric)
        ax.legend(fontsize=8)
        ax.set_title(metric)
        fig.tight_layout()
        fig.savefig(out_dir / fname, dpi=150)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for method in sized["method"].unique():
        sub = sized[sized["method"] == method].sort_values("target_n")
        ax.plot(sub["target_n"], sub["osm_fraction"], marker="o", label=f"{method} osm")
    ax.set_xlabel("target_n")
    ax.set_ylabel("osm_fraction")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out_dir / "source_type_balance_vs_n.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for method in sized["method"].unique():
        sub = sized[sized["method"] == method].sort_values("target_n")
        ax.plot(sub["target_n"], sub["archetype_coverage"], marker="o", label=method)
    ax.axhline(15, color="gray", linestyle="--", label="15 archetypes")
    ax.set_xlabel("target_n")
    ax.set_ylabel("archetype_coverage")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "archetype_coverage_vs_n.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    pivot = sized.groupby(["method", "target_n"])["max_distance_to_selected"].mean().unstack(0)
    pivot.plot(kind="bar", ax=ax)
    ax.set_title("max_distance_to_selected by method and n")
    fig.tight_layout()
    fig.savefig(out_dir / "selection_method_comparison.png", dpi=150)
    plt.close(fig)


def write_size_decision_report(decision: dict[str, Any], experiments: pd.DataFrame) -> None:
    lines = [
        "# Selected map space v1 — size decision",
        "",
        f"Generated: {decision.get('generated_at', '')}",
        "",
        f"- **Official method:** `{decision['official_method']}`",
        f"- **Official N:** {decision['official_n']}",
        f"- **Constraints satisfied:** {decision['constraints_satisfied']}",
        "",
        "## Rationale",
        "",
        decision["reason"],
        "",
        "## Paper-ready claim",
        "",
        f"> {decision['paper_ready_claim']}",
        "",
        "## Coverage metrics",
        "",
        "```json",
        json.dumps(decision.get("coverage_metrics", {}), indent=2, default=_json_default),
        "```",
    ]
    SIZE_DECISION_REPORT.parent.mkdir(parents=True, exist_ok=True)
    SIZE_DECISION_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def assign_feature_clusters(z: np.ndarray, selected_idx: np.ndarray) -> dict[int, int]:
    if len(selected_idx) == 0:
        return {}
    sel = z[selected_idx]
    d = pairwise_l2(z[selected_idx], sel)
    labels = d.argmin(axis=1)
    return {int(selected_idx[i]): int(labels[i]) for i in range(len(selected_idx))}


def write_official(
    pool: pd.DataFrame,
    z: np.ndarray,
    selected_idx: np.ndarray,
    roles: dict[int, str],
    method: str,
    seed: int,
    decision: dict[str, Any],
) -> None:
    root = DEFAULT_SELECTED_ROOT
    root.mkdir(parents=True, exist_ok=True)
    wkt_root = root / "wkt"
    wkt_root.mkdir(exist_ok=True)

    dist_sel = distances_to_selected(z, selected_idx)
    centroid = z.mean(axis=0, keepdims=True)
    dist_centroid = pairwise_l2(z, centroid).ravel()
    clusters = assign_feature_clusters(z, selected_idx)

    manifest_rows: list[dict[str, Any]] = []
    for rank, i in enumerate(selected_idx):
        row = pool.iloc[i]
        map_id = row["map_id"]
        dest = wkt_root / map_id
        dest.mkdir(parents=True, exist_ok=True)

        for col, fname in [("roads_wkt", "roads.wkt"), ("metadata_json", "metadata.json"), ("preview_png", "preview.png")]:
            src_rel = row.get(col, "")
            if pd.isna(src_rel) or not src_rel:
                continue
            src = MAP_ROOT / str(src_rel)
            if src.exists():
                shutil.copy2(src, dest / fname)

        manifest_rows.append(
            {
                "selected_id": rank + 1,
                "map_id": map_id,
                "source_type": row["source_type"],
                "anchor_id": row.get("anchor_id", ""),
                "anchor_label": row.get("anchor_label", ""),
                "archetype": row["archetype"],
                "generator_type": row.get("generator_type", ""),
                "selection_method": method,
                "selection_role": roles.get(int(i), "global_medoid"),
                "feature_cluster": clusters.get(int(i), -1),
                "batch_target": int(row["batch_target"]),
                "validation_status": row["validation_status"],
                "wkt_dir": f"wkt/{map_id}",
                "roads_wkt": f"wkt/{map_id}/roads.wkt",
                "metadata_json": f"wkt/{map_id}/metadata.json",
                "preview_png": f"wkt/{map_id}/preview.png",
                "world_size_x": row.get("world_size_x", ""),
                "world_size_y": row.get("world_size_y", ""),
                "n_nodes": row.get("n_nodes", ""),
                "n_edges": row.get("n_edges", ""),
                "road_density": row.get("road_density", ""),
                "gridness_score": row.get("gridness_score", ""),
                "corridor_score": row.get("corridor_score", ""),
                "partition_score": row.get("partition_score", ""),
                "community_score": row.get("community_score", ""),
                "distance_to_nearest_selected": float(dist_sel[i]),
                "distance_to_pool_centroid": float(dist_centroid[i]),
                "notes": "",
            }
        )

    manifest_df = pd.DataFrame(manifest_rows)
    manifest_df.to_csv(root / "manifest_selected_maps.csv", index=False)
    (root / "selected_map_ids.txt").write_text("\n".join(manifest_df["map_id"]) + "\n", encoding="utf-8")
    pool.iloc[selected_idx].to_csv(root / "selected_maps_features.csv", index=False)

    summary = manifest_df.groupby(["archetype", "source_type"]).size().reset_index(name="count")
    summary.to_csv(root / "selected_maps_summary.csv", index=False)

    cov_rows = []
    for arch in pool["archetype"].unique():
        pool_n = int((pool["archetype"] == arch).sum())
        sel_n = int((manifest_df["archetype"] == arch).sum())
        cov_rows.append({"archetype": arch, "pool_count": pool_n, "selected_count": sel_n})
    pd.DataFrame(cov_rows).to_csv(root / "selected_maps_coverage.csv", index=False)

    rationale_lines = ["# Selected maps rationale", "", f"Method: {method}, N={len(selected_idx)}, seed={seed}", ""]
    for _, r in manifest_df.iterrows():
        rationale_lines.append(
            f"- **{r['map_id']}** ({r['archetype']}, {r['source_type']}): role={r['selection_role']}"
        )
    (root / "selected_maps_rationale.md").write_text("\n".join(rationale_lines) + "\n", encoding="utf-8")

    readme = [
        "# selected_map_space_v1",
        "",
        f"Official representative map subset from Phase 1 pool @1200.",
        "",
        f"- **N:** {len(selected_idx)}",
        f"- **Method:** {method}",
        f"- **Seed:** {seed}",
        f"- **Decision:** {decision.get('reason', '')}",
        "",
        "WKT assets are copied under `wkt/{map_id}/`.",
    ]
    (root / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(f"Official set written to {root} ({len(selected_idx)} maps)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Select representative maps v1")
    parser.add_argument("--method", default="hybrid")
    parser.add_argument("--target-n", type=int, default=None)
    parser.add_argument("--epsilon", type=float, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--run-experiments", action="store_true")
    parser.add_argument("--write-official", action="store_true")
    parser.add_argument("--write-decision-only", action="store_true")
    args = parser.parse_args()

    policy = load_policy(args.policy)
    pool = load_official_pool()
    z, _ = build_selection_matrix(pool, policy)
    print(f"Pool: {len(pool)} maps, feature dim {z.shape[1]}")

    if args.run_experiments:
        exp_df = run_experiments(pool, z, policy, args.seed)
        DEFAULT_EXPERIMENTS.parent.mkdir(parents=True, exist_ok=True)
        exp_df.to_csv(DEFAULT_EXPERIMENTS, index=False)
        plot_experiments(exp_df, DEFAULT_FIGURES)
        decision = decide_official_selection(exp_df, policy)
        write_json(DEFAULT_DECISION, decision)
        write_size_decision_report(decision, exp_df)
        print(f"Experiments -> {DEFAULT_EXPERIMENTS}")
        print(f"Decision: {decision['official_method']} n={decision['official_n']}")
        return

    if args.write_decision_only:
        exp_df = pd.read_csv(DEFAULT_EXPERIMENTS)
        decision = decide_official_selection(exp_df, policy)
        write_json(DEFAULT_DECISION, decision)
        write_size_decision_report(decision, exp_df)
        return

    method = args.method
    target_n = args.target_n
    if args.write_official and target_n is None and DEFAULT_DECISION.exists():
        decision = json.loads(DEFAULT_DECISION.read_text(encoding="utf-8"))
        method = decision.get("official_method", method)
        target_n = decision.get("official_n", target_n)
    else:
        decision = {}

    idx, roles = run_method(method, pool, z, policy, target_n=target_n, epsilon=args.epsilon, seed=args.seed)
    metrics = evaluate_selection(z, idx, pool, policy)
    print(json.dumps({k: v for k, v in metrics.items() if k != "distances_to_selected"}, indent=2))

    if args.write_official:
        if not decision:
            decision = json.loads(DEFAULT_DECISION.read_text(encoding="utf-8")) if DEFAULT_DECISION.exists() else {}
        write_official(pool, z, idx, roles, method, args.seed, decision)


if __name__ == "__main__":
    main()
