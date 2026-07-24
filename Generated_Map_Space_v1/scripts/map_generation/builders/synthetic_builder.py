"""Synthetic builder facade for revised v2."""

from __future__ import annotations

import random
from typing import Any

from map_generation.models import PlannedCandidate
from map_generation.provenance import provenance_for_candidate
from map_generation.validation.geometry import edges_look_valid


def build_synthetic_candidate(
    cand: PlannedCandidate,
    *,
    dry_run: bool = True,
    write_wkt: bool = False,
) -> dict[str, Any]:
    from map_space_synthetic import GENERATORS

    prov = provenance_for_candidate(cand)
    if cand.trace_id:
        raise ValueError("pure synthetic builder received trace_id; use trace_builder")
    gen = GENERATORS.get(cand.generator_type)
    if gen is None:
        raise KeyError(f"Unknown generator_type: {cand.generator_type}")
    if dry_run and not write_wkt:
        # Still exercise generator once for smoke validity when explicitly requested in tests
        # via write_wkt=False dry_run: skip generation for speed.
        prov["status"] = "dry_run_no_wkt"
        return prov

    rng = random.Random(int(cand.seed))
    edges, meta = gen(dict(cand.generator_parameters), rng)
    ok, reason = edges_look_valid(edges)
    prov["generator_meta"] = meta
    prov["validation"] = {"ok": ok, "reason": reason}
    prov["n_edges"] = len(edges)
    if not ok:
        raise RuntimeError(f"synthetic geometry invalid: {reason}")
    return prov


def smoke_generate(generator_type: str, params: dict[str, Any], seed: int) -> tuple[bool, str, int]:
    from map_space_synthetic import GENERATORS

    gen = GENERATORS[generator_type]
    edges, _ = gen(params, random.Random(seed))
    ok, reason = edges_look_valid(edges)
    return ok, reason, len(edges)
