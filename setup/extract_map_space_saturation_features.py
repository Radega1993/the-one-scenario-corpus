#!/usr/bin/env python3
"""Extract topology features from validated map_space_saturation_v1 maps."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_space_topology import build_road_graph, extract_saturation_features  # noqa: E402

REPO_ROOT = _SETUP.parent.parent
SCENARIOS_DIR = REPO_ROOT / "scenarios"
DEFAULT_MAP_ROOT = SCENARIOS_DIR / "map_space_saturation_v1"
DEFAULT_MANIFEST = DEFAULT_MAP_ROOT / "manifest_maps_all.csv"
DEFAULT_VALIDATION = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_validation.csv"
DEFAULT_ARCHETYPES = SCENARIOS_DIR / "analysis" / "data" / "map_archetype_definitions_v1.csv"
DEFAULT_OUTPUT = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_features.csv"
DEFAULT_OUTPUT_NORMALIZED = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_features_normalized.csv"
DEFAULT_NORM_PARAMS = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_features_normalization_params.csv"
DEFAULT_REPORT = SCENARIOS_DIR / "analysis" / "reports" / "map_space_saturation_features_report.md"
DEFAULT_EXCLUDED = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_features_excluded_fail.csv"

INCLUDED_STATUSES = frozenset({"PASS", "WARNING", "STRESS"})

IDENTITY_COLUMNS = [
    "map_id",
    "batch_target",
    "source_type",
    "anchor_id",
    "archetype",
    "generator_type",
]

SCALE_COLUMNS = [
    "world_size_x",
    "world_size_y",
    "world_area",
    "bbox_width",
    "bbox_height",
    "useful_area",
    "useful_area_ratio",
]

GRAPH_COLUMNS = [
    "n_nodes",
    "n_edges",
    "total_road_length_m",
    "road_density",
    "avg_edge_length_m",
    "median_edge_length_m",
    "avg_degree",
    "max_degree",
    "dead_end_ratio",
    "intersection_ratio",
]

CONNECTIVITY_COLUMNS = [
    "n_components",
    "largest_component_ratio",
    "bridge_edges_count",
    "bridge_edges_ratio",
    "articulation_points_count",
    "articulation_points_ratio",
]

SHAPE_COLUMNS = [
    "graph_diameter_approx",
    "avg_shortest_path_approx",
    "circuity_approx",
    "orientation_entropy",
    "gridness_score",
    "corridor_score",
    "radial_score",
    "partition_score",
    "community_score",
    "tree_like_score",
]

THE_ONE_COLUMNS = [
    "supports_map_based",
    "supports_route_movement_candidate",
    "supports_cluster_overlay",
    "supports_wdm_candidate",
    "supports_bus_route_candidate",
]

META_COLUMNS = [
    "validation_status",
    "feature_omissions",
    "sampling_seed",
]

FEATURE_COLUMNS = (
    IDENTITY_COLUMNS
    + SCALE_COLUMNS
    + GRAPH_COLUMNS
    + CONNECTIVITY_COLUMNS
    + SHAPE_COLUMNS
    + THE_ONE_COLUMNS
    + META_COLUMNS
)

NUMERIC_FEATURE_COLUMNS = SCALE_COLUMNS + GRAPH_COLUMNS + CONNECTIVITY_COLUMNS + SHAPE_COLUMNS

CLUSTER_OVERLAY_BY_ARCHETYPE: dict[str, str] = {
    "clustered_communities": "yes",
    "compact_residential": "yes",
    "campus_compact": "partial",
    "conference_event_compact": "partial",
    "dense_urban_irregular": "partial",
}

BUS_ROUTE_BY_ARCHETYPE: dict[str, str] = {
    "bus_route_urban_suburban": "yes",
    "corridor_linear": "partial",
    "suburban_low_density": "partial",
}

FEATURE_DEFINITIONS: dict[str, str] = {
    "world_size_x": "Simulation world width (m) from metadata.",
    "world_size_y": "Simulation world height (m) from metadata.",
    "world_area": "world_size_x * world_size_y.",
    "bbox_width": "Road network bounding box width (m).",
    "bbox_height": "Road network bounding box height (m).",
    "useful_area": "Area of road bbox (m²).",
    "useful_area_ratio": "useful_area / world_area.",
    "n_nodes": "Unique graph nodes (rounded coordinates).",
    "n_edges": "Unique undirected road segments.",
    "total_road_length_m": "Sum of segment lengths (m).",
    "road_density": "n_edges / world_area.",
    "avg_edge_length_m": "Mean segment length (m).",
    "median_edge_length_m": "Median segment length (m).",
    "avg_degree": "2|E|/|N|.",
    "max_degree": "Maximum node degree.",
    "dead_end_ratio": "Fraction of degree-1 nodes.",
    "intersection_ratio": "Fraction of nodes with degree >= 3.",
    "n_components": "Connected components.",
    "largest_component_ratio": "Largest component size / n_nodes.",
    "bridge_edges_count": "NetworkX bridge edges.",
    "bridge_edges_ratio": "bridge_edges_count / n_edges.",
    "articulation_points_count": "NetworkX articulation points.",
    "articulation_points_ratio": "articulation_points_count / n_nodes.",
    "graph_diameter_approx": "2 × eccentricity from highest-degree node.",
    "avg_shortest_path_approx": "Mean shortest path over random node pairs (sampled).",
    "circuity_approx": "Mean shortest-path / Euclidean ratio (sampled pairs).",
    "orientation_entropy": "Entropy of edge bearing histogram (36 bins).",
    "gridness_score": "Fraction of edges aligned to N-S/E-W (±15°).",
    "corridor_score": "Elongation of node point cloud (1 = line-like).",
    "radial_score": "Hub concentration vs periphery.",
    "partition_score": "1 - largest_component_ratio when partitioned.",
    "community_score": "Greedy modularity intra-community edge fraction.",
    "tree_like_score": "Tree-likeness of largest component.",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_archetype_table(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv(path)
    return {r["archetype"]: r for r in rows if r.get("archetype")}


def the_one_flags(archetype: str, arch_table: dict[str, dict[str, str]]) -> dict[str, str]:
    row = arch_table.get(archetype, {})
    return {
        "supports_map_based": row.get("supports_map_based_movement", "unknown") or "unknown",
        "supports_route_movement_candidate": row.get("supports_route_movement", "unknown") or "unknown",
        "supports_wdm_candidate": row.get("supports_wdm", "unknown") or "unknown",
        "supports_cluster_overlay": CLUSTER_OVERLAY_BY_ARCHETYPE.get(archetype, "no"),
        "supports_bus_route_candidate": BUS_ROUTE_BY_ARCHETYPE.get(archetype, "no"),
    }


def fmt_value(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, float) and math.isnan(val):
        return "NaN"
    if isinstance(val, float):
        return repr(val)
    return str(val)


def parse_float(s: str) -> float:
    if not s or s == "NaN":
        return float("nan")
    return float(s)


def zscore_normalize_rows(
    rows: list[dict[str, str]],
    numeric_cols: list[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Z-score per numeric column; NaN imputed to 0 after normalization."""
    params: list[dict[str, str]] = []
    col_values: dict[str, list[float]] = {c: [] for c in numeric_cols}

    for row in rows:
        for c in numeric_cols:
            v = parse_float(row.get(c, ""))
            if not math.isnan(v):
                col_values[c].append(v)

    means: dict[str, float] = {}
    stds: dict[str, float] = {}
    for c in numeric_cols:
        vals = col_values[c]
        if not vals:
            means[c] = 0.0
            stds[c] = 0.0
        else:
            means[c] = sum(vals) / len(vals)
            if len(vals) > 1:
                var = sum((x - means[c]) ** 2 for x in vals) / len(vals)
                stds[c] = math.sqrt(var)
            else:
                stds[c] = 0.0
        params.append({"feature": c, "mean": fmt_value(means[c]), "std": fmt_value(stds[c])})

    norm_rows: list[dict[str, str]] = []
    for row in rows:
        out = {"map_id": row["map_id"]}
        for c in numeric_cols:
            v = parse_float(row.get(c, ""))
            if math.isnan(v) or stds[c] == 0:
                out[c] = "0"
            else:
                out[c] = fmt_value((v - means[c]) / stds[c])
        st = row.get("source_type", "")
        out["source_type_osm"] = "1" if st == "osm" else "0"
        out["source_type_synthetic"] = "1" if st == "synthetic" else "0"
        out["source_type_trace_reference_synthetic"] = "1" if st == "trace_reference_synthetic" else "0"
        norm_rows.append(out)

    return norm_rows, params


def extract_one_map(
    *,
    map_id: str,
    mrow: dict[str, str],
    vstatus: str,
    map_root: Path,
    arch_table: dict[str, dict[str, str]],
) -> dict[str, str] | None:
    wkt_rel = mrow.get("wkt_dir", "")
    roads_rel = mrow.get("roads_wkt", "")
    if roads_rel:
        roads = map_root / roads_rel
    elif wkt_rel:
        roads = map_root / wkt_rel / "roads.wkt"
    else:
        return None
    if not roads.is_file():
        return None

    meta: dict[str, Any] = {}
    meta_path = roads.parent / "metadata.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    ws = meta.get("world_size", [0, 0])
    world_size = (int(ws[0] or 0), int(ws[1] or 0))
    seed = int(meta.get("seed", mrow.get("seed", 42) or 42))

    row: dict[str, str] = {
        "map_id": map_id,
        "batch_target": mrow.get("batch_target", ""),
        "source_type": mrow.get("source_type", ""),
        "anchor_id": mrow.get("anchor_id", ""),
        "archetype": mrow.get("archetype", ""),
        "generator_type": mrow.get("generator_type", ""),
        "validation_status": vstatus,
        "sampling_seed": str(seed),
        "feature_omissions": "",
    }
    row.update(the_one_flags(mrow.get("archetype", ""), arch_table))

    try:
        rg = build_road_graph(roads)
        feats, omissions = extract_saturation_features(rg, world_size, seed=seed)
        for k, v in feats.items():
            row[k] = fmt_value(v)
        row["feature_omissions"] = ";".join(sorted(set(omissions)))
    except Exception as exc:
        row["feature_omissions"] = f"extract_failed:{exc}"
        for c in NUMERIC_FEATURE_COLUMNS:
            row[c] = "NaN"

    return row


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def quantize_signature(row: dict[str, str]) -> tuple[str, ...]:
    keys = ("n_nodes", "n_edges", "total_road_length_m", "world_size_x", "world_size_y")
    return tuple(row.get(k, "") for k in keys)


def compute_outliers(rows: list[dict[str, str]], col: str, top_n: int = 5) -> list[tuple[str, float]]:
    vals: list[tuple[str, float]] = []
    for r in rows:
        v = parse_float(r.get(col, ""))
        if not math.isnan(v):
            vals.append((r["map_id"], v))
    if len(vals) < 4:
        return []
    sorted_vals = sorted(v for _, v in vals)
    q1 = sorted_vals[len(sorted_vals) // 4]
    q3 = sorted_vals[(3 * len(sorted_vals)) // 4]
    iqr = q3 - q1
    if iqr <= 0:
        return []
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = [(mid, v) for mid, v in vals if v < lo or v > hi]
    outliers.sort(key=lambda x: abs(x[1] - (q1 + q3) / 2), reverse=True)
    return outliers[:top_n]


def write_report(
    path: Path,
    *,
    included: list[dict[str, str]],
    excluded: list[dict[str, str]],
    status_counts: Counter[str],
    omission_counts: Counter[str],
    archetype_declared: set[str],
) -> None:
    lines: list[str] = [
        "# map_space_saturation_features_report.md",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## 1. Summary",
        "",
        f"- maps_with_features: {len(included)}",
        f"- maps_excluded_fail: {len(excluded)}",
        f"- validation PASS: {status_counts.get('PASS', 0)}",
        f"- validation WARNING: {status_counts.get('WARNING', 0)}",
        f"- validation STRESS: {status_counts.get('STRESS', 0)}",
        "",
        "## 2. Features generated",
        "",
    ]
    for col in NUMERIC_FEATURE_COLUMNS + THE_ONE_COLUMNS:
        desc = FEATURE_DEFINITIONS.get(col, "(categorical flag from archetype table)")
        lines.append(f"- `{col}`: {desc}")

    lines.extend(["", "## 3. Omitted features", ""])
    if omission_counts:
        for feat, cnt in omission_counts.most_common():
            lines.append(f"- `{feat}`: {cnt} maps")
    else:
        lines.append("- No per-map feature omissions recorded.")

    lines.extend(
        [
            "",
            "## 4. Sampling methodology",
            "",
            "- `graph_diameter_approx`: 2 × eccentricity from highest-degree node (exact on sampled BFS tree).",
            "- `avg_shortest_path_approx`: mean Dijkstra distance over up to 64 random node pairs (`sampling_seed` per map).",
            "- `circuity_approx`: mean (shortest-path / Euclidean) over up to 64 pairs (seed+1).",
            "- For graphs with n_nodes > 10_000, sample count reduced to 32.",
            "- `community_score`: greedy modularity; NaN if algorithm fails.",
            "",
            "## 5. Distribution by batch",
            "",
        ]
    )
    batch_c = Counter(r.get("batch_target", "") for r in included)
    for bt in sorted(batch_c.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        lines.append(f"- batch_{int(bt):04d}: {batch_c[bt]}")

    lines.extend(["", "## 6. Distribution by archetype", ""])
    arch_c = Counter(r.get("archetype", "") or "(none)" for r in included)
    for arch, cnt in arch_c.most_common():
        lines.append(f"- {arch}: {cnt}")
    covered = set(r.get("archetype", "") for r in included if r.get("archetype"))
    missing_arch = sorted(archetype_declared - covered)
    if missing_arch:
        lines.extend(["", "**Archetypes declared but without PASS/WARNING/STRESS maps:**", ""])
        for a in missing_arch:
            lines.append(f"- {a}")

    lines.extend(["", "## 7. Outliers (IQR method)", ""])
    for col in ("road_density", "dead_end_ratio", "n_nodes", "gridness_score"):
        lines.append(f"### {col}")
        outs = compute_outliers(included, col)
        if not outs:
            lines.append("- (none detected)")
        else:
            for mid, v in outs:
                lines.append(f"- {mid}: {v:.4f}")
        lines.append("")

    lines.extend(["## 8. Degenerate / suspect maps", ""])
    degenerate = [
        r
        for r in included
        if parse_float(r.get("n_edges", "")) <= 20
        or parse_float(r.get("tree_like_score", "")) > 0.9
        or len((r.get("feature_omissions") or "").split(";")) > 3
    ]
    lines.append(f"- count: {len(degenerate)}")
    for r in degenerate[:15]:
        lines.append(
            f"  - {r['map_id']}: n_edges={r.get('n_edges')} tree_like={r.get('tree_like_score')} "
            f"omissions={r.get('feature_omissions', '')[:60]}"
        )

    lines.extend(["", "## 9. Duplicate feature signatures", ""])
    sig_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for r in included:
        sig_groups[quantize_signature(r)].append(r["map_id"])
    dup_groups = [ids for ids in sig_groups.values() if len(ids) > 1]
    lines.append(f"- duplicate_groups: {len(dup_groups)}")
    lines.append(f"- max_group_size: {max((len(g) for g in dup_groups), default=0)}")
    for g in sorted(dup_groups, key=len, reverse=True)[:5]:
        lines.append(f"  - {len(g)} maps: {', '.join(g[:4])}{'...' if len(g) > 4 else ''}")

    lines.extend(
        [
            "",
            "## 10. Excluded FAIL maps",
            "",
            f"Documented in `map_space_saturation_features_excluded_fail.csv` ({len(excluded)} rows).",
            "",
            "## 11. Recommendations",
            "",
            "- Use `map_space_saturation_features_normalized.csv` for distance/cluster saturation metrics.",
            "- FAIL maps are excluded from the primary feature-space; re-include only after re-validation.",
            "- Duplicate OSM signatures are expected when variants share identical windows; dedupe in saturation analysis.",
            "- Proceed to Phase 2: batch-wise saturation curves (n_clusters, max nearest distance, archetype coverage).",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract saturation features from validated maps.")
    parser.add_argument("--map-root", type=Path, default=DEFAULT_MAP_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--archetypes", type=Path, default=DEFAULT_ARCHETYPES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output-normalized", type=Path, default=DEFAULT_OUTPUT_NORMALIZED)
    parser.add_argument("--norm-params", type=Path, default=DEFAULT_NORM_PARAMS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--excluded-report", type=Path, default=DEFAULT_EXCLUDED)
    parser.add_argument("--no-normalize", action="store_true")
    args = parser.parse_args()

    manifest = {r["map_id"]: r for r in read_csv(args.manifest) if r.get("map_id")}
    validation = {r["map_id"]: r for r in read_csv(args.validation) if r.get("map_id")}
    arch_table = load_archetype_table(args.archetypes)
    archetype_declared = set(arch_table.keys())

    included_rows: list[dict[str, str]] = []
    excluded_rows: list[dict[str, str]] = []
    status_counts: Counter[str] = Counter()
    omission_counts: Counter[str] = Counter()

    for map_id in sorted(manifest.keys()):
        mrow = manifest[map_id]
        vrow = validation.get(map_id, {})
        vstatus = vrow.get("status", "")

        if vstatus == "FAIL" or (vstatus and vstatus not in INCLUDED_STATUSES):
            if vstatus == "FAIL" or not vstatus:
                excluded_rows.append(
                    {
                        "map_id": map_id,
                        "validation_status": vstatus or "UNKNOWN",
                        "reason": vrow.get("reason", ""),
                        "source_type": mrow.get("source_type", ""),
                        "archetype": mrow.get("archetype", ""),
                    }
                )
            continue

        if vstatus not in INCLUDED_STATUSES:
            continue

        row = extract_one_map(
            map_id=map_id,
            mrow=mrow,
            vstatus=vstatus,
            map_root=args.map_root,
            arch_table=arch_table,
        )
        if row is None:
            excluded_rows.append(
                {
                    "map_id": map_id,
                    "validation_status": vstatus,
                    "reason": "missing_roads_wkt",
                    "source_type": mrow.get("source_type", ""),
                    "archetype": mrow.get("archetype", ""),
                }
            )
            continue

        included_rows.append(row)
        status_counts[vstatus] += 1
        for o in (row.get("feature_omissions") or "").split(";"):
            if o and not o.startswith("extract_failed"):
                omission_counts[o] += 1

    write_csv(args.output, included_rows, FEATURE_COLUMNS)

    if not args.no_normalize and included_rows:
        norm_rows, params = zscore_normalize_rows(included_rows, NUMERIC_FEATURE_COLUMNS)
        norm_columns = ["map_id"] + NUMERIC_FEATURE_COLUMNS + [
            "source_type_osm",
            "source_type_synthetic",
            "source_type_trace_reference_synthetic",
        ]
        write_csv(args.output_normalized, norm_rows, norm_columns)
        write_csv(args.norm_params, params, ["feature", "mean", "std"])

    write_csv(
        args.excluded_report,
        excluded_rows,
        ["map_id", "validation_status", "reason", "source_type", "archetype"],
    )

    write_report(
        args.report,
        included=included_rows,
        excluded=excluded_rows,
        status_counts=status_counts,
        omission_counts=omission_counts,
        archetype_declared=archetype_declared,
    )

    print(f"Features: {len(included_rows)} maps → {args.output}")
    print(f"Excluded: {len(excluded_rows)} maps → {args.excluded_report}")
    print(f"Report: {args.report}")
    if not args.no_normalize and included_rows:
        print(f"Normalized: {args.output_normalized}")


if __name__ == "__main__":
    main()
