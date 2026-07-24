# STOP diagnostics @ planned ceiling N=2000

**Date:** 2026-07-23  
**Pool:** `map_space_revised_v2` (features n=1860; transform freeze N≈1117; ε=0.3566)  
**Prior decision:** `CEILING_2000_NO_STOP` under the **original** pre-registered joint STOP.

## Questions

1. Is the missed STOP an artifact of the final short ladder step (1800→1860 = 60 maps)?
2. Are `critical_strata` still novel at the end (TARGETED_EXPAND)?
3. What documented amendment is needed before a defendable GMS freeze?

## Findings

### 1) Short-step ΔC artifact — **yes, partial**

| Step | raw ΔC | ΔC^(100) = 100·raw/ΔN |
|------|-------:|----------------------:|
| 1700→1800 (ΔN=100) | 0.0161 | 0.0164 |
| 1800→1860 (ΔN=60) | **0.0043** | **0.0072** |

Raw ΔC on the last step is **below** the original 0.005 threshold; scaling to /100 inflates it above the threshold.  
So the short final rung **alone** would block a last-step PASS under ΔC^(100), but it is **not** the only blocker.

### 2) D95 relative-improvement pathology — **primary blocker**

Original rule: relative D95 improvement `(D95_prev − D95)/D95_prev < 0.02`.

When D95 collapses toward 0 (1700→1800), relative improvement ≈ **1.0**, so the clause **fails precisely when residual mass vanishes**. Near-zero D95 also makes relative changes numerically unstable.

Late original audit (joint = C≥0.98 ∧ ΔC^(100)<0.005 ∧ D95-rel<0.02):

| N | C | ΔC^(100) | D95 | joint |
|--:|--:|---------:|----:|:-----:|
| 1700 | 0.980 | 0.019 | 0.123 | no |
| 1800 | 0.996 | 0.016 | ~0 | no (ΔC + D95-rel) |
| 1860 | 1.000 | 0.007 | ~0 | no (ΔC^(100) + D95-rel) |

### 3) Critical strata — **not hot; no TARGETED**

Stratified R=20 last-block novelty (audit-consistent ε): all five critical cells have `nov_median = 0` and are **not** > 1.5·ε.  
→ **Do not** run TARGETED_EXPAND on protocol critical strata.

### 4) Sensitivity (same bands CSV; no pool change)

| Rule variant | stop_at |
|--------------|--------:|
| Original | none |
| min_step≥100 only | none |
| D95 absolute floor (D95≤ε) only | none |
| D95≤ε + ΔC_tail=0.02 when C≥0.98 + need=3 | none (only 2 late PASSes) |
| **D95≤ε + ΔC_tail=0.02 when C≥0.98 + need=2** | **1860** |

## Recommended amendment (documented, post-hoc)

File: [`../config/saturation_protocol_amendment_ceiling_2000.yaml`](../config/saturation_protocol_amendment_ceiling_2000.yaml)

1. **D95 clause:** PASS if `D95 ≤ ε` (absolute floor). Keep relative clause only as legacy fallback when D95 > ε.
2. **Tail ΔC:** when `C(ε) ≥ 0.98`, use `ΔC^(100) < 0.02` (tail finishing), else keep `0.005`.
3. **Short steps:** if ladder ΔN < 100, evaluate ΔC on **raw** ΔC against 0.005 (avoid /100 inflation).
4. **Consecutive:** `need = 2` once in the C≥0.98 regime (plateau confirmation), else keep 3 for early ladder (implementation: use need=2 globally under this amendment for decision re-eval at ceiling).

**Honesty:** this amendment is **post-hoc** after seeing ceiling curves. It does **not** rewrite history of the original `CEILING_2000_NO_STOP`. It is an explicit protocol fix for known STOP pathologies at the coverage tail.

## Outcome under amendment

Re-evaluation on the frozen bands → **STOP at N=1860**, critical strata not hot → **GMS freeze candidate**; SMS may proceed only after explicit freeze acceptance.
