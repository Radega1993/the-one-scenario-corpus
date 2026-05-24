#!/usr/bin/env python3
"""
Cross-audit settings + metrics → scenario_diagnosis.csv / .md

Usage:
  scenarios/analysis/.venv/bin/python scenarios/analysis/diagnose_scenarios.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import DATA_DIR, REPO_ROOT as ROOT  # noqa: E402
from lib.report_paths import SCENARIO_DIAGNOSIS  # noqa: E402
from lib.scenario_diagnosis import build_diagnosis_table, write_diagnosis_report  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Diagnose corpus scenarios.")
    ap.add_argument("--settings-audit", type=str, default=str(DATA_DIR / "settings_audit.csv"))
    ap.add_argument("--output-metrics", type=str, default=str(DATA_DIR / "output_metrics.csv"))
    ap.add_argument("--indirect-features", type=str, default=str(DATA_DIR / "indirect_features_diego.csv"))
    ap.add_argument("--spatial-metrics", type=str, default=str(DATA_DIR / "spatial_occupancy_metrics.csv"))
    ap.add_argument("--thresholds", type=str, default=str(DATA_DIR / "realism_thresholds.yaml"))
    ap.add_argument("--reports-dir", type=str, default="reports")
    ap.add_argument("--output-csv", type=str, default=str(DATA_DIR / "scenario_diagnosis.csv"))
    ap.add_argument("--output-report", type=str, default=str(SCENARIO_DIAGNOSIS))
    ap.add_argument("--repo-root", type=str, default=str(ROOT))
    args = ap.parse_args()

    import pandas as pd

    repo = Path(args.repo_root).resolve()

    def _p(s: str) -> Path:
        p = Path(s)
        return p if p.is_absolute() else repo / p

    sa = pd.read_csv(_p(args.settings_audit))
    om = pd.read_csv(_p(args.output_metrics))
    ind = pd.read_csv(_p(args.indirect_features))
    sp_path = _p(args.spatial_metrics)
    spatial = pd.read_csv(sp_path) if sp_path.is_file() else None

    reports_dir = _p(args.reports_dir)
    th_path = _p(args.thresholds)

    df = build_diagnosis_table(
        sa,
        om,
        ind,
        spatial,
        thresholds_path=th_path,
        reports_dir=reports_dir,
        repo_root=repo,
    )

    out_csv = _p(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    out_md = _p(args.output_report)
    write_diagnosis_report(df, out_md, th_path)

    print(f"Wrote {out_csv} ({len(df)} rows)")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
