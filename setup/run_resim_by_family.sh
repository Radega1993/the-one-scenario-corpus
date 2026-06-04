#!/usr/bin/env bash
# Re-simulate corpus_v1 per family after worldSize calibration (spatial occupancy reports).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
EXTRA=scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt
PY="${PY:-venv/bin/python}"
JOBS="${JOBS:-2}"
export PYTHONUNBUFFERED=1
for fam in 01_urban 02_campus 03_vehicles 04_rural 05_disaster 06_social; do
  echo "======== family $fam ========"
  "$PY" scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
    --family "$fam" \
    --extra-settings "$EXTRA" \
    --jobs "$JOBS" || true
done
echo "Done. Run analyze_spatial_occupancy.py per family or globally."
