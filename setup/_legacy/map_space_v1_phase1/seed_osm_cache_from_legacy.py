#!/usr/bin/env python3
"""Seed OSM GraphML cache from legacy scenarios/maps/raw for offline generation."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from generate_map_space_v1 import DEFAULT_YAML, OUTPUT_ROOT, iter_osm_candidates, load_design_space  # noqa: E402

LEGACY_RAW = _SETUP.parent / "maps" / "raw"

ARCHETYPE_LEGACY_GRAPHML: dict[str, str] = {
    "dense_urban_irregular": "HelsinkiDowntown.graphml",
    "urban_grid": "ManhattanMidtownGrid.graphml",
    "campus_compact": "KumpulaCampus.graphml",
    "suburban_low_density": "HelsinkiDowntown.graphml",
    "rural_roads": "NuuksioSparseTrails.graphml",
    "sparse_trails": "NuuksioSparseTrails.graphml",
    "corridor_linear": "ManhattanMidtownGrid.graphml",
    "industrial_disrupted": "HelsinkiDisrupted.graphml",
    "island_or_partitioned": "NuuksioSparseTrails.graphml",
    "compact_residential": "KallioCommunityCompact.graphml",
}


def seed_caches(output_root: Path, yaml_path: Path, seed: int, max_maps: int) -> int:
    spec = load_design_space(yaml_path)
    raw_dir = output_root / "real_osm" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for cand in iter_osm_candidates(spec, seed):
        legacy = ARCHETYPE_LEGACY_GRAPHML.get(cand.archetype)
        if not legacy:
            continue
        src = LEGACY_RAW / legacy
        if not src.is_file():
            print(f"Missing legacy cache: {src}", file=sys.stderr)
            continue
        dst = raw_dir / f"{cand.map_id}.graphml"
        if dst.is_file():
            continue
        shutil.copy2(src, dst)
        n += 1
    return n


def main() -> None:
    p = argparse.ArgumentParser(description="Seed OSM cache from legacy maps/raw GraphML")
    p.add_argument("--output", type=Path, default=OUTPUT_ROOT)
    p.add_argument("--design-space", type=Path, default=DEFAULT_YAML)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-maps", type=int, default=600)
    args = p.parse_args()
    # OSM candidates start after 300 synthetic in full run
    osm_only = max(0, args.max_maps - 300)
    n = seed_caches(args.output.resolve(), args.design_space, args.seed, osm_only)
    print(f"Seeded {n} OSM cache files → {args.output / 'real_osm' / 'raw'}")


if __name__ == "__main__":
    main()
