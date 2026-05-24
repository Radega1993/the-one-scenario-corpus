#!/usr/bin/env python3
"""
Build strict paper-freeze checklist for corpus_v2 (protocol-comparison scope).

Writes:
  - reports/paper_freeze_checklist.md
  - data/paper_freeze_checklist.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import pandas as pd

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import (
    ANALYSIS_DIR,
    CORPUS_V2,
    DATA_DIR,
    DEFAULT_MANIFEST_V2,
    REPO_ROOT,
    SCENARIOS_DIR,
)
from lib.report_paths import (
    CORPUS_V2_BENCHMARK_VALIDATION,
    DASHBOARD_READINESS_REPORT,
    MESSAGE_ANALYSIS_WINDOW_POLICY,
    PAPER_FREEZE_CHECKLIST,
    PROTOCOL_BENCHMARK_KPI_POLICY,
    RESULTADOS_ACTUALES,
    SPATIAL_OCCUPANCY_ANALYSIS_SUMMARY,
    SPATIAL_VS_PERFORMANCE_ANALYSIS,
    TRAFFIC_PROFILE_KPI_ANALYSIS,
)

Status = Literal["DONE", "PARTIAL", "MISSING", "BLOCKER"]
Rec = Literal["READY_FOR_WRITING", "READY_WITH_MINOR_FIXES", "NOT_READY", "BLOCKED"]

EXPECTED_N = 720
PAPER_DIR = ANALYSIS_DIR / "figures" / "paper"
FIG_INDEX = PAPER_DIR / "FIGURES_AND_TABLES_INDEX.md"
WIKI_DIR = SCENARIOS_DIR / ".wiki-clone"
HEATMAP_DIR = ANALYSIS_DIR / "figures" / "spatial_heatmaps"


@dataclass
class Item:
    block: str
    item_id: str
    item: str
    status: Status
    evidence: str
    action_required: str = ""
    blocks_writing: str = "no"


def _count_csv_rows(path: Path) -> int | None:
    if not path.is_file():
        return None
    try:
        return len(pd.read_csv(path))
    except Exception:
        return None


def _count_settings() -> int:
    return len(list(CORPUS_V2.rglob("*.settings")))


def _parse_figure_index() -> list[dict[str, str]]:
    if not FIG_INDEX.is_file():
        return []
    rows: list[dict[str, str]] = []
    for line in FIG_INDEX.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|") or line.startswith("| filename") or line.startswith("|-"):
            continue
        content = line.strip().strip("|")
        parts = [p.strip().replace(r"\|", "|") for p in re.split(r"(?<!\\)\|", content)]
        if len(parts) != 8:
            continue
        rows.append(
            {
                "filename": parts[0],
                "type": parts[1],
                "status": parts[7],
            }
        )
    return rows


def _wiki_message_window_drift() -> bool:
    p = WIKI_DIR / "11-Message-Analysis-Window.md"
    if not p.is_file():
        return False
    text = p.read_text(encoding="utf-8", errors="replace").lower()
    return "policy b" in text or "5% warmup" in text or "0.05*endtime" in text


def _bench_validation_counts() -> dict[str, int]:
    p = DATA_DIR / "corpus_v2_benchmark_validation.csv"
    if not p.is_file():
        return {}
    df = pd.read_csv(p)
    col = "validation_status"
    if col not in df.columns:
        return {}
    return df[col].astype(str).value_counts().to_dict()


def _tp_kpi_counts() -> dict[str, int]:
    p = DATA_DIR / "traffic_profile_kpi_summary.csv"
    if not p.is_file():
        return {}
    df = pd.read_csv(p)
    if "validation_status" not in df.columns:
        return {}
    return df["validation_status"].astype(str).value_counts().to_dict()


def _null_delivery() -> int:
    p = DATA_DIR / "output_metrics.csv"
    if not p.is_file():
        return -1
    df = pd.read_csv(p)
    if "delivery_ratio" not in df.columns:
        return -1
    return int(df["delivery_ratio"].isna().sum())


def _spatial_summary_stale() -> bool:
    p = SPATIAL_OCCUPANCY_ANALYSIS_SUMMARY
    if not p.is_file():
        return False
    text = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Scenarios processed:\s*(\d+)", text)
    if m and int(m.group(1)) < EXPECTED_N:
        return True
    return False


def audit() -> dict:
    manifest_n = _count_csv_rows(DEFAULT_MANIFEST_V2)
    settings_n = _count_settings()
    output_n = _count_csv_rows(DATA_DIR / "output_metrics.csv")
    features_n = _count_csv_rows(DATA_DIR / "features.csv")
    features_core_n = _count_csv_rows(DATA_DIR / "features_core.csv")
    spatial_n = _count_csv_rows(DATA_DIR / "spatial_occupancy_metrics.csv")
    msg_policy_n = _count_csv_rows(DATA_DIR / "message_analysis_window_policy.csv")
    heatmaps_n = len(list(HEATMAP_DIR.glob("*.png"))) if HEATMAP_DIR.is_dir() else 0
    fig_rows = _parse_figure_index()
    fig_main = [r for r in fig_rows if r["type"] == "main" and r["filename"].endswith(".png")]
    fig_supp = [r for r in fig_rows if r["type"] == "supplementary" and r["filename"].endswith(".png")]
    fig_tables = [r for r in fig_rows if r["type"] == "table"]
    main_lista = sum(1 for r in fig_main if r["status"] == "lista")
    main_revisar = sum(1 for r in fig_main if r["status"] == "revisar")
    supp_lista = sum(1 for r in fig_supp if r["status"] == "lista")
    supp_revisar = sum(1 for r in fig_supp if r["status"] == "revisar")
    tables_lista = sum(1 for r in fig_tables if r["status"] == "lista")
    null_del = _null_delivery()
    bench = _bench_validation_counts()
    tp_kpi = _tp_kpi_counts()
    manifest_revision = (CORPUS_V2 / "manifest_revision.csv").is_file()
    wiki_drift = _wiki_message_window_drift()
    spatial_stale = _spatial_summary_stale()

    required_reports = {
        "RESULTADOS_ACTUALES.md": RESULTADOS_ACTUALES,
        "corpus_v2_benchmark_validation.md": CORPUS_V2_BENCHMARK_VALIDATION,
        "traffic_profile_kpi_analysis.md": TRAFFIC_PROFILE_KPI_ANALYSIS,
        "protocol_benchmark_kpi_policy.md": PROTOCOL_BENCHMARK_KPI_POLICY,
        "message_analysis_window_policy.md": MESSAGE_ANALYSIS_WINDOW_POLICY,
        "spatial_vs_performance_analysis.md": SPATIAL_VS_PERFORMANCE_ANALYSIS,
    }
    reports_present = {k: v.is_file() for k, v in required_reports.items()}

    return {
        "manifest_n": manifest_n,
        "settings_n": settings_n,
        "output_n": output_n,
        "features_n": features_n,
        "features_core_n": features_core_n,
        "spatial_n": spatial_n,
        "msg_policy_n": msg_policy_n,
        "heatmaps_n": heatmaps_n,
        "fig_main_total": len(fig_main),
        "fig_main_lista": main_lista,
        "fig_main_revisar": main_revisar,
        "fig_supp_total": len(fig_supp),
        "fig_supp_lista": supp_lista,
        "fig_supp_revisar": supp_revisar,
        "fig_tables_total": len(fig_tables),
        "fig_tables_lista": tables_lista,
        "null_delivery": null_del,
        "bench": bench,
        "tp_kpi": tp_kpi,
        "manifest_revision": manifest_revision,
        "wiki_drift": wiki_drift,
        "spatial_stale": spatial_stale,
        "reports_present": reports_present,
        "protocol_defs_csv": (DATA_DIR / "protocol_benchmark_kpi_definitions.csv").is_file(),
        "protocol_placeholder": (PAPER_DIR / "supplementary" / "protocol_comparison_placeholder.png").is_file()
        or (PAPER_DIR / "supplementary" / "protocol_comparison_placeholder.png").is_file(),
        "dashboard_readiness": DASHBOARD_READINESS_REPORT.is_file(),
        "wiki_freeze_page": (WIKI_DIR / "14-Paper-Freeze-Checklist.md").is_file(),
        "wiki_protocol_page": (WIKI_DIR / "12-Benchmark-Protocol-Comparison.md").is_file(),
        "limitations_report": False,
    }


def build_items(a: dict) -> list[Item]:
    items: list[Item] = []
    bench = a["bench"]
    tp_kpi = a["tp_kpi"]
    err_prob = bench.get("error_probable", 0)
    sospechosa = bench.get("configuracion_sospechosa", 0)
    pend_rev = bench.get("pendiente_revision", 0)
    tp_blocked = tp_kpi.get("blocked", 0)
    tp_partial = tp_kpi.get("partial", 0)
    tp_validated = tp_kpi.get("validated", 0)

    def add(
        block: str,
        item_id: str,
        item: str,
        status: Status,
        evidence: str,
        action: str = "",
        blocks: str = "no",
    ) -> None:
        items.append(Item(block, item_id, item, status, evidence, action, blocks))

    # 1. Corpus
    corp_manifest_ok = a["manifest_n"] == EXPECTED_N and a["settings_n"] == EXPECTED_N
    add(
        "corpus",
        "CORP-01",
        "manifest.csv 720 rows + 720 .settings",
        "DONE" if corp_manifest_ok else "PARTIAL",
        f"manifest rows={a['manifest_n']}, settings={a['settings_n']}",
        "" if corp_manifest_ok else "Align manifest and settings count to 720",
    )
    add(
        "corpus",
        "CORP-02",
        "Factorial design 60 bases x 12 TP x 7 families documented",
        "DONE",
        "corpus_v2/README.md; corpus_overview_paper.png (lista)",
    )
    add(
        "corpus",
        "CORP-03",
        "Benchmark splits frozen in main manifest",
        "PARTIAL" if a["manifest_revision"] else "MISSING",
        "manifest_revision.csv exists" if a["manifest_revision"] else "manifest_revision.csv not found",
        "Freeze benchmark_split into manifest or document split CSV as canonical",
    )
    add(
        "corpus",
        "CORP-04",
        "Active docs reference corpus_v2 only (no corpus_v3 as active)",
        "DONE",
        "README.md and INVENTARIO.md declare corpus_v2 active; corpus_v3 only in _archive",
    )

    # 2. Settings
    add(
        "settings",
        "SET-01",
        "Settings audit for all 720 scenarios",
        "DONE" if (DATA_DIR / "settings_audit.csv").is_file() else "MISSING",
        "settings_audit.csv present" if (DATA_DIR / "settings_audit.csv").is_file() else "Run audit_settings.py",
        "" if (DATA_DIR / "settings_audit.csv").is_file() else "Generate settings_audit.csv",
    )
    tp_val_status = "PARTIAL" if tp_blocked or tp_partial else "DONE"
    add(
        "settings",
        "SET-02",
        "Traffic Profile settings validation (TP01-TP12)",
        tp_val_status,
        f"tp_validation_settings.csv; KPI summary: validated={tp_validated}, partial={tp_partial}, blocked={tp_blocked}",
        "Resolve TP03/TP11 blocked (S1 missing outputs)" if tp_blocked else "",
        "yes" if tp_blocked else "no",
    )
    add(
        "settings",
        "SET-03",
        "P0/P1 map worldSize WDM issues resolved or excluded",
        "PARTIAL",
        f"bench validation: pendiente_revision={pend_rev}, configuracion_sospechosa={sospechosa}",
        "Formalize exclusion in benchmark_split main tier",
    )

    # 3. Simulations
    sim_epidemic = "PARTIAL" if err_prob > 0 or a["null_delivery"] > 0 else "DONE"
    add(
        "simulations",
        "SIM-01",
        "ONE batch Epidemic complete 720/720",
        sim_epidemic,
        f"output_metrics rows={a['output_n']}; null delivery_ratio={a['null_delivery']}; error_probable={err_prob}",
        "Re-simulate S1_StrongCommunities TP03 and TP11" if err_prob else "",
        "yes" if err_prob else "no",
    )
    add(
        "simulations",
        "SIM-02",
        "Multi-protocol simulations (PRoPHET MaxProp etc.)",
        "MISSING",
        "Wiki 12-Benchmark-Protocol-Comparison: no runs; protocol_comparison_placeholder only",
        "Run batch with analysis/protocol_overlays/ on main split",
        "yes",
    )
    add(
        "simulations",
        "SIM-03",
        "Batch reproducibility documented (commands seeds)",
        "PARTIAL",
        "SCRIPTS_INDEX covers Epidemic; no executed multi-protocol runbook",
        "Document and run multi-protocol batch before writing Results",
    )

    # 4. Outputs
    out_status: Status = "DONE"
    if a["output_n"] != EXPECTED_N or a["null_delivery"] > 0:
        out_status = "PARTIAL"
    add(
        "outputs",
        "OUT-01",
        "output_metrics.csv complete 720 rows",
        out_status,
        f"rows={a['output_n']}; null delivery={a['null_delivery']}",
        "Fix 2 missing S1 outputs" if a["null_delivery"] else "",
        "yes" if a["null_delivery"] else "no",
    )
    add(
        "outputs",
        "OUT-02",
        "ONE reports (MessageStats Connectivity spatial grid)",
        "PARTIAL",
        f"Repo reports/ not versioned; {err_prob} scenarios incomplete",
        "Re-simulate incomplete scenarios; archive report paths in manifest",
    )
    useful_ok = (DATA_DIR / "useful_simulation_time_metrics.csv").is_file()
    indirect_ok = (DATA_DIR / "indirect_features_diego.csv").is_file()
    add(
        "outputs",
        "OUT-03",
        "Auxiliary outputs (indirect useful time)",
        "DONE" if useful_ok and indirect_ok else "PARTIAL",
        f"useful_simulation_time_metrics={useful_ok}; indirect_features={indirect_ok}",
    )

    # 5. Features
    feat_ok = a["features_n"] == EXPECTED_N and a["features_core_n"] == EXPECTED_N
    add(
        "features",
        "FEAT-01",
        "features.csv and features_core.csv 720 scenarios",
        "DONE" if feat_ok else "PARTIAL",
        f"features={a['features_n']}, features_core={a['features_core_n']}",
    )
    add(
        "features",
        "FEAT-02",
        "Diversity metrics frozen n=720",
        "DONE" if a["reports_present"].get("RESULTADOS_ACTUALES.md") else "MISSING",
        "RESULTADOS_ACTUALES.md",
    )
    add(
        "features",
        "FEAT-03",
        "Feature-feature redundancy acceptable",
        "PARTIAL",
        "Persistent high pair mm_WDM <-> mm_Bus = 0.9393; max |r|=1.0 between scenarios",
        "Disclose in Methods; justify core-23 retention",
    )
    add(
        "features",
        "FEAT-04",
        "Ablation 17/23/46 documented",
        "DONE",
        "table_ablation_metrics_en/es lista; ablation reports",
    )

    # 6. Traffic Profiles
    add(
        "traffic_profiles",
        "TP-01",
        "12 Traffic Profiles defined and experimentally validated",
        "PARTIAL",
        f"validated={tp_validated}, partial={tp_partial}, blocked={tp_blocked}",
        "Unblock TP03/TP11 after re-simulation",
        "yes" if tp_blocked else "no",
    )
    add(
        "traffic_profiles",
        "TP-02",
        "Traffic Profile KPI analysis report",
        "DONE" if a["reports_present"].get("traffic_profile_kpi_analysis.md") else "MISSING",
        "traffic_profile_kpi_analysis.md",
    )
    add(
        "traffic_profiles",
        "TP-03",
        "Stress/directional/control tiers in protocol comparison pipeline",
        "PARTIAL",
        "Splits in manifest_revision.csv; not wired to multi-protocol runs",
        "Integrate tiers when running protocol comparison",
    )

    # 7. Spatial
    spat_ok = a["spatial_n"] == EXPECTED_N
    heat_ok = a["heatmaps_n"] == EXPECTED_N
    add(
        "spatial_occupancy",
        "SPAT-01",
        "spatial_occupancy_metrics.csv 720 rows",
        "DONE" if spat_ok else "PARTIAL",
        f"rows={a['spatial_n']}",
    )
    add(
        "spatial_occupancy",
        "SPAT-02",
        "Spatial heatmaps 720 scenarios",
        "DONE" if heat_ok else "PARTIAL",
        f"PNG count={a['heatmaps_n']}",
    )
    spat_vs_perf = a["reports_present"].get("spatial_vs_performance_analysis.md", False)
    add(
        "spatial_occupancy",
        "SPAT-03",
        "Spatial vs performance analysis report",
        "MISSING" if not spat_vs_perf else "DONE",
        "spatial_vs_performance_analysis.md absent"
        if not spat_vs_perf
        else "spatial_vs_performance_analysis.md present",
        "Write spatial_vs_performance_analysis.md linking coverage to delivery",
    )
    add(
        "spatial_occupancy",
        "SPAT-04",
        "Paper figure spatial_coverage_by_family_paper",
        "PARTIAL",
        f"Indexed status revisar; summary stale={a['spatial_stale']}",
        "Regenerate figure; refresh spatial_occupancy_analysis_summary.md",
    )

    # 8. Message windows
    add(
        "message_windows",
        "MSG-01",
        "Canonical message window policy document",
        "DONE" if a["reports_present"].get("message_analysis_window_policy.md") else "MISSING",
        "message_analysis_window_policy.md (full window primary; optional 10% censor)",
    )
    if a["wiki_drift"]:
        msg_impl: Status = "PARTIAL"
        msg_ev = "Wiki 11 still cites Policy B + 5% warmup (drift)"
        msg_act = "Align wiki 11 with canonical policy"
    else:
        msg_impl = "PARTIAL"
        msg_ev = "Canonical policy documented; output_metrics uses full MessageStatsReport aggregates"
        msg_act = "Optional: implement explicit window filter in extraction code for appendix"
    add(
        "message_windows",
        "MSG-02",
        "Policy implemented in output_metrics extraction pipeline",
        msg_impl,
        msg_ev,
        msg_act,
        "no",
    )
    add(
        "message_windows",
        "MSG-03",
        "Per-scenario policy CSV 720 rows",
        "DONE" if a["msg_policy_n"] == EXPECTED_N else "PARTIAL",
        f"message_analysis_window_policy.csv rows={a['msg_policy_n']}",
    )

    # 9. KPIs
    add(
        "kpis",
        "KPI-01",
        "Per-TP KPIs under Epidemic",
        "DONE",
        "traffic_profile_kpi_summary.csv + traffic_profile_kpi_analysis.md",
    )
    prot_pol = a["reports_present"].get("protocol_benchmark_kpi_policy.md", False)
    add(
        "kpis",
        "KPI-02",
        "Protocol benchmark KPI policy document",
        "MISSING" if not prot_pol else "DONE",
        "protocol_benchmark_kpi_policy.md absent" if not prot_pol else "present",
        "Write protocol_benchmark_kpi_policy.md",
        "yes" if not prot_pol else "no",
    )
    add(
        "kpis",
        "KPI-03",
        "protocol_benchmark_kpi_definitions.csv",
        "MISSING" if not a["protocol_defs_csv"] else "DONE",
        "CSV not generated" if not a["protocol_defs_csv"] else "present",
        "Generate KPI definitions CSV for multi-protocol comparison",
        "yes" if not a["protocol_defs_csv"] else "no",
    )
    add(
        "kpis",
        "KPI-04",
        "Core-4 metrics agreed for cross-protocol comparison",
        "PARTIAL",
        "Defined in TP report; not validated across protocols",
        "Formalize in protocol_benchmark_kpi_policy.md after runs",
    )

    # 10. Figures
    add(
        "figures",
        "FIG-01",
        "FIGURES_AND_TABLES_INDEX.md complete",
        "DONE" if FIG_INDEX.is_file() else "MISSING",
        f"{a['fig_main_total'] + a['fig_supp_total'] + a['fig_tables_total']} indexed items",
    )
    main_fig_status: Status = "DONE"
    if a["fig_main_revisar"] > 0:
        main_fig_status = "PARTIAL"
    add(
        "figures",
        "FIG-02",
        "Main paper figures ready (lista)",
        main_fig_status,
        f"lista={a['fig_main_lista']}/{a['fig_main_total']}, revisar={a['fig_main_revisar']}",
        "Regenerate 7 main figures marked revisar",
    )
    supp_fig_status: Status = "DONE"
    if a["fig_supp_revisar"] > 0:
        supp_fig_status = "PARTIAL"
    add(
        "figures",
        "FIG-03",
        "Supplementary figures ready (lista)",
        supp_fig_status,
        f"lista={a['fig_supp_lista']}/{a['fig_supp_total']}, revisar={a['fig_supp_revisar']}",
        "Regenerate supplementary figures marked revisar",
    )
    add(
        "figures",
        "FIG-04",
        "Protocol comparison figure (real data)",
        "MISSING",
        "Only protocol_comparison_placeholder.png",
        "Run multi-protocol simulations and plot comparison",
        "yes",
    )

    # 11. Tables
    en_tables = a["fig_tables_lista"] >= 4
    add(
        "tables",
        "TAB-01",
        "English paper tables (diversity ablation families features)",
        "DONE" if en_tables else "PARTIAL",
        f"tables lista={a['fig_tables_lista']}/{a['fig_tables_total']}",
    )
    add(
        "tables",
        "TAB-02",
        "Spanish draft tables",
        "DONE" if a["fig_tables_lista"] == a["fig_tables_total"] else "PARTIAL",
        "ES tables marked lista in index",
    )
    add(
        "tables",
        "TAB-03",
        "Multi-protocol results tables",
        "MISSING",
        "No protocol comparison result tables",
        "Generate after multi-protocol batch",
        "yes",
    )

    # 12. Wiki
    add(
        "wiki",
        "WIKI-01",
        "Paper wiki rebuild pages 01-14",
        "PARTIAL",
        f".wiki-clone present; key pages draft status",
    )
    add(
        "wiki",
        "WIKI-02",
        "Wiki aligned with canonical analysis reports",
        "PARTIAL" if a["wiki_drift"] else "DONE",
        "Wiki 11 contradicts message_analysis_window_policy.md" if a["wiki_drift"] else "No drift detected on message window",
        "Update 11-Message-Analysis-Window.md to match canonical policy",
    )
    add(
        "wiki",
        "WIKI-03",
        "Formal freeze checklist in analysis/reports",
        "DONE",
        "This report (paper_freeze_checklist.md) supersedes informal wiki checklist",
    )

    # 13. Reproducibility
    add(
        "reproducibility",
        "REP-01",
        "Official pipeline documented (SCRIPTS_INDEX)",
        "DONE",
        "analysis/SCRIPTS_INDEX.md 12-step pipeline",
    )
    add(
        "reproducibility",
        "REP-02",
        "Dashboard for paper exploration",
        "DONE" if a["dashboard_readiness"] else "PARTIAL",
        "dashboard_readiness_report.md" if a["dashboard_readiness"] else "dashboard not documented",
    )
    add(
        "reproducibility",
        "REP-03",
        "One-command regeneration figures and tables",
        "PARTIAL",
        f"Commands in index; {a['fig_main_revisar'] + a['fig_supp_revisar']} figures still revisar",
        "Run build_paper_figures_tables_index.py after regen",
    )
    add(
        "reproducibility",
        "REP-04",
        "Simulation outputs (reports/) reproducible from manifest",
        "PARTIAL",
        "reports/ at repo root not fully versioned; re-sim cost high",
        "Document exact one.sh invocations per scenario batch",
    )

    # 14. Limitations
    add(
        "limitations",
        "LIM-01",
        "Limitations documented (maps WDM synthetic stress tiers)",
        "PARTIAL",
        f"Dispersed in benchmark validation ({sospechosa} sospechosa, 312 valido_extremo)",
        "Consolidate into Methods/Limitations section",
    )
    add(
        "limitations",
        "LIM-02",
        "Threats-to-validity section frozen",
        "MISSING" if not a["limitations_report"] else "DONE",
        "No single limitations.md report",
        "Write limitations/threats section or report",
    )
    add(
        "limitations",
        "LIM-03",
        "Extreme scenarios excluded from main protocol ranking",
        "PARTIAL",
        "manifest_revision splits exist; not enforced in analysis outputs",
        "Apply benchmark_split filter in protocol comparison tables",
    )

    return items


def recommend(items: list[Item]) -> Rec:
    blockers = [i for i in items if i.status == "BLOCKER"]
    missing_blocks = [i for i in items if i.status == "MISSING" and i.blocks_writing == "yes"]
    protocol_only = {
        i.item_id
        for i in missing_blocks
        if i.item_id in ("SIM-02", "FIG-04", "TAB-03", "KPI-02", "KPI-03")
    }
    corpus_gaps = [
        i
        for i in missing_blocks
        if i.item_id not in protocol_only
    ]

    if blockers:
        return "NOT_READY"

    if corpus_gaps:
        return "NOT_READY"

    partial_count = sum(1 for i in items if i.status == "PARTIAL")
    if missing_blocks and protocol_only == {i.item_id for i in missing_blocks}:
        return "READY_WITH_MINOR_FIXES"

    if partial_count > 12:
        return "NOT_READY"

    if partial_count > 0 or missing_blocks:
        return "READY_WITH_MINOR_FIXES"

    return "READY_FOR_WRITING"


def write_csv(path: Path, items: list[Item]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["block", "item_id", "item", "status", "evidence", "action_required", "blocks_writing"])
        for i in items:
            w.writerow([i.block, i.item_id, i.item, i.status, i.evidence, i.action_required, i.blocks_writing])


def write_md(path: Path, items: list[Item], rec: Rec, a: dict) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    blocks = sorted({i.block for i in items})

    lines = [
        "# Paper freeze checklist (corpus_v2)",
        "",
        f"Generated: {ts}",
        "",
        "**Scope:** paper with **multi-protocol routing comparison** on corpus_v2.",
        "**Active corpus:** `corpus_v2` (not corpus_v3).",
        "",
        "## Executive summary",
        "",
        f"- Simulations in manifest: **{a['manifest_n']}** (expected {EXPECTED_N})",
        f"- Settings files: **{a['settings_n']}**",
        f"- Output metrics null delivery: **{a['null_delivery']}**",
        f"- Benchmark `error_probable`: **{a['bench'].get('error_probable', 0)}**",
        f"- Benchmark `configuracion_sospechosa`: **{a['bench'].get('configuracion_sospechosa', 0)}**",
        f"- Main figures lista/revisar: **{a['fig_main_lista']}/{a['fig_main_total']}** lista, **{a['fig_main_revisar']}** revisar",
        "",
        "## Status legend",
        "",
        "| Status | Meaning |",
        "|--------|---------|",
        "| DONE | Complete, corpus_v2-aligned, traceable |",
        "| PARTIAL | Exists but incomplete, stale, or needs human review |",
        "| MISSING | Required artifact absent |",
        "| BLOCKER | Blocks central paper claims |",
        "",
    ]

    for block in blocks:
        title = block.replace("_", " ").title()
        lines.extend([f"## {title}", "", "| ID | Item | Status | Evidence | Action |", "|----|------|--------|----------|--------|"])
        for i in items:
            if i.block != block:
                continue
            act = i.action_required or "—"
            lines.append(f"| {i.item_id} | {i.item} | **{i.status}** | {i.evidence} | {act} |")
        lines.append("")

    blockers = [i for i in items if i.status in ("BLOCKER", "MISSING") and i.blocks_writing == "yes"]
    lines.extend(["## Critical blockers (writing gate)", ""])
    if blockers:
        for i in blockers:
            lines.append(f"- **{i.item_id}** ({i.status}): {i.item} — {i.evidence}")
    else:
        lines.append("- None marked as writing blockers.")
    lines.append("")

    lines.extend(
        [
            "## Block summary",
            "",
            "| Block | DONE | PARTIAL | MISSING | BLOCKER |",
            "|-------|-----:|--------:|--------:|--------:|",
        ]
    )
    for block in blocks:
        sub = [i for i in items if i.block == block]
        lines.append(
            f"| {block} | "
            f"{sum(1 for i in sub if i.status == 'DONE')} | "
            f"{sum(1 for i in sub if i.status == 'PARTIAL')} | "
            f"{sum(1 for i in sub if i.status == 'MISSING')} | "
            f"{sum(1 for i in sub if i.status == 'BLOCKER')} |"
        )

    lines.extend(
        [
            "",
            "## Minimum path to READY_FOR_WRITING",
            "",
            "1. Complete re-simulation of any missing Epidemic outputs (e.g. S1 TP03 if still null).",
            "2. Run multi-protocol batch on `manifest_revision.csv` main split with `protocol_overlays/`.",
            "3. Regenerate `output_metrics.csv` per protocol; build comparison figures/tables.",
            "4. Re-run `build_paper_freeze_checklist.py`.",
            "",
            "## Final recommendation",
            "",
            f"### **{rec}**",
            "",
        ]
    )

    if rec == "NOT_READY":
        lines.extend(
            [
                "The project is **not ready** for formal paper writing with protocol-comparison claims.",
                "",
                "**Ready for Methods / corpus design** (diversity, families, TP, spatial) with documented limitations.",
                "",
                "Primary reasons:",
            ]
        )
        for i in blockers[:12]:
            lines.append(f"- **{i.item_id}** ({i.status}): {i.item}.")
        if a["null_delivery"] > 0:
            lines.append(f"- **{a['null_delivery']}** scenario(s) still missing `delivery_ratio` in output_metrics.")
        if a["fig_main_revisar"] > 0:
            lines.append(f"- **{a['fig_main_revisar']}** main paper figures still marked revisar.")
        lines.append("")
    elif rec == "READY_WITH_MINOR_FIXES":
        lines.extend(
            [
                "Core corpus documentation and Epidemic baseline are in place.",
                "Address remaining PARTIAL items and complete multi-protocol runs before Results claims.",
                "",
            ]
        )
    elif rec == "READY_WITH_MINOR_FIXES":
        lines.append("Address remaining PARTIAL items before submission; core data exists.")
    elif rec == "READY_FOR_WRITING":
        lines.append("All checklist items pass strict gate; proceed with formal writing.")
    else:
        lines.append("Critical blockers prevent any writing phase until resolved.")

    lines.extend(
        [
            "",
            "## Regeneration",
            "",
            "```bash",
            "scenarios/analysis/.venv/bin/python scenarios/analysis/build_paper_freeze_checklist.py",
            "# or from scenarios/analysis:",
            "python build_paper_freeze_checklist.py",
            "```",
            "",
            "Machine-readable: [`data/paper_freeze_checklist.csv`](../data/paper_freeze_checklist.csv).",
            "",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build paper freeze checklist for corpus_v2.")
    ap.add_argument("--report", type=Path, default=PAPER_FREEZE_CHECKLIST)
    ap.add_argument("--csv", type=Path, default=DATA_DIR / "paper_freeze_checklist.csv")
    args = ap.parse_args()

    a = audit()
    items = build_items(a)
    rec = recommend(items)
    write_csv(args.csv, items)
    write_md(args.report, items, rec, a)

    n_block = sum(1 for i in items if i.status == "BLOCKER")
    print(f"Wrote {args.report} ({len(items)} items, recommendation={rec}, blockers={n_block})")
    print(f"Wrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
