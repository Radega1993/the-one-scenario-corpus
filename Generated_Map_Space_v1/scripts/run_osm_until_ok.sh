#!/usr/bin/env bash
# Download remaining GMS OSM maps until FAIL_DOWNLOAD_SKIPPED is gone.
#   bash scenarios/Generated_Map_Space_v1/scripts/run_osm_until_ok.sh
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PACK_ROOT="$(cd "$SCRIPTS_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PACK_ROOT/../.." && pwd)"
PYTHON="${PYTHON:-$REPO_ROOT/venv/bin/python}"
GEN="$PACK_ROOT/scripts/generate.py"
CONFIG="$PACK_ROOT/config/map_design_space.yaml"
MANIFEST="$PACK_ROOT/manifest_maps_all.csv"
LOG="${LOG:-$PACK_ROOT/ops/logs/osm_download_loop.log}"
mkdir -p "$(dirname "$LOG")"

MAX_DOWNLOADS="${MAX_DOWNLOADS:-25}"
OSM_PAUSE="${OSM_PAUSE:-8}"
OSM_TIMEOUT="${OSM_TIMEOUT:-180}"
SEED="${SEED:-42}"
TARGET="${TARGET:-1600}"
MAX_ROUNDS="${MAX_ROUNDS:-40}"
STALL_ROUNDS="${STALL_ROUNDS:-4}"

export MANIFEST
export PYTHONPATH="${PACK_ROOT}/scripts:${REPO_ROOT}/scenarios/setup${PYTHONPATH:+:$PYTHONPATH}"

count_skip() {
  "$PYTHON" - <<'PY'
import csv, os
from pathlib import Path
rows = list(csv.DictReader(Path(os.environ["MANIFEST"]).open()))
skip = sum(1 for r in rows if r.get("generation_status") == "FAIL_DOWNLOAD_SKIPPED")
osm_ok = sum(
    1
    for r in rows
    if r.get("source_type") == "osm"
    and r.get("generation_status") in ("OK", "SKIPPED_EXISTING_OK")
)
fail_t = sum(1 for r in rows if r.get("generation_status") == "FAIL_DOWNLOAD_TRANSIENT")
fail_b = sum(1 for r in rows if r.get("generation_status") == "FAIL_BUILD_OSM")
print(f"{skip}\t{osm_ok}\t{fail_t}\t{fail_b}")
PY
}

{
  echo "=== tmp_run_osm_revised_v2_until_ok ==="
  echo "started: $(date -Is)"
  echo "max_downloads=$MAX_DOWNLOADS max_rounds=$MAX_ROUNDS stall_rounds=$STALL_ROUNDS"
  echo ""
} | tee -a "$LOG"

round=0
stall=0
prev_skip=-1

while (( round < MAX_ROUNDS )); do
  round=$((round + 1))
  read -r skip osm_ok fail_t fail_b <<< "$(count_skip)"
  echo "--- Round $round/$MAX_ROUNDS --- skip=$skip osm_ok=$osm_ok transient=$fail_t build_fail=$fail_b" | tee -a "$LOG"

  if (( skip == 0 )); then
    echo "No FAIL_DOWNLOAD_SKIPPED remaining. Done." | tee -a "$LOG"
    break
  fi

  if (( skip == prev_skip )); then
    stall=$((stall + 1))
  else
    stall=0
  fi
  prev_skip=$skip
  if (( stall >= STALL_ROUNDS )); then
    echo "Stalled ($STALL_ROUNDS rounds with no skip reduction). Stopping." | tee -a "$LOG"
    break
  fi

  echo ">> generate --source osm --max-downloads $MAX_DOWNLOADS" | tee -a "$LOG"
  "$PYTHON" "$GEN" \
    --config "$CONFIG" \
    --generate \
    --source osm \
    --target-total "$TARGET" \
    --seed "$SEED" \
    --max-downloads "$MAX_DOWNLOADS" \
    --osm-pause "$OSM_PAUSE" \
    --osm-timeout "$OSM_TIMEOUT" \
    2>&1 | tee -a "$LOG"
done

read -r skip osm_ok fail_t fail_b <<< "$(count_skip)"
echo "=== Final: skip=$skip osm_ok=$osm_ok transient=$fail_t build_fail=$fail_b ===" | tee -a "$LOG"
echo "finished: $(date -Is)" | tee -a "$LOG"
