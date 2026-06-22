#!/usr/bin/env python3
"""Export anchor inventory from YAML and cross-reference with valid maps."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_DIR = REPO_ROOT / "scenarios"

DEFAULT_YAML = SCENARIOS_DIR / "analysis" / "config" / "map_design_space_saturation_v1.yaml"
DEFAULT_FEATURES = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_features.csv"
DEFAULT_CSV = SCENARIOS_DIR / "analysis" / "data" / "map_anchor_inventory_v1.csv"
DEFAULT_REPORT = SCENARIOS_DIR / "analysis" / "reports" / "map_anchor_inventory_v1.md"

OSM_TYPES = {"osm_bbox", "osm_place"}
TRACE_TYPES = {"trace_reference_not_map"}


def load_anchors(yaml_path: Path) -> list[dict]:
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    root = data.get("map_design_space_saturation_v1", data)
    return list(root["real_anchors"]["anchors"])


def anchor_flags(anchor_type: str, bbox: dict | None, place_name: str | None) -> dict[str, bool]:
    at = anchor_type or ""
    return {
        "is_osm_downloadable": at in OSM_TYPES,
        "is_trace_only": at in TRACE_TYPES,
        "has_bbox": bbox is not None and bool(bbox),
        "has_place": bool(place_name and str(place_name).strip() and str(place_name).lower() != "null"),
    }


def count_maps_by_anchor(features_path: Path) -> dict[str, int]:
    if not features_path.is_file():
        return {}
    counts: Counter[str] = Counter()
    with features_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            aid = (row.get("anchor_id") or "").strip()
            if aid:
                counts[aid] += 1
    return dict(counts)


def build_rows(anchors: list[dict], map_counts: dict[str, int]) -> list[dict]:
    rows: list[dict] = []
    for a in anchors:
        flags = anchor_flags(a.get("anchor_type"), a.get("bbox"), a.get("place_name"))
        aid = a["anchor_id"]
        n_maps = map_counts.get(aid, 0)
        expected_use = a.get("expected_use") or []
        if isinstance(expected_use, list):
            expected_use_str = ";".join(str(x) for x in expected_use)
        else:
            expected_use_str = str(expected_use)
        rows.append({
            "anchor_id": aid,
            "label": a.get("label", ""),
            "anchor_type": a.get("anchor_type", ""),
            "archetype": a.get("archetype", ""),
            "source_context": (a.get("source_context") or "").replace("\n", " ").strip(),
            "dataset_basis": (a.get("dataset_basis") or "").replace("\n", " ").strip(),
            "is_osm_downloadable": flags["is_osm_downloadable"],
            "is_trace_only": flags["is_trace_only"],
            "has_bbox": flags["has_bbox"],
            "has_place": flags["has_place"],
            "expected_use": expected_use_str,
            "n_valid_maps": n_maps,
            "has_valid_map": n_maps > 0,
        })
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "anchor_id", "label", "anchor_type", "archetype", "source_context", "dataset_basis",
        "is_osm_downloadable", "is_trace_only", "has_bbox", "has_place", "expected_use",
        "n_valid_maps", "has_valid_map",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_report(path: Path, rows: list[dict], features_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    n_total = len(rows)
    n_osm = sum(1 for r in rows if r["is_osm_downloadable"] == "True" or r["is_osm_downloadable"] is True)
    n_trace = sum(1 for r in rows if r["is_trace_only"] == "True" or r["is_trace_only"] is True)
    n_with_maps = sum(1 for r in rows if r["has_valid_map"] == "True" or r["has_valid_map"] is True)

    synth_no_anchor = 0
    if features_path.is_file():
        with features_path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if not (row.get("anchor_id") or "").strip():
                    synth_no_anchor += 1

    table = "\n".join(
        f"| {r['anchor_id']} | {r['anchor_type']} | {r['archetype']} | "
        f"{'yes' if r['is_osm_downloadable'] in (True, 'True') else 'no'} | "
        f"{'yes' if r['is_trace_only'] in (True, 'True') else 'no'} | {r['n_valid_maps']} |"
        for r in rows
    )

    body = f"""# Map anchor inventory (v1)

Generated: {ts}

Source: `map_design_space_saturation_v1.yaml` (`real_anchors.anchors`)

## Summary

| Metric | Count |
|--------|-------|
| Declared anchors in YAML | **{n_total}** |
| OSM-downloadable (`osm_bbox` / `osm_place`) | **{n_osm}** |
| Trace-only (`trace_reference_not_map`) | **{n_trace}** |
| Anchors with ≥1 valid map (features CSV) | **{n_with_maps}** |
| Valid maps without geographic anchor_id | **{synth_no_anchor}** |

## Full inventory

| anchor_id | anchor_type | archetype | OSM | trace-only | n_valid_maps |
|-----------|-------------|-----------|-----|------------|--------------|
{table}

## Notes

- Trace-only anchors parametrize `trace_reference_synthetic` maps; they are **not** downloadable OSM geometries.
- `n_valid_maps` counts rows in `{features_path.name}` with matching `anchor_id`.
- Canonical declared total: **{n_total}** (not 20).

## Output

- `map_anchor_inventory_v1.csv`
"""
    path.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yaml", type=Path, default=DEFAULT_YAML)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    anchors = load_anchors(args.yaml)
    map_counts = count_maps_by_anchor(args.features)
    rows = build_rows(anchors, map_counts)
    write_csv(args.output_csv, rows)
    write_report(args.report, rows, args.features)
    print(f"Wrote {args.output_csv} ({len(rows)} anchors)")
    print(f"Wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
