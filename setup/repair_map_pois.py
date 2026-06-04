#!/usr/bin/env python3
"""Repair POI WKT files for a single map (snap to road graph, urban thresholds)."""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import (  # noqa: E402
    DATA_DIR,
    SCENARIOS_DIR,
    WKT_DIR,
    SimTransform,
    load_road_graph,
    parse_linestrings,
    parse_points,
    transform_points,
    vertex_distances,
    world_size_from_metadata,
)

MAP_DATA = SCENARIOS_DIR / "analysis" / "data" / "maps"
REPORTS = SCENARIOS_DIR / "analysis" / "reports" / "maps"

POI_FILES = (
    ("A_homes.wkt", "homes"),
    ("A_offices.wkt", "offices"),
    ("A_meetingspots.wkt", "meetingspots"),
)

DEFAULT_OK_M = 30.0
DEFAULT_WARN_M = 75.0
BORDER_EPS = 2.0

def write_points_wkt(raw_points: list[tuple[float, float]], path: Path) -> None:
    def fmt(v: float) -> str:
        return f"{v:.6f}"

    with path.open("w", encoding="utf-8") as f:
        for x, y in raw_points:
            f.write(f"POINT ({fmt(x)} {fmt(y)})\n\n")

def classify_dist(
    d: float,
    inside_ws: bool,
    on_border: bool,
    *,
    ok_m: float = DEFAULT_OK_M,
    warn_m: float = DEFAULT_WARN_M,
) -> str:
    if not inside_ws or on_border:
        return "FIX_REQUIRED"
    if d <= ok_m:
        return "OK"
    if d <= warn_m:
        return "WARNING"
    return "FIX_REQUIRED"

def needs_fix(status: str) -> bool:
    return status == "FIX_REQUIRED"

def fix_sim_point(
    x: float,
    y: float,
    wx: float,
    wy: float,
    rg,
) -> tuple[float, float, str]:
    reason_parts: list[str] = []
    nx, ny = x, y
    if wx > 0 and wy > 0:
        if x < 0 or y < 0 or x > wx or y > wy:
            reason_parts.append("outside_worldSize")
            nx = min(max(x, BORDER_EPS), wx - BORDER_EPS)
            ny = min(max(y, BORDER_EPS), wy - BORDER_EPS)
        elif x <= BORDER_EPS or y <= BORDER_EPS:
            reason_parts.append("border_artifact")
            nx = max(x, BORDER_EPS)
            ny = max(y, BORDER_EPS)
    snapped = rg.snap_to_nearest_node(nx, ny)
    if snapped != (nx, ny):
        reason_parts.append("snap_to_road_node")
    return snapped, "; ".join(reason_parts) if reason_parts else "snap_to_road_node"

def audit_and_repair_map(
    map_name: str,
    *,
    apply: bool,
    install: bool,
    output_prefix: str | None = None,
    ok_m: float = DEFAULT_OK_M,
    warn_m: float = DEFAULT_WARN_M,
) -> tuple[list[dict], list[dict], list[str]]:
    prefix = output_prefix or map_name
    rg, roads_path, meta = load_road_graph(map_name)
    raw_roads = parse_linestrings(roads_path)
    tf = SimTransform.from_raw_lines(raw_roads)
    wx, wy = world_size_from_metadata(meta)
    map_dir = WKT_DIR / map_name

    validation_rows: list[dict] = []
    correction_rows: list[dict] = []
    modified_files: list[str] = []

    for fname, poi_type in POI_FILES:
        poi_path = map_dir / fname
        if not poi_path.is_file():
            continue
        raw_pts = parse_points(poi_path)
        sim_pts = transform_points(raw_pts)
        new_raw: list[tuple[float, float]] = []
        file_changed = False

        for i, ((rx, ry), (sx, sy)) in enumerate(zip(raw_pts, sim_pts)):
            dists = vertex_distances(rg, [(sx, sy)])
            d = dists[0] if dists else 0.0
            inside = (0 <= sx <= wx and 0 <= sy <= wy) if wx and wy else True
            on_border = wx > 0 and (sx <= BORDER_EPS or sy <= BORDER_EPS)
            status = classify_dist(d, inside, on_border, ok_m=ok_m, warn_m=warn_m)

            validation_rows.append(
                {
                    "map_name": map_name,
                    "poi_file": fname,
                    "poi_type": poi_type,
                    "point_index": i,
                    "raw_x": round(rx, 3),
                    "raw_y": round(ry, 3),
                    "sim_x": round(sx, 3),
                    "sim_y": round(sy, 3),
                    "inside_world_size": inside,
                    "dist_to_road_m": round(d, 2),
                    "dist_to_nearest_node_m": round(d, 2),
                    "status": status,
                    "action": "none",
                }
            )

            out_rx, out_ry = rx, ry
            if needs_fix(status):
                fixed_sim, reason = fix_sim_point(sx, sy, wx, wy, rg)
                out_rx, out_ry = tf.sim_to_raw(fixed_sim[0], fixed_sim[1])
                new_d = vertex_distances(rg, [fixed_sim])[0]
                validation_rows[-1]["action"] = "corrected" if apply else "would_correct"
                if apply:
                    correction_rows.append(
                        {
                            "map_name": map_name,
                            "poi_file": fname,
                            "point_index": i,
                            "old_raw_x": round(rx, 3),
                            "old_raw_y": round(ry, 3),
                            "new_raw_x": round(out_rx, 3),
                            "new_raw_y": round(out_ry, 3),
                            "old_dist_m": round(d, 2),
                            "new_dist_m": round(new_d, 2),
                            "reason": reason,
                        }
                    )
                    file_changed = True
            new_raw.append((out_rx, out_ry))

        if apply and file_changed:
            write_points_wkt(new_raw, poi_path)
            modified_files.append(str(poi_path.relative_to(SCENARIOS_DIR.parent)))

    if apply and install and modified_files:
        dst = DATA_DIR / map_name
        dst.mkdir(parents=True, exist_ok=True)
        for fname, _ in POI_FILES:
            src = map_dir / fname
            if src.is_file():
                shutil.copy2(src, dst / fname)

    return validation_rows, correction_rows, modified_files

def write_poi_report(
    map_name: str,
    validation_rows: list[dict],
    correction_rows: list[dict],
    path: Path,
    *,
    ok_m: float = DEFAULT_OK_M,
    warn_m: float = DEFAULT_WARN_M,
    threshold_label: str = "urban",
) -> None:
    n = len(validation_rows)
    n_ok = sum(1 for r in validation_rows if r["status"] == "OK")
    n_warn = sum(1 for r in validation_rows if r["status"] == "WARNING")
    n_fix = sum(1 for r in validation_rows if r["status"] == "FIX_REQUIRED")
    lines = [
        f"# {map_name} — POI report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Summary",
        "",
        f"- Points reviewed: {n}",
        f"- OK (≤{ok_m} m): {n_ok}",
        f"- WARNING ({ok_m}–{warn_m} m): {n_warn}",
        f"- Required fix (>{warn_m} m or outside WS): {n_fix}",
        f"- Corrections applied: {len(correction_rows)}",
        "",
        f"## Thresholds ({threshold_label})",
        "",
        f"- ≤{ok_m} m: OK",
        f"- {ok_m}–{warn_m} m: WARNING (documented, not auto-corrected)",
        f"- >{warn_m} m or outside worldSize: snap to nearest road node",
        "",
    ]
    if correction_rows:
        lines.extend(["## Corrections", ""])
        for r in correction_rows[:30]:
            lines.append(
                f"- `{r['poi_file']}` point {r['point_index']}: "
                f"({r['old_raw_x']},{r['old_raw_y']}) → ({r['new_raw_x']},{r['new_raw_y']}) "
                f"[{r['reason']}]"
            )
        if len(correction_rows) > 30:
            lines.append(f"- … and {len(correction_rows) - 30} more")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", default="HelsinkiDowntown")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--ok-m", type=float, default=DEFAULT_OK_M)
    ap.add_argument("--warn-m", type=float, default=DEFAULT_WARN_M)
    args = ap.parse_args()

    if not args.dry_run and not args.apply:
        print("Use --dry-run or --apply")
        return 1

    apply = args.apply
    if apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = WKT_DIR / f"_backup_{args.map.lower()}_poi_{stamp}"
        src = WKT_DIR / args.map
        if src.is_dir():
            shutil.copytree(src, backup / args.map, dirs_exist_ok=True)
            print(f"Backup -> {backup}")

    val, corr, modified = audit_and_repair_map(
        args.map,
        apply=apply,
        install=args.install and apply,
        ok_m=args.ok_m,
        warn_m=args.warn_m,
    )

    MAP_DATA.mkdir(parents=True, exist_ok=True)
    prefix = args.map
    val_csv = MAP_DATA / f"{prefix}_poi_validation.csv"
    corr_csv = MAP_DATA / f"{prefix}_poi_corrections.csv"
    if val:
        with val_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(val[0].keys()))
            w.writeheader()
            w.writerows(val)
    if corr:
        with corr_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(corr[0].keys()))
            w.writeheader()
            w.writerows(corr)
    label = "campus" if args.ok_m <= 25 else "urban"
    write_poi_report(
        args.map,
        val,
        corr,
        REPORTS / f"{prefix}_poi_report.md",
        ok_m=args.ok_m,
        warn_m=args.warn_m,
        threshold_label=label,
    )
    print(f"Wrote {val_csv} ({len(val)} points)")
    print(f"Corrections: {len(corr)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())