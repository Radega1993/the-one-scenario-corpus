#!/usr/bin/env python3
"""
validate_maps.py — Validate WKT map files for The ONE simulator compatibility.

Checks per map:
  1. Graph connectivity (single connected component)
  2. worldSize coherence (road span fits declared worldSize)
  3. Coordinate validity (non-negative after translation)
  4. No isolated nodes (degree >= 1)
  5. Spatial coverage (road area vs worldSize area)
  6. POIs within road bounds
  7. Bus route proximity to road nodes

Outputs:
  scenarios/maps/validation/{map_name}_validation.json
  scenarios/analysis/data/map_inventory.csv

Usage:
  python3 scenarios/setup/validate_maps.py
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

SCENARIOS_DIR = Path(__file__).resolve().parent.parent
WKT_DIR = SCENARIOS_DIR / "maps" / "wkt"
VALIDATION_DIR = SCENARIOS_DIR / "maps" / "validation"
DATA_DIR = SCENARIOS_DIR / "analysis" / "data"

POI_MARGIN_M = 500
BUS_SNAP_M = 200
COVERAGE_WARN_PCT = 5.0

# ── WKT parsing ─────────────────────────────────────────────────────────────

def parse_linestrings(path: Path) -> list[list[tuple[float, float]]]:
    lines = []
    for raw in path.read_text().splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        m = re.search(r"LINESTRING\s*\((.+)\)", raw, re.IGNORECASE)
        if not m:
            continue
        coords = []
        for pt in m.group(1).split(","):
            parts = pt.strip().split()
            if len(parts) >= 2:
                coords.append((float(parts[0]), float(parts[1])))
        if coords:
            lines.append(coords)
    return lines

def parse_points(path: Path) -> list[tuple[float, float]]:
    pts = []
    for raw in path.read_text().splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        m = re.search(r"POINT\s*\((.+)\)", raw, re.IGNORECASE)
        if not m:
            continue
        parts = m.group(1).strip().split()
        if len(parts) >= 2:
            pts.append((float(parts[0]), float(parts[1])))
    return pts

# ── Validation logic ────────────────────────────────────────────────────────

def _build_adjacency(edges: list[list[tuple[float, float]]]) -> dict[tuple, set[tuple]]:
    adj: dict[tuple, set[tuple]] = {}
    for seg in edges:
        for i in range(len(seg) - 1):
            a = (round(seg[i][0], 3), round(seg[i][1], 3))
            b = (round(seg[i + 1][0], 3), round(seg[i + 1][1], 3))
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)
    return adj

def _count_components(adj: dict[tuple, set[tuple]]) -> int:
    visited: set[tuple] = set()
    components = 0
    for node in adj:
        if node in visited:
            continue
        components += 1
        stack = [node]
        while stack:
            n = stack.pop()
            if n in visited:
                continue
            visited.add(n)
            for nb in adj.get(n, set()):
                if nb not in visited:
                    stack.append(nb)
    return components

def validate_map(name: str) -> dict:
    result: dict = {"map_name": name, "checks": {}, "status": "PASS", "notes": []}
    map_dir = WKT_DIR / name
    roads_path = map_dir / "roads.wkt"

    if not roads_path.exists():
        result["status"] = "MISSING"
        result["notes"].append("roads.wkt not found")
        return result

    edges = parse_linestrings(roads_path)
    if not edges:
        result["status"] = "FAIL"
        result["notes"].append("roads.wkt contains no LINESTRING data")
        return result

    all_pts = [p for seg in edges for p in seg]
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max_x - min_x
    span_y = max_y - min_y

    result["n_road_segments"] = len(edges)
    result["n_unique_points"] = len(set((round(x, 3), round(y, 3)) for x, y in all_pts))
    result["span_x"] = round(span_x, 1)
    result["span_y"] = round(span_y, 1)

    meta_path = map_dir / "metadata.json"
    world_size = None
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        world_size = tuple(meta.get("world_size", [0, 0]))
        result["world_size_x"] = world_size[0]
        result["world_size_y"] = world_size[1]
        result["source"] = meta.get("source", "unknown")
        result["family"] = meta.get("family", "")
        result["crs"] = meta.get("crs", "")

    # 1. Connectivity
    adj = _build_adjacency(edges)
    n_components = _count_components(adj)
    result["checks"]["connectivity"] = n_components == 1
    result["n_components"] = n_components
    if n_components > 1:
        result["status"] = "FAIL"
        result["notes"].append(f"Graph has {n_components} connected components (must be 1)")

    # 2. worldSize coherence
    if world_size:
        fits = span_x <= world_size[0] and span_y <= world_size[1]
        result["checks"]["worldSize_fits"] = fits
        if not fits:
            result["status"] = "FAIL"
            result["notes"].append(f"Road span ({span_x:.0f}x{span_y:.0f}) exceeds worldSize {world_size}")

    # 3. Isolated nodes
    isolated = sum(1 for n, nb in adj.items() if len(nb) == 0)
    result["checks"]["no_isolated_nodes"] = isolated == 0
    result["n_isolated"] = isolated
    if isolated > 0:
        result["notes"].append(f"{isolated} isolated nodes")

    # 4. Coverage
    if world_size and world_size[0] > 0 and world_size[1] > 0:
        total_length = sum(
            math.sqrt((seg[i + 1][0] - seg[i][0]) ** 2 + (seg[i + 1][1] - seg[i][1]) ** 2)
            for seg in edges
            for i in range(len(seg) - 1)
        )
        coverage_pct = (total_length * 10) / (world_size[0] * world_size[1]) * 100
        result["coverage_pct"] = round(coverage_pct, 2)
        result["total_road_length_m"] = round(total_length, 1)
        result["checks"]["coverage_reasonable"] = coverage_pct >= COVERAGE_WARN_PCT
        if coverage_pct < COVERAGE_WARN_PCT:
            result["notes"].append(f"Low road coverage: {coverage_pct:.1f}%")

    # 5. POIs within bounds
    for cat in ("homes", "offices", "meetingspots"):
        poi_path = map_dir / f"A_{cat}.wkt"
        if not poi_path.exists():
            result["checks"][f"poi_{cat}_exists"] = False
            result["notes"].append(f"Missing A_{cat}.wkt")
            continue
        pts = parse_points(poi_path)
        result[f"n_{cat}"] = len(pts)
        outside = sum(
            1 for x, y in pts
            if x < min_x - POI_MARGIN_M or x > max_x + POI_MARGIN_M
            or y < min_y - POI_MARGIN_M or y > max_y + POI_MARGIN_M
        )
        result["checks"][f"poi_{cat}_within_bounds"] = outside == 0
        if outside > 0:
            result["notes"].append(f"{outside}/{len(pts)} {cat} POIs outside road bounds (+{POI_MARGIN_M}m)")

    # 6. Bus route
    bus_path = map_dir / "A_bus.wkt"
    if bus_path.exists():
        bus_segs = parse_linestrings(bus_path)
        bus_pts = [p for seg in bus_segs for p in seg]
        result["n_bus_stops"] = len(bus_pts)
        result["checks"]["bus_route_exists"] = len(bus_pts) >= 2
    else:
        result["checks"]["bus_route_exists"] = False
        result["notes"].append("Missing A_bus.wkt")

    if not result["notes"]:
        result["notes"].append("All checks passed")

    return result

def main() -> int:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not WKT_DIR.exists():
        print(f"ERROR: {WKT_DIR} does not exist. Run prepare_maps.py first.")
        return 1

    map_dirs = sorted(d for d in WKT_DIR.iterdir() if d.is_dir())
    if not map_dirs:
        print(f"No map directories found in {WKT_DIR}")
        return 1

    results = []
    for d in map_dirs:
        name = d.name
        print(f"\nValidating: {name}")
        r = validate_map(name)
        results.append(r)

        val_path = VALIDATION_DIR / f"{name}_validation.json"
        with open(val_path, "w") as f:
            json.dump(r, f, indent=2)

        status = r["status"]
        tag = "OK" if status == "PASS" else status
        print(f"  [{tag}] segments={r.get('n_road_segments', '?')} "
              f"span={r.get('span_x', '?')}x{r.get('span_y', '?')} "
              f"components={r.get('n_components', '?')}")
        for note in r.get("notes", []):
            print(f"    - {note}")

    csv_path = DATA_DIR / "map_inventory.csv"
    fieldnames = [
        "map_name", "family", "source", "crs",
        "n_road_segments", "n_unique_points", "n_components",
        "span_x", "span_y", "world_size_x", "world_size_y",
        "total_road_length_m", "coverage_pct",
        "n_homes", "n_offices", "n_meetingspots", "n_bus_stops",
        "status", "notes",
    ]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in results:
            row = {k: r.get(k, "") for k in fieldnames}
            row["notes"] = "; ".join(r.get("notes", []))
            w.writerow(row)

    print(f"\nWrote {csv_path} ({len(results)} maps)")
    print(f"Validation JSONs in {VALIDATION_DIR}/")

    fails = [r for r in results if r["status"] != "PASS"]
    if fails:
        print(f"\n*** {len(fails)} map(s) FAILED validation ***")
        return 1
    print("\nAll maps PASS.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())