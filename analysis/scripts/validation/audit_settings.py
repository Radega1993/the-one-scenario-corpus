#!/usr/bin/env python3
"""
Audit all .settings in corpus_v2 (or manifest) and write settings_audit.csv + report.

Usage:
  scenarios/analysis/.venv/bin/python scenarios/analysis/scripts/validation/audit_settings.py \\
    --manifest scenarios/corpus_v2/manifest.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import REPO_ROOT  # noqa: E402

from lib.paths import DATA_DIR  # noqa: E402
from lib.report_paths import SETTINGS_AUDIT  # noqa: E402
from lib.settings_audit import audit_corpus_dir, audit_from_manifest  # noqa: E402


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _write_report(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = len(rows)
    families = Counter(r.get("family", "") for r in rows)
    maps = Counter(r.get("map_dataset", "") or "unknown" for r in rows)
    mm = Counter()
    for r in rows:
        for part in str(r.get("movement_models", "")).split("|"):
            if part.strip():
                mm[part.strip()] += 1
    bases = len({r.get("scenario_base") for r in rows})
    tps = Counter(r.get("tp", "") for r in rows)

    lines = [
        "# Settings audit (corpus_v2)",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"- Scenarios audited: **{n}**",
        f"- Unique scenario bases: **{bases}**",
        f"- Traffic profiles (TP): **{len(tps)}** distinct",
        "",
        "## Families",
        "",
        "| family | count |",
        "|--------|------:|",
    ]
    for fam, c in sorted(families.items()):
        lines.append(f"| `{fam}` | {c} |")

    lines.extend(
        [
            "",
            "## Map datasets",
            "",
            "| map_dataset | count |",
            "|-------------|------:|",
        ]
    )
    for m, c in maps.most_common():
        lines.append(f"| `{m}` | {c} |")

    lines.extend(
        [
            "",
            "## Movement models (per group entries)",
            "",
            "| movement_model | count |",
            "|----------------|------:|",
        ]
    )
    for m, c in mm.most_common(15):
        lines.append(f"| `{m}` | {c} |")

    lines.extend(
        [
            "",
            "## Traffic profiles",
            "",
            "| TP | count |",
            "|----|------:|",
        ]
    )
    for tp, c in sorted(tps.items()):
        lines.append(f"| `{tp}` | {c} |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Full per-scenario table: `data/settings_audit.csv`.",
            "- Mobility and map parameters are unchanged from corpus_v1 inside each base; TP overlays Events* and Group.msgTtl.",
            "- Most v2 scenarios reference **HelsinkiMedium** WKT under `data/HelsinkiMedium/`.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit corpus .settings files.")
    ap.add_argument("--manifest", type=str, default="scenarios/corpus_v2/manifest.csv")
    ap.add_argument("--corpus-dir", type=str, default=None)
    ap.add_argument("--output-csv", type=str, default=str(DATA_DIR / "settings_audit.csv"))
    ap.add_argument("--output-report", type=str, default=str(SETTINGS_AUDIT))
    ap.add_argument("--repo-root", type=str, default=str(REPO_ROOT))
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    mf = Path(args.manifest)
    if not mf.is_absolute():
        mf = repo / mf

    rows: list[dict] = []
    if mf.is_file():
        import pandas as pd

        df = pd.read_csv(mf)
        manifest_rows = df.to_dict(orient="records")
        rows = audit_from_manifest(manifest_rows, repo)
        print(f"Audited {len(rows)} scenarios from manifest {mf.name}")
    elif args.corpus_dir:
        corpus = Path(args.corpus_dir)
        if not corpus.is_absolute():
            corpus = repo / corpus
        rows = audit_corpus_dir(corpus)
        print(f"Audited {len(rows)} .settings under {corpus}")
    else:
        print("Provide --manifest or --corpus-dir", file=sys.stderr)
        return 1

    out_csv = Path(args.output_csv)
    if not out_csv.is_absolute():
        out_csv = repo / out_csv
    out_md = Path(args.output_report)
    if not out_md.is_absolute():
        out_md = repo / out_md

    _write_csv(rows, out_csv)
    _write_report(rows, out_md)
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
