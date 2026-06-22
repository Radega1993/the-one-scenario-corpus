# START HERE: scenario_space_v1 Phase 1 Complete

> **Actualización 2026-06-14:** El corpus estructural tiene **100.800** candidatos (`manifest.csv`). Trazabilidad del pipeline de mapas (Fases 0–2b) en [`scenarios/scenario_space_v1/migration/`](../scenario_space_v1/migration/README.md).

**Status**: ✅ COMPLETE (Tasks 1-3)  
**Date**: 2026-06-13  
**Output**: 3,000 candidate scenarios ready for Phase 2  
**Next**: Begin Phase 2 (Tasks 4-10) or review documentation

---

## What Happened

You've completed a comprehensive redesign of The ONE scenario corpus from manual/ad-hoc to **systematic and reproducible**. 

**Previously**: 6 manual families × base scenarios manually designed  
**Now**: Explicit design space → 3,000 empirically-grounded candidates → (later) pruned corpus

---

## 30-Second Summary

- **Phase 0 (Prior)**: Audited 17 real DTN/OppNet datasets; extracted empirical parameter ranges
- **Task 1**: Analyzed codebase; documented 5 movement models, 6 maps, 15+ constraints
- **Task 2**: Defined explicit 8-dimensional design space (YAML)
- **Task 3**: Built generator; created 3,000 parameter-only scenarios
- **Status**: Ready for Phase 2 (convert parameters → .settings files → features → prune → corpus_v2)

---

## Key Findings

✓ Design space: 100,800 valid combinations (filtered from 216,000 brute-force)  
✓ 3,000 candidates: 3% representative sample across all dimensions  
✓ All empirically grounded (real-trace audit + base_scenarios analysis)  
✓ Fully reproducible (deterministic, seed-based)  
✓ No modifications to corpus_v1 or base_scenarios (frozen as reference)

---

## What You Can Do Right Now

### Quick Test
```bash
cd /home/raul/Documents/the-one

# Estimate total design space (10 seconds)
python3 scenarios/setup/generate_scenario_space_v1.py --estimate-only

# Preview 20 candidates without writing files (5 seconds)
python3 scenarios/setup/generate_scenario_space_v1.py --dry-run --max-settings 20
```

### Use the Data
```bash
# Load 3000 candidates in Python
import pandas as pd
df = pd.read_csv("scenarios/scenario_space_v1/manifest_candidates.csv")
print(df.shape)  # (3000, 13)
```

### Understand the Design
```bash
# Read design space specification (YAML)
cat scenarios/analysis/config/scenario_design_space_v1.yaml

# Read code audit (what models/maps exist)
less scenarios/analysis/reports/scenario_space_v1_code_audit.md
```

---

## Documents to Read (Pick Your Path)

### Executive (5 min)
→ **SCENARIO_SPACE_V1_EXECUTIVE_SUMMARY.md**

### Technical (15 min)
→ **scenario_space_v1_phase1_summary.md**

### For Navigation
→ **INDEX_SCENARIO_SPACE_V1.md** (all documents organized by role)

### For Implementation
→ **scenario_space_v1_code_audit.md** (movement models, constraints)

### For Details
→ **scenario_space_v1_size_estimate.md** (space breakdown, sampling analysis)

### For Using the Tool
→ **scenarios/scenario_space_v1/README.md** (quick-start)

---

## Key Artifacts

| What | Where | Size | What It Is |
|------|-------|------|-----------|
| Generator | `scenarios/setup/generate_scenario_space_v1.py` | 24 KB | Python script (3 modes) |
| Design Space | `scenarios/analysis/config/scenario_design_space_v1.yaml` | 13 KB | YAML specification |
| Candidates | `scenarios/scenario_space_v1/manifest_candidates.csv` | 364 KB | 3000 parameter combinations |
| Code Audit | `scenarios/analysis/reports/scenario_space_v1_code_audit.md` | 22 KB | Movement models & constraints |
| Size Report | `scenarios/analysis/reports/scenario_space_v1_size_estimate.md` | 12 KB | Space breakdown & analysis |

---

## Next: Phase 2 (Tasks 4-10)

**Timeline**: 6–9 days (sequential)

| Task | Output | Days |
|------|--------|------|
| 4. Validity | Valid candidates list | 1–2 |
| 5. .settings | 3000 .settings files | 1–2 |
| 6. Features | Static feature matrix | 1 |
| 7. Diversity | Feature analysis | 1 |
| 8. Pruning | 500–1000 selected scenarios | 1 |
| 9. Traffic | corpus_v2 (5000–10000 files) | 1–2 |
| 10. Docs | Final reports & validation | 1 |

**Output**: corpus_v2 (final scenario corpus ready for use)

---

## FAQ

**Q: Where are the 3000 .settings files?**  
A: Not yet. Task 5 generates them. Currently only parameter metadata exists.

**Q: Can I use scenario_space_v1 now?**  
A: Yes, but Phase 2 is needed to make it usable (Task 5 creates .settings).

**Q: What happened to corpus_v1?**  
A: It's frozen and unchanged. corpus_v2 (new) will eventually replace it.

**Q: How do I regenerate the candidates?**  
A: `python3 scenarios/setup/generate_scenario_space_v1.py --generate --max-settings 5000 --seed 123`

**Q: Is this grounded in real data?**  
A: Yes. All values come from (1) real-trace audit (17 datasets) or (2) base_scenarios analysis.

---

## Checklist (For Phase 2 Start)

- [ ] Review executive summary (5 min)
- [ ] Verify manifest: `wc -l scenarios/scenario_space_v1/manifest_candidates.csv` (should be 3001)
- [ ] Test generator: `python3 scenarios/setup/generate_scenario_space_v1.py --estimate-only`
- [ ] Read design space: `cat scenarios/analysis/config/scenario_design_space_v1.yaml | head -100`
- [ ] Confirm corpus_v1 untouched: `ls scenarios/corpus_v1/manifest.csv`
- [ ] Approve proceeding to Task 4

---

## Most Important Files

**You are here**  
👇  
`00_START_HERE_SCENARIO_SPACE_V1.md` (this file)

**For decisions**  
👇  
`SCENARIO_SPACE_V1_EXECUTIVE_SUMMARY.md`

**For implementation**  
👇  
`scenario_space_v1_phase1_summary.md`

**For navigation**  
👇  
`INDEX_SCENARIO_SPACE_V1.md`

**For using the generator**  
👇  
`scenarios/scenario_space_v1/README.md`

---

## Status

✅ Phase 1 (Tasks 1-3): COMPLETE  
- Code audit: DONE
- Design space defined: DONE
- Generator implemented: DONE
- 3,000 candidates generated: DONE

⏳ Phase 2 (Tasks 4-10): PENDING  
- Ready to start Task 4 (Validity Constraints)
- Awaiting approval to proceed

---

**Next Action**: 
1. Read `SCENARIO_SPACE_V1_EXECUTIVE_SUMMARY.md` (10 min)
2. Verify manifest file exists and has 3000 rows
3. Decide: Proceed to Phase 2 or request modifications

