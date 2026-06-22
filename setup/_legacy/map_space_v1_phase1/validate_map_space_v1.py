#!/usr/bin/env python3
"""
validate_map_space_v1.py — Validate map_space_v1 candidates for The ONE compatibility.

Usage:
    scenarios/analysis/.venv/bin/python scenarios/setup/validate_map_space_v1.py
    scenarios/analysis/.venv/bin/python scenarios/setup/validate_map_space_v1.py --update-manifest
    scenarios/analysis/.venv/bin/python scenarios/setup/validate_map_space_v1.py --extract-features
"""

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

import yaml

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_space_topology import (  # noqa: E402
    MapRecord,
    margin_m_from_meta,
    roads_encroach_world_margin,
    spatial_coverage_ratio,
    build_road_graph,
    count_components,
    discover_maps,
    is_partition_marked,
    render_validation_preview,
    segment_length_stats,
)

SCENARIOS_DIR = _SETUP.parent
MAP_SPACE_ROOT = SCENARIOS_DIR / "map_space_v1"
DEFAULT_YAML = SCENARIOS_DIR / "analysis" / "config" / "map_design_space_v1.yaml"
VALIDATION_CSV = SCENARIOS_DIR / "analysis" / "data" / "map_space_v1_validation.csv"
VALIDATION_REPORT = SCENARIOS_DIR / "analysis" / "reports" / "map_space_v1_validation_report.md"
PREVIEWS_VALIDATION = MAP_SPACE_ROOT / "previews_validation"

VALIDATION_COLUMNS = [
    "map_id",
    "source_type",
    "anchor_id",
    "archetype",
    "generator_type",
    "wkt_dir",
    "validation_class",
    "status",
    "failure_reasons",
    "warnings",
    "n_components",
    "largest_component_ratio",
    "n_edges",
    "total_road_length_m",
    "world_size_x",
    "world_size_y",
    "preview_path",
    "validation_preview_path",
    "partition_marked",
    "installable",
    "asset_policy_ok",
    "checks_json",
]


def validation_class_to_status(vclass: str) -> str:
    mapping = {
        "valid": "PASS",
        "valid_partitioned": "PASS",
        "stress": "STRESS",
        "invalid": "FAIL",
    }
    return mapping.get(vclass, "FAIL")


def check_asset_policy(rec: MapRecord, map_space_root: Path, policy: dict[str, Any]) -> tuple[bool, list[str]]:
    """Verify auxiliary assets match map_asset_policy_v1."""
    warnings: list[str] = []
    meta = rec.meta or {}
    wkt_dir = rec.wkt_dir
    try:
        from map_asset_generator_v1 import should_generate_pois, should_generate_routes
    except ImportError:
        return True, []

    need_pois = should_generate_pois(meta, policy)
    need_routes = should_generate_routes(meta, policy)
    has_pois = (wkt_dir / "A_homes.wkt").is_file()
    has_routes = any(wkt_dir.glob("A_*.wkt")) and not has_pois or any(
        (wkt_dir / n).is_file()
        for n in ("A_bus.wkt", "A_vehicle_route.wkt", "A_ranger_patrol.wkt", "A_emergency_route.wkt")
    )

    if need_pois and not (wkt_dir / "A_homes.wkt").is_file():
        warnings.append("policy expects POIs but A_homes.wkt missing")
    if not need_pois and (wkt_dir / "A_homes.wkt").is_file():
        warnings.append("POIs present but not required by asset policy")
    if need_routes and not has_routes:
        warnings.append("policy expects routes but none found")
    return len(warnings) == 0, warnings


def load_validation_thresholds(yaml_path: Path) -> dict[str, Any]:
    if not yaml_path.is_file():
        return {"min_road_segments": 50, "min_useful_area_ratio": 0.05}
    with yaml_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("map_design_space_v1", {}).get("validation", {}).get("thresholds", {})


def validate_one(
    rec: MapRecord,
    map_space_root: Path,
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    failures: list[str] = []
    warnings: list[str] = []

    min_segments = int(thresholds.get("min_road_segments", 50))
    min_ratio = float(thresholds.get("min_useful_area_ratio", 0.05))

    roads_path = rec.roads_path
    meta_path = rec.metadata_path
    preview = rec.preview_path(map_space_root)

    checks["roads_wkt_exists"] = roads_path.is_file()
    if not checks["roads_wkt_exists"]:
        failures.append("roads.wkt missing")

    checks["metadata_exists"] = meta_path.is_file()
    if not checks["metadata_exists"]:
        failures.append("metadata.json missing")

    meta = rec.meta if rec.meta else {}
    ws = meta.get("world_size", [0, 0])
    wx, wy = int(ws[0]) if len(ws) > 0 else 0, int(ws[1]) if len(ws) > 1 else 0

    checks["world_size_positive"] = wx > 0 and wy > 0
    if not checks["world_size_positive"]:
        failures.append("worldSize not positive")

    checks["preview_exists"] = preview is not None and preview.is_file()
    if not checks["preview_exists"]:
        failures.append("preview PNG missing")

    n_components = 0
    largest_ratio = 0.0
    n_edges = 0
    total_len = 0.0
    rg = None

    if checks["roads_wkt_exists"]:
        try:
            rg = build_road_graph(roads_path)
            checks["wkt_non_empty"] = rg.graph.number_of_edges() > 0 or len(rg.segments) > 0
            if not checks["wkt_non_empty"]:
                failures.append("WKT empty")

            total_len, n_degen = segment_length_stats(rg)
            checks["no_degenerate_segments"] = n_degen == 0
            if not checks["no_degenerate_segments"]:
                failures.append(f"{n_degen} degenerate segments")

            checks["total_length_positive"] = total_len > 0
            if not checks["total_length_positive"]:
                failures.append("total road length is zero")

            min_x, min_y, max_x, max_y = rg.bbox
            checks["metric_coordinates"] = (
                all(math.isfinite(v) for v in (min_x, min_y, max_x, max_y))
                and (max_x > min_x or max_y > min_y)
            )
            if not checks["metric_coordinates"]:
                failures.append("invalid metric coordinates")

            if wx > 0 and wy > 0:
                tol = 1.0
                checks["geometry_within_world_size"] = (
                    min_x >= -tol and min_y >= -tol and max_x <= wx + tol and max_y <= wy + tol
                )
                if not checks["geometry_within_world_size"]:
                    failures.append(f"geometry exceeds worldSize ({max_x:.0f},{max_y:.0f}) vs ({wx},{wy})")

            n_edges = rg.graph.number_of_edges()
            checks["min_road_segments"] = n_edges >= min_segments
            if not checks["min_road_segments"]:
                failures.append(f"n_edges {n_edges} < {min_segments}")

            n_components, largest_ratio = count_components(rg.graph)
            partition_marked = is_partition_marked(meta)

            if n_components > 1:
                checks["partition_marked"] = partition_marked
                if not partition_marked:
                    failures.append(f"multi_component ({n_components}) without partitioned flag")
                checks["main_component"] = largest_ratio >= 0.5
            else:
                checks["partition_marked"] = True
                checks["main_component"] = True

            if wx > 0 and wy > 0:
                ratio = spatial_coverage_ratio(rg, (wx, wy))
                if ratio < min_ratio:
                    warnings.append(f"low useful_area_ratio {ratio:.4f}")
                margin_m = margin_m_from_meta(
                    meta,
                    float(thresholds.get("world_size_margin_m", 20)),
                )
                if roads_encroach_world_margin(rg, (wx, wy), margin_m):
                    warnings.append("roads near worldSize boundary")

        except Exception as exc:
            failures.append(f"graph parse error: {exc}")
            checks["wkt_non_empty"] = False
    else:
        checks["wkt_non_empty"] = False
        checks["metric_coordinates"] = False
        checks["geometry_within_world_size"] = False
        checks["no_degenerate_segments"] = False
        checks["total_length_positive"] = False
        checks["min_road_segments"] = False
        checks["main_component"] = False
        checks["partition_marked"] = False

    installable = (
        checks.get("roads_wkt_exists", False)
        and checks.get("metadata_exists", False)
        and rec.wkt_dir.is_dir()
    )
    checks["installable_to_data"] = installable
    if not installable:
        failures.append("not installable to data/")

    hard_keys = [
        "roads_wkt_exists",
        "wkt_non_empty",
        "metric_coordinates",
        "world_size_positive",
        "geometry_within_world_size",
        "no_degenerate_segments",
        "total_length_positive",
        "preview_exists",
        "metadata_exists",
        "installable_to_data",
        "min_road_segments",
        "partition_marked",
        "main_component",
    ]
    hard_ok = all(checks.get(k, False) for k in hard_keys)

    if not hard_ok:
        vclass = "invalid"
    elif n_components > 1 and is_partition_marked(meta):
        vclass = "valid_partitioned"
    elif warnings:
        vclass = "stress"
    else:
        vclass = "valid"

    status_label = validation_class_to_status(vclass)
    if warnings and status_label == "PASS":
        status_label = "WARNING"

    asset_policy_ok = True
    asset_warnings: list[str] = []
    policy_path = SCENARIOS_DIR / "analysis" / "config" / "map_asset_policy_v1.yaml"
    if policy_path.is_file():
        with policy_path.open(encoding="utf-8") as f:
            asset_policy = yaml.safe_load(f).get("map_asset_policy_v1", {})
        asset_policy_ok, asset_warnings = check_asset_policy(rec, map_space_root, asset_policy)
        warnings.extend(asset_warnings)
        if asset_warnings and status_label == "PASS":
            status_label = "WARNING"

    val_preview_rel = f"previews_validation/{rec.map_id}_validation.png"
    val_preview_path = map_space_root / val_preview_rel

    if rg is not None:
        render_validation_preview(
            rg,
            world_size=(wx, wy),
            map_id=rec.map_id,
            validation_class=vclass,
            out_path=val_preview_path,
            failure_reasons="; ".join(failures),
            warnings="; ".join(warnings),
            n_components=n_components,
        )

    return {
        "map_id": rec.map_id,
        "source_type": rec.source_type,
        "anchor_id": rec.manifest_row.get("anchor_id", meta.get("anchor_id", "")),
        "archetype": rec.archetype,
        "generator_type": rec.generator_type,
        "wkt_dir": str(rec.wkt_dir.relative_to(map_space_root)),
        "validation_class": vclass,
        "status": status_label,
        "failure_reasons": "; ".join(failures),
        "warnings": "; ".join(warnings),
        "n_components": n_components,
        "largest_component_ratio": round(largest_ratio, 4),
        "n_edges": n_edges,
        "total_road_length_m": round(total_len, 2),
        "world_size_x": wx,
        "world_size_y": wy,
        "preview_path": str(preview.relative_to(map_space_root)) if preview else "",
        "validation_preview_path": val_preview_rel,
        "partition_marked": is_partition_marked(meta),
        "installable": installable,
        "asset_policy_ok": asset_policy_ok,
        "checks_json": json.dumps(checks),
    }


def write_validation_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=VALIDATION_COLUMNS)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in VALIDATION_COLUMNS})


def update_manifest(
    manifest_path: Path,
    rows: list[dict[str, Any]],
    map_space_root: Path,
) -> None:
    existing = {}
    fieldnames: list[str] = []
    if manifest_path.is_file():
        with manifest_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            for row in reader:
                existing[row["map_id"]] = row

    for col in ("validation_class", "validation_notes"):
        if col not in fieldnames:
            fieldnames.append(col)

    by_id = {r["map_id"]: r for r in rows}
    for map_id, row in by_id.items():
        if map_id in existing:
            existing[map_id]["validation_class"] = row["validation_class"]
            existing[map_id]["validation_notes"] = row["failure_reasons"] or row["warnings"]
        else:
            existing[map_id] = {
                "map_id": map_id,
                "map_name": map_id,
                "source_type": row["source_type"],
                "source": row["source_type"],
                "archetype": row["archetype"],
                "generator_type": row["generator_type"],
                "wkt_dir": row["wkt_dir"],
                "roads_wkt": f"{row['wkt_dir']}/roads.wkt",
                "world_size_x": row["world_size_x"],
                "world_size_y": row["world_size_y"],
                "crs": "",
                "bbox_or_generator_params": "",
                "seed": "",
                "status": row["status"],
                "notes": "discovered_by_validation",
                "validation_class": row["validation_class"],
                "validation_notes": row["failure_reasons"] or row["warnings"],
            }

    if not fieldnames:
        fieldnames = [
            "map_id", "map_name", "source_type", "source", "archetype", "generator_type",
            "wkt_dir", "roads_wkt", "world_size_x", "world_size_y", "crs",
            "bbox_or_generator_params", "seed", "status", "notes",
            "validation_class", "validation_notes",
        ]

    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for map_id in sorted(existing.keys()):
            w.writerow(existing[map_id])


def write_validation_report(
    rows: list[dict[str, Any]],
    manifest_ids: set[str],
    path: Path,
) -> None:
    counts = Counter(r["validation_class"] for r in rows)
    disk_ids = {r["map_id"] for r in rows}
    orphans = disk_ids - manifest_ids

    lines = [
        "# map_space_v1 — Informe de validación",
        "",
        f"**Fecha:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        f"**Mapas validados:** {len(rows)}",
        "",
        "## 1. Resumen por clase",
        "",
        "| Clase | Count |",
        "|-------|------:|",
    ]
    for cls in ("valid", "valid_partitioned", "stress", "invalid"):
        lines.append(f"| {cls} | {counts.get(cls, 0)} |")

    invalid_rows = [r for r in rows if r["validation_class"] == "invalid"]
    if invalid_rows:
        lines.extend(["", "## 2. Mapas inválidos", ""])
        for r in invalid_rows:
            lines.append(f"- **{r['map_id']}**: {r['failure_reasons']}")

    stress_rows = [r for r in rows if r["validation_class"] == "stress"]
    if stress_rows:
        lines.extend(["", "## 3. Mapas stress (warnings)", ""])
        for r in stress_rows:
            lines.append(f"- **{r['map_id']}**: {r['warnings']}")

    if orphans:
        lines.extend(["", "## 4. Mapas huérfanos (disco, no en manifest original)", ""])
        for oid in sorted(orphans):
            lines.append(f"- `{oid}`")

    lines.extend([
        "",
        "## 5. Política partitioned",
        "",
        "Mapas con `n_components > 1` requieren `topology_flags` con `partitioned` en metadata.",
        "Clase `valid_partitioned` = checks hard OK + flag presente.",
        "",
        "## 6. Próximo paso",
        "",
        "Ejecutar `extract_map_features_v1.py` y luego `select_map_space_v1.py` (Fase 3).",
        "",
        f"CSV: [`map_space_v1_validation.csv`](../data/map_space_v1_validation.csv)",
    ])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate map_space_v1 candidates")
    parser.add_argument("--map-space", type=Path, default=MAP_SPACE_ROOT)
    parser.add_argument("--design-space", type=Path, default=DEFAULT_YAML)
    parser.add_argument("--output-csv", type=Path, default=VALIDATION_CSV)
    parser.add_argument("--report", type=Path, default=VALIDATION_REPORT)
    parser.add_argument("--update-manifest", action="store_true")
    parser.add_argument("--extract-features", action="store_true")
    args = parser.parse_args()

    map_space_root = args.map_space.resolve()
    manifest_path = map_space_root / "manifest_maps.csv"
    manifest_ids = set(load_manifest_ids(manifest_path))

    thresholds = load_validation_thresholds(args.design_space)
    records = discover_maps(map_space_root, manifest_path)

    rows = [validate_one(rec, map_space_root, thresholds) for rec in records]
    write_validation_csv(rows, args.output_csv)
    write_validation_report(rows, manifest_ids, args.report)

    if args.update_manifest:
        update_manifest(manifest_path, rows, map_space_root)

    counts = Counter(r["validation_class"] for r in rows)
    print(f"Validated {len(rows)} maps → {args.output_csv}")
    for cls, n in sorted(counts.items()):
        print(f"  {cls}: {n}")

    if args.extract_features:
        from extract_map_features_v1 import run_extract  # noqa: WPS433

        run_extract(validation_csv=args.output_csv, map_space_root=map_space_root)


def load_manifest_ids(manifest_path: Path) -> set[str]:
    if not manifest_path.is_file():
        return set()
    with manifest_path.open(encoding="utf-8") as f:
        return {row["map_id"] for row in csv.DictReader(f)}


if __name__ == "__main__":
    main()
