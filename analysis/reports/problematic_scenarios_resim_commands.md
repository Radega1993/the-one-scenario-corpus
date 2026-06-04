# Re-simulation commands — repaired mobility scenarios

Re-run **48** environmental scenarios (4 bases × 12 traffic profiles) after map-aware mobility repair.

## Full repair batch (recommended)

```bash
cd /path/to/the-one

python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 \
  --name-regex '(S1_StrongCommunities_LimitedMixing|S6_FamilyGroups_LocalRoutines|D1_ShelterHotspots_EmergencyMobility|R2_VillagesTrails_InterVillage)__TP' \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt \
  --jobs 2 \
  --timeout 21600
```

## By family

```bash
# Social (S1 + S6) — 24 scenarios
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --family 06_social \
  --name-regex '(S1_StrongCommunities_LimitedMixing|S6_FamilyGroups_LocalRoutines)__TP' \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt \
  --jobs 2 --timeout 21600

# Disaster (D1) — 12 scenarios
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --family 05_disaster \
  --scenario-base D1_ShelterHotspots_EmergencyMobility \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt \
  --jobs 2 --timeout 21600

# Rural (R2) — 12 scenarios
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --family 04_rural \
  --scenario-base R2_VillagesTrails_InterVillage \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt \
  --jobs 2 --timeout 21600
```

## Smoke test (single scenario)

```bash
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 \
  --settings scenarios/corpus_v1/06_social/S1_StrongCommunities_LimitedMixing__TP01_Baseline.settings \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt \
  --timeout 21600
```

## Post-simulation analysis

```bash
scenarios/analysis/.venv/bin/python scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py \
  --reports-dir reports --corpus corpus_v1 \
  --name-regex '(S1_StrongCommunities_LimitedMixing|S6_FamilyGroups_LocalRoutines|D1_ShelterHotspots_EmergencyMobility|R2_VillagesTrails_InterVillage)' \
  --zoom-mode roads

scenarios/analysis/.venv/bin/python scenarios/analysis/run_analysis.py \
  --corpus corpus_v1 --phase output_metrics

scenarios/analysis/.venv/bin/python scenarios/analysis/run_analysis.py \
  --corpus corpus_v1 --phase features
```

Legacy reports under `reports/` with old scenario names are retained; new runs use the new `Scenario.name` stems.