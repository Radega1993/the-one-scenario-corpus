#!/usr/bin/env python3
"""Validate auxiliary route WKT files (*_bus, *_route, *_patrol, etc.) against roads.wkt."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import (  # noqa: E402
    ACTIVE_MAPS,
    ANALYSIS_DATA,
    SCENARIOS_DIR,
    euclidean_polyline_length,
    graph_path_length,
    list_route_wkt_files,
    load_road_graph,
    parse_linestrings,
    percentile,
    points_inside_world_size,
    threshold_for_family,
    vertex_distances,
    world_size_from_metadata,
    wkt_to_sim_coords,
)

REPORTS_DIR = SCENARIOS_DIR / "analysis" / "reports" / "maps"

def classify_route(
    *,
    within_ws: bool,
    pct_over: float,
    chord_ratio: float,
    crossing_suspect: bool,
    max_dist: float,
    threshold: float,
) -> str:
    if not within_ws or pct_over > 20 or max_dist > threshold * 3:
        return "FAIL"
    if crossing_suspect or pct_over > 5 or chord_ratio > 2.0 or max_dist > threshold:
        return "WARNING"
    return "PASS"

def validate_one(
    map_name: str,
    bus_path: Path,
    max_vertex_urban: float,
    max_vertex_rural: float,
    max_vertex_stress: float,
    max_cross: float,
    max_ratio: float,
) -> dict:
    rg, roads_path, meta = load_road_graph(map_name)
    family = meta.get("family", "")
    if family == "04_rural":
        thresh = max_vertex_rural
    else:
        thresh = max_vertex_urban

    raw_lines = parse_linestrings(bus_path)
    if not raw_lines:
        return {
            "map_name": map_name,
            "route_file": bus_path.name,
            "family": family,
            "status": "FAIL",
            "notes": "empty or unparseable LINESTRING",
        }

    sim_lines = wkt_to_sim_coords(raw_lines)
    verts = sim_lines[0] if len(sim_lines) == 1 else [p for seg in sim_lines for p in seg]

    dists = vertex_distances(rg, verts)
    n = len(verts)
    over = sum(1 for d in dists if d > thresh)
    pct_over = 100.0 * over / n if n else 0.0
    eucl = euclidean_polyline_length(verts)
    gpath = graph_path_length(rg, verts)
    ratio = (eucl / gpath) if gpath and gpath > 0 else 0.0
    max_seg = 0.0
    for i in range(len(verts) - 1):
        max_seg = max(max_seg, math.hypot(verts[i + 1][0] - verts[i][0], verts[i + 1][1] - verts[i][1]))

    crossing = max_seg > max_cross and ratio > 1.5
    wx, wy = world_size_from_metadata(meta)
    within_ws = points_inside_world_size(verts, wx, wy)

    status = classify_route(
        within_ws=within_ws,
        pct_over=pct_over,
        chord_ratio=ratio if ratio else 0.0,
        crossing_suspect=crossing,
        max_dist=max(dists) if dists else 0.0,
        threshold=thresh,
    )
    notes = []
    if not within_ws:
        notes.append("vertices outside worldSize")
    if crossing:
        notes.append(f"chord segment>{max_cross}m with high graph/eucl ratio")
    if ratio > max_ratio:
        notes.append(f"eucl/graph ratio {ratio:.2f}>{max_ratio}")

    return {
        "map_name": map_name,
        "route_file": bus_path.name,
        "family": family,
        "n_vertices": n,
        "euclidean_length_m": round(eucl, 1),
        "graph_path_length_m": round(gpath, 1) if gpath is not None else "",
        "chord_vs_graph_ratio": round(ratio, 3) if gpath else "",
        "mean_vertex_dist_m": round(sum(dists) / n, 2) if n else 0,
        "p95_vertex_dist_m": round(percentile(dists, 95), 2),
        "max_vertex_dist_m": round(max(dists), 2) if dists else 0,
        "pct_vertices_over_threshold": round(pct_over, 2),
        "threshold_m": thresh,
        "max_chord_segment_m": round(max_seg, 1),
        "crossing_suspect": crossing,
        "within_world_size": within_ws,
        "world_size_x": int(wx),
        "world_size_y": int(wy),
        "status": status,
        "notes": "; ".join(notes),
    }

def write_report(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Route file validation report",
        "",
        f"Generated: {ts}",
        "",
        "Route files in wiki figures are **waypoint sequences** (`routeFile`), not roads. "
        "The ONE moves carriers with shortest paths on the road graph between waypoints.",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|--------|------:|",
    ]
    for st in ("PASS", "WARNING", "FAIL"):
        c = sum(1 for r in rows if r.get("status") == st)
        lines.append(f"| {st} | {c} |")
    lines.extend(["", "## Per route", "", "| Map | Route | Status | Ratio | Max dist (m) | Notes |", "|-----|-------|--------|-------|--------------|-------|"])
    for r in rows:
        lines.append(
            f"| {r.get('map_name','')} | {r.get('route_file','')} | {r.get('status','')} | "
            f"{r.get('chord_vs_graph_ratio','')} | {r.get('max_vertex_dist_m','')} | {r.get('notes','')} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-vertex-distance-urban", type=float, default=50.0)
    ap.add_argument("--max-vertex-distance-rural", type=float, default=150.0)
    ap.add_argument("--max-vertex-distance-stress", type=float, default=100.0)
    ap.add_argument("--max-segment-cross-distance", type=float, default=200.0)
    ap.add_argument("--max-chord-graph-ratio", type=float, default=2.0)
    ap.add_argument("--output-csv", type=str, default=str(ANALYSIS_DATA / "bus_route_validation.csv"))
    ap.add_argument("--output-report", type=str, default=str(REPORTS_DIR / "bus_route_validation_report.md"))
    args = ap.parse_args()

    rows: list[dict] = []
    for map_name in ACTIVE_MAPS:
        wkt_dir = Path(__file__).resolve().parent.parent / "maps" / "wkt" / map_name
        for bus_path in list_route_wkt_files(wkt_dir):
            rows.append(
                validate_one(
                    map_name,
                    bus_path,
                    args.max_vertex_distance_urban,
                    args.max_vertex_distance_rural,
                    args.max_vertex_distance_stress,
                    args.max_segment_cross_distance,
                    args.max_chord_graph_ratio,
                )
            )

    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    write_report(rows, Path(args.output_report))
    print(f"Wrote {out_csv}")
    print(f"Wrote {args.output_report}")
    fails = [r for r in rows if r.get("status") == "FAIL"]
    return 1 if fails else 0

if __name__ == "__main__":
    raise SystemExit(main())