#!/usr/bin/env python3
"""Build map_assets_inventory.csv for active benchmark maps."""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import (  # noqa: E402
    ACTIVE_MAPS,
    ANALYSIS_DATA,
    DATA_DIR,
    WKT_DIR,
    list_route_wkt_files,
    list_poi_wkt_files,
    load_map_metadata,
    parse_linestrings,
    parse_points,
    wkt_to_sim_coords,
    world_size_from_metadata,
)

def file_md5(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.md5(path.read_bytes()).hexdigest()[:12]

def inventory_row(map_name: str, include_data: bool) -> dict:
    wkt_dir = WKT_DIR / map_name
    data_dir = DATA_DIR / map_name
    meta = load_map_metadata(wkt_dir)
    family = meta.get("family", "")
    source = meta.get("source", "osm")

    roads_wkt = wkt_dir / "roads.wkt"
    raw_roads = parse_linestrings(roads_wkt) if roads_wkt.is_file() else []
    sim_roads = wkt_to_sim_coords(raw_roads)
    all_pts = [p for seg in sim_roads for p in seg]
    notes: list[str] = []

    if all_pts:
        xs, ys = zip(*all_pts)
        bbox = (min(xs), min(ys), max(xs), max(ys))
    else:
        bbox = (0, 0, 0, 0)
        notes.append("missing roads.wkt")

    wx, wy = world_size_from_metadata(meta)
    bus_files = list_route_wkt_files(wkt_dir)
    poi_files = list_poi_wkt_files(wkt_dir)

    if include_data and data_dir.is_dir():
        for bf in bus_files:
            dw = data_dir / bf.name
            if dw.is_file() and file_md5(bf) != file_md5(dw):
                notes.append(f"wkt/data mismatch {bf.name}")

    status = "PASS" if roads_wkt.is_file() and all_pts else "FAIL"
    if notes and status == "PASS":
        status = "NOTES"

    return {
        "map_name": map_name,
        "family": family,
        "map_source": source,
        "roads_file": f"scenarios/maps/wkt/{map_name}/roads.wkt" if roads_wkt.is_file() else "",
        "n_road_lines": len(raw_roads),
        "n_road_vertices": sum(len(s) for s in raw_roads),
        "road_bbox_min_x": round(bbox[0], 1),
        "road_bbox_min_y": round(bbox[1], 1),
        "road_bbox_max_x": round(bbox[2], 1),
        "road_bbox_max_y": round(bbox[3], 1),
        "world_size_x": int(wx),
        "world_size_y": int(wy),
        "bus_route_files": ";".join(p.name for p in bus_files),
        "n_bus_routes": len(bus_files),
        "poi_files": ";".join(p.name for p in poi_files),
        "n_homes": len(parse_points(wkt_dir / "A_homes.wkt")),
        "n_offices": len(parse_points(wkt_dir / "A_offices.wkt")),
        "n_meetingspots": len(parse_points(wkt_dir / "A_meetingspots.wkt")),
        "status": status,
        "notes": "; ".join(notes),
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-data", action="store_true")
    ap.add_argument("--output", type=str, default=str(ANALYSIS_DATA / "map_assets_inventory.csv"))
    args = ap.parse_args()

    rows = [inventory_row(n, args.include_data) for n in ACTIVE_MAPS]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out} ({len(rows)} maps)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())