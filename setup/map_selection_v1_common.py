"""Shared utilities for map selection Phase 2 (selected_map_space_v1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from analyze_map_space_saturation_v1 import dist_to_set, pairwise_l2
from extract_map_space_saturation_features import INCLUDED_STATUSES, NUMERIC_FEATURE_COLUMNS

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCENARIOS_DIR = REPO_ROOT / "scenarios"

DEFAULT_MANIFEST = SCENARIOS_DIR / "map_space_saturation_v1" / "manifest_maps_all.csv"
DEFAULT_VALIDATION = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_validation.csv"
DEFAULT_FEATURES = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_features.csv"
DEFAULT_POLICY = SCENARIOS_DIR / "analysis" / "config" / "selected_map_space_v1_policy.yaml"
DEFAULT_POOL_CSV = SCENARIOS_DIR / "analysis" / "data" / "map_selection_pool_v1.csv"
DEFAULT_DECISION = SCENARIOS_DIR / "analysis" / "data" / "selected_map_space_v1_decision.json"
DEFAULT_EXPERIMENTS = SCENARIOS_DIR / "analysis" / "data" / "selected_map_space_v1_selection_experiments.csv"
DEFAULT_SELECTED_ROOT = SCENARIOS_DIR / "selected_map_space_v1"
DEFAULT_FIGURES = SCENARIOS_DIR / "analysis" / "figures" / "selected_map_space_v1"

SOURCE_TYPES = ["osm", "synthetic", "trace_reference_synthetic"]
OFFICIAL_MAX_BATCH = 1200


def load_policy(path: Path | None = None) -> dict[str, Any]:
    path = path or DEFAULT_POLICY
    with path.open(encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    return doc["selected_map_space_v1"]


def load_official_pool(
    manifest_path: Path | None = None,
    validation_path: Path | None = None,
    features_path: Path | None = None,
    max_batch: int = OFFICIAL_MAX_BATCH,
) -> pd.DataFrame:
    manifest_path = manifest_path or DEFAULT_MANIFEST
    validation_path = validation_path or DEFAULT_VALIDATION
    features_path = features_path or DEFAULT_FEATURES

    manifest = pd.read_csv(manifest_path)
    validation = pd.read_csv(validation_path)
    features = pd.read_csv(features_path)

    val_cols = validation[["map_id", "status"]].rename(columns={"status": "validation_status_val"})
    pool = features.merge(val_cols, on="map_id", how="left")
    pool = pool.merge(
        manifest[
            [
                "map_id",
                "anchor_label",
                "wkt_dir",
                "roads_wkt",
                "metadata_json",
                "preview_png",
                "generation_status",
            ]
        ],
        on="map_id",
        how="left",
        suffixes=("", "_m"),
    )

    if "validation_status" not in pool.columns or pool["validation_status"].isna().any():
        pool["validation_status"] = pool["validation_status"].fillna(pool.get("validation_status_val", ""))

    pool["batch_target"] = pool["batch_target"].astype(int)
    pool = pool[pool["batch_target"] <= max_batch].copy()
    pool = pool[pool["validation_status"].isin(INCLUDED_STATUSES)].copy()
    pool = pool.sort_values("map_id").reset_index(drop=True)
    return pool


def build_selection_matrix(df: pd.DataFrame, policy: dict[str, Any]) -> tuple[np.ndarray, list[str]]:
    """Z-score on pool subset + optional source_type one-hot."""
    fs = policy.get("feature_space", {})
    numeric_cols = [c for c in NUMERIC_FEATURE_COLUMNS if c in df.columns]
    raw = df[numeric_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)

    mean = raw.mean(axis=0)
    std = raw.std(axis=0)
    std = np.where(std < 1e-12, 1.0, std)
    z = (raw - mean) / std

    if fs.get("include_source_type_one_hot", True):
        for st in SOURCE_TYPES:
            col = (df["source_type"] == st).astype(np.float64).to_numpy().reshape(-1, 1)
            z = np.hstack([z, col])

    feature_names = list(numeric_cols)
    if fs.get("include_source_type_one_hot", True):
        feature_names += [f"source_type_{st}" for st in SOURCE_TYPES]

    return z, feature_names


def pool_centroid_idx(z: np.ndarray) -> int:
    c = z.mean(axis=0, keepdims=True)
    d = pairwise_l2(z, c)
    return int(d.argmin())


def distances_to_selected(z: np.ndarray, selected_idx: np.ndarray) -> np.ndarray:
    if len(selected_idx) == 0:
        return np.full(z.shape[0], np.inf)
    sel = z[selected_idx]
    d = pairwise_l2(z, sel)
    return d.min(axis=1)


def check_constraints(meta: pd.DataFrame, policy: dict[str, Any]) -> tuple[bool, list[str]]:
    constraints = policy.get("constraints", {})
    notes: list[str] = []
    ok = True
    n = len(meta)
    if n == 0:
        return False, ["empty selection"]

    arch_counts = meta["archetype"].value_counts()
    min_arch = int(constraints.get("min_maps_per_archetype", 2))
    if arch_counts.min() < min_arch:
        ok = False
        notes.append(f"min_maps_per_archetype<{min_arch}: {arch_counts.min()}")

    declared_arch = 15
    if meta["archetype"].nunique() < declared_arch:
        ok = False
        notes.append(f"archetype_coverage<{declared_arch}")

    st_counts = meta["source_type"].value_counts(normalize=True)
    for key, col in [
        ("min_osm_fraction", "osm"),
        ("min_synthetic_fraction", "synthetic"),
        ("min_trace_reference_synthetic_fraction", "trace_reference_synthetic"),
    ]:
        lo = constraints.get(key)
        if lo is not None and st_counts.get(col, 0.0) < float(lo):
            ok = False
            notes.append(f"{col}_frac<{lo}")

    max_osm = constraints.get("max_osm_fraction")
    if max_osm is not None and st_counts.get("osm", 0.0) > float(max_osm):
        ok = False
        notes.append(f"osm_frac>{max_osm}")

    max_arch_frac = float(constraints.get("max_single_archetype_fraction", 1.0))
    if (arch_counts.max() / n) > max_arch_frac:
        ok = False
        notes.append(f"max_single_archetype_fraction>{max_arch_frac}")

    if "anchor_id" in meta.columns:
        ac = meta[meta["anchor_id"].notna() & (meta["anchor_id"] != "")]["anchor_id"].value_counts()
        if len(ac) > 0:
            max_anchor = float(constraints.get("max_single_anchor_fraction", 1.0))
            if (ac.max() / n) > max_anchor:
                ok = False
                notes.append(f"max_single_anchor_fraction>{max_anchor}")

    for st in SOURCE_TYPES:
        if st not in set(meta["source_type"]):
            ok = False
            notes.append(f"missing_source_type:{st}")

    return ok, notes


def evaluate_selection(
    z: np.ndarray,
    selected_idx: np.ndarray,
    pool: pd.DataFrame,
    policy: dict[str, Any],
) -> dict[str, Any]:
    sel_meta = pool.iloc[selected_idx].copy()
    n_sel = len(selected_idx)
    dist_all = distances_to_selected(z, selected_idx)

    if n_sel > 1:
        sel_z = z[selected_idx]
        pdist = pairwise_l2(sel_z, sel_z)
        triu = pdist[np.triu_indices(n_sel, k=1)]
        mean_pair = float(np.mean(triu)) if len(triu) else 0.0
        min_pair = float(np.min(triu)) if len(triu) else 0.0
    else:
        mean_pair = 0.0
        min_pair = 0.0

    arch_counts = sel_meta["archetype"].value_counts()
    st_frac = sel_meta["source_type"].value_counts(normalize=True)

    constraints_ok, constraint_notes = check_constraints(sel_meta, policy)

    # outlier preservation: fraction of pool points with dist > p95 that are within 1.05x of nearest selected
    p95_pool = float(np.percentile(dist_all, 95))
    far_mask = dist_all >= p95_pool
    if far_mask.any():
        outlier_pres = float(np.mean(dist_all[far_mask] <= p95_pool * 1.05))
    else:
        outlier_pres = 1.0

    redundant = 0.0
    if n_sel > 1:
        nn_sel = np.sort(pairwise_l2(z[selected_idx], z[selected_idx]), axis=1)[:, 1]
        redundant = float(np.mean(nn_sel < 0.25))

    anchor_cov = 0
    if "anchor_id" in sel_meta.columns:
        anchor_cov = int(sel_meta[sel_meta["anchor_id"].notna() & (sel_meta["anchor_id"] != "")]["anchor_id"].nunique())

    return {
        "n_selected": n_sel,
        "mean_distance_to_selected": float(np.mean(dist_all)),
        "median_distance_to_selected": float(np.median(dist_all)),
        "p95_distance_to_selected": float(np.percentile(dist_all, 95)),
        "max_distance_to_selected": float(np.max(dist_all)),
        "mean_pairwise_selected_distance": mean_pair,
        "min_pairwise_selected_distance": min_pair,
        "archetype_coverage": int(arch_counts.shape[0]),
        "source_type_coverage": int(sel_meta["source_type"].nunique()),
        "anchor_coverage": anchor_cov,
        "min_maps_per_archetype": int(arch_counts.min()) if len(arch_counts) else 0,
        "max_single_archetype_fraction": float(arch_counts.max() / n_sel) if n_sel else 0.0,
        "osm_fraction": float(st_frac.get("osm", 0.0)),
        "synthetic_fraction": float(st_frac.get("synthetic", 0.0)),
        "trace_reference_synthetic_fraction": float(st_frac.get("trace_reference_synthetic", 0.0)),
        "outlier_preservation": outlier_pres,
        "redundancy_within_selected": redundant,
        "constraints_satisfied": constraints_ok,
        "constraint_notes": "; ".join(constraint_notes),
        "distances_to_selected": dist_all,
    }


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def write_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, default=_json_default), encoding="utf-8")
