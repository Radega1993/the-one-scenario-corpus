#!/usr/bin/env python3
"""
Audit paper figures/tables for corpus_v2, promote aggregated figures,
generate corpus overview, and write index + readiness report.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import ANALYSIS_DIR, CORPUS_V2, DATA_DIR, REPORTS_ANALYSIS_DIR, SCENARIOS_DIR  # noqa: E402

DEFAULT_MANIFEST = CORPUS_V2 / "manifest.csv"
DEFAULT_DATA = DATA_DIR
DEFAULT_REPORTS = REPORTS_ANALYSIS_DIR
HERE = ANALYSIS_DIR
from lib.report_paths import (  # noqa: E402
    CORRELATION_CORE23_REPORT_TXT,
    CORRELATION_REPORT_TXT,
    PAPER_FIGURES_TABLES_READINESS,
    REPORTS_PIPELINE_DIR,
)
PAPER_DIR = HERE / "figures" / "paper"
MAIN_DIR = PAPER_DIR / "main"
SUPP_DIR = PAPER_DIR / "supplementary"
TABLES_DIR = PAPER_DIR / "tables"
AGG_DIR = HERE / "figures" / "aggregated"
FIGURES_ROOT = HERE / "figures"

EXPECTED_N = 720

# Catalog: stem -> metadata (without extension)
FIGURE_CATALOG: dict[str, dict[str, str]] = {
    "histogram_correlations_pearson_paper": {
        "type": "main",
        "data_source": "correlation_pearson.csv",
        "generator_script": "run_analysis.py --phase figures_paper",
        "description": "Histogram of off-diagonal Pearson r between scenario Z-vectors (core feature space).",
        "scientific_message": "Most scenario pairs are weakly correlated; diversity criterion (few pairs |r|≥0.7) is met.",
        "paper_section": "Methods / Corpus diversity",
    },
    "pca_by_family": {
        "type": "main",
        "data_source": "features_normalized.csv, manifest family",
        "generator_script": "run_analysis.py --phase figures_paper",
        "description": "PCA 2D of normalized features colored by scenario family.",
        "scientific_message": "Seven families occupy distinct regions of the input feature space.",
        "paper_section": "Results / Feature space structure",
    },
    "pca_by_cluster": {
        "type": "main",
        "data_source": "features_normalized.csv, cluster_assignments.csv",
        "generator_script": "run_analysis.py --phase figures_paper",
        "description": "PCA 2D colored by Ward clustering (k=7).",
        "scientific_message": "Unsupervised clusters align partially with families, supporting benchmark stratification.",
        "paper_section": "Results / Clustering",
    },
    "ablation_pairs_high_bar": {
        "type": "main",
        "data_source": "ablation_metrics.csv",
        "generator_script": "run_analysis.py --phase figures_paper",
        "description": "Bar chart: % scenario pairs with |r|≥0.7 for reduced_17, core_23, full_46.",
        "scientific_message": "Core-23 reduces redundant pairs vs full-46 without losing diversity.",
        "paper_section": "Methods / Feature ablation",
    },
    "ablation_silhouette_bar": {
        "type": "main",
        "data_source": "ablation_metrics.csv",
        "generator_script": "run_analysis.py --phase figures_paper",
        "description": "Silhouette (Ward k=7) per feature set in ablation.",
        "scientific_message": "Core-23 yields best cluster separation among ablated sets.",
        "paper_section": "Methods / Feature ablation",
    },
    "heatmap_feature_feature_core": {
        "type": "main",
        "data_source": "feature_feature_correlation_core.csv",
        "generator_script": "run_analysis.py --phase figures_paper",
        "description": "23×23 heatmap of correlations between core features.",
        "scientific_message": "Within-feature redundancy is localized; core set is not orthogonal but manageable.",
        "paper_section": "Supplementary / Feature redundancy",
    },
    "corpus_overview_paper": {
        "type": "main",
        "data_source": "corpus_v2/manifest.csv",
        "generator_script": "build_paper_figures_tables_index.py",
        "description": "Stacked bar: 720 simulations = 60 bases × 12 TPs across 7 families.",
        "scientific_message": "Benchmark scale and family×TP factorial design of corpus_v2.",
        "paper_section": "Methods / Benchmark design",
    },
    "outputs_boxplot_by_tp_paper": {
        "type": "main",
        "data_source": "output_metrics.csv, manifest.csv",
        "generator_script": "run_figures_aggregated.py (promoted)",
        "description": "Boxplots of delivery, latency, overhead, drop by Traffic Profile (12 TPs).",
        "scientific_message": "Traffic profiles induce distinct output regimes (stress vs baseline vs burst).",
        "paper_section": "Results / Output metrics by TP",
    },
    "histogram_correlations_spearman_paper": {
        "type": "supplementary",
        "data_source": "correlation_spearman.csv",
        "generator_script": "run_analysis.py --phase figures_paper",
        "description": "Spearman rank correlation histogram between scenario vectors.",
        "scientific_message": "Robustness check: rank correlations show similar diversity pattern.",
        "paper_section": "Supplementary / Correlation robustness",
    },
    "histogram_correlations_outputs_paper": {
        "type": "supplementary",
        "data_source": "output_metrics.csv",
        "generator_script": "run_analysis.py --phase figures_paper",
        "description": "Histogram of Pearson r between output metric vectors across scenarios.",
        "scientific_message": "Outputs are not trivially collinear across the 720 scenarios.",
        "paper_section": "Supplementary / Output diversity",
    },
    "spatial_coverage_by_family_paper": {
        "type": "supplementary",
        "data_source": "spatial_occupancy_metrics.csv",
        "generator_script": "run_figures_aggregated.py (promoted)",
        "description": "Spatial grid coverage distribution by family.",
        "scientific_message": "Mobility/map regimes differ in explored world fraction (WDM vs open map).",
        "paper_section": "Supplementary / Spatial mobility",
    },
    "message_creation_time_by_tp_paper": {
        "type": "supplementary",
        "data_source": "message_creation_time_summary.csv",
        "generator_script": "analyze_message_creation_times.py (promoted)",
        "description": "Boxplot of median normalized message creation time per TP.",
        "scientific_message": "TP07 concentrates traffic early; full-window TPs show ~uniform creation (median ~0.5).",
        "paper_section": "Supplementary / Traffic timing",
    },
    "protocol_comparison_placeholder": {
        "type": "supplementary",
        "data_source": "N/A (future multi-protocol runs)",
        "generator_script": "build_paper_figures_tables_index.py",
        "description": "Placeholder for routing-protocol comparison (not yet simulated).",
        "scientific_message": "Future work: compare Epidemic with PRoPHET, MaxProp, etc. on corpus_v2 splits.",
        "paper_section": "Discussion / Future work",
    },
}

TABLE_CATALOG: dict[str, dict[str, str]] = {
    "table_core_vs_extended_en.md": {
        "type": "table",
        "data_source": "internal/03-feature_fichas_tecnicas.md, features_normalized.csv",
        "generator_script": "run_analysis.py --phase tables_paper",
        "description": "Core 23 vs extended features with category and rationale.",
        "scientific_message": "Transparent feature selection for scenario characterization.",
        "paper_section": "Methods / Features",
    },
    "table_core_vs_extended_es.md": {
        "type": "table",
        "data_source": "internal/03-feature_fichas_tecnicas.md",
        "generator_script": "run_analysis.py --phase tables_paper",
        "description": "Spanish version of core vs extended features.",
        "scientific_message": "Same as EN table.",
        "paper_section": "Methods / Features (ES draft)",
    },
    "table_diversity_metrics_en.md": {
        "type": "table",
        "data_source": "correlation_report.txt, correlation_core23_report.txt, cluster_assignments*.csv",
        "generator_script": "run_analysis.py --phase tables_paper",
        "description": "Diversity metrics for full_46 and core_23 spaces (n=720).",
        "scientific_message": "Quantitative evidence that the corpus meets diversity thresholds.",
        "paper_section": "Results / Diversity",
    },
    "table_diversity_metrics_es.md": {
        "type": "table",
        "data_source": "correlation_report.txt, correlation_core23_report.txt",
        "generator_script": "run_analysis.py --phase tables_paper",
        "description": "Spanish diversity metrics table.",
        "scientific_message": "Same as EN.",
        "paper_section": "Results / Diversity (ES draft)",
    },
    "table_ablation_metrics_en.md": {
        "type": "table",
        "data_source": "ablation_metrics.csv",
        "generator_script": "run_analysis.py --phase tables_paper",
        "description": "Ablation 17 vs 23 vs 46 features.",
        "scientific_message": "Core-23 balances redundancy reduction and cluster quality.",
        "paper_section": "Methods / Ablation",
    },
    "table_ablation_metrics_es.md": {
        "type": "table",
        "data_source": "ablation_metrics.csv",
        "generator_script": "run_analysis.py --phase tables_paper",
        "description": "Spanish ablation table.",
        "scientific_message": "Same as EN.",
        "paper_section": "Methods / Ablation (ES draft)",
    },
    "table_families_en.md": {
        "type": "table",
        "data_source": ".wiki-clone/05-corpus/Scenario-families.md",
        "generator_script": "run_analysis.py --phase tables_paper",
        "description": "Seven scenario families (counts are base scenarios per family, not 720).",
        "scientific_message": "Taxonomy of mobility/traffic regimes in the benchmark.",
        "paper_section": "Methods / Scenario families",
    },
    "table_families_es.md": {
        "type": "table",
        "data_source": ".wiki-clone/05-corpus/Scenario-families-es.md",
        "generator_script": "run_analysis.py --phase tables_paper",
        "description": "Spanish families table.",
        "scientific_message": "Same as EN.",
        "paper_section": "Methods / Families (ES draft)",
    },
}

PROMOTIONS: list[tuple[Path, Path]] = [
    (AGG_DIR / "outputs_boxplot_by_tp.png", MAIN_DIR / "outputs_boxplot_by_tp_paper.png"),
    (AGG_DIR / "outputs_boxplot_by_tp.pdf", MAIN_DIR / "outputs_boxplot_by_tp_paper.pdf"),
    (AGG_DIR / "spatial_coverage_by_family.png", SUPP_DIR / "spatial_coverage_by_family_paper.png"),
    (AGG_DIR / "spatial_coverage_by_family.pdf", SUPP_DIR / "spatial_coverage_by_family_paper.pdf"),
    (FIGURES_ROOT / "message_creation_time_boxplot_by_tp.png", SUPP_DIR / "message_creation_time_by_tp_paper.png"),
]


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def validate_corpus(manifest_path: Path, data_dir: Path) -> dict[str, Any]:
    m = pd.read_csv(manifest_path)
    n_manifest = len(m)
    checks: dict[str, Any] = {"n_manifest": n_manifest, "ok": n_manifest == EXPECTED_N}

    for name in ("correlation_pearson.csv", "output_metrics.csv", "features_normalized.csv"):
        p = data_dir / name
        if p.is_file():
            df = pd.read_csv(p, index_col=0 if "correlation" in name else None)
            n = len(df) if name != "correlation_pearson.csv" else len(df.index)
            checks[name] = n
            if n != EXPECTED_N:
                checks["ok"] = False
        else:
            checks[name] = None
            checks["ok"] = False
    return checks


def _newer_than(src: Path, dst: Path) -> bool:
    if not dst.is_file() or not src.is_file():
        return False
    return src.stat().st_mtime > dst.stat().st_mtime


def _figure_status(stem: str, png: Path, data_dir: Path) -> str:
    if stem == "protocol_comparison_placeholder":
        return "lista" if png.is_file() else "regenerar"
    cat = FIGURE_CATALOG.get(stem, {})
    src_name = cat.get("data_source", "")
    if not png.is_file():
        return "regenerar"
    stale = False
    for part in src_name.replace(" ", "").split(","):
        p = data_dir / part.strip()
        if p.is_file() and _newer_than(p, png):
            stale = True
            break
    manifest = SCENARIOS_DIR / "corpus_v2" / "manifest.csv"
    if manifest.is_file() and _newer_than(manifest, png):
        stale = True
    if stale and stem not in ("corpus_overview_paper",):
        return "revisar"
    if stem.endswith("_paper") and "promoted" in cat.get("generator_script", ""):
        return "lista"
    return "lista"


def _table_status(path: Path, data_dir: Path, reports_dir: Path) -> str:
    if not path.is_file():
        return "regenerar"
    name = path.name
    stale_sources = [
        data_dir / "ablation_metrics.csv",
        CORRELATION_REPORT_TXT,
        CORRELATION_CORE23_REPORT_TXT,
    ]
    for src in stale_sources:
        if src.is_file() and _newer_than(src, path):
            return "regenerar"
    if name.startswith("table_diversity") or name.startswith("table_ablation"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "n_scenarios" in text and "| 60 |" in text:
            return "regenerar"
        if name.startswith("table_diversity") and "| 720 |" not in text and "| None |" in text:
            return "regenerar"
    return "lista"


def promote_figures() -> list[str]:
    log: list[str] = []
    for src, dst in PROMOTIONS:
        if not src.is_file():
            log.append(f"SKIP missing source: {src.name}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        log.append(f"Copied {src.name} -> {dst.relative_to(HERE)}")
    return log


def plot_corpus_overview(manifest_path: Path, out_base: Path) -> None:
    m = pd.read_csv(manifest_path)
    fam_order = [
        "01_urban", "02_campus", "03_vehicles", "04_rural",
        "05_disaster", "06_social", "07_traffic",
    ]
    labels = ["Urban", "Campus", "Vehicles", "Rural", "Disaster", "Social", "Traffic"]
    bases = m.groupby("family")["scenario_base"].nunique().reindex(fam_order).fillna(0).astype(int)
    sims = m.groupby("family").size().reindex(fam_order).fillna(0).astype(int)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = range(len(fam_order))
    ax.bar(x, bases.values, label="Base scenarios (60 total)", color="#4C72B0", alpha=0.85)
    ax.bar(
        x,
        (sims - bases).values,
        bottom=bases.values,
        label="Traffic-profile variants (+11 per base)",
        color="#DD8452",
        alpha=0.85,
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("Count")
    ax.set_title("corpus_v2: 720 simulations = 60 bases × 12 Traffic Profiles")
    ax.legend(loc="upper right", fontsize=8)
    for i, (b, s) in enumerate(zip(bases.values, sims.values)):
        ax.text(i, s + 2, str(s), ha="center", fontsize=8)
    fig.tight_layout()
    out_base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_base.with_suffix(".png"), dpi=150, bbox_inches="tight")
    fig.savefig(out_base.with_suffix(".pdf"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def create_protocol_placeholder(out_base: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.axis("off")
    ax.text(
        0.5,
        0.55,
        "Routing protocol comparison",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.35,
        "Placeholder — corpus_v2 currently uses Epidemic only.\n"
        "Future: Epidemic vs PRoPHET / MaxProp / Spray-and-Wait on benchmark splits.",
        ha="center",
        va="center",
        fontsize=10,
        color="#444444",
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.savefig(out_base.with_suffix(".pdf"), dpi=150, bbox_inches="tight")
    fig.savefig(out_base.with_suffix(".png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def collect_index_rows(data_dir: Path, reports_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for subdir, ftype in [(MAIN_DIR, "main"), (SUPP_DIR, "supplementary")]:
        if not subdir.is_dir():
            continue
        seen: set[str] = set()
        for png in sorted(subdir.glob("*.png")):
            stem = png.stem
            if stem in seen:
                continue
            seen.add(stem)
            meta = FIGURE_CATALOG.get(stem, {})
            status = _figure_status(stem, png, data_dir)
            rows.append(
                {
                    "filename": png.name,
                    "type": meta.get("type", ftype),
                    "data_source": meta.get("data_source", "see figures/README.md"),
                    "generator_script": meta.get("generator_script", "run_analysis.py --phase figures_paper"),
                    "description": meta.get("description", stem.replace("_", " ")),
                    "scientific_message": meta.get("scientific_message", ""),
                    "paper_section": meta.get("paper_section", "TBD"),
                    "status": status,
                }
            )

    for md in sorted(TABLES_DIR.glob("table_*.md")):
        meta = TABLE_CATALOG.get(md.name, {})
        rows.append(
            {
                "filename": md.name,
                "type": "table",
                "data_source": meta.get("data_source", "analysis/data, reports/"),
                "generator_script": meta.get("generator_script", "run_analysis.py --phase tables_paper"),
                "description": meta.get("description", md.stem),
                "scientific_message": meta.get("scientific_message", ""),
                "paper_section": meta.get("paper_section", "Methods"),
                "status": _table_status(md, data_dir, reports_dir),
            }
        )
    return rows


def write_index(path: Path, rows: list[dict[str, str]], validation: dict[str, Any]) -> None:
    lines = [
        "# Paper figures and tables index (corpus_v2)",
        "",
        f"Generated: {_utc()}",
        "",
        f"**Corpus:** corpus_v2 — {validation['n_manifest']} simulations (expected {EXPECTED_N}).",
        f"**Validation:** {'PASS' if validation.get('ok') else 'CHECK FAILED'}",
        "",
        "| filename | type | data_source | generator_script | description | scientific_message | paper_section | status |",
        "|----------|------|-------------|------------------|-------------|--------------------|---------------|--------|",
    ]
    for r in rows:
        def esc(s: str) -> str:
            return str(s).replace("|", "\\|").replace("\n", " ")

        lines.append(
            f"| {esc(r['filename'])} | {esc(r['type'])} | {esc(r['data_source'])} | "
            f"{esc(r['generator_script'])} | {esc(r['description'])} | {esc(r['scientific_message'])} | "
            f"{esc(r['paper_section'])} | {esc(r['status'])} |"
        )
    lines.extend(
        [
            "",
            "## Regeneration commands",
            "",
            "```bash",
            "scenarios/analysis/.venv/bin/python scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase figures_paper",
            "scenarios/analysis/.venv/bin/python scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase tables_paper",
            "scenarios/analysis/.venv/bin/python scenarios/analysis/run_figures_aggregated.py --corpus corpus_v2",
            "scenarios/analysis/.venv/bin/python scenarios/analysis/build_paper_figures_tables_index.py",
            "```",
            "",
            "Canonical results: [`reports/RESULTADOS_ACTUALES.md`](../../reports/RESULTADOS_ACTUALES.md).",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readiness(
    path: Path,
    rows: list[dict[str, str]],
    validation: dict[str, Any],
    promote_log: list[str],
) -> None:
    main_ok = [r for r in rows if r["type"] == "main" and r["status"] == "lista"]
    main_rev = [r for r in rows if r["type"] == "main" and r["status"] != "lista"]
    supp_ok = [r for r in rows if r["type"] == "supplementary" and r["status"] == "lista"]
    supp_rev = [r for r in rows if r["type"] == "supplementary" and r["status"] != "lista"]
    tab_ok = [r for r in rows if r["type"] == "table" and r["status"] == "lista"]
    tab_regen = [r for r in rows if r["type"] == "table" and r["status"] == "regenerar"]
    missing = [r for r in rows if r["status"] == "regenerar" and not (PAPER_DIR / "main" / r["filename"]).exists()
               and not (PAPER_DIR / "supplementary" / r["filename"]).exists()
               and not (TABLES_DIR / r["filename"]).exists()]

    lines = [
        "# Paper figures and tables readiness (corpus_v2)",
        "",
        f"Generated: {_utc()}",
        "",
        "## Executive summary",
        "",
        f"- **Corpus:** corpus_v2, N={validation.get('n_manifest', '?')} simulations.",
        f"- **Data validation:** correlation_pearson={validation.get('correlation_pearson.csv', '?')}, "
        f"output_metrics={validation.get('output_metrics.csv', '?')}.",
        "- **Policy:** All figures must trace to current `analysis/data/*.csv` (720 rows), not corpus_v1 or 60-scenario pilots.",
        "",
        "## Figures ready (main)",
        "",
    ]
    if main_ok:
        for r in main_ok:
            lines.append(f"- `{r['filename']}` — {r['paper_section']}")
    else:
        lines.append("- None yet.")
    lines.extend(["", "## Figures to review or regenerate (main)", ""])
    for r in main_rev:
        lines.append(f"- `{r['filename']}` — **{r['status']}**")

    lines.extend(["", "## Figures ready (supplementary)", ""])
    for r in supp_ok:
        lines.append(f"- `{r['filename']}` — {r['paper_section']}")
    lines.extend(["", "## Figures to review (supplementary)", ""])
    for r in supp_rev:
        lines.append(f"- `{r['filename']}` — **{r['status']}**")

    lines.extend(["", "## Tables ready", ""])
    for r in tab_ok:
        lines.append(f"- `{r['filename']}`")
    lines.extend(["", "## Tables to regenerate", ""])
    for r in tab_regen:
        lines.append(f"- `{r['filename']}` — run `tables_paper` after correlation/ablation refresh")

    lines.extend(
        [
            "",
            "## Commands to regenerate",
            "",
            "```bash",
            "cd scenarios/analysis",
            ".venv/bin/python run_analysis.py --corpus corpus_v2 --phase tables_paper",
            ".venv/bin/python run_analysis.py --corpus corpus_v2 --phase figures_paper",
            ".venv/bin/python run_figures_aggregated.py --corpus corpus_v2",
            ".venv/bin/python build_paper_figures_tables_index.py",
            "```",
            "",
            "## Still missing for paper closure",
            "",
            "1. **Routing protocol comparison** — placeholder only (`protocol_comparison_placeholder`); requires new simulations.",
            "2. **Optional:** promote additional aggregated heatmaps (`outputs_heatmap_base_x_tp_*`) if space allows.",
            "3. **README cleanup** — ensure all docs reference `corpus_v2`, not `corpus_v1`.",
            "",
            "## Closure checklist",
            "",
            "- [ ] 8–10 main figures (PNG+PDF) — current count: "
            f"{len([r for r in rows if r['type']=='main'])} indexed",
            "- [ ] 4+ supplementary figures",
            "- [ ] 4 EN tables regenerated with n=720 diversity metrics",
            "- [ ] `FIGURES_AND_TABLES_INDEX.md` committed",
            "- [ ] Cross-check numbers vs `RESULTADOS_ACTUALES.md`",
            "",
            "## Promotion log",
            "",
        ]
    )
    lines.extend(f"- {x}" for x in promote_log)
    lines.extend(
        [
            "",
            "## Cross-references",
            "",
            "- [`FIGURES_AND_TABLES_INDEX.md`](../figures/paper/FIGURES_AND_TABLES_INDEX.md)",
            "- [`figures/README.md`](../figures/README.md)",
            "- [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build paper figures/tables index for corpus_v2.")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    ap.add_argument("--skip-promote", action="store_true")
    ap.add_argument("--skip-plots", action="store_true")
    args = ap.parse_args()

    validation = validate_corpus(args.manifest, args.data_dir)
    promote_log: list[str] = []
    if not args.skip_promote:
        promote_log = promote_figures()
    if not args.skip_plots:
        plot_corpus_overview(args.manifest, MAIN_DIR / "corpus_overview_paper")
        create_protocol_placeholder(SUPP_DIR / "protocol_comparison_placeholder")
        promote_log.append("Generated corpus_overview_paper")
        promote_log.append("Generated protocol_comparison_placeholder")

    rows = collect_index_rows(args.data_dir, args.reports_dir)
    index_path = PAPER_DIR / "FIGURES_AND_TABLES_INDEX.md"
    report_path = (
        PAPER_FIGURES_TABLES_READINESS
        if args.reports_dir == DEFAULT_REPORTS
        else args.reports_dir / "paper_figures_tables_readiness.md"
    )
    write_index(index_path, rows, validation)
    write_readiness(report_path, rows, validation, promote_log)

    try:
        from dashboard.data_loaders import write_dashboard_readiness_report

        dash_report = write_dashboard_readiness_report()
        print(f"Wrote {dash_report}")
    except Exception as exc:
        print(f"Warning: dashboard readiness report skipped: {exc}")

    n_lista = sum(1 for r in rows if r["status"] == "lista")
    print(f"Wrote {index_path} ({len(rows)} items, {n_lista} lista)")
    print(f"Wrote {report_path}")
    print(f"Validation ok={validation.get('ok')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
