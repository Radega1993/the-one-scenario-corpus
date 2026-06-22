#!/usr/bin/env python3
"""
generate_map_space_saturation_v1.py

Batch-oriented map candidate generation (OSM anchors + synthetic topology
generators) controlled by:
  - scenarios/analysis/config/map_design_space_saturation_v1.yaml
  - scenarios/analysis/data/map_archetype_definitions_v1.csv

Outputs:
  scenarios/map_space_saturation_v1/
    batch_0100/
    batch_0200/
    batch_0400/
    batch_0600/
    batch_0800/
    manifest_maps_all.csv
    generation_config_used.yaml
    README.md
    previews/

This script is generation-only in this phase: it writes `roads.wkt`,
`metadata.json` and `preview.png`. It does not generate POIs or routes.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import os
import random
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")


REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_DIR = REPO_ROOT / "scenarios"
SETUP_DIR = SCENARIOS_DIR / "setup"

DEFAULT_DESIGN_SPACE_YAML = SCENARIOS_DIR / "analysis" / "config" / "map_design_space_saturation_v1.yaml"
DEFAULT_ARCHETYPE_CSV = SCENARIOS_DIR / "analysis" / "data" / "map_archetype_definitions_v1.csv"
DEFAULT_OUTPUT_ROOT = SCENARIOS_DIR / "map_space_saturation_v1"

BATCH_TARGETS = [100, 200, 400, 600, 800, 1000, 1200, 1600, 2000]

OSM_QUEUE_PATH_NAME = "osm_download_queue.csv"

# Legacy status names mapped to v2 pipeline statuses (for manifest migration).
LEGACY_STATUS_MAP = {
    "FAIL_DOWNLOAD": "FAIL_DOWNLOAD_TRANSIENT",
    "FAIL_BUILD": "FAIL_BUILD_OSM",
    "PLANNED": "PLANNED",
    "OK": "OK",
    "SKIPPED_EXISTING_OK": "SKIPPED_EXISTING_OK",
}

# Asegura que `map_geometry.py` sea importable.
if str(SETUP_DIR) not in sys.path:
    sys.path.insert(0, str(SETUP_DIR))


MANIFEST_COLUMNS = [
    "map_id",
    "batch_target",
    "source_type",
    "anchor_id",
    "anchor_label",
    "archetype",
    "generator_type",
    "wkt_dir",
    "roads_wkt",
    "preview_png",
    "metadata_json",
    "world_size_x",
    "world_size_y",
    "crs",
    "network_type",
    "bbox_or_params",
    "seed",
    "generation_status",
    "generation_notes",
]


def _stable_int(*parts: Any, bits: int = 64) -> int:
    """
    Deterministic integer from SHA-256 (never Python hash()).
    """
    import hashlib

    msg = "::".join("" if p is None else str(p) for p in parts).encode("utf-8")
    digest = hashlib.sha256(msg).digest()
    take = bits // 8
    return int.from_bytes(digest[:take], "big", signed=False)


def stable_seed_u32(global_seed: int, *parts: Any) -> int:
    return int(_stable_int(global_seed, *parts, bits=32))


def stable_unit_float(global_seed: int, *parts: Any) -> float:
    # Map stable 64-bit integer into [0,1).
    v = _stable_int(global_seed, *parts, bits=64)
    return v / 2**64


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"YAML at {path} did not parse to dict")
    return data


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(path)
    by_id: dict[str, dict[str, str]] = {}
    for r in rows:
        mid = r.get("map_id")
        if mid:
            by_id[mid] = r
    return by_id


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


def append_generation_note(existing: dict[str, str], note: str) -> None:
    prev = existing.get("generation_notes", "") or ""
    if prev:
        existing["generation_notes"] = prev + " | " + note
    else:
        existing["generation_notes"] = note


def stage_target_for_index(idx_0_based: int) -> int:
    # idx_0_based=0 maps to batch_0100.
    n = idx_0_based + 1
    for t in BATCH_TARGETS:
        if n <= t:
            return t
    raise ValueError(f"idx_0_based={idx_0_based} exceeds supported target totals ({BATCH_TARGETS[-1]})")


def meters_to_degrees(lat: float, width_m: float, height_m: float) -> tuple[float, float, float, float]:
    """
    Convert meters bbox around (lat,lon) center into degrees bbox.
    Returns (north, south, east, west).
    """
    m_per_deg_lat = 111_320.0
    lat_rad = math.radians(lat)
    m_per_deg_lon = 111_320.0 * math.cos(lat_rad)
    half_h = (height_m / 2.0) / m_per_deg_lat
    half_w = (width_m / 2.0) / m_per_deg_lon if m_per_deg_lon != 0 else 0.0
    north = lat + half_h
    south = lat - half_h
    # caller uses (east, west) from lon +/- half_w
    return north, south, half_w, half_w


def offset_latlon(lat: float, lon: float, distance_m: float, direction: str) -> tuple[float, float]:
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat))
    dlat = distance_m / m_per_deg_lat
    dlon = distance_m / m_per_deg_lon if m_per_deg_lon != 0 else 0.0

    if direction == "offset_n":
        return lat + dlat, lon
    if direction == "offset_s":
        return lat - dlat, lon
    if direction == "offset_e":
        return lat, lon + dlon
    if direction == "offset_w":
        return lat, lon - dlon
    raise ValueError(f"Unknown offset direction: {direction}")


def eligible_window_sizes_for_anchor(anchor: dict[str, Any], osm_policy: dict[str, Any]) -> list[int]:
    window_sizes = [int(x) for x in osm_policy.get("window_sizes_m", [1000, 1500, 2500])]
    by_use = osm_policy.get("window_size_by_expected_use", {}) or {}
    uses = anchor.get("expected_use", []) or []
    sizes: set[int] = set()
    for use in uses:
        for key, vals in by_use.items():
            if key in str(use):
                for v in vals:
                    sizes.add(int(v))
    if not sizes:
        return window_sizes
    return sorted(sizes)


def cartesian_param_count(generator: dict[str, Any]) -> int:
    params = generator.get("parameters", {}) or {}
    keys = sorted(params.keys())
    sizes = []
    for k in keys:
        v = params[k]
        if isinstance(v, list):
            sizes.append(len(v))
        else:
            sizes.append(1)
    total = 1
    for s in sizes:
        total *= max(1, int(s))
    return int(total)


def pick_params_by_index(generator: dict[str, Any], index: int) -> dict[str, Any]:
    """
    Deterministic parameter picking: maps a non-negative `index` into a
    parameter cartesian product using mixed radix.
    """
    params = generator.get("parameters", {}) or {}
    keys = sorted(params.keys())
    # Mixed radix: keep stable key order
    out: dict[str, Any] = {}
    idx = int(index)
    for k in keys:
        vals = params[k]
        if isinstance(vals, list) and vals:
            base = len(vals)
            pick_i = idx % base
            out[k] = vals[pick_i]
            idx //= base
        else:
            out[k] = vals
    return out


@dataclass(frozen=True)
class PlannedCandidate:
    map_id: str
    batch_target: int
    source_type: str  # osm | synthetic | trace_reference_synthetic
    anchor_id: str
    anchor_label: str
    archetype: str
    generator_type: str  # empty for osm
    crs: str
    network_type: str  # anchor network_type for osm else "synthetic"
    wkt_dir: Path
    osm_raw_dir: Path | None
    preview_dir: Path
    bbox_or_params_obj: Any
    generator_params: dict[str, Any] | None
    anchor_variant_type: str | None
    anchor_distance_m: float | None
    window_size_m: float | None
    center_lat: float | None
    center_lon: float | None
    cand_seed: int
    generation_key: str  # for determinism/debugging


def normalize_generation_status(status: str) -> str:
    return LEGACY_STATUS_MAP.get(status, status)


def map_wkt_ok(wkt_dir: Path) -> bool:
    return (wkt_dir / "roads.wkt").is_file() and (wkt_dir / "metadata.json").is_file()


def compute_plan(
    *,
    design_space: dict[str, Any],
    global_seed: int,
    target_total: int,
    output_root: Path,
    osm_cache_use_cache: bool = True,  # placeholder: we always pass use_cache=True to legacy generator
) -> list[PlannedCandidate]:
    if target_total <= 0:
        return []

    ds = design_space["map_design_space_saturation_v1"]
    anchors = ds["real_anchors"]["anchors"]
    osm_policy = ds["osm_generation_policy"]
    syn_policy = ds["synthetic_generation_policy"]

    osm_allowed_anchor_types = set(osm_policy.get("anchor_types_allowed", ["osm_bbox", "osm_place"]))

    osm_anchors = []
    for a in anchors:
        if a.get("anchor_type") not in osm_allowed_anchor_types:
            continue
        if not a.get("bbox"):
            continue
        osm_anchors.append(a)
    if not osm_anchors:
        raise RuntimeError("No OSM anchors available for osm_generation_policy constraints")

    # Stable order by anchor_id for determinism.
    osm_anchors.sort(key=lambda x: str(x.get("anchor_id", "")))

    generators = syn_policy.get("generators", []) or []
    if not generators:
        raise RuntimeError("synthetic_generation_policy.generators empty")
    generators.sort(key=lambda g: str(g.get("generator_id", "")))

    # Trace-only anchors (synthetic generation only).
    trace_anchors = [a for a in anchors if a.get("anchor_type") == "trace_reference_not_map"]
    trace_ref_mapping = syn_policy.get("trace_reference_mapping", {}) or {}
    trace_generator_to_anchors: dict[str, list[dict[str, Any]]] = {}
    for a in trace_anchors:
        gen_id = trace_ref_mapping.get(a.get("anchor_id"))
        if gen_id:
            trace_generator_to_anchors.setdefault(str(gen_id), []).append(a)

    for gen_id, arr in trace_generator_to_anchors.items():
        arr.sort(key=lambda x: str(x.get("anchor_id", "")))

    osm_fraction = float(ds["batch_generation_policy"]["batch_composition"]["osm_fraction"])
    if osm_fraction <= 0 or osm_fraction >= 1:
        raise ValueError(f"Expected osm_fraction in (0,1), got: {osm_fraction}")

    # Prepare deterministic iterators
    variant_dirs = ["exact", "offset_n", "offset_e", "offset_s", "offset_w"]
    offsets = [int(x) for x in osm_policy.get("offset_distances_m", [0, 200, 500, 1000, 1500])]
    max_offset = int(float(osm_policy.get("max_offset_from_anchor_m", 2000)))
    offsets_nonzero = [o for o in offsets if int(o) > 0 and int(o) <= max_offset]
    if not offsets_nonzero:
        offsets_nonzero = [200]

    osm_counter = 0
    syn_counter = 0
    generator_local_counter: dict[str, int] = {}
    trace_anchor_local_counter: dict[str, int] = {}

    candidates: list[PlannedCandidate] = []

    for idx in range(target_total):
        batch_target = stage_target_for_index(idx)
        batch_dir = output_root / f"batch_{batch_target:04d}"
        wkt_dir = batch_dir / "wkt" / f"map_{idx:04d}"
        preview_dir = output_root / "previews"

        # Candidate mix
        u = stable_unit_float(global_seed, "mix", idx)
        is_osm = u < osm_fraction

        if is_osm:
            anchor = osm_anchors[osm_counter % len(osm_anchors)]
            osm_counter += 1

            anchor_id = str(anchor.get("anchor_id", ""))
            anchor_label = str(anchor.get("label", anchor_id))
            archetype = str(anchor.get("archetype", ""))
            crs = str(anchor.get("crs", "EPSG:3067"))
            network_type = str(anchor.get("network_type", "drive"))

            eligible_windows = eligible_window_sizes_for_anchor(anchor, osm_policy)
            variant_type = variant_dirs[osm_counter % len(variant_dirs)]
            window_size_m = float(eligible_windows[(osm_counter // len(variant_dirs)) % len(eligible_windows)])

            if variant_type == "exact":
                offset_m = 0.0
                direction = "exact"
            else:
                offset_m = float(offsets_nonzero[(osm_counter // (len(variant_dirs) * len(eligible_windows))) % len(offsets_nonzero)])
                direction = variant_type

            bbox = anchor.get("bbox") or {}
            center_lat = (float(bbox["south"]) + float(bbox["north"])) / 2.0
            center_lon = (float(bbox["west"]) + float(bbox["east"])) / 2.0
            if direction != "exact":
                center_lat, center_lon = offset_latlon(center_lat, center_lon, offset_m, direction)

            # MapCandidate compatible parameters (legacy generator expects these keys).
            params = {
                "center_lat": round(center_lat, 6),
                "center_lon": round(center_lon, 6),
                "width_m": int(window_size_m),
                "height_m": int(window_size_m),
                "variant_type": variant_type,
                "anchor_distance_m": float(offset_m),
                "window_size_m": float(window_size_m),
                "osm_network_type": network_type,
            }

            # Allow partitioned output when expected topology suggests multiple components.
            allow_partitioned = False
            topology_flags: list[str] = []
            exp_topo = anchor.get("expected_topology", {}) or {}
            if "n_components_min" in exp_topo:
                try:
                    if int(exp_topo["n_components_min"]) >= 2:
                        allow_partitioned = True
                        topology_flags.append("partitioned")
                except (TypeError, ValueError):
                    pass
            if not allow_partitioned:
                expected_use = anchor.get("expected_use", []) or []
                if any("partition" in str(u) for u in expected_use):
                    allow_partitioned = True
                    topology_flags.append("partitioned")

            # Deterministic map_id includes idx so extension keeps a stable prefix.
            map_id = f"OSM_{anchor_id}_{variant_type}_{int(window_size_m)}m_{int(offset_m)}m_{idx:04d}"
            map_seed = stable_seed_u32(global_seed, map_id)

            planned = PlannedCandidate(
                map_id=map_id,
                batch_target=batch_target,
                source_type="osm",
                anchor_id=anchor_id,
                anchor_label=anchor_label,
                archetype=archetype,
                generator_type="",
                crs=crs,
                network_type=network_type,
                wkt_dir=wkt_dir,
                osm_raw_dir=batch_dir / "raw_osm",
                preview_dir=preview_dir,
                bbox_or_params_obj=params,
                generator_params=None,
                anchor_variant_type=variant_type,
                anchor_distance_m=float(offset_m),
                window_size_m=float(window_size_m),
                center_lat=float(center_lat),
                center_lon=float(center_lon),
                cand_seed=map_seed,
                generation_key="osm",
            )
            # Attach extra legacy-required fields by embedding into bbox_or_params_obj.
            # We will reconstruct MapCandidate from these fields during generation.
            # Store allow_partitioned/topology_flags by packing into bbox_or_params_obj.
            planned_bbox = dict(planned.bbox_or_params_obj)
            planned_bbox["_allow_partitioned"] = allow_partitioned
            planned_bbox["_topology_flags"] = topology_flags
            planned = PlannedCandidate(**{**planned.__dict__, "bbox_or_params_obj": planned_bbox})
            candidates.append(planned)
            continue

        # Synthetic candidate
        gen = generators[syn_counter % len(generators)]
        syn_counter += 1

        gen_id = str(gen.get("generator_id", ""))
        archetype = str(gen.get("archetype", ""))
        generator_local_counter.setdefault(gen_id, 0)
        local_i = generator_local_counter[gen_id]
        generator_local_counter[gen_id] = local_i + 1

        params = pick_params_by_index(gen, local_i)
        if gen_id in ("clustered_communities", "conference_event_compact"):
            params = dict(params)
            params["_allow_partitioned"] = True
            params["_topology_flags"] = ["multi_component_allowed"]

        # If generator is produced from some trace-only anchors, pick one deterministically.
        trace_candidates = trace_generator_to_anchors.get(gen_id, [])
        if trace_candidates:
            trace_anchor_local_counter.setdefault(gen_id, 0)
            ta_i = trace_anchor_local_counter[gen_id]
            trace_anchor_local_counter[gen_id] = ta_i + 1
            trace_anchor = trace_candidates[ta_i % len(trace_candidates)]
            anchor_id = str(trace_anchor.get("anchor_id", ""))
            anchor_label = str(trace_anchor.get("label", anchor_id))
            source_type = "trace_reference_synthetic"
        else:
            anchor_id = ""
            anchor_label = ""
            source_type = "synthetic"

        # MapCandidate compatible params: generator params only.
        map_id = f"SYN_{gen_id}_{anchor_id or 'none'}_{idx:04d}"
        map_seed = stable_seed_u32(global_seed, map_id)

        planned = PlannedCandidate(
            map_id=map_id,
            batch_target=batch_target,
            source_type=source_type,
            anchor_id=anchor_id,
            anchor_label=anchor_label,
            archetype=archetype,
            generator_type=gen_id,
            crs="local",
            network_type="synthetic",
            wkt_dir=wkt_dir,
            osm_raw_dir=None,
            preview_dir=preview_dir,
            bbox_or_params_obj=params,
            generator_params=params,
            anchor_variant_type=None,
            anchor_distance_m=None,
            window_size_m=None,
            center_lat=None,
            center_lon=None,
            cand_seed=map_seed,
            generation_key="synthetic",
        )
        candidates.append(planned)

    return candidates


def ensure_candidate_dirs(candidate: PlannedCandidate) -> None:
    ensure_dir(candidate.wkt_dir)
    if candidate.osm_raw_dir is not None:
        ensure_dir(candidate.osm_raw_dir)
    ensure_dir(candidate.preview_dir)


def planned_to_osm_ctx(cand: PlannedCandidate) -> Any:
    from map_space_osm_builder import OsmBuildContext

    params = dict(cand.bbox_or_params_obj or {})
    allow_partitioned = bool(params.pop("_allow_partitioned", False))
    topology_flags = list(params.pop("_topology_flags", []))
    return OsmBuildContext(
        map_id=cand.map_id,
        source_type=cand.source_type,
        anchor_id=cand.anchor_id,
        anchor_label=cand.anchor_label,
        archetype=cand.archetype,
        crs=cand.crs,
        network_type=cand.network_type,
        params=params,
        allow_partitioned=allow_partitioned,
        topology_flags=topology_flags,
        variant_type=str(cand.anchor_variant_type or ""),
        anchor_distance_m=float(cand.anchor_distance_m or 0.0),
        window_size_m=float(cand.window_size_m or 0.0),
        seed=cand.cand_seed,
    )


def planned_to_synthetic_ctx(cand: PlannedCandidate) -> Any:
    from map_space_synthetic_builder import SyntheticBuildContext

    return SyntheticBuildContext(
        map_id=cand.map_id,
        source_type=cand.source_type,
        anchor_id=cand.anchor_id,
        anchor_label=cand.anchor_label,
        archetype=cand.archetype,
        generator_type=cand.generator_type,
        params=dict(cand.generator_params or cand.bbox_or_params_obj or {}),
        seed=cand.cand_seed,
    )


def build_one_candidate(
    *,
    cand: PlannedCandidate,
    output_root: Path,
    global_seed: int,
    force: bool,
    margin_m: float = 50.0,
) -> tuple[str, str]:
    if map_wkt_ok(cand.wkt_dir) and not force:
        return "SKIPPED_EXISTING_OK", "existing roads.wkt+metadata"

    if cand.source_type == "osm":
        from map_space_osm_builder import build_osm_map_from_cache

        ctx = planned_to_osm_ctx(cand)
        return build_osm_map_from_cache(
            ctx=ctx,
            output_root=output_root,
            wkt_dir=cand.wkt_dir,
            preview_dir=cand.preview_dir,
            margin_m=margin_m,
        )

    if cand.source_type in ("synthetic", "trace_reference_synthetic"):
        from map_space_synthetic_builder import build_synthetic_map

        ctx = planned_to_synthetic_ctx(cand)
        return build_synthetic_map(
            ctx=ctx,
            wkt_dir=cand.wkt_dir,
            preview_dir=cand.preview_dir,
            margin_m=margin_m,
            global_seed=global_seed,
        )

    return "FAIL_UNKNOWN", f"unknown source_type={cand.source_type}"


def osm_queue_path(output_root: Path) -> Path:
    return output_root / OSM_QUEUE_PATH_NAME


def load_osm_queue(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(path)
    return {r["map_id"]: r for r in rows if r.get("map_id")}


def write_osm_queue(path: Path, rows: list[dict[str, str]]) -> None:
    from map_space_osm_builder import QUEUE_COLUMNS

    ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=QUEUE_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda x: x.get("map_id", "")):
            w.writerow(r)
    tmp.replace(path)


def init_osm_download_queue(
    *,
    planned: list[PlannedCandidate],
    output_root: Path,
    existing_manifest: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    from map_space_osm_builder import (
        QUEUE_STATUS_DOWNLOADED,
        QUEUE_STATUS_FAILED_PERMANENT,
        QUEUE_STATUS_FAILED_TRANSIENT,
        QUEUE_STATUS_PENDING,
        find_cached_graphml,
    )

    queue_path = osm_queue_path(output_root)
    existing_queue = load_osm_queue(queue_path) if queue_path.is_file() else {}
    rows: list[dict[str, str]] = []

    for cand in planned:
        if cand.source_type != "osm":
            continue
        params = dict(cand.bbox_or_params_obj or {})
        params.pop("_allow_partitioned", None)
        params.pop("_topology_flags", None)
        bbox_json = json.dumps(
            {
                "center_lat": params.get("center_lat"),
                "center_lon": params.get("center_lon"),
                "width_m": params.get("width_m"),
                "height_m": params.get("height_m"),
            },
            sort_keys=True,
        )
        prev = existing_queue.get(cand.map_id, {})
        manifest_row = existing_manifest.get(cand.map_id, {})
        gen_status = normalize_generation_status(manifest_row.get("generation_status", ""))

        cached = find_cached_graphml(output_root, cand.map_id)
        if cached is not None:
            status = QUEUE_STATUS_DOWNLOADED
            cache_hit = "true"
            graphml_rel = str(cached.relative_to(output_root))
            notes = "cache_hit"
        elif prev.get("status"):
            status = prev["status"]
            cache_hit = prev.get("cache_hit", "false")
            graphml_rel = prev.get("raw_graphml_path", "")
            notes = prev.get("notes", "")
        elif gen_status == "FAIL_DOWNLOAD_PERMANENT":
            status = QUEUE_STATUS_FAILED_PERMANENT
            cache_hit = "false"
            graphml_rel = ""
            notes = manifest_row.get("generation_notes", "")
        elif gen_status in ("FAIL_DOWNLOAD_TRANSIENT", "FAIL_DOWNLOAD"):
            status = QUEUE_STATUS_FAILED_TRANSIENT
            cache_hit = "false"
            graphml_rel = ""
            notes = manifest_row.get("generation_notes", "")
        else:
            status = QUEUE_STATUS_PENDING
            cache_hit = "false"
            graphml_rel = ""
            notes = ""

        rows.append(
            {
                "map_id": cand.map_id,
                "anchor_id": cand.anchor_id,
                "bbox": bbox_json,
                "network_type": cand.network_type,
                "status": status,
                "attempts": prev.get("attempts", manifest_row.get("attempts", "0")),
                "last_error": prev.get("last_error", notes if status.startswith("FAILED") else ""),
                "last_attempt_at": prev.get("last_attempt_at", ""),
                "raw_graphml_path": graphml_rel,
                "raw_geojson_path": prev.get("raw_geojson_path", ""),
                "cache_hit": cache_hit,
                "notes": notes,
            }
        )
    return rows


def run_acquire_osm(
    *,
    planned: list[PlannedCandidate],
    output_root: Path,
    existing_manifest: dict[str, dict[str, str]],
    max_downloads: int,
    osm_timeout: int,
    osm_pause: float,
    retry_transient: bool,
    retry_attempts: int,
    retry_backoff_seconds: float,
) -> dict[str, dict[str, str]]:
    from map_space_osm_builder import (
        QUEUE_STATUS_DOWNLOADED,
        QUEUE_STATUS_FAILED_PERMANENT,
        QUEUE_STATUS_FAILED_TRANSIENT,
        QUEUE_STATUS_PENDING,
        TRANSIENT_NETWORK,
        download_osm_graph_for_candidate,
    )

    queue_rows = init_osm_download_queue(
        planned=planned,
        output_root=output_root,
        existing_manifest=existing_manifest,
    )
    by_id = {c.map_id: c for c in planned if c.source_type == "osm"}
    downloads_done = 0

    for row in queue_rows:
        if downloads_done >= max_downloads:
            break
        status = row.get("status", "")
        if status == QUEUE_STATUS_DOWNLOADED:
            continue
        if status == QUEUE_STATUS_FAILED_PERMANENT:
            continue
        if status == QUEUE_STATUS_FAILED_TRANSIENT and not retry_transient:
            continue
        if status not in (QUEUE_STATUS_PENDING, QUEUE_STATUS_FAILED_TRANSIENT):
            continue

        cand = by_id.get(row["map_id"])
        if cand is None:
            continue

        params = dict(cand.bbox_or_params_obj or {})
        params.pop("_allow_partitioned", None)
        params.pop("_topology_flags", None)

        result = None
        for attempt in range(1, max(1, retry_attempts) + 1):
            result = download_osm_graph_for_candidate(
                map_id=cand.map_id,
                params=params,
                network_type=cand.network_type,
                output_root=output_root,
                raw_dir=cand.osm_raw_dir,
                timeout=osm_timeout,
                pause_seconds=osm_pause if downloads_done > 0 or attempt > 1 else 0.0,
                use_cache=True,
            )
            row["attempts"] = str(int(row.get("attempts", "0") or 0) + 1)
            row["last_attempt_at"] = datetime.now(timezone.utc).isoformat()
            if result.success:
                break
            if result.error_kind != TRANSIENT_NETWORK:
                break
            if attempt < retry_attempts:
                sleep_s = retry_backoff_seconds * (2 ** (attempt - 1))
                logger.info("Transient OSM error for %s; backoff %.1fs", cand.map_id, sleep_s)
                if sleep_s > 0:
                    time.sleep(sleep_s)

        assert result is not None
        downloads_done += 1
        if result.success:
            row["status"] = QUEUE_STATUS_DOWNLOADED
            row["cache_hit"] = "true" if result.cache_hit else "false"
            if result.graphml_path is not None and result.graphml_path.is_file():
                try:
                    row["raw_graphml_path"] = str(result.graphml_path.relative_to(output_root))
                except ValueError:
                    row["raw_graphml_path"] = str(result.graphml_path)
            row["last_error"] = ""
            row["notes"] = "cache_hit" if result.cache_hit else "downloaded"
        elif result.error_kind == TRANSIENT_NETWORK:
            row["status"] = QUEUE_STATUS_FAILED_TRANSIENT
            row["last_error"] = result.error_message
            row["notes"] = result.error_kind
        else:
            row["status"] = QUEUE_STATUS_FAILED_PERMANENT
            row["last_error"] = result.error_message
            row["notes"] = result.error_kind or "UNKNOWN"

    write_osm_queue(osm_queue_path(output_root), queue_rows)
    return {r["map_id"]: r for r in queue_rows}


def run_build_phase(
    *,
    planned: list[PlannedCandidate],
    output_root: Path,
    source: str,
    global_seed: int,
    force: bool,
    existing_manifest: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    from map_space_osm_builder import QUEUE_STATUS_DOWNLOADED, find_cached_graphml

    rows_by_id = dict(existing_manifest)
    queue = load_osm_queue(osm_queue_path(output_root)) if osm_queue_path(output_root).is_file() else {}

    for cand in planned:
        is_osm = cand.source_type == "osm"
        is_syn = cand.source_type in ("synthetic", "trace_reference_synthetic")
        if source == "synthetic" and not is_syn:
            continue
        if source == "osm" and not is_osm:
            continue

        ensure_candidate_dirs(cand)
        existing = rows_by_id.get(cand.map_id)
        if existing and not force:
            prev_status = normalize_generation_status(existing.get("generation_status", ""))
            if prev_status in ("OK", "SKIPPED_EXISTING_OK") and map_wkt_ok(cand.wkt_dir):
                continue

        if is_osm:
            qrow = queue.get(cand.map_id, {})
            has_cache = find_cached_graphml(output_root, cand.map_id) is not None
            if not has_cache and qrow.get("status") != QUEUE_STATUS_DOWNLOADED:
                status = "FAIL_DOWNLOAD_TRANSIENT"
                notes = qrow.get("last_error") or "no cached graphml; run --acquire-osm"
                write_error_metadata(cand, cand.wkt_dir, generation_status=status, notes=notes)
                row = build_manifest_row(cand=cand, generation_status=status, generation_notes=notes)
                rows_by_id[cand.map_id] = row
                continue

        status, notes = build_one_candidate(
            cand=cand,
            output_root=output_root,
            global_seed=global_seed,
            force=force,
        )
        if status != "OK" and not (cand.wkt_dir / "metadata.json").is_file():
            write_error_metadata(cand, cand.wkt_dir, generation_status=status, notes=notes)
        row = build_manifest_row(cand=cand, generation_status=status, generation_notes=notes)
        rows_by_id[cand.map_id] = row

    return rows_by_id


def run_plan_phase(
    *,
    planned: list[PlannedCandidate],
    output_root: Path,
    existing_manifest: dict[str, dict[str, str]],
    force: bool,
) -> dict[str, dict[str, str]]:
    rows_by_id = dict(existing_manifest)
    for cand in planned:
        ensure_candidate_dirs(cand)
        if cand.map_id in rows_by_id and not force:
            prev = rows_by_id[cand.map_id]
            if normalize_generation_status(prev.get("generation_status", "")) != "PLANNED":
                continue
        row = build_manifest_row(cand=cand, generation_status="PLANNED", generation_notes="")
        rows_by_id[cand.map_id] = row
    init_rows = init_osm_download_queue(
        planned=planned,
        output_root=output_root,
        existing_manifest=rows_by_id,
    )
    write_osm_queue(osm_queue_path(output_root), init_rows)
    return rows_by_id


def write_generation_reports(manifest_path: Path, output_root: Path) -> None:
    rows = read_csv_dicts(manifest_path)
    reports_dir = SCENARIOS_DIR / "analysis" / "reports"

    # Error analysis
    status_counts: dict[str, int] = {}
    anchor_errors: dict[str, int] = {}
    window_errors: dict[str, int] = {}
    network_errors: dict[str, int] = {}
    for r in rows:
        st = normalize_generation_status(r.get("generation_status", "") or "PLANNED")
        status_counts[st] = status_counts.get(st, 0) + 1
        if st.startswith("FAIL"):
            aid = r.get("anchor_id") or "(none)"
            anchor_errors[aid] = anchor_errors.get(aid, 0) + 1
            try:
                params = json.loads(r.get("bbox_or_params", "{}") or "{}")
                ws = params.get("window_size_m") or params.get("width_m")
                if ws is not None:
                    window_errors[str(ws)] = window_errors.get(str(ws), 0) + 1
            except json.JSONDecodeError:
                pass
            nt = r.get("network_type", "") or "(none)"
            network_errors[nt] = network_errors.get(nt, 0) + 1

    err_lines = [
        "# map_generation_error_analysis_v1.md",
        "",
        "## Totals",
        f"- total_candidates: {len(rows)}",
    ]
    for key in sorted(status_counts.keys()):
        err_lines.append(f"- {key}: {status_counts[key]}")
    err_lines.extend(
        [
            "",
            "## Failures by anchor_id",
        ]
    )
    for k, v in sorted(anchor_errors.items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
        err_lines.append(f"- {k}: {v}")
    err_lines.extend(["", "## Failures by window_size_m"])
    for k, v in sorted(window_errors.items(), key=lambda kv: (-kv[1], kv[0])):
        err_lines.append(f"- {k}: {v}")
    err_lines.extend(["", "## Failures by network_type"])
    for k, v in sorted(network_errors.items(), key=lambda kv: (-kv[1], kv[0])):
        err_lines.append(f"- {k}: {v}")
    err_lines.extend(
        [
            "",
            "## Interpretation",
            "- `FAIL_DOWNLOAD_TRANSIENT`: Overpass/network; retry with `--acquire-osm --retry-transient`.",
            "- `FAIL_DOWNLOAD_PERMANENT`: empty bbox / no OSM network; do not retry.",
            "- `FAIL_BUILD_SYNTHETIC_DEGENERATE`: generator produced insufficient graph; check `synthetic_validation` in metadata.",
            "- `FAIL_BUILD_OSM`: cached graph could not be converted to WKT.",
            "",
        ]
    )
    (reports_dir / "map_generation_error_analysis_v1.md").write_text("\n".join(err_lines) + "\n", encoding="utf-8")

    recovery = [
        "# map_generation_recovery_plan_v1.md",
        "",
        "## Recommended order",
        "1. Plan without network:",
        "```bash",
        "python3 scenarios/setup/generate_map_space_saturation_v1.py --plan-only --target-total 800 --seed 42",
        "```",
        "2. Build synthetics offline:",
        "```bash",
        "python3 scenarios/setup/generate_map_space_saturation_v1.py --build --source synthetic --seed 42",
        "```",
        "3. Validate synthetics:",
        "```bash",
        "python3 scenarios/setup/validate_map_space_saturation_v1.py",
        "```",
        "4. Extract features from valid maps:",
        "```bash",
        "python3 scenarios/setup/extract_map_space_saturation_features.py",
        "```",
        "5. Acquire OSM in small batches:",
        "```bash",
        "python3 scenarios/setup/generate_map_space_saturation_v1.py --acquire-osm --max-downloads 25 --retry-transient --retry-attempts 2 --retry-backoff-seconds 30 --seed 42",
        "```",
        "6. Build OSM from cache:",
        "```bash",
        "python3 scenarios/setup/generate_map_space_saturation_v1.py --build --source osm --seed 42",
        "```",
        "",
        "## Saturation decision",
        "Continue feature-space analysis with maps in `OK` / validation `PASS` even if some OSM downloads remain transient failures.",
        "",
    ]
    (reports_dir / "map_generation_recovery_plan_v1.md").write_text("\n".join(recovery) + "\n", encoding="utf-8")


def write_error_metadata(
    candidate: PlannedCandidate,
    wkt_dir: Path,
    *,
    generation_status: str,
    notes: str,
) -> None:
    ensure_dir(wkt_dir)
    meta_path = wkt_dir / "metadata.json"
    meta = {
        "name": candidate.map_id,
        "map_id": candidate.map_id,
        "source": candidate.source_type,
        "source_type": candidate.source_type,
        "anchor_id": candidate.anchor_id or None,
        "anchor_label": candidate.anchor_label or None,
        "archetype": candidate.archetype,
        "generator_type": candidate.generator_type or None,
        "map_generator_type": candidate.generator_type or candidate.archetype,
        "map_archetype": candidate.archetype,
        "crs": candidate.crs,
        "network_type": "synthetic" if candidate.source_type != "osm" else candidate.network_type,
        "world_size": [0, 0],
        "occupancy_margin_m": 50.0,
        "seed": candidate.cand_seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "failed",
        "generation_status": generation_status,
        "error_notes": notes,
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def read_world_size_from_metadata(meta_path: Path) -> tuple[int, int]:
    try:
        if not meta_path.is_file():
            return 0, 0
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        ws = meta.get("world_size") or [0, 0]
        return int(ws[0]), int(ws[1])
    except Exception:
        return 0, 0


def build_manifest_row(
    *,
    cand: PlannedCandidate,
    generation_status: str,
    generation_notes: str,
) -> dict[str, str]:
    generation_status = normalize_generation_status(generation_status)
    meta_path = cand.wkt_dir / "metadata.json"
    wx, wy = read_world_size_from_metadata(meta_path)

    roads_path = cand.wkt_dir / "roads.wkt"
    preview_path = cand.preview_dir / f"{cand.map_id}.png"

    bbox_or_params = cand.bbox_or_params_obj
    bbox_or_params_str = json.dumps(bbox_or_params, sort_keys=True, separators=(",", ":"))

    # Paths in manifest are relative to output root.
    # (We keep them relative to make the artifact relocatable.)
    try:
        wkt_dir_rel = str(cand.wkt_dir)
        preview_rel = str(preview_path)
        # Convert to relative later when writing.
    except Exception:
        wkt_dir_rel = str(cand.wkt_dir)
        preview_rel = str(preview_path)

    world_x = str(wx)
    world_y = str(wy)

    # `network_type` for synthetic is fixed to "synthetic"
    network_type = cand.network_type if cand.source_type == "osm" else "synthetic"

    # WKT/preview existence handling
    roads_wkt_rel = "" if not roads_path.is_file() else roads_path.name
    if roads_path.is_file():
        roads_wkt_rel = str(roads_path.relative_to(roads_path.parents[1]))  # batch_root/wkt/../

    return {
        "map_id": cand.map_id,
        "batch_target": str(cand.batch_target),
        "source_type": cand.source_type,
        "anchor_id": cand.anchor_id,
        "anchor_label": cand.anchor_label,
        "archetype": cand.archetype,
        "generator_type": cand.generator_type,
        "wkt_dir": "",  # filled when writing manifest
        "roads_wkt": "",  # filled when writing manifest
        "preview_png": "",  # filled when writing manifest
        "metadata_json": "",  # filled when writing manifest
        "world_size_x": world_x,
        "world_size_y": world_y,
        "crs": cand.crs,
        "network_type": network_type,
        "bbox_or_params": bbox_or_params_str,
        "seed": str(cand.cand_seed),
        "generation_status": generation_status,
        "generation_notes": generation_notes,
    }


def relativize_manifest_rows(rows: list[dict[str, str]], output_root: Path) -> None:
    """
    Convert absolute paths (produced in earlier steps) into relative paths.
    """
    # We reconstruct actual paths from row fields by map_id using current FS layout.
    for r in rows:
        mid = r["map_id"]
        batch_target = int(r["batch_target"])
        batch_dir = output_root / f"batch_{batch_target:04d}"
        wkt_dir = batch_dir / "wkt" / f"map_{int(mid.split('_')[-1]):04d}"
        # Note: above assumes map_id tail equals idx; our map_id includes idx as last component.
        # This keeps us robust without storing extra derived paths in the row.
        # However if parsing fails, we fallback to empty paths.
        try:
            idx_tail = int(mid.split("_")[-1])
            wkt_dir = batch_dir / "wkt" / f"map_{idx_tail:04d}"
            meta_path = wkt_dir / "metadata.json"
            roads_path = wkt_dir / "roads.wkt"
            preview_path = output_root / "previews" / f"{mid}.png"
            r["wkt_dir"] = str(wkt_dir.relative_to(output_root))
            r["roads_wkt"] = str(roads_path.relative_to(output_root)) if roads_path.is_file() else ""
            r["preview_png"] = str(preview_path.relative_to(output_root)) if preview_path.is_file() else ""
            r["metadata_json"] = str(meta_path.relative_to(output_root)) if meta_path.is_file() else ""
        except Exception:
            r["wkt_dir"] = ""
            r["roads_wkt"] = ""
            r["preview_png"] = ""
            r["metadata_json"] = ""


def write_batch_report(manifest_path: Path, report_path: Path) -> None:
    rows = read_csv_dicts(manifest_path)
    if not rows:
        report_path.write_text("# map_generation_batches_v1.md\n\n(no data)\n", encoding="utf-8")
        return

    # Index by batch_target
    by_batch: dict[int, list[dict[str, str]]] = {}
    for r in rows:
        try:
            bt = int(r.get("batch_target", "0") or 0)
        except ValueError:
            continue
        if bt not in by_batch:
            by_batch[bt] = []
        by_batch[bt].append(r)

    lines: list[str] = []
    lines.append("# map_generation_batches_v1.md")
    lines.append("")
    lines.append("## Batch summary (from `manifest_maps_all.csv`)")
    lines.append("")

    for bt in BATCH_TARGETS:
        btrs = by_batch.get(bt, [])
        if not btrs:
            continue

        attempted = [
            r
            for r in btrs
            if normalize_generation_status(r.get("generation_status") or "") not in ("PLANNED",)
        ]
        osm_cnt = sum(1 for r in attempted if (r.get("source_type") or "") == "osm")
        syn_cnt = sum(1 for r in attempted if (r.get("source_type") or "") != "osm")
        fail_cnt = sum(1 for r in attempted if (r.get("generation_status") or "").startswith("FAIL"))

        lines.append(f"### batch_0{bt // 100:02d}{'00' if bt in (100,200) else ''}".replace("batch_00", "batch_0"))
        lines.append("")
        lines.append(f"- candidates_present: {len(btrs)}")
        lines.append(f"- attempted_generated_or_failed: {len(attempted)}")
        lines.append(f"- osm_cnt: {osm_cnt}")
        lines.append(f"- synthetic_cnt: {syn_cnt}")
        lines.append(f"- failures: {fail_cnt}")

        # Distribution by archetype
        dist_arch: dict[str, int] = {}
        for r in attempted:
            a = r.get("archetype", "") or ""
            dist_arch[a] = dist_arch.get(a, 0) + 1
        lines.append("")
        lines.append("- distribution_by_archetype:")
        for a, c in sorted(dist_arch.items(), key=lambda kv: (-kv[1], kv[0])):
            if not a:
                a = "(none)"
            lines.append(f"  - {a}: {c}")

        # Distribution by anchor
        dist_anchor: dict[str, int] = {}
        for r in attempted:
            aid = r.get("anchor_id", "") or ""
            dist_anchor[aid or "(none)"] = dist_anchor.get(aid or "(none)", 0) + 1
        lines.append("")
        lines.append("- distribution_by_anchor_id:")
        for aid, c in sorted(dist_anchor.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"  - {aid}: {c}")

        # Error notes
        error_notes = []
        for r in attempted:
            st = r.get("generation_status", "")
            if st.startswith("FAIL"):
                n = r.get("generation_notes", "") or ""
                if n:
                    error_notes.append(n)
        lines.append("")
        lines.append("- top_error_notes (up to 5):")
        for n in error_notes[:5]:
            lines.append(f"  - {n}")
        lines.append("")

    ensure_dir(report_path.parent)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_readme(output_root: Path, *, target_total: int | None, seed: int | None) -> None:
    lines: list[str] = []
    lines.append("# Map space saturation candidates (v1)")
    lines.append("")
    lines.append("This directory contains *roads-only* candidate maps generated from the saturation spec.")
    lines.append("")
    lines.append("## Output layout")
    lines.append("- `batch_XXXX/`: per-stage candidate storage")
    lines.append("- `previews/`: preview PNGs (one per map_id)")
    lines.append("- `manifest_maps_all.csv`: global manifest")
    lines.append("")
    lines.append("## Run parameters")
    lines.append(f"- target_total: {target_total if target_total is not None else '(estimate-only)'}")
    lines.append(f"- seed: {seed if seed is not None else '(estimate-only)'}")
    lines.append("")
    lines.append("## Notes")
    lines.append("- This phase does not generate POIs, routes, or traffic profiles.")
    lines.append("")
    (output_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate map_space_saturation_v1 candidates from saturation spec.")
    parser.add_argument("--design-space", type=Path, default=DEFAULT_DESIGN_SPACE_YAML)
    parser.add_argument("--archetype-csv", type=Path, default=DEFAULT_ARCHETYPE_CSV)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--estimate-only", action="store_true", help="Estimate candidates without generating WKT.")
    parser.add_argument("--plan-only", action="store_true", help="Plan manifest + OSM queue only (no download/build).")
    parser.add_argument("--acquire-osm", action="store_true", help="Download OSM graphs into cache (bounded).")
    parser.add_argument("--build", action="store_true", help="Build roads.wkt/metadata/previews from cache or synthetics.")
    parser.add_argument("--generate", action="store_true", help="Plan + build (no OSM download unless --max-downloads > 0).")
    parser.add_argument("--source", choices=["synthetic", "osm", "all"], default="all")
    parser.add_argument("--target-total", type=int, default=800, help="Total planned candidates (prefix).")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true", help="Overwrite existing OK artifacts.")
    parser.add_argument("--max-downloads", type=int, default=0, help="Max OSM downloads per --acquire-osm/--generate run.")
    parser.add_argument("--osm-timeout", type=int, default=180)
    parser.add_argument("--osm-pause", type=float, default=10.0)
    parser.add_argument("--retry-transient", action="store_true", help="Retry FAILED_TRANSIENT queue rows.")
    parser.add_argument("--retry-attempts", type=int, default=2)
    parser.add_argument("--retry-backoff-seconds", type=float, default=30.0)
    parser.add_argument(
        "--retry-fail-download-only",
        action="store_true",
        help="Deprecated: use --acquire-osm --retry-transient instead.",
    )
    args = parser.parse_args()

    mode_count = sum(
        bool(x)
        for x in (
            args.estimate_only,
            args.plan_only,
            args.acquire_osm,
            args.build,
            args.generate,
        )
    )
    if mode_count == 0:
        parser.error("Specify one of: --estimate-only, --plan-only, --acquire-osm, --build, --generate")
    if args.estimate_only and mode_count > 1:
        parser.error("--estimate-only cannot be combined with other modes")

    if args.target_total <= 0:
        parser.error("--target-total must be > 0")

    design_spec_full = load_yaml(args.design_space)
    if "map_design_space_saturation_v1" not in design_spec_full:
        raise ValueError(f"Expected key map_design_space_saturation_v1 in {args.design_space}")
    if not args.archetype_csv.is_file():
        raise FileNotFoundError(f"Missing archetype CSV: {args.archetype_csv}")

    output_root: Path = args.output
    ensure_dir(output_root)
    ensure_dir(output_root / "previews")
    from map_space_osm_builder import osm_cache_dir

    ensure_dir(osm_cache_dir(output_root))
    for bt in BATCH_TARGETS:
        ensure_dir(output_root / f"batch_{bt:04d}")

    planned = compute_plan(
        design_space=design_spec_full,
        global_seed=int(args.seed),
        target_total=int(args.target_total),
        output_root=output_root,
    )
    manifest_path = output_root / "manifest_maps_all.csv"
    existing_by_id = load_manifest(manifest_path)

    if args.estimate_only:
        osm_cnt = sum(1 for c in planned if c.source_type == "osm")
        syn_cnt = len(planned) - osm_cnt
        logger.info("Estimate-only: target_total=%s seed=%s", args.target_total, args.seed)
        logger.info("Estimated OSM candidates: %s; synthetic candidates: %s", osm_cnt, syn_cnt)
        return

    do_plan = args.plan_only or args.generate
    do_acquire = args.acquire_osm or args.retry_fail_download_only or (args.generate and args.max_downloads > 0)
    do_build = args.build or args.generate

    if args.retry_fail_download_only and not args.acquire_osm:
        args.acquire_osm = True
        args.retry_transient = True
        if args.max_downloads <= 0:
            args.max_downloads = 25

    rows_by_id = dict(existing_by_id)

    if do_plan:
        rows_by_id = run_plan_phase(
            planned=planned,
            output_root=output_root,
            existing_manifest=rows_by_id,
            force=bool(args.force),
        )
        logger.info("Plan phase: %s candidates marked PLANNED", len(planned))

    if do_acquire:
        max_dl = int(args.max_downloads) if args.max_downloads > 0 else 25
        run_acquire_osm(
            planned=planned,
            output_root=output_root,
            existing_manifest=rows_by_id,
            max_downloads=max_dl,
            osm_timeout=int(args.osm_timeout),
            osm_pause=float(args.osm_pause),
            retry_transient=bool(args.retry_transient or args.retry_fail_download_only),
            retry_attempts=int(args.retry_attempts),
            retry_backoff_seconds=float(args.retry_backoff_seconds),
        )
        logger.info("Acquire OSM phase complete (max_downloads=%s)", max_dl)

    if do_build:
        build_source = args.source
        if args.generate and not args.build and not args.plan_only:
            build_source = args.source
        rows_by_id = run_build_phase(
            planned=planned,
            output_root=output_root,
            source=build_source,
            global_seed=int(args.seed),
            force=bool(args.force),
            existing_manifest=rows_by_id,
        )
        logger.info("Build phase complete (source=%s)", build_source)

    rows = list(rows_by_id.values())
    for r in rows:
        r["generation_status"] = normalize_generation_status(r.get("generation_status", ""))
    rows.sort(key=lambda r: str(r.get("map_id", "")))
    relativize_manifest_rows(rows, output_root=output_root)
    write_manifest(manifest_path, rows)

    write_generation_reports(manifest_path, output_root)
    report_path = SCENARIOS_DIR / "analysis" / "reports" / "map_generation_batches_v1.md"
    write_batch_report(manifest_path, report_path)
    build_readme(output_root, target_total=args.target_total, seed=args.seed)

    ok = sum(1 for r in rows if normalize_generation_status(r.get("generation_status", "")) in ("OK", "SKIPPED_EXISTING_OK"))
    logger.info("Manifest updated: %s rows, %s OK/skipped", len(rows), ok)


if __name__ == "__main__":
    main()

