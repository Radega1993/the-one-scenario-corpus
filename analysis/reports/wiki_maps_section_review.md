# Wiki maps & families documentation review

Generated: 2026-05-28

Backup before edits: `scenarios/.wiki-clone/_backup_before_maps_doc_update_20260528_183217/`

## Pages reviewed

| Page | Status |
|------|--------|
| `scenarios/.wiki-clone/02-Maps-and-Map-Generation.md` | Updated |
| `scenarios/.wiki-clone/05-Scenario-Families.md` | Rewritten |
| `scenarios/.wiki-clone/06-Urban-Family.md` | Updated |
| `scenarios/.wiki-clone/07-Campus-Family.md` | Updated |
| `scenarios/.wiki-clone/08-Vehicles-Family.md` | Updated |
| `scenarios/.wiki-clone/09-Rural-Family.md` | Updated |
| `scenarios/.wiki-clone/10-Disaster-Family.md` | Updated |
| `scenarios/.wiki-clone/11-Social-Family.md` | Updated |

## Changes by file

### 02-Maps-and-Map-Generation.md

- Added **Benchmark map policy** (synthetic benchmark, no real traces, one map per family, stress grid excluded from environmental corpus).
- Replaced *Map assignment by scenario family* with **Map assignment by family** (6-column table + paper status).
- Gallery: intro paragraph per paper spec; clarified wiki PNGs vs `*_validation.png` QA figures.
- Fixed smoke set: `R1_Rural_SparseSPMM` (was `R1_Rural_RandomWaypoint`).
- Legacy HelsinkiMedium/Manhattan labelled **Legacy / retired**.
- Link to Scenario Families → `05-Scenario-Families`.

### 05-Scenario-Families.md

- Corrected to **six environmental families + one stress/control family**.
- Added index table (family → map → wiki → base → TP counts).
- Links to maps page and Traffic Profiles (forward ref).

### 06–11 family pages

- Standardised structure: Map table, visual legend, **Why this map fits**, Base scenarios, Movement models, WKT assets, Validation, Corpus size.
- Legacy notes: vehicles (`A_bus` retired), rural (RandomWaypoint → SparseSPMM), social (ClusterMovement vs SPMM).

## Images

| Asset | Present |
|-------|---------|
| `assets/maps/HelsinkiDowntown.png` | Yes |
| `assets/maps/KumpulaCampus.png` | Yes |
| `assets/maps/ManhattanMidtownGrid.png` | Yes |
| `assets/maps/NuuksioSparseTrails.png` | Yes |
| `assets/maps/HelsinkiDisrupted.png` | Yes |
| `assets/maps/KallioCommunityCompact.png` | Yes |
| `assets/maps/.png` | Yes |

**Missing images:** none.

Regenerate if needed:

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps {MapName}
```

## Broken links

- All `assets/maps/*.png` references in active wiki pages: **OK** (7/7).
- `Traffic-Profiles` page: forward reference only (not in `.wiki-clone` tree; linked from Home as elsewhere).

## Legacy references

| Term | Active wiki handling |
|------|----------------------|
| `seven environmental families` | Removed from 05 |
| `720 scenarios` | Not present in active pages |
| `corpus_v2` | Only as **retired name** in 02 benchmark scope table |
| `HelsinkiMedium` / `Manhattan` | Marked legacy/retired in 02 |
| `R1_Rural_RandomWaypoint` | Fixed to `R1_Rural_SparseSPMM` in 02 smoke set; noted in 09 |
| `A_bus.wkt` (vehicles) | Documented as retired in 08; valid in 06 urban |

## Paper-ready status by family

| Family | Map | Status |
|--------|-----|--------|
| `01_urban` | HelsinkiDowntown | Paper-ready |
| `02_campus` | KumpulaCampus | Paper-ready |
| `03_vehicles` | ManhattanMidtownGrid | Paper-ready |
| `04_rural` | NuuksioSparseTrails | Paper-ready |
| `05_disaster` | HelsinkiDisrupted | Paper-ready |
| `06_social` | KallioCommunityCompact | Paper-ready |
| `07_` |  | Stress/control only |

## Final checklist

- [x] 02 explains synthetic benchmark and no real mobility traces
- [x] One fixed map per environmental family documented
- [x]  excluded from environmental paper corpus
- [x] **Map assignment by family** table with 6 columns
- [x] Gallery with intro + 7 PNGs from `assets/maps/`
- [x] No validation PNGs as main wiki gallery images
- [x] 05 = six + stress index with base/TP counts
- [x] Family pages 06–11 follow minimum template
- [x] Legacy terms corrected or labelled retired
- [x] All image links verified on disk
- [x] Backup created before edits
- [x] Review MD and CSV written

## Scope excluded

No changes to `.settings`, WKT, simulations, or numeric results.