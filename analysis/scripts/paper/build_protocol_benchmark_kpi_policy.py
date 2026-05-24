#!/usr/bin/env python3
"""Build protocol benchmark KPI policy and definitions CSV for corpus_v2."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import CORPUS_V2, DATA_DIR, REPORTS_ANALYSIS_DIR  # noqa: E402
from lib.report_paths import PROTOCOL_BENCHMARK_KPI_POLICY  # noqa: E402

DEFAULT_DATA = DATA_DIR
DEFAULT_REPORTS = REPORTS_ANALYSIS_DIR
DEFAULT_MANIFEST_REVISION = CORPUS_V2 / "manifest_revision.csv"

CORE_KPIS = [
    ("delivery_ratio", "maximize", "Primary routing effectiveness"),
    ("overhead_ratio", "minimize", "Replication cost"),
    ("latency_mean", "minimize", "Delivery delay (delivered messages only)"),
    ("drop_ratio", "minimize", "Buffer/transmission stress"),
]

PROTOCOLS = [
    ("Epidemic", "measured", "Current corpus_v2 router in all 720 .settings"),
    ("PRoPHET", "pending", "Overlay: protocol_overlays/router_prophet.txt"),
    ("MaxProp", "pending", "Overlay: protocol_overlays/router_maxprop.txt"),
    ("SprayAndWait", "pending", "Overlay: protocol_overlays/router_sprayandwait.txt"),
]

TIERS = [
    ("main", "TP01–TP08 on viable bases; exclude error_probable and configuracion_sospechosa"),
    ("stress", "TP04, TP05, TP09, TP10, TP03 high-load paths; report separately"),
    ("control", "TP12 partition controls; validate isolation not delivery ranking"),
]


def _split_counts(path: Path) -> dict[str, int]:
    if not path.is_file():
        return {}
    df = pd.read_csv(path)
    col = "benchmark_split" if "benchmark_split" in df.columns else None
    if not col:
        return {}
    return df[col].astype(str).value_counts().to_dict()


def build_definitions() -> pd.DataFrame:
    rows: list[dict] = []
    for protocol, status, _ in PROTOCOLS:
        for kpi, direction, _ in CORE_KPIS:
            for tier, _ in TIERS:
                rows.append(
                    {
                        "protocol": protocol,
                        "kpi": kpi,
                        "direction": direction,
                        "tier": tier,
                        "window_policy": "full_simulation_primary",
                        "status": status,
                    }
                )
    return pd.DataFrame(rows)


def write_report(
    path: Path,
    *,
    split_counts: dict[str, int],
    tp_blocked: int,
    definitions: pd.DataFrame,
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Protocol benchmark KPI policy (corpus_v2)",
        "",
        f"Generated: {ts}",
        "",
        "## Executive summary",
        "",
        "- **Corpus:** corpus_v2 — 720 simulations (Epidemic reference router).",
        "- **Comparison scope:** same mobility, map, Traffic Profile; only `Group.router` changes via overlays.",
        "- **Primary metrics window:** full simulation (`valid_start=0`, `valid_end=endTime`) per "
        "[message_analysis_window_policy.md](message_analysis_window_policy.md).",
        "- **Optional sensitivity:** exclude messages with `creation_time >= 0.9 * endTime` (appendix only).",
        "",
        "## Core-4 KPIs (all protocol comparisons)",
        "",
        "| KPI | Direction | Role |",
        "|-----|-----------|------|",
    ]
    for kpi, direction, role in CORE_KPIS:
        lines.append(f"| `{kpi}` | {direction} | {role} |")

    lines.extend(
        [
            "",
            "## Benchmark splits (`manifest_revision.csv`)",
            "",
        ]
    )
    if split_counts:
        lines.append("| Split | Scenarios |")
        lines.append("|-------|----------:|")
        for k, v in sorted(split_counts.items()):
            lines.append(f"| `{k}` | {v} |")
    else:
        lines.append("*(manifest_revision.csv not found — use manual main/stress/control tiers.)*")

    lines.extend(
        [
            "",
            "## Tier reporting rules",
            "",
            "1. **main** — Primary claims and protocol rankings (TP01–TP08, viable bases).",
            "2. **stress** — TP04/05/09/10 and extreme load; never mix with main-tier medians without label.",
            "3. **control** — TP12 cross-group partition; document partition behavior, not delivery leaderboard.",
            "",
            "## Exclusions before ranking",
            "",
            "- `validation_status == error_probable` (missing or corrupt simulation output).",
            "- `validation_status == configuracion_sospechosa` unless explicitly included in sensitivity appendix.",
            "- Zero-contact disconnected bases (document as `valido_extremo`, exclude from latency rankings).",
            "",
            f"- Traffic profiles blocked in KPI summary: **{tp_blocked}** (re-check after re-simulation).",
            "",
            "## Protocols and overlays",
            "",
            "| Protocol | Status | Overlay / notes |",
            "|----------|--------|-----------------|",
        ]
    )
    for protocol, status, note in PROTOCOLS:
        lines.append(f"| {protocol} | {status} | {note} |")

    lines.extend(
        [
            "",
            "## Per-TP KPI guidance",
            "",
            "Use [`traffic_profile_kpi_summary.csv`](../data/traffic_profile_kpi_summary.csv) for "
            "profile-specific primary/secondary KPIs when interpreting Epidemic baseline. "
            "Protocol comparison should still report core-4 on the same scenario subset.",
            "",
            "## Aggregation",
            "",
            "- Report **median** per TP and per family; show IQR or bootstrap CI if seeds available.",
            "- Paired comparison: same `scenario_base` + TP across protocols (720-row join on scenario key).",
            "",
            "## Artifacts",
            "",
            "- Definitions: [`protocol_benchmark_kpi_definitions.csv`](../data/protocol_benchmark_kpi_definitions.csv)",
            "- Traffic profiles: [`traffic_profile_kpi_analysis.md`](traffic_profile_kpi_analysis.md)",
            "- Window policy: [`message_analysis_window_policy.md`](message_analysis_window_policy.md)",
            "- Validation: [`corpus_v2_benchmark_validation.md`](corpus_v2_benchmark_validation.md)",
            "",
            "## Regeneration",
            "",
            "```bash",
            "python3 scenarios/analysis/build_protocol_benchmark_kpi_policy.py",
            "```",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build protocol benchmark KPI policy.")
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    ap.add_argument("--manifest-revision", type=Path, default=DEFAULT_MANIFEST_REVISION)
    args = ap.parse_args()

    split_counts = _split_counts(args.manifest_revision)
    tp_blocked = 0
    tp_path = args.data_dir / "traffic_profile_kpi_summary.csv"
    if tp_path.is_file():
        tdf = pd.read_csv(tp_path)
        if "validation_status" in tdf.columns:
            tp_blocked = int((tdf["validation_status"] == "blocked").sum())

    defs = build_definitions()
    csv_path = args.data_dir / "protocol_benchmark_kpi_definitions.csv"
    defs.to_csv(csv_path, index=False)

    report_path = (
        PROTOCOL_BENCHMARK_KPI_POLICY
        if args.reports_dir == DEFAULT_REPORTS
        else args.reports_dir / "protocol_benchmark_kpi_policy.md"
    )
    write_report(report_path, split_counts=split_counts, tp_blocked=tp_blocked, definitions=defs)

    print(f"Wrote {csv_path} ({len(defs)} rows)")
    print(f"Wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
