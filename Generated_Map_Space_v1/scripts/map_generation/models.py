"""Shared dataclasses for map generation v2."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class PlannedCandidate:
    planned_map_id: str
    archetype: str
    source_type: str
    anchor_id: str
    trace_id: str
    generator_type: str
    seed: int
    builder: str
    input_reference: str
    output_directory: str
    config_hash: str
    enabled: bool
    skip_reason: str = ""
    generator_parameters: dict[str, Any] = field(default_factory=dict)
    extracted_parameters: dict[str, Any] = field(default_factory=dict)
    parameter_extractor: str = ""
    trace_support: tuple[str, ...] = ()
    window_size_m: int = 0
    variant_type: str = ""
    offset_m: int = 0
    network_type: str = ""
    batch_target: int = 0

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["trace_support"] = ";".join(self.trace_support)
        row["generator_parameters"] = _compact_json(self.generator_parameters)
        row["extracted_parameters"] = _compact_json(self.extracted_parameters)
        return row


def _compact_json(obj: dict[str, Any]) -> str:
    import json

    if not obj:
        return ""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


@dataclass
class PlanValidationIssue:
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW | INFO
    code: str
    message: str


@dataclass
class GenerationPlan:
    candidates: list[PlannedCandidate]
    issues: list[PlanValidationIssue]
    config_hash: str
    seed: int

    @property
    def critical_errors(self) -> list[PlanValidationIssue]:
        return [i for i in self.issues if i.severity == "CRITICAL"]

    def counts_by(self, key: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for c in self.candidates:
            if not c.enabled:
                continue
            val = getattr(c, key)
            out[str(val)] = out.get(str(val), 0) + 1
        return dict(sorted(out.items()))
