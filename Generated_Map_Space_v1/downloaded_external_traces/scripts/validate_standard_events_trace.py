#!/usr/bin/env python3
"""Validate a The ONE StandardEventsReader connectivity trace + optional ID mapping."""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_NODES = 52
EXPECTED_CONTACTS = 10873
EXPECTED_EVENTS = 21746
EXPECTED_DURATION = 987529
EXPECTED_NODE_MAX = 51
MISSING_ORIGINAL_IDS = {40, 41}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_trace(trace_path: Path) -> tuple[dict, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    stats: dict = {
        "path": str(trace_path),
        "exists": trace_path.is_file(),
        "n_events": 0,
        "n_up": 0,
        "n_down": 0,
        "n_contacts": 0,
        "n_nodes": 0,
        "node_ids": [],
        "min_time": None,
        "max_time": None,
        "duration_seconds": 0,
        "duration_days": 0.0,
    }

    if not stats["exists"]:
        errors.append(f"Trace file does not exist: {trace_path}")
        return stats, errors, warnings

    nodes: set[int] = set()
    open_pairs: dict[tuple[int, int], int] = defaultdict(int)
    prev_time: int | None = None

    with trace_path.open(encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, start=1):
            raw = line.rstrip("\n")
            if not raw.strip():
                continue
            cols = raw.split("\t")
            if len(cols) != 5:
                errors.append(f"L{lineno}: expected 5 tab-separated columns, got {len(cols)}")
                continue
            time_s, action, a, b, typ = cols
            try:
                t = int(time_s)
            except ValueError:
                errors.append(f"L{lineno}: time is not an integer: {time_s!r}")
                continue
            if t < 0:
                errors.append(f"L{lineno}: negative time {t}")
            if prev_time is not None and t < prev_time:
                errors.append(f"L{lineno}: time not non-decreasing ({prev_time} -> {t})")
            prev_time = t

            if action != "CONN":
                errors.append(f"L{lineno}: action must be CONN, got {action!r}")
            if typ not in ("up", "down"):
                errors.append(f"L{lineno}: type must be up|down, got {typ!r}")

            try:
                na = int(a)
                nb = int(b)
            except ValueError:
                errors.append(f"L{lineno}: nodes not integers: {a!r}, {b!r}")
                continue

            for n in (na, nb):
                nodes.add(n)
                if n < 0 or n > EXPECTED_NODE_MAX:
                    errors.append(f"L{lineno}: node {n} outside expected range 0–{EXPECTED_NODE_MAX}")

            pair = (min(na, nb), max(na, nb))
            if typ == "up":
                stats["n_up"] += 1
                open_pairs[pair] += 1
            elif typ == "down":
                stats["n_down"] += 1
                if open_pairs[pair] <= 0:
                    errors.append(f"L{lineno}: down without prior up for pair {pair}")
                else:
                    open_pairs[pair] -= 1

            stats["n_events"] += 1
            if stats["min_time"] is None or t < stats["min_time"]:
                stats["min_time"] = t
            if stats["max_time"] is None or t > stats["max_time"]:
                stats["max_time"] = t

    still_open = {p: c for p, c in open_pairs.items() if c > 0}
    if still_open:
        errors.append(f"Open connections remain at end: {len(still_open)} pairs")

    stats["n_nodes"] = len(nodes)
    stats["node_ids"] = sorted(nodes)
    stats["n_contacts"] = stats["n_up"]  # one contact = one up/down pair when balanced
    stats["duration_seconds"] = int(stats["max_time"] or 0)
    stats["duration_days"] = round(stats["duration_seconds"] / 86400.0, 2)

    if stats["n_events"] != EXPECTED_EVENTS:
        errors.append(f"Expected {EXPECTED_EVENTS} events, got {stats['n_events']}")
    if stats["n_up"] != EXPECTED_CONTACTS:
        errors.append(f"Expected {EXPECTED_CONTACTS} up events (contacts), got {stats['n_up']}")
    if stats["n_down"] != EXPECTED_CONTACTS:
        errors.append(f"Expected {EXPECTED_CONTACTS} down events, got {stats['n_down']}")
    if stats["n_up"] != stats["n_down"]:
        errors.append(f"up/down imbalance: up={stats['n_up']} down={stats['n_down']}")
    if stats["n_nodes"] != EXPECTED_NODES:
        errors.append(f"Expected {EXPECTED_NODES} unique nodes, got {stats['n_nodes']}")
    if stats["duration_seconds"] != EXPECTED_DURATION:
        errors.append(
            f"Expected max duration {EXPECTED_DURATION}s, got {stats['duration_seconds']}s"
        )
    if stats["node_ids"] and (min(stats["node_ids"]) != 0 or max(stats["node_ids"]) != EXPECTED_NODE_MAX):
        warnings.append(
            f"Node ID span is {min(stats['node_ids'])}–{max(stats['node_ids'])} "
            f"(expected 0–{EXPECTED_NODE_MAX})"
        )

    return stats, errors, warnings


def validate_mapping(mapping_path: Path | None) -> tuple[dict, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    stats: dict = {
        "path": str(mapping_path) if mapping_path else "",
        "exists": bool(mapping_path and mapping_path.is_file()),
        "n_rows": 0,
        "new_ids": [],
        "old_ids": [],
        "missing_original_ids_observed": [],
    }
    if mapping_path is None:
        warnings.append("No mapping file provided; skip mapping checks")
        return stats, errors, warnings
    if not stats["exists"]:
        errors.append(f"Mapping file does not exist: {mapping_path}")
        return stats, errors, warnings

    new_ids: list[int] = []
    old_ids: list[int] = []
    with mapping_path.open(encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, start=1):
            raw = line.rstrip("\n")
            if not raw.strip():
                continue
            cols = raw.split("\t")
            if len(cols) != 2:
                errors.append(f"mapping L{lineno}: expected 2 columns, got {len(cols)}")
                continue
            try:
                new_id = int(cols[0])
                old_id = int(cols[1])
            except ValueError:
                errors.append(f"mapping L{lineno}: non-integer IDs: {cols}")
                continue
            new_ids.append(new_id)
            old_ids.append(old_id)

    stats["n_rows"] = len(new_ids)
    stats["new_ids"] = new_ids
    stats["old_ids"] = old_ids
    if len(new_ids) != EXPECTED_NODES:
        errors.append(f"Mapping must have {EXPECTED_NODES} rows, got {len(new_ids)}")
    if new_ids and sorted(new_ids) != list(range(EXPECTED_NODES)):
        errors.append("Mapping new IDs must be exactly 0..51 without gaps/duplicates")
    if len(set(new_ids)) != len(new_ids):
        errors.append("Duplicate new IDs in mapping")
    if len(set(old_ids)) != len(old_ids):
        errors.append("Duplicate old IDs in mapping")

    present_old = set(old_ids)
    missing = sorted(MISSING_ORIGINAL_IDS - present_old)
    unexpected_present = sorted(MISSING_ORIGINAL_IDS & present_old)
    stats["missing_original_ids_observed"] = missing
    if missing != sorted(MISSING_ORIGINAL_IDS):
        warnings.append(
            f"Expected original IDs 40 and 41 to be absent; missing observed={missing}, "
            f"unexpectedly present={unexpected_present}"
        )
    else:
        warnings.append(
            "Original IDs 40 and 41 absent from mapping (expected: stationary devices "
            "that only saw external nodes)."
        )

    return stats, errors, warnings


def write_report(
    out_path: Path,
    trace_stats: dict,
    map_stats: dict,
    errors: list[str],
    warnings: list[str],
    checksums: dict[str, str],
) -> str:
    status = "PASS" if not errors else "FAIL"
    lines = [
        "# Validation — haggle_one_cambridge_city_complete",
        "",
        f"- **Validation date (UTC):** {datetime.now(timezone.utc).isoformat()}",
        f"- **Status:** **{status}**",
        f"- **Validated path:** `{trace_stats['path']}`",
        f"- **Mapping path:** `{map_stats.get('path') or 'n/a'}`",
        "",
        "## Summary counts",
        "",
        f"| Metric | Value |",
        f"|--------|------:|",
        f"| Events | {trace_stats['n_events']} |",
        f"| Contacts (up events) | {trace_stats['n_contacts']} |",
        f"| Nodes | {trace_stats['n_nodes']} |",
        f"| Duration (seconds) | {trace_stats['duration_seconds']} |",
        f"| Duration (days) | {trace_stats['duration_days']} |",
        f"| Events up | {trace_stats['n_up']} |",
        f"| Events down | {trace_stats['n_down']} |",
        f"| Node ID range | {min(trace_stats['node_ids']) if trace_stats['node_ids'] else 'n/a'}–{max(trace_stats['node_ids']) if trace_stats['node_ids'] else 'n/a'} |",
        f"| Mapping rows | {map_stats.get('n_rows', 0)} |",
        "",
        "## Expected contract",
        "",
        f"- Nodes: {EXPECTED_NODES}",
        f"- Contacts: {EXPECTED_CONTACTS}",
        f"- Events: {EXPECTED_EVENTS} (= 2 × contacts)",
        f"- Duration: {EXPECTED_DURATION} s (~11.43 days)",
        f"- Schema: `time\\taction\\tfirst_node\\tsecond_node\\ttype` with `action=CONN`, `type∈{{up,down}}`",
        "",
        "## Checksums (SHA256)",
        "",
    ]
    for name, digest in checksums.items():
        lines.append(f"- `{name}`: `{digest}`")
    lines += ["", "## Errors", ""]
    if errors:
        lines.extend(f"- {e}" for e in errors)
    else:
        lines.append("- none")
    lines += ["", "## Warnings", ""]
    if warnings:
        lines.extend(f"- {w}" for w in warnings)
    else:
        lines.append("- none")
    lines += [
        "",
        "## Notes",
        "",
        "- This validation does **not** redistribute the raw CRAWDAD payload.",
        "- Trace is a design/reference anchor for SMS-v1 / TPSC-v1, not an OSM map.",
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(lines)
    out_path.write_text(text, encoding="utf-8")
    return status


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--mapping", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    t_stats, t_err, t_warn = validate_trace(args.trace)
    m_stats, m_err, m_warn = validate_mapping(args.mapping)
    errors = t_err + m_err
    warnings = t_warn + m_warn

    checksums: dict[str, str] = {}
    for p in [args.trace, args.mapping]:
        if p and p.is_file():
            checksums[p.name] = sha256_file(p)
    meta = args.trace.parent / "metadata.yaml"
    if meta.is_file():
        checksums[meta.name] = sha256_file(meta)

    status = write_report(args.out, t_stats, m_stats, errors, warnings, checksums)
    print(f"{status}: wrote {args.out}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    for w in warnings:
        print(f"WARN: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
