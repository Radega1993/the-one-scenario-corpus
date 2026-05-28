# Wiki core pages and Installation — review

Generated: 2026-05-28

Backup: `scenarios/.wiki-clone/_backup_before_installation_page_20260528_192425/`

## Pages reviewed

| Page | Action |
|------|--------|
| `Home.md` | Updated |
| `02-Maps-and-Map-Generation.md` | Updated (summary table, legend, Installation link) |
| `03-Installation.md` | **Created** |
| `05-Scenario-Families.md` | Expanded |
| `06-Urban-Family.md` | Expanded to full template |
| `07-Campus-Family.md` | Expanded |
| `08-Vehicles-Family.md` | Expanded |
| `09-Rural-Family.md` | Expanded |
| `10-Disaster-Family.md` | Expanded |
| `11-Social-Family.md` | Expanded |

## Pages created

- `scenarios/.wiki-clone/03-Installation.md`

## Pages incomplete / pending

| Page | Notes |
|------|-------|
| `Usage` | Forward reference from Home — no file in `.wiki-clone` |
| `Traffic-Profiles` | Forward reference |
| `Reproducibility` | Forward reference |
| `Protocol-Benchmarking`, `Diversity-Validation`, `Figures-and-Tables` | Forward references in old Home nav — trimmed in new Home |
| `12-Stress-Family` | Not created (stress documented in 05 + 02) |

## Images

All seven map PNGs present under `scenarios/.wiki-clone/assets/maps/`:

- HelsinkiDowntown.png
- KumpulaCampus.png
- ManhattanMidtownGrid.png
- NuuksioSparseTrails.png
- HelsinkiDisrupted.png
- KallioCommunityCompact.png
- ControlCompactGrid.png

**Missing:** none.

Regenerate if needed:

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps {MapName}
```

## Internal links added

- Home → `03-Installation`, `05-Scenario-Families`, family pages
- 02 → `03-Installation`
- 05 → `03-Installation`, family pages, 02-Maps
- Family pages → `assets/maps/{Map}.png` (all verified)

## Legacy terms

| Term | Handling |
|------|----------|
| seven environmental families | Removed from 05; Home states six + one stress |
| 720 scenarios | Not used; counts 45/540/30/615 |
| `corpus_v2` | Legacy note on Home only (retired) |
| HelsinkiMedium as active map | Legacy notes in 02, 03, 09; not used in settings |
| RandomWaypoint | Documented as retired → R1_Rural_SparseSPMM |
| `A_bus.wkt` (vehicles) | Documented retired in 08; valid in 06 urban |

## Final status by page

| Page | Exists | Complete | Updated | Notes |
|------|-------:|---------:|--------:|-------|
| Home.md | yes | yes | yes | Counts 45/540/30; 6+1 families |
| 02-Maps-and-Map-Generation.md | yes | yes | yes | Summary table + gallery |
| 03-Installation.md | yes | yes | yes | New; smoke test + run_all flags |
| 05-Scenario-Families.md | yes | yes | yes | Purpose / corpus role table |
| 06-Urban-Family.md | yes | yes | yes | Full template |
| 07-Campus-Family.md | yes | yes | yes | Full template |
| 08-Vehicles-Family.md | yes | yes | yes | Full template |
| 09-Rural-Family.md | yes | yes | yes | Full template |
| 10-Disaster-Family.md | yes | yes | yes | Full template |
| 11-Social-Family.md | yes | yes | yes | Full template |

## Checklist

- [x] Home complete
- [x] Maps page complete
- [x] Scenario families page complete
- [x] One page per environmental family complete
- [x] Installation page created
- [x] Links validated (map images 7/7)
- [x] Legacy terms removed or documented
- [x] Review MD and CSV written
- [x] Backup before edits

## Scope excluded

No changes to `.settings`, WKT, simulation results, or analysis scripts.
