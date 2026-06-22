"""OSM download, cache, and WKT build for map_space_saturation_v1."""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from map_geometry import world_size_from_sim_roads
from map_space_preview import render_preview
from map_space_synthetic import write_roads_wkt

logger = logging.getLogger(__name__)

TRANSIENT_NETWORK = "TRANSIENT_NETWORK"
EMPTY_OSM_RESPONSE = "EMPTY_OSM_RESPONSE"
INVALID_BBOX = "INVALID_BBOX"
BUILD_ERROR = "BUILD_ERROR"
UNKNOWN = "UNKNOWN"

QUEUE_COLUMNS = [
    "map_id",
    "anchor_id",
    "bbox",
    "network_type",
    "status",
    "attempts",
    "last_error",
    "last_attempt_at",
    "raw_graphml_path",
    "raw_geojson_path",
    "cache_hit",
    "notes",
]

QUEUE_STATUS_PENDING = "PENDING"
QUEUE_STATUS_DOWNLOADED = "DOWNLOADED"
QUEUE_STATUS_FAILED_TRANSIENT = "FAILED_TRANSIENT"
QUEUE_STATUS_FAILED_PERMANENT = "FAILED_PERMANENT"
QUEUE_STATUS_SKIPPED = "SKIPPED"


@dataclass
class OsmDownloadResult:
    success: bool
    graphml_path: Path | None
    cache_hit: bool
    error_kind: str | None
    error_message: str


@dataclass
class OsmBuildContext:
    map_id: str
    source_type: str
    anchor_id: str
    anchor_label: str
    archetype: str
    crs: str
    network_type: str
    params: dict[str, Any]
    allow_partitioned: bool
    topology_flags: list[str]
    variant_type: str
    anchor_distance_m: float
    window_size_m: float
    seed: int


def meters_to_degrees_bbox(lat: float, lon: float, width_m: float, height_m: float) -> tuple[float, float, float, float]:
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat))
    half_h = (height_m / 2.0) / m_per_deg_lat
    half_w = (width_m / 2.0) / m_per_deg_lon if m_per_deg_lon != 0 else 0.0
    north = lat + half_h
    south = lat - half_h
    west = lon - half_w
    east = lon + half_w
    return north, south, east, west


def classify_osm_error(exc: BaseException) -> str:
    msg = str(exc).lower()
    if isinstance(exc, ValueError):
        if "bbox" in msg or "south" in msg or "north" in msg or "west" in msg or "east" in msg:
            return INVALID_BBOX
        return BUILD_ERROR
    if isinstance(exc, ConnectionResetError):
        return TRANSIENT_NETWORK
    try:
        import requests

        if isinstance(exc, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
            return TRANSIENT_NETWORK
    except ModuleNotFoundError:
        pass
    try:
        import osmnx._errors as ox_errors

        if isinstance(exc, ox_errors.InsufficientResponseError):
            return EMPTY_OSM_RESPONSE
    except (ModuleNotFoundError, AttributeError):
        pass
    if "connection reset" in msg or "timed out" in msg or "timeout" in msg:
        return TRANSIENT_NETWORK
    if "insufficient" in msg or "no data" in msg or "empty" in msg:
        return EMPTY_OSM_RESPONSE
    if "invalid bbox" in msg:
        return INVALID_BBOX
    return UNKNOWN


def osm_cache_dir(output_root: Path) -> Path:
    return output_root / "osm_cache"


def canonical_cache_path(output_root: Path, map_id: str) -> Path:
    return osm_cache_dir(output_root) / f"{map_id}.graphml"


def find_cached_graphml(output_root: Path, map_id: str) -> Path | None:
    primary = canonical_cache_path(output_root, map_id)
    if primary.is_file() and primary.stat().st_size > 0:
        return primary
    for p in sorted(output_root.glob("batch_*/raw_osm/*.graphml")):
        if p.stem == map_id and p.stat().st_size > 0:
            return p
    return None


def graph_from_bbox_compat(
    north: float,
    south: float,
    east: float,
    west: float,
    network_type: str,
    *,
    timeout: int = 180,
) -> Any:
    import osmnx as ox

    if south >= north:
        raise ValueError(f"Invalid bbox: south ({south}) >= north ({north})")
    if west >= east:
        raise ValueError(f"Invalid bbox: west ({west}) >= east ({east})")

    ox.settings.timeout = int(timeout)
    version = getattr(ox, "__version__", "1.0.0")
    major = int(version.split(".")[0])
    if major >= 2:
        return ox.graph_from_bbox(
            bbox=(west, south, east, north),
            network_type=network_type,
            simplify=True,
        )
    return ox.graph_from_bbox(
        north,
        south,
        east,
        west,
        network_type=network_type,
        simplify=True,
    )


def graph_to_edges(
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


def download_osm_graph_for_candidate(
    *,
    map_id: str,
    params: dict[str, Any],
    network_type: str,
    output_root: Path,
    raw_dir: Path | None = None,
    timeout: int = 180,
    pause_seconds: float = 0.0,
    use_cache: bool = True,
) -> OsmDownloadResult:
    cache_path = canonical_cache_path(output_root, map_id)
    if use_cache:
        existing = find_cached_graphml(output_root, map_id)
        if existing is not None:
            if existing != cache_path:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_bytes(existing.read_bytes())
            return OsmDownloadResult(
                success=True,
                graphml_path=cache_path,
                cache_hit=True,
                error_kind=None,
                error_message="",
            )

    try:
        lat = float(params["center_lat"])
        lon = float(params["center_lon"])
        w = float(params["width_m"])
        h = float(params["height_m"])
        north, south, east, west = meters_to_degrees_bbox(lat, lon, w, h)
    except (KeyError, TypeError, ValueError) as exc:
        return OsmDownloadResult(
            success=False,
            graphml_path=None,
            cache_hit=False,
            error_kind=INVALID_BBOX,
            error_message=str(exc),
        )

    if pause_seconds > 0:
        time.sleep(pause_seconds)

    try:
        G = graph_from_bbox_compat(north, south, east, west, network_type, timeout=timeout)
        if G is None or getattr(G, "number_of_nodes", lambda: 0)() == 0:
            return OsmDownloadResult(
                success=False,
                graphml_path=None,
                cache_hit=False,
                error_kind=EMPTY_OSM_RESPONSE,
                error_message="empty graph (0 nodes)",
            )
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        import osmnx as ox

        ox.save_graphml(G, str(cache_path))
        if raw_dir is not None:
            raw_dir.mkdir(parents=True, exist_ok=True)
            raw_copy = raw_dir / f"{map_id}.graphml"
            if not raw_copy.is_file():
                raw_copy.write_bytes(cache_path.read_bytes())
        meta = {
            "map_id": map_id,
            "network_type": network_type,
            "bbox": {"north": north, "south": south, "east": east, "west": west},
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
        }
        (cache_path.with_suffix(".metadata.json")).write_text(
            json.dumps(meta, indent=2) + "\n",
            encoding="utf-8",
        )
        return OsmDownloadResult(
            success=True,
            graphml_path=cache_path,
            cache_hit=False,
            error_kind=None,
            error_message="",
        )
    except Exception as exc:
        kind = classify_osm_error(exc)
        return OsmDownloadResult(
            success=False,
            graphml_path=None,
            cache_hit=False,
            error_kind=kind,
            error_message=str(exc),
        )


def write_osm_metadata(
    path: Path,
    ctx: OsmBuildContext,
    *,
    world_size: tuple[int, int],
    margin_m: float,
    info: dict[str, Any],
    n_edges: int,
) -> None:
    north, south, east, west = meters_to_degrees_bbox(
        float(ctx.params["center_lat"]),
        float(ctx.params["center_lon"]),
        float(ctx.params["width_m"]),
        float(ctx.params["height_m"]),
    )
    meta = {
        "name": ctx.map_id,
        "map_id": ctx.map_id,
        "source": ctx.source_type,
        "source_type": ctx.source_type,
        "anchor_id": ctx.anchor_id or None,
        "anchor_label": ctx.anchor_label or None,
        "archetype": ctx.archetype,
        "generator_type": None,
        "map_generator_type": ctx.archetype,
        "map_archetype": ctx.archetype,
        "crs": ctx.crs,
        "network_type": ctx.network_type,
        "world_size": list(world_size),
        "occupancy_margin_m": margin_m,
        "world_size_policy": f"sim_road_max_plus_{int(margin_m)}m_margin_per_axis",
        "n_road_segments": n_edges,
        "n_edges": n_edges,
        "n_nodes": info.get("n_nodes", 0),
        "bbox_latlon": [south, west, north, east],
        "bbox_m": [
            info.get("min_x", 0),
            info.get("min_y", 0),
            info.get("max_x", 0),
            info.get("max_y", 0),
        ],
        "variant_type": ctx.variant_type or None,
        "anchor_distance_m": ctx.anchor_distance_m,
        "window_size_m": ctx.window_size_m or None,
        "generator_params": ctx.params,
        "topology_flags": ctx.topology_flags or None,
        "n_components": info.get("n_components", 1),
        "seed": ctx.seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "generated",
    }
    path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def build_osm_map_from_cache(
    *,
    ctx: OsmBuildContext,
    output_root: Path,
    wkt_dir: Path,
    preview_dir: Path,
    margin_m: float = 50.0,
    min_segments: int = 20,
) -> tuple[str, str]:
    graphml = find_cached_graphml(output_root, ctx.map_id)
    if graphml is None:
        return "FAIL_DOWNLOAD_TRANSIENT", "no cached graphml; run --acquire-osm first"

    try:
        import osmnx as ox

        G = ox.load_graphml(str(graphml))
        keep_largest = not ctx.allow_partitioned
        edges, info = graph_to_edges(G, ctx.crs, keep_largest_only=keep_largest)
    except Exception as exc:
        return "FAIL_BUILD_OSM", f"osm_process: {exc}"

    if len(edges) < min_segments:
        return "FAIL_BUILD_OSM", f"too few segments ({len(edges)} < {min_segments})"

    try:
        wkt_dir.mkdir(parents=True, exist_ok=True)
        roads_path = wkt_dir / "roads.wkt"
        write_roads_wkt(edges, roads_path)
        world_size = world_size_from_sim_roads(roads_path, margin_m)
        write_osm_metadata(
            wkt_dir / "metadata.json",
            ctx,
            world_size=world_size,
            margin_m=margin_m,
            info=info,
            n_edges=len(edges),
        )
        preview_path = preview_dir / f"{ctx.map_id}.png"
        render_preview(roads_path, preview_path, world_size)
    except Exception as exc:
        msg = str(exc)
        if "preview" in msg.lower():
            return "FAIL_PREVIEW", msg
        if "metadata" in msg.lower():
            return "FAIL_METADATA", msg
        return "FAIL_BUILD_OSM", msg

    return "OK", ""
