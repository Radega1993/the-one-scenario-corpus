# scenario_space_v1 Implementation: Executive Summary

## Objective Achieved ✅

Created a **systematic scenario generator** for The ONE DTN simulator, producing **3,000 candidate scenarios** from an explicit, reproducible design space. This replaces manual 6-family design with empirically-grounded parametric generation.

---

## What Was Built (Phase 1)

### 1. Code Audit (Task 1) - Complete ✅
- Analyzed 45 base scenarios + 540 corpus scenarios
- Documented 5 movement models with parameter requirements
- Identified 6 WKT maps with worldSize constraints
- Extracted 15+ validity rules
- **Deliverable**: 22 KB markdown audit report

### 2. Design Space Definition (Task 2) - Complete ✅
- 8 orthogonal dimensions (maps, models, nodes, duration, groups, network)
- All ranges empirically grounded (real-trace audit + base_scenarios)
- 14 valid map-model pairs identified (of 30 theoretically possible)
- **Deliverable**: YAML configuration file (13 KB)

### 3. Generator & Estimation (Task 3) - Complete ✅
- Python generator script: 3 modes (estimate, dry-run, generate)
- Theoretical space: 216,000 → 100,800 valid combinations (after filtering)
- Generated 3,000 candidate scenarios with random sampling
- **Deliverables**: 
  - Python script (24 KB)
  - CSV manifest (364 KB, 3000 rows)
  - Estimation reports (12 KB markdown + 1.4 KB JSON)

---

## Key Findings

### Design Space Structure
| Dimension | Count | Constraint | Coverage |
|-----------|-------|-----------|----------|
| Maps | 6 | Map-model compatibility | 100% |
| Models | 5 | Supported per map | 100% |
| Node Populations | 12 | 30–300 nodes | Empirical range ✓ |
| Durations | 5 | 2h–24h | Use-case driven ✓ |
| Group Structures | 5 | Pattern-based | Observed in base ✓ |
| Network Params | 18 | Ranges per param | Empirical ✓ |

### Candidate Pool Characteristics (3000 scenarios)
- **Uniformity**: 99% uniform across 15/18 dimensions
- **Completeness**: All 6 maps, 5 models, 12 node values represented
- **Reproducibility**: Deterministic (seed=42); same output every run
- **Validity**: All map-model pairs verified; other constraints to be checked Task 4

### Empirical Grounding
✓ Node count (30–300) aligns with DieselNet (~40), INFOCOM (~100), Cabspotting (~500 upper bound)  
✓ Duration (2h–24h) covers all research use cases  
✓ Speed ranges match pedestrian (0.5–2 m/s) and vehicular (5–15 km/h) empirical data  
✓ Density (0.06–0.36 nodes/m²) within real-trace bounds for most scenarios  

---

## Artifacts Created

| Artifact | Path | Size | Purpose |
|----------|------|------|---------|
| Code audit | `scenarios/analysis/reports/scenario_space_v1_code_audit.md` | 22 KB | Movement models, maps, constraints |
| Design space YAML | `scenarios/analysis/config/scenario_design_space_v1.yaml` | 13 KB | Parameter ranges & validity rules |
| Generator script | `scenarios/setup/generate_scenario_space_v1.py` | 24 KB | Executable generator (3 modes) |
| Candidate manifest | `scenarios/scenario_space_v1/manifest_candidates.csv` | 364 KB | 3000 parameter combinations |
| Size estimate (JSON) | `scenarios/scenario_space_v1/scenario_space_v1_size_estimate.json` | 1.4 KB | Space breakdown |
| Size estimate (MD) | `scenarios/analysis/reports/scenario_space_v1_size_estimate.md` | 12 KB | Sampling analysis |
| Phase 1 summary | `scenarios/analysis/reports/scenario_space_v1_phase1_summary.md` | 13 KB | Roadmap to Phase 2 |
| README | `scenarios/scenario_space_v1/README.md` | 5 KB | Usage guide |

**Total**: ~465 KB of new documentation + code

---

## How to Use (Phase 1 Outputs)

### Estimate design space size (no files written)
```bash
cd /home/raul/Documents/the-one
python3 scenarios/setup/generate_scenario_space_v1.py --estimate-only
```
Output: Console summary + JSON breakdown

### Preview candidates (dry-run)
```bash
python3 scenarios/setup/generate_scenario_space_v1.py --dry-run --max-settings 100 --seed 42
```
Output: Console list of first 10 scenarios (no disk writes)

### Generate full 3000-candidate pool
```bash
python3 scenarios/setup/generate_scenario_space_v1.py --generate --max-settings 3000 --sampling random --seed 42
```
Output: `scenarios/scenario_space_v1/manifest_candidates.csv`

---

## What's NOT Done Yet (Phase 2, Tasks 4-10)

| Task | Goal | Deliverable |
|------|------|-------------|
| 4 | Validate all 3000 candidates | validity_results.csv |
| 5 | Generate .settings files | 3000 .settings files in settings/subdirs |
| 6 | Extract static features | static_features.csv (3000 × 30+ cols) |
| 7 | Analyze feature space | diversity matrices, redundancy report |
| 8 | Prune to final corpus | Select 500–1000 representative scenarios |
| 9 | Apply Traffic Profiles | corpus_v2 (5000–10000 final scenarios) |
| 10 | Document & validate | Final reports, corpus_v2 manifest |

**Timeline**: ~6–9 days (sequential phases, 3–4 hours/day)

---

## Relationship to Earlier Work

### Real-Trace Audit (Phase 0, Completed)
- Inventoried 17 DTN/OppNet datasets (4 tiers: reproducible, convertible, reference, theoretical)
- Extracted empirical parameter ranges (nodes, contact duration, density, speeds)
- **Used for**: Grounding all design space values

### Base Scenarios (Reference, Frozen)
- 45 manually-curated structural bases (6 families)
- **Used for**: Validation of move models, maps, validity constraints, parameter sampling
- **Status**: NOT modified; remains frozen for historical reference

### corpus_v1 (Reference, Frozen)
- 540 scenarios (45 bases × 6 traffic profiles each)
- **Status**: NOT modified; remains frozen

---

## Key Decisions Made (Rationale)

### 1. 3000 Candidates (Not Millions)
- **Reason**: 100,800 valid combinations is tractable; 3000 (3% sample) is sufficient for:
  - Diversity-based pruning (Task 8)
  - Feature-based coverage assessment
  - Ensuring no map/model under-represented
- **Trade-off**: Not exhaustive, but statistically representative

### 2. Discrete Parameter Values (Not Continuous)
- **Reason**: Keeps candidate pool bounded; enables stratified sampling
- **Example**: 12 node values (30–300) instead of continuous range
- **Trade-off**: Less granular, but sufficient for empirical grid search

### 3. Random Sampling for Generation (Not Stratified)
- **Reason**: Stratified only generates 168 candidates (all map-model pairs); random allows 3000
- **Trade-off**: Random may oversample some combinations; mitigated by seed-based reproducibility

### 4. Validity Rules as Constraints, Not Rejections
- **Reason**: Incorporate constraints into design space definition (not in generator)
- **Example**: Map-model pairs validated at YAML level, not runtime
- **Trade-off**: Cleaner separation of concerns; eliminates ~54% of brute-force combinations upfront

### 5. EpidemicRouter Placeholder
- **Reason**: Phase 2 applies Traffic Profiles; protocol comparison is out-of-scope
- **Trade-off**: Corpus v1 is monolithic (EpidemicRouter only); corpus v2 will support multi-router

---

## Validation Against Requirements

### Original Mandate (User Specification)
- [x] Audit current code (Task 1) → Done
- [x] Define design space (Task 2) → Done
- [x] Estimate size (Task 3) → Done
- [x] Generate candidates (Task 3) → Done (3000, not millions)
- [ ] Generate .settings files (Task 5) → Deferred to Phase 2
- [ ] Extract features (Task 6) → Deferred to Phase 2
- [ ] Prune corpus (Task 8) → Deferred to Phase 2
- [ ] Apply Traffic Profiles (Task 9) → Deferred to Phase 2

### Non-Functional Requirements
- [x] **Reproducibility**: Deterministic generation (seed=42)
- [x] **No modification to existing**: corpus_v1 & base_scenarios untouched
- [x] **No Traffic Profiles in v1**: Baseline events only (placeholder)
- [x] **No long simulations**: No ONE runs yet; Task 6+ extracts static features only
- [x] **Documentation**: All choices documented; audit + design space + reports

---

## Next Phase Checklist

To begin Phase 2 (Tasks 4-10):

- [ ] Confirm manifest_candidates.csv is correct
- [ ] Verify all 6 maps, 5 models are in candidate pool
- [ ] Check that no corpus_v1 or base_scenarios were modified
- [ ] Review design space YAML for any needed adjustments
- [ ] Approve candidate pool size (3000) or request regeneration

**Then proceed to Task 4**: Implement validity constraints

---

## Open Questions for Phase 2

1. **POI file validation**: Should Task 4 create missing POI files or reject candidates?
   - Current plan: Reject (fail fast, audit required)
   - Alternative: Auto-generate random POI clusters

2. **Pruning algorithm**: k-medoids or farthest-point sampling?
   - Current plan: k-medoids (faster, deterministic)
   - Alternative: Farthest-point (exact diversity)

3. **Traffic profile count**: 6 profiles per scenario or more?
   - Current plan: 6–10 (similar to corpus_v1)
   - Alternative: 10–15 (larger final corpus)

4. **Validation scope**: Smoke-test 10% of corpus_v2 or full validation?
   - Current plan: 10% (time-efficient)
   - Alternative: 100% (comprehensive)

---

## References

### Phase 1 Outputs
- **All files in**: `scenarios/analysis/reports/scenario_space_v1_*`
- **Generator**: `scenarios/setup/generate_scenario_space_v1.py`
- **Config**: `scenarios/analysis/config/scenario_design_space_v1.yaml`
- **Candidates**: `scenarios/scenario_space_v1/manifest_candidates.csv`

### Earlier Phases
- **Real-trace audit**: `scenarios/analysis/data/real_trace_scenarios_inventory.csv`
- **Real-trace reports**: `scenarios/analysis/reports/real_trace_*`
- **Base scenarios**: `scenarios/base_scenarios/manifest.csv`
- **corpus_v1**: `scenarios/corpus_v1/manifest.csv`

---

## Conclusion

Phase 1 successfully establishes the foundation for systematic scenario generation. The explicit design space replaces ad-hoc manual design, enabling reproducible, empirically-grounded corpus construction. 

**Status**: Ready for Phase 2 (Tasks 4-10) upon approval.

**Expected Outcome (Phase 2)**: corpus_v2 with 5000–10000 final scenarios, pruned by diversity and qualified by feature coverage.

