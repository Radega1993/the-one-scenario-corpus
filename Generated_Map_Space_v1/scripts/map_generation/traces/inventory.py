"""Read the canonical real-trace inventory CSV."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from map_generation.config import DEFAULT_INVENTORY, resolve_repo_path


def load_inventory(path: Path | str | None = None) -> dict[str, dict[str, str]]:
    p = resolve_repo_path(path) if path else DEFAULT_INVENTORY
    if not p.is_file():
        raise FileNotFoundError(f"Missing real-trace inventory: {p}")
    rows: dict[str, dict[str, str]] = {}
    with p.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tid = (row.get("trace_id") or "").strip()
            if tid:
                rows[tid] = {k: (v or "") for k, v in row.items()}
    return rows


def inventory_summary(inv: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "n_traces": len(inv),
        "validated": sorted(t for t, r in inv.items() if "validated" in r.get("local_status", "")),
        "downloaded": sorted(t for t, r in inv.items() if r.get("local_status") == "downloaded"),
    }
