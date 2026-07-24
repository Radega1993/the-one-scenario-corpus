"""Metadata validation for map generation v2."""

from __future__ import annotations

from typing import Any

from map_generation import CANONICAL_ARCHETYPES, SOURCE_TYPES


def validate_plan_metadata_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if row.get("archetype") not in CANONICAL_ARCHETYPES:
        errors.append(f"bad archetype: {row.get('archetype')}")
    if row.get("source_type") not in SOURCE_TYPES:
        errors.append(f"bad source_type: {row.get('source_type')}")
    if not row.get("planned_map_id"):
        errors.append("missing planned_map_id")
    if not row.get("config_hash"):
        errors.append("missing config_hash")
    return errors
