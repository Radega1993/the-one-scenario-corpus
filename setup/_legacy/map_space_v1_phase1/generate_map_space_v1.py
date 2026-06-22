#!/usr/bin/env python3
"""
generate_map_space_v1.py

Generate map candidates (anchor-based OSM + synthetic) for map_space_v1.

Usage:
    python3 scenarios/setup/generate_map_space_v1.py --estimate-only
    python3 scenarios/setup/generate_map_space_v1.py --dry-run
    python3 scenarios/setup/generate_map_space_v1.py --generate --max-maps 100 --seed 42
    python3 scenarios/setup/generate_map_space_v1.py --generate --max-maps 600 --seed 42 --force
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import math
import random
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import yaml

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import world_size_from_sim_roads, wkt_to_sim_coords, parse_linestrings  # noqa: E402
from map_space_synthetic import GENERATORS, sample_discrete_params, write_roads_wkt  # noqa: E402

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = _SETUP.parent.parent
SCENARIOS_DIR = REPO_ROOT / "scenarios"
DEFAULT_YAML = SCENARIOS_DIR / "analysis" / "config" / "map_design_space_v1.yaml"
DEFAULT_ANCHORS = SCENARIOS_DIR / "analysis" / "config" / "real_map_anchors_v1.yaml"
OUTPUT_ROOT = SCENARIOS_DIR / "map_space_v1"
DEFAULT_MAX_MAPS = 100
FORCE_THRESHOLD = 1000

MANIFEST_COLUMNS = [
    "map_id",
    "map_name",
    "source_type",
    "anchor_id",
    "anchor_label",
    "dataset_basis",
    "archetype",
    "generator_type",
    "wkt_dir",
    "roads_wkt",
    "world_size_x",
    "world_size_y",
    "crs",
    "network_type",
    "bbox_or_generator_params",
    "seed",
    "n_nodes",
    "n_edges",
    "status",
    "notes",
]


def stable_seed(seed: int, *parts: str) -> int:
    raw = "::".join([str(seed), *map(str, parts)]).encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:8], 16)


@dataclass
class MapCandidate:
    map_id: str
    map_name: str
    source_type: str  # osm | synthetic | trace_reference_synthetic
    archetype: str
    generator_type: str
    anchor_id: str = ""
    anchor_label: str = ""
    dataset_basis: str = ""
    variant_type: str = ""
    anchor_distance_m: float = 0.0
    window_size_m: float = 0.0
    params: dict[str, Any] = field(default_factory=dict)
    topology_flags: list[str] = field(default_factory=list)
    crs: str = "EPSG:3067"
    osm_network_type: str = "drive"
    allow_partitioned: bool = False


def load_design_space(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["map_design_space_v1"]


def load_anchors(spec: dict[str, Any], anchors_path: Path | None = None) -> list[dict[str, Any]]:
    ref = spec.get("anchors_ref", "scenarios/analysis/config/real_map_anchors_v1.yaml")
    path = anchors_path or (REPO_ROOT / ref if not Path(ref).is_absolute() else Path(ref))
    if not path.is_file():
        path = SCENARIOS_DIR / "analysis" / "config" / "real_map_anchors_v1.yaml"
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("real_map_anchors_v1", {}).get("anchors", [])


def _pick_rng(seed: int, *parts: str) -> random.Random:
    return random.Random(stable_seed(seed, *parts))


def _anchor_center(anchor: dict[str, Any]) -> tuple[float, float]:
    bbox = anchor.get("bbox") or {}
    if not bbox:
        return 0.0, 0.0
    lat = (float(bbox["south"]) + float(bbox["north"])) / 2
    lon = (float(bbox["west"]) + float(bbox["east"])) / 2
    return lat, lon


def _window_sizes_for_anchor(anchor: dict[str, Any], sampling: dict[str, Any]) -> list[float]:
    default = [float(x) for x in sampling.get("window_sizes_m", [1000, 1500, 2500])]
    by_use = sampling.get("window_size_by_expected_use", {})
    uses = anchor.get("expected_use", [])
    sizes: set[float] = set()
    for use in uses:
        for key, vals in by_use.items():
            if key in str(use):
                sizes.update(float(v) for v in vals)
    if not sizes:
        bbox = anchor.get("bbox") or {}
        if bbox:
            lat = (float(bbox["south"]) + float(bbox["north"])) / 2
            m_per_deg_lat = 111_320.0
            m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat))
            h_m = (float(bbox["north"]) - float(bbox["south"])) * m_per_deg_lat
            w_m = (float(bbox["east"]) - float(bbox["west"])) * m_per_deg_lon
            sizes.add(max(h_m, w_m))
    return sorted(sizes) if sizes else default


def _offset_latlon(
    lat: float, lon: float, distance_m: float, direction: str
) -> tuple[float, float]:
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat))
    dlat = distance_m / m_per_deg_lat
    dlon = distance_m / m_per_deg_lon
    if direction == "offset_n":
        return lat + dlat, lon
    if direction == "offset_s":
        return lat - dlat, lon
    if direction == "offset_e":
        return lat, lon + dlon
    if direction == "offset_w":
        return lat, lon - dlon
    return lat, lon


def iter_osm_candidates(
    spec: dict[str, Any], seed: int, anchors: list[dict[str, Any]]
) -> Iterator[MapCandidate]:
    sampling = spec.get("osm_sampling", {})
    total = int(sampling.get("total_osm_candidates", 300))
    anchor_types = set(sampling.get("anchor_types", ["osm_bbox", "osm_region_or_reference"]))
    osm_anchors = [a for a in anchors if a.get("anchor_type") in anchor_types and a.get("bbox")]
    if not osm_anchors:
        return

    per_anchor = max(1, total // len(osm_anchors))
    idx = 0
    variant_dirs = ["exact", "offset_n", "offset_e", "offset_s", "offset_w"]
    offsets = [float(x) for x in sampling.get("offset_distances_m", [0, 200, 500, 1000])]
    max_offset = float(sampling.get("max_offset_from_anchor_m", 2000))

    for anchor in osm_anchors:
        anchor_id = anchor["anchor_id"]
        sizes = _window_sizes_for_anchor(anchor, sampling)
        flags = list(anchor.get("topology_flags", []))
        for i in range(per_anchor):
            rng = _pick_rng(seed, "osm", anchor_id, str(i))
            window_m = float(rng.choice(sizes))
            variant = variant_dirs[i % len(variant_dirs)]
            offset_m = 0.0 if variant == "exact" else float(rng.choice([o for o in offsets if o > 0] or [500]))
            offset_m = min(offset_m, max_offset)
            center_lat, center_lon = _anchor_center(anchor)
            if variant != "exact":
                center_lat, center_lon = _offset_latlon(center_lat, center_lon, offset_m, variant)
            map_id = f"OSM_{anchor_id}_{idx:04d}"
            yield MapCandidate(
                map_id=map_id,
                map_name=map_id,
                source_type="osm",
                archetype=anchor.get("archetype", "dense_urban_irregular"),
                generator_type="",
                anchor_id=anchor_id,
                anchor_label=anchor.get("label", anchor_id),
                dataset_basis=anchor.get("dataset_basis", ""),
                variant_type=variant,
                anchor_distance_m=offset_m,
                window_size_m=window_m,
                params={
                    "center_lat": round(center_lat, 6),
                    "center_lon": round(center_lon, 6),
                    "width_m": window_m,
                    "height_m": window_m,
                    "variant_type": variant,
                    "anchor_distance_m": offset_m,
                    "window_size_m": window_m,
                    "osm_network_type": anchor.get("network_type", "drive"),
                },
                topology_flags=flags,
                crs=anchor.get("crs", "EPSG:3067"),
                osm_network_type=anchor.get("network_type", "drive"),
                allow_partitioned="partitioned" in flags,
            )
            idx += 1


def iter_trace_synthetic_candidates(
    spec: dict[str, Any], seed: int, anchors: list[dict[str, Any]]
) -> Iterator[MapCandidate]:
    trace_cfg = spec.get("trace_synthetic", {})
    total = int(trace_cfg.get("total_candidates", 40))
    trace_types = set(trace_cfg.get("trace_anchor_types", ["trace_reference_not_map"]))
    trace_anchors = [a for a in anchors if a.get("anchor_type") in trace_types]
    if not trace_anchors:
        return

    archetype_to_gen = {
        "conference_event_compact": "conference_event_compact",
        "corridor": "corridor",
        "clustered_communities": "clustered_communities",
    }
    per_anchor = max(1, total // len(trace_anchors))
    gen_specs = {g["id"]: g for g in spec.get("synthetic_generators", [])}
    idx = 0

    for anchor in trace_anchors:
        arch = anchor.get("archetype", "conference_event_compact")
        gen_id = archetype_to_gen.get(arch, "conference_event_compact")
        gen_spec = gen_specs.get(gen_id, {})
        for i in range(per_anchor):
            rng = _pick_rng(seed, "trace", anchor["anchor_id"], str(i))
            params = sample_discrete_params(gen_spec, rng) if gen_spec else {}
            map_id = f"SYN_{gen_id}_{anchor['anchor_id']}_{idx:04d}"
            yield MapCandidate(
                map_id=map_id,
                map_name=map_id,
                source_type="trace_reference_synthetic",
                archetype=arch,
                generator_type=gen_id,
                anchor_id=anchor["anchor_id"],
                anchor_label=anchor.get("label", anchor["anchor_id"]),
                dataset_basis=anchor.get("dataset_basis", ""),
                variant_type="trace_param",
                params=params,
                topology_flags=list(gen_spec.get("topology_flags", [])),
                crs="local",
                allow_partitioned=False,
            )
            idx += 1


def iter_synthetic_candidates(spec: dict[str, Any], seed: int) -> Iterator[MapCandidate]:
    idx = 0
    for gen in spec.get("synthetic_generators", []):
        gen_id = gen["id"]
        n = int(gen.get("target_candidates", 0))
        flags = gen.get("topology_flags", [])
        trace_anchors = gen.get("trace_anchors", [])
        for i in range(n):
            rng = _pick_rng(seed, "syn", gen_id, str(i))
            params = sample_discrete_params(gen, rng)
            map_id = f"SYN_{gen_id}_{idx:04d}"
            anchor_id = trace_anchors[i % len(trace_anchors)] if trace_anchors else ""
            source_type = (
                "trace_reference_synthetic"
                if gen.get("source_type") == "trace_reference_synthetic" or trace_anchors
                else "synthetic"
            )
            yield MapCandidate(
                map_id=map_id,
                map_name=map_id,
                source_type=source_type,
                archetype=gen_id,
                generator_type=gen_id,
                anchor_id=anchor_id,
                params=params,
                topology_flags=list(flags),
                crs="local",
                allow_partitioned=bool(flags),
            )
            idx += 1


def iter_all_candidates(
    spec: dict[str, Any], seed: int, anchors: list[dict[str, Any]]
) -> Iterator[MapCandidate]:
    yield from iter_synthetic_candidates(spec, seed)
    yield from iter_osm_candidates(spec, seed, anchors)


def estimate(spec: dict[str, Any], anchors: list[dict[str, Any]]) -> dict[str, Any]:
    osm_n = int(spec.get("osm_sampling", {}).get("total_osm_candidates", 300))
    syn_n = sum(int(g.get("target_candidates", 0)) for g in spec.get("synthetic_generators", []))
    osm_anchors = [a for a in anchors if a.get("anchor_type") in ("osm_bbox", "osm_region_or_reference")]
    trace_anchors = [a for a in anchors if a.get("anchor_type") == "trace_reference_not_map"]
    return {
        "osm_anchors": len(osm_anchors),
        "trace_anchors": len(trace_anchors),
        "synthetic_generators": len(spec.get("synthetic_generators", [])),
        "osm_candidates": osm_n,
        "synthetic_candidates": syn_n,
        "total_candidates": osm_n + syn_n,
        "targets": spec.get("targets", {}),
    }


def _meters_to_degrees(lat: float, width_m: float, height_m: float) -> tuple[float, float, float, float]:
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat))
    half_w = (width_m / 2) / m_per_deg_lon
    half_h = (height_m / 2) / m_per_deg_lat
    return half_w, half_h, m_per_deg_lat, m_per_deg_lon


def _bbox_from_candidate(cand: MapCandidate) -> tuple[float, float, float, float]:
    lat = cand.params["center_lat"]
    lon = cand.params["center_lon"]
    w = cand.params["width_m"]
    h = cand.params["height_m"]
    half_w, half_h, _, _ = _meters_to_degrees(lat, w, h)
    north = lat + half_h
    south = lat - half_h
    west = lon - half_w
    east = lon + half_w
    return north, south, east, west


def graph_from_bbox_compat(
    north: float, south: float, east: float, west: float, network_type: str
) -> Any:
    import osmnx as ox

    if south >= north:
        raise ValueError(f"Invalid bbox: south ({south}) >= north ({north})")
    if west >= east:
        raise ValueError(f"Invalid bbox: west ({west}) >= east ({east})")

    version = getattr(ox, "__version__", "1.0.0")
    major = int(version.split(".")[0])
    if major >= 2:
        return ox.graph_from_bbox(
            bbox=(west, south, east, north),
            network_type=network_type,
            simplify=True,
        )
    return ox.graph_from_bbox(
        north, south, east, west,
        network_type=network_type,
        simplify=True,
    )


def _download_osm_graph(
    cand: MapCandidate,
    cache_path: Path,
    *,
    use_cache: bool = True,
) -> Any:
    if use_cache and cache_path.is_file():
        import osmnx as ox

        logger.info("  Using cached GraphML: %s", cache_path.name)
        return ox.load_graphml(str(cache_path))

    north, south, east, west = _bbox_from_candidate(cand)
    logger.info(
        "  Downloading OSM bbox N=%.4f S=%.4f W=%.4f E=%.4f type=%s anchor=%s",
        north, south, west, east, cand.osm_network_type, cand.anchor_id,
    )
    G = graph_from_bbox_compat(north, south, east, west, cand.osm_network_type)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    import osmnx as ox
    ox.save_graphml(G, str(cache_path))
    return G


def _graph_to_edges(
    G: Any,
    crs: str,
    *,
    keep_largest_only: bool = True,
) -> tuple[list[list[tuple[float, float]]], dict[str, Any]]:
    import networkx as nx
    import osmnx as ox

    G_proj = ox.project_graph(G, to_crs=crs)
    n_components = 1
    if not nx.is_weakly_connected(G_proj):
        components = sorted(nx.weakly_connected_components(G_proj), key=len, reverse=True)
        n_components = len(components)
        if keep_largest_only:
            G_proj = G_proj.subgraph(components[0]).copy()
        else:
            all_edges: list[list[tuple[float, float]]] = []
            min_x = min_y = float("inf")
            max_x = max_y = float("-inf")
            n_nodes = 0
            for comp in components:
                sub = G_proj.subgraph(comp).copy()
                _, edges_gdf = ox.graph_to_gdfs(sub)
                for _, row in edges_gdf.iterrows():
                    geom = row.geometry
                    coords = [(c[0], c[1]) for c in geom.coords]
                    if len(coords) >= 2:
                        all_edges.append(coords)
                        for x, y in coords:
                            min_x, max_x = min(min_x, x), max(max_x, x)
                            min_y, max_y = min(min_y, y), max(max_y, y)
                n_nodes += sub.number_of_nodes()
            return all_edges, {
                "min_x": min_x if min_x != float("inf") else 0,
                "max_x": max_x if max_x != float("-inf") else 0,
                "min_y": min_y if min_y != float("inf") else 0,
                "max_y": max_y if max_y != float("-inf") else 0,
                "n_components": n_components,
                "n_nodes": n_nodes,
                "n_edges": len(all_edges),
            }

    nodes_gdf, edges_gdf = ox.graph_to_gdfs(G_proj)
    all_edges: list[list[tuple[float, float]]] = []
    for _, row in edges_gdf.iterrows():
        geom = row.geometry
        coords = [(c[0], c[1]) for c in geom.coords]
        if len(coords) >= 2:
            all_edges.append(coords)

    xs = [row.geometry.x for _, row in nodes_gdf.iterrows()]
    ys = [row.geometry.y for _, row in nodes_gdf.iterrows()]
    return all_edges, {
        "min_x": min(xs) if xs else 0,
        "max_x": max(xs) if xs else 0,
        "min_y": min(ys) if ys else 0,
        "max_y": max(ys) if ys else 0,
        "n_components": n_components,
        "n_nodes": len(xs),
        "n_edges": len(all_edges),
    }


def render_preview(roads_path: Path, preview_path: Path, world_size: tuple[int, int]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    raw = parse_linestrings(roads_path)
    sim = wkt_to_sim_coords(raw)
    wx, wy = world_size

    fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")
    for line in sim:
        xs, ys = zip(*line)
        ax.plot(xs, ys, color="#2c5282", linewidth=0.5, alpha=0.9)
    if wx > 0 and wy > 0:
        ax.add_patch(Rectangle((0, 0), wx, wy, fill=False, edgecolor="#a0aec0", linestyle="--", linewidth=1))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(preview_path, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def write_metadata(
    path: Path,
    cand: MapCandidate,
    *,
    world_size: tuple[int, int],
    margin_m: float,
    info: dict[str, Any],
    n_edges: int,
    seed: int,
) -> None:
    north, south, east, west = (None, None, None, None)
    if cand.source_type == "osm" and "center_lat" in cand.params:
        north, south, east, west = _bbox_from_candidate(cand)
    meta = {
        "name": cand.map_id,
        "map_id": cand.map_id,
        "source": cand.source_type,
        "source_type": cand.source_type,
        "anchor_id": cand.anchor_id or None,
        "anchor_label": cand.anchor_label or None,
        "dataset_basis": cand.dataset_basis or None,
        "archetype": cand.archetype,
        "generator_type": cand.generator_type or None,
        "map_generator_type": cand.generator_type or cand.archetype,
        "map_archetype": cand.archetype,
        "crs": cand.crs,
        "network_type": cand.osm_network_type if cand.source_type == "osm" else "synthetic",
        "world_size": list(world_size),
        "occupancy_margin_m": margin_m,
        "world_size_policy": f"sim_road_max_plus_{int(margin_m)}m_margin_per_axis",
        "n_road_segments": n_edges,
        "n_edges": n_edges,
        "n_nodes": info.get("n_nodes", 0),
        "bbox_latlon": [south, west, north, east] if south is not None else None,
        "bbox_m": [
            info.get("min_x", 0),
            info.get("min_y", 0),
            info.get("max_x", 0),
            info.get("max_y", 0),
        ],
        "variant_type": cand.variant_type or None,
        "anchor_distance_m": cand.anchor_distance_m,
        "window_size_m": cand.window_size_m or None,
        "generator_params": cand.params,
        "topology_flags": cand.topology_flags or None,
        "n_components": info.get("n_components", 1),
        "seed": seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "generated",
    }
    path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def generate_synthetic_map(
    cand: MapCandidate,
    wkt_dir: Path,
    preview_dir: Path,
    margin_m: float,
    seed: int,
) -> tuple[str, str]:
    gen_fn = GENERATORS.get(cand.generator_type)
    if gen_fn is None:
        return "failed", f"unknown generator {cand.generator_type}"

    param_key = json.dumps(cand.params, sort_keys=True)
    rng = random.Random(stable_seed(seed, cand.map_id, param_key))
    edges, info = gen_fn(cand.params, rng)
    if len(edges) < 10:
        return "failed", "too few edges"

    wkt_dir.mkdir(parents=True, exist_ok=True)
    roads_path = wkt_dir / "roads.wkt"
    write_roads_wkt(edges, roads_path)
    world_size = world_size_from_sim_roads(roads_path, margin_m)
    info.setdefault("n_edges", len(edges))
    info.setdefault("n_nodes", info.get("n_nodes", 0))

    write_metadata(
        wkt_dir / "metadata.json",
        cand,
        world_size=world_size,
        margin_m=margin_m,
        info=info,
        n_edges=len(edges),
        seed=seed,
    )
    render_preview(roads_path, preview_dir / f"{cand.map_id}.png", world_size)
    return "ok", ""


def generate_osm_map(
    cand: MapCandidate,
    raw_dir: Path,
    wkt_dir: Path,
    preview_dir: Path,
    margin_m: float,
    seed: int,
    *,
    use_cache: bool = True,
) -> tuple[str, str]:
    cache_path = raw_dir / f"{cand.map_id}.graphml"
    try:
        G = _download_osm_graph(cand, cache_path, use_cache=use_cache)
    except Exception as exc:
        return "failed", f"osm_download: {exc}"

    try:
        keep_largest = not cand.allow_partitioned
        edges, info = _graph_to_edges(G, cand.crs, keep_largest_only=keep_largest)
    except Exception as exc:
        return "failed", f"osm_process: {exc}"

    min_segments = 50
    if len(edges) < min_segments:
        return "failed", f"too few segments ({len(edges)} < {min_segments})"

    wkt_dir.mkdir(parents=True, exist_ok=True)
    roads_path = wkt_dir / "roads.wkt"
    write_roads_wkt(edges, roads_path)
    world_size = world_size_from_sim_roads(roads_path, margin_m)
    write_metadata(
        wkt_dir / "metadata.json",
        cand,
        world_size=world_size,
        margin_m=margin_m,
        info=info,
        n_edges=len(edges),
        seed=seed,
    )
    render_preview(roads_path, preview_dir / f"{cand.map_id}.png", world_size)
    return "ok", ""


def candidate_to_row(
    cand: MapCandidate,
    *,
    output_root: Path,
    wkt_dir: Path,
    status: str,
    notes: str,
    seed: int,
    world_size: tuple[int, int] | None = None,
) -> dict[str, str]:
    params_json = json.dumps(cand.params, sort_keys=True)
    roads = wkt_dir / "roads.wkt"
    wx, wy = world_size or (0, 0)
    n_nodes, n_edges = 0, 0
    if (wkt_dir / "metadata.json").is_file():
        meta = json.loads((wkt_dir / "metadata.json").read_text(encoding="utf-8"))
        ws = meta.get("world_size", [0, 0])
        wx, wy = int(ws[0]), int(ws[1])
        n_nodes = int(meta.get("n_nodes", 0))
        n_edges = int(meta.get("n_edges", meta.get("n_road_segments", 0)))
    network_type = cand.osm_network_type if cand.source_type == "osm" else "synthetic"
    return {
        "map_id": cand.map_id,
        "map_name": cand.map_name,
        "source_type": cand.source_type,
        "anchor_id": cand.anchor_id,
        "anchor_label": cand.anchor_label,
        "dataset_basis": cand.dataset_basis,
        "archetype": cand.archetype,
        "generator_type": cand.generator_type,
        "wkt_dir": str(wkt_dir.relative_to(output_root)),
        "roads_wkt": str(roads.relative_to(output_root)) if roads.is_file() else "",
        "world_size_x": str(wx),
        "world_size_y": str(wy),
        "crs": cand.crs,
        "network_type": network_type,
        "bbox_or_generator_params": params_json,
        "seed": str(seed),
        "n_nodes": str(n_nodes),
        "n_edges": str(n_edges),
        "status": status,
        "notes": notes,
    }


def write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def map_wkt_ok(wkt_dir: Path) -> bool:
    return (wkt_dir / "roads.wkt").is_file() and (wkt_dir / "metadata.json").is_file()


def run_generate(
    spec: dict[str, Any],
    anchors: list[dict[str, Any]],
    *,
    output_root: Path,
    max_maps: int,
    seed: int,
    force: bool,
    yaml_path: Path,
    skip_ok: bool = False,
) -> list[dict[str, str]]:
    targets = spec.get("targets", {})
    force_limit = int(targets.get("require_force_above", targets.get("max_maps_without_force", 1000)))
    if max_maps > force_limit and not force:
        raise SystemExit(
            f"Requested {max_maps} maps exceeds require_force_above={force_limit}. Use --force."
        )

    margin_m = float(spec["validation"]["thresholds"]["world_size_margin_m"])
    syn_wkt = output_root / "synthetic" / "wkt"
    syn_preview = output_root / "synthetic" / "previews"
    osm_raw = output_root / "real_osm" / "raw"
    osm_wkt = output_root / "real_osm" / "wkt"
    osm_preview = output_root / "real_osm" / "previews"

    rows: list[dict[str, str]] = []
    attempted = 0
    for cand in iter_all_candidates(spec, seed, anchors):
        if attempted >= max_maps:
            break
        attempted += 1

        is_osm = cand.source_type == "osm"
        if is_osm:
            wkt_dir = osm_wkt / cand.map_id
            preview_dir = osm_preview
            if skip_ok and map_wkt_ok(wkt_dir):
                status, notes = "ok", "skipped_existing"
            else:
                status, notes = generate_osm_map(
                    cand, osm_raw, wkt_dir, preview_dir, margin_m, seed, use_cache=True
                )
        else:
            wkt_dir = syn_wkt / cand.map_id
            preview_dir = syn_preview
            if skip_ok and map_wkt_ok(wkt_dir):
                status, notes = "ok", "skipped_existing"
            else:
                status, notes = generate_synthetic_map(cand, wkt_dir, preview_dir, margin_m, seed)

        row = candidate_to_row(
            cand, output_root=output_root, wkt_dir=wkt_dir, status=status, notes=notes, seed=seed
        )
        rows.append(row)
        if status == "ok":
            logger.info("Generated %s [%s] anchor=%s", cand.map_id, cand.source_type, cand.anchor_id)
        else:
            logger.warning("Skipped %s: %s", cand.map_id, notes)

    gen_cfg = output_root / "generation_config_used.yaml"
    shutil.copy2(yaml_path, gen_cfg)
    with gen_cfg.open("a", encoding="utf-8") as f:
        f.write(f"\n# generation_run:\n#   seed: {seed}\n#   max_maps: {max_maps}\n")
        f.write(f"#   timestamp: {datetime.now(timezone.utc).isoformat()}\n")

    write_manifest(rows, output_root / "manifest_maps.csv")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate map_space_v1 candidates")
    parser.add_argument("--design-space", type=Path, default=DEFAULT_YAML)
    parser.add_argument("--anchors", type=Path, default=DEFAULT_ANCHORS)
    parser.add_argument("--output", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--estimate-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--max-maps", type=int, default=DEFAULT_MAX_MAPS)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true", help="Allow >1000 maps or overwrite")
    parser.add_argument("--skip-ok", action="store_true")
    args = parser.parse_args()

    output_root = args.output.resolve()
    spec = load_design_space(args.design_space)
    anchors = load_anchors(spec, args.anchors)

    if args.estimate_only:
        est = estimate(spec, anchors)
        print("=" * 60)
        print("map_space_v1 size estimate")
        print("=" * 60)
        for k, v in est.items():
            print(f"  {k}: {v}")
        print("=" * 60)
        return

    if args.dry_run:
        print(f"Dry run (seed={args.seed}, max_maps={args.max_maps})")
        count = 0
        for cand in iter_all_candidates(spec, args.seed, anchors):
            if count >= args.max_maps:
                break
            print(
                f"  [{cand.source_type}] {cand.map_id} archetype={cand.archetype} "
                f"anchor={cand.anchor_id}"
            )
            count += 1
        print(f"Would process {count} candidates")
        return

    if not args.generate:
        parser.error("Specify --estimate-only, --dry-run, or --generate")

    rows = run_generate(
        spec,
        anchors,
        output_root=output_root,
        max_maps=args.max_maps,
        seed=args.seed,
        force=args.force,
        yaml_path=args.design_space,
        skip_ok=args.skip_ok,
    )
    ok = sum(1 for r in rows if r["status"] == "ok")
    print(f"Done: {ok} maps generated, {len(rows)} manifest rows → {output_root / 'manifest_maps.csv'}")


if __name__ == "__main__":
    main()
