# scenario_space_v1: Phase 1 Complete (Tasks 1-3)

**Milestone**: Explicit design space defined; candidate pool generated; ready for .settings generation

**Date**: 2026-06-13  
**Status**: ✅ Tasks 1-3 COMPLETE | ⏳ Tasks 4-10 PENDING  
**Target**: 3000 candidate scenarios for diversity-based pruning before Traffic Profiles

---

## Phase 1 Deliverables (Tasks 1-3)

### Task 1: Code Audit ✅
**Deliverable**: `scenarios/analysis/reports/scenario_space_v1_code_audit.md` (22 KB)

**Key Findings**:
- 5 movement models identified (SPMBM, WDM, MRM, BM, CM)
- 6 WKT maps with fixed worldSize constraints
- 45 base scenarios analyzed; all syntactically valid
- Parameter ranges extracted and documented
- 15+ validity constraints identified
- Map-model compatibility matrix defined

**Impact**: Enables systematic parametrization without manual intervention

---

### Task 2: Design Space Definition ✅
**Deliverable**: `scenarios/analysis/config/scenario_design_space_v1.yaml` (13 KB)

**Dimensions**:
- 8 orthogonal dimensions
- 14 valid map-model pairs (of 30 possible)
- All ranges empirically grounded or base-scenarios derived
- Validity rules expressed as YAML constraints

**Impact**: Enables reproducible, parameter-driven generation

---

### Task 3: Size Estimation & Generation ✅

**3a. Space Estimation**:
- Deliverable: `scenarios/scenario_space_v1/scenario_space_v1_size_estimate.json`
- Theoretical size: 100,800 valid combinations (after map-model filtering)
- Brute-force: 216,000 (54% invalid due to constraints)
- Breakdown by map and model provided

**3b. Generator Script**:
- Deliverable: `scenarios/setup/generate_scenario_space_v1.py` (24 KB)
- Three modes: `--estimate-only`, `--dry-run`, `--generate`
- Supports multiple sampling strategies: stratified, random, full
- Deterministic (seed-based) for reproducibility

**3c. Candidate Pool Generation**:
- Deliverable: `scenarios/scenario_space_v1/manifest_candidates.csv` (364 KB)
- 3,000 candidates generated with seed=42, random sampling
- Includes: candidate_id, param_id, map, model, n_hosts, duration, group_structure, network params, rng_seed
- All 6 maps, 5 models, 12 node populations, 5 durations covered
- Near-uniform distribution across all dimensions

**3d. Reports**:
- **Deliverable**: `scenarios/analysis/reports/scenario_space_v1_size_estimate.md` (12 KB)
  - Executive summary of space size
  - Breakdown by map and model
  - Sampling strategy justification
  - Coverage assessment against real-trace audit
  - Feature distribution statistics

- **Deliverable**: `scenarios/scenario_space_v1/README.md` (5 KB)
  - Usage guide for generator
  - Quick-start commands
  - Design space overview
  - Next steps for Phase 2

**Impact**: 3,000 candidate parameter combinations ready for .settings generation and feature extraction

---

## State of Artifacts

| Artifact | Status | Path | Size | Purpose |
|----------|--------|------|------|---------|
| Code audit | ✅ | `scenarios/analysis/reports/scenario_space_v1_code_audit.md` | 22 KB | Document movement models, maps, constraints |
| Design space YAML | ✅ | `scenarios/analysis/config/scenario_design_space_v1.yaml` | 13 KB | Define discrete parameter ranges |
| Generator script | ✅ | `scenarios/setup/generate_scenario_space_v1.py` | 24 KB | Executable candidate generator |
| Size estimate (JSON) | ✅ | `scenarios/scenario_space_v1/scenario_space_v1_size_estimate.json` | 1.4 KB | Theoretical space breakdown |
| Candidate manifest | ✅ | `scenarios/scenario_space_v1/manifest_candidates.csv` | 364 KB | 3000 parameter combinations |
| Space report (MD) | ✅ | `scenarios/analysis/reports/scenario_space_v1_size_estimate.md` | 12 KB | Sampling analysis & justification |
| README | ✅ | `scenarios/scenario_space_v1/README.md` | 5 KB | Usage guide & architecture |
| Base scenarios | 📌 | `scenarios/base_scenarios/` | - | 45 structural bases (frozen) |
| corpus_v1 | 📌 | `scenarios/corpus_v1/` | - | 540 corpus scenarios (frozen) |

**Legend**: ✅ = Created (Phase 1) | 📌 = Frozen (reference only) | ⏳ = Next phase

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Design space (brute-force) | 216,000 combinations |
| Design space (valid, filtered) | 100,800 combinations |
| Candidate pool size | 3,000 (3% sample) |
| Maps | 6/6 (100%) |
| Movement models | 5/5 (100%) |
| Node populations | 12/12 (100%) |
| Durations | 5/5 (100%) |
| RNG seed range | 1000–3999 |
| Manifest file size | 364 KB |

---

## Transition to Phase 2 (Tasks 4-10)

### Task 4: Validity Constraints ⏳
**Goal**: Implement full validity checking

**Input**: manifest_candidates.csv (3000 rows)

**Process**:
- For each candidate, verify:
  - Map-model compatibility (already filtered)
  - POI files exist (for WorkingDayMovement)
  - Route files exist (for MapRouteMovement/BusMovement)
  - Cluster center in bounds (for ClusterMovement)
  - No duplicate names
  - Positive values for all required fields

**Output**: 
- `scenario_space_v1_validity_results.csv` (3000 rows with validity status)
- List of invalid candidates (if any) with error codes

**Effort**: ~2–3 hours (straightforward validation)

---

### Task 5: .settings Generation ⏳
**Goal**: Create executable .settings files from manifest

**Input**: manifest_candidates.csv + design space YAML

**Process**:
- For each valid candidate, create .settings file using template:
  - Header with generation metadata
  - Movement model configuration (map-specific POI/route files)
  - Network parameters (transmit range, buffer, TTL)
  - Baseline events block (EpidemicRouter, simple message generation)
  - Report configuration (MessageStatsReport, ContactTimesReport)

**Output**:
- `scenarios/scenario_space_v1/settings/{map_id}/*.settings` (3000 files)
- Structure: `SV1_{family}_{map_abbr}_{model_abbr}_{n_hosts}_{duration}h_{seed}.settings`

**Effort**: ~4–6 hours (template-based generation, validation)

**Validation**: Test 10% sample by running with The ONE

---

### Task 6: Static Feature Extraction ⏳
**Goal**: Extract features from .settings without simulation

**Input**: scenario_space_v1/settings/ (3000 .settings files)

**Process**:
- Parse each file to extract:
  - Structural: n_hosts, n_groups, group composition
  - Spatial: world_area, density (nodes/m²), map features
  - Mobility: movement_model, speed_range, wait_range, cluster parameters
  - Network: transmit_range, buffer_size, ttl
  - Temporal: endTime, RNG seed
- Compute derived: area_per_node, speed_category, density_category

**Output**:
- `scenarios/analysis/data/scenario_space_v1_static_features.csv` (3000 rows × 30+ columns)
- Feature distribution report

**Effort**: ~3–4 hours (parsing + CSV writing)

---

### Task 7: Feature Analysis & Diversity ⏳
**Goal**: Analyze feature space and identify redundancy

**Input**: static_features.csv (3000 rows)

**Process**:
- Normalize features (0–1 scale)
- Compute pairwise distances:
  - Euclidean distance matrix
  - Cosine similarity
  - Pearson correlation (for temporal/speed features)
- Identify clusters and redundant scenarios
- Generate diversity heatmap

**Output**:
- Distance matrix (JSON or NPZ)
- Correlation heatmap (visualization)
- Redundancy report

**Effort**: ~2–3 hours (scipy clustering)

---

### Task 8: Pruning Strategy & Selection ⏳
**Goal**: Select diverse corpus from 3000 candidates

**Input**: static_features.csv, distance matrices

**Process**:
- Apply diversity selection algorithm:
  - k-medoids or farthest-point sampling
  - Select ~500–1000 representative scenarios
  - Ensure coverage of all maps, models, and density ranges
- Validate selected scenarios:
  - No extreme outliers
  - Covers empirical parameter ranges
  - Balanced by environment type (urban, campus, rural, etc.)

**Output**:
- `scenario_space_v1_pruned_indices.txt` (list of 500–1000 selected candidate IDs)
- Pruning report with justification

**Effort**: ~3–4 hours (selection + visualization)

---

### Task 9: Traffic Profiles ⏳
**Goal**: Apply traffic profiles to pruned corpus

**Input**: scenario_space_v1/settings/ (500–1000 .settings)

**Process**:
- For each scenario, create 6–10 variants with different traffic profiles:
  - TP01_Baseline (moderate load)
  - TP02_LowLoad (sparse)
  - TP03_ManySmall (high frequency, small messages)
  - TP04_FewLarge (low frequency, large messages)
  - TP05_RealTime (short TTL, urgent)
  - TP06_DelayTolerant (long TTL)
  - ... (protocol/load variants)

**Output**:
- `corpus_v2/` (5000–10000 .settings files)
  - Subdirectories: 01_urban/, 02_campus/, ..., 06_social/ (mirroring base_scenarios structure)
  - Manifest: corpus_v2/manifest.csv (columns: family, scenario_base, scenario_name, traffic_profile_id, settings_file, ...)

**Effort**: ~4–6 hours (template application + validation)

---

### Task 10: Final Documentation & Validation ⏳
**Goal**: Document corpus, validate all scenarios, publish final deliverables

**Input**: corpus_v2/, static_features.csv

**Process**:
- Validate corpus_v2:
  - Run 10% sample through The ONE (quick smoke test)
  - Check syntax, no duplicates, all files exist
- Document:
  - Corpus design rationale (traceability to design space)
  - Feature coverage vs. real traces
  - Sampling methodology
  - Limitations and future work
- Publish reports:
  - `corpus_v2/README.md` (usage guide)
  - `scenarios/analysis/reports/corpus_v2_design_report.md` (full methodology)
  - `scenarios/analysis/reports/corpus_v2_feature_coverage.md` (empirical justification)

**Output**:
- corpus_v2/ (final corpus)
- corpus_v2/manifest.csv (final manifest)
- Documentation (3 reports, 30–50 KB total)

**Effort**: ~3–4 hours (validation + writing)

---

## Phase 2 Timeline Estimate

| Task | Effort | Duration | Blocker |
|------|--------|----------|---------|
| 4. Validity | 2–3h | 1 day | None |
| 5. .settings generation | 4–6h | 1–2 days | Task 4 |
| 6. Static features | 3–4h | 1 day | Task 5 |
| 7. Feature analysis | 2–3h | 1 day | Task 6 |
| 8. Pruning | 3–4h | 1 day | Task 7 |
| 9. Traffic profiles | 4–6h | 1–2 days | Task 8 |
| 10. Documentation | 3–4h | 1 day | Task 9 |
| **Total** | **23–30h** | **6–9 days** | Sequential |

**Estimated completion**: Within 2 weeks (assuming 3–4h/day work)

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| POI files missing for some candidates | Task 5 fails | Verify all required files exist (Task 4) |
| The ONE version incompatibility | Scenarios don't run | Test on current ONE version; document version |
| Feature extraction too slow | Phase 2 blocked | Optimize parser; parallelize if needed |
| Pruning selects unbalanced corpus | Corpus skewed | Ensure stratification by environment type |
| Traffic profile parameters unrealistic | Validation fails | Cross-check against real-trace ranges |

---

## Success Criteria for Phase 2

- [ ] All 3000 candidates pass validity checks or are marked invalid with reason
- [ ] ~3000 .settings files generated (or 2900+ if small fraction invalid)
- [ ] Static features extracted for all valid scenarios
- [ ] 500–1000 representative scenarios selected via principled algorithm
- [ ] corpus_v2 created with 5000–10000 final scenarios (500–1000 bases × 6–10 traffic profiles)
- [ ] All scenarios validated to be syntactically correct for The ONE
- [ ] Documentation complete with traceability to design space and real-trace audit
- [ ] corpus_v1 and base_scenarios remain frozen (no modifications)

---

## References & Navigation

**Phase 1 Outputs** (Current):
- Code audit: `scenarios/analysis/reports/scenario_space_v1_code_audit.md`
- Design space: `scenarios/analysis/config/scenario_design_space_v1.yaml`
- Generator: `scenarios/setup/generate_scenario_space_v1.py`
- Candidate pool: `scenarios/scenario_space_v1/manifest_candidates.csv`
- Reports: `scenarios/analysis/reports/scenario_space_v1_*.md`

**Reference Materials** (Earlier phases):
- Real-trace audit: `scenarios/analysis/data/real_trace_scenarios_inventory.csv`
- Real-trace reports: `scenarios/analysis/reports/real_trace_*.md`
- Base scenarios: `scenarios/base_scenarios/`
- corpus_v1: `scenarios/corpus_v1/` (frozen, for reference)

**The ONE Simulator**:
- Jar: `/home/raul/Documents/the-one/one-1.6.0.jar` (or current version)
- Docs: `/home/raul/Documents/the-one/doc/`

---

## Handoff Checklist

- [x] Design space fully specified in YAML
- [x] Candidate pool generated (3000 scenarios)
- [x] Manifest CSV complete
- [x] Generator script tested (estimate, dry-run, generate modes)
- [x] Reports document methodology
- [x] No modifications to corpus_v1 or base_scenarios
- [x] All deliverables traceable to requirements
- [ ] Task 4 ready to begin (awaiting next phase approval)

---

**End of Phase 1 Summary**

Phase 1 successfully delivered an explicit, reproducible design space for systematic scenario generation. The 3000-candidate pool represents 3% of the valid design space, providing sufficient diversity for empirical corpus design. Tasks 4–10 will now convert parameters to .settings files, extract features, prune via diversity metrics, apply Traffic Profiles, and produce the final corpus_v2.

