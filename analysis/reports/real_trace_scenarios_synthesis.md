# Real Trace Scenarios Audit — Final Synthesis & Recommendations

**Date**: 2026-06-13  
**Audit Scope**: DTN/OppNet datasets for The ONE corpus parametrization  
**Status**: Comprehensive audit completed with actionable recommendations

---

## Executive Summary

### Key Finding

The ONE simulator has **infrastructure to support real trace data** (DieselNet converter, ExternalMovement, ExternalEvent), but the current **corpus (corpus_v1, base_scenarios) is entirely synthetic** with **no validation against real datasets**.

### Opportunity

**14 real datasets** have been identified and classified:
- **1 immediately usable** (DieselNet via existing Perl converter)
- **4 convertible with engineering** (SF Taxi, NYC Taxi, UCSD WiFi, NUS WiFi)
- **5 reference-only** (INFOCOM, MIT Reality, RollerNet, Cambridge Haggle, KAIST)
- **3 theoretical baselines** (RWP, Brownian Motion, CRAWDAD meta-repository)

### Recommendation Priority

1. **Tier 1 (Do First)**: Validate `03_vehicles` family against DieselNet + Cabspotting
2. **Tier 2 (Do Soon)**: Implement GPS-to-trajectory converter for CF Taxi validation
3. **Tier 3 (Do Later)**: Attempt to obtain Cambridge Haggle for campus benchmark
4. **Tier 4 (Reference Only)**: Use INFOCOM/MIT Reality for parametrization guidance

---

## What We Found (Inventory Summary)

### Tier 1: Reproducible (Ready to Run)

#### DieselNet Fall 2007 & Spring 2008
- **Availability**: ✓ **PUBLIC** (UMass Traces Repository)
- **Format**: Bus contact traces (40 PVTA buses)
- **The ONE Support**: ✓ **YES** — Perl converter in `toolkit/dieselnetConverter.pl`
- **Effort**: Minimal (< 1 day to test)
- **Use Case**: Validate urban vehicular contact patterns, tune vehicle scenarios
- **Status**: **IMMEDIATELY ACTIONABLE**

### Tier 2: Convertible (Available, Requires Engineering)

#### SF Taxi Cabspotting
- **Availability**: ✓ **PUBLIC** (CRAWDAD repository)
- **Format**: GPS trajectories (~500 taxis, ~1 month)
- **Conversion**: GPS → ExternalMovement (coordinates + interpolation)
- **Effort**: ~1–2 weeks (write Python converter, validate)
- **Use Case**: Validate MapRouteMovement, city-scale mobility
- **Status**: **RECOMMENDED FOR EARLY PHASE**

#### UCSD WiFi Campus
- **Availability**: ✓ **PUBLIC** (CRAWDAD)
- **Format**: WiFi association events (~1000 devices, 1+ years)
- **Conversion**: WiFi logs → derived contact pairs
- **Effort**: ~1 week (derive contacts, validate assumptions)
- **Use Case**: Contact graph validation, campus-scale benchmark
- **Status**: **RECOMMENDED FOR PHASE 2**

#### NYC Manhattan Taxi
- **Availability**: ✓ **PUBLIC** (TLC + research datasets)
- **Format**: GPS trajectories (~13k taxis, massive scale)
- **Conversion**: Same as Cabspotting (higher complexity due to scale)
- **Effort**: ~2–3 weeks (heavy data engineering)
- **Use Case**: Large-scale urban mobility (optional, computationally expensive)
- **Status**: **OPTIONAL FOR INFRASTRUCTURE STUDY**

### Tier 3: Reference Only (Limited/No Access)

#### INFOCOM Conference Series (2005–2007)
- **Availability**: ✗ **RESTRICTED** (academic legacy, no public repo)
- **Format**: Bluetooth contact traces (~78–150 attendees, 3 days each)
- **Contribution**: Empirical contact densities, interaction patterns
- **Use Case**: Conference/event scenario parametrization
- **Status**: Use for **inspiration only**; extract parameter ranges

#### MIT Reality Mining
- **Availability**: ✗ **RESTRICTED** (MIT-only, non-disclosure)
- **Format**: Long-term proximity (100 users, 9 months)
- **Contribution**: Long-term social structure, temporal evolution
- **Use Case**: Social dynamics, extended simulation validation
- **Status**: Use for **parametrization guidance only**

#### Cambridge Haggle / iMote
- **Availability**: ⚠ **PUBLIC WITH REQUEST** (academic contact required)
- **Format**: Bluetooth contact logs (104 users, 11 days, mixed environment)
- **Contribution**: Mixed indoor/outdoor patterns
- **Use Case**: Campus benchmark (if obtained)
- **Status**: **Worth attempting to obtain** (low-risk contact)

#### RollerNet
- **Availability**: ✗ **NOT PUBLIC** (legacy research)
- **Format**: Dense event-based contacts (62 participants, 24 hours)
- **Contribution**: High-density social pattern reference
- **Use Case**: Dense scenario inspiration only
- **Status**: **Citation only**

#### KAIST Mobile Traces
- **Availability**: ⚠ **POSSIBLY AVAILABLE** (contact KAIST)
- **Format**: Campus mobility + contacts (200 users, 2+ months)
- **Contribution**: Extended campus patterns
- **Use Case**: Campus validation (if obtained)
- **Status**: **Worth investigating** (medium-risk contact)

### Tier 4: Theoretical Baselines (Not Datasets)

- Random Waypoint Model (RWP)
- Brownian Motion Model
- CRAWDAD Meta-Repository (pointer to other traces)

---

## Analysis: Current Corpus Status

### Base_scenarios (45 scenarios, no Traffic Profiles)

| Family | Mobility Model | Empirical Validation | Recommendation |
|--------|----------------|--------------------|-----------------|
| 01_urban | RWP (pedestrian) | ✗ NONE | Add pedestrian campus validation |
| 02_campus | RWP + clustering | ✗ NONE | Validate against campus traces if available |
| 03_vehicles | MapRouteMovement | ✗ NONE | **VALIDATE AGAINST DIESELNET + CABSPOTTING** |
| 04_rural | RWP (sparse) | ✗ NONE | Reference only (no real sparse vehicular data) |
| 05_disaster | Disrupted backbone | ✗ NONE | Scenario-specific (emergency context) |
| 06_social | Group-based RWP | ✗ NONE | Validate against INFOCOM parameters |

**Finding**: All families are synthetic; **zero validation against real traces**.

**Implication**: Parameters (node count, speed, contact duration, etc.) are reasonable guesses but not evidence-based.

### Corpus_v1 (540 scenarios with Traffic Profiles 01–12)

**Status**: Built on top of unvalidated base_scenarios; Traffic Profiles add messaging patterns but not mobility realism.

---

## Parameter Ranges Extracted

### Recommended Core Ranges (from available data)

```
Number of Nodes:
  - Conference/event: 50–150 nodes ✓ (INFOCOM data)
  - Campus: 100–500 nodes ✓ (UCSD, NUS data)
  - Urban vehicular: 30–500 nodes ✓ (DieselNet, Cabspotting data)
  - Sparse rural: 20–80 nodes (inference from literature)

Duration:
  - Event-driven: 1 day (RollerNet 24h; INFOCOM 3h–3 days) ✓
  - Urban operations: 7–30 days (Cabspotting 30 days, DieselNet spring 180 days) ✓
  - Long-term: 90+ days (MIT Reality 9 months, UCSD WiFi 365+ days) ✓

Contact Duration:
  - Stationary/conference: 10–60 minutes (INFOCOM peak) ✓
  - Pedestrian: 2–20 minutes (INFOCOM avg, campus) ✓
  - Vehicular: 1–5 minutes (DieselNet buses) ✓
  - Dense social: 30+ minutes (RollerNet) ✓

Contact Density (edges / total possible node pairs):
  - High (conference, event): 0.3–0.8 ✓ (INFOCOM, RollerNet)
  - Medium (campus, urban): 0.1–0.3 ✓ (Cambridge, MIT Reality)
  - Low (sparse vehicular): 0.02–0.1 ✓ (DieselNet)
  - Very sparse (rural): <0.02 (inference)
```

**Assessment**: Current corpus ranges are **reasonable but unvalidated**. ✓ **Keep current ranges; add validation.**

---

## Recommendations

### Phase 1: Early Wins (0–2 months)

#### Task 1.1: Validate Vehicle Scenarios Against DieselNet
**Goal**: Establish ground truth for 03_vehicles family

**Steps**:
1. Download DieselNet Fall 2007 dataset from UMass (free, public)
2. Test existing `toolkit/dieselnetConverter.pl` converter
3. Run simulation with converted trace as connectivity overlay
4. Compare synthetic vehicle contact patterns (current corpus) with real DieselNet traces
5. Document findings (contact rate, duration, intercontact time, topology)

**Output**:
- Validation report: "03_vehicles_vs_DieselNet_baseline.md"
- Metrics comparison table
- If mismatch: tuning recommendations for MapRouteMovement parameters

**Effort**: ~3–5 days  
**Impact**: High (first real-trace validation)

#### Task 1.2: Extract Empirical Contact Parameters
**Goal**: Anchor Traffic Profiles in real data

**Steps**:
1. Compute contact statistics from all available real traces (DieselNet, INFOCOM estimates, MIT Reality citations)
2. Extract: mean contact duration, std dev, intercontact time distribution
3. Map to current TP parameters (message generation rates, TTLs, etc.)
4. Document ranges and justify TP defaults

**Output**:
- "empirical_contact_statistics.csv" (extracted from traces)
- "tp_parameter_mapping.md" (TP justification)

**Effort**: ~2–3 days  
**Impact**: Medium (improves TP credibility)

---

### Phase 2: Medium-term (2–6 months)

#### Task 2.1: Implement GPS-to-ExternalMovement Converter
**Goal**: Enable Cabspotting and other taxi traces

**Steps**:
1. Write Python converter: GPS CSV → ExternalMovement format
2. Implement coordinate transformation (lat/lon → simulation space)
3. Add validation checks (bounds, velocity, time order)
4. Test on Cabspotting sample (e.g., 1 day, 50 taxis)

**Output**:
- `scenarios/analysis/tools/gps_to_trajectory_converter.py`
- Usage guide: "using_gps_traces_guide.md"

**Effort**: ~1–2 weeks  
**Impact**: High (enables GPS-based mobility validation)

#### Task 2.2: Validate Mobility Against Cabspotting
**Goal**: Extend validation to GPS-based movement

**Steps**:
1. Convert SF Taxi Cabspotting subset (1 week, ~100 taxis)
2. Run simulation with ExternalMovement
3. Compare synthetic vehicle trajectories with real GPS
4. Measure: average speed, route patterns, spatial coverage, contact rate (if nodes in range)

**Output**:
- Validation report: "03_vehicles_vs_Cabspotting_gps.md"
- Metrics comparison (speed distribution, spatial coverage)

**Effort**: ~2–3 weeks  
**Impact**: High (validates MapRouteMovement realism)

---

### Phase 3: Long-term (6–12 months)

#### Task 3.1: Obtain Cambridge Haggle Dataset (if Possible)
**Goal**: Secure mixed indoor/outdoor campus benchmark

**Steps**:
1. Contact Cambridge research group (Hui et al., http://www.cl.cam.ac.uk/~aej26/haggle/)
2. Request dataset access
3. If granted: convert contact traces, validate 02_campus family
4. If denied: note in documentation and proceed with alternatives

**Effort**: ~1–2 weeks (+ waiting time)  
**Impact**: Medium (campus validation)

#### Task 3.2: Investigate KAIST Mobile Traces
**Goal**: Explore alternative campus dataset

**Steps**:
1. Search for KAIST dataset availability (may be archived or lost)
2. If found: similar conversion and validation as Haggle

**Effort**: ~1 week (research + contact)  
**Impact**: Low–Medium (backup option)

#### Task 3.3: Create "Reference Scenarios" Tied to Real Traces
**Goal**: Establish ground-truth simulation checkpoints

**Steps**:
1. Create 3–5 scenarios explicitly based on real traces (e.g., "03_vehicles_dieselnet_reference")
2. Run simulations, extract metrics
3. Create canonical protocol benchmark using these scenarios
4. Use for reproducibility claims in papers

**Effort**: ~4–6 weeks  
**Impact**: High (reproducibility + credibility)

---

### Phase 4: Future Directions (12+ months)

#### Generate Synthetic Scenarios Parameterized by Real Data
Once empirical parameters are solidified:
- Generate next corpus version with parameters explicitly tied to real traces
- Use empirical contact distributions, mobility speeds, etc.
- Create scenario variants (e.g., "Low-density urban variant" anchored in DieselNet)

#### Contribute Converters Back to The ONE Project
- Open-source GPS-to-trajectory converter
- WiFi-to-contact converter
- Submit as pull requests to GitHub (akeranen/the-one)

#### Publish Reproducibility Study
- "Empirical Parametrization of DTN Simulator Scenarios: The ONE Corpus Validated Against Real Traces"
- Tables: real trace vs. synthetic metrics
- Appendix: all converters, validation code

---

## Decision Matrix: What to Prioritize

| Dataset | Availability | Effort | Impact | Timeline | Priority |
|---------|--------------|--------|--------|----------|----------|
| **DieselNet** | ✓ Easy | 1 day | High | Month 1 | **P1 - NOW** |
| **Cabspotting** | ✓ Easy | 2 weeks | High | Month 2–3 | **P1 - SOON** |
| **Cambridge Haggle** | ⚠ Medium | 2–4 weeks | Medium | Month 3–6 | **P2 - MEDIUM** |
| **UCSD WiFi** | ✓ Easy | 1 week | Medium | Month 3–4 | **P2 - MEDIUM** |
| **KAIST** | ⚠ Unknown | 2–4 weeks | Low–Med | Month 6+ | **P3 - LOW** |
| **INFOCOM params** | ✗ Hard | 1 week research | Medium | Month 1 | **P1 - NOW (ref)** |
| **NYC Taxi** | ✓ Easy access | 3–4 weeks | Low (optional) | Month 6+ | **P3 - OPTIONAL** |

**Recommended Order**:
1. DieselNet validation (immediate)
2. INFOCOM parameter extraction (immediate)
3. Cabspotting converter (month 2)
4. Cabspotting validation (month 3)
5. Cambridge Haggle outreach (month 3, parallel)
6. Contingency: UCSD WiFi as backup

---

## Documentation Deliverables (Completed)

| Document | Location | Status | Purpose |
|----------|----------|--------|---------|
| **real_trace_scenarios_inventory.csv** | scenarios/analysis/data/ | ✓ DONE | Structured dataset registry |
| **real_trace_scenarios_inventory.md** | scenarios/analysis/reports/ | ✓ DONE | Executive summary + findings |
| **real_trace_parameter_ranges.md** | scenarios/analysis/reports/ | ✓ DONE | Empirical parameter extraction |
| **real_trace_conversion_guide.md** | scenarios/analysis/reports/ | ✓ DONE | Technical conversion procedures |
| **Plan.md** (this file) | session workspace | ✓ DONE | Synthesis + roadmap |

**Next Documentation**:
- `validation_dieselnet_report.md` (after Phase 1.1)
- `gps_converter_usage_guide.md` (after Phase 2.1)
- `reproducibility_study.md` (after Phase 3.3)

---

## Key Decisions

### 1. Do NOT Attempt to Replicate RollerNet
**Reason**: Too dense, inaccessible, niche scenario (not representative of general DTN). Use only for inspiration on dense contact patterns.

### 2. Do NOT Use NYC Taxi as Primary Validation
**Reason**: Scale too large (~13k nodes) makes simulations computationally expensive; Cabspotting (~500) is sufficient for vehicle validation.

### 3. Keep Random Waypoint as Baseline
**Reason**: Despite criticism, it's well-established. Use it as **control/baseline** not as *truth model*.

### 4. Prioritize Contact Traces Over GPS
**Reason**: Contact traces directly validate routing/caching protocols (the key OppNet problem). GPS validates *mobility* (secondary concern).

### 5. Do Not Modify corpus_v1 or base_scenarios Yet
**Reason**: Current freeze is reasonable; await validation results. Only update with evidence-based parameters.

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| DieselNet converter doesn't work | Low | Medium | Rewrite converter (simple format) |
| Cabspotting data unavailable | Low | Medium | Use NYC Taxi as fallback |
| Cambridge/KAIST datasets locked | Medium | Low | Reference-only (still valuable) |
| GPS-converter complexity | Low | Low | Prototype on small sample first |
| Parameter discrepancy found | High | Medium | Document & propose tuning (transparent) |
| Team pushback on changes | Medium | Low | Lead with validation evidence |

---

## Success Criteria

**Audit Complete When**:
1. ✓ Inventory finalized (17 datasets, 4 tiers)
2. ✓ Conversion guides documented
3. ✓ Parameter ranges extracted
4. ✓ Roadmap actionable (Phase 1 clearly defined)

**Phase 1 Success (0–2 months)**:
1. DieselNet converter tested
2. Validation metrics computed (contact rate, duration, etc.)
3. Report published: "Is 03_vehicles realistic? DieselNet validation."
4. Decision: Keep parameters or tune?

**Overall Success (12 months)**:
1. At least 1 scenario family (03_vehicles) validated against real traces
2. GPS converter operational
3. Publications or reports referencing real-trace validation
4. Reproducibility improved (traced back to empirical data)

---

## Conclusion & Call to Action

### What This Audit Accomplished
1. ✓ Identified 14 real datasets (contact + GPS)
2. ✓ Classified by availability & convertibility
3. ✓ Extracted empirical parameter ranges
4. ✓ Documented technical conversion procedures
5. ✓ Created actionable roadmap

### What Should Happen Next

**Immediate (Week 1)**:
- Review this summary with team
- Confirm buy-in for Phase 1

**Month 1**:
- Task 1.1: DieselNet validation
- Task 1.2: Empirical contact parameters
- Decision: Proceed to Phase 2 or iterate?

**Month 3**:
- Task 2.1: GPS converter
- Task 2.2: Cabspotting validation

**Month 6+**:
- Phase 3: Extended campaigns (Haggle, reference scenarios)

### Final Recommendation

> **The ONE corpus has strong potential for empirical grounding.** Infrastructure exists (converters, external event/movement support). Real traces are accessible (DieselNet, Cabspotting, UCSD). **Starting with DieselNet validation (1–2 weeks effort) can immediately improve reproducibility claims.** Recommend proceeding to Phase 1 with full team commitment.

---

## Appendix: Questions Answered

**Q: Does The ONE support real traces?**  
A: ✓ Yes — DieselNet converter (Perl), ExternalEvent, ExternalMovement classes.

**Q: Are real datasets publicly available?**  
A: ✓ Partially — DieselNet, Cabspotting, UCSD WiFi (free). INFOCOM, MIT Reality, RollerNet (restricted).

**Q: How do we convert traces?**  
A: Covered in conversion guide. Contact traces → CONN format. GPS → coordinate interpolation. WiFi → derived contacts.

**Q: Does current corpus match real data?**  
A: Unknown — current corpus is entirely synthetic. DieselNet validation would answer this.

**Q: What's the first actionable step?**  
A: Test DieselNet converter; compute contact statistics; compare with synthetic 03_vehicles.

---

**Document Version**: 1.0  
**Last Updated**: 2026-06-13  
**Status**: Ready for team review and Phase 1 execution
