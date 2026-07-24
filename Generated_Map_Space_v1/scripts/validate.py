#!/usr/bin/env python3
"""Validate map_space_revised_v2 (GMS-v1) maps before feature extraction."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
_PACK = _SCRIPTS.parent
_SCENARIOS = _PACK.parent
_SETUP = _SCENARIOS / "setup"
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import parse_linestrings, wkt_to_sim_coords  # noqa: E402


SCENARIOS_DIR = _SCENARIOS
MAP_SPACE_ROOT = _PACK
MANIFEST_CSV = MAP_SPACE_ROOT / "manifest_maps_all.csv"
VALIDATION_CSV = MAP_SPACE_ROOT / "data" / "map_space_revised_v2_validation.csv"
VALIDATION_REPORT = MAP_SPACE_ROOT / "docs" / "map_space_revised_v2_validation_report.md"

CSV_COLUMNS = [
    "map_id",
    "batch_target",
    "source_type",
    "anchor_id",
    "archetype",
    "generator_type",
    "status",
    "reason",
    "n_lines",
    "n_vertices",
    "n_components",
    "largest_component_ratio",
    "total_road_length_m",
    "world_size_x",
    "world_size_y",
    "world_area",
    "notes",
]

ALLOWED_REASONS = {
    "empty_wkt",
    "too_few_edges",
    "disconnected_unmarked",
    "coordinates_outside_world",
    "invalid_world_size",
    "degenerate_segments",
    "missing_metadata",
    "missing_preview",
    "osm_download_failed",
    "other",
}


@dataclass
class ValidationThresholds:
    min_nodes: int = 20
    min_edges: int = 20
    min_total_length_m: float = 200.0
    degenerate_len_m: float = 1e-6
    coord_tol_m: float = 1.0
    stress_largest_component_ratio: float = 0.8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate map_space_revised_v2 (GMS-v1) maps")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_CSV)
    parser.add_argument("--output-csv", type=Path, default=VALIDATION_CSV)
    parser.add_argument("--output-report", type=Path, default=VALIDATION_REPORT)
    parser.add_argument("--map-root", type=Path, default=MAP_SPACE_ROOT)
    parser.add_argument("--min-nodes", type=int, default=20)
    parser.add_argument("--min-edges", type=int, default=20)
    parser.add_argument("--min-total-length-m", type=float, default=200.0)
    return parser.parse_args()


def read_manifest(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Manifest not found: {path}")
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_bbox_or_params(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def compute_graph_metrics(
    sim_lines: list[list[tuple[float, float]]],
    *,
    degenerate_len_m: float,
) -> dict[str, Any]:
    node_to_id: dict[tuple[float, float], int] = {}
    adjacency: dict[int, set[int]] = defaultdict(set)
    total_len = 0.0
    degenerate = 0
    n_edges = 0

    def node_id(pt: tuple[float, float]) -> int:
        if pt not in node_to_id:
            node_to_id[pt] = len(node_to_id)
        return node_to_id[pt]

    for line in sim_lines:
        for i in range(len(line) - 1):
            a = line[i]
            b = line[i + 1]
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            if length < degenerate_len_m:
                degenerate += 1
                continue
            ida = node_id(a)
            idb = node_id(b)
            adjacency[ida].add(idb)
            adjacency[idb].add(ida)
            total_len += length
            n_edges += 1

    n_nodes = len(node_to_id)

    # Connected components over adjacency.
    seen: set[int] = set()
    comp_sizes: list[int] = []
    for nid in adjacency:
        if nid in seen:
            continue
        stack = [nid]
        seen.add(nid)
        size = 0
        while stack:
            cur = stack.pop()
            size += 1
            for nxt in adjacency[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        comp_sizes.append(size)

    n_components = len(comp_sizes) if comp_sizes else 0
    largest_ratio = (max(comp_sizes) / n_nodes) if n_nodes > 0 and comp_sizes else 0.0

    return {
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "n_components": n_components,
        "largest_component_ratio": largest_ratio,
        "total_road_length_m": total_len,
        "degenerate_segments": degenerate,
    }


def validate_one(
    row: dict[str, str],
    *,
    map_root: Path,
    th: ValidationThresholds,
) -> dict[str, str]:
    map_id = row.get("map_id", "")
    source_type = row.get("source_type", "")
    batch_target = row.get("batch_target", "")
    anchor_id = row.get("anchor_id", "")
    archetype = row.get("archetype", "")
    generator_type = row.get("generator_type", "")
    generation_status = row.get("generation_status", "")
    generation_notes = row.get("generation_notes", "")

    wkt_rel = row.get("wkt_dir", "")
    roads_rel = row.get("roads_wkt", "")
    preview_rel = row.get("preview_png", "")
    meta_rel = row.get("metadata_json", "")
    crs = row.get("crs", "")
    wkt_path_abs = (row.get("wkt_path") or "").strip()
    metadata_path_abs = (row.get("metadata_path") or "").strip()

    wkt_dir = map_root / wkt_rel if wkt_rel else None
    if roads_rel:
        roads_path = map_root / roads_rel
    elif wkt_path_abs:
        roads_path = Path(wkt_path_abs)
    elif wkt_dir:
        roads_path = wkt_dir / "roads.wkt"
    else:
        roads_path = None
    preview_path = map_root / preview_rel if preview_rel else (map_root / "previews" / f"{map_id}.png")
    if meta_rel:
        metadata_path = map_root / meta_rel
    elif metadata_path_abs:
        metadata_path = Path(metadata_path_abs)
    elif roads_path is not None:
        metadata_path = roads_path.parent / "metadata.json"
    elif wkt_dir:
        metadata_path = wkt_dir / "metadata.json"
    else:
        metadata_path = None

    # Defaults for output fields.
    status = "PASS"
    reasons: list[str] = []
    notes: list[str] = []
    n_lines = 0
    n_vertices = 0
    n_components = 0
    largest_component_ratio = 0.0
    total_road_length_m = 0.0
    world_size_x = int(row.get("world_size_x", "0") or 0)
    world_size_y = int(row.get("world_size_y", "0") or 0)

    _early_fail = (
        "FAIL_DOWNLOAD",
        "FAIL_DOWNLOAD_TRANSIENT",
        "FAIL_DOWNLOAD_PERMANENT",
        "FAIL_DOWNLOAD_SKIPPED",
        "FAIL_BUILD_OSM",
        "FAIL_BUILD_SYNTHETIC_DEGENERATE",
    )
    if generation_status in _early_fail:
        status = "FAIL"
        reasons.append("generation_failed")
        notes.append(generation_notes or generation_status or "generation failed")
        if metadata_path and metadata_path.is_file():
            try:
                meta = json.loads(metadata_path.read_text(encoding="utf-8"))
                ws = meta.get("world_size", [world_size_x, world_size_y])
                if isinstance(ws, list) and len(ws) >= 2:
                    world_size_x = int(ws[0] or 0)
                    world_size_y = int(ws[1] or 0)
            except Exception:
                pass
        return {
            "map_id": map_id,
            "batch_target": batch_target,
            "source_type": source_type,
            "anchor_id": anchor_id,
            "archetype": archetype,
            "generator_type": generator_type,
            "status": status,
            "reason": ";".join(reasons),
            "n_lines": str(n_lines),
            "n_vertices": str(n_vertices),
            "n_components": str(n_components),
            "largest_component_ratio": f"{largest_component_ratio:.6f}",
            "total_road_length_m": f"{total_road_length_m:.6f}",
            "world_size_x": str(world_size_x),
            "world_size_y": str(world_size_y),
            "world_area": str(max(0, world_size_x * world_size_y)),
            "notes": " | ".join(notes),
        }

    # Metadata check
    meta: dict[str, Any] = {}
    if metadata_path is None or not metadata_path.is_file():
        reasons.append("missing_metadata")
        status = "FAIL"
    else:
        try:
            meta = json.loads(metadata_path.read_text(encoding="utf-8"))
            ws = meta.get("world_size", [world_size_x, world_size_y])
            if isinstance(ws, list) and len(ws) >= 2:
                world_size_x = int(ws[0] or 0)
                world_size_y = int(ws[1] or 0)
            if not crs:
                crs = str(meta.get("crs") or (meta.get("generator_params") or {}).get("crs") or "")
        except Exception as exc:
            reasons.append("other")
            notes.append(f"metadata parse error: {exc}")
            status = "FAIL"

    # Preview check (warning if rest is valid).
    if preview_path is None or not preview_path.is_file():
        if status != "FAIL":
            status = "WARNING"
        reasons.append("missing_preview")

    # world size check
    if world_size_x <= 0 or world_size_y <= 0:
        status = "FAIL"
        reasons.append("invalid_world_size")

    # roads / WKT checks
    raw_lines: list[list[tuple[float, float]]] = []
    sim_lines: list[list[tuple[float, float]]] = []
    if roads_path is None or not roads_path.is_file():
        status = "FAIL"
        reasons.append("empty_wkt")
    else:
        try:
            raw_lines = parse_linestrings(roads_path)
            sim_lines = wkt_to_sim_coords(raw_lines)
        except Exception as exc:
            status = "FAIL"
            reasons.append("empty_wkt")
            notes.append(f"WKT parse error: {exc}")

    n_lines = len(sim_lines)
    n_vertices = sum(len(line) for line in sim_lines)
    if n_lines == 0 or n_vertices == 0:
        status = "FAIL"
        reasons.append("empty_wkt")

    # finite/metric and bounds checks
    if sim_lines:
        finite_ok = True
        max_x = 0.0
        max_y = 0.0
        for line in sim_lines:
            for x, y in line:
                if not (math.isfinite(x) and math.isfinite(y)):
                    finite_ok = False
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y
        if not finite_ok:
            status = "FAIL"
            reasons.append("other")
            notes.append("non-finite coordinates")
        if world_size_x > 0 and world_size_y > 0:
            if max_x > world_size_x + th.coord_tol_m or max_y > world_size_y + th.coord_tol_m:
                status = "FAIL"
                reasons.append("coordinates_outside_world")

    metrics = compute_graph_metrics(sim_lines, degenerate_len_m=th.degenerate_len_m) if sim_lines else {}
    n_edges = int(metrics.get("n_edges", 0))
    n_nodes = int(metrics.get("n_nodes", 0))
    n_components = int(metrics.get("n_components", 0))
    largest_component_ratio = float(metrics.get("largest_component_ratio", 0.0))
    total_road_length_m = float(metrics.get("total_road_length_m", 0.0))
    degenerate = int(metrics.get("degenerate_segments", 0))

    if degenerate > 0:
        status = "FAIL"
        reasons.append("degenerate_segments")
        notes.append(f"degenerate_segments={degenerate}")

    if n_edges < th.min_edges:
        status = "FAIL"
        reasons.append("too_few_edges")
        notes.append(f"n_edges={n_edges} < {th.min_edges}")

    if n_nodes < th.min_nodes:
        status = "FAIL"
        reasons.append("other")
        notes.append(f"n_nodes={n_nodes} < {th.min_nodes}")

    if total_road_length_m < th.min_total_length_m:
        status = "FAIL"
        reasons.append("other")
        notes.append(f"total_road_length_m={total_road_length_m:.2f} < {th.min_total_length_m:.2f}")

    bbox_or_params = parse_bbox_or_params(row.get("bbox_or_params", ""))
    # Revised v2 stores params under metadata.generator_params
    if not bbox_or_params and isinstance(meta.get("generator_params"), dict):
        bbox_or_params = dict(meta.get("generator_params") or {})
    partitioned = bool(
        bbox_or_params.get("_allow_partitioned", False)
        or meta.get("_allow_partitioned", False)
        or (isinstance(meta.get("topology_flags"), list) and "partitioned" in (meta.get("topology_flags") or []))
        or str(meta.get("archetype") or archetype) == "island_or_partitioned"
    )
    if not partitioned and n_components > 1:
        # Revised v2: keep multi-component maps in saturation pool as STRESS
        # (geometry exists; planner attrition already documented separately).
        if status != "FAIL":
            status = "STRESS"
        reasons.append("disconnected_unmarked")
        notes.append(f"multi_component_unmarked n_components={n_components}")
    elif partitioned and n_components > 1:
        if status == "PASS" and largest_component_ratio < th.stress_largest_component_ratio:
            status = "STRESS"
        notes.append(f"partitioned_allowed n_components={n_components}")

    # OSM-specific checks (CRS / bbox from metadata when manifest columns absent)
    if source_type == "osm":
        if not crs:
            status = "FAIL"
            reasons.append("other")
            notes.append("missing CRS for OSM")
        has_bbox_like = any(
            k in bbox_or_params
            for k in ("center_lat", "center_lon", "width_m", "height_m", "window_size_m")
        ) or bool(meta.get("bbox_latlon") or meta.get("bbox_m"))
        if not has_bbox_like:
            status = "FAIL"
            reasons.append("other")
            notes.append("missing bbox/center params for OSM")

    # Stress heuristic for non-fail maps.
    if status != "FAIL":
        if n_components > 1 and largest_component_ratio < th.stress_largest_component_ratio:
            status = "STRESS"
        elif "missing_preview" in reasons:
            status = "WARNING"
        else:
            status = "PASS"

    # normalize reasons
    normalized = []
    for r in reasons:
        if r in ALLOWED_REASONS and r not in normalized:
            normalized.append(r)
    if not normalized and status != "PASS":
        normalized = ["other"]

    return {
        "map_id": map_id,
        "batch_target": batch_target,
        "source_type": source_type,
        "anchor_id": anchor_id,
        "archetype": archetype,
        "generator_type": generator_type,
        "status": status,
        "reason": ";".join(normalized),
        "n_lines": str(n_lines),
        "n_vertices": str(n_vertices),
        "n_components": str(n_components),
        "largest_component_ratio": f"{largest_component_ratio:.6f}",
        "total_road_length_m": f"{total_road_length_m:.6f}",
        "world_size_x": str(world_size_x),
        "world_size_y": str(world_size_y),
        "world_area": str(max(0, world_size_x * world_size_y)),
        "notes": " | ".join(notes),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def grouped_counts(rows: list[dict[str, str]], key: str) -> dict[str, Counter]:
    out: dict[str, Counter] = {}
    for r in rows:
        k = r.get(key, "")
        st = r.get("status", "")
        out.setdefault(k, Counter())
        out[k][st] += 1
    return out


def recommend_batch_usability(batch_rows: list[dict[str, str]]) -> str:
    total = len(batch_rows)
    fails = sum(1 for r in batch_rows if r["status"] == "FAIL")
    if total == 0:
        return "no_data"
    fail_ratio = fails / total
    if fail_ratio <= 0.10:
        return "usable_for_features"
    if fail_ratio <= 0.30:
        return "usable_with_caution"
    return "not_recommended_for_features"


def write_report(path: Path, rows: list[dict[str, str]], th: ValidationThresholds) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    by_batch = grouped_counts(rows, "batch_target")
    by_source = grouped_counts(rows, "source_type")
    by_arch = grouped_counts(rows, "archetype")

    fail_rows = [r for r in rows if r["status"] == "FAIL"]
    risk_rows = [r for r in rows if r["status"] in ("WARNING", "STRESS")]

    lines: list[str] = []
    lines.append("# map_space_saturation_validation_report")
    lines.append("")
    lines.append(f"- total_maps_validated: {len(rows)}")
    lines.append("")
    lines.append("## Resumen por batch")
    lines.append("")
    for batch in sorted(by_batch.keys(), key=lambda x: int(x or 0)):
        cnt = by_batch[batch]
        batch_rows = [r for r in rows if r["batch_target"] == batch]
        recommendation = recommend_batch_usability(batch_rows)
        lines.append(
            f"- batch_{int(batch):04d}: PASS={cnt['PASS']} WARNING={cnt['WARNING']} "
            f"STRESS={cnt['STRESS']} FAIL={cnt['FAIL']} -> {recommendation}"
        )

    lines.append("")
    lines.append("## Resumen por source_type")
    lines.append("")
    for src in sorted(by_source.keys()):
        cnt = by_source[src]
        lines.append(
            f"- {src}: PASS={cnt['PASS']} WARNING={cnt['WARNING']} STRESS={cnt['STRESS']} FAIL={cnt['FAIL']}"
        )

    lines.append("")
    lines.append("## Resumen por archetype")
    lines.append("")
    for arch in sorted(by_arch.keys()):
        cnt = by_arch[arch]
        lines.append(
            f"- {arch}: PASS={cnt['PASS']} WARNING={cnt['WARNING']} STRESS={cnt['STRESS']} FAIL={cnt['FAIL']}"
        )

    lines.append("")
    lines.append("## Mapas FAIL y motivo")
    lines.append("")
    if not fail_rows:
        lines.append("- none")
    else:
        for r in fail_rows:
            lines.append(f"- {r['map_id']}: {r['reason']} ({r['notes']})")

    lines.append("")
    lines.append("## Mapas WARNING/STRESS")
    lines.append("")
    if not risk_rows:
        lines.append("- none")
    else:
        for r in risk_rows:
            lines.append(f"- {r['map_id']} [{r['status']}]: {r['reason']} ({r['notes']})")

    lines.append("")
    lines.append("## Criterios de aceptación usados")
    lines.append("")
    lines.append(f"- min_nodes: {th.min_nodes}")
    lines.append(f"- min_edges: {th.min_edges}")
    lines.append(f"- min_total_length_m: {th.min_total_length_m}")
    lines.append("- world_size_x/world_size_y > 0")
    lines.append("- coords within worldSize (tol 1m)")
    lines.append("- no degenerate segments (<1e-6m)")
    lines.append("- disconnected_unmarked => FAIL")
    lines.append("- partitioned allowed but documented")
    lines.append("")
    lines.append("## Recomendación de usabilidad por batch")
    lines.append("")
    for batch in sorted(by_batch.keys(), key=lambda x: int(x or 0)):
        batch_rows = [r for r in rows if r["batch_target"] == batch]
        lines.append(f"- batch_{int(batch):04d}: {recommend_batch_usability(batch_rows)}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    th = ValidationThresholds(
        min_nodes=int(args.min_nodes),
        min_edges=int(args.min_edges),
        min_total_length_m=float(args.min_total_length_m),
    )

    manifest_rows = read_manifest(args.manifest)
    validated = [validate_one(r, map_root=args.map_root, th=th) for r in manifest_rows]

    # One row per manifest map.
    validated.sort(key=lambda x: x["map_id"])
    write_csv(args.output_csv, validated)
    write_report(args.output_report, validated, th)

    status_counts = Counter(r["status"] for r in validated)
    print(
        f"Validated {len(validated)} maps -> PASS={status_counts['PASS']} "
        f"WARNING={status_counts['WARNING']} STRESS={status_counts['STRESS']} FAIL={status_counts['FAIL']}"
    )
    print(f"CSV: {args.output_csv}")
    print(f"Report: {args.output_report}")


if __name__ == "__main__":
    main()

