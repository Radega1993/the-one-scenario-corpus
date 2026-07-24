"""Synthetic map generation with validation and regeneration for map_space_saturation_v1."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from map_geometry import parse_linestrings, world_size_from_sim_roads, wkt_to_sim_coords
from map_space_preview import render_preview
from map_space_synthetic import GENERATORS, write_roads_wkt

MIN_NODES = 20
MIN_EDGES = 20
MIN_TOTAL_LENGTH_M = 200.0
MIN_WORLD_AXIS = 50
MAX_REGENERATION_ATTEMPTS = 5


@dataclass
class SyntheticBuildContext:
    map_id: str
    source_type: str
    anchor_id: str
    anchor_label: str
    archetype: str
    generator_type: str
    params: dict[str, Any]
    seed: int


def stable_seed(seed: int, *parts: str) -> int:
    raw = "::".join([str(seed), *map(str, parts)]).encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:8], 16)


def _total_length_m(edges: list[tuple[tuple[float, float], tuple[float, float]]]) -> float:
    total = 0.0
    for a, b in edges:
        total += ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    return total


def _has_degenerate_segments(edges: list[tuple[tuple[float, float], tuple[float, float]]]) -> bool:
    for a, b in edges:
        if ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 < 1e-6:
            return True
    return False


def validate_synthetic_graph(
    edges: list[tuple[tuple[float, float], tuple[float, float]]],
    *,
    world_size: tuple[int, int] | None = None,
    n_nodes_hint: int | None = None,
) -> tuple[bool, str]:
    if len(edges) < MIN_EDGES:
        return False, f"too_few_edges ({len(edges)} < {MIN_EDGES})"
    nodes = set()
    for a, b in edges:
        nodes.add(a)
        nodes.add(b)
    n_nodes = len(nodes) if n_nodes_hint is None else max(len(nodes), n_nodes_hint)
    if n_nodes < MIN_NODES:
        return False, f"too_few_nodes ({n_nodes} < {MIN_NODES})"
    total_len = _total_length_m(edges)
    if total_len < MIN_TOTAL_LENGTH_M:
        return False, f"too_short ({total_len:.1f}m < {MIN_TOTAL_LENGTH_M}m)"
    if _has_degenerate_segments(edges):
        return False, "degenerate_segments"
    if world_size is not None:
        wx, wy = world_size
        if wx < MIN_WORLD_AXIS or wy < MIN_WORLD_AXIS:
            return False, f"world_too_small ({wx}x{wy})"
    return True, ""


def write_synthetic_metadata(
    path: Path,
    ctx: SyntheticBuildContext,
    *,
    world_size: tuple[int, int],
    margin_m: float,
    info: dict[str, Any],
    n_edges: int,
    synthetic_validation: dict[str, Any],
) -> None:
    meta = {
        "name": ctx.map_id,
        "map_id": ctx.map_id,
        "source": ctx.source_type,
        "source_type": ctx.source_type,
        "anchor_id": ctx.anchor_id or None,
        "anchor_label": ctx.anchor_label or None,
        "archetype": ctx.archetype,
        "generator_type": ctx.generator_type,
        "map_generator_type": ctx.generator_type,
        "map_archetype": ctx.archetype,
        "crs": "local",
        "network_type": "synthetic",
        "world_size": list(world_size),
        "occupancy_margin_m": margin_m,
        "world_size_policy": f"sim_road_max_plus_{int(margin_m)}m_margin_per_axis",
        "n_road_segments": n_edges,
        "n_edges": n_edges,
        "n_nodes": info.get("n_nodes", 0),
        "generator_params": ctx.params,
        "topology_flags": info.get("topology_flags"),
        "n_components": info.get("n_components", 1),
        "seed": ctx.seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "generated",
        "synthetic_validation": synthetic_validation,
    }
    path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def build_synthetic_map(
    *,
    ctx: SyntheticBuildContext,
    wkt_dir: Path,
    preview_dir: Path,
    margin_m: float = 50.0,
    global_seed: int = 42,
) -> tuple[str, str]:
    gen_fn = GENERATORS.get(ctx.generator_type)
    if gen_fn is None:
        return "FAIL_BUILD_SYNTHETIC_DEGENERATE", f"unknown generator {ctx.generator_type}"

    param_key = json.dumps(ctx.params, sort_keys=True)
    last_reason = ""
    synthetic_validation: dict[str, Any] = {}

    for attempt in range(1, MAX_REGENERATION_ATTEMPTS + 1):
        attempt_seed = stable_seed(global_seed, ctx.map_id, param_key, f"attempt_{attempt}")
        rng = random.Random(attempt_seed)
        edges, info = gen_fn(ctx.params, rng)
        ok, reason = validate_synthetic_graph(edges, n_nodes_hint=int(info.get("n_nodes", 0) or 0))
        if not ok:
            last_reason = reason
            synthetic_validation = {
                "n_nodes": int(info.get("n_nodes", 0) or 0),
                "n_edges": len(edges),
                "total_length_m": round(_total_length_m(edges), 2),
                "regeneration_attempts": attempt,
                "last_failure": reason,
            }
            continue

        try:
            wkt_dir.mkdir(parents=True, exist_ok=True)
            roads_path = wkt_dir / "roads.wkt"
            write_roads_wkt(edges, roads_path)
            world_size = world_size_from_sim_roads(roads_path, margin_m)
            ok2, reason2 = validate_synthetic_graph(edges, world_size=world_size, n_nodes_hint=int(info.get("n_nodes", 0) or 0))
            if not ok2:
                last_reason = reason2
                synthetic_validation = {
                    "n_nodes": int(info.get("n_nodes", 0) or 0),
                    "n_edges": len(edges),
                    "total_length_m": round(_total_length_m(edges), 2),
                    "regeneration_attempts": attempt,
                    "last_failure": reason2,
                }
                continue

            info.setdefault("n_edges", len(edges))
            synthetic_validation = {
                "n_nodes": int(info.get("n_nodes", 0) or 0),
                "n_edges": len(edges),
                "total_length_m": round(_total_length_m(edges), 2),
                "regeneration_attempts": attempt,
            }
            write_synthetic_metadata(
                wkt_dir / "metadata.json",
                ctx,
                world_size=world_size,
                margin_m=margin_m,
                info=info,
                n_edges=len(edges),
                synthetic_validation=synthetic_validation,
            )
            render_preview(roads_path, preview_dir / f"{ctx.map_id}.png", world_size)
            return "OK", ""
        except Exception as exc:
            msg = str(exc)
            if "preview" in msg.lower():
                return "FAIL_PREVIEW", msg
            if "metadata" in msg.lower():
                return "FAIL_METADATA", msg
            return "FAIL_UNKNOWN", msg

    wkt_dir.mkdir(parents=True, exist_ok=True)
    fail_meta = {
        "name": ctx.map_id,
        "map_id": ctx.map_id,
        "source_type": ctx.source_type,
        "status": "failed",
        "generation_status": "FAIL_BUILD_SYNTHETIC_DEGENERATE",
        "error_notes": last_reason,
        "synthetic_validation": synthetic_validation,
    }
    (wkt_dir / "metadata.json").write_text(json.dumps(fail_meta, indent=2) + "\n", encoding="utf-8")
    return "FAIL_BUILD_SYNTHETIC_DEGENERATE", last_reason or "degenerate after retries"
