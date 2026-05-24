#!/usr/bin/env python3
"""
Validate corpus_v2 benchmark readiness for routing protocol comparison.

Merges manifest + metric CSVs, classifies each scenario, and writes:
  data/corpus_v2_benchmark_validation.csv
  reports/corpus_v2_benchmark_validation.md
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import (  # noqa: E402
    CORPUS_V2,
    DATA_DIR,
    DEFAULT_MANIFEST_V2,
    REPO_ROOT,
)
from lib.report_paths import CORPUS_V2_BENCHMARK_VALIDATION  # noqa: E402

STRESS_TPS = frozenset({"TP04", "TP05", "TP09", "TP10", "TP11"})
EXTREME_BASE_PREFIXES = ("R10_", "R11_", "D1_", "D2_", "D3_", "D4_", "D5_", "D6_", "D7_", "D8_", "D9_")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _parse_flags(val: Any) -> set[str]:
    if pd.isna(val) or val == "":
        return set()
    return {x.strip() for x in str(val).split("|") if x.strip()}


def _is_nan(x: Any) -> bool:
    return x is None or (isinstance(x, float) and pd.isna(x))


def classify_row(row: pd.Series) -> tuple[str, str, str]:
    """Return (validation_status, reason, recommended_action)."""
    flags = _parse_flags(row.get("problem_flags", ""))
    tp = str(row.get("traffic_profile", ""))
    base = str(row.get("base_scenario", ""))
    family = str(row.get("family", ""))
    priority = str(row.get("diagnosis_priority", "") or "")

    dr = row.get("delivery_ratio")
    lat = row.get("latency_mean")
    oh = row.get("overhead_ratio")
    drops = row.get("drop_ratio")
    enc = row.get("total_encounters")
    pct_late = row.get("pct_last_10pct_sim")

    enc_val = 0.0 if _is_nan(enc) else float(enc)
    dr_val = float("nan") if _is_nan(dr) else float(dr)
    drops_val = 0.0 if _is_nan(drops) else float(drops)

    # 1. error_probable
    if _is_nan(dr):
        return (
            "error_probable",
            "missing delivery_ratio (simulation report incomplete or absent)",
            "re_simulate",
        )
    if row.get("_missing_output"):
        return (
            "error_probable",
            "missing row in output_metrics.csv",
            "re_simulate",
        )

    # 2. valido_extremo
    if "STRUCTURAL_PARTITION_VALID" in flags:
        return (
            "valido_extremo",
            "STRUCTURAL_PARTITION_VALID (TP12 / cross-group control)",
            "include_control",
        )
    if tp == "TP12" and dr_val == 0.0:
        return (
            "valido_extremo",
            "TP12 partition control with zero delivery",
            "include_control",
        )
    if enc_val <= 0 and ("ZERO_CONTACTS" in flags or base.startswith(EXTREME_BASE_PREFIXES)):
        return (
            "valido_extremo",
            "disconnected or extreme-base control (ZERO_CONTACTS)",
            "include_control",
        )
    if tp in STRESS_TPS and (
        dr_val == 0.0
        or drops_val >= 50.0
        or "EXTREME_OVERHEAD" in flags
        or "EXTREME_DROPS" in flags
    ):
        return (
            "valido_extremo",
            f"stress traffic profile {tp} (TTL/load/overhead extreme)",
            "include_stress",
        )
    if base.startswith(("R10_", "R11_")) and dr_val == 0.0:
        return (
            "valido_extremo",
            "rural extreme base (R10/R11) with zero delivery by design",
            "document_as_extreme",
        )
    if "MAP_UNDERUSED" in flags and priority != "P0":
        return (
            "valido_extremo",
            "low world grid coverage on roads (MAP_UNDERUSED, mobility on streets)",
            "document_as_extreme",
        )
    if family == "07_traffic":
        return (
            "valido_extremo",
            "07_traffic laboratory family (stress tier)",
            "include_stress",
        )

    # 3. configuracion_sospechosa
    if "ZERO_DELIVERY" in flags and enc_val > 0 and "STRUCTURAL_PARTITION_VALID" not in flags:
        return (
            "configuracion_sospechosa",
            "ZERO_DELIVERY with contacts present (non-structural)",
            "exclude_protocol_ranking",
        )
    if priority == "P0" and (
        "EXTREME_OVERHEAD" in flags or "EXTREME_DROPS" in flags
    ) and tp in ("TP01", "TP02", "TP03", "TP06", "TP07", "TP08"):
        return (
            "configuracion_sospechosa",
            f"P0 extreme outputs on main-tier TP {tp}",
            "exclude_protocol_ranking",
        )
    if flags == {"TP_NOT_DIFFERENTIATING"}:
        return (
            "configuracion_sospechosa",
            "TP_NOT_DIFFERENTIATING (metrics identical across TPs on base)",
            "fix_settings",
        )

    # 4. pendiente_revision
    if priority == "P0":
        hint = str(row.get("recommended_action_hint", "") or "review P0 flags")
        return (
            "pendiente_revision",
            f"P0: {','.join(sorted(flags)) or 'unspecified'}",
            "fix_settings" if "MAP" in hint.upper() else "exclude_protocol_ranking",
        )
    if priority == "P1":
        return (
            "pendiente_revision",
            f"P1: {','.join(sorted(flags))}",
            "fix_settings",
        )
    if _is_nan(lat) and enc_val > 0:
        return (
            "pendiente_revision",
            "latency missing despite contacts (zero deliveries?)",
            "apply_message_window",
        )
    if not _is_nan(pct_late) and float(pct_late) > 15.0:
        return (
            "pendiente_revision",
            f"high late message creation ({float(pct_late):.1f}% in last 10% sim)",
            "apply_message_window",
        )
    if "MAP_TOO_LARGE" in flags or "MAP_UNDERUSED" in flags:
        return (
            "pendiente_revision",
            "spatial/worldSize flags (MAP_TOO_LARGE or MAP_UNDERUSED with P0 context)",
            "fix_settings",
        )

    # 5. ok
    return ("ok", "metrics complete, no P0/P1 flags", "include_main")


def load_and_merge(
    manifest_path: Path,
    data_dir: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load manifest and metric CSVs; return merged frame + completeness stats."""
    m = pd.read_csv(manifest_path)
    expected = len(m)

    def _read(name: str) -> pd.DataFrame:
        p = data_dir / name
        if not p.is_file():
            raise FileNotFoundError(p)
        return pd.read_csv(p)

    out = _read("output_metrics.csv").rename(columns={"scenario": "scenario_name"})
    sp = _read("spatial_occupancy_metrics.csv").rename(columns={"scenario": "scenario_name"})
    ind = _read("indirect_features_diego.csv").rename(columns={"scenario": "scenario_name"})
    msg = _read("message_creation_time_summary.csv")
    use = _read("useful_simulation_time_metrics.csv").rename(columns={"scenario": "scenario_name"})
    diag_path = data_dir / "scenario_diagnosis.csv"
    diag = pd.read_csv(diag_path) if diag_path.is_file() else pd.DataFrame()

    settings_count = sum(1 for _ in CORPUS_V2.rglob("*.settings"))

    completeness: dict[str, Any] = {
        "settings_count": settings_count,
        "manifest_rows": expected,
        "bases": int(m["scenario_base"].nunique()),
        "traffic_profiles": int(m["traffic_profile_id"].nunique()),
        "output_metrics_rows": len(out),
        "spatial_rows": len(sp),
        "indirect_rows": len(ind),
        "message_creation_rows": len(msg),
        "useful_time_rows": len(use),
        "diagnosis_rows": len(diag) if not diag.empty else 0,
    }

    df = m[
        ["scenario_name", "scenario_base", "family", "traffic_profile_id"]
    ].rename(columns={"scenario_base": "base_scenario", "traffic_profile_id": "traffic_profile"})

    df = df.merge(
        out[["scenario_name", "delivery_ratio", "latency_mean", "overhead_ratio", "drop_ratio"]],
        on="scenario_name",
        how="left",
    )
    df["_missing_output"] = df["delivery_ratio"].isna()

    df = df.merge(
        sp[["scenario_name", "final_coverage_pct"]].rename(
            columns={"final_coverage_pct": "spatial_coverage_pct"}
        ),
        on="scenario_name",
        how="left",
    )
    df = df.merge(
        use[["scenario_name", "useful_time_ratio"]],
        on="scenario_name",
        how="left",
    )
    df = df.merge(
        ind[["scenario_name", "contact_time_per_min", "total_encounters"]],
        on="scenario_name",
        how="left",
    )
    if "scenario_name" not in msg.columns and "scenario" in msg.columns:
        msg = msg.rename(columns={"scenario": "scenario_name"})
    df = df.merge(
        msg[["scenario_name", "pct_last_10pct_sim"]],
        on="scenario_name",
        how="left",
    )

    if not diag.empty:
        diag = diag.rename(columns={"scenario": "scenario_name", "tp": "traffic_profile_diag"})
        df = df.merge(
            diag[
                [
                    "scenario_name",
                    "problem_flags",
                    "priority",
                    "recommended_action_hint",
                ]
            ].rename(columns={"priority": "diagnosis_priority"}),
            on="scenario_name",
            how="left",
        )
    else:
        df["problem_flags"] = ""
        df["diagnosis_priority"] = ""
        df["recommended_action_hint"] = ""

    if len(df) != expected:
        raise RuntimeError(f"merged rows {len(df)} != manifest {expected}")

    completeness["merged_rows"] = len(df)
    completeness["null_delivery"] = int(df["delivery_ratio"].isna().sum())
    completeness["zero_delivery"] = int((df["delivery_ratio"] == 0).sum())
    completeness["zero_encounters"] = int((df["total_encounters"] == 0).sum())

    return df, completeness


def build_validation_table(df: pd.DataFrame) -> pd.DataFrame:
    statuses: list[str] = []
    reasons: list[str] = []
    actions: list[str] = []
    for _, row in df.iterrows():
        st, rs, act = classify_row(row)
        statuses.append(st)
        reasons.append(rs)
        actions.append(act)

    out = df[
        [
            "scenario_name",
            "base_scenario",
            "family",
            "traffic_profile",
            "delivery_ratio",
            "latency_mean",
            "overhead_ratio",
            "drop_ratio",
            "spatial_coverage_pct",
            "useful_time_ratio",
            "contact_time_per_min",
            "total_encounters",
        ]
    ].copy()
    out["validation_status"] = statuses
    out["reason"] = reasons
    out["recommended_action"] = actions
    return out


def write_report(
    val: pd.DataFrame,
    completeness: dict[str, Any],
    out_path: Path,
) -> None:
    status_counts = val["validation_status"].value_counts().sort_index()
    p0_diag = int((val["validation_status"].isin(
        ["error_probable", "configuracion_sospechosa", "pendiente_revision"]
    )).sum())

    lines = [
        "# Corpus v2 benchmark validation",
        "",
        f"Generated: {_utc()}",
        "",
        "## Executive summary",
        "",
        f"- **Corpus:** `corpus_v2` — **720** scenarios (60 bases × 12 TP)",
        f"- **Settings files:** {completeness['settings_count']}",
        f"- **Manifest rows:** {completeness['manifest_rows']}",
        f"- **Output metrics:** {completeness['output_metrics_rows']} rows",
        f"- **Spatial metrics:** {completeness['spatial_rows']} rows",
        f"- **Scenarios needing attention (non-ok, non-valido_extremo):** "
        f"{int(status_counts.get('error_probable', 0) + status_counts.get('configuracion_sospechosa', 0) + status_counts.get('pendiente_revision', 0))}",
        "",
        "### Validation status counts",
        "",
        "| Status | Count |",
        "|--------|------:|",
    ]
    for st, n in status_counts.items():
        lines.append(f"| `{st}` | {n} |")

    lines.extend([
        "",
        "## Completeness",
        "",
        "| Check | Result |",
        "|-------|--------|",
        f"| `.settings` in corpus_v2 | {completeness['settings_count']} |",
        f"| manifest.csv data rows | {completeness['manifest_rows']} |",
        f"| Scenario bases | {completeness['bases']} |",
        f"| Traffic profiles | {completeness['traffic_profiles']} |",
        f"| output_metrics.csv | {completeness['output_metrics_rows']} |",
        f"| spatial_occupancy_metrics.csv | {completeness['spatial_rows']} |",
        f"| indirect_features_diego.csv | {completeness['indirect_rows']} |",
        f"| message_creation_time_summary.csv | {completeness['message_creation_rows']} |",
        f"| useful_simulation_time_metrics.csv | {completeness['useful_time_rows']} |",
        f"| Null delivery_ratio | {completeness['null_delivery']} |",
        f"| Zero delivery_ratio | {completeness['zero_delivery']} |",
        f"| Zero total_encounters | {completeness['zero_encounters']} |",
        "",
        "## Problem distribution",
        "",
        "### By family",
        "",
        "| family | ok | valido_extremo | pendiente_revision | configuracion_sospechosa | error_probable |",
        "|--------|---:|---:|---:|---:|---:|",
    ])

    for fam, grp in val.groupby("family"):
        c = grp["validation_status"].value_counts()
        lines.append(
            f"| `{fam}` | {c.get('ok', 0)} | {c.get('valido_extremo', 0)} | "
            f"{c.get('pendiente_revision', 0)} | {c.get('configuracion_sospechosa', 0)} | "
            f"{c.get('error_probable', 0)} |"
        )

    lines.extend([
        "",
        "### By traffic profile",
        "",
        "| TP | ok | valido_extremo | pendiente_revision | configuracion_sospechosa | error_probable |",
        "|----|---:|---:|---:|---:|---:|",
    ])
    for tp, grp in val.groupby("traffic_profile"):
        c = grp["validation_status"].value_counts()
        lines.append(
            f"| `{tp}` | {c.get('ok', 0)} | {c.get('valido_extremo', 0)} | "
            f"{c.get('pendiente_revision', 0)} | {c.get('configuracion_sospechosa', 0)} | "
            f"{c.get('error_probable', 0)} |"
        )

  # Error probable list
    err = val[val["validation_status"] == "error_probable"]
    if not err.empty:
        lines.extend(["", "### error_probable scenarios", ""])
        for _, r in err.iterrows():
            lines.append(f"- `{r['scenario_name']}` — {r['reason']}")

    lines.extend([
        "",
        "## Methodological answers",
        "",
        "### 1. Is corpus_v2 sufficiently complete to use as a benchmark?",
        "",
        "**Yes for configuration/diversity benchmarking** — all 720 `.settings`, manifest rows, "
        "feature matrices, output metrics, spatial metrics, and auxiliary CSVs are present (720/720).",
        "",
        "**Almost ready for routing protocol comparison** — two scenarios lack output metrics "
        f"(`error_probable`, see CSV); message analysis window (policy B) is not yet enforced in the pipeline.",
        "",
        "### 2. Which scenarios should be kept as valid extremes?",
        "",
        "- **TP12** cross-group partition controls (`include_control`)",
        "- **TP04 / TP05 / TP10** stress load and CriticalTTL tiers (`include_stress`)",
        "- **R10 / R11** and disconnected bases with `ZERO_CONTACTS` (`include_control` / `document_as_extreme`)",
        "- **07_traffic** family (traffic-pattern laboratory)",
        "- **MAP_UNDERUSED** WDM scenarios (~8–10% world grid coverage on roads — not a simulation failure)",
        "",
        f"Count `valido_extremo`: **{int(status_counts.get('valido_extremo', 0))}** scenarios.",
        "",
        "### 3. Which scenarios need review before the paper?",
        "",
        f"- **{int(status_counts.get('error_probable', 0))}** scenarios with missing outputs → re-simulate",
        f"- **{int(status_counts.get('configuracion_sospechosa', 0))}** suspicious configs (zero delivery with contacts, etc.)",
        f"- **{int(status_counts.get('pendiente_revision', 0))}** pending revision (P0/P1 map, worldSize, latency window)",
        "- Urban WDM **MAP_TOO_LARGE / MAP_UNDERUSED** — document in Methods, optional worldSize crop",
        "",
        "### 4. Which problems do NOT block the paper?",
        "",
        "- Diversity metrics frozen in `RESULTADOS_ACTUALES.md` (720 scenarios)",
        "- Low spatial *world* coverage on map-based mobility (roads vs rectangle world)",
        "- Stress-tier extremes reported separately from main claims",
        "- 24 disconnected control scenarios (documented in tp_validation_report)",
        "",
        "### 5. Which problems COULD block protocol comparison?",
        "",
        "- **Message analysis window not implemented** — compare protocols only after policy B in pipeline",
        "- **Missing output metrics** (2 scenarios) — exclude or re-simulate before ranking",
        "- **Mixing P0 scenarios in main split** without stratification (use `manifest_revision.csv` benchmark_split)",
        "- **TP05 zero-delivery** in aggregate main-tier ranking without stress tier separation",
        "",
        "## Recommended splits",
        "",
        "Align protocol runs with `corpus_v2/manifest_revision.csv`:",
        "",
        "- **main:** TP01–TP08 on viable bases; exclude `error_probable` and `configuracion_sospechosa`",
        "- **stress:** TP09–TP11, TP04–TP06 load, all `07_traffic`",
        "- **control:** TP12 partition, disconnected extremes",
        "",
        "## Next steps",
        "",
        "1. Re-simulate `S1_StrongCommunities_SeparateClusters__TP03_ManySmall` and `__TP11_ManyToOne`",
        "2. Implement TTL-aware message window in `output_metrics` pipeline",
        "3. Filter validation CSV when exporting paper tables (`validation_status == ok` for main tier)",
        "4. Re-run after settings revision: `validate_corpus_v2_benchmark.py`",
        "",
        "## Artifacts",
        "",
        "- Validation table: [`data/corpus_v2_benchmark_validation.csv`](../data/corpus_v2_benchmark_validation.csv)",
        "- Diagnosis: [`data/scenario_diagnosis.csv`](../data/scenario_diagnosis.csv)",
        "- TP validation: [`tp_validation_report.md`](tp_validation_report.md)",
        "- Frozen diversity: [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)",
        "",
    ])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate corpus_v2 benchmark readiness.")
    ap.add_argument("--manifest", type=str, default=str(DEFAULT_MANIFEST_V2))
    ap.add_argument("--data-dir", type=str, default=str(DATA_DIR))
    ap.add_argument("--output-csv", type=str, default=str(DATA_DIR / "corpus_v2_benchmark_validation.csv"))
    ap.add_argument("--output-report", type=str, default=str(CORPUS_V2_BENCHMARK_VALIDATION))
    ap.add_argument(
        "--refresh-diagnosis",
        action="store_true",
        help="Run diagnose_scenarios.py before validation",
    )
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    if args.refresh_diagnosis:
        subprocess.run(
            [sys.executable, str(_ANALYSIS / "scripts/validation/diagnose_scenarios.py")],
            check=True,
            cwd=str(REPO_ROOT),
        )

    df, completeness = load_and_merge(Path(args.manifest), data_dir)
    val = build_validation_table(df)

    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    val.to_csv(out_csv, index=False)

    write_report(val, completeness, Path(args.output_report))

    print(f"Wrote {out_csv} ({len(val)} rows)")
    print(f"Wrote {args.output_report}")
    print(val["validation_status"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
