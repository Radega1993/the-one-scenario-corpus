#!/usr/bin/env python3
"""Recompute world_size in map metadata from sim-aligned roads.wkt bbox + margin."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_config import MAP_DEFS, WORLD_SIZE_MARGIN_M  # noqa: E402
from map_geometry import (  # noqa: E402
    ACTIVE_MAPS,
    WKT_DIR,
    load_map_metadata,
    world_size_from_sim_roads,
)

def crop_map(name: str, margin_m: float, apply: bool) -> dict:
    map_dir = WKT_DIR / name
    roads = map_dir / "roads.wkt"
    if not roads.is_file():
        raise FileNotFoundError(roads)

    meta = load_map_metadata(map_dir)
    old_ws = tuple(meta.get("world_size", [0, 0]))
    new_ws = world_size_from_sim_roads(roads, margin_m)

    row = {
        "map": name,
        "old_world_size": old_ws,
        "new_world_size": new_ws,
        "margin_m": margin_m,
    }

    if apply:
        meta["world_size"] = list(new_ws)
        meta["world_size_policy"] = f"sim_road_max_plus_{int(margin_m)}m_margin_per_axis"
        (map_dir / "metadata.json").write_text(
            json.dumps(meta, indent=2) + "\n",
            encoding="utf-8",
        )
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--margin",
        type=float,
        default=WORLD_SIZE_MARGIN_M,
        help=f"Metres per side (default {WORLD_SIZE_MARGIN_M})",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Write metadata.json (default: dry-run table only)",
    )
    ap.add_argument("--maps", default="", help="Comma-separated map names (default: all active)")
    args = ap.parse_args()

    names = [m.strip() for m in args.maps.split(",") if m.strip()] or list(ACTIVE_MAPS)
    unknown = [n for n in names if n not in MAP_DEFS]
    if unknown:
        print(f"Unknown maps: {unknown}")
        return 1

    print(f"{'map':<24} {'old':>12} {'new':>12} {'delta_x':>8} {'delta_y':>8}")
    for name in names:
        row = crop_map(name, args.margin, args.apply)
        ox, oy = row["old_world_size"][:2]
        nx, ny = row["new_world_size"]
        print(
            f"{row['map']:<24} {ox:>5}x{oy:<5} {nx:>5}x{ny:<5} "
            f"{nx - int(ox):>+8} {ny - int(oy):>+8}"
        )

    if args.apply:
        print("\nApplied metadata.json updates. Run: bash scenarios/setup/bootstrap_maps.sh --install")
    else:
        print("\n(dry-run; pass --apply to update metadata.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
