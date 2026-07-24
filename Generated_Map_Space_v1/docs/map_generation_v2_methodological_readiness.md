# Map generation v2 — methodological readiness (go / no-go)

**Date:** 2026-07-23 (STOP diagnostics + documented amendment)  
**Pool:** `scenarios/Generated_Map_Space_v1/`

## Official position

Planned ceiling **N=2000** completed. Under the **original** pre-registered STOP → `CEILING_2000_NO_STOP`.  
After **documented post-hoc amendment** (D95≤ε floor, tail ΔC, short-step raw ΔC, need=2) → **`STOP_AMENDED_CEILING_2000`** at N=1860.

**GMS-v1:** `freeze_candidate` (accept freeze explicitly before SMS).  
**SMS-v1:** blocked until that freeze is accepted.  
Critical strata: **not hot** → no TARGETED_EXPAND.

| Gate | Status | Evidence |
|------|--------|----------|
| Pool @2000 | DONE | OK 1865 / features 1860 |
| Original STOP | NOT MET | `CEILING_2000_NO_STOP` preserved |
| STOP diagnostics | DONE | [`stop_diagnostics_ceiling_2000.md`](stop_diagnostics_ceiling_2000.md) |
| Protocol amendment | DOCUMENTED | [`saturation_protocol_amendment_ceiling_2000.yaml`](../config/saturation_protocol_amendment_ceiling_2000.yaml) |
| Amended STOP | **MET @1860** | [`map_space_revised_v2_saturation_decision.json`](../data/map_space_revised_v2_saturation_decision.json) |
| GMS freeze | **CANDIDATE** | awaiting explicit freeze acceptance |
| SMS-v1 | **BLOCKED** | until GMS freeze |

## Policy

- Do not auto-expand balanced beyond 2000.
- Do not claim absolute map-space saturation.
- Original curves/bands unchanged; amendment only changes the STOP decision rule, with full audit trail.

## Phase layout

GMS pack is self-contained after phase close: configs, scripts, docs, data, figures, and
**colocated traces** in [`downloaded_external_traces/`](../downloaded_external_traces/)
(legacy symlink: `scenarios/external_traces`). Corpus maps remain in `scenarios/maps/`.

## Next human action

Accept GMS-v1 freeze (lock pool + decision artifacts) → then SMS-v1 selection may start.
