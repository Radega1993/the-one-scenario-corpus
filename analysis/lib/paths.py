"""Canonical paths for scenario analysis scripts (repo-relative layout)."""

from __future__ import annotations

from pathlib import Path

# scenarios/analysis/
ANALYSIS_DIR = Path(__file__).resolve().parent.parent
# repo root (parent of scenarios/)
REPO_ROOT = ANALYSIS_DIR.parent.parent
SCENARIOS_DIR = ANALYSIS_DIR.parent

# Active paper benchmark layout (post-rename)
CORPUS_V1_DIR = SCENARIOS_DIR / "corpus_v1"
STRESS_CONTROLS_DIR = SCENARIOS_DIR / "stress_controls"
# Stress scenarios now live flat under stress_controls/ (no subfolder)
STRESS_CONTROLS_FAMILY_DIR = STRESS_CONTROLS_DIR
BASE_SCENARIOS_DIR = SCENARIOS_DIR / "base_scenarios"
LEGACY_CORPUS_V1_DIR = SCENARIOS_DIR / "_archive" / "legacy_corpus_v1_pre_rename"

DEFAULT_MANIFEST_V1 = CORPUS_V1_DIR / "manifest.csv"
STRESS_MANIFEST = STRESS_CONTROLS_DIR / "manifest.csv"
COMBINED_MANIFEST_CSV = ANALYSIS_DIR / "data" / "corpus_v1_combined_manifest.csv"

REPORTS_DIR = REPO_ROOT / "reports"
DATA_DIR = ANALYSIS_DIR / "data"
REPORTS_ANALYSIS_DIR = ANALYSIS_DIR / "reports"

# Legacy alias (old name for active paper benchmark)
CORPUS_V2 = CORPUS_V1_DIR
DEFAULT_MANIFEST_V2 = COMBINED_MANIFEST_CSV

# Overlay presets (paths relative to REPO_ROOT)
_OVERLAYS = ANALYSIS_DIR / "overlays"
ROUTING_CONTACT_REPORTS_OVERLAY = _OVERLAYS / "routing_contact_reports_overrides.txt"
DIEGO17_OVERLAY = ROUTING_CONTACT_REPORTS_OVERLAY
SPATIAL_OVERLAY = _OVERLAYS / "spatial_occupancy_reports_overrides.txt"
CREATED_MESSAGES_OVERLAY = _OVERLAYS / "created_messages_report_overrides.txt"
SELECTION_EXAMPLE = ANALYSIS_DIR / "examples" / "selection_example.txt"

PAPER_BENCHMARK_CORPORA = ("corpus_v1", "corpus_v2")  # corpus_v2 kept as CLI alias


def resolve_corpus_dirs(corpus: str, *, include_stress: bool = False) -> list[Path]:
    """Return physical directories for a logical corpus name.

    For ``corpus_v1``: environmental benchmark only (540). Stress/control lives in
    ``stress_controls/`` — use ``--corpus stress_controls`` or ``include_stress=True``
    (analysis / combined manifest) to include those 30 scenarios.
    """
    c = corpus.strip()
    if c in PAPER_BENCHMARK_CORPORA:
        dirs = [CORPUS_V1_DIR]
        if include_stress and STRESS_CONTROLS_FAMILY_DIR.is_dir():
            dirs.append(STRESS_CONTROLS_FAMILY_DIR)
        return dirs
    if c == "base_scenarios":
        return [BASE_SCENARIOS_DIR]
    if c in ("stress_controls", "07_stress_controls"):
        return [STRESS_CONTROLS_FAMILY_DIR]
    p = SCENARIOS_DIR / c
    return [p]


def primary_corpus_dir(corpus: str) -> Path:
    """Primary directory for --corpus (used in CLI messages)."""
    return resolve_corpus_dirs(corpus, include_stress=False)[0]


def collect_settings_paths(corpus: str, *, include_stress: bool = False) -> list[Path]:
    """All .settings under the logical corpus.

    Simulation default for ``corpus_v1``: 540 environmental (no stress_controls).
    Pass ``include_stress=True`` for the full paper set (570) in analysis/validation.
    """
    paths: list[Path] = []
    for d in resolve_corpus_dirs(corpus, include_stress=include_stress):
        if not d.is_dir():
            continue
        # Skip backup folders inside corpora
        for sf in sorted(d.rglob("*.settings")):
            if any(p.startswith("_") or "backup" in p.lower() for p in sf.parts):
                continue
            paths.append(sf.resolve())
    return sorted(set(paths))


def build_combined_manifest_csv() -> Path:
    """Merge corpus_v1 + stress_controls manifests into one CSV for dashboard/tools."""
    import csv

    rows: list[dict] = []
    for manifest in (DEFAULT_MANIFEST_V1, STRESS_MANIFEST):
        if not manifest.is_file():
            continue
        with manifest.open(newline="", encoding="utf-8") as f:
            rows.extend(csv.DictReader(f))
    COMBINED_MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return COMBINED_MANIFEST_CSV
    with COMBINED_MANIFEST_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return COMBINED_MANIFEST_CSV
