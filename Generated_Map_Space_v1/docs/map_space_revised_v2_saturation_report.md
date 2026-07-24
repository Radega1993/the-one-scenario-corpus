# Stratified saturation report — map_space_revised_v2

**Role:** empirical saturation analysis under a pre-registered protocol.
**GMS-v1:** not closed unless decision is STOP.
**SMS-v1:** blocked until GMS freeze.

- Pool OK maps analysed: **1860**
- Permutations R: **100** (stratified nested round-robin)
- Geometry dims: **33** (no source_type one-hot)
- ε (20th pct of 5-NN distances on full pool): **0.356622**
- Decision: **`STOP_AMENDED_CEILING_2000`** (amended STOP; original preserved as `CEILING_2000_NO_STOP`)

## Protocol (frozen)

- Config: `scenarios/Generated_Map_Space_v1/config/saturation_protocol.yaml`
- Freeze: `scenarios/Generated_Map_Space_v1/data/map_space_revised_v2_pool_freeze.json`
- Transform: `scenarios/Generated_Map_Space_v1/data/map_space_revised_v2_feature_transform_freeze_n1117.json` (applied; ε recomputed on current pool)
- Figures: `scenarios/Generated_Map_Space_v1/figures/saturation/`

## Primary curves (median over R; bands Q2.5–Q97.5)

| N | C(ε) med | C q025 | C q975 | D95 med | ΔC^(100) med | n_arch med | n_cells med |
|--:|---------:|-------:|-------:|--------:|-------------:|-----------:|------------:|
| 100 | 0.1707 | 0.1554 | 0.1858 | 12.6239 | nan | 15.0 | 31.0 |
| 200 | 0.2804 | 0.2618 | 0.3003 | 7.9128 | 0.1097 | 15.0 | 31.0 |
| 300 | 0.3691 | 0.3518 | 0.3911 | 5.1848 | 0.0895 | 15.0 | 31.0 |
| 400 | 0.4457 | 0.4268 | 0.4629 | 3.6307 | 0.0742 | 15.0 | 31.0 |
| 500 | 0.5129 | 0.4946 | 0.5280 | 2.9053 | 0.0667 | 15.0 | 31.0 |
| 600 | 0.5696 | 0.5551 | 0.5871 | 2.3182 | 0.0565 | 15.0 | 31.0 |
| 700 | 0.6247 | 0.6094 | 0.6401 | 1.9449 | 0.0548 | 15.0 | 31.0 |
| 800 | 0.6731 | 0.6569 | 0.6866 | 1.7339 | 0.0478 | 15.0 | 31.0 |
| 900 | 0.7175 | 0.7013 | 0.7326 | 1.5301 | 0.0435 | 15.0 | 31.0 |
| 1000 | 0.7581 | 0.7462 | 0.7740 | 1.3765 | 0.0414 | 15.0 | 31.0 |
| 1100 | 0.7995 | 0.7839 | 0.8132 | 1.1944 | 0.0401 | 15.0 | 31.0 |
| 1200 | 0.8360 | 0.8231 | 0.8473 | 1.0686 | 0.0360 | 15.0 | 31.0 |
| 1300 | 0.8694 | 0.8591 | 0.8793 | 0.9014 | 0.0339 | 15.0 | 31.0 |
| 1400 | 0.8992 | 0.8892 | 0.9092 | 0.6593 | 0.0296 | 15.0 | 31.0 |
| 1500 | 0.9309 | 0.9242 | 0.9411 | 0.4570 | 0.0323 | 15.0 | 31.0 |
| 1600 | 0.9608 | 0.9527 | 0.9667 | 0.2766 | 0.0277 | 15.0 | 31.0 |
| 1700 | 0.9796 | 0.9744 | 0.9847 | 0.1229 | 0.0188 | 15.0 | 31.0 |
| 1800 | 0.9957 | 0.9927 | 0.9984 | 0.0000 | 0.0164 | 15.0 | 31.0 |
| 1860 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0072 | 15.0 | 31.0 |

Categorical coverage (archetypes/cells) is a **design condition**, not primary saturation evidence.

## Audit order (batch_target → map_id) — not primary

| N | C(ε) | D95 | n_arch | n_cells |
|--:|-----:|----:|-------:|--------:|
| 100 | 0.2312 | 44.1438 | 14 | 26 |
| 200 | 0.3425 | 44.1438 | 14 | 26 |
| 300 | 0.4097 | 44.1438 | 14 | 26 |
| 400 | 0.4597 | 44.1438 | 14 | 26 |
| 500 | 0.4737 | 44.1438 | 14 | 26 |
| 600 | 0.4833 | 44.1438 | 14 | 26 |
| 700 | 0.4898 | 44.1438 | 14 | 26 |
| 800 | 0.4941 | 44.1438 | 14 | 26 |
| 900 | 0.5382 | 21.3720 | 14 | 26 |
| 1000 | 0.5710 | 16.4147 | 14 | 26 |
| 1100 | 0.6145 | 16.2072 | 14 | 26 |
| 1200 | 0.6651 | 15.1250 | 14 | 28 |
| 1300 | 0.7419 | 7.0903 | 14 | 29 |
| 1400 | 0.8231 | 3.6644 | 14 | 29 |
| 1500 | 0.8790 | 1.4050 | 15 | 31 |
| 1600 | 0.9145 | 0.7331 | 15 | 31 |
| 1700 | 0.9441 | 0.4819 | 15 | 31 |
| 1800 | 0.9747 | 0.0000 | 15 | 31 |
| 1860 | 1.0000 | 0.0000 | 15 | 31 |

## Decision

**`STOP_AMENDED_CEILING_2000`** — Amended STOP met for 2 consecutive ladder steps ending at N=1860 (D95 floor / tail ΔC / short-step raw ΔC). No hot critical strata. See scenarios/Generated_Map_Space_v1/docs/stop_diagnostics_ceiling_2000.md.

- gms_status: `freeze_candidate`
- sms_status: `unblocked_after_gms_freeze`
- stop_at_N: `1860`
- prior (pre-amendment): `CEILING_2000_NO_STOP` → [`map_space_revised_v2_saturation_decision_ceiling_no_stop.json`](../data/map_space_revised_v2_saturation_decision_ceiling_no_stop.json)
- diagnostics: [`stop_diagnostics_ceiling_2000.md`](stop_diagnostics_ceiling_2000.md)
- amendment: [`saturation_protocol_amendment_ceiling_2000.yaml`](../config/saturation_protocol_amendment_ceiling_2000.yaml)

Defendable closure language (amended STOP / freeze candidate):

> The configured map-generation design space reached empirical saturation under the declared generator families, parameter ranges, source allocation policy, feature representation, and operational stopping criteria.


## Deferred

- PCA as primary deliverable
- Separability analysis
- Actual expansion execution (recommendation only in decision.json)
- SMS-v1 selection

