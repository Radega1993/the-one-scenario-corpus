#!/usr/bin/env python3
"""Lightweight pilot spatial metrics (numpy only; no pandas/scipy)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

_ANALYSIS = Path(__file__).resolve().parents[2]
_REPO = _ANALYSIS.parent.parent
_WKT = _REPO / "scenarios" / "maps" / "wkt"
_CAL = _ANALYSIS / "data" / "world_size_calibration.csv"
_OUT = _ANALYSIS / "data" / "pilot_spatial_metrics.csv"
_REPORTS = _REPO / "reports"

LINESTRING_RE = re.compile(r"LINESTRING\s*\(([^)]+)\)", re.IGNORECASE)
RE_WORLD = re.compile(r"^MovementModel\.worldSize\s*=\s*(\d+)\s*,\s*(\d+)", re.MULTILINE)
RE_MAP = re.compile(r"^MapBasedMovement\.mapFile1\s*=\s*(\S+)", re.MULTILINE)


def _parse_linestrings(path: Path) -> list[list[tuple[float, float]]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines: list[list[tuple[float, float]]] = []
    for m in LINESTRING_RE.finditer(text):
        pts: list[tuple[float, float]] = []
        for pair in m.group(1).split(","):
            parts = pair.strip().split()
            if len(parts) >= 2:
                try:
                    pts.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    continue
        if len(pts) >= 2:
            lines.append(pts)
    return lines


def _wkt_to_sim(raw: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    mirrored = [[(x, -y) for x, y in line] for line in raw]
    xs = [x for line in mirrored for x, _ in line]
    ys = [y for line in mirrored for _, y in line]
    min_x, min_y = min(xs), min(ys)
    return [[(x - min_x, y - min_y) for x, y in line] for line in mirrored]


def _cell_idx(x: float, y: float, wx: float, wy: float, gs: int) -> tuple[int, int]:
    cw, ch = wx / gs, wy / gs
    cx = max(0.0, min(x, wx))
    cy = max(0.0, min(y, wy))
    i = min(int(math.floor(cx / cw)), gs - 1)
    j = min(int(math.floor(cy / ch)), gs - 1)
    return max(i, 0), max(j, 0)


def _rasterize_roads(sim, wx: float, wy: float, gs: int) -> np.ndarray:
    road = np.zeros((gs, gs), dtype=bool)
    for line in sim:
        for k in range(len(line) - 1):
            x0, y0 = line[k]
            x1, y1 = line[k + 1]
            length = math.hypot(x1 - x0, y1 - y0)
            steps = max(int(math.ceil(length / (min(wx, wy) / gs / 4))), 1)
            for t in range(steps + 1):
                f = t / steps
                i, j = _cell_idx(x0 + f * (x1 - x0), y0 + f * (y1 - y0), wx, wy, gs)
                road[i, j] = True
    return road


def _bbox_mask(sim, wx: float, wy: float, gs: int, margin: float) -> np.ndarray:
    xs = [x for line in sim for x, _ in line]
    ys = [y for line in sim for _, y in line]
    x0, y0 = min(xs) - margin, min(ys) - margin
    x1, y1 = max(xs) + margin, max(ys) + margin
    cw, ch = wx / gs, wy / gs
    mask = np.zeros((gs, gs), dtype=bool)
    for i in range(gs):
        cx = (i + 0.5) * cw
        if cx < x0 or cx > x1:
            continue
        for j in range(gs):
            cy = (j + 0.5) * ch
            if y0 <= cy <= y1:
                mask[i, j] = True
    return mask


def _read_grid(path: Path, gs: int) -> np.ndarray:
    vis = np.zeros((gs, gs), dtype=bool)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            i, j = int(row["cell_i"]), int(row["cell_j"])
            if float(row["visit_count"]) > 0 and 0 <= i < gs and 0 <= j < gs:
                vis[i, j] = True
    return vis


def _settings_world(settings: Path) -> tuple[float, float]:
    text = settings.read_text(encoding="utf-8")
    m = RE_WORLD.search(text)
    if not m:
        return 0.0, 0.0
    return float(m.group(1)), float(m.group(2))


def _summary_world(summary: Path) -> tuple[float, float, int]:
    with summary.open(newline="", encoding="utf-8") as f:
        row = next(csv.DictReader(f), {})
    return float(row.get("world_x", 0)), float(row.get("world_y", 0)), int(float(row.get("grid_size", 50)))


def _margin_for_map(map_name: str) -> float:
    meta = _WKT / map_name / "metadata.json"
    if meta.is_file():
        data = json.loads(meta.read_text(encoding="utf-8"))
        return float(data.get("occupancy_margin_m", 50))
    return 50.0


def metrics_for_pilot(scenario: str, map_name: str, settings: Path, reports_dir: Path) -> dict:
    grid = reports_dir / f"{scenario}_spatial_occupancy_grid.csv"
    summary = reports_dir / f"{scenario}_spatial_occupancy_summary.csv"
    if not grid.is_file():
        return {"scenario": scenario, "status": "missing_grid"}
    wx_set, wy_set = _settings_world(settings)
    wx_sum, wy_sum, gs = _summary_world(summary) if summary.is_file() else (0, 0, 50)
    wx, wy = wx_set or wx_sum, wy_set or wy_sum
    mismatch = (
        wx_set > 0
        and wx_sum > 0
        and (abs(wx_set - wx_sum) > 2 or abs(wy_set - wy_sum) > 2)
    )
    status = "ok"
    if mismatch:
        status = "re_sim_required"
    roads = _REPO / "data" / map_name / "roads.wkt"
    sim = _wkt_to_sim(_parse_linestrings(roads))
    margin = _margin_for_map(map_name)
    road = _rasterize_roads(sim, wx, wy, gs)
    bbox = _bbox_mask(sim, wx, wy, gs, margin)
    vis = _read_grid(grid, gs)
    world_total = gs * gs
    road_total = int(road.sum())
    return {
        "scenario": scenario,
        "map_name": map_name,
        "status": status,
        "world_size_mismatch": mismatch,
        "world_x_settings": wx_set,
        "world_y_settings": wy_set,
        "world_x_summary": wx_sum,
        "world_y_summary": wy_sum,
        "occupancy_margin_m": margin,
        "coverage_world_pct": round(100.0 * vis.sum() / world_total, 4),
        "coverage_road_cells_pct": round(100.0 * (vis & road).sum() / road_total, 4)
        if road_total
        else None,
        "coverage_map_bbox_pct": round(100.0 * (vis & bbox).sum() / int(bbox.sum()), 4)
        if bbox.sum()
        else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--calibration-csv", type=Path, default=_CAL)
    ap.add_argument("--reports-dir", type=Path, default=_REPORTS)
    ap.add_argument("--corpus", type=Path, default=_REPO / "scenarios" / "corpus_v1")
    ap.add_argument("--output", type=Path, default=_OUT)
    args = ap.parse_args()

    if not args.calibration_csv.is_file():
        print(f"Missing {args.calibration_csv}")
        return 1

    rows_out: list[dict] = []
    with args.calibration_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pilot = row["pilot_scenario"]
            map_name = row["map_name"]
            settings = None
            for sf in args.corpus.rglob(f"{pilot}.settings"):
                settings = sf
                break
            if settings is None:
                rows_out.append(
                    {"scenario": pilot, "map_name": map_name, "status": "no_settings"}
                )
                continue
            m = metrics_for_pilot(pilot, map_name, settings, args.reports_dir)
            m["pilot_scenario"] = pilot
            rows_out.append(m)

    if not rows_out:
        return 1
    fields = list(rows_out[0].keys())
    for r in rows_out:
        fields.extend(k for k in r if k not in fields)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows_out)
    print(f"Wrote {args.output} ({len(rows_out)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
