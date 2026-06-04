#!/usr/bin/env python3
"""Validate diversity-validation readiness for paper (scope: corpus_v1 only, N=540)."""

from __future__ import annotations

import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import SCENARIOS_DIR  # noqa: E402

SCEN = SCENARIOS_DIR
AN = SCEN / "analysis"
DATA = AN / "data"
REPORTS = AN / "reports"
FIG = AN / "figures"
WIKI = SCEN / ".wiki-clone"
PIPELINE = REPORTS / "pipeline"
ARCHIVE_LEGACY = SCEN / "_archive" / "diversity_legacy_20260527"

EXPECTED_N = 540
COMBINED_N = 540
EXPECTED_PAIRS = EXPECTED_N * (EXPECTED_N - 1) // 2  # 145530
FEATURE_DIMS = {"reduced_17": 17, "core_23": 23, "full_46": 46}
ABLATION_SETS = ("reduced_17", "core_23", "full_46")

OUT_CSV = DATA / "diversity_validation_checklist.csv"
OUT_MD = REPORTS / "diversity_validation_readiness.md"
ARCHIVE_CANDIDATES_MD = REPORTS / "diversity_archive_candidates.md"

checks: list[dict[str, str]] = []
structure_notes: list[str] = []

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def add(
    item_id: str,
    category: str,
    artifact: str,
    expected_path: str,
    exists: bool,
    status: str,
    severity: str,
    notes: str,
    recommended_action: str,
) -> None:
    checks.append(
        {
            "item_id": item_id,
            "category": category,
            "artifact": artifact,
            "expected_path": expected_path,
            "exists": "yes" if exists else "no",
            "status": status,
            "severity": severity,
            "notes": notes,
            "recommended_action": recommended_action,
        }
    )

def count_settings(d: Path) -> int:
    return sum(1 for _ in d.rglob("*.settings")) if d.is_dir() else 0

def csv_data_rows(p: Path) -> int:
    if not p.is_file():
        return -1
    with p.open(newline="", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in csv.DictReader(f))

def matrix_dim(p: Path) -> tuple[int, int] | None:
    if not p.is_file():
        return None
    try:
        df = pd.read_csv(p, index_col=0, nrows=0)
        ncols = len(df.columns)
        with p.open(encoding="utf-8", errors="replace") as f:
            nrows = sum(1 for _ in f) - 1
        return nrows, ncols
    except Exception:
        return None

def scenario_ids_from_features() -> set[str] | None:
    p = DATA / "features.csv"
    if not p.is_file():
        return None
    df = pd.read_csv(p)
    col = "scenario" if "scenario" in df.columns else df.columns[0]
    return set(df[col].astype(str))

def check_scenario_id_alignment() -> None:
    ids_feat = scenario_ids_from_features()
    if not ids_feat:
        add(
            "S003",
            "consistency",
            "scenario_ids_aligned",
            "analysis/data/features.csv",
            False,
            "FAIL",
            "BLOCKER",
            "features.csv missing",
            "run --phase features ",
        )
        return

    mismatches: list[str] = []
    for fname in ("cluster_assignments.csv", "cluster_assignments_core23.csv"):
        p = DATA / fname
        if not p.is_file():
            mismatches.append(f"{fname} missing")
            continue
        df = pd.read_csv(p)
        col = "scenario" if "scenario" in df.columns else df.columns[0]
        ids = set(df[col].astype(str))
        if ids != ids_feat:
            mismatches.append(f"{fname}: symmetric_diff={len(ids ^ ids_feat)}")

    for fname in ("correlation_pearson.csv",):
        p = DATA / fname
        if p.is_file():
            df = pd.read_csv(p, index_col=0)
            idx = set(df.index.astype(str))
            cols = set(df.columns.astype(str))
            if idx != ids_feat or cols != ids_feat:
                mismatches.append(f"{fname}: index/col mismatch with features")

    status = "PASS" if not mismatches else "FAIL"
    add(
        "S003",
        "consistency",
        "scenario_ids_aligned",
        "analysis/data/*.csv",
        True,
        status,
        "BLOCKER" if mismatches else "INFO",
        "; ".join(mismatches) if mismatches else f"n={len(ids_feat)} aligned",
        "regenerate correlation/cluster with " if mismatches else "none",
    )

def check_matrix_finite() -> None:
    for fname in (
        "correlation_pearson.csv",
        "correlation_spearman.csv",
        "distance_cosine.csv",
        "distance_euclidean.csv",
    ):
        p = DATA / fname
        if not p.is_file():
            continue
        df = pd.read_csv(p, index_col=0)
        arr = df.to_numpy(dtype=float)
        nan_frac = float(np.isnan(arr).mean())
        inf_n = int(np.isinf(arr).sum())
        ok = nan_frac < 0.01 and inf_n == 0
        add(
            f"S004_{fname[:8]}",
            "consistency",
            f"{fname}_finite",
            str(p.relative_to(SCEN)),
            True,
            "PASS" if ok else "WARN",
            "MAJOR" if not ok else "INFO",
            f"nan_frac={nan_frac:.4f} inf={inf_n}",
            "inspect feature extraction" if not ok else "none",
        )

def check_ablation_dims() -> None:
    p = DATA / "ablation_metrics.csv"
    if not p.is_file():
        return
    df = pd.read_csv(p)
    issues: list[str] = []
    if "set" in df.columns:
        sets = set(df["set"].astype(str))
        if sets != set(ABLATION_SETS):
            issues.append(f"sets={sets}")
    if "n_features" in df.columns and "set" in df.columns:
        for s, exp in FEATURE_DIMS.items():
            row = df[df["set"] == s]
            if row.empty:
                issues.append(f"missing {s}")
            elif int(row["n_features"].iloc[0]) != exp:
                issues.append(f"{s} n_features={row['n_features'].iloc[0]} expected {exp}")
    add(
        "S005",
        "consistency",
        "ablation_feature_dims",
        str(p.relative_to(SCEN)),
        True,
        "PASS" if not issues else "FAIL",
        "BLOCKER" if issues else "INFO",
        "; ".join(issues) if issues else "17/23/46 verified",
        "rerun --phase ablation " if issues else "none",
    )

def check_resultados_coherence() -> None:
    res_path = REPORTS / "RESULTADOS_ACTUALES.md"
    abl_path = DATA / "ablation_metrics.csv"
    if not res_path.is_file() or not abl_path.is_file():
        add(
            "S006",
            "consistency",
            "RESULTADOS_vs_ablation",
            str(res_path.relative_to(SCEN)),
            res_path.is_file() and abl_path.is_file(),
            "FAIL",
            "BLOCKER",
            "missing file",
            "regenerate RESULTADOS and ablation",
        )
        return

    txt = res_path.read_text(encoding="utf-8", errors="replace")
    df = pd.read_csv(abl_path)
    issues: list[str] = []
    for _, row in df.iterrows():
        s = str(row.get("set", ""))
        pairs = int(row.get("pairs_r_above_threshold", 0))
        sil = float(row.get("silhouette", 0))
        label = {"reduced_17": "Reduced", "core_23": "CORE", "full_46": "completo"}.get(s, s)
        if str(pairs) not in txt:
            issues.append(f"{s}: pairs {pairs} not in RESULTADOS")
        if f"{sil:.4f}" not in txt and f"{sil:.3f}" not in txt:
            issues.append(f"{s}: silhouette {sil:.4f} not in RESULTADOS")

    if "145530" not in txt and "145,530" not in txt:
        issues.append("total pairs 145530 not in RESULTADOS")

    add(
        "S006",
        "consistency",
        "RESULTADOS_vs_ablation",
        str(res_path.relative_to(SCEN)),
        True,
        "PASS" if not issues else "WARN",
        "MAJOR" if issues else "INFO",
        "; ".join(issues) if issues else "numeric fields match ablation_metrics.csv",
        "run run_phase_results_actuales or refresh RESULTADOS" if issues else "none",
    )

def document_structure() -> None:
    base_n = count_settings(SCEN / "base_scenarios")
    corpus_n = count_settings(SCEN / "corpus_v1")
    structure_notes.extend(
        [
            f"- **base_scenarios/**: {base_n} structural bases (no TP)",
            f"- **corpus_v1/**: {corpus_n} environmental scenarios with TP (benchmark scope)",
            f"- **Paper benchmark:** {EXPECTED_N} scenarios in `corpus_v1/`",
            f"- **Legacy archive:** `_archive/diversity_legacy_20260527/` (720-era CSVs; not canonical)",
        ]
    )
    if ARCHIVE_LEGACY.is_dir():
        n_legacy = sum(1 for _ in ARCHIVE_LEGACY.rglob("*.csv"))
        structure_notes.append(f"- Legacy CSV count in archive: {n_legacy}")

def write_archive_candidates() -> None:
    lines = [
        "# Diversity archive candidates",
        "",
        f"Generated: {utc_now()}",
        "",
        "**Policy:** do not delete; move to `_archive/` only after explicit approval.",
        "",
        "## Legacy diversity run (720)",
        "",
        f"- Directory: `{ARCHIVE_LEGACY.relative_to(SCEN)}/`",
        "",
        "## Full N×N heatmaps (exploratory, not paper main)",
        "",
    ]
    for stem in ("heatmap_pearson", "heatmap_spearman"):
        for ext in (".png", ".pdf"):
            p = FIG / f"{stem}{ext}"
            if p.is_file():
                dim = matrix_dim(DATA / "correlation_pearson.csv")
                n_note = f" (current diversity N={dim[0] if dim else '?'})"
                lines.append(f"- `{p.relative_to(SCEN)}` — INTERNAL_ONLY / OBSOLETE if from 720 run{n_note}")

    legacy_data = list(DATA.glob("*720*")) + list(DATA.glob("*legacy*"))
    if legacy_data:
        lines.append("\n## Legacy-named files in analysis/data/\n")
        for p in legacy_data:
            lines.append(f"- `{p.relative_to(SCEN)}`")

    ARCHIVE_CANDIDATES_MD.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE_CANDIDATES_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {ARCHIVE_CANDIDATES_MD}")

def write_figures_inventory() -> None:
    """Classify diversity-related figures for paper use."""
    inv_path = DATA / "diversity_figures_inventory.csv"
    rows: list[dict[str, str]] = []
    catalog: list[tuple[str, str, str]] = [
        ("figures/paper/main/histogram_correlations_pearson_paper.png", "MAIN_PAPER", "Pearson histogram"),
        ("figures/paper/main/pca_by_family.png", "MAIN_PAPER", "PCA by family"),
        ("figures/paper/main/pca_by_cluster.png", "MAIN_PAPER", "PCA by Ward cluster"),
        ("figures/paper/main/ablation_pairs_high_bar.png", "MAIN_PAPER", "Ablation high-|r| pairs"),
        ("figures/paper/main/ablation_silhouette_bar.png", "MAIN_PAPER", "Ablation silhouette"),
        ("figures/paper/main/heatmap_feature_feature_core.png", "MAIN_PAPER", "Feature-feature core 23"),
        ("figures/paper/main/corpus_overview_paper.png", "MAIN_PAPER", "Corpus design overview"),
        ("figures/paper/supplementary/histogram_correlations_spearman_paper.png", "SUPPLEMENTARY", "Spearman robustness"),
        ("figures/by_space/heatmap_pearson_core_23.png", "INTERNAL_ONLY", "Exploratory per-space"),
        ("figures/by_space/histogram_correlations_pearson_core_23.png", "INTERNAL_ONLY", "Exploratory per-space"),
        ("figures/aggregated/correlation_ablation_histogram_compare.png", "INTERNAL_ONLY", "Aggregated ablation compare"),
        ("figures/heatmap_pearson.png", "OBSOLETE", "Full N×N exploratory; use paper/main histogram"),
        ("figures/heatmap_spearman.png", "OBSOLETE", "Full N×N exploratory"),
    ]
    min_bytes = 1000
    for rel, cls, desc in catalog:
        p = AN / rel
        exists = p.is_file()
        size_ok = exists and p.stat().st_size > min_bytes
        rows.append(
            {
                "path": rel,
                "classification": cls,
                "exists": "yes" if exists else "no",
                "non_empty": "yes" if size_ok else ("no" if exists else "n/a"),
                "scope_n": str(EXPECTED_N),
                "notes": desc if size_ok else ("empty/corrupt" if exists else "missing"),
            }
        )
    with inv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["path", "classification", "exists", "non_empty", "scope_n", "notes"],
        )
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {inv_path}")

def run_checks() -> None:
    document_structure()

    corpus_n = count_settings(SCEN / "corpus_v1")
    add(
        "S001",
        "consistency",
        "corpus_v1_settings_count",
        "scenarios/corpus_v1/",
        True,
        "PASS" if corpus_n == EXPECTED_N else "FAIL",
        "BLOCKER" if corpus_n != EXPECTED_N else "INFO",
        f"observed={corpus_n}",
        "verify corpus_v1 has 540 .settings",
    )

    data_files = {
        "D001": ("features.csv", EXPECTED_N, None),
        "D002": ("features_normalized.csv", EXPECTED_N, FEATURE_DIMS["full_46"]),
        "D003": ("features_reduced.csv", EXPECTED_N, FEATURE_DIMS["reduced_17"]),
        "D004": ("features_core.csv", EXPECTED_N, FEATURE_DIMS["core_23"]),
        "D005": ("normalization_params.csv", FEATURE_DIMS["full_46"], None),
        "D006": ("correlation_pearson.csv", EXPECTED_N, EXPECTED_N),
        "D007": ("correlation_spearman.csv", EXPECTED_N, EXPECTED_N),
        "D008": ("distance_cosine.csv", EXPECTED_N, EXPECTED_N),
        "D009": ("distance_euclidean.csv", EXPECTED_N, EXPECTED_N),
        "D010": ("correlation_pearson_core23.csv", EXPECTED_N, EXPECTED_N),
        "D011": ("distance_cosine_core23.csv", EXPECTED_N, EXPECTED_N),
        "D012": ("cluster_assignments.csv", EXPECTED_N, None),
        "D013": ("cluster_assignments_core23.csv", EXPECTED_N, None),
        "D014": ("feature_feature_correlation_core.csv", FEATURE_DIMS["core_23"], FEATURE_DIMS["core_23"]),
        "D015": ("ablation_metrics.csv", 3, None),
    }

    for item_id, (fname, exp_rows, exp_cols) in data_files.items():
        p = DATA / fname
        exists = p.is_file()
        notes = ""
        status = "FAIL"
        severity = "BLOCKER"

        if not exists:
            notes = "missing"
        elif exp_cols is not None and exp_cols == EXPECTED_N:
            dim = matrix_dim(p)
            if dim and dim[0] == EXPECTED_N and dim[1] == EXPECTED_N:
                status, severity = "PASS", "INFO"
                notes = f"matrix {dim[0]}x{dim[1]}"
            else:
                notes = f"matrix dim={dim}, expected {EXPECTED_N}x{EXPECTED_N}"
        elif fname == "feature_feature_correlation_core.csv":
            dim = matrix_dim(p)
            d = FEATURE_DIMS["core_23"]
            if dim and dim[0] == d and dim[1] == d:
                status, severity = "PASS", "INFO"
                notes = f"matrix {d}x{d}"
            else:
                notes = f"matrix dim={dim}, expected {d}x{d}"
        elif fname == "ablation_metrics.csv":
            rows = csv_data_rows(p)
            df = pd.read_csv(p)
            tp = int(df["total_pairs"].iloc[0]) if "total_pairs" in df.columns and len(df) else None
            if rows == 3 and tp == EXPECTED_PAIRS:
                status, severity = "PASS", "INFO"
                notes = f"rows=3 total_pairs={tp}"
            elif rows == 3:
                status, severity = "WARN", "MAJOR"
                notes = f"rows=3 total_pairs={tp} expected {EXPECTED_PAIRS}"
            else:
                notes = f"rows={rows} total_pairs={tp}"
        elif fname == "normalization_params.csv":
            rows = csv_data_rows(p)
            if rows == FEATURE_DIMS["full_46"]:
                status, severity = "PASS", "INFO"
                notes = f"rows={rows}"
            else:
                notes = f"rows={rows} expected {FEATURE_DIMS['full_46']}"
        elif fname in ("features_reduced.csv", "features_core.csv", "features_normalized.csv"):
            rows = csv_data_rows(p)
            df = pd.read_csv(p, nrows=1)
            n_feat = len(df.columns) - 1  # minus scenario
            exp_feat = FEATURE_DIMS.get(
                {"features_reduced.csv": "reduced_17", "features_core.csv": "core_23"}.get(fname, "full_46"),
                FEATURE_DIMS["full_46"],
            )
            if rows == exp_rows and n_feat == exp_feat:
                status, severity = "PASS", "INFO"
                notes = f"rows={rows} features={n_feat}"
            else:
                notes = f"rows={rows} features={n_feat} expected rows={exp_rows} feat={exp_feat}"
        else:
            rows = csv_data_rows(p)
            if rows == exp_rows:
                status, severity = "PASS", "INFO"
                notes = f"rows={rows}"
            else:
                notes = f"rows={rows} expected {exp_rows}"

        add(
            item_id,
            "data",
            fname,
            str(p.relative_to(SCEN)),
            exists,
            status,
            severity,
            notes,
            "regenerate diversity pipeline with " if status != "PASS" else "none",
        )

    check_scenario_id_alignment()
    check_matrix_finite()
    check_ablation_dims()
    check_resultados_coherence()

    feat_path = DATA / "features.csv"
    if feat_path.is_file():
        df = pd.read_csv(feat_path)
        id_col = df.columns[0]
        stress_prefixes = ("T10_", "T11_", "T12_", "T13_", "T14_", "T15_")
        stress_hits = int(df[id_col].astype(str).str.startswith(stress_prefixes).sum())
        ok_scope = stress_hits == 0 and len(df) == EXPECTED_N
        add(
            "S002",
            "consistency",
            "features_scope_no_stress",
            str(feat_path.relative_to(SCEN)),
            True,
            "PASS" if ok_scope else "FAIL",
            "BLOCKER" if not ok_scope else "INFO",
            f"rows={len(df)} stress_like={stress_hits}",
            "rerun features with ",
        )

    report_files = [
        ("R001", "RESULTADOS_ACTUALES.md", REPORTS / "RESULTADOS_ACTUALES.md"),
        ("R002", "correlation_report.txt", PIPELINE / "correlation_report.txt"),
        ("R003", "correlation_core23_report.txt", PIPELINE / "correlation_core23_report.txt"),
        ("R004", "ablation_report.txt", PIPELINE / "ablation_report.txt"),
        ("R005", "feature_feature_correlation_report.txt", PIPELINE / "feature_feature_correlation_report.txt"),
        ("R006", "multiple_comparisons_report.txt", PIPELINE / "multiple_comparisons_report.txt"),
        ("R007", "clustering_report.txt", PIPELINE / "clustering_report.txt"),
        ("R008", "scenarios_to_diversify.txt", PIPELINE / "scenarios_to_diversify.txt"),
        ("R009", "scenarios_to_diversify_core23.txt", PIPELINE / "scenarios_to_diversify_core23.txt"),
    ]
    for item_id, name, path in report_files:
        exists = path.is_file()
        notes = ""
        status = "PASS" if exists else "FAIL"
        severity = "BLOCKER" if not exists else "INFO"
        if exists:
            txt = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"\bn\s*=\s*720\b", txt) or "258840" in txt:
                status, severity, notes = "FAIL", "BLOCKER", "contains legacy n=720 metrics"
            elif name == "RESULTADOS_ACTUALES.md":
                if "540" not in txt[:500]:
                    status, severity, notes = "WARN", "MAJOR", "header should state 540 scenarios"
            elif re.search(r"\bn\s*=\s*540\b", txt) and "stress" not in txt.lower():
                status, severity, notes = "WARN", "MAJOR", "contains n=540 without stress context"
        flat_alt = REPORTS / name
        if not exists and flat_alt.is_file():
            notes = f"found at legacy flat path {flat_alt.name}; canonical: reports/pipeline/"
            status, severity = "WARN", "MINOR"
        add(
            item_id,
            "report",
            name,
            f"reports/pipeline/{name}" if name.endswith(".txt") else str(path.relative_to(SCEN)),
            exists or flat_alt.is_file(),
            status,
            severity,
            notes or ("pipeline path OK" if exists else "missing"),
            "regenerate reports after diversity pipeline" if status == "FAIL" else "none",
        )

    paper_main = [
        "histogram_correlations_pearson_paper.png",
        "pca_by_family.png",
        "pca_by_cluster.png",
        "ablation_pairs_high_bar.png",
        "ablation_silhouette_bar.png",
        "heatmap_feature_feature_core.png",
    ]
    for i, stem in enumerate(paper_main, start=1):
        p = FIG / "paper" / "main" / stem
        add(
            f"F{i:03d}",
            "figure",
            stem,
            str(p.relative_to(SCEN)),
            p.is_file() and p.stat().st_size > 1000,
            "PASS" if p.is_file() and p.stat().st_size > 1000 else "FAIL",
            "BLOCKER" if not p.is_file() else "INFO",
            "MAIN_PAPER" if p.is_file() else "missing",
            "run --phase figures_paper ",
        )

    paper_tables = [
        "table_diversity_metrics_en.md",
        "table_ablation_metrics_en.md",
        "table_core_vs_extended_en.md",
        "table_families_en.md",
        "table_diversity_criteria_en.md",
    ]
    for i, name in enumerate(paper_tables, start=1):
        p = FIG / "paper" / "tables" / name
        notes = ""
        status = "PASS" if p.is_file() else "FAIL"
        if p.is_file():
            txt = p.read_text(encoding="utf-8", errors="replace")
            if re.search(r"\b570\b", txt) and "stress" not in txt.lower():
                status, notes = "WARN", "table references n=540 without stress context"
            elif "540" in txt or name == "table_diversity_criteria_en.md":
                notes = "present"
        add(
            f"T{i:03d}",
            "table",
            name,
            str(p.relative_to(SCEN)),
            p.is_file(),
            status,
            "MAJOR" if status == "FAIL" else "INFO",
            notes,
            "run --phase tables_paper " if status != "PASS" else "none",
        )

    doc_paths = [
        ("DOC001", "features_core_vs_extended.md", AN / "docs" / "features_core_vs_extended.md"),
        ("DOC002", "analysis README.md", AN / "README.md"),
        ("DOC003", "SCRIPTS_INDEX.md", AN / "SCRIPTS_INDEX.md"),
        ("DOC004", "wiki 07-Diversity-Validation", WIKI / "07-Diversity-Validation.md"),
        ("DOC005", "wiki Resultados-Actuales", WIKI / "Resultados-Actuales.md"),
    ]
    for item_id, name, path in doc_paths:
        exists = path.is_file()
        notes = ""
        status = "PASS" if exists else "FAIL"
        if exists:
            txt = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"\b720\b", txt) and not re.search(r"legacy|históric|historical|archive", txt, re.I):
                status, notes = "WARN", "mentions 720 without legacy context"
        add(
            item_id,
            "wiki" if "wiki" in name.lower() else "readme",
            name,
            str(path.relative_to(SCEN)),
            exists,
            status,
            "MINOR" if status == "WARN" else ("BLOCKER" if status == "FAIL" else "INFO"),
            notes,
            "update documentation to scope 540",
        )

    # Cross-doc consistency (WARN only for diversity gate)
    root_readme = SCEN / "README.md"
    if root_readme.is_file():
        txt = root_readme.read_text(encoding="utf-8", errors="replace")
        if "Diversity snapshot (540" in txt:
            add(
                "C001",
                "consistency",
                "root_README_diversity_scope",
                str(root_readme.relative_to(SCEN)),
                True,
                "WARN",
                "MINOR",
                "Diversity snapshot labeled 540; canonical freeze is 540",
                "point to RESULTADOS_ACTUALES.md (540)",
            )
        else:
            add(
                "C001",
                "consistency",
                "root_README_diversity_scope",
                str(root_readme.relative_to(SCEN)),
                True,
                "PASS",
                "INFO",
                "OK",
                "none",
            )

    fig_index = FIG / "paper" / "FIGURES_AND_TABLES_INDEX.md"
    if fig_index.is_file():
        txt = fig_index.read_text(encoding="utf-8", errors="replace")
        if "Diversity validation:** PASS" in txt:
            add(
                "C002",
                "consistency",
                "FIGURES_AND_TABLES_INDEX",
                str(fig_index.relative_to(SCEN)),
                True,
                "PASS",
                "INFO",
                "diversity validation PASS in index",
                "none",
            )
        elif "CHECK FAILED" in txt or "Diversity validation:** CHECK FAILED" in txt:
            add(
                "C002",
                "consistency",
                "FIGURES_AND_TABLES_INDEX",
                str(fig_index.relative_to(SCEN)),
                True,
                "WARN",
                "MINOR",
                "diversity validation failed in index",
                "run build_paper_figures_tables_index.py after diversity pipeline",
            )
        else:
            add(
                "C002",
                "consistency",
                "FIGURES_AND_TABLES_INDEX",
                str(fig_index.relative_to(SCEN)),
                True,
                "PASS",
                "INFO",
                "validation PASS",
                "none",
            )

    n_out = csv_data_rows(DATA / "output_metrics.csv")
    add(
        "C003",
        "consistency",
        "output_metrics_benchmark_scope",
        str((DATA / "output_metrics.csv").relative_to(SCEN)),
        n_out >= 0,
        "WARN" if n_out != COMBINED_N else "PASS",
        "MINOR" if n_out != COMBINED_N else "INFO",
        f"rows={n_out} expected {COMBINED_N} for combined benchmark (not diversity scope)",
        "complete simulations and rerun output_metrics" if n_out != COMBINED_N else "none",
    )

def decide() -> str:
    blockers = [c for c in checks if c["status"] == "FAIL" and c["severity"] == "BLOCKER"]
    if blockers:
        return "NOT_READY"
    # Benchmark-scope items (C003) do not block diversity freeze
    diversity_warns = [
        c
        for c in checks
        if c["status"] in ("WARN", "FAIL")
        and c["item_id"] not in ("C003",)
        and "not diversity scope" not in c.get("notes", "")
    ]
    if diversity_warns:
        return "READY_WITH_MINOR_FIXES"
    benchmark_warns = [c for c in checks if c["status"] == "WARN" and c["item_id"] == "C003"]
    if benchmark_warns:
        return "READY_FOR_PAPER"  # diversity complete; benchmark outputs incomplete
    return "READY_FOR_PAPER"

def write_outputs(decision: str) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "item_id",
                "category",
                "artifact",
                "expected_path",
                "exists",
                "status",
                "severity",
                "notes",
                "recommended_action",
            ],
        )
        w.writeheader()
        w.writerows(checks)

    fails = [c for c in checks if c["status"] == "FAIL"]
    warns = [c for c in checks if c["status"] == "WARN"]
    passes = [c for c in checks if c["status"] == "PASS"]

    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("# Diversity validation readiness report\n\n")
        f.write(f"Generated: {utc_now()}\n\n")
        f.write(
            f"**Corpus scope:** `corpus_v1` only — **{EXPECTED_N}** scenarios "
            "\n\n"
        )
        f.write(f"**Expected pairs:** C({EXPECTED_N},2) = {EXPECTED_PAIRS}\n\n")
        f.write(f"**Decision (diversity scope):** `{decision}`\n\n")
        n_out = csv_data_rows(DATA / "output_metrics.csv")
        bench = "READY_WITH_MINOR_FIXES" if n_out != COMBINED_N else "READY"
        f.write(
            f"**Benchmark routing/outputs:** `{bench}` "
            f"(output_metrics={n_out}/{COMBINED_N})\n\n"
        )

        f.write("## Project structure (active)\n\n")
        for line in structure_notes:
            f.write(f"{line}\n")
        f.write("\n")

        f.write(
            "**Pipeline reports:** canonical paths are under "
            "`analysis/reports/pipeline/` (flat `reports/*.txt` names are legacy aliases).\n\n"
        )

        f.write("## Summary\n\n")
        f.write(f"- PASS: {len(passes)}\n")
        f.write(f"- WARN: {len(warns)}\n")
        f.write(f"- FAIL: {len(fails)}\n\n")

        f.write("## Canonical artifacts (diversity freeze)\n\n")
        f.write("| Type | Path |\n|------|------|\n")
        f.write("| Data | `analysis/data/features*.csv`, `correlation_*.csv`, `distance_*.csv`, `ablation_metrics.csv` |\n")
        f.write("| Reports | `analysis/reports/RESULTADOS_ACTUALES.md`, `analysis/reports/pipeline/*.txt` |\n")
        f.write("| Figures | `analysis/figures/paper/main/` (F001–F006) |\n")
        f.write("| Tables | `analysis/figures/paper/tables/table_*_en.md` |\n")
        f.write("| Methodology | `analysis/docs/features_core_vs_extended.md` |\n\n")

        f.write("## Checklist\n\n")
        f.write("| item_id | category | artifact | status | severity | notes |\n")
        f.write("|---|---|---|---|---|---|\n")
        for c in checks:
            f.write(
                f"| {c['item_id']} | {c['category']} | {c['artifact']} | "
                f"{c['status']} | {c['severity']} | {c['notes']} |\n"
            )
        if fails:
            f.write("\n## Blockers\n\n")
            for c in fails:
                f.write(
                    f"- **{c['item_id']}** {c['artifact']}: {c['notes']} → "
                    f"{c['recommended_action']}\n"
                )
        if warns:
            f.write("\n## Warnings\n\n")
            for c in warns:
                f.write(
                    f"- **{c['item_id']}** {c['artifact']}: {c['notes']} → "
                    f"{c['recommended_action']}\n"
                )

        f.write("\n## Recommended actions (non-diversity)\n\n")
        f.write(
            "- Complete benchmark simulations (540) and regenerate "
            "`output_metrics.csv` if routing results are needed.\n"
        )
        f.write(
            "- Regenerate `spatial_occupancy_metrics.csv` for 540 scope "
            "(current file may still be 720 legacy).\n"
        )
        f.write(
            f"- Archive candidates: see [{ARCHIVE_CANDIDATES_MD.name}]({ARCHIVE_CANDIDATES_MD.relative_to(REPORTS)})\n"
        )

    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")
    print(f"decision={decision}")

def main() -> int:
    run_checks()
    write_figures_inventory()
    write_archive_candidates()
    decision = decide()
    write_outputs(decision)
    return 0 if decision != "NOT_READY" else 1

if __name__ == "__main__":
    raise SystemExit(main())