# scenario_space_v1: Documentation Index

**Phase 1 Complete** (Tasks 1-3)  
**Generated**: 2026-06-13  
**Purpose**: Navigation guide for scenario_space_v1 documentation and deliverables

---

## Quick Navigation

### For Decision Makers (5-min read)
→ Start here: **`SCENARIO_SPACE_V1_EXECUTIVE_SUMMARY.md`**
- What was built
- Key findings
- Timeline to completion
- Next steps

### For Implementation (Developers/Researchers)
→ Start with: **`scenario_space_v1_phase1_summary.md`**
- Detailed Phase 1 deliverables
- Phase 2 task breakdown
- Effort estimates
- Success criteria

### For Understanding the Design Space
→ Technical specification: **`scenarios/analysis/config/scenario_design_space_v1.yaml`**
→ Explanation: **`scenario_space_v1_code_audit.md`**

### For Using the Generator
→ User guide: **`scenarios/scenario_space_v1/README.md`**
→ Script: **`scenarios/setup/generate_scenario_space_v1.py`**

### For Feature Analysis (Phase 2+)
→ Output analysis: **`scenario_space_v1_size_estimate.md`**

---

## Document Map

### Phase 1 Deliverables (Current)

| Document | Type | Size | Audience | Purpose |
|----------|------|------|----------|---------|
| **SCENARIO_SPACE_V1_EXECUTIVE_SUMMARY.md** | Report | 10 KB | Decision makers, leads | High-level overview; what's done, what's next |
| **scenario_space_v1_phase1_summary.md** | Technical | 13 KB | Developers, researchers | Detailed milestones, Phase 2 roadmap, risks |
| **scenario_space_v1_code_audit.md** | Analysis | 22 KB | Technical leads, SMEs | Movement models, maps, constraints, parameter ranges |
| **scenario_space_v1_size_estimate.md** | Analysis | 12 KB | Researchers, data analysts | Design space size, sampling strategy, coverage |
| **scenarios/analysis/config/scenario_design_space_v1.yaml** | Configuration | 13 KB | Developers | Formal specification of design space |
| **scenarios/setup/generate_scenario_space_v1.py** | Code | 24 KB | Developers | Executable generator (estimate, dry-run, generate) |
| **scenarios/scenario_space_v1/README.md** | Usage Guide | 5 KB | Users | Quick-start, command reference |
| **scenarios/scenario_space_v1/manifest_candidates.csv** | Data | 364 KB | Data analysts | 3000 candidate scenarios (parameters) |
| **scenarios/scenario_space_v1/scenario_space_v1_size_estimate.json** | Data | 1.4 KB | Programmatic access | Design space size breakdown |

### Earlier Phase Outputs (Reference)

| Document | Phase | Type | Purpose |
|----------|-------|------|---------|
| **scenarios/analysis/data/real_trace_scenarios_inventory.csv** | 0 (Audit) | Data | 17 DTN/OppNet datasets; availability, convertibility, parameters |
| **scenarios/analysis/reports/real_trace_scenarios_inventory.md** | 0 (Audit) | Report | Detailed findings on real traces; tier classification |
| **scenarios/analysis/reports/real_trace_parameter_ranges.md** | 0 (Audit) | Report | Empirical parameter ranges extracted from traces |
| **scenarios/analysis/reports/real_trace_conversion_guide.md** | 0 (Audit) | Report | How to convert traces (GPS, contacts) to The ONE format |
| **scenarios/base_scenarios/manifest.csv** | N/A | Data | 45 base scenarios (reference, frozen) |
| **scenarios/corpus_v1/manifest.csv** | N/A | Data | 540 corpus scenarios (reference, frozen) |

---

## How to Navigate by Role

### Decision Maker / Project Lead
1. Read: **SCENARIO_SPACE_V1_EXECUTIVE_SUMMARY.md** (10 min)
2. Skim: **scenario_space_v1_phase1_summary.md** section "Phase 2 Timeline Estimate" (3 min)
3. Decide: Approve proceeding to Phase 2, or request modifications

### Researcher / Data Analyst
1. Read: **SCENARIO_SPACE_V1_EXECUTIVE_SUMMARY.md** (10 min)
2. Study: **scenario_space_v1_size_estimate.md** (15 min)
3. Explore: **scenario_space_v1_code_audit.md** section "Parameter Ranges Summary" (10 min)
4. Query: Load and analyze **scenarios/scenario_space_v1/manifest_candidates.csv** in Python/R/SQL

### Developer / Software Engineer
1. Study: **scenario_space_v1_code_audit.md** (20 min)
2. Reference: **scenarios/analysis/config/scenario_design_space_v1.yaml** (YAML spec)
3. Understand: **scenarios/setup/generate_scenario_space_v1.py** (code walkthrough, 20 min)
4. Extend: Implement Task 4 (validity constraints) based on rules documented

### User / Simulation Operator
1. Start: **scenarios/scenario_space_v1/README.md** (5 min)
2. Run: `python3 scenarios/setup/generate_scenario_space_v1.py --estimate-only` (1 min)
3. Generate: `python3 scenarios/setup/generate_scenario_space_v1.py --generate --max-settings 3000` (1 min)
4. Use: Load **scenarios/scenario_space_v1/manifest_candidates.csv** for Phase 2 processing

---

## Data Flow

```
Real-trace audit (Phase 0)
    ↓
    → scenarios/analysis/data/real_trace_scenarios_inventory.csv
    → scenarios/analysis/reports/real_trace_parameter_ranges.md
                    ↓
                    ├→ Informs design space values
                    
Code audit (Task 1)
    ↓
    → scenarios/analysis/reports/scenario_space_v1_code_audit.md
                    ↓
                    ├→ Documents movement models, maps, constraints
                    
Design space definition (Task 2)
    ↓
    → scenarios/analysis/config/scenario_design_space_v1.yaml
                    ↓
                    ├→ Input to generator
                    
Generator script (Task 3)
    ↓
    → scenarios/setup/generate_scenario_space_v1.py
    → scenarios/scenario_space_v1/scenario_space_v1_size_estimate.json
                    ↓
                    ├→ Estimate mode
                    
Generation (Task 3)
    ↓
    → scenarios/scenario_space_v1/manifest_candidates.csv (3000 rows)
    → scenarios/analysis/reports/scenario_space_v1_size_estimate.md
                    ↓
                    ├→ Input to Phase 2 (Tasks 4-10)

Phase 2 (Tasks 4-10, Planned)
    ↓
    → Validity (Task 4)
    → .settings files (Task 5)
    → Static features (Task 6)
    → Feature analysis (Task 7)
    → Pruning (Task 8)
    → Traffic Profiles (Task 9)
    → Final corpus_v2 (Task 10)
```

---

## Key Artifacts by Purpose

### Configuration & Specification
- `scenarios/analysis/config/scenario_design_space_v1.yaml` — Authoritative design space definition

### Executable Code
- `scenarios/setup/generate_scenario_space_v1.py` — Scenario generator (3 modes)

### Input Data
- `scenarios/scenario_space_v1/manifest_candidates.csv` — 3000 parameter combinations
- `scenarios/analysis/data/real_trace_scenarios_inventory.csv` — Reference dataset inventory

### Analysis Reports
- `scenarios/analysis/reports/scenario_space_v1_code_audit.md` — Movement models & constraints
- `scenarios/analysis/reports/scenario_space_v1_size_estimate.md` — Space size & sampling analysis
- `scenarios/analysis/reports/scenario_space_v1_phase1_summary.md` — Phase 1 summary & Phase 2 roadmap

### User Documentation
- `scenarios/scenario_space_v1/README.md` — Quick-start guide
- `SCENARIO_SPACE_V1_EXECUTIVE_SUMMARY.md` — Executive summary (this document's context)

### Reference (Frozen)
- `scenarios/base_scenarios/` — 45 structural bases (DO NOT MODIFY)
- `scenarios/corpus_v1/` — 540 corpus scenarios (DO NOT MODIFY)

---

## FAQ

### Q: Where do I find the 3000 candidate scenarios?
A: In `scenarios/scenario_space_v1/manifest_candidates.csv` (CSV with 3000 rows, one per candidate)
   These are parameter combinations, not yet .settings files (those come in Task 5/Phase 2)

### Q: How do I regenerate the candidates with different parameters?
A: Run: `python3 scenarios/setup/generate_scenario_space_v1.py --generate --max-settings 5000 --sampling random --seed 123`
   See `scenarios/scenario_space_v1/README.md` for full command reference

### Q: What's the difference between manifest_candidates.csv and corpus_v1/manifest.csv?
A: 
- `manifest_candidates.csv`: Parameters only (no .settings files yet); all 3000 from design space
- `corpus_v1/manifest.csv`: Final corpus (540 scenarios × 6 traffic profiles); has .settings file paths

### Q: Why are corpus_v1 and base_scenarios frozen?
A: They serve as historical reference and validation baseline. corpus_v2 will be the new standard.

### Q: When will .settings files be generated for the 3000 candidates?
A: Task 5 (Phase 2), estimated 1–2 days. Then static features extracted (Task 6).

### Q: Can I use the 3000 candidates for simulation now?
A: Not yet. Task 5 generates .settings files. Currently only parameter metadata exists.

### Q: How do I know which candidates are valid?
A: All 3000 in manifest_candidates.csv have passed map-model compatibility checks (Task 3).
   Full validation (POI files, route files, cluster bounds) happens in Task 4 (Phase 2).

---

## Contact & Questions

For issues or questions about scenario_space_v1:

1. Check the relevant document (see navigation guide above)
2. Review code comments in `scenarios/setup/generate_scenario_space_v1.py`
3. Consult `scenarios/analysis/reports/scenario_space_v1_code_audit.md` for technical details
4. Refer to `scenarios/analysis/config/scenario_design_space_v1.yaml` for specification questions

---

**Last Updated**: 2026-06-13  
**Phase**: 1 (COMPLETE) | Phase 2 (PENDING)
