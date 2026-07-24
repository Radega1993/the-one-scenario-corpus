"""Registry of builders and generators available to the planner."""

from __future__ import annotations

from typing import Any

# Imported lazily in functions to keep dry-run import light when generators unused.


BUILDERS = {
    "osm": "map_generation.builders.osm_builder",
    "synthetic": "map_generation.builders.synthetic_builder",
    "trace_reference_synthetic": "map_generation.builders.trace_builder",
}


def known_generator_ids() -> set[str]:
    from map_space_synthetic import GENERATORS

    return set(GENERATORS.keys())


def generator_spec_map(design_space: dict[str, Any]) -> dict[str, dict[str, Any]]:
    gens = (design_space.get("synthetic_generation_policy") or {}).get("generators") or []
    return {str(g["generator_id"]): g for g in gens}
