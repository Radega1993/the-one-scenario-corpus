#!/usr/bin/env bash
# Run 6 pilot simulations after worldSize calibration (one TP01 per map).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PILOT_RE='U1_CBD_Commuting_HelsinkiDowntown__TP01_Baseline|C1_Campus_ClassChange__TP01_Baseline|V1_TaxiLow_ManhattanMidtownGridMidtownGrid__TP01_Baseline|R1_Rural_SparseSPMM__TP01_Baseline|D1_ShelterHotspots_EmergencyMobility__TP01_Baseline|S2_WeakCommunities_HighMixing__TP01_Baseline'
EXTRA=scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt
venv/bin/python scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
  --name-regex "$PILOT_RE" \
  --extra-settings "$EXTRA" \
  --jobs 2
