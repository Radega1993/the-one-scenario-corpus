#!/usr/bin/env python3
"""Analyze FAIL_BUILD_SYNTHETIC_DEGENERATE rows in map_space_revised_v2 manifest."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


_PACK = Path(__file__).resolve().parents[1]
SCENARIOS = _PACK.parent
DEFAULT_MANIFEST = _PACK / "manifest_maps_all.csv"
DEFAULT_CSV = _PACK / "data" / "synthetic_generation_failures_v2.csv"
DEFAULT_SUMMARY = _PACK / "data" / "synthetic_generation_failure_summary_v2.csv"
DEFAULT_MD = _PACK / "docs" / "synthetic_generation_failure_analysis_v2.md"


def _load_metadata(wkt_hint: str, map_id: str, output_root: Path) -> dict[str, Any]:
    candidates = []
    if wkt_hint:
        p = Path(wkt_hint)
        if p.is_file():
            candidates.append(p.with_name("metadata.json") if p.name == "roads.wkt" else p.parent / "metadata.json")
        else:
            candidates.append(Path(str(wkt_hint).replace("roads.wkt", "metadata.json")))
    # search under output_root
    for meta in output_root.glob(f"batch_*/wkt/{map_id}/metadata.json"):
        candidates.append(meta)
    for path in candidates:
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return {}
    return {}


def analyze(manifest: Path, output_root: Path) -> tuple[list[dict[str, str]], list[dict[str, Any]], str]:
    rows = list(csv.DictReader(manifest.open(encoding="utf-8")))
    by_gen: dict[str, Counter[str]] = defaultdict(Counter)
    detail_rows: list[dict[str, str]] = []
    for r in rows:
        gen = r.get("generator_type") or "(none)"
        st = r.get("generation_status") or ""
        by_gen[gen][st] += 1
        by_gen[gen]["planned"] += 1

    deg = [r for r in rows if r.get("generation_status") == "FAIL_BUILD_SYNTHETIC_DEGENERATE"]
    for r in deg:
        meta = _load_metadata(r.get("wkt_path") or r.get("metadata_path") or "", r.get("map_id") or "", output_root)
        syn_val = meta.get("synthetic_validation") or {}
        detail_rows.append(
            {
                "map_id": r.get("map_id", ""),
                "source_type": r.get("source_type", ""),
                "archetype": r.get("archetype", ""),
                "generator_type": r.get("generator_type", ""),
                "trace_id": r.get("trace_id", ""),
                "seed": r.get("seed", ""),
                "error_notes": r.get("error_notes", ""),
                "regeneration_attempts": str(syn_val.get("regeneration_attempts", "")),
                "n_nodes": str(syn_val.get("n_nodes", meta.get("n_nodes", ""))),
                "n_edges": str(syn_val.get("n_edges", meta.get("n_edges", ""))),
                "generator_params": json.dumps(meta.get("generator_params") or {}, sort_keys=True),
            }
        )

    summary: list[dict[str, Any]] = []
    for gen in sorted(by_gen):
        c = by_gen[gen]
        planned = int(c["planned"])
        ok = int(c.get("OK", 0) + c.get("SKIPPED_EXISTING_OK", 0))
        degenerate = int(c.get("FAIL_BUILD_SYNTHETIC_DEGENERATE", 0))
        rate = (degenerate / planned) if planned else 0.0
        notes = Counter(d["error_notes"] for d in detail_rows if d["generator_type"] == gen)
        main = notes.most_common(1)[0][0] if notes else ""
        summary.append(
            {
                "generator_type": gen,
                "planned": planned,
                "ok": ok,
                "degenerate": degenerate,
                "degenerate_rate": round(rate, 4),
                "main_cause": main,
            }
        )

    # Markdown
    lines = [
        "# Synthetic generation failure analysis v2",
        "",
        "**Pool:** `scenarios/Generated_Map_Space_v1/` (engineering validation pool)",
        f"**Manifest:** `{manifest}`",
        f"**Degenerate count:** {len(deg)}",
        "",
        "## Policy",
        "",
        "- Failed attempts remain in `manifest_maps_all.csv` (`FAIL_BUILD_SYNTHETIC_DEGENERATE`).",
        "- Do **not** silently regenerate until PASS without recording failures (avoids survival bias).",
        "- This analysis is required before completing remaining OSM downloads.",
        "",
        "## Summary by generator",
        "",
        "| Generator | Planned | OK | Degenerate | Rate | Main cause |",
        "|-----------|--------:|---:|-----------:|-----:|------------|",
    ]
    for s in summary:
        if s["planned"] == 0 and s["generator_type"] == "(none)":
            continue
        if s["degenerate"] == 0 and s["generator_type"] not in {d["generator_type"] for d in detail_rows}:
            # still show generators that appear in synthetic attempts
            if s["generator_type"] == "(none)":
                continue
        lines.append(
            f"| `{s['generator_type']}` | {s['planned']} | {s['ok']} | {s['degenerate']} | "
            f"{s['degenerate_rate']:.1%} | {s['main_cause']} |"
        )

    by_arch = Counter(d["archetype"] for d in detail_rows)
    by_src = Counter(d["source_type"] for d in detail_rows)
    by_cause = Counter(d["error_notes"] for d in detail_rows)
    lines += [
        "",
        "## Degenerate by archetype",
        "",
    ]
    for k, v in by_arch.most_common():
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Degenerate by source_type", ""]
    for k, v in by_src.most_common():
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Degenerate by error_notes", ""]
    for k, v in by_cause.most_common():
        lines.append(f"- `{k}`: {v}")

    lines += [
        "",
        "## Interpretation",
        "",
        "All recorded degenerates in the current engineering pool are `source_type=synthetic` "
        "(not `trace_reference_synthetic`). Failures concentrate on generators whose discrete "
        "parameter extremes produce graphs below validation floors "
        "(`min_nodes=20`, `min_edges=20`):",
        "",
        "- `bus_route_corridor`: sparse stop/corridor layouts at low `n_stops` / narrow corridors.",
        "- `campus_compact`: few buildings × low path density → too few nodes.",
        "- `corridor` / `radial_city`: extreme length/width or ring/spoke settings near minima.",
        "",
        "### Recommended actions (before more generation)",
        "",
        "1. Tighten discrete parameter ranges so mid/high settings always clear validation floors, **or**",
        "2. Lower floors only with an explicit methodological note (not preferred), **or**",
        "3. Keep ranges but treat degenerates as part of the design surface (documented attrition).",
        "",
        "Do not drop failed rows from the manifest.",
        "",
    ]
    return detail_rows, summary, "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--output-root", type=Path, default=_PACK)
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--summary-csv", type=Path, default=DEFAULT_SUMMARY)
    ap.add_argument("--md", type=Path, default=DEFAULT_MD)
    args = ap.parse_args()

    detail, summary, md = analyze(args.manifest, args.output_root)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.md.parent.mkdir(parents=True, exist_ok=True)
    if detail:
        with args.csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(detail[0].keys()))
            w.writeheader()
            w.writerows(detail)
    with args.summary_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["generator_type", "planned", "ok", "degenerate", "degenerate_rate", "main_cause"],
        )
        w.writeheader()
        for s in summary:
            w.writerow(s)
    args.md.write_text(md, encoding="utf-8")
    print(f"Wrote {args.md} ({len(detail)} degenerate rows)")


if __name__ == "__main__":
    main()
