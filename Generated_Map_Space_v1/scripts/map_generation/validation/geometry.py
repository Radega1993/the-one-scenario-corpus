"""Geometry / metadata validation helpers (lightweight)."""

from __future__ import annotations

from typing import Any


def validate_provenance_dict(prov: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("map_id", "archetype", "source_type", "builder", "seed", "config_hash"):
        if key not in prov:
            errors.append(f"missing provenance field: {key}")
    st = prov.get("source_type")
    if st == "trace_reference_synthetic":
        for key in ("trace_id", "generator_type", "parameter_extractor"):
            if not prov.get(key):
                errors.append(f"trace_reference_synthetic missing {key}")
    if st == "synthetic" and prov.get("trace_id"):
        errors.append("pure synthetic provenance must not include trace_id")
    if st == "osm" and not prov.get("anchor_id"):
        errors.append("osm provenance missing anchor_id")
    return errors


def edges_look_valid(edges: list[tuple[tuple[float, float], tuple[float, float]]], *, min_edges: int = 20) -> tuple[bool, str]:
    if len(edges) < min_edges:
        return False, f"too_few_edges:{len(edges)}"
    nodes = set()
    for a, b in edges:
        if a == b:
            return False, "degenerate_segment"
        nodes.add(a)
        nodes.add(b)
    if len(nodes) < 20:
        return False, f"too_few_nodes:{len(nodes)}"
    return True, "ok"
