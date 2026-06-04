#!/usr/bin/env python3
"""Generate wiki rebuild research reports (phase 1 audit + phases 4-8)."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import ANALYSIS_DIR, DATA_DIR, REPO_ROOT, SCENARIOS_DIR  # noqa: E402
from lib.report_paths import (  # noqa: E402
    CURRENT_RESULTS_REVIEW,
    EVALUATION_METRICS_REVIEW,
    PAPER_PHASE1_ACTION_PLAN,
    REPORTS_WIKI_META_DIR,
    SIMULATION_TIME_POLICY,
    WIKI_NEW_INDEX,
    WIKI_OLD_AUDIT,
)

_WIKI_META_WRITES = {
    "wiki_old_audit.md": WIKI_OLD_AUDIT,
    "wiki_new_index.md": WIKI_NEW_INDEX,
}
_VALIDATION_WRITES = {
    "current_results_review.md": CURRENT_RESULTS_REVIEW,
    "evaluation_metrics_review.md": EVALUATION_METRICS_REVIEW,
}
_PAPER_GATE_WRITES = {
    "paper_phase1_action_plan.md": PAPER_PHASE1_ACTION_PLAN,
}
REPO = REPO_ROOT
WIKI = SCENARIOS_DIR / ".wiki-clone"
REPORTS = ANALYSIS_DIR / "reports"
DATA = DATA_DIR
BACKUP = SCENARIOS_DIR / "_archive/wiki/wiki_backup_20260520_133832"

def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def audit_old_wiki() -> str:
    pages = sorted(WIKI.rglob("*.md")) if WIKI.is_dir() else []
    by_top: dict[str, list[str]] = {}
    es_dup = []
    en_pages = []
    for p in pages:
        rel = str(p.relative_to(WIKI))
        top = rel.split("/")[0] if "/" in rel else "(root)"
        by_top.setdefault(top, []).append(rel)
        if rel.endswith("-es.md"):
            es_dup.append(rel)
        elif not rel.endswith("-es.md") and rel not in ("README.md",):
            en_pages.append(rel)

    migrate = [
        "03-reference/Methodological-limitations.md",
        "03-reference/Methodology.md",
        "02-guide/Reproducibility.md",
        "03-reference/Extraction-formulas.md",
        "03-reference/NaN-and-normalization-policy.md",
    ]
    obsolete = [
        "01-home/Home.md (60-scenario freeze, corpus_v1)",
        "04-results/Final-frozen-results.md",
        "04-results/Diversity-status.md",
        "05-corpus/Corpus-overview.md (v1 only)",
        "05-corpus/scenarios-en/* (per-scenario v1 catalog)",
    ]
    incomplete = [
        "No TP01-TP12 traffic profile methodology",
        "No spatial occupancy / grid metrics",
        "No protocol routing benchmark plan",
        "No message analysis window policy",
        "No corpus_v1 revision / manifest_revision",
    ]

    lines = [
        "# Audit of previous wiki (pre-rebuild)",
        "",
        f"Generated: {_utc()}",
        "",
        f"Backup location: `{BACKUP}`",
        "",
        f"- Total markdown pages scanned: **{len(pages)}**",
        f"- English-primary pages (excl. `*-es.md`): **{len(en_pages)}**",
        f"- Spanish duplicate pages (`*-es.md`): **{len(es_dup)}**",
        "",
        "## Inventory by folder",
        "",
        "| Folder | Pages |",
        "|--------|------:|",
    ]
    for k in sorted(by_top):
        lines.append(f"| `{k}` | {len(by_top[k])} |")

    lines.extend(["", "## Pages to migrate (update for corpus_v1)", ""])
    for m in migrate:
        lines.append(f"- `{m}` — rewrite, do not copy verbatim")

    lines.extend(["", "## Obsolete for paper (archive only)", ""])
    for o in obsolete:
        lines.append(f"- {o}")

    lines.extend(["", "## Duplicate / bilingual overhead", ""])
    lines.append(
        "- **223** files are all `.md`; ~half are `*-es.md` mirrors of English pages."
    )
    lines.append("- New wiki: **English-first** at repository root; Spanish optional later.")

    lines.extend(["", "## Incomplete relative to thesis/paper needs", ""])
    for i in incomplete:
        lines.append(f"- {i}")

    lines.extend(
        [
            "",
            "## Proposed new structure",
            "",
            "See [wiki_new_index.md](wiki_new_index.md).",
            "",
            "## Sample of old page paths (first 30)",
            "",
            "```",
            *sorted(en_pages)[:30],
            "...",
            "```",
            "",
        ]
    )
    return "\n".join(lines)

def wiki_new_index() -> str:
    rows = [
        ("Home.md", "Paper-oriented landing page", "draft", "01–14, References"),
        ("01-Research-Goal.md", "DTN/OppNet benchmark research question", "draft", "02, 11"),
        ("02-Corpus-Overview.md", "corpus_v1 vs v2, 720 scenarios", "needs validation", "manifest, revision"),
        ("03-Scenario-Families.md", "7 families, benchmark splits", "draft", "04, 10"),
        ("04-Traffic-Profiles.md", "TP01–TP12 overlays", "stable", "tp_validation_report"),
        ("05-Mobility-and-Maps.md", "Real map vs synthetic mobility", "draft", "06, 12"),
        ("06-Spatial-Occupancy.md", "Grid coverage, heatmaps", "needs validation", "spatial CSV"),
        ("07-Simulation-Time-and-Warmup.md", "endTime, useful window", "draft", "simulation_time_policy"),
        ("08-Message-Generation-and-Analysis-Window.md", "Events*, analysis window", "draft", "message audits"),
        ("09-Evaluation-Metrics.md", "Routing benchmark metrics", "draft", "11"),
        ("10-Results-Summary.md", "Current CSV synthesis", "needs validation", "output_metrics"),
        ("11-Protocol-Benchmarking-Plan.md", "How to compare protocols", "draft", "09"),
        ("12-Limitations-and-Threats-to-Validity.md", "Threats, Helsinki dependency", "draft", "05, 06"),
        ("13-Reproducibility.md", "Scripts, order of execution", "stable", "README analysis"),
        ("14-Paper-Freeze-Checklist.md", "Freeze criteria", "draft", "paper_phase1"),
        ("References.md", "Bibliography pointers", "draft", ""),
        ("CHANGELOG.md", "Wiki change log", "draft", ""),
        ("Glossary.md", "Terms (DTN, TP, WDM, …)", "draft", ""),
    ]
    lines = [
        "# Proposed new wiki index (paper-oriented)",
        "",
        f"Generated: {_utc()}",
        "",
        "Template per page: **Purpose | Content | Status | Internal links | Open questions | Paper usage**",
        "",
        "| Page | Purpose | Status | Links |",
        "|------|---------|--------|-------|",
    ]
    for r in rows:
        lines.append(f"| [{r[0]}]({r[0]}) | {r[1]} | {r[2]} | {r[3]} |")
    lines.append("")
    return "\n".join(lines)

def data_inventory() -> str:
    data_files = sorted(DATA.glob("*"))
    report_files = sorted(REPORTS.glob("*.md"))
    fig_spatial = (
        list((ANALYSIS_DIR / "figures" / "spatial_heatmaps").glob("*.png"))
        if (ANALYSIS_DIR / "figures").is_dir()
        else []
    )
    n_settings = len(list((REPO / "scenarios/corpus_v1").rglob("*.settings")))
    n_reports = len(list((REPO / "reports").glob("*_MessageStatsReport.txt")))

    def row_count(p: Path) -> str:
        if p.suffix != ".csv":
            return "—"
        try:
            return str(sum(1 for _ in open(p)) - 1)
        except OSError:
            return "?"

    lines = [
        "# Data and artifact inventory",
        "",
        f"Generated: {_utc()}",
        "",
        "## Analysis CSV (`scenarios/analysis/data/`)",
        "",
        "| File | Rows (approx) | Role |",
        "|------|-------------:|------|",
    ]
    key = {
        "output_metrics.csv": "Primary routing outcomes (delivery, latency, overhead, drops)",
        "indirect_features_diego.csv": "Connectivity indirect features",
        "spatial_occupancy_metrics.csv": "Grid spatial coverage (partial)",
        "useful_simulation_time_metrics.csv": "Useful simulation time from connectivity",
        "scenario_diagnosis.csv": "Problem flags cross-audit",
        "settings_audit.csv": "Parsed .settings features",
        "corpus_v1_revision_summary.csv": "Per-base revision actions",
        "manifest_revision.csv": "benchmark_split sidecar (720)",
    }
    for p in data_files:
        if p.is_file():
            role = key.get(p.name, "Supporting analysis")
            lines.append(f"| `{p.name}` | {row_count(p)} | {role} |")

    lines.extend(
        [
            "",
            "## Reports (`scenarios/analysis/reports/`)",
            "",
            f"Markdown reports: **{len(report_files)}**",
            "",
            "## Figures",
            "",
            f"- Spatial heatmaps: **{len(fig_spatial)}** PNG under `figures/spatial_heatmaps/`",
            "",
            "## Corpus",
            "",
            f"- `corpus_v1` settings: **{n_settings}**",
            f"- ONE reports in `reports/`: **{n_reports}** MessageStats (approx)",
            "",
            "## Known gaps",
            "",
            "- Spatial occupancy: see `spatial_occupancy_metrics.csv` (720 scenarios when fully processed)",
            "- Simulation metrics may be **pre–corpus_v1 revision** until re-run (see `corpus_v1_revision_changelog.md`)",
            "- Wiki backup: `_archive/wiki/wiki_backup_20260520_133832/`",
            "- Repo map: `scenarios/INVENTARIO.md` (replaces this auto-inventory when archived)",
            "",
        ]
    )
    return "\n".join(lines)

def current_results_review() -> str:
    om = pd.read_csv(DATA / "output_metrics.csv")
    ind = pd.read_csv(DATA / "indirect_features_diego.csv")
    diag = pd.read_csv(DATA / "scenario_diagnosis.csv") if (DATA / "scenario_diagnosis.csv").is_file() else None
    om = om.merge(ind[["scenario", "total_encounters"]], on="scenario", how="left")
    om["tp"] = om["scenario"].str.extract(r"__(TP\d{2})_")[0]
    om["family"] = om["scenario"].str.extract(r"^([^_]+)_")[0]  # wrong - use manifest
    mf = pd.read_csv(REPO / "scenarios/corpus_v1/manifest.csv")
    om = om.drop(columns=["family"], errors="ignore").merge(
        mf[["scenario_name", "family", "scenario_base"]],
        left_on="scenario",
        right_on="scenario_name",
        how="left",
    )

    zero_del = om[om["delivery_ratio"] == 0]
    sat_del = om[om["delivery_ratio"] >= 0.95]
    no_lat = om[om["latency_mean"].isna() | (om["latency_mean"] == 0)]
    extreme_oh = om[om["overhead_ratio"] > 100]
    extreme_drop = om[om["drop_ratio"] > 50]
    zero_enc = om[om["total_encounters"] == 0]

    tp_agg = om.groupby("tp").agg(
        delivery_mean=("delivery_ratio", "mean"),
        delivery_std=("delivery_ratio", "std"),
        overhead_mean=("overhead_ratio", "mean"),
        drops_mean=("drop_ratio", "mean"),
        n=("scenario", "count"),
    ).reset_index()

    fam_agg = om.groupby("family").agg(
        delivery_mean=("delivery_ratio", "mean"),
        encounters_mean=("total_encounters", "mean"),
        n=("scenario", "count"),
    ).reset_index().sort_values("delivery_mean", ascending=False)

    lines = [
        "# Current simulation results review",
        "",
        f"Generated: {_utc()}",
        "",
        f"- Scenarios in `output_metrics.csv`: **{len(om)}**",
        f"- `delivery_ratio == 0`: **{len(zero_del)}**",
        f"- `delivery_ratio >= 0.95`: **{len(sat_del)}**",
        f"- `latency_mean` empty/zero: **{len(no_lat)}**",
        f"- `overhead_ratio > 100`: **{len(extreme_oh)}**",
        f"- `drop_ratio > 50`: **{len(extreme_drop)}**",
        f"- `total_encounters == 0`: **{len(zero_enc)}**",
        "",
        "> **Caveat:** metrics may reflect settings before `apply_corpus_v1_revision.py`; re-simulation required.",
        "",
        "## Top problematic scenarios (P0 from diagnosis)",
        "",
    ]
    if diag is not None:
        p0 = diag[diag["priority"] == "P0"].head(15)
        lines.append("| scenario | delivery | overhead | flags |")
        lines.append("|----------|----------:|---------:|-------|")
        for _, r in p0.iterrows():
            lines.append(
                f"| `{r['scenario']}` | {r.get('delivery_ratio', '')} | {r.get('overhead_ratio', '')} | `{r.get('problem_flags', '')}` |"
            )

    lines.extend(["", "## TP profiles (mean delivery std across bases)", ""])
    lines.append("| TP | mean delivery | std delivery | mean overhead | mean drops | n |")
    lines.append("|----|--------------:|-------------:|--------------:|-----------:|--:|")
    for _, r in tp_agg.sort_values("tp").iterrows():
        lines.append(
            f"| `{r['tp']}` | {r['delivery_mean']:.4f} | {r['delivery_std']:.4f} | "
            f"{r['overhead_mean']:.1f} | {r['drops_mean']:.1f} | {int(r['n'])} |"
        )

    lines.extend(["", "## Families (mean delivery)", ""])
    lines.append("| family | mean delivery | mean encounters | n |")
    lines.append("|--------|--------------:|----------------:|--:|")
    for _, r in fam_agg.iterrows():
        lines.append(
            f"| `{r['family']}` | {r['delivery_mean']:.4f} | {r['encounters_mean']:.0f} | {int(r['n'])} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- **TP04** shows highest drops/overhead — stress profile, not main benchmark.",
            "- **TP05** often zero delivery with short TTL — diagnostic.",
            "- **TP12** zero cross-group delivery is structural when partition is valid.",
            "- **04_rural** R1/R11: zero contacts — configuration or control extremes.",
            "",
        ]
    )
    return "\n".join(lines)

def evaluation_metrics_review() -> str:
    lines = [
        "# Evaluation metrics review (routing benchmark)",
        "",
        f"Generated: {_utc()}",
        "",
        "Source: `MessageStatsReport` (The ONE) → `output_metrics.csv`; indirect mobility from `ConnectivityONEReport`.",
        "",
        "## Primary metrics (paper main tables)",
        "",
        "| Metric | ONE source | Measures | Interpretation | Risks | Paper use |",
        "|--------|------------|----------|----------------|-------|-------------|",
        "| delivery_ratio | delivery_prob | Fraction created messages delivered | Higher = better reach | Saturated ~1 hides differentiation | Main comparison |",
        "| latency_mean | latency_avg | Mean delivery delay (s) | Lower = faster | NaN if zero deliveries | Main comparison |",
        "| overhead_ratio | overhead_ratio | Relay cost vs deliveries | Lower = efficient | Extreme if few deliveries | Main comparison |",
        "| drop_ratio | derived | Drops / started | Loss under congestion | High on TP04/TP10 | Secondary |",
        "",
        "## Secondary (MessageStatsReport fields)",
        "",
        "| Metric | Field | Use |",
        "|--------|-------|-----|",
        "| created | created | Load generated |",
        "| started | started | Forwarding attempts |",
        "| relayed | relayed | Relay load |",
        "| delivered | delivered | Absolute deliveries |",
        "| hopcount_avg | hopcount_avg | Path length |",
        "| response_prob | response_prob | Request-response (if used) |",
        "",
        "## Diagnostic / mobility (not protocol outcomes)",
        "",
        "| Metric | Source | Use |",
        "|--------|--------|-----|",
        "| total_encounters | ConnectivityONEReport | Mobility/connectivity |",
        "| contact_time_per_min | indirect CSV | Activity density |",
        "| coverage_world_ratio | SpatialOccupancyReport | Map usage |",
        "",
        "## Minimum set for protocol comparison",
        "",
        "1. delivery_ratio",
        "2. latency_mean (only if delivery > 0)",
        "3. overhead_ratio",
        "4. drop_ratio",
        "5. hopcount_avg (from report parsing extension)",
        "6. total_encounters (context column)",
        "",
        "## Open questions",
        "",
        "- Add hopcount/buffertime to `output_metrics.csv` pipeline?",
        "- Normalize latency by useful window vs full endTime?",
        "",
    ]
    return "\n".join(lines)

def message_analysis_window_policy() -> str:
    """Deprecated stub — canonical report from build_message_analysis_window_policy.py."""
    return (
        "# Message analysis window policy\n\n"
        "**Canonical report:** run `build_message_analysis_window_policy.py`.\n"
        "This stub is not regenerated by `build_wiki_research_reports.py`.\n"
    )

def simulation_time_policy() -> tuple[pd.DataFrame, str]:
    useful = pd.read_csv(DATA / "useful_simulation_time_metrics.csv")
    spatial = pd.read_csv(DATA / "spatial_occupancy_metrics.csv")
    om = pd.read_csv(DATA / "output_metrics.csv")
    mf = pd.read_csv(REPO / "scenarios/corpus_v1/manifest.csv")

    sp = spatial[["scenario", "final_coverage_pct", "time_to_50pct", "time_to_80pct", "time_to_90pct"]].copy()
    sp = sp.rename(columns={"final_coverage_pct": "coverage_total_pct"})
    df = mf[["scenario_name", "family", "Scenario.endTime"]].rename(columns={"scenario_name": "scenario"})
    df = df.merge(useful, on="scenario", how="left")
    df = df.merge(sp, on="scenario", how="left")
    df = df.merge(om[["scenario", "delivery_ratio"]], on="scenario", how="left")

    df["end_time"] = pd.to_numeric(df["Scenario.endTime"], errors="coerce").fillna(43200)
    df["coverage_total"] = pd.to_numeric(df["coverage_total_pct"], errors="coerce") / 100.0
    df["recommended_warmup"] = (df["end_time"] * 0.05).round(0)
    df["recommended_cutoff"] = (df["end_time"] * 0.90).round(0)
    df["recommended_useful_window"] = df.apply(
        lambda r: f"[{int(r['recommended_warmup'])},{int(r['recommended_cutoff'])}]", axis=1
    )
    df["decision"] = "keep_endTime"
    df.loc[df["coverage_total"].notna() & (df["coverage_total"] < 0.12), "decision"] = "review_worldSize"
    df.loc[df["total_encounters"] == 0, "decision"] = "exclude_or_fix_mobility"
    df["justification"] = "Default 5% warmup, 90% cutoff; see useful_simulation_time_metrics"

    out_cols = [
        "scenario", "family", "end_time", "coverage_total",
        "time_to_50pct", "time_to_80pct", "time_to_90pct",
        "total_encounters", "delivery_ratio",
        "recommended_warmup", "recommended_cutoff", "recommended_useful_window",
        "decision", "justification",
    ]
    out = df[[c for c in out_cols if c in df.columns]]

    md = [
        "# Simulation time and warmup policy",
        "",
        f"Generated: {_utc()}",
        "",
        f"- Rows: **{len(out)}**",
        f"- CSV: `data/simulation_time_policy.csv`",
        "",
        "## Global policy",
        "",
        "- `warmup = 5% × endTime` (2160 s for 12 h runs)",
        "- `analysis_cutoff = 90% × endTime` for message outcome metrics",
        "- `Scenario.endTime = 43200` s is **sufficient** for connectivity-heavy scenarios (see `useful_time_ratio` ≈ 1)",
        "",
        "## Spatial coverage linkage",
        "",
        "Where `coverage_total < 12%`, prefer **worldSize crop** before extending endTime.",
        "",
        "## Family notes",
        "",
        "| family | note |",
        "|--------|------|",
        "| 01_urban | Low spatial % often map oversized, not short sim |",
        "| 04_rural | R1/R11 may need mobility fix not longer time |",
        "",
    ]
    return out, "\n".join(md)

def map_realism_review() -> str:
    sa = pd.read_csv(DATA / "settings_audit.csv")
    helsinki = (sa["map_dataset"] == "HelsinkiMedium").sum()
    lines = [
        "# Map realism review",
        "",
        f"Generated: {_utc()}",
        "",
        f"- Bases using HelsinkiMedium: **{helsinki}** / {sa['scenario_base'].nunique()} unique bases in audit",
        "- U2/U4 migrated to **Manhattan** (projected activity WKT) in corpus_v1 revision",
        "",
        "## What real maps add",
        "",
        "- Constrained movement on roads (MapBasedMovement, WDM)",
        "- Realistic geographic extent and bottlenecks",
        "",
        "## Limits of single-map reuse",
        "",
        "- Urban/vehicle/disaster scenarios share Helsinki geometry → correlated spatial features",
        "- Cannot claim geographic diversity without multiple maps",
        "",
        "## Large worldSize + low coverage",
        "",
        "| Case | Interpretation | Action |",
        "|------|----------------|--------|",
        "| WDM on full Helsinki grid, ~8–10% world coverage | Mobility explores roads, not empty world | Crop worldSize to roads bbox |",
        "| RWP tiny range in huge world | Design bug | Reduce world or increase range |",
        "",
        "## Recommendations",
        "",
        "1. **Keep Helsinki** for WDM urban benchmark (after worldSize crop).",
        "2. **Manhattan** for U2/U4 diversity (document projected WKT limitation).",
        "3. **Campus/rural/social:** synthetic worlds without OSM — separate map realism from mobility realism.",
        "4. **Paper:** separate \"map-constrained\" vs \"synthetic arena\" families in methods.",
        "",
    ]
    return "\n".join(lines)

def paper_phase1_action_plan() -> str:
    return f"""# Paper phase 1 action plan

Generated: {_utc()}

## Closed decisions

- Corpus benchmark = **synthetic/semi-synthetic**, not empirical traces
- **corpus_v1**: 720 scenarios = 60 bases × 12 TP
- Traffic = Events overlay; mobility from v1 base per scenario
- Minimum routing metrics: delivery, latency, overhead, drops
- Wiki rebuilt paper-oriented; old wiki backed up to `_archive/wiki/wiki_backup_20260520_133832`

## Pending decisions

- [ ] Re-run full corpus after settings revision
- [ ] Complete spatial occupancy 720/720
- [ ] Add hopcount to output_metrics pipeline
- [ ] Freeze benchmark_split in main manifest

## Priority tasks

1. Re-simulate corpus_v1 with Diego17 + spatial reports
2. Re-run `diagnose_scenarios.py` and `build_corpus_v1_revision_plan.py`
3. Regenerate `output_metrics.csv` from new reports
4. Select **main** benchmark subset (~40 bases × TP01–08) from `manifest_revision.csv`
5. First protocol comparison (Epidemic vs Prophet vs …) on main split only

## Missing for paper

| Item | Status |
|------|--------|
| Protocol comparison tables | Not started |
| Spatial figures all families | Partial |
| Message window in metrics pipeline | Policy only |
| Statistical tests across protocols | Not started |

## Can write in Methods now

- Scenario families and TP design
- Synthetic traffic generation (MessageEventGenerator)
- Map-constrained vs synthetic mobility taxonomy
- Evaluation metrics definitions
- Reproducibility (scripts in `scenarios/analysis/`)

## Do not claim yet

- Final delivery rankings after revision until re-sim
- Geographic diversity beyond Helsinki+Manhattan
- Optimal corpus size without re-diagnosis

## Recommended execution order

1. Simulation batch (720)
2. `run_analysis.py --phase output_metrics indirects`
3. `analyze_spatial_occupancy.py` (full manifest)
4. `diagnose_scenarios.py` + research reports refresh
5. Protocol experiments on `benchmark_split=main`
"""

def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    writers: dict[str, Path] = {
        **_WIKI_META_WRITES,
        **_VALIDATION_WRITES,
        **_PAPER_GATE_WRITES,
    }
    fn_map = {
        "wiki_old_audit.md": audit_old_wiki,
        "wiki_new_index.md": wiki_new_index,
        "current_results_review.md": current_results_review,
        "evaluation_metrics_review.md": evaluation_metrics_review,
        "paper_phase1_action_plan.md": paper_phase1_action_plan,
    }
    for name, out_path in writers.items():
        fn = fn_map[name]
        text = fn()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {out_path}")

    st_df, st_md = simulation_time_policy()
    st_df.to_csv(DATA / "simulation_time_policy.csv", index=False)
    SIMULATION_TIME_POLICY.parent.mkdir(parents=True, exist_ok=True)
    SIMULATION_TIME_POLICY.write_text(st_md, encoding="utf-8")
    print(f"Wrote simulation_time_policy.csv ({len(st_df)} rows)")
    return 0

if __name__ == "__main__":
    sys.exit(main())