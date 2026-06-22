# corpus_v2 — removed

This directory previously held the experimental corpus from `scenario_space_v1` Phase 2 Task 9 (750 bases × 6 TP).

**Status (2026-06-13):** All `.settings` removed. Scenario generation is consolidated in:

- `scenarios/scenario_space_v1/settings/` — structural candidates (brute force)
- `scenarios/setup/generate_scenario_space_v1.py` — generator
- `scenarios/setup/scenario_space_settings_builder.py` — `.settings` builder (reference-aligned)

Traffic Profiles are applied later to a pruned subset, not in `corpus_v2/`.

The paper benchmark remains `scenarios/corpus_v1/` (540 scenarios).
