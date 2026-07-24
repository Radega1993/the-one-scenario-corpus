#!/usr/bin/env bash
# Live progress for GMS-v1 OSM download loop (Generated_Map_Space_v1).
#
#   bash scenarios/Generated_Map_Space_v1/scripts/watch_osm_progress.sh
#   bash scenarios/Generated_Map_Space_v1/scripts/watch_osm_progress.sh --once
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PACK_ROOT="$(cd "$SCRIPTS_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PACK_ROOT/../.." && pwd)"
MANIFEST="$PACK_ROOT/manifest_maps_all.csv"
CACHE="$PACK_ROOT/osm_cache"
# Prefer ops/logs, then pack root expand log, then legacy loop log.
LOG_EXPAND_OPS="$PACK_ROOT/ops/logs/osm_expand_2000.log"
LOG_EXPAND="$PACK_ROOT/osm_expand_2000.log"
LOG_EXPAND1600_OPS="$PACK_ROOT/ops/logs/osm_expand_1600.log"
LOG_EXPAND1600="$PACK_ROOT/osm_expand_1600.log"
LOG_LEGACY_OPS="$PACK_ROOT/ops/logs/osm_download_loop.log"
LOG_LEGACY="$PACK_ROOT/osm_download_loop.log"
if [[ -f "$LOG_EXPAND_OPS" ]]; then
  LOG="$LOG_EXPAND_OPS"
  OSM_TARGET_HINT=899
elif [[ -f "$LOG_EXPAND" ]]; then
  LOG="$LOG_EXPAND"
  OSM_TARGET_HINT=899
elif [[ -f "${LOG_EXPAND1600_OPS:-}" ]]; then
  LOG="$LOG_EXPAND1600_OPS"
  OSM_TARGET_HINT=719
elif [[ -f "${LOG_EXPAND1600:-}" ]]; then
  LOG="$LOG_EXPAND1600"
  OSM_TARGET_HINT=719
elif [[ -f "$LOG_LEGACY_OPS" ]]; then
  LOG="$LOG_LEGACY_OPS"
  OSM_TARGET_HINT=539
else
  LOG="$LOG_LEGACY"
  OSM_TARGET_HINT=539
fi
PYTHON="${PYTHON:-$REPO_ROOT/venv/bin/python}"
ONCE=0
[[ "${1:-}" == "--once" ]] && ONCE=1

export MANIFEST CACHE LOG OSM_TARGET_HINT

print_status() {
  "$PYTHON" - <<'PY'
import csv
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

manifest = Path(os.environ["MANIFEST"])
cache = Path(os.environ["CACHE"])
log = Path(os.environ["LOG"])

rows = list(csv.DictReader(manifest.open())) if manifest.is_file() else []
osm = [r for r in rows if r.get("source_type") == "osm"]
c = Counter(r.get("generation_status", "") for r in osm)
ok = c.get("OK", 0) + c.get("SKIPPED_EXISTING_OK", 0)
skip = c.get("FAIL_DOWNLOAD_SKIPPED", 0)
transient = c.get("FAIL_DOWNLOAD_TRANSIENT", 0)
build = c.get("FAIL_BUILD_OSM", 0)
osm_total = len(osm)
# Progress denominator: planned OSM for current phase (expand≈719, else rows or legacy 539).
target = int(os.environ.get("OSM_TARGET_HINT", "719"))
if osm_total > target:
    target = osm_total
done_manifest = ok + build + transient  # attempted (not pending skip)
# Prefer row growth toward expansion target when skips are already 0.
pct_base = max(target, 1)
pct = 100.0 * min(osm_total, target) / pct_base
bar_w = 30
filled = int(round(bar_w * min(osm_total, target) / pct_base))
bar = "#" * filled + "-" * (bar_w - filled)

n_cache = len(list(cache.glob("*.graphml"))) if cache.is_dir() else 0

round_info = ""
if log.is_file():
    text = log.read_text(encoding="utf-8", errors="replace")
    rounds = re.findall(
        r"Round (\d+)(?:/(\d+))? ---? skip=(\d+) osm_ok=(\d+)(?: osm_total=(\d+))?",
        text,
    )
    if rounds:
        r, mx, sk, ook, ot = rounds[-1]
        mx = mx or "?"
        ot = ot or "?"
        round_info = f"round {r}/{mx} (skip={sk} osm_ok={ook} osm_total={ot})"
    if re.search(
        r"No FAIL_DOWNLOAD_SKIPPED remaining|=== Final:|=== Final skip=|OSM expansion complete|Stalled",
        text,
    ):
        round_info += " | LOOP REPORTED FINAL"

print(f"[{datetime.now().strftime('%H:%M:%S')}] OSM rows [{bar}] {osm_total}/{target} ({pct:5.1f}%)")
print(f"  OK={ok}  SKIP_REMAINING={skip}  TRANSIENT={transient}  BUILD_FAIL={build}")
print(f"  osm_cache graphml files: {n_cache}")
print(f"  log: {log.name}")
if round_info:
    print(f"  {round_info}")
print("  Note: manifest updates when each generate round finishes (~25 downloads).")
PY
}

loop_alive() {
  pgrep -f 'tmp_run_osm_revised_v2_until_ok\.sh' >/dev/null 2>&1 \
    || pgrep -f 'osm_expand_1600' >/dev/null 2>&1 \
    || pgrep -f 'generate_map_space_saturation_v1.py --config .*map_design_space_revised_v2' >/dev/null 2>&1
}

finished_in_log() {
  [[ -f "$LOG" ]] && grep -qE 'No FAIL_DOWNLOAD_SKIPPED remaining|=== Final:|=== Final skip=|OSM expansion complete|Stalled' "$LOG"
}

if (( ONCE )); then
  print_status
  if loop_alive; then echo "  loop: RUNNING"; elif finished_in_log; then echo "  loop: FINISHED"; else echo "  loop: NOT RUNNING"; fi
  if [[ -f "$LOG" ]]; then echo "  last log:"; tail -5 "$LOG" | sed 's/^/    /'; fi
  exit 0
fi

echo "Watching OSM download (Ctrl+C stops this view only)."
echo "Log file: $LOG"
echo ""

was_running=0
while true; do
  clear 2>/dev/null || printf '\n---\n'
  echo "=== Generated_Map_Space_v1 OSM download ==="
  print_status
  if loop_alive; then
    was_running=1
    echo "  loop: RUNNING"
  elif finished_in_log || (( was_running )); then
    echo "  loop: FINISHED"
    echo ""
    print_status
    echo ""
    echo "****************************************"
    echo "*  OSM DOWNLOAD LOOP DONE — continue   *"
    echo "****************************************"
    if [[ -f "$LOG" ]]; then
      echo ""
      grep -E 'Round |Final|Done\.|Stalled|OSM expansion complete' "$LOG" | tail -20
    fi
    exit 0
  else
    echo "  loop: NOT RUNNING (not started or already gone)"
  fi
  echo ""
  echo "--- last log lines ---"
  if [[ -f "$LOG" ]]; then tail -15 "$LOG"; else echo "(no log yet)"; fi
  sleep 20
done
