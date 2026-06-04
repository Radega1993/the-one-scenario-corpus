#!/usr/bin/env python3
"""Build semantic route inventory CSV for all active maps."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import ACTIVE_MAPS, ANALYSIS_DATA, DATA_DIR, SCENARIOS_DIR, WKT_DIR, list_route_wkt_files  # noqa: E402
from route_semantic_config import MAP_FAMILY, ROUTE_SEMANTIC_ROWS  # noqa: E402

OUT_CSV = ANALYSIS_DATA / "map_route_semantic_inventory.csv"
USAGE_CSV = ANALYSIS_DATA / "route_usage_by_scenario.csv"
REPORT_MD = SCENARIOS_DIR / "analysis" / "reports" / "maps" / "route_semantic_policy.md"

def ensure_route_usage() -> None:
    if USAGE_CSV.is_file():
        return
    subprocess.run(
        [sys.executable, str(_SETUP / "audit_route_usage.py")],
        cwd=SCENARIOS_DIR.parent,
        check=False,
    )

def load_settings_refs() -> dict[tuple[str, str], int]:
    """Count routeFile references per (map, filename)."""
    counts: dict[tuple[str, str], int] = defaultdict(int)
    if not USAGE_CSV.is_file():
        return counts
    with USAGE_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("route_file_exists", "").lower() == "false":
                continue
            rf = row.get("route_file", "")
            if not rf:
                continue
            map_name = row.get("map_name", "")
            fname = Path(rf).name
            counts[(map_name, fname)] += 1
    return counts

def action_for(map_name: str, current: str, recommended: str, refs: int) -> str:
    if current == recommended:
        return "regenerate_only" if refs else "optional_asset"
    if refs > 0:
        return "rename_and_regenerate"
    return "optional_asset"

def build_rows() -> list[dict]:
    ensure_route_usage()
    refs = load_settings_refs()
    semantic_lookup = {(m, c): (r, l) for m, c, r, l in ROUTE_SEMANTIC_ROWS}
    rows: list[dict] = []

    for map_name in ACTIVE_MAPS:
        family = MAP_FAMILY[map_name]
        wkt_dir = WKT_DIR / map_name
        data_dir = DATA_DIR / map_name
        on_disk = {p.name for p in list_route_wkt_files(wkt_dir)}
        on_disk |= {p.name for p in list_route_wkt_files(data_dir)} if data_dir.is_dir() else set()

        planned = [(c, r, l) for m, c, r, l in ROUTE_SEMANTIC_ROWS if m == map_name]
        if not planned:
            for fname in sorted(on_disk):
                rows.append(
                    {
                        "map_name": map_name,
                        "family": family,
                        "current_file": fname,
                        "recommended_file": fname,
                        "semantic_label": "unknown",
                        "on_disk": "yes",
                        "in_settings": refs.get((map_name, fname), 0),
                        "action_required": "none",
                    }
                )
            continue

        for current, recommended, label in planned:
            ref_count = refs.get((map_name, current), 0)
            if ref_count == 0 and recommended != current:
                ref_count = refs.get((map_name, recommended), 0)
            rows.append(
                {
                    "map_name": map_name,
                    "family": family,
                    "current_file": current,
                    "recommended_file": recommended,
                    "semantic_label": label,
                    "on_disk": "yes" if current in on_disk or recommended in on_disk else "no",
                    "in_settings": ref_count,
                    "action_required": action_for(map_name, current, recommended, ref_count),
                }
            )
    return rows

def write_policy_stub() -> None:
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    if REPORT_MD.is_file():
        return
    REPORT_MD.write_text(
        "# Route semantic policy\n\n"
        "Run `build_map_route_semantic_inventory.py` then edit this file, "
        "or regenerate via `regenerate_family_routes.py`.\n",
        encoding="utf-8",
    )

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-policy-stub", action="store_true")
    args = ap.parse_args()

    rows = build_rows()
    ANALYSIS_DATA.mkdir(parents=True, exist_ok=True)
    fields = [
        "map_name",
        "family",
        "current_file",
        "recommended_file",
        "semantic_label",
        "on_disk",
        "in_settings",
        "action_required",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")
    if args.write_policy_stub:
        write_policy_stub()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())