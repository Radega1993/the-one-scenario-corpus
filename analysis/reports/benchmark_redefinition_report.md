# Benchmark definition (active)

**Active benchmark:** `corpus_v1` — **540** scenarios (45 environmental bases × 12 traffic profiles TP01–TP12) across six families (`01_urban` … `06_social`).

| Tier | Families | Scenarios |
|------|----------|----------:|
| Environmental core | `01_urban`–`06_social` | **540** |
| Structural bases (no TP) | same six families | **45** |

**Official active total: 540** routing scenarios in `corpus_v1/` for simulation and analysis.

## Design

- **One map per environmental family** — topology held constant within family.
- **Traffic profiles (TP01–TP12)** — application-layer workload applied on top of mobility bases.
- **Protocol overlays** — routing and report configuration applied at experiment time, not baked into corpus `.settings`.

Historical notes on retired layouts (`corpus_v2`, 720 scenarios, separate stress laboratories) live under `scenarios/_archive/` only.

See also: `scenarios/corpus_v1/README.md`, `scenarios/analysis/data/benchmark_definition.csv`, `scenarios/analysis/reports/canonical/corpus_benchmark_validation.md`.
