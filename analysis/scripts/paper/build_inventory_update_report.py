#!/usr/bin/env python3
"""Regenerate inventory_update_report.md with current file counts."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import SCENARIOS_DIR  # noqa: E402
from lib.report_paths import INVENTORY_UPDATE_REPORT  # noqa: E402

SCENARIOS = SCENARIOS_DIR
REPORT = INVENTORY_UPDATE_REPORT


def _run(cmd: str) -> str:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=SCENARIOS)
    return (r.stdout or "").strip().split()[-1] if r.stdout else "?"


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = _run("find . -type f ! -path './.git/*' ! -path './analysis/.venv/*' ! -path '*/__pycache__/*' ! -path './.wiki-clone/.git/*' | wc -l")
    settings_v2 = _run("find corpus_v2 -name '*.settings' | wc -l")
    csv_data = _run("find analysis/data -name '*.csv' | wc -l")
    reports_n = _run("find analysis/reports -type f | wc -l")
    fig_png = _run("find analysis/figures -name '*.png' | wc -l")
    heatmaps = _run("find analysis/figures/spatial_heatmaps -name '*.png' | wc -l")
    wiki_md = _run("find .wiki-clone -name '*.md' ! -path './.wiki-clone/.git/*' | wc -l")
    manifest = _run("wc -l < corpus_v2/manifest.csv")
    output = _run("wc -l < analysis/data/output_metrics.csv")

    text = f"""# Inventory update report

Generated: {ts}

## Verified counts (from `scenarios/`)

| Metric | Count |
|--------|------:|
| Total files (excl. .git, .venv, __pycache__) | {total} |
| `corpus_v2` `.settings` | {settings_v2} |
| `analysis/data/` CSV files | {csv_data} |
| `analysis/reports/` files | {reports_n} |
| Figures PNG | {fig_png} |
| Spatial heatmaps PNG | {heatmaps} |
| `.wiki-clone/` markdown | {wiki_md} |
| `manifest.csv` lines | {manifest} |
| `output_metrics.csv` lines | {output} |

## Structural changes (2026-05-24 round 2)

- `corpus_dropped_v1/` → `_archive/corpus_dropped_v1/`
- `.wiki-clone/_legacy_pre_paper_rebuild/` → `_archive/wiki/legacy_pre_paper_rebuild/`
- Backup: `../scenarios_backup_20260524_pre_freeze.tar.gz` (repo parent)

## Regeneration

```bash
python3 scenarios/analysis/scripts/paper/build_inventory_update_report.py
```

Update [`INVENTARIO.md`](../INVENTARIO.md) manually when taxonomy changes.
"""
    REPORT.write_text(text, encoding="utf-8")
    print(f"Wrote {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
