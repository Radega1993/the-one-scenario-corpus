# Diversity status

**English** | [Español](Diversity-status-es)

---

Current status of **diversity criteria** and actions taken to reduce correlation between scenarios.

---

## Criteria (reminder)

- **|r| < 0.7** for ≥95% of pairs (Pearson on feature vectors).
- **Minimum cosine distance > 0.05** (no almost-identical pairs).
- **No pair with cos_dist < 0.05** ✓ (currently 0).
- **Silhouette > 0.3** (optional; current 0.00).

---

## Current status

| Criterion | Status |
|-----------|--------|
| Pairs with \|r\| < 0.7 | 93.7% (target ≥95%) — **not met** |
| Pairs with cos_dist < 0.05 | 0 ✓ |
| Min cosine distance | 0.0534 > 0.05 ✓ |

---

## Pairs that are too correlated

There are **153 pairs** with |r| ≥ 0.7. Examples (see full list in `analysis/reports/correlation_report.txt`):

- V4_MixedBusPed ↔ V5_RushHourBusDensity (r = 0.9475)
- U3_NightlifeClusters ↔ C5_Festival_MultiHotspots (r = 0.9420)
- T10_HighRateLowSpeed ↔ T15_TransmitSpeed_256k (r = 0.9397)
- … and 150 more.

---

## Scenarios to diversify / decisions made

- The list of scenarios that appear in high-|r| pairs or in dense clusters is in **`analysis/reports/scenarios_to_diversify.txt`**.
- **Diversification** = modifying `.settings` (speed, waitTime, transmitRange, workDayLength, TTL, buffer, nrOfOffices, nrOfMeetingSpots, etc.) to move the scenario away in feature space.
- **Radical scenarios** (R9–R12, T11–T15, D9, etc.) were added to increase diversity; clustering and pairwise diversification have been applied in previous steps (see [ROADMAP](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/ROADMAP.md)).

*(Update this section as new diversification steps are completed.)*

---

## See also

- [Results overview](Results-overview) — Full correlation and distance numbers  
- [Methodology](Methodology) — Diversity criteria  
- [Corpus overview](Corpus-overview) — Families and design  
