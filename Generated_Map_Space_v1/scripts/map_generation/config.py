"""Load and validate revised map-generation configuration."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from map_generation import CANONICAL_ARCHETYPES, SOURCE_TYPES


# __file__ = .../Generated_Map_Space_v1/scripts/map_generation/config.py
PACK_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
SCENARIOS_DIR = PACK_ROOT.parent
REPO_ROOT = SCENARIOS_DIR.parent
DEFAULT_REVISED_CONFIG = PACK_ROOT / "config" / "map_design_space.yaml"
DEFAULT_TRACE_POLICY = PACK_ROOT / "config" / "trace_to_map_generation_policy.yaml"
DEFAULT_INVENTORY = PACK_ROOT / "downloaded_external_traces" / "registry" / "real_trace_inventory_v1.csv"
DEFAULT_ARCHETYPE_SOURCE_ALLOCATION = PACK_ROOT / "config" / "archetype_source_allocation.yaml"


class ConfigError(ValueError):
    """Invalid map-generation configuration."""


def resolve_repo_path(path_str: str | Path) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    # Paths in config are relative to repo root (the-one/).
    return (REPO_ROOT / p).resolve()


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError(f"YAML root must be a mapping: {path}")
    return data


def config_hash(obj: Any) -> str:
    raw = yaml.dump(obj, sort_keys=True, allow_unicode=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def load_revised_design_space(path: Path | None = None) -> dict[str, Any]:
    path = path or DEFAULT_REVISED_CONFIG
    full = load_yaml(path)
    if "map_design_space_revised_v2" not in full:
        raise ConfigError(f"Expected key map_design_space_revised_v2 in {path}")
    ds = full["map_design_space_revised_v2"]
    validate_design_space(ds)
    return ds


def validate_design_space(ds: dict[str, Any]) -> None:
    arch = list(ds.get("base_archetypes") or [])
    if arch != list(CANONICAL_ARCHETYPES):
        missing = set(CANONICAL_ARCHETYPES) - set(arch)
        extra = set(arch) - set(CANONICAL_ARCHETYPES)
        raise ConfigError(
            f"base_archetypes must match the 15 canonical archetypes exactly. "
            f"missing={sorted(missing)} extra={sorted(extra)}"
        )
    allowed = list((ds.get("source_types") or {}).get("allowed") or [])
    if set(allowed) != set(SOURCE_TYPES):
        raise ConfigError(f"source_types.allowed must be {list(SOURCE_TYPES)}, got {allowed}")

    osm_anchors = ds.get("osm_anchors") or []
    if not osm_anchors:
        raise ConfigError("osm_anchors empty")
    ids = [a.get("anchor_id") for a in osm_anchors]
    if len(ids) != len(set(ids)):
        raise ConfigError("Duplicate osm anchor_id values")
    for a in osm_anchors:
        aid = a.get("anchor_id")
        at = a.get("anchor_type")
        if at not in ("osm_bbox", "osm_place"):
            raise ConfigError(f"OSM anchor {aid} has invalid anchor_type={at}")
        arch_id = a.get("archetype")
        if arch_id not in CANONICAL_ARCHETYPES:
            raise ConfigError(f"OSM anchor {aid} archetype {arch_id} not canonical")
        if not a.get("bbox"):
            raise ConfigError(f"OSM anchor {aid} missing bbox")

    gens = (ds.get("synthetic_generation_policy") or {}).get("generators") or []
    if len(gens) != 13:
        raise ConfigError(f"Expected 13 synthetic generators, got {len(gens)}")
    for g in gens:
        gid = g.get("generator_id")
        if g.get("archetype") not in CANONICAL_ARCHETYPES:
            raise ConfigError(f"Generator {gid} archetype not canonical: {g.get('archetype')}")

    paths = ds.get("paths") or {}
    for key in ("output_root", "plan_csv", "trace_inventory", "trace_policy"):
        if key not in paths:
            raise ConfigError(f"paths.{key} missing")


def load_trace_policy(path: Path | None = None) -> dict[str, Any]:
    path = path or DEFAULT_TRACE_POLICY
    full = load_yaml(path)
    if "trace_to_map_generation_policy_v1" not in full:
        raise ConfigError(f"Expected key trace_to_map_generation_policy_v1 in {path}")
    return full["trace_to_map_generation_policy_v1"]


def load_archetype_source_allocation(path: Path | None = None) -> dict[str, Any]:
    """Return mapping archetype -> {osm|synthetic|trace_reference_synthetic -> {role,min_candidates}}."""
    path = path or DEFAULT_ARCHETYPE_SOURCE_ALLOCATION
    full = load_yaml(path)
    archs = full.get("archetypes")
    if not isinstance(archs, dict):
        raise ConfigError(f"archetype_source_allocation missing archetypes: {path}")
    missing = set(CANONICAL_ARCHETYPES) - set(archs)
    extra = set(archs) - set(CANONICAL_ARCHETYPES)
    if missing or extra:
        raise ConfigError(
            f"allocation archetypes mismatch canonical set. missing={sorted(missing)} extra={sorted(extra)}"
        )
    out: dict[str, Any] = {}
    for arch, body in archs.items():
        entry: dict[str, Any] = {"rationale": body.get("rationale") or ""}
        for src in SOURCE_TYPES:
            spec = body.get(src)
            if not isinstance(spec, dict) or "role" not in spec:
                raise ConfigError(f"allocation {arch}.{src} requires role")
            role = str(spec["role"])
            if role not in ("primary", "supporting", "optional", "none"):
                raise ConfigError(f"allocation {arch}.{src} invalid role={role}")
            entry[src] = {
                "role": role,
                "min_candidates": int(spec.get("min_candidates") or 0),
            }
        out[str(arch)] = entry
    return out


def source_role(allocation: dict[str, Any], archetype: str, source_type: str) -> str:
    return str((allocation.get(archetype) or {}).get(source_type, {}).get("role") or "none")


def source_allowed(allocation: dict[str, Any], archetype: str, source_type: str) -> bool:
    return source_role(allocation, archetype, source_type) != "none"
