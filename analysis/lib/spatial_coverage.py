"""
Spatial coverage metrics with multiple denominators (world, map bbox, road cells, buffers).

The ONE SpatialOccupancyReport reports coverage over the full MovementModel.worldSize grid.
This module derives interpretable metrics using roads.wkt in simulation-aligned coordinates.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import ndimage

from lib.map_context import build_map_context, load_settings_flat, roads_wkt_from_settings
from lib.paths import REPO_ROOT

DEFAULT_BUFFER_M_LIST: tuple[int, ...] = (10, 15, 25)
DEFAULT_BBOX_MARGIN_M = 50.0
WKT_MAPS_DIR = REPO_ROOT / "scenarios" / "maps" / "wkt"


def occupancy_margin_from_metadata(meta: dict, default: float = DEFAULT_BBOX_MARGIN_M) -> float:
    for key in ("occupancy_margin_m", "world_size_margin_m"):
        if key in meta:
            try:
                return float(meta[key])
            except (TypeError, ValueError):
                pass
    return default


def bbox_margin_for_map(map_name: str | None, default: float = DEFAULT_BBOX_MARGIN_M) -> float:
    if not map_name:
        return default
    meta_path = WKT_MAPS_DIR / map_name / "metadata.json"
    if not meta_path.is_file():
        return default
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default
    return occupancy_margin_from_metadata(meta, default)

_MASK_CACHE: dict[tuple[Any, ...], RoadCellMasks] = {}

@dataclass
class RoadCellMasks:
    """Boolean masks over the occupancy grid (shape grid_size x grid_size, index cell_i, cell_j)."""

    grid_size: int
    world_x: float
    world_y: float
    cell_w: float
    cell_h: float
    road_cell: np.ndarray
    road_buffer: dict[int, np.ndarray] = field(default_factory=dict)
    map_bbox: tuple[float, float, float, float] | None = None

    @property
    def map_bbox_mask(self) -> np.ndarray:
        if self.map_bbox is None:
            return np.zeros_like(self.road_cell, dtype=bool)
        x0, y0, x1, y1 = self.map_bbox
        gs = self.grid_size
        mask = np.zeros((gs, gs), dtype=bool)
        for i in range(gs):
            cx = (i + 0.5) * self.cell_w
            if cx < x0 or cx > x1:
                continue
            for j in range(gs):
                cy = (j + 0.5) * self.cell_h
                if y0 <= cy <= y1:
                    mask[i, j] = True
        return mask

def map_name_from_settings(settings_path: Path | None, repo_root: Path = REPO_ROOT) -> str | None:
    """Extract map folder name from MapBasedMovement.mapFile1 or scenarios/maps/wkt/."""
    if settings_path and settings_path.is_file():
        kv = load_settings_flat(settings_path)
        raw = kv.get("MapBasedMovement.mapFile1", "")
        if raw:
            p = Path(raw)
            if not p.is_absolute():
                p = repo_root / p
            if p.is_file():
                return p.parent.name
            parts = p.parts
            if "wkt" in parts:
                idx = parts.index("wkt")
                if idx + 1 < len(parts):
                    return parts[idx + 1]
    return None

def roads_bbox_sim(
    roads_sim: list[list[tuple[float, float]]] | None,
    *,
    margin: float = DEFAULT_BBOX_MARGIN_M,
) -> tuple[float, float, float, float] | None:
    if not roads_sim:
        return None
    xs: list[float] = []
    ys: list[float] = []
    for line in roads_sim:
        for x, y in line:
            xs.append(x)
            ys.append(y)
    if not xs:
        return None
    return (min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin)

def _cell_indices_for_point(x: float, y: float, world_x: float, world_y: float, gs: int) -> tuple[int, int]:
    """Match SpatialOccupancyReport.cellIndex (clamp to grid)."""
    cell_w = world_x / gs
    cell_h = world_y / gs
    cx = max(0.0, min(float(x), float(world_x)))
    cy = max(0.0, min(float(y), float(world_y)))
    i = int(math.floor(cx / cell_w))
    j = int(math.floor(cy / cell_h))
    if i >= gs:
        i = gs - 1
    if j >= gs:
        j = gs - 1
    if i < 0:
        i = 0
    if j < 0:
        j = 0
    return i, j

def _rasterize_segment(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    mask: np.ndarray,
    world_x: float,
    world_y: float,
    gs: int,
) -> None:
    length = math.hypot(x1 - x0, y1 - y0)
    if length < 1e-9:
        i, j = _cell_indices_for_point(x0, y0, world_x, world_y, gs)
        mask[i, j] = True
        return
    cell_min = min(world_x / gs, world_y / gs) / 4.0
    steps = max(int(math.ceil(length / max(cell_min, 1e-6))), 1)
    for k in range(steps + 1):
        t = k / steps
        x = x0 + t * (x1 - x0)
        y = y0 + t * (y1 - y0)
        i, j = _cell_indices_for_point(x, y, world_x, world_y, gs)
        mask[i, j] = True

def build_road_cell_masks(
    roads_sim: list[list[tuple[float, float]]] | None,
    *,
    world_x: float,
    world_y: float,
    grid_size: int,
    buffer_m_list: tuple[int, ...] = DEFAULT_BUFFER_M_LIST,
    bbox_margin: float = DEFAULT_BBOX_MARGIN_M,
    cache_key: tuple[Any, ...] | None = None,
) -> RoadCellMasks | None:
    """Mark cells intersecting road segments; dilate for buffer variants."""
    gs = int(grid_size)
    if gs < 1 or world_x <= 0 or world_y <= 0 or not roads_sim:
        return None

    if cache_key is not None and cache_key in _MASK_CACHE:
        return _MASK_CACHE[cache_key]

    cell_w = world_x / gs
    cell_h = world_y / gs
    road_cell = np.zeros((gs, gs), dtype=bool)
    for line in roads_sim:
        if len(line) < 2:
            continue
        for k in range(len(line) - 1):
            x0, y0 = line[k]
            x1, y1 = line[k + 1]
            _rasterize_segment(x0, y0, x1, y1, road_cell, world_x, world_y, gs)

    road_buffer: dict[int, np.ndarray] = {}
    cell_min = min(cell_w, cell_h)
    for buf_m in buffer_m_list:
        radius_cells = max(int(math.ceil(float(buf_m) / cell_min)), 1)
        y, x = np.ogrid[-radius_cells : radius_cells + 1, -radius_cells : radius_cells + 1]
        struct = (x * x + y * y) <= radius_cells * radius_cells
        road_buffer[int(buf_m)] = ndimage.binary_dilation(road_cell, structure=struct)

    masks = RoadCellMasks(
        grid_size=gs,
        world_x=float(world_x),
        world_y=float(world_y),
        cell_w=cell_w,
        cell_h=cell_h,
        road_cell=road_cell,
        road_buffer=road_buffer,
        map_bbox=roads_bbox_sim(roads_sim, margin=bbox_margin),
    )
    if cache_key is not None:
        _MASK_CACHE[cache_key] = masks
    return masks

def visited_mask_from_grid(grid_df: pd.DataFrame, grid_size: int) -> np.ndarray:
    """Boolean (gs, gs) visited cells from occupancy grid CSV."""
    gs = int(grid_size)
    vis = np.zeros((gs, gs), dtype=bool)
    for _, row in grid_df.iterrows():
        i, j = int(row["cell_i"]), int(row["cell_j"])
        if 0 <= i < gs and 0 <= j < gs and float(row["visit_count"]) > 0:
            vis[i, j] = True
    return vis

def _coverage_pct(visited: int, total: int) -> float | None:
    if total <= 0:
        return None
    return round(100.0 * visited / total, 4)

def compute_spatial_coverage_metrics(
    grid_df: pd.DataFrame,
    masks: RoadCellMasks | None,
    *,
    scenario_name: str = "",
    map_name: str | None = None,
) -> dict[str, float | int | str | None]:
    """Full metric row for spatial_occupancy_metrics.csv."""
    gs = masks.grid_size if masks else int(grid_df["cell_i"].max()) + 1
    wx = masks.world_x if masks else 0.0
    wy = masks.world_y if masks else 0.0
    visited = visited_mask_from_grid(grid_df, gs)

    world_total = gs * gs
    world_visited = int(visited.sum())

    out: dict[str, float | int | str | None] = {
        "scenario_name": scenario_name,
        "map_name": map_name or "",
        "grid_size": gs,
        "world_width": round(wx, 4) if wx else None,
        "world_height": round(wy, 4) if wy else None,
        "world_total_cells": world_total,
        "world_visited_cells": world_visited,
        "coverage_world_pct": _coverage_pct(world_visited, world_total),
        "map_bbox_total_cells": None,
        "map_bbox_visited_cells": None,
        "coverage_map_bbox_pct": None,
        "road_total_cells": None,
        "road_visited_cells": None,
        "coverage_road_cells_pct": None,
    }
    for buf_m in DEFAULT_BUFFER_M_LIST:
        out[f"road_buffer_{buf_m}m_total_cells"] = None
        out[f"road_buffer_{buf_m}m_visited_cells"] = None
        out[f"coverage_road_buffer_{buf_m}m_pct"] = None

    if masks is None:
        return out

    bbox_m = masks.map_bbox_mask
    road_m = masks.road_cell
    bbox_total = int(bbox_m.sum())
    bbox_vis = int((visited & bbox_m).sum())
    road_total = int(road_m.sum())
    road_vis = int((visited & road_m).sum())

    out.update(
        {
            "map_bbox_total_cells": bbox_total,
            "map_bbox_visited_cells": bbox_vis,
            "coverage_map_bbox_pct": _coverage_pct(bbox_vis, bbox_total),
            "road_total_cells": road_total,
            "road_visited_cells": road_vis,
            "coverage_road_cells_pct": _coverage_pct(road_vis, road_total),
        }
    )
    for buf_m, buf_mask in masks.road_buffer.items():
        bt = int(buf_mask.sum())
        bv = int((visited & buf_mask).sum())
        out[f"road_buffer_{buf_m}m_total_cells"] = bt
        out[f"road_buffer_{buf_m}m_visited_cells"] = bv
        out[f"coverage_road_buffer_{buf_m}m_pct"] = _coverage_pct(bv, bt)

    return out

def masks_for_scenario(
    settings_path: Path | None,
    *,
    world_x: float,
    world_y: float,
    grid_size: int,
    buffer_m_list: tuple[int, ...] = DEFAULT_BUFFER_M_LIST,
    bbox_margin: float | None = None,
) -> tuple[RoadCellMasks | None, str | None]:
    ctx = build_map_context(settings_path, world_x=world_x, world_y=world_y, load_roads=True)
    map_name = map_name_from_settings(settings_path)
    margin = bbox_margin if bbox_margin is not None else bbox_margin_for_map(map_name)
    roads_path = ctx.roads_path
    cache_key = None
    if roads_path and roads_path.is_file():
        cache_key = (
            str(roads_path.resolve()),
            int(grid_size),
            round(world_x, 3),
            round(world_y, 3),
            buffer_m_list,
            round(margin, 3),
        )
    masks = build_road_cell_masks(
        ctx.roads_sim,
        world_x=world_x,
        world_y=world_y,
        grid_size=grid_size,
        buffer_m_list=buffer_m_list,
        bbox_margin=margin,
        cache_key=cache_key,
    )
    return masks, map_name

def metrics_for_scenario(
    grid_path: Path,
    settings_path: Path | None,
    *,
    scenario_name: str = "",
    world_x: float | None = None,
    world_y: float | None = None,
    grid_size: int | None = None,
) -> dict[str, float | int | str | None]:
    df = pd.read_csv(grid_path)
    name = scenario_name or grid_path.stem.replace("_spatial_occupancy_grid", "")
    ctx = build_map_context(settings_path, world_x=world_x, world_y=world_y, load_roads=False)
    wx = float(world_x if world_x is not None else ctx.world_x or 1.0)
    wy = float(world_y if world_y is not None else ctx.world_y or 1.0)
    gs = int(grid_size) if grid_size is not None else int(df["cell_i"].max()) + 1
    masks, map_name = masks_for_scenario(settings_path, world_x=wx, world_y=wy, grid_size=gs)
    return compute_spatial_coverage_metrics(df, masks, scenario_name=name, map_name=map_name)

def zoom_extent_from_masks(
    masks: RoadCellMasks,
    visited: np.ndarray,
    mode: str,
    *,
    pad_cells: int = 2,
) -> tuple[int, int, int, int]:
    """Return i0, i1, j0, j1 cell index ranges for heatmap zoom (exclusive upper)."""
    gs = masks.grid_size
    if mode == "map_bbox" and masks.map_bbox is not None:
        bb = masks.map_bbox_mask
        idx = np.argwhere(bb)
    elif mode == "roads":
        idx = np.argwhere(masks.road_cell)
    else:
        idx = np.argwhere(visited)
    if idx.size == 0:
        return 0, gs, 0, gs
    i0 = max(int(idx[:, 0].min()) - pad_cells, 0)
    i1 = min(int(idx[:, 0].max()) + pad_cells + 1, gs)
    j0 = max(int(idx[:, 1].min()) - pad_cells, 0)
    j1 = min(int(idx[:, 1].max()) + pad_cells + 1, gs)
    return i0, i1, j0, j1

def coverage_title_parts(metrics: dict[str, float | int | str | None]) -> list[str]:
    """Short labels for heatmap titles."""
    parts: list[str] = []
    w = metrics.get("coverage_world_pct")
    if w is not None:
        parts.append(f"world {float(w):.1f}%")
    b = metrics.get("coverage_map_bbox_pct")
    if b is not None:
        parts.append(f"map bbox {float(b):.1f}%")
    r = metrics.get("coverage_road_cells_pct")
    if r is not None:
        parts.append(f"road cells {float(r):.1f}%")
    b25 = metrics.get("coverage_road_buffer_25m_pct")
    if b25 is not None:
        parts.append(f"buffer25 {float(b25):.1f}%")
    return parts

def enrich_timeseries_from_positions(
    world_ts: pd.DataFrame,
    node_pos_path: Path,
    masks: RoadCellMasks,
    *,
    time_bin_size: float,
    end_time: float | None = None,
) -> pd.DataFrame:
    """
    Replay NodePositionReport to compute multi-denominator coverage per time bin.
    world_ts must contain time_bin_end (and optionally legacy coverage_pct).
    """
    if not node_pos_path.is_file() or node_pos_path.stat().st_size == 0:
        return world_ts
    try:
        pos = pd.read_csv(node_pos_path)
    except pd.errors.EmptyDataError:
        return world_ts
    if pos.empty or "time" not in pos.columns:
        return world_ts

    gs = masks.grid_size
    wx, wy = masks.world_x, masks.world_y
    bbox_m = masks.map_bbox_mask
    road_m = masks.road_cell
    world_total = gs * gs
    bbox_total = int(bbox_m.sum())
    road_total = int(road_m.sum())
    buf_masks = masks.road_buffer
    buf_totals = {b: int(buf_masks[b].sum()) for b in buf_masks}

    ever_world: set[tuple[int, int]] = set()
    ever_bbox: set[tuple[int, int]] = set()
    ever_road: set[tuple[int, int]] = set()
    ever_buf: dict[int, set[tuple[int, int]]] = {b: set() for b in buf_masks}

    pos = pos.sort_values("time")
    bin_ends = world_ts["time_bin_end"].to_numpy(dtype=float)
    if end_time is not None and end_time > 0:
        bin_ends = bin_ends[bin_ends <= float(end_time) + 1e-6]

    rows: list[dict[str, Any]] = []
    pos_idx = 0
    n_pos = len(pos)

    for t_end in bin_ends:
        while pos_idx < n_pos and float(pos.iloc[pos_idx]["time"]) <= t_end + 1e-9:
            row = pos.iloc[pos_idx]
            i, j = _cell_indices_for_point(
                float(row["x"]), float(row["y"]), wx, wy, gs
            )
            ever_world.add((i, j))
            if bbox_m[i, j]:
                ever_bbox.add((i, j))
            if road_m[i, j]:
                ever_road.add((i, j))
            for buf_m, bm in buf_masks.items():
                if bm[i, j]:
                    ever_buf[buf_m].add((i, j))
            pos_idx += 1

        rec: dict[str, Any] = {
            "time_bin_end": t_end,
            "coverage_world_pct": _coverage_pct(len(ever_world), world_total),
            "coverage_map_bbox_pct": _coverage_pct(len(ever_bbox), bbox_total),
            "coverage_road_cells_pct": _coverage_pct(len(ever_road), road_total),
        }
        for buf_m in sorted(buf_masks.keys()):
            rec[f"coverage_road_buffer_{buf_m}m_pct"] = _coverage_pct(
                len(ever_buf[buf_m]), buf_totals[buf_m]
            )
        rows.append(rec)

    cov_df = pd.DataFrame(rows)
    meta_cols = [
        c
        for c in world_ts.columns
        if c not in ("coverage_pct", "coverage_world_pct")
        and not (c.startswith("coverage_") and c.endswith("_pct"))
    ]
    meta = world_ts[meta_cols].reset_index(drop=True)
    return pd.concat([meta, cov_df.drop(columns=["time_bin_end"])], axis=1)

# Backward compatibility
def compute_coverage_breakdown(
    grid_df: pd.DataFrame,
    *,
    world_x: float,
    world_y: float,
    grid_size: int,
    roads_sim: list[list[tuple[float, float]]] | None,
    bbox_margin: float = DEFAULT_BBOX_MARGIN_M,
) -> dict[str, float | int | None]:
    cache_key = None
    masks = build_road_cell_masks(
        roads_sim,
        world_x=world_x,
        world_y=world_y,
        grid_size=grid_size,
        bbox_margin=bbox_margin,
        cache_key=cache_key,
    )
    m = compute_spatial_coverage_metrics(grid_df, masks)
    return {
        "coverage_world_pct": m.get("coverage_world_pct"),
        "coverage_map_bbox_pct": m.get("coverage_map_bbox_pct"),
        "cells_outside_map_bbox_pct": round(
            100.0
            * (int(m.get("world_total_cells") or 0) - int(m.get("map_bbox_total_cells") or 0))
            / max(int(m.get("world_total_cells") or 1), 1),
            4,
        )
        if m.get("map_bbox_total_cells")
        else None,
        "cells_visited": m.get("world_visited_cells"),
        "cells_total": m.get("world_total_cells"),
        "cells_in_map_bbox": m.get("map_bbox_total_cells"),
        "cells_visited_in_map_bbox": m.get("map_bbox_visited_cells"),
        "coverage_road_cells_pct": m.get("coverage_road_cells_pct"),
    }

def coverage_breakdown_for_scenario(
    grid_path: Path,
    settings_path: Path | None,
    *,
    world_x: float | None = None,
    world_y: float | None = None,
    grid_size: int | None = None,
) -> dict[str, float | int | None]:
    return metrics_for_scenario(
        grid_path,
        settings_path,
        world_x=world_x,
        world_y=world_y,
        grid_size=grid_size,
    )