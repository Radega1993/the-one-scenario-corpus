#!/usr/bin/env python3
"""Register / upsert a row in external_traces/registry/real_trace_inventory_v1.csv."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_CSV = ROOT / "registry" / "real_trace_inventory_v1.csv"
REGISTRY_MD = ROOT / "registry" / "real_trace_inventory_v1.md"

FIELDNAMES = [
    "trace_id",
    "dataset_family",
    "source_dataset",
    "source_version",
    "format",
    "nodes",
    "contacts",
    "duration_seconds",
    "source_repository",
    "doi",
    "local_status",
    "used_in_sms_v1",
    "archetypes",
    "anchor_ids",
    "redistribution",
]


def upsert_row(row: dict[str, str]) -> None:
    REGISTRY_CSV.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    if REGISTRY_CSV.is_file():
        with REGISTRY_CSV.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    rows = [r for r in rows if r.get("trace_id") != row["trace_id"]]
    rows.append(row)
    rows.sort(key=lambda r: r.get("trace_id", ""))
    with REGISTRY_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)
    print(f"Updated {REGISTRY_CSV} ({len(rows)} rows)")


def write_md_stub() -> None:
    if REGISTRY_MD.is_file():
        return
    REGISTRY_MD.write_text(
        "# Real trace inventory v1\n\nSee `real_trace_inventory_v1.csv`.\n",
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trace-id", required=True)
    ap.add_argument("--dataset-family", required=True)
    ap.add_argument("--source-dataset", required=True)
    ap.add_argument("--source-version", required=True)
    ap.add_argument("--format", required=True)
    ap.add_argument("--nodes", required=True)
    ap.add_argument("--contacts", required=True)
    ap.add_argument("--duration-seconds", required=True)
    ap.add_argument("--source-repository", required=True)
    ap.add_argument("--doi", required=True)
    ap.add_argument("--local-status", default="downloaded")
    ap.add_argument("--used-in-sms-v1", default="true")
    ap.add_argument("--archetypes", required=True)
    ap.add_argument("--anchor-ids", required=True)
    ap.add_argument("--redistribution", default="do_not_redistribute_raw_trace")
    args = ap.parse_args()

    row = {
        "trace_id": args.trace_id,
        "dataset_family": args.dataset_family,
        "source_dataset": args.source_dataset,
        "source_version": args.source_version,
        "format": args.format,
        "nodes": args.nodes,
        "contacts": args.contacts,
        "duration_seconds": args.duration_seconds,
        "source_repository": args.source_repository,
        "doi": args.doi,
        "local_status": args.local_status,
        "used_in_sms_v1": args.used_in_sms_v1,
        "archetypes": args.archetypes,
        "anchor_ids": args.anchor_ids,
        "redistribution": args.redistribution,
    }
    upsert_row(row)
    write_md_stub()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
