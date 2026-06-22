#!/usr/bin/env python3
"""Audit coverage of the official selected_map_space_v1 subset."""

from __future__ import annotations

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

from map_selection_v1_common import (  # noqa: E402
    DEFAULT_POLICY,
    DEFAULT_SELECTED_ROOT,
    SCENARIOS_DIR,
    build_selection_matrix,
    distances_to_selected,
    evaluate_selection,
    load_official_pool,
    load_policy,
)
from analyze_map_space_saturation_v1 import pairwise_l2  # noqa: E402


def pca_2d(z: np.ndarray) -> np.ndarray:
    zc = z - z.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(zc, full_matrices=False)
    return zc @ vt[:2].T


FIGURES = SCENARIOS_DIR / "analysis" / "figures" / "selected_map_space_v1"
COVERAGE_CSV = SCENARIOS_DIR / "analysis" / "data" / "selected_map_space_v1_coverage.csv"
DISTANCE_AUDIT_CSV = SCENARIOS_DIR / "analysis" / "data" / "selected_map_space_v1_distance_audit.csv"
REPORT_PATH = SCENARIOS_DIR / "analysis" / "reports" / "selected_map_space_v1_coverage_report.md"


def main() -> None:
    policy = load_policy(DEFAULT_POLICY)
    pool = load_official_pool()
    z, _ = build_selection_matrix(pool, policy)

    manifest_path = DEFAULT_SELECTED_ROOT / "manifest_selected_maps.csv"
    if not manifest_path.exists():
        raise SystemExit(f"Missing {manifest_path}; run --write-official first")

    selected = pd.read_csv(manifest_path)
    sel_ids = set(selected["map_id"])
    pool_idx = pool.index[pool["map_id"].isin(sel_ids)].to_numpy()
    selected_idx = np.array(pool_idx, dtype=int)

    metrics = evaluate_selection(z, selected_idx, pool, policy)
    dist_all = metrics.pop("distances_to_selected")

    # coverage by archetype / source
    cov_rows = []
    for arch in sorted(pool["archetype"].unique()):
        pmask = pool["archetype"] == arch
        smask = selected["archetype"] == arch
        cov_rows.append(
            {
                "archetype": arch,
                "pool_count": int(pmask.sum()),
                "selected_count": int(smask.sum()),
                "fraction_selected": float(smask.sum() / pmask.sum()) if pmask.sum() else 0.0,
            }
        )
    cov_df = pd.DataFrame(cov_rows)
    cov_df.to_csv(COVERAGE_CSV, index=False)

    audit = pool[["map_id", "archetype", "source_type", "anchor_id", "validation_status"]].copy()
    audit["distance_to_nearest_selected"] = dist_all
    audit["is_selected"] = audit["map_id"].isin(sel_ids)
    audit.to_csv(DISTANCE_AUDIT_CSV, index=False)

    FIGURES.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    selected["archetype"].value_counts().sort_index().plot(kind="bar", ax=ax)
    ax.set_title("Selected archetype counts")
    fig.tight_layout()
    fig.savefig(FIGURES / "selected_archetype_counts.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    selected["source_type"].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Selected source type counts")
    fig.tight_layout()
    fig.savefig(FIGURES / "selected_source_type_counts.png", dpi=150)
    plt.close(fig)

    anchor_sel = selected[selected["anchor_id"].notna() & (selected["anchor_id"] != "")]["anchor_id"]
    fig, ax = plt.subplots(figsize=(10, 5))
    anchor_sel.value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Selected anchor counts")
    fig.tight_layout()
    fig.savefig(FIGURES / "selected_anchor_counts.png", dpi=150)
    plt.close(fig)

    coords = pca_2d(z)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(coords[:, 0], coords[:, 1], s=8, alpha=0.3, label="pool")
    ax.scatter(coords[selected_idx, 0], coords[selected_idx, 1], s=40, c="red", label="selected")
    ax.legend()
    ax.set_title("Pool vs selected (PCA)")
    fig.tight_layout()
    fig.savefig(FIGURES / "pool_vs_selected_pca.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(dist_all, bins=40, alpha=0.8)
    ax.set_xlabel("distance to nearest selected")
    ax.set_title("Coverage distance histogram")
    fig.tight_layout()
    fig.savefig(FIGURES / "coverage_distance_histogram.png", dpi=150)
    plt.close(fig)

    if len(selected_idx) > 1:
        sel_z = z[selected_idx]
        dmat = pairwise_l2(sel_z, sel_z)
        fig, ax = plt.subplots(figsize=(8, 7))
        im = ax.imshow(dmat, cmap="viridis")
        ax.set_title("Selected map distance heatmap")
        fig.colorbar(im, ax=ax)
        fig.tight_layout()
        fig.savefig(FIGURES / "selected_map_distance_heatmap.png", dpi=150)
        plt.close(fig)

    min_arch = int(policy["constraints"].get("min_maps_per_archetype", 2))
    weak = cov_df[cov_df["selected_count"] < min_arch]

    lines = [
        "# Selected map space v1 — coverage audit",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"- Selected maps: **{len(selected)}**",
        f"- Pool maps: **{len(pool)}**",
        f"- Archetype coverage: **{metrics['archetype_coverage']}/15**",
        f"- Source type coverage: **{metrics['source_type_coverage']}/3**",
        f"- Anchor coverage: **{metrics['anchor_coverage']}**",
        f"- Mean distance to selected: **{metrics['mean_distance_to_selected']:.4f}**",
        f"- Max distance to selected: **{metrics['max_distance_to_selected']:.4f}**",
        f"- P95 distance: **{metrics['p95_distance_to_selected']:.4f}**",
        f"- Constraints satisfied: **{metrics['constraints_satisfied']}**",
        "",
        "## Source type fractions",
        "",
        f"- OSM: {metrics['osm_fraction']:.3f}",
        f"- synthetic: {metrics['synthetic_fraction']:.3f}",
        f"- trace_reference_synthetic: {metrics['trace_reference_synthetic_fraction']:.3f}",
        "",
    ]
    if len(weak):
        lines.append("## Weak archetypes")
        lines.append("")
        for _, r in weak.iterrows():
            lines.append(f"- {r['archetype']}: {r['selected_count']} selected (min {min_arch})")
    else:
        lines.append("All archetypes meet minimum per-archetype quota.")

    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{COVERAGE_CSV.relative_to(SCENARIOS_DIR.parent)}`",
            f"- `{DISTANCE_AUDIT_CSV.relative_to(SCENARIOS_DIR.parent)}`",
            f"- Figures under `scenarios/analysis/figures/selected_map_space_v1/`",
        ]
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Coverage audit -> {REPORT_PATH}")


if __name__ == "__main__":
    main()
