"""Canonical paths for scenario analysis scripts (repo-relative layout)."""

from __future__ import annotations

from pathlib import Path

# scenarios/analysis/
ANALYSIS_DIR = Path(__file__).resolve().parent.parent
# repo root (parent of scenarios/)
REPO_ROOT = ANALYSIS_DIR.parent.parent
SCENARIOS_DIR = ANALYSIS_DIR.parent

CORPUS_V2 = SCENARIOS_DIR / "corpus_v2"
REPORTS_DIR = REPO_ROOT / "reports"
DATA_DIR = ANALYSIS_DIR / "data"
REPORTS_ANALYSIS_DIR = ANALYSIS_DIR / "reports"
DEFAULT_MANIFEST_V2 = CORPUS_V2 / "manifest.csv"


# Overlay presets (paths relative to REPO_ROOT)
_OVERLAYS = ANALYSIS_DIR / "overlays"
ROUTING_CONTACT_REPORTS_OVERLAY = _OVERLAYS / "routing_contact_reports_overrides.txt"
# Alias histórico (nombre anterior poco descriptivo)
DIEGO17_OVERLAY = ROUTING_CONTACT_REPORTS_OVERLAY
SPATIAL_OVERLAY = _OVERLAYS / "spatial_occupancy_reports_overrides.txt"
CREATED_MESSAGES_OVERLAY = _OVERLAYS / "created_messages_report_overrides.txt"
SELECTION_EXAMPLE = ANALYSIS_DIR / "examples" / "selection_example.txt"
