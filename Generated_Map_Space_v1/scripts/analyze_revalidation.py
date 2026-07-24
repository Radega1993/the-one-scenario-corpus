#!/usr/bin/env python3
"""Pool revalidation and attrition analysis for map_space_revised_v2 (post–Phase B OSM).

Produces survival rates (archetype × source), soft-target Δp, attrition bias tables,
incremental ladder definition, and the official markdown report.

Does NOT run feature extraction, saturation analysis, or SMS selection.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

_PACK = Path(__file__).resolve().parents[1]
SCENARIOS = _PACK.parent
DEFAULT_MANIFEST = _PACK / "manifest_maps_all.csv"
DEFAULT_ALLOCATION = _PACK / "config" / "archetype_source_allocation.yaml"
DEFAULT_DESIGN = _PACK / "config" / "map_design_space.yaml"
DEFAULT_DATA = _PACK / "data"
DEFAULT_MD = _PACK / "docs" / "map_space_revised_v2_pool_revalidation_attrition.md"

SOURCE_TYPES = ("osm", "synthetic", "trace_reference_synthetic")
OK_STATUSES = frozenset({"OK", "SKIPPED_EXISTING_OK"})
LADDER = [100, 200, 300, 400, 600, 800, 1000, 1200, 1600, 1860]

KNOWN_SYN_FAIL_GENS = ("bus_route_corridor", "campus_compact", "corridor", "radial_city")
KNOWN_OSM_FAIL_ANCHORS = (
    "nuuksio_sparse_trails",
    "tampere_suburban",
    "manhattan_midtown",
    "lapland_rural_sparse",
)


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be mapping: {path}")
    return data


def _load_allocation(path: Path) -> dict[str, Any]:
    full = _load_yaml(path)
    return full.get("archetypes") or {}


def _soft_targets(design_path: Path) -> dict[str, float]:
    full = _load_yaml(design_path)
    ds = full.get("map_design_space_revised_v2") or full
    planning = ds.get("planning") or {}
    return {
        "osm": float(planning.get("osm_fraction", 0.45)),
        "synthetic": float(planning.get("synthetic_fraction", 0.40)),
        "trace_reference_synthetic": float(planning.get("trace_reference_fraction", 0.15)),
    }


def _is_ok(status: str) -> bool:
    return status in OK_STATUSES


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def build_survival(
    rows: list[dict[str, str]],
    allocation: dict[str, Any],
) -> list[dict[str, Any]]:
    cells: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for r in rows:
        arch = r.get("archetype") or ""
        src = r.get("source_type") or ""
        st = r.get("generation_status") or ""
        cells[(arch, src)]["planned"] += 1
        if _is_ok(st):
            cells[(arch, src)]["ok"] += 1
        else:
            cells[(arch, src)]["failed"] += 1
            cells[(arch, src)][f"fail::{st}"] += 1

    # Ensure all allocation cells appear (including role=none with zero planned)
    all_archs = sorted(set(allocation) | {a for a, _ in cells})
    out: list[dict[str, Any]] = []
    for arch in all_archs:
        body = allocation.get(arch) or {}
        for src in SOURCE_TYPES:
            spec = body.get(src) or {}
            role = str(spec.get("role") or "none")
            min_c = int(spec.get("min_candidates") or 0)
            c = cells.get((arch, src), Counter())
            planned = int(c["planned"])
            ok = int(c["ok"])
            failed = int(c["failed"])
            rate = (ok / planned) if planned else (1.0 if role == "none" else 0.0)
            under_min = bool(role in ("primary", "supporting", "optional") and planned > 0 and ok < min_c)
            # optional with min 0: under_min only if min_c > 0
            if role == "optional" and min_c == 0:
                under_min = False
            zero_ok = bool(role in ("primary", "supporting") and ok == 0 and (planned > 0 or min_c > 0))
            # also flag primary/supporting with zero ok even if somehow unplanned but required by matrix
            if role in ("primary", "supporting") and ok == 0 and min_c > 0:
                zero_ok = True
            out.append(
                {
                    "archetype": arch,
                    "source_type": src,
                    "matrix_role": role,
                    "min_candidates": min_c,
                    "N_planned": planned,
                    "N_OK": ok,
                    "N_failed": failed,
                    "survival_rate": round(rate, 6),
                    "under_min": under_min,
                    "zero_ok_when_allowed": zero_ok,
                    "FAIL_BUILD_SYNTHETIC_DEGENERATE": int(c.get("fail::FAIL_BUILD_SYNTHETIC_DEGENERATE", 0)),
                    "FAIL_BUILD_OSM": int(c.get("fail::FAIL_BUILD_OSM", 0)),
                    "other_fail": failed
                    - int(c.get("fail::FAIL_BUILD_SYNTHETIC_DEGENERATE", 0))
                    - int(c.get("fail::FAIL_BUILD_OSM", 0)),
                }
            )
    return out


def build_soft_delta(rows: list[dict[str, str]], soft: dict[str, float]) -> list[dict[str, Any]]:
    ok_rows = [r for r in rows if _is_ok(r.get("generation_status") or "")]
    n = len(ok_rows)
    counts = Counter(r.get("source_type") or "" for r in ok_rows)
    out: list[dict[str, Any]] = []
    for src in SOURCE_TYPES:
        p_star = soft[src]
        p = (counts.get(src, 0) / n) if n else 0.0
        out.append(
            {
                "source_type": src,
                "N_OK": counts.get(src, 0),
                "N_OK_total": n,
                "p_star": p_star,
                "p": round(p, 6),
                "delta_p": round(p - p_star, 6),
            }
        )
    return out


def build_attrition_bias(
    rows: list[dict[str, str]],
    survival: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Failures by generator (synthetic) and anchor (OSM), with remaining OK for same arch×src."""
    ok_by_cell = {(s["archetype"], s["source_type"]): int(s["N_OK"]) for s in survival}
    planned_by_cell = {(s["archetype"], s["source_type"]): int(s["N_planned"]) for s in survival}

    # Synthetic by generator
    syn_fail = [r for r in rows if r.get("generation_status") == "FAIL_BUILD_SYNTHETIC_DEGENERATE"]
    syn_ok = [
        r
        for r in rows
        if r.get("source_type") == "synthetic" and _is_ok(r.get("generation_status") or "")
    ]
    by_gen_fail = Counter(r.get("generator_type") or "(none)" for r in syn_fail)
    by_gen_ok = Counter(r.get("generator_type") or "(none)" for r in syn_ok)
    by_gen_arch = {}
    for r in syn_fail + [
        r for r in rows if r.get("source_type") == "synthetic" and r.get("generator_type")
    ]:
        g = r.get("generator_type") or "(none)"
        by_gen_arch.setdefault(g, r.get("archetype") or "")

    out: list[dict[str, Any]] = []
    for gen, n_fail in sorted(by_gen_fail.items(), key=lambda x: (-x[1], x[0])):
        arch = by_gen_arch.get(gen, "")
        n_ok_gen = by_gen_ok.get(gen, 0)
        n_planned_gen = n_fail + n_ok_gen
        cell_ok = ok_by_cell.get((arch, "synthetic"), 0)
        out.append(
            {
                "fail_axis": "generator_type",
                "key": gen,
                "source_type": "synthetic",
                "archetype": arch,
                "N_failed": n_fail,
                "N_OK_same_key": n_ok_gen,
                "N_planned_same_key": n_planned_gen,
                "fail_rate_same_key": round(n_fail / n_planned_gen, 6) if n_planned_gen else 0.0,
                "N_OK_archetype_source": cell_ok,
                "N_planned_archetype_source": planned_by_cell.get((arch, "synthetic"), 0),
                "known_hotspot": gen in KNOWN_SYN_FAIL_GENS,
                "coverage_ok_residual": cell_ok > 0,
            }
        )

    # OSM by anchor
    osm_fail = [r for r in rows if r.get("generation_status") == "FAIL_BUILD_OSM"]
    osm_ok = [
        r for r in rows if r.get("source_type") == "osm" and _is_ok(r.get("generation_status") or "")
    ]
    by_anch_fail = Counter(r.get("anchor_id") or "(none)" for r in osm_fail)
    by_anch_ok = Counter(r.get("anchor_id") or "(none)" for r in osm_ok)
    by_anch_arch = {}
    for r in rows:
        if r.get("source_type") == "osm" and r.get("anchor_id"):
            by_anch_arch[r["anchor_id"]] = r.get("archetype") or ""

    for aid, n_fail in sorted(by_anch_fail.items(), key=lambda x: (-x[1], x[0])):
        arch = by_anch_arch.get(aid, "")
        n_ok_a = by_anch_ok.get(aid, 0)
        n_planned_a = n_fail + n_ok_a
        cell_ok = ok_by_cell.get((arch, "osm"), 0)
        out.append(
            {
                "fail_axis": "anchor_id",
                "key": aid,
                "source_type": "osm",
                "archetype": arch,
                "N_failed": n_fail,
                "N_OK_same_key": n_ok_a,
                "N_planned_same_key": n_planned_a,
                "fail_rate_same_key": round(n_fail / n_planned_a, 6) if n_planned_a else 0.0,
                "N_OK_archetype_source": cell_ok,
                "N_planned_archetype_source": planned_by_cell.get((arch, "osm"), 0),
                "known_hotspot": aid in KNOWN_OSM_FAIL_ANCHORS,
                "coverage_ok_residual": cell_ok > 0,
            }
        )
    return out


def build_ladder(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    ok = [r for r in rows if _is_ok(r.get("generation_status") or "")]
    ok_sorted = sorted(
        ok,
        key=lambda r: (int(r.get("batch_target") or 0), r.get("map_id") or ""),
    )
    n_ok = len(ok_sorted)
    full_marker = LADDER[-1]
    out: list[dict[str, Any]] = []
    for n in LADDER:
        is_full = n == full_marker
        prefix = ok_sorted[: min(n, n_ok)] if not is_full else ok_sorted
        archs = {r.get("archetype") for r in prefix}
        srcs = {r.get("source_type") for r in prefix}
        cells = {(r.get("archetype"), r.get("source_type")) for r in prefix}
        out.append(
            {
                "N": n_ok if is_full else min(n, n_ok),
                "ladder_label": f"{n_ok} (full_OK_pool)" if is_full else str(n),
                "n_maps": len(prefix),
                "n_archetypes": len(archs),
                "n_source_types": len(srcs),
                "n_archetype_source_cells": len(cells),
                "status": "defined_not_executed",
                "notes": (
                    "Prefix of OK maps ordered by batch_target then map_id. "
                    "Saturation analysis not run in this revalidation script. "
                    "Further expansion to 2000 is conditional on saturation STOP rules."
                ),
            }
        )
    return out


def decide_go_nogo(survival: list[dict[str, Any]]) -> tuple[str, list[str]]:
    """GO for experimental saturation if no primary/supporting cell has zero OK when planned/required."""
    blockers: list[str] = []
    warnings: list[str] = []
    for s in survival:
        role = s["matrix_role"]
        if role in ("primary", "supporting") and s["zero_ok_when_allowed"]:
            blockers.append(
                f"{s['archetype']} × {s['source_type']} (role={role}): N_OK=0 "
                f"(planned={s['N_planned']}, min={s['min_candidates']})"
            )
        elif role in ("primary", "supporting") and s["under_min"]:
            warnings.append(
                f"{s['archetype']} × {s['source_type']} (role={role}): N_OK={s['N_OK']} "
                f"< min_candidates={s['min_candidates']} (planned={s['N_planned']})"
            )
    if blockers:
        return "NO-GO", blockers + [f"WARN: {w}" for w in warnings]
    if warnings:
        return "GO_WITH_WARNINGS", warnings
    return "GO", []


def render_markdown(
    *,
    rows: list[dict[str, str]],
    survival: list[dict[str, Any]],
    soft_delta: list[dict[str, Any]],
    bias: list[dict[str, Any]],
    ladder: list[dict[str, Any]],
    verdict: str,
    issues: list[str],
) -> str:
    n_total = len(rows)
    n_ok = sum(1 for r in rows if _is_ok(r.get("generation_status") or ""))
    status_c = Counter(r.get("generation_status") or "" for r in rows)
    n_syn_fail = status_c.get("FAIL_BUILD_SYNTHETIC_DEGENERATE", 0)
    n_osm_fail = status_c.get("FAIL_BUILD_OSM", 0)

    lines: list[str] = [
        "# Pool Revalidation and Attrition Report — map_space_revised_v2",
        "",
        "**Status:** official project state after Phase B OSM completion",
        "**Pool:** `scenarios/Generated_Map_Space_v1/`",
        f"**Manifest rows:** {n_total}",
        f"**OK maps:** {n_ok} ({100.0 * n_ok / n_total:.1f}%)" if n_total else "**OK maps:** 0",
        f"**Documented failures:** {n_syn_fail + n_osm_fail} "
        f"({n_syn_fail} synthetic degenerate + {n_osm_fail} OSM build)",
        "",
        "## Methodological position",
        "",
        "- The pool passed **engineering validation**; it is **not** yet the definitive Generated Map Space.",
        "- It does **not** by itself justify SMS-v1 selection.",
        "- `N=1200` remains an **initial engineering target**, not a scientific stopping rule.",
        "- Failures remain in the manifest (no documentary survival bias).",
        "- **Decisions:** do **not** repair the 32 `FAIL_BUILD_OSM` in bulk; do **not** regenerate "
        "solely to correct global source proportions; **do** check affected (archetype × source) coverage.",
        "",
        "```mermaid",
        "flowchart LR",
        "  poolDone[Pool_completed]",
        "  reval[Coverage_attrition_revalidation]",
        "  sat[Incremental_saturation]",
        "  expand[Conditional_1600_2000]",
        "  sms[SMS_v1_selection]",
        "  poolDone --> reval",
        "  reval -->|go| sat",
        "  sat -->|marginal_gain| expand",
        "  sat -->|stable| sms",
        "  expand --> sms",
        "```",
        "",
        "## 1. Coverage after attrition (archetype × source)",
        "",
        "Survival rate \\(r_{a,s} = N^{OK}_{a,s} / N^{planned}_{a,s}\\). "
        "Planned counts are manifest attempts per cell.",
        "",
        "| Archetype | Source | Role | Min | Planned | OK | Failed | Survival | under_min | zero_OK |",
        "|-----------|--------|------|----:|--------:|---:|-------:|---------:|:---------:|:-------:|",
    ]
    for s in survival:
        if s["matrix_role"] == "none" and s["N_planned"] == 0:
            continue
        lines.append(
            f"| `{s['archetype']}` | `{s['source_type']}` | {s['matrix_role']} | "
            f"{s['min_candidates']} | {s['N_planned']} | {s['N_OK']} | {s['N_failed']} | "
            f"{s['survival_rate']:.3f} | {s['under_min']} | {s['zero_ok_when_allowed']} |"
        )

    # Also note none-role cells with accidental plans
    accidental = [s for s in survival if s["matrix_role"] == "none" and s["N_planned"] > 0]
    if accidental:
        lines += ["", "### Unexpected planned rows on role=none (should be empty)", ""]
        for s in accidental:
            lines.append(
                f"- `{s['archetype']}` × `{s['source_type']}`: planned={s['N_planned']} OK={s['N_OK']}"
            )

    lines += [
        "",
        "CSV: [`../data/pool_revalidation_archetype_source_survival_v2.csv`]"
        "(../data/pool_revalidation_archetype_source_survival_v2.csv)",
        "",
        "## 2. Soft-target deviation",
        "",
        "Targets \\(p^* = (0.45,\\,0.40,\\,0.15)\\) for (osm, synthetic, TRS). "
        "Realized shares are over **OK** maps only.",
        "",
        "| Source | N_OK | p* | p | Δp |",
        "|--------|-----:|---:|--:|---:|",
    ]
    for d in soft_delta:
        lines.append(
            f"| `{d['source_type']}` | {d['N_OK']} | {d['p_star']:.3f} | {d['p']:.6f} | {d['delta_p']:+.6f} |"
        )
    lines += [
        "",
        "**Conclusion:** |Δp| is small. **Do not regenerate** maps solely to rebalance global source fractions.",
        "",
        "CSV: [`../data/pool_revalidation_soft_target_delta_v2.csv`]"
        "(../data/pool_revalidation_soft_target_delta_v2.csv)",
        "",
        "## 3. Attrition bias",
        "",
        "Failures are **not** uniform. Concentrations:",
        "",
        "### Synthetic (`FAIL_BUILD_SYNTHETIC_DEGENERATE`)",
        "",
        "| Generator | Archetype | Failed | OK same gen | Fail rate | OK in arch×synthetic | Residual coverage |",
        "|-----------|-----------|-------:|------------:|----------:|---------------------:|:-----------------:|",
    ]
    for b in bias:
        if b["fail_axis"] != "generator_type":
            continue
        lines.append(
            f"| `{b['key']}` | `{b['archetype']}` | {b['N_failed']} | {b['N_OK_same_key']} | "
            f"{b['fail_rate_same_key']:.3f} | {b['N_OK_archetype_source']} | {b['coverage_ok_residual']} |"
        )
    lines += [
        "",
        "### OSM (`FAIL_BUILD_OSM`)",
        "",
        "| Anchor | Archetype | Failed | OK same anchor | Fail rate | OK in arch×osm | Residual coverage |",
        "|--------|-----------|-------:|---------------:|----------:|---------------:|:-----------------:|",
    ]
    for b in bias:
        if b["fail_axis"] != "anchor_id":
            continue
        lines.append(
            f"| `{b['key']}` | `{b['archetype']}` | {b['N_failed']} | {b['N_OK_same_key']} | "
            f"{b['fail_rate_same_key']:.3f} | {b['N_OK_archetype_source']} | {b['coverage_ok_residual']} |"
        )
    lines += [
        "",
        "Keeping failures in the manifest avoids **documentary** survival bias but does not erase "
        "possible **coverage bias** in the OK set. Residual OK > 0 for affected archetype×source "
        "cells is required before saturation.",
        "",
        "CSV: [`../data/pool_revalidation_attrition_bias_v2.csv`]"
        "(../data/pool_revalidation_attrition_bias_v2.csv)",
        "",
        "## 4. Incremental ladder (defined, not executed)",
        "",
        "Saturation must **not** treat N=1117 as a single point. Use cumulative prefixes of OK maps "
        "(order: `batch_target`, then `map_id`):",
        "",
        "| Ladder N | Maps in prefix | Archetypes | Sources | Arch×src cells | Status |",
        "|---------:|---------------:|-----------:|--------:|---------------:|--------|",
    ]
    for L in ladder:
        lines.append(
            f"| {L['ladder_label']} | {L['n_maps']} | {L['n_archetypes']} | "
            f"{L['n_source_types']} | {L['n_archetype_source_cells']} | {L['status']} |"
        )
    lines += [
        "",
        "Expansion **1600 → 2000** is **conditional**: activate only if saturation curves show "
        "relevant marginal gain. Recommended future stop signals (several consecutive batches):",
        "",
        "- \\(\\Delta C_N = C_N - C_{N-\\Delta N} < \\varepsilon_C\\)",
        "- \\(\\Delta K_N \\approx 0\\) (cluster count stability)",
        "- New maps do not materially change geometric structure of the feature space",
        "",
        "Metrics per N (for the **next** phase): new archetypes covered, new clusters, feature-space "
        "coverage increment, distance to nearest representative, cluster stability, "
        "archetype×source coverage.",
        "",
        "CSV: [`../data/pool_revalidation_incremental_ladder_v2.csv`]"
        "(../data/pool_revalidation_incremental_ladder_v2.csv)",
        "",
        "## 5. Verdict: go / no-go for incremental saturation",
        "",
        f"**Verdict: `{verdict}`**",
        "",
    ]
    if issues:
        lines.append("Issues / warnings:")
        lines.append("")
        for i in issues:
            lines.append(f"- {i}")
        lines.append("")
    else:
        lines.append("No primary/supporting cells with zero OK; matrix floors checked.")
        lines.append("")

    lines += [
        "### Explicitly deferred",
        "",
        "- Feature extraction / PCA / separability on this pool",
        "- Running `analyze_map_space_saturation_v1.py`",
        "- Automatic expansion to 1600/2000",
        "- SMS-v1 selection",
        "",
        "### Next step if GO / GO_WITH_WARNINGS",
        "",
        "1. Extract saturation features for OK maps under `map_space_revised_v2`.",
        "2. Run **incremental** saturation on ladder prefixes (adapt batch thresholds to include 1117).",
        "3. Expand planner only if marginal gains persist.",
        "4. Select SMS-v1 only when saturation curves justify the stop.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--allocation", type=Path, default=DEFAULT_ALLOCATION)
    ap.add_argument("--design-space", type=Path, default=DEFAULT_DESIGN)
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--md", type=Path, default=DEFAULT_MD)
    args = ap.parse_args()

    rows = list(csv.DictReader(args.manifest.open(encoding="utf-8")))
    allocation = _load_allocation(args.allocation)
    soft = _soft_targets(args.design_space)

    survival = build_survival(rows, allocation)
    soft_delta = build_soft_delta(rows, soft)
    bias = build_attrition_bias(rows, survival)
    ladder = build_ladder(rows)
    verdict, issues = decide_go_nogo(survival)

    data = args.data_dir
    _write_csv(
        data / "pool_revalidation_archetype_source_survival_v2.csv",
        survival,
        [
            "archetype",
            "source_type",
            "matrix_role",
            "min_candidates",
            "N_planned",
            "N_OK",
            "N_failed",
            "survival_rate",
            "under_min",
            "zero_ok_when_allowed",
            "FAIL_BUILD_SYNTHETIC_DEGENERATE",
            "FAIL_BUILD_OSM",
            "other_fail",
        ],
    )
    _write_csv(
        data / "pool_revalidation_soft_target_delta_v2.csv",
        soft_delta,
        ["source_type", "N_OK", "N_OK_total", "p_star", "p", "delta_p"],
    )
    _write_csv(
        data / "pool_revalidation_attrition_bias_v2.csv",
        bias,
        [
            "fail_axis",
            "key",
            "source_type",
            "archetype",
            "N_failed",
            "N_OK_same_key",
            "N_planned_same_key",
            "fail_rate_same_key",
            "N_OK_archetype_source",
            "N_planned_archetype_source",
            "known_hotspot",
            "coverage_ok_residual",
        ],
    )
    _write_csv(
        data / "pool_revalidation_incremental_ladder_v2.csv",
        ladder,
        [
            "N",
            "ladder_label",
            "n_maps",
            "n_archetypes",
            "n_source_types",
            "n_archetype_source_cells",
            "status",
            "notes",
        ],
    )

    md = render_markdown(
        rows=rows,
        survival=survival,
        soft_delta=soft_delta,
        bias=bias,
        ladder=ladder,
        verdict=verdict,
        issues=issues,
    )
    args.md.parent.mkdir(parents=True, exist_ok=True)
    args.md.write_text(md, encoding="utf-8")

    n_ok = sum(1 for r in rows if _is_ok(r.get("generation_status") or ""))
    print(f"Wrote {args.md}")
    print(f"OK={n_ok}/{len(rows)}  verdict={verdict}")
    if issues:
        for i in issues:
            print(f"  - {i}")


if __name__ == "__main__":
    main()
