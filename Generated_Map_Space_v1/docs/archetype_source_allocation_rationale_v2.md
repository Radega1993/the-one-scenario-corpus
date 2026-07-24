# Archetype × source allocation rationale (v2)

**Config:** [`../config/archetype_source_allocation_v2.yaml`](../config/archetype_source_allocation_v2.yaml)  
**CSV:** [`../data/archetype_source_allocation_v2.csv`](../data/archetype_source_allocation_v2.csv)

## Why a matrix (not only global quotas)

Global fractions OSM 0.45 / synthetic 0.40 / TRS 0.15 are **soft engineering targets**. Scientific balance is per-archetype: some archetypes are OSM-only (`compact_residential`, `suburban_low_density`), some synthetic-only (`radial_city`, `hub_and_spoke`), some TRS-primary (`conference_event_compact`, `clustered_communities`).

The planner **must not** emit `source_type` with role `none` for an archetype. Primary sources are filled first for that archetype; supporting/optional fill remaining soft slots.

## Fixed examples (from plan)

| Archetype | Primary | Supporting / optional | None |
|-----------|---------|----------------------|------|
| `radial_city` | synthetic | — | OSM, TRS |
| `conference_event_compact` | TRS | synthetic; OSM optional | — |
| `clustered_communities` | TRS | synthetic; OSM optional | — |
| `urban_grid` | OSM | synthetic | TRS |
| `dense_urban_irregular` | OSM | synthetic | TRS |
| `bus_route_urban_suburban` | OSM | synthetic | TRS (DieselNet/Rio are OSM support, not TRS maps) |

## Soft global fractions

Matrix-implied mass (if every archetype met only its primary mins) is OSM-heavy. Soft targets 0.45/0.40/0.15 remain as engineering fill preferences **after** matrix constraints, checked in plan validation as INFO/HIGH warnings — not as a methodological stopping rule and not as a reason to violate `none`.

## Relation to N=1200

`target_total_default: 1200` is an **initial engineering target** (inherited from baseline). Final corpus size is deferred to incremental saturation (ladder includes 1600/2000). See `map_generation_v2_methodological_readiness.md`.
