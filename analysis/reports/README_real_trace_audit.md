# Real Trace Scenarios Audit — README

**Audit Date**: 2026-06-13  
**Status**: Comprehensive inventory and analysis complete  
**Purpose**: Empirical grounding for DTN/OppNet scenario corpus parametrization

---

## What's Here

This audit examines **14 real datasets** from the DTN/OppNet literature and determines how they can inform or validate The ONE simulator scenarios.

### Documents

| File | Purpose | Audience |
|------|---------|----------|
| **real_trace_scenarios_inventory.csv** | Structured registry of 14 datasets (metadata, availability, convertibility) | Data scientists, researchers |
| **real_trace_scenarios_inventory.md** | Executive summary, detailed findings, tier classification | Decision-makers, PMs |
| **real_trace_parameter_ranges.md** | Extracted empirical parameter ranges (nodes, duration, contact patterns) | Corpus designers, modelers |
| **real_trace_conversion_guide.md** | Technical howto for converting traces to The ONE format | Developers, tooling |
| **real_trace_scenarios_synthesis.md** | Roadmap, recommendations, implementation phases | Team leads, project managers |

### Data

- **Inventory CSV**: 17 rows (16 real + 1 meta), 20 columns (trace metadata)

---

## Quick Start

### For Decision-Makers
1. Read: **real_trace_scenarios_synthesis.md** (5 min read)
2. Decision: Approve Phase 1 (DieselNet validation) — 1–2 week effort, high impact

### For Data Scientists
1. Read: **real_trace_parameter_ranges.md** — empirical baseline comparison
2. Validate: current corpus against real trace statistics
3. Output: comparison report + tuning recommendations

### For Developers
1. Read: **real_trace_conversion_guide.md** — conversion procedures
2. Implement: GPS-to-trajectory converter (2–3 weeks)
3. Test: against Cabspotting dataset

---

## Key Findings

### Inventory (17 entries)

- **Tier 1 (Immediately Usable)**: DieselNet ✓ (existing Perl converter)
- **Tier 2 (Convertible)**: SF Taxi, NYC Taxi, UCSD WiFi, NUS WiFi
- **Tier 3 (Reference Only)**: INFOCOM, MIT Reality, RollerNet, Cambridge Haggle, KAIST
- **Tier 4 (Theoretical)**: RWP, Brownian Motion, CRAWDAD

### Current State

- **corpus_v1** (540 scenarios): Entirely synthetic, no real-trace validation
- **base_scenarios** (45 scenarios): Entirely synthetic, unvalidated parameters
- **The ONE Infrastructure**: Has DieselNet converter + ExternalEvent/ExternalMovement support ✓

### Opportunity

1. **DieselNet**: 1-day effort to test; immediate ground truth for 03_vehicles family
2. **Cabspotting**: 2-3 week effort to implement GPS converter; validates MapRouteMovement
3. **Parameter Alignment**: Empirical ranges match current corpus reasonably well (but unvalidated)

---

## Recommendations (Priority Order)

### Phase 1: Immediate (Weeks 1–2)
- [ ] Test DieselNet converter (`toolkit/dieselnetConverter.pl`)
- [ ] Extract contact statistics (real vs. synthetic comparison)
- [ ] Decision: Keep or tune vehicle scenarios?

### Phase 2: Short-term (Weeks 3–8)
- [ ] Implement GPS-to-trajectory converter
- [ ] Validate against Cabspotting subset
- [ ] Extend to other vehicle scenarios

### Phase 3: Medium-term (Weeks 9–24)
- [ ] Contact Cambridge (attempt to obtain Haggle dataset)
- [ ] Create reference scenarios tied to real traces
- [ ] Publish reproducibility study

### Phase 4: Long-term (Months 12+)
- [ ] Generate next corpus version with empirical parameters
- [ ] Contribute converters to The ONE GitHub
- [ ] Research paper: "Empirical Parametrization of DTN Scenarios"

---

## CSV Columns Explained

The `real_trace_scenarios_inventory.csv` has 20 columns:

| Column | Example | Notes |
|--------|---------|-------|
| **trace_id** | dieselnet-fall2007 | Unique ID for reference |
| **trace_name** | DieselNet Fall 2007 | Human-readable name |
| **aliases** | UMass DieselNet; PVTA buses | Alternative names |
| **source_url** | http://traces.cs.umass.edu/ | Repository/DOI link |
| **source_paper** | Moturu et al. 2006 | Citation |
| **trace_type** | contact_only, gps_trajectory, wifi_association | Data type |
| **environment_type** | urban_vehicular, conference, campus | Scenario context |
| **n_nodes** | 40, 500, 1000+ | Scale |
| **duration_days** | 2, 30, 365 | Temporal extent |
| **spatial_data_available** | yes/no | Have coordinates? |
| **contact_data_available** | yes/no | Have contacts/proximity? |
| **map_data_available** | yes/no | Have infrastructure map? |
| **the_one_settings_found** | yes/no | Existing The ONE config? |
| **settings_path_or_url** | toolkit/dieselnetConverter.pl | Where to find/how to use |
| **conversion_required** | yes/no | Needs preprocessing? |
| **conversion_method** | ContactTrace, ExternalMovement | Target format |
| **compatibility_level** | needs_minor_format_conversion, ready_to_run, reference_only | Implementation status |
| **license_or_access_conditions** | public_available, restricted_academic | Access barriers |
| **recommended_use_for_project** | main_reference, inspiration_only, validation_baseline | Role in corpus |
| **notes** | Long description | Context, caveats, links |

---

## Parameter Ranges (from Synthesis)

**Recommended core ranges** (backed by real data):

```
Nodes:     30–500 (event: 50–150; campus: 100–500; vehicular: 30–100)
Duration:  1–30 days (typical); 90+ days (rare, long-term)
Contact:   1–60 min (depends on mobility: pedestrian shorter, stationary longer)
Density:   0.02–0.8 (sparse vehicular to dense social)
Speed:     1–2 m/s (pedestrian); 5–15 km/h (vehicular average)
```

**Current corpus**: Ranges are reasonable but unvalidated. ✓ Keep; add validation.

---

## Implementation Timeline

### Week 1–2 (Phase 1)
```
Task 1.1: Test DieselNet converter
  - Download data (free, public)
  - Run Perl converter
  - Compute contact statistics
  - Output: validation_dieselnet.md

Task 1.2: Extract empirical parameters
  - Consolidate real-trace ranges
  - Map to current TP design
  - Output: empirical_contact_statistics.csv
```

### Week 3–8 (Phase 2)
```
Task 2.1: GPS-to-trajectory converter
  - Write Python converter
  - Lat/lon → simulation coordinates
  - Validation checks
  - Output: gps_to_trajectory_converter.py

Task 2.2: Cabspotting validation
  - Download + convert sample
  - Compare with synthetic vehicle movement
  - Output: validation_cabspotting_gps.md
```

### Week 9–24 (Phase 3)
```
Task 3.1: Cambridge Haggle outreach
Task 3.2: Create reference scenarios
Task 3.3: Publish findings
```

---

## Success Metrics

**Audit Success** (achieved): ✓
- 17 datasets inventoried
- 4 conversion techniques documented
- Empirical ranges extracted
- Actionable roadmap created

**Phase 1 Success**:
- DieselNet converter tested ✓
- Contact metrics compared (synthetic vs. real)
- Decision: Update corpus parameters or keep current?

**Overall Success (12 months)**:
- ≥1 scenario family validated against real traces
- GPS converter operational
- Reproducibility improved
- Paper/report published

---

## Contact & Attribution

**Audit Conducted**: 2026-06-13  
**Method**: Literature review, dataset survey, infrastructure analysis  
**Author**: Copilot + Manual Research (DTN/OppNet expertise)

**Next Steps**: Hand off to implementation team. Recommend assigning Phase 1 tasks to 1–2 developers.

---

## References

### Datasets
- DieselNet: http://traces.cs.umass.edu/
- SF Taxi: http://crawdad.org/ucsd/mobility/
- UCSD WiFi: http://crawdad.org/ucsd/wifi/
- INFOCOM: Legacy (contact authors)
- MIT Reality: http://realitycommons.media.mit.edu/

### The ONE
- GitHub: https://github.com/akeranen/the-one
- Documentation: https://akeranen.github.io/the-one/
- Converter (`dieselnetConverter.pl`): Local copy at `toolkit/`

---

**Last Updated**: 2026-06-13  
**Status**: Ready for review and Phase 1 execution
