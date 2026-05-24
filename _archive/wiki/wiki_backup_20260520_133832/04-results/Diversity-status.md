# Diversity status

**English** | [Español](Diversity-status-es)

---

Current status of **diversity criteria** and actions taken. Diversity is evaluated in the **core 23** feature space (see [Features reference](../03-reference/Features-reference) for why 23 core and why others are discarded).

---

## Criteria (reminder)

- **|r| < 0.7** for ≥95% of pairs (Pearson on **core 23** feature vectors).
- **Minimum cosine distance** (no almost-identical pairs).
- **Silhouette > 0.3** (Ward k=7).

---

## Current status — final optimized freeze (60 scenarios)

| Criterion | Value |
|-----------|--------|
| Pairs with \|r\| ≥ 0.7 | **58 (3.3%)** |
| Pairs with \|r\| < 0.7 | **96.7%** |
| max \|r\| | **0.9829** |
| Min cosine distance | **0.0152** |
| Silhouette (k=7) | **0.2681** |

Space 46: 46 pairs (2.6%) with \|r\| ≥ 0.7; max \|r\| 0.9377; min cosine 0.0620; silhouette 0.2929. Ablation: `analysis/reports/ablation_report.txt`.

---

## Baseline initial vs final optimized

- Core-23 high-correlation pairs: `93 -> 58`.
- Full-46 high-correlation pairs: `57 -> 46`.
- Full-46 silhouette: `0.2924 -> 0.2929`.
- Full-46 min cosine: `0.0585 -> 0.0620`.

---

## Declared limitations

- Residual high-correlation pairs remain.
- Core-23 silhouette is moderate in final freeze (`0.2681`).
- One strong residual feature dependency remains: `mm_WDM <-> mm_Bus = 0.9393`.

---

## Pairs that are too correlated (core 23)

Full list: **`analysis/reports/correlation_core23_report.txt`**. Scenarios to prioritise for diversification: **`analysis/reports/scenarios_to_diversify_core23.txt`**.

---

## Scenarios to diversify / decisions made

- **List:** `analysis/reports/scenarios_to_diversify_core23.txt` (priority by core-23 high-|r| pairs).
- **Diversification** = modifying `.settings` (speed, waitTime, transmitRange, workDayLength, TTL, buffer, nrOfOffices, nrOfMeetingSpots, etc.) to move the scenario away in **core 23** space.
- Current framing: **freeze with declared limitations**. This is a publishable baseline, not an optimal final corpus.

---

## See also

- [Results overview](Results-overview) — Full correlation and distance numbers  
- [Methodology](Methodology) — Diversity criteria  
- [Corpus overview](Corpus-overview) — Families and design  
