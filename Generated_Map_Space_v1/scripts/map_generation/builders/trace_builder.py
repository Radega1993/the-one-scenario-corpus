"""Trace-parameterized synthetic builder (trace_reference_synthetic)."""

from __future__ import annotations

import random
from typing import Any

from map_generation.models import PlannedCandidate
from map_generation.provenance import provenance_for_candidate
from map_generation.traces.extractors import extract_for_entry, map_extracted_to_generator_params
from map_generation.validation.geometry import edges_look_valid


def build_trace_reference_candidate(
    cand: PlannedCandidate,
    *,
    policy_entry: dict[str, Any],
    generator_spec: dict[str, Any],
    dry_run: bool = True,
    materialize_geometry: bool = False,
) -> dict[str, Any]:
    if not cand.trace_id:
        raise ValueError("trace_reference_synthetic requires trace_id")
    extracted = dict(cand.extracted_parameters) if cand.extracted_parameters else extract_for_entry(policy_entry, dry_run=dry_run)
    params = dict(cand.generator_parameters) or map_extracted_to_generator_params(
        cand.generator_type, extracted, generator_spec
    )
    prov = provenance_for_candidate(cand)
    prov["extracted_parameters"] = extracted
    prov["generator_parameters"] = params
    # Never copy raw payloads into outputs.
    prov["raw_trace_copied"] = False

    if dry_run and not materialize_geometry:
        prov["status"] = "dry_run_no_wkt"
        return prov

    from map_space_synthetic import GENERATORS

    gen = GENERATORS[cand.generator_type]
    edges, meta = gen(params, random.Random(int(cand.seed)))
    ok, reason = edges_look_valid(edges)
    prov["generator_meta"] = meta
    prov["validation"] = {"ok": ok, "reason": reason}
    if not ok:
        raise RuntimeError(f"trace_reference geometry invalid: {reason}")
    return prov
