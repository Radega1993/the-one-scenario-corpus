# Selected map space v1 — documentation update report

**Date:** June 2026  
**Objective:** Close Phase 2 (`selected_map_space_v1`) documentation and prepare transition to structural scenario generation.

---

## Files updated

| File | Path | Summary of changes |
|------|------|-------------------|
| Narrativa Fase 1 + transición | [`scenarios/internal/map_space_saturation_archetypes_and_results_v1.md`](../../internal/map_space_saturation_archetypes_and_results_v1.md) | §12.5 ampliado (tabla, cobertura, codo N=75, WKT copiados); §12.6 escenarios estructurales sin Traffic Profiles; §13 +6 informes Fase 2; pie actualizado |
| Inventario Fase 1 | [`scenarios/internal/map_generation_phase1_inventory_v1.md`](../../internal/map_generation_phase1_inventory_v1.md) | §6.3 con INDEX Fase 2 y descripciones spec; nueva §11 Estado posterior |
| Índice maestro Fase 1 | [`INDEX_MAP_GENERATION_PHASE1_FINAL.md`](INDEX_MAP_GENERATION_PHASE1_FINAL.md) | Sección Related phases; 6 informes Fase 2 en Reports; Next step alineado con manifest |
| Índice maestro Fase 2 | [`INDEX_SELECTED_MAP_SPACE_V1.md`](INDEX_SELECTED_MAP_SPACE_V1.md) | Reescrito como índice definitivo (secciones A–J): status, executive table, artefactos, scripts, datos, informes, 12 figuras, reproducción, claims, next phase |
| **Este informe** | `selected_map_space_v1_documentation_update.md` | Changelog de cierre documental |

---

## Route discrepancy (resolved)

The task specification cited:

```text
scenarios/analysis/docs/map_space_saturation_archetypes_and_results_v1.md
scenarios/analysis/docs/map_generation_phase1_inventory_v1.md
```

**Canonical location:** `scenarios/internal/` (not `scenarios/analysis/docs/`). All existing cross-links in the repo already point to `scenarios/internal/`. No file move was performed per user decision.

---

## Inconsistencies corrected

| Issue | Resolution |
|-------|------------|
| §12.5 Fase 2 demasiado breve | Expandido con tabla oficial, métricas de cobertura y nota CERRADA |
| §12.6 sin alcance de fase siguiente | Añadido diagrama, no Traffic Profiles, extract/validate/prune |
| §13 sin informes reviewer Fase 2 | Añadidos methodology, selection_report, reviewer_rationale, paper_ready, coverage |
| Inventario Fase 1 sin transición | §11 Estado posterior añadida |
| INDEX Fase 2 incompleto (~88 líneas) | Expandido a índice maestro A–J |
| INDEX Fase 1 sin Related phases | Tabla Phase 1 CLOSED / Phase 2 DONE añadida |

**Not changed (already correct):** canonical counts 13 generators, 19 anchors; no recalculation of metrics.

---

## Main links

| Resource | Path |
|----------|------|
| Phase 2 master index | [`INDEX_SELECTED_MAP_SPACE_V1.md`](INDEX_SELECTED_MAP_SPACE_V1.md) |
| Official manifest | [`scenarios/selected_map_space_v1/manifest_selected_maps.csv`](../../selected_map_space_v1/manifest_selected_maps.csv) |
| Decision JSON | [`selected_map_space_v1_decision.json`](../data/selected_map_space_v1_decision.json) |
| Phase 2 narrative (ES) | [`map_space_selection_methods_and_results_v1.md`](../../internal/map_space_selection_methods_and_results_v1.md) |
| Phase 2 inventory (ES) | [`map_generation_phase2_inventory_v1.md`](../../internal/map_generation_phase2_inventory_v1.md) |
| Phase 1 index | [`INDEX_MAP_GENERATION_PHASE1_FINAL.md`](INDEX_MAP_GENERATION_PHASE1_FINAL.md) |

---

## Final state

| Phase | Status |
|-------|--------|
| Phase 1 — map space saturation @1200 | **CLOSED** |
| Phase 2 — selected_map_space_v1 | **CLOSED** / reviewer-ready |
| Official selection | **75 maps**, hybrid, seed 42 |
| Constraints | `constraints_satisfied: true` |

---

## Next step

**Structural scenario generation** using:

```text
scenarios/selected_map_space_v1/manifest_selected_maps.csv
```

```text
selected maps (75)
    × movement models
    × node densities
    × group structures
    × network parameters
    → structural scenario space
```

- Do **not** apply Traffic Profiles yet.
- Do **not** modify `corpus_v1/` or `base_scenarios/`.
- No scenarios generated in this documentation update task.

---

*Documentation closure report — selected_map_space_v1, June 2026*
