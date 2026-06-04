"""Canonical paths for scenario analysis scripts (repo-relative layout)."""

from __future__ import annotations

from pathlib import Path

# scenarios/analysis/
ANALYSIS_DIR = Path(__file__).resolve().parent.parent
# repo root (parent of scenarios/)
REPO_ROOT = ANALYSIS_DIR.parent.parent
SCENARIOS_DIR = ANALYSIS_DIR.parent

# Active paper benchmark layout
CORPUS_V1_DIR = SCENARIOS_DIR / "corpus_v1"
BASE_SCENARIOS_DIR = SCENARIOS_DIR / "base_scenarios"
LEGACY_CORPUS_V1_DIR = SCENARIOS_DIR / "_archive" / "legacy_corpus_v1_pre_rename"

DEFAULT_MANIFEST_V1 = CORPUS_V1_DIR / "manifest.csv"
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

def resolve_corpus_dirs(corpus: str) -> list[Path]:
    """Return physical directories for a logical corpus name (environmental benchmark only)."""
    c = corpus.strip()
    if c in PAPER_BENCHMARK_CORPORA:
        return [CORPUS_V1_DIR]
    if c == "base_scenarios":
        return [BASE_SCENARIOS_DIR]
    p = SCENARIOS_DIR / c
    return [p]

def primary_corpus_dir(corpus: str) -> Path:
    """Primary directory for --corpus (used in CLI messages)."""
    return resolve_corpus_dirs(corpus)[0]

def collect_settings_paths(corpus: str) -> list[Path]:
    """All .settings under the logical corpus (540 for corpus_v1)."""
    paths: list[Path] = []
    for d in resolve_corpus_dirs(corpus):
        if not d.is_dir():
            continue
        for sf in sorted(d.rglob("*.settings")):
            if any(p.startswith("_") or "backup" in p.lower() for p in sf.parts):
                continue
            paths.append(sf.resolve())
    return sorted(set(paths))

def build_combined_manifest_csv() -> Path:
    """Copy corpus_v1 manifest to combined manifest path (dashboard/tools alias)."""
    import csv
    import shutil

    if not DEFAULT_MANIFEST_V1.is_file():
        return COMBINED_MANIFEST_CSV
    COMBINED_MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DEFAULT_MANIFEST_V1, COMBINED_MANIFEST_CSV)
    return COMBINED_MANIFEST_CSV