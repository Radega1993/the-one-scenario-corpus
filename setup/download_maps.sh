#!/usr/bin/env bash
# download_maps.sh — Download OSM road networks and POI data for benchmark maps.
#
# Usage:
#   bash scenarios/setup/download_maps.sh [--force]
#
# Requires: python3 with osmnx, geopandas, shapely installed
#   pip install -r scenarios/setup/requirements_maps.txt
#
# Outputs are stored under scenarios/maps/raw/ (GraphML + GeoJSON).
# Idempotent: skips maps whose raw files already exist unless --force.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCENARIOS_DIR="$(dirname "$SCRIPT_DIR")"
RAW_DIR="$SCENARIOS_DIR/maps/raw"

FORCE=false
[[ "${1:-}" == "--force" ]] && FORCE=true

mkdir -p "$RAW_DIR"

echo "=== Map download pipeline ==="
echo "Output: $RAW_DIR"
echo "Force re-download: $FORCE"
echo

python3 - "$RAW_DIR" "$FORCE" <<'PYEOF'
"""Download OSM data for each map defined in map_config."""
import json
import sys
from pathlib import Path

raw_dir = Path(sys.argv[1])
force = sys.argv[2].lower() == "true"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "setup"))
# Inline the config to avoid import issues when running via heredoc
MAP_DEFS = {
    "HelsinkiDowntown": {
        "bbox": (60.165, 60.178, 24.925, 24.955),
        "crs": "EPSG:3067", "network_type": "drive",
    },
    "KumpulaCampus": {
        "bbox": (60.2025, 60.2115, 24.958, 24.978),
        "crs": "EPSG:3067", "network_type": "all",
    },
    "ManhattanMidtownGrid": {
        "bbox": (40.748, 40.766, -73.993, -73.968),
        "crs": "EPSG:32618", "network_type": "drive",
    },
    "NuuksioSparseTrails": {
        "bbox": (60.310, 60.335, 24.490, 24.535),
        "crs": "EPSG:3067", "network_type": "all",
    },
    "HelsinkiDisrupted": {
        "bbox": (60.180, 60.196, 24.965, 24.995),
        "crs": "EPSG:3067", "network_type": "all",
    },
    "KallioCommunityCompact": {
        "bbox": (60.179, 60.189, 24.938, 24.957),
        "crs": "EPSG:3067", "network_type": "all",
    },
}

try:
    import osmnx as ox
    import geopandas as gpd
except ImportError:
    print("ERROR: osmnx / geopandas not installed. Run:")
    print("  pip install -r scenarios/setup/requirements_maps.txt")
    sys.exit(1)

ox.settings.log_console = False
ox.settings.use_cache = True

for name, cfg in MAP_DEFS.items():
    if cfg.get("synthetic"):
        print(f"[SKIP] {name} — synthetic (generated in prepare_maps.py)")
        continue

    graphml = raw_dir / f"{name}.graphml"
    pois_json = raw_dir / f"{name}_pois.geojson"

    if graphml.exists() and pois_json.exists() and not force:
        print(f"[CACHED] {name}")
        continue

    south, north, west, east = cfg["bbox"]
    ntype = cfg.get("network_type", "drive")
    print(f"[DOWNLOAD] {name}  bbox=({south},{north},{west},{east})  type={ntype}")

    # osmnx v2 bbox: (west, south, east, north)
    G = ox.graph_from_bbox(bbox=(west, south, east, north), network_type=ntype)
    ox.save_graphml(G, filepath=str(graphml))
    print(f"  -> {graphml.name}  nodes={len(G.nodes)} edges={len(G.edges)}")

    tags_map = {
        "homes": {"building": ["residential", "apartments", "house"]},
        "offices": {"building": ["commercial", "office", "industrial"]},
        "meetingspots": {"amenity": ["cafe", "restaurant", "bar", "pub", "library"]},
    }
    pois_all = {}
    for cat, tags in tags_map.items():
        try:
            gdf = ox.features_from_bbox(bbox=(west, south, east, north), tags=tags)
            centroids = gdf.geometry.centroid
            pois_all[cat] = [{"x": p.x, "y": p.y} for p in centroids if p and not p.is_empty]
            print(f"  POI {cat}: {len(pois_all[cat])} features")
        except Exception as exc:
            print(f"  POI {cat}: failed ({exc}), will generate random fallback")
            pois_all[cat] = []

    with open(pois_json, "w") as f:
        json.dump(pois_all, f, indent=2)

print("\nDownload complete.")
PYEOF

echo "Done."
