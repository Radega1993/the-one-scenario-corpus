# Traffic profile review

Aggregated over all 720 scenarios (12 TP × 60 bases).

| TP | mean delivery | std delivery | mean overhead | mean drops | n |
|----|--------------:|-------------:|--------------:|-----------:|--:|
| `TP01` | 0.2681 | 0.2971 | 119.2 | 9.2 | 60 |
| `TP02` | 0.2950 | 0.3222 | 139.0 | 22.0 | 60 |
| `TP03` | 0.2612 | 0.2868 | 57.0 | 4.7 | 60 |
| `TP04` | 0.1407 | 0.1594 | 838.6 | 97.4 | 60 |
| `TP05` | 0.0262 | 0.0837 | 42.6 | 2.1 | 60 |
| `TP06` | 0.2864 | 0.3052 | 75.0 | 16.7 | 60 |
| `TP07` | 0.3418 | 0.3519 | 108.5 | 14.4 | 60 |
| `TP08` | 0.2366 | 0.2641 | 181.2 | 27.5 | 60 |
| `TP09` | 0.2137 | 0.2369 | 275.7 | 64.1 | 60 |
| `TP10` | 0.0973 | 0.1763 | 91.5 | 12.4 | 60 |
| `TP11` | 0.3037 | 0.3094 | 55.8 | 5.4 | 60 |
| `TP12` | 0.2576 | 0.3086 | 82.5 | 17.5 | 60 |

## Differentiation

- Bases with delivery std < 0.02 across TP: **18** / 60 → flag `TP_NOT_DIFFERENTIATING`.
- **TP04_FewLarge** and **TP10_Storm** show highest overhead/drops variance; keep in **stress** split, not main benchmark.
- **TP12_GroupToGroup** intentionally zero cross-group delivery; label **diagnostic** / `STRUCTURAL_PARTITION_VALID`.
- v3 main benchmark should use **TP01–TP08** with verified std ≥ 0.05 per base after rebuild.
