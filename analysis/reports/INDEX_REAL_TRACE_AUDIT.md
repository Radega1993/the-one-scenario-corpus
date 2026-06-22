# Real Trace Scenarios Audit — Complete Index

**Generated**: 2026-06-13  
**Status**: Audit Complete ✓  
**Scope**: DTN/OppNet datasets for The ONE corpus parametrization

---

## 📋 Document Navigation

### Executive Level (Start Here)
- **[AUDIT_EXECUTIVE_SUMMARY.txt](AUDIT_EXECUTIVE_SUMMARY.txt)** ⭐
  - Quick 3-minute read
  - Key findings + immediate action items
  - Recommendation: Phase 1 (DieselNet validation)
  - **→ Start here if:** You need a quick overview

### Strategic Level (Decision Makers)
- **[real_trace_scenarios_synthesis.md](real_trace_scenarios_synthesis.md)**
  - Complete roadmap (phases 1–4)
  - Decision matrix + risk analysis
  - Success criteria
  - **→ Read this for:** Project planning & team alignment

### Operational Level (Implementers)

#### 1. Data Registry
- **[real_trace_scenarios_inventory.csv](../data/real_trace_scenarios_inventory.csv)**
  - 17 datasets, 20 metadata columns
  - Tier classification, availability, convertibility
  - **→ Use for:** Structured dataset lookup

#### 2. Findings & Analysis
- **[real_trace_scenarios_inventory.md](real_trace_scenarios_inventory.md)**
  - Detailed findings by tier
  - Tier 1: Reproducible (1 dataset)
  - Tier 2: Convertible (4 datasets)
  - Tier 3: Reference (5 datasets)
  - Tier 4: Theoretical (3+ baselines)
  - License/access summary
  - **→ Read for:** Full context on each dataset

#### 3. Empirical Data
- **[real_trace_parameter_ranges.md](real_trace_parameter_ranges.md)**
  - Extracted ranges: nodes, duration, contact patterns
  - Mobility model parameters
  - Environment type distribution
  - Parameter checklist for validation
  - **→ Use for:** Corpus parametrization guidance

#### 4. Technical Implementation
- **[real_trace_conversion_guide.md](real_trace_conversion_guide.md)**
  - Pattern 1: Contact traces → ExternalEvent (CONN format)
  - Pattern 2: GPS trajectories → ExternalMovement
  - Pattern 3: WiFi associations → Derived contacts
  - Code examples (Python)
  - Validation scripts
  - **→ Read for:** Technical how-to for converting traces

### Meta Documentation
- **[README_real_trace_audit.md](README_real_trace_audit.md)**
  - Overview of all documents
  - Column explanations
  - Quick-start by role
  - **→ Reference this for:** Document index & glossary

---

## 🎯 Quick Navigation by Role

### For Project Managers
1. Read: `AUDIT_EXECUTIVE_SUMMARY.txt` (3 min)
2. Scan: `real_trace_scenarios_synthesis.md` (phases & timeline)
3. Decide: Approve Phase 1?

### For Data Scientists / Corpus Designers
1. Read: `real_trace_scenarios_inventory.md` (findings)
2. Study: `real_trace_parameter_ranges.md` (empirical data)
3. Compare: Current corpus vs. real-trace ranges
4. Output: Parametrization report

### For Developers / Tool Builders
1. Read: `real_trace_conversion_guide.md` (full technical guide)
2. Implement: GPS-to-trajectory converter (Phase 2.1)
3. Test: Against Cabspotting sample
4. Validate: Using provided scripts

### For Academic Researchers / Paper Authors
1. Read: All documents in order (comprehensive review)
2. Cite: Specific datasets + parametrization findings
3. Extend: With new datasets or improved converters

---

## 📊 Key Tables & Figures (Summary)

### Inventory Summary (17 datasets)

| Tier | Count | Example | Status |
|------|-------|---------|--------|
| Tier 1 | 1 | DieselNet | Ready to run ✓ |
| Tier 2 | 4 | SF Taxi, UCSD WiFi | Convertible (2-3 weeks) |
| Tier 3 | 5 | INFOCOM, MIT Reality | Reference only |
| Tier 4 | 3+ | RWP, CRAWDAD | Theoretical baselines |

### Empirical Parameter Ranges

```
Nodes:      30–500 (environment-dependent)
Duration:   1–365+ days (1 day, 7 days, 30 days typical)
Contact:    1–60 min (pedestrian ~10 min, vehicular ~3 min)
Density:    0.02–0.8 (sparse to dense)
Speed:      1–2 m/s pedestrian; 5–15 km/h vehicular
```

### Recommendation Priority

| Dataset | Availability | Effort | Impact | Timeline | Priority |
|---------|--------------|--------|--------|----------|----------|
| DieselNet | ✓ Easy | 1 d | HIGH | Month 1 | **P1 NOW** |
| Cabspotting | ✓ Easy | 2 wk | HIGH | Mo 2–3 | **P1 SOON** |
| Haggle | ⚠ Medium | 2–4 wk | MEDIUM | Mo 3–6 | **P2** |
| INFOCOM | ✗ Hard | 1 wk | MEDIUM | Month 1 | **P1 REF** |
| NYC Taxi | ✓ Easy | 3 wk | LOW | Mo 6+ | **P3** |

---

## 🔍 How to Use This Audit

### Scenario 1: "I need a 5-minute executive brief"
→ Read: `AUDIT_EXECUTIVE_SUMMARY.txt`

### Scenario 2: "I need to decide if we should use DieselNet"
→ Read: 
  1. `AUDIT_EXECUTIVE_SUMMARY.txt` (overview)
  2. `real_trace_scenarios_inventory.md` → "DieselNet Fall 2007" (details)
  3. `real_trace_synthesis.md` → "Phase 1.1" (implementation plan)

### Scenario 3: "I need to convert GPS traces from Cabspotting"
→ Read:
  1. `real_trace_conversion_guide.md` → "Pattern 2: GPS Trajectories"
  2. Study Python code examples
  3. Follow validation steps

### Scenario 4: "I need to justify corpus parameters empirically"
→ Read:
  1. `real_trace_parameter_ranges.md` (extract ranges)
  2. `real_trace_scenarios_inventory.md` → "Tier 1-2" (which traces have data)
  3. Create parametrization report citing specific datasets

### Scenario 5: "I need the complete picture (audit, findings, roadmap)"
→ Read all documents in this order:
  1. `AUDIT_EXECUTIVE_SUMMARY.txt` (overview)
  2. `real_trace_scenarios_inventory.md` (findings)
  3. `real_trace_parameter_ranges.md` (empirical data)
  4. `real_trace_conversion_guide.md` (technical details)
  5. `real_trace_scenarios_synthesis.md` (roadmap)

---

## 📁 File Locations

```
scenarios/analysis/
├── data/
│   └── real_trace_scenarios_inventory.csv ................... Data registry
└── reports/
    ├── AUDIT_EXECUTIVE_SUMMARY.txt .......................... Quick overview
    ├── INDEX_REAL_TRACE_AUDIT.md ............................ This file
    ├── README_real_trace_audit.md ........................... Doc index
    ├── real_trace_scenarios_inventory.md .................... Findings
    ├── real_trace_parameter_ranges.md ....................... Empirical data
    ├── real_trace_conversion_guide.md ....................... Technical how-to
    └── real_trace_scenarios_synthesis.md .................... Roadmap

toolkit/
└── dieselnetConverter.pl .................................. Existing converter (ready)
```

---

## 🚀 Next Steps (Immediate)

### Week 1: Review & Approval
- [ ] Decision makers review `AUDIT_EXECUTIVE_SUMMARY.txt`
- [ ] Approve Phase 1 (DieselNet validation, ~1 week effort)
- [ ] Assign 1–2 developers

### Week 2–3: Phase 1 Execution
- [ ] Download DieselNet dataset
- [ ] Test `toolkit/dieselnetConverter.pl`
- [ ] Compute contact statistics
- [ ] Compare with synthetic corpus

### Week 4: Decision Point
- [ ] Publish validation report
- [ ] Decision: Proceed to Phase 2 (GPS converter)?

---

## ❓ FAQ

**Q: Is the audit complete?**  
A: ✓ Yes. 17 datasets inventoried, conversion techniques documented, roadmap created.

**Q: What do I do now?**  
A: Start Phase 1 (DieselNet). 1-week effort for high impact. See `AUDIT_EXECUTIVE_SUMMARY.txt`.

**Q: Can we skip straight to Phase 2?**  
A: Not recommended. Phase 1 validates the approach on free, public data (minimal risk). Phase 2 follows with more engineering.

**Q: Do we need all 17 datasets?**  
A: No. Priority: DieselNet (immediate), Cabspotting (month 2), Cambridge Haggle (if obtainable). Others are optional or reference-only.

**Q: Are there licensing issues?**  
A: Not for Tier 1-2 datasets (public). Tier 3 requires academic contact (Haggle, KAIST) or is restricted (MIT Reality, INFOCOM).

**Q: How much does this improve reproducibility?**  
A: High impact. From "unvalidated synthetic" to "validated against real traces" (single sentence → credibility boost).

---

## 📞 Contact & Attribution

**Audit Conducted**: 2026-06-13  
**Method**: Literature review, dataset survey, infrastructure analysis  
**Tools Used**: SQL inventory tracking, Markdown documentation, Python prototypes

**For Questions**: Refer to specific documents or contact project lead.

---

## 📚 References & Resources

### Datasets
- **DieselNet**: http://traces.cs.umass.edu/
- **SF Taxi (Cabspotting)**: http://crawdad.org/ucsd/mobility/
- **UCSD WiFi**: http://crawdad.org/ucsd/wifi/
- **INFOCOM/MIT Reality**: See document for details

### The ONE
- **GitHub**: https://github.com/akeranen/the-one
- **Documentation**: https://akeranen.github.io/the-one/
- **Converter Tool**: `toolkit/dieselnetConverter.pl`

---

**Last Updated**: 2026-06-13  
**Status**: Complete & Ready for Implementation  
**Version**: 1.0

---

**Next Document** → [AUDIT_EXECUTIVE_SUMMARY.txt](AUDIT_EXECUTIVE_SUMMARY.txt) for quick overview  
**Full Documentation** → [README_real_trace_audit.md](README_real_trace_audit.md) for guidance
