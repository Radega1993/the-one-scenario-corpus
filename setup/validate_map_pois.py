#!/usr/bin/env python3
"""Validate POI WKT files against roads and worldSize."""

from __future__ import annotations

import argparse
import csv
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
    load_road_graph,
    parse_points,
    percentile,
    points_inside_world_size,
    threshold_for_family,
    transform_points,
    vertex_distances,
    world_size_from_metadata,
    WKT_DIR,
)

REPORTS_DIR = SCENARIOS_DIR / "analysis" / "reports" / "maps"

POI_TYPES = (
    ("A_homes.wkt", "homes"),
    ("A_offices.wkt", "offices"),
    ("A_meetingspots.wkt", "meetingspots"),
)


def classify_poi(pct_inside: float, pct_over: float, max_dist: float, thresh: float) -> str:
    if pct_inside < 100:
        return "FAIL"
    if pct_over > 20 or max_dist > thresh * 3:
        return "FAIL"
    if pct_over > 5 or max_dist > thresh:
        return "WARNING"
    return "PASS"


def validate_poi(map_name: str, poi_path: Path, poi_type: str) -> dict:
    rg, _, meta = load_road_graph(map_name)
    family = meta.get("family", "")
    thresh = threshold_for_family(family)
    raw_pts = parse_points(poi_path)
    verts = transform_points(raw_pts)
    wx, wy = world_size_from_metadata(meta)
    n = len(verts)
    inside = sum(1 for x, y in verts if 0 <= x <= wx and 0 <= y <= wy) if wx and wy else n
    pct_inside = 100.0 * inside / n if n else 100.0
    dists = vertex_distances(rg, verts)
    over = sum(1 for d in dists if d > thresh)
    pct_over = 100.0 * over / n if n else 0.0
    status = classify_poi(pct_inside, pct_over, max(dists) if dists else 0.0, thresh)
    notes = []
    if pct_inside < 100:
        notes.append("POIs outside worldSize")
    if pct_over > 0:
        notes.append(f"{over} POIs >{thresh}m from road")
    return {
        "map_name": map_name,
        "poi_file": poi_path.name,
        "poi_type": poi_type,
        "family": family,
        "n_points": n,
        "pct_inside_world_size": round(pct_inside, 2),
        "mean_dist_to_road_m": round(sum(dists) / n, 2) if n else 0,
        "p95_dist_to_road_m": round(percentile(dists, 95), 2),
        "max_dist_to_road_m": round(max(dists), 2) if dists else 0,
        "n_over_threshold": over,
        "pct_over_threshold": round(pct_over, 2),
        "threshold_m": thresh,
        "world_size_x": int(wx),
        "world_size_y": int(wy),
        "status": status,
        "notes": "; ".join(notes),
    }


def write_report(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Map POI validation report",
        "",
        f"Generated: {ts}",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|--------|------:|",
    ]
    for st in ("PASS", "WARNING", "FAIL"):
        lines.append(f"| {st} | {sum(1 for r in rows if r.get('status') == st)} |")
    lines.extend(
        [
            "",
            "## Per file",
            "",
            "| Map | POI file | Status | Inside WS % | Max dist (m) | Notes |",
            "|-----|----------|--------|-------------|--------------|-------|",
        ]
    )
    for r in rows:
        lines.append(
            f"| {r['map_name']} | {r['poi_file']} | {r['status']} | "
            f"{r['pct_inside_world_size']} | {r['max_dist_to_road_m']} | {r.get('notes','')} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-csv", type=str, default=str(ANALYSIS_DATA / "map_poi_validation.csv"))
    ap.add_argument("--output-report", type=str, default=str(REPORTS_DIR / "map_poi_validation_report.md"))
    args = ap.parse_args()

    rows: list[dict] = []
    for map_name in ACTIVE_MAPS:
        wkt_dir = WKT_DIR / map_name
        for fname, ptype in POI_TYPES:
            p = wkt_dir / fname
            if p.is_file():
                rows.append(validate_poi(map_name, p, ptype))

    out = Path(args.output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    write_report(rows, Path(args.output_report))
    print(f"Wrote {out}")
    print(f"Wrote {args.output_report}")
    return 1 if any(r.get("status") == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
