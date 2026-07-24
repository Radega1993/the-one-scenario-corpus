"""Provenance helpers for planned / built maps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from map_generation.models import PlannedCandidate


def provenance_for_candidate(cand: PlannedCandidate) -> dict[str, Any]:
    base: dict[str, Any] = {
        "map_id": cand.planned_map_id,
        "archetype": cand.archetype,
        "source_type": cand.source_type,
        "builder": cand.builder,
        "seed": cand.seed,
        "config_hash": cand.config_hash,
    }
    if cand.source_type == "osm":
        base.update(
            {
                "anchor_id": cand.anchor_id,
                "trace_support": list(cand.trace_support),
                "osm_query": {
                    "place": None,
                    "bbox": None,
                    "network_type": cand.network_type or "drive",
                    "window_size_m": cand.window_size_m,
                    "variant_type": cand.variant_type,
                    "offset_m": cand.offset_m,
                },
                "input_reference": cand.input_reference,
            }
        )
    elif cand.source_type == "trace_reference_synthetic":
        base.update(
            {
                "trace_id": cand.trace_id,
                "generator_type": cand.generator_type,
                "parameter_extractor": cand.parameter_extractor,
                "extracted_parameters": dict(cand.extracted_parameters),
                "generator_parameters": dict(cand.generator_parameters),
                "anchor_id": cand.anchor_id,
            }
        )
    else:
        base.update(
            {
                "generator_type": cand.generator_type,
                "generator_parameters": dict(cand.generator_parameters),
                "trace_id": "",
            }
        )
    return base


def write_provenance(path: Path, cand: PlannedCandidate) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(provenance_for_candidate(cand), indent=2, sort_keys=True) + "\n", encoding="utf-8")
