#!/usr/bin/env bash
# bootstrap_maps.sh — One-command pipeline: download → prepare → validate → install.
#
# Usage:
#   bash scenarios/setup/bootstrap_maps.sh [--install] [--force-download]
#
# Flags:
#   --install          Copy generated WKT maps into data/ for The ONE
#   --force-download   Re-download OSM data even if cached
#
# Prerequisites:
#   pip install -r scenarios/setup/requirements_maps.txt
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INSTALL_FLAG=""
DOWNLOAD_FLAGS=""

for arg in "$@"; do
  case "$arg" in
    --install) INSTALL_FLAG="--install" ;;
    --force-download) DOWNLOAD_FLAGS="--force" ;;
    *) echo "Unknown flag: $arg"; exit 1 ;;
  esac
done

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Map Pipeline: OSM → WKT for The ONE simulator         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo

# ── Step 0: Check dependencies ──────────────────────────────────────────────
echo "Step 0: Checking Python dependencies..."
python3 -c "import osmnx, shapely, pyproj, networkx, geopandas" 2>/dev/null || {
  echo "  Missing dependencies. Installing from requirements_maps.txt..."
  pip install -r "$SCRIPT_DIR/requirements_maps.txt"
}
echo "  OK"
echo

# ── Step 1: Download ────────────────────────────────────────────────────────
echo "Step 1: Downloading OSM data..."
bash "$SCRIPT_DIR/download_maps.sh" $DOWNLOAD_FLAGS
echo

# ── Step 2: Prepare ─────────────────────────────────────────────────────────
echo "Step 2: Converting OSM → WKT..."
python3 "$SCRIPT_DIR/prepare_maps.py" $INSTALL_FLAG
echo

# ── Step 3: Validate ────────────────────────────────────────────────────────
echo "Step 3: Validating maps..."
python3 "$SCRIPT_DIR/validate_maps.py"
echo

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Pipeline complete.                                     ║"
echo "║                                                         ║"
echo "║  WKT maps:  scenarios/maps/wkt/                         ║"
echo "║  Inventory: scenarios/analysis/data/map_inventory.csv   ║"
echo "║  Reports:   scenarios/maps/validation/                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
