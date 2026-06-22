#!/usr/bin/env python3
"""
extract_map_features_v1.py — Extract topology features for map_space_v1 candidates.

Usage:
    scenarios/analysis/.venv/bin/python scenarios/setup/extract_map_features_v1.py
    scenarios/analysis/.venv/bin/python scenarios/setup/extract_map_features_v1.py --validation-csv scenarios/analysis/data/map_space_v1_validation.csv
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_space_topology import build_road_graph, discover_maps, extract_topology_features  # noqa: E402

SCENARIOS_DIR = _SETUP.parent
MAP_SPACE_ROOT = SCENARIOS_DIR / "map_space_v1"
DEFAULT_VALIDATION_CSV = SCENARIOS_DIR / "analysis" / "data" / "map_space_v1_validation.csv"
FEATURES_CSV = SCENARIOS_DIR / "analysis" / "data" / "map_space_v1_features.csv"
FEATURES_REPORT = SCENARIOS_DIR / "analysis" / "reports" / "map_space_v1_features_report.md"

FEATURE_COLUMNS = [
    "map_id",
    "features_status",
    "skip_reason",
    "validation_class",
    "map_archetype",
    "source_type",
    "anchor_id",
    "generator_type",
    "n_nodes",
    "n_edges",
    "total_road_length_m",
    "road_density",
    "world_area",
    "useful_area",
    "useful_area_ratio",
    "avg_degree",
    "max_degree",
    "dead_end_ratio",
    "n_components",
    "largest_component_ratio",
    "bridge_edges",
    "articulation_points",
    "orientation_entropy",
    "gridness_score",
    "corridor_score",
    "radial_score",
    "partition_score",
    "community_score",
    "graph_diameter_approx",
    "avg_shortest_path_approx",
    "circuity_approx",
]

VALID_CLASSES = {"valid", "valid_partitioned", "stress", "PASS", "WARNING", "STRESS"}
NUMERIC_FEATURES = [c for c in FEATURE_COLUMNS if c not in (
    "map_id", "features_status", "skip_reason", "validation_class",
    "map_archetype", "source_type", "anchor_id", "generator_type",
)]


def load_validation_classes(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        return {row["map_id"]: row for row in csv.DictReader(f)}


def pearson_r(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den_x = sum((x - mx) ** 2 for x in xs) ** 0.5
    den_y = sum((y - my) ** 2 for y in ys) ** 0.5
    if den_x < 1e-12 or den_y < 1e-12:
        return 0.0
    return num / (den_x * den_y)


def run_extract(
    *,
    validation_csv: Path = DEFAULT_VALIDATION_CSV,
    map_space_root: Path = MAP_SPACE_ROOT,
    features_csv: Path = FEATURES_CSV,
    report_path: Path = FEATURES_REPORT,
    include_stress: bool = True,
    seed: int = 42,
) -> list[dict[str, Any]]:
    val_rows = load_validation_classes(validation_csv)
    manifest_path = map_space_root / "manifest_maps.csv"
    records = discover_maps(map_space_root, manifest_path)

    allowed = set(VALID_CLASSES) if include_stress else {"valid", "valid_partitioned"}

    out_rows: list[dict[str, Any]] = []
    for rec in records:
        val = val_rows.get(rec.map_id, {})
        vclass = val.get("validation_class", "unknown")
        meta_pre = rec.meta
        base = {
            "map_id": rec.map_id,
            "validation_class": vclass,
            "map_archetype": rec.archetype,
            "source_type": rec.source_type,
            "anchor_id": rec.manifest_row.get("anchor_id", meta_pre.get("anchor_id", "")),
            "generator_type": rec.generator_type,
        }

        if vclass not in allowed:
            row = {**base, "features_status": "skipped_invalid", "skip_reason": val.get("failure_reasons", vclass)}
            out_rows.append(row)
            continue

        meta = rec.meta
        ws = meta.get("world_size", [0, 0])
        wx, wy = int(ws[0]), int(ws[1])
        rg = build_road_graph(rec.roads_path)
        feats = extract_topology_features(rg, (wx, wy), seed=seed)
        row = {
            **base,
            "features_status": "ok",
            "skip_reason": "",
            **feats,
        }
        out_rows.append(row)

    features_csv.parent.mkdir(parents=True, exist_ok=True)
    with features_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FEATURE_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for row in out_rows:
            w.writerow({k: row.get(k, "") for k in FEATURE_COLUMNS})

    write_features_report(out_rows, report_path)
    ok = sum(1 for r in out_rows if r.get("features_status") == "ok")
    print(f"Features extracted: {ok}/{len(out_rows)} → {features_csv}")
    return out_rows


def write_features_report(rows: list[dict[str, Any]], path: Path) -> None:
    ok_rows = [r for r in rows if r.get("features_status") == "ok"]
    lines = [
        "# map_space_v1 — Informe de features topológicas",
        "",
        f"**Fecha:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        f"**Mapas con features:** {len(ok_rows)} / {len(rows)}",
        "",
        "## 1. Distribución marginal (mapas válidos)",
        "",
        "| Feature | min | median | max |",
        "|---------|----:|-------:|----:|",
    ]

    for feat in NUMERIC_FEATURES:
        vals = [float(r[feat]) for r in ok_rows if r.get(feat) not in (None, "")]
        if not vals:
            continue
        lines.append(
            f"| {feat} | {min(vals):.4g} | {statistics.median(vals):.4g} | {max(vals):.4g} |"
        )

    lines.extend(["", "## 2. Correlaciones altas (|r| ≥ 0.9)", ""])
    high_pairs: list[tuple[str, str, float]] = []
    if len(ok_rows) >= 3:
        for i, f1 in enumerate(NUMERIC_FEATURES):
            v1 = [float(r[f1]) for r in ok_rows if r.get(f1) not in (None, "")]
            if len(v1) != len(ok_rows):
                continue
            for f2 in NUMERIC_FEATURES[i + 1 :]:
                v2 = [float(r[f2]) for r in ok_rows if r.get(f2) not in (None, "")]
                if len(v2) != len(ok_rows):
                    continue
                r_val = pearson_r(v1, v2)
                if abs(r_val) >= 0.9:
                    high_pairs.append((f1, f2, r_val))

    if high_pairs:
        for f1, f2, r_val in sorted(high_pairs, key=lambda x: -abs(x[2])):
            lines.append(f"- `{f1}` ↔ `{f2}`: r = {r_val:.3f}")
    else:
        lines.append("- Ninguna correlación |r| ≥ 0.9 en el conjunto actual.")

    lines.extend(["", "## 3. Cobertura por arquetipo", ""])
    arch_counts: dict[str, int] = {}
    for r in ok_rows:
        a = r.get("map_archetype") or "unknown"
        arch_counts[a] = arch_counts.get(a, 0) + 1
    for arch, n in sorted(arch_counts.items()):
        lines.append(f"- `{arch}`: {n} mapas")

    lines.extend([
        "",
        "## 4. Uso en poda",
        "",
        "Este CSV es la entrada para `select_map_space_v1.py` (Fase 3).",
        "",
        f"CSV: [`map_space_v1_features.csv`](../data/map_space_v1_features.csv)",
    ])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract map_space_v1 topology features")
    parser.add_argument("--validation-csv", type=Path, default=DEFAULT_VALIDATION_CSV)
    parser.add_argument("--map-space", type=Path, default=MAP_SPACE_ROOT)
    parser.add_argument("--output-csv", type=Path, default=FEATURES_CSV)
    parser.add_argument("--report", type=Path, default=FEATURES_REPORT)
    parser.add_argument("--no-stress", action="store_true", help="Exclude stress maps")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    run_extract(
        validation_csv=args.validation_csv,
        map_space_root=args.map_space,
        features_csv=args.output_csv,
        report_path=args.report,
        include_stress=not args.no_stress,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
