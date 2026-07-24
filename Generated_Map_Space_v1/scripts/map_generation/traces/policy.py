"""Trace generation policy helpers."""

from __future__ import annotations

from typing import Any

from map_generation import GENERATION_ROLES
from map_generation.config import ConfigError, load_trace_policy


def policy_by_trace(policy: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    pol = policy or load_trace_policy()
    out: dict[str, dict[str, Any]] = {}
    for entry in pol.get("traces") or []:
        tid = entry.get("trace_id")
        if not tid:
            raise ConfigError("trace policy entry missing trace_id")
        role = entry.get("generation_role")
        if role not in GENERATION_ROLES:
            raise ConfigError(f"Unknown generation_role for {tid}: {role}")
        out[str(tid)] = entry
    return out


def enabled_entries(policy_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [e for e in policy_map.values() if bool(e.get("enabled"))]


def role_is_generative(role: str) -> bool:
    return role in ("parameterize_generator", "trace_reference_synthetic", "direct_trace_geometry")


def validate_policy_against_inventory(
    policy_map: dict[str, dict[str, Any]],
    inventory: dict[str, dict[str, str]],
    *,
    generator_ids: set[str],
    osm_anchor_ids: set[str],
    archetypes: set[str],
) -> list[str]:
    errors: list[str] = []
    for tid, entry in policy_map.items():
        if tid not in inventory:
            errors.append(f"policy trace_id not in inventory: {tid}")
            continue
        if not entry.get("enabled"):
            continue
        role = entry.get("generation_role")
        if role in ("evidence_only", "unsupported_for_generation", "future_candidate"):
            errors.append(f"enabled trace {tid} has non-generative role {role}")
        for arch in entry.get("target_archetypes") or []:
            if arch not in archetypes:
                errors.append(f"trace {tid} unknown archetype {arch}")
        for gid in entry.get("target_generators") or []:
            if gid and gid not in generator_ids:
                errors.append(f"trace {tid} unknown generator {gid}")
        for aid in entry.get("target_osm_anchors") or []:
            if aid and aid not in osm_anchor_ids:
                errors.append(f"trace {tid} unknown osm anchor {aid}")
        extractor = entry.get("parameter_extractor") or ""
        if role == "parameterize_generator" and not extractor:
            errors.append(f"enabled parameterize trace {tid} missing parameter_extractor")
        if extractor == "static_parameters_v1" and not entry.get("static_parameters"):
            errors.append(f"trace {tid} static_parameters_v1 missing static_parameters")
        if extractor == "standard_events_contact_summary_v1" and not entry.get("events_path"):
            errors.append(f"trace {tid} missing events_path")
        if (
            entry.get("enabled")
            and extractor == "gps_trace_summary_v1"
            and not entry.get("gps_columns")
        ):
            errors.append(f"enabled GPS extractor for {tid} requires gps_columns configuration")
    missing_policy = set(inventory) - set(policy_map)
    for tid in sorted(missing_policy):
        errors.append(f"inventory trace missing from policy: {tid}")
    return errors
