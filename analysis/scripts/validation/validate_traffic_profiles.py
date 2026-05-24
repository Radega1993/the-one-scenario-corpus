#!/usr/bin/env python3
"""
Validate Traffic Profiles v1.0 (TP01–TP12) for corpus_v2 and summarize benchmark readiness.

Outputs (default under scenarios/analysis/):
  data/traffic_profile_windows.csv   — per-scenario simulation / generation windows
  data/tp_validation_settings.csv  — per-file settings check (pass/fail + notes)
  data/tp_validation_summary.csv   — per-TP metric aggregates (global + connected-only)
  data/tp_validation_by_base.csv   — per base scenario: spread of delivery across TPs
  reports/tp_validation_report.md  — human-readable closure report

Does not modify corpus files or existing simulation reports.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

# Reuse canonical TP definitions from the generator (single source of truth).
from lib.traffic_profile_generator import (  # noqa: E402
    PROFILE_ORDER,
    build_events_block,
    infer_end_time,
    infer_total_hosts,
    parse_simple_settings,
    profile_ttl_minutes,
)

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))
from lib.paths import CORPUS_V2, DATA_DIR, REPORTS_ANALYSIS_DIR, SCENARIOS_DIR  # noqa: E402
from lib.report_paths import TP_VALIDATION_REPORT  # noqa: E402

DEFAULT_CORPUS = CORPUS_V2
DEFAULT_MANIFEST = DEFAULT_CORPUS / "manifest.csv"
DEFAULT_DATA = DATA_DIR
DEFAULT_REPORTS = REPORTS_ANALYSIS_DIR

PROFILE_IDS = [tp for tp, _ in PROFILE_ORDER]

# Fields we compare between disk and generator (Events block + TTL).
CHECK_KEYS = [
    "Group.msgTtl",
    "Events.nrof",
    "Events1.interval",
    "Events1.size",
    "Events1.hosts",
    "Events1.tohosts",
    "Events1.time",
    "Events2.interval",
    "Events2.size",
]


def _parse_scenario_name(name: str) -> tuple[str, str]:
    m = re.search(r"__(TP\d{2}_[A-Za-z0-9]+)$", name)
    if not m:
        return name, ""
    base = name[: m.start()]
    tp_label = m.group(1)
    tp_id = tp_label.split("_", 1)[0]
    return base, tp_id


def _infer_group_sizes(kv: dict[str, str]) -> tuple[int | None, int | None]:
    g1 = kv.get("Group1.nrofHosts")
    g2 = kv.get("Group2.nrofHosts")
    try:
        return (int(g1) if g1 else None, int(g2) if g2 else None)
    except ValueError:
        return None, None


def _tp07_window(end_t: float) -> tuple[int, int]:
    t0 = int(end_t * 0.20)
    t1 = int(end_t * 0.28)
    if t1 <= t0 + 30:
        t1 = min(int(end_t * 0.95), t0 + max(120, int(end_t * 0.05)))
    return t0, t1


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _fnum(x: Any) -> float | None:
    if x is None or x == "":
        return None
    try:
        v = float(x)
        if v != v:  # NaN
            return None
        return v
    except (TypeError, ValueError):
        return None


def check_settings_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    kv = parse_simple_settings(text)
    scenario = kv.get("Scenario.name", path.stem)
    base, tp_id = _parse_scenario_name(scenario)
    if tp_id not in PROFILE_IDS:
        return {
            "settings_file": str(path),
            "scenario_name": scenario,
            "traffic_profile_id": tp_id,
            "status": "fail",
            "mismatches": "unknown_traffic_profile",
        }

    n = infer_total_hosts(kv)
    end_t = infer_end_time(kv)
    g1, g2 = _infer_group_sizes(kv)
    if n is None:
        return {
            "settings_file": str(path),
            "scenario_name": scenario,
            "traffic_profile_id": tp_id,
            "status": "fail",
            "mismatches": "cannot_infer_n_hosts",
        }

    expected_block, _ = build_events_block(tp_id, n, end_t, g1, g2)
    expected_kv = parse_simple_settings(expected_block)
    expected_kv["Group.msgTtl"] = str(profile_ttl_minutes(tp_id, base))

    mismatches: list[str] = []
    for key in CHECK_KEYS:
        exp = expected_kv.get(key)
        if exp is None:
            continue
        got = kv.get(key)
        if got is None:
            mismatches.append(f"missing:{key}")
        elif got.replace(" ", "") != exp.replace(" ", ""):
            mismatches.append(f"{key}: got={got!r} exp={exp!r}")

    ttl_lines = re.findall(r"^Group\d*\.msgTtl\s*=\s*(\S+)", text, flags=re.MULTILINE)
    exp_ttl = str(profile_ttl_minutes(tp_id, base))
    for t in ttl_lines:
        if t != exp_ttl:
            mismatches.append(f"Group*.msgTtl inconsistent: {t} != {exp_ttl}")
            break

    return {
        "settings_file": str(path),
        "scenario_name": scenario,
        "traffic_profile_id": tp_id,
        "n_hosts": n,
        "Scenario.endTime": int(end_t),
        "status": "ok" if not mismatches else "fail",
        "mismatches": "; ".join(mismatches),
    }


def build_windows_table(settings_paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in settings_paths:
        kv = parse_simple_settings(path.read_text(encoding="utf-8", errors="replace"))
        scenario = kv.get("Scenario.name", path.stem)
        base, tp_id = _parse_scenario_name(scenario)
        end_t = infer_end_time(kv)
        ttl_min = (
            profile_ttl_minutes(tp_id, base)
            if tp_id in PROFILE_IDS
            else kv.get("Group.msgTtl", "")
        )
        if tp_id == "TP07":
            t0, t1 = _tp07_window(end_t)
            gen_start, gen_end = t0, t1
            gen_note = "burst_only"
        else:
            gen_start, gen_end = 0.0, end_t
            gen_note = "full_simulation"
        rows.append(
            {
                "scenario_name": scenario,
                "scenario_base": base,
                "traffic_profile_id": tp_id,
                "sim_end_time_s": int(end_t),
                "traffic_gen_start_s": gen_start,
                "traffic_gen_end_s": gen_end,
                "traffic_gen_fraction": round((gen_end - gen_start) / end_t, 4) if end_t else "",
                "traffic_gen_note": gen_note,
                "Group.msgTtl_minutes": ttl_min,
                "msg_ttl_seconds": int(ttl_min) * 60 if str(ttl_min).isdigit() else "",
                "Report.warmup_s": kv.get("Report.warmup", "0"),
            }
        )
    return rows


def summarize_metrics(
    output_metrics: Path,
    indirect_features: Path,
) -> tuple[list[dict], list[dict], dict[str, Any]]:
    om = _read_csv(output_metrics)
    ind = {r["scenario"]: r for r in _read_csv(indirect_features)}

    by_tp_global: dict[str, list[dict]] = defaultdict(list)
    by_tp_connected: dict[str, list[dict]] = defaultdict(list)
    by_base: dict[str, list[dict]] = defaultdict(list)

    for row in om:
        scen = row.get("scenario", "")
        base, tp_id = _parse_scenario_name(scen)
        if not tp_id:
            continue
        dr = _fnum(row.get("delivery_ratio"))
        lat = _fnum(row.get("latency_mean"))
        drop = _fnum(row.get("drop_ratio"))
        oh = _fnum(row.get("overhead_ratio"))
        enc = _fnum(ind.get(scen, {}).get("total_encounters"))
        rec = {
            "scenario": scen,
            "scenario_base": base,
            "traffic_profile_id": tp_id,
            "delivery_ratio": dr,
            "latency_mean": lat,
            "drop_ratio": drop,
            "overhead_ratio": oh,
            "total_encounters": enc,
        }
        by_tp_global[tp_id].append(rec)
        by_base[base].append(rec)
        if enc is not None and enc > 0:
            by_tp_connected[tp_id].append(rec)

    def agg(rows: list[dict], field: str) -> dict[str, float | int | str]:
        vals = [r[field] for r in rows if r.get(field) is not None]
        if not vals:
            return {"n": len(rows), "mean": "", "std": ""}
        return {
            "n": len(rows),
            "mean": round(mean(vals), 4),
            "std": round(pstdev(vals), 4) if len(vals) > 1 else 0.0,
        }

    summary_rows: list[dict] = []
    for tp_id, _ in PROFILE_ORDER:
        g = by_tp_global.get(tp_id, [])
        c = by_tp_connected.get(tp_id, [])
        for view, rows in (("global", g), ("connected_only", c)):
            summary_rows.append(
                {
                    "traffic_profile_id": tp_id,
                    "view": view,
                    "n_scenarios": len(rows),
                    **{f"delivery_ratio_{k}": v for k, v in agg(rows, "delivery_ratio").items() if k != "n"},
                    **{f"latency_mean_{k}": v for k, v in agg(rows, "latency_mean").items() if k != "n"},
                    **{f"drop_ratio_{k}": v for k, v in agg(rows, "drop_ratio").items() if k != "n"},
                    "n": len(rows),
                }
            )

    base_rows: list[dict] = []
    for base, rows in sorted(by_base.items()):
        drs = [r["delivery_ratio"] for r in rows if r.get("delivery_ratio") is not None]
        if len(drs) < 2:
            spread = 0.0
        else:
            spread = max(drs) - min(drs)
        base_rows.append(
            {
                "scenario_base": base,
                "n_profiles": len(rows),
                "delivery_ratio_min": round(min(drs), 4) if drs else "",
                "delivery_ratio_max": round(max(drs), 4) if drs else "",
                "delivery_ratio_spread": round(spread, 4),
                "n_disconnected_profiles": sum(
                    1 for r in rows if r.get("total_encounters") is not None and r["total_encounters"] == 0
                ),
            }
        )

    meta = {
        "n_output_metrics": len(om),
        "n_with_indirect": sum(1 for r in om if r.get("scenario") in ind),
        "n_disconnected_scenarios": sum(
            1
            for r in om
            if _fnum(ind.get(r.get("scenario", ""), {}).get("total_encounters")) == 0
        ),
        "n_connected_scenarios": sum(
            1
            for r in om
            if (_fnum(ind.get(r.get("scenario", ""), {}).get("total_encounters")) or 0) > 0
        ),
    }
    return summary_rows, base_rows, meta


def write_report(
    path: Path,
    *,
    settings_checks: list[dict],
    windows_n: int,
    summary_rows: list[dict],
    base_rows: list[dict],
    meta: dict[str, Any],
    manifest_n: int,
    settings_n: int,
) -> None:
    fails = [r for r in settings_checks if r["status"] != "ok"]
    n_ok = len(settings_checks) - len(fails)

    lines = [
        "# Traffic Profiles v1.0 — validation report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Corpus integrity",
        "",
        f"- Settings files scanned: **{settings_n}**",
        f"- Manifest rows: **{manifest_n}**",
        f"- Settings vs generator spec: **{n_ok}/{len(settings_checks)} OK**",
        f"- Window table rows: **{windows_n}**",
        "",
        "## Simulation metrics coverage",
        "",
        f"- Rows in `output_metrics.csv`: **{meta.get('n_output_metrics', 0)}**",
        f"- Scenarios with `total_encounters > 0`: **{meta.get('n_connected_scenarios', 0)}**",
        f"- Disconnected control (`total_encounters = 0`): **{meta.get('n_disconnected_scenarios', 0)}**",
        "",
    ]

    if fails:
        lines += [
            "## Settings mismatches (action required)",
            "",
            f"**{len(fails)}** files differ from `lib/traffic_profile_generator.py`.",
            "",
            "| scenario | mismatches |",
            "|---|---|",
        ]
        for r in fails[:20]:
            lines.append(f"| `{r['scenario_name']}` | {r['mismatches']} |")
        if len(fails) > 20:
            lines.append(f"| … | (+{len(fails) - 20} more in `data/tp_validation_settings.csv`) |")
        lines.append("")

    lines += [
        "## Per-profile aggregates (global view)",
        "",
        "| TP | n | mean delivery | std delivery | mean latency (s) | mean drop |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for tp_id, _ in PROFILE_ORDER:
        row = next(
            (r for r in summary_rows if r["traffic_profile_id"] == tp_id and r["view"] == "global"),
            None,
        )
        if not row:
            continue
        lines.append(
            f"| {tp_id} | {row['n']} | {row.get('delivery_ratio_mean', '')} | "
            f"{row.get('delivery_ratio_std', '')} | {row.get('latency_mean_mean', '')} | "
            f"{row.get('drop_ratio_mean', '')} |"
        )

    lines += [
        "",
        "## Per-profile aggregates (connected only, `total_encounters > 0`)",
        "",
        "| TP | n | mean delivery | std delivery | mean latency (s) | mean drop |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for tp_id, _ in PROFILE_ORDER:
        row = next(
            (r for r in summary_rows if r["traffic_profile_id"] == tp_id and r["view"] == "connected_only"),
            None,
        )
        if not row:
            continue
        lines.append(
            f"| {tp_id} | {row['n']} | {row.get('delivery_ratio_mean', '')} | "
            f"{row.get('delivery_ratio_std', '')} | {row.get('latency_mean_mean', '')} | "
            f"{row.get('drop_ratio_mean', '')} |"
        )

    spreads = [_fnum(r.get("delivery_ratio_spread")) for r in base_rows]
    spreads = [s for s in spreads if s is not None]
    if spreads:
        lines += [
            "",
            "## Traffic-profile separation by base scenario",
            "",
            f"- Mean delivery spread across 12 TPs (max−min per base): **{mean(spreads):.4f}**",
            f"- Bases with spread < 0.05 (weak TP differentiation): "
            f"**{sum(1 for s in spreads if s < 0.05)}** / {len(spreads)}",
            "",
            "Full table: `data/tp_validation_by_base.csv`.",
        ]

    lines += [
        "",
        "## Methodology pointers",
        "",
        "- Closure document: `scenarios/internal/17-benchmark_methodology_closure.md`",
        "- Profile rationale: `scenarios/internal/16-traffic_profiles_v1_justification.md`",
        "- Generator (source of truth): `scenarios/analysis/lib/traffic_profile_generator.py`",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate TP01–TP12 and summarize benchmark metrics.")
    ap.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    ap.add_argument("--output-metrics", type=Path, default=DEFAULT_DATA / "output_metrics.csv")
    ap.add_argument("--indirect-features", type=Path, default=DEFAULT_DATA / "indirect_features_diego.csv")
    ap.add_argument("--skip-settings", action="store_true")
    ap.add_argument("--skip-metrics", action="store_true")
    args = ap.parse_args()

    settings_paths = sorted(args.corpus_dir.rglob("*.settings"))
    manifest_rows = _read_csv(args.manifest)

    if len(settings_paths) != 720:
        print(f"Warning: expected 720 settings, found {len(settings_paths)}", file=sys.stderr)
    if manifest_rows and len(manifest_rows) != len(settings_paths):
        print(
            f"Warning: manifest rows ({len(manifest_rows)}) != settings files ({len(settings_paths)})",
            file=sys.stderr,
        )

    settings_checks: list[dict] = []
    if not args.skip_settings:
        for p in settings_paths:
            settings_checks.append(check_settings_file(p))
        _write_csv(args.data_dir / "tp_validation_settings.csv", settings_checks)
        windows = build_windows_table(settings_paths)
        _write_csv(args.data_dir / "traffic_profile_windows.csv", windows)
    else:
        windows = []

    summary_rows: list[dict] = []
    base_rows: list[dict] = []
    meta: dict[str, Any] = {}
    if not args.skip_metrics and args.output_metrics.exists():
        summary_rows, base_rows, meta = summarize_metrics(args.output_metrics, args.indirect_features)
        _write_csv(args.data_dir / "tp_validation_summary.csv", summary_rows)
        _write_csv(args.data_dir / "tp_validation_by_base.csv", base_rows)
    elif not args.skip_metrics:
        print(f"Metrics file not found: {args.output_metrics}", file=sys.stderr)

    out_report = TP_VALIDATION_REPORT if args.reports_dir == DEFAULT_REPORTS else args.reports_dir / "tp_validation_report.md"
    write_report(
        out_report,
        settings_checks=settings_checks,
        windows_n=len(windows),
        summary_rows=summary_rows,
        base_rows=base_rows,
        meta=meta,
        manifest_n=len(manifest_rows),
        settings_n=len(settings_paths),
    )

    n_fail = sum(1 for r in settings_checks if r["status"] != "ok")
    print(f"Wrote {out_report}")
    if settings_checks:
        print(f"Settings validation: {len(settings_checks) - n_fail}/{len(settings_checks)} OK")
    if summary_rows:
        print(f"TP summary rows: {len(summary_rows)}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
