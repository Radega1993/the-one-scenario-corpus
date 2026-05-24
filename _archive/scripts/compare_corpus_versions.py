#!/usr/bin/env python3
"""
Compare corpus_v2 vs corpus_v3 (when present): settings keys and metrics.

Skeleton for post-rebuild validation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO_ROOT = BASE.parent.parent

if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from lib.map_context import load_settings_flat  # noqa: E402
from lib.paths import DATA_DIR, REPO_ROOT as ROOT  # noqa: E402


def _settings_keys(corpus_dir: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for p in sorted(corpus_dir.rglob("*.settings")):
        kv = load_settings_flat(p)
        name = kv.get("Scenario.name", p.stem)
        out[name] = set(kv.keys())
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare two corpus versions.")
    ap.add_argument("--corpus-a", default="scenarios/corpus_v2")
    ap.add_argument("--corpus-b", default="scenarios/corpus_v3")
    ap.add_argument("--metrics-a", default=str(DATA_DIR / "output_metrics.csv"))
    ap.add_argument("--metrics-b", default=None, help="Post-v3 metrics CSV (optional)")
    ap.add_argument("--output", default=str(DATA_DIR / "corpus_version_diff.csv"))
    ap.add_argument("--repo-root", default=str(ROOT))
    args = ap.parse_args()

    import pandas as pd

    repo = Path(args.repo_root).resolve()
    dir_a = repo / args.corpus_a
    dir_b = repo / args.corpus_b

    if not dir_a.is_dir():
        print(f"Missing corpus A: {dir_a}", file=sys.stderr)
        return 1

    keys_a = _settings_keys(dir_a)
    print(f"corpus A: {len(keys_a)} settings files")

    rows = []
    if dir_b.is_dir():
        keys_b = _settings_keys(dir_b)
        print(f"corpus B: {len(keys_b)} settings files")
        common = set(keys_a) & set(keys_b)
        for scen in sorted(common):
            only_a = keys_a[scen] - keys_b[scen]
            only_b = keys_b[scen] - keys_a[scen]
            rows.append(
                {
                    "scenario": scen,
                    "keys_only_in_a": len(only_a),
                    "keys_only_in_b": len(only_b),
                    "sample_keys_a": ";".join(sorted(only_a)[:5]),
                    "sample_keys_b": ";".join(sorted(only_b)[:5]),
                }
            )
    else:
        print(f"corpus B not found ({dir_b}); settings diff skipped.")

    ma = repo / args.metrics_a
    if ma.is_file():
        dfa = pd.read_csv(ma)
        print(f"metrics A: {len(dfa)} rows")
    if args.metrics_b:
        mb = Path(args.metrics_b)
        if not mb.is_absolute():
            mb = repo / mb
        if mb.is_file():
            dfb = pd.read_csv(mb)
            merged = dfa.merge(dfb, on="scenario", suffixes=("_v2", "_v3"), how="inner")
            print(f"metrics overlap: {len(merged)} scenarios")
            if "delivery_ratio_v2" in merged.columns and "delivery_ratio_v3" in merged.columns:
                merged["delivery_delta"] = merged["delivery_ratio_v3"] - merged["delivery_ratio_v2"]
                print(
                    "delivery_delta mean:",
                    merged["delivery_delta"].mean(),
                )

    out = Path(args.output)
    if not out.is_absolute():
        out = repo / out
    if rows:
        pd.DataFrame(rows).to_csv(out, index=False)
        print(f"Wrote {out}")
    else:
        print("No diff rows written (corpus_v3 may not exist yet).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
