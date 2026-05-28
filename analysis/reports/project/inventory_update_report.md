# Inventory update report

Generated: 2026-05-24 17:01 UTC

## Verified counts (from `scenarios/`)

| Metric | Count |
|--------|------:|
| Total files (excl. .git, .venv, __pycache__) | 2777 |
| `corpus_v1` `.settings` | 720 |
| `analysis/data/` CSV files | 45 |
| `analysis/reports/` files | 51 |
| Figures PNG | 770 |
| Spatial heatmaps PNG | 720 |
| `.wiki-clone/` markdown | 19 |
| `manifest.csv` lines | 721 |
| `output_metrics.csv` lines | 721 |

## Structural changes (2026-05-24 round 2)

- `corpus_dropped_v1/` → `_archive/corpus_dropped_v1/`
- `.wiki-clone/_legacy_pre_paper_rebuild/` → `_archive/wiki/legacy_pre_paper_rebuild/`
- Backup: `../scenarios_backup_20260524_pre_freeze.tar.gz` (repo parent)

## Regeneration

```bash
python3 scenarios/analysis/scripts/paper/build_inventory_update_report.py
```

Update [`INVENTARIO.md`](../INVENTARIO.md) manually when taxonomy changes.
