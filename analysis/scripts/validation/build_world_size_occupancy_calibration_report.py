#!/usr/bin/env python3
"""Generate world_size_occupancy_calibration.md from calibration CSV + pilot metrics."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_ANALYSIS = Path(__file__).resolve().parents[2]
ANALYSIS_DIR = _ANALYSIS

CAL_CSV = ANALYSIS_DIR / "data" / "world_size_calibration.csv"
METRICS_CSV = ANALYSIS_DIR / "data" / "spatial_occupancy_metrics.csv"
PILOT_CSV = ANALYSIS_DIR / "data" / "pilot_spatial_metrics.csv"
OUT_MD = ANALYSIS_DIR / "reports" / "spatial" / "world_size_occupancy_calibration.md"

ROAD_MIN_PCT = 70.0
WORLD_ROAD_RATIO_MIN = 0.85


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--calibration-csv", type=Path, default=CAL_CSV)
    ap.add_argument("--metrics-csv", type=Path, default=METRICS_CSV)
    ap.add_argument("--pilot-csv", type=Path, default=PILOT_CSV)
    ap.add_argument("--output", type=Path, default=OUT_MD)
    args = ap.parse_args()

    if not args.calibration_csv.is_file():
        print(f"Missing {args.calibration_csv}; run calibrate_world_size_per_map.py first")
        return 1

    with args.calibration_csv.open(newline="", encoding="utf-8") as f:
        cal = list(csv.DictReader(f))
    metrics_by_pilot: dict[str, dict] = {}
    if args.pilot_csv.is_file():
        with args.pilot_csv.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = row.get("pilot_scenario") or row.get("scenario", "")
                metrics_by_pilot[key] = row
    elif args.metrics_csv.is_file():
        with args.metrics_csv.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                metrics_by_pilot[row.get("scenario", "")] = row

    lines = [
        "# World size occupancy calibration (pilot)",
        "",
        "Per-map `MovementModel.worldSize` from sim road span + `occupancy_margin_m`.",
        "Primary metric: **`coverage_road_cells_pct`**. Re-sim required before metrics match settings.",
        "",
        "## Calibration table",
        "",
        "| Map | margin (m) | worldSize | bbox/world cells | pilot scenario |",
        "|-----|------------|-----------|------------------|----------------|",
    ]
    for r in cal:
        lines.append(
            f"| {r['map_name']} | {float(r['occupancy_margin_m']):.0f} | "
            f"{int(r['world_size_x'])}×{int(r['world_size_y'])} | "
            f"{float(r['map_bbox_cell_ratio']):.3f} | `{r.get('pilot_scenario', '')}` |"
        )

    lines.extend(["", "## Pilot acceptance", ""])
    if not metrics_by_pilot:
        lines.append("_No pilot metrics — run pilot sims + analyze_pilot_spatial_metrics.py._")
    else:
        lines.extend(
            [
                "| Map | pilot | road % | world % | world≥0.85×road | mismatch | PASS |",
                "|-----|-------|--------|---------|-----------------|----------|------|",
            ]
        )
        for r in cal:
            pilot = str(r.get("pilot_scenario", ""))
            m = metrics_by_pilot.get(pilot, {})
            if m.get("status") not in ("ok", None) and not m.get("coverage_road_cells_pct"):
                note = m.get("status", "pending re-sim")
                lines.append(f"| {r['map_name']} | `{pilot}` | — | — | — | — | {note} |")
                continue
            road = float(m.get("coverage_road_cells_pct") or 0)
            world = float(m.get("coverage_world_pct") or 0)
            ratio_ok = world >= 100.0 * WORLD_ROAD_RATIO_MIN * (road / 100.0) if road else False
            road_ok = road >= ROAD_MIN_PCT
            mismatch = str(m.get("world_size_mismatch", "")).lower() in ("true", "1", "yes")
            ok = m.get("status") == "ok" and road_ok and ratio_ok and not mismatch
            lines.append(
                f"| {r['map_name']} | `{pilot}` | {road:.1f} | {world:.1f} | "
                f"{'yes' if ratio_ok else 'no'} | {'yes' if mismatch else 'no'} | "
                f"{'PASS' if ok else 'FAIL'} |"
            )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Do not compare `coverage_world_pct` from pre-calibration simulation reports.",
            "- Full corpus (540) re-sim is out of scope; scale after pilot PASS.",
        ]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
