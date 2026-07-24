"""Deterministic planner / dry-run for map generation revised v2."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from map_generation import CANONICAL_ARCHETYPES, SOURCE_TYPES
from map_generation.config import (
    config_hash,
    load_archetype_source_allocation,
    load_revised_design_space,
    load_trace_policy,
    resolve_repo_path,
    source_allowed,
    source_role,
)
from map_generation.models import GenerationPlan, PlannedCandidate, PlanValidationIssue
from map_generation.provenance import provenance_for_candidate
from map_generation.registry import generator_spec_map, known_generator_ids
from map_generation.traces.extractors import ExtractorError, extract_for_entry_cached, map_extracted_to_generator_params
from map_generation.traces.inventory import load_inventory
from map_generation.traces.policy import policy_by_trace, validate_policy_against_inventory


PLAN_COLUMNS = [
    "planned_map_id",
    "archetype",
    "source_type",
    "anchor_id",
    "trace_id",
    "generator_type",
    "seed",
    "builder",
    "input_reference",
    "output_directory",
    "config_hash",
    "enabled",
    "skip_reason",
    "generator_parameters",
    "extracted_parameters",
    "parameter_extractor",
    "trace_support",
    "window_size_m",
    "variant_type",
    "offset_m",
    "network_type",
    "batch_target",
]


def stable_seed(global_seed: int, *parts: str) -> int:
    raw = "::".join([str(global_seed), *map(str, parts)]).encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:8], 16)


def candidate_seed(
    global_seed: int,
    *,
    map_id: str,
    archetype: str,
    source_type: str,
    trace_id: str = "",
    generator_type: str = "",
) -> int:
    """SHA256(global_seed::map_id::archetype::source_type::trace_id::generator_type)[:8]."""
    return stable_seed(
        global_seed,
        map_id,
        archetype,
        source_type,
        trace_id or "",
        generator_type or "",
    )


def _stage_target(idx: int, batch_targets: list[int]) -> int:
    for bt in batch_targets:
        if idx < bt:
            return bt
    return batch_targets[-1] if batch_targets else 0


def _anchor_center(anchor: dict[str, Any]) -> tuple[float, float]:
    bbox = anchor.get("bbox") or {}
    lat = (float(bbox["south"]) + float(bbox["north"])) / 2.0
    lon = (float(bbox["west"]) + float(bbox["east"])) / 2.0
    return lat, lon


def _apply_offset(lat: float, lon: float, variant: str, offset_m: int) -> tuple[float, float]:
    if offset_m <= 0 or variant == "exact":
        return lat, lon
    dlat = offset_m / 111_320.0
    dlon = offset_m / (111_320.0 * max(0.2, abs(__import__("math").cos(__import__("math").radians(lat)))))
    if variant == "offset_n":
        return lat + dlat, lon
    if variant == "offset_s":
        return lat - dlat, lon
    if variant == "offset_e":
        return lat, lon + dlon
    if variant == "offset_w":
        return lat, lon - dlon
    return lat, lon


def _pick_discrete(spec: dict[str, Any], index: int) -> dict[str, Any]:
    params: dict[str, Any] = {}
    discrete = spec.get("parameters") or {}
    for key, values in discrete.items():
        if isinstance(values, list) and values:
            params[key] = values[index % len(values)]
    return params


def build_plan(
    *,
    design_space: dict[str, Any] | None = None,
    design_space_path: Path | None = None,
    global_seed: int | None = None,
    target_total: int | None = None,
) -> GenerationPlan:
    ds = design_space or load_revised_design_space(design_space_path)
    ch = config_hash(ds)
    seed = int(global_seed if global_seed is not None else (ds.get("seed_policy") or {}).get("global_seed_default", 42))
    planning = ds.get("planning") or {}
    target = int(target_total if target_total is not None else planning.get("target_total_default", 1200))
    batch_targets = [int(x) for x in planning.get("batch_targets") or [100, 200, 400, 600, 800, 1000, 1200]]
    osm_frac = float(planning.get("osm_fraction", 0.45))
    syn_frac = float(planning.get("synthetic_fraction", 0.40))
    trs_frac = float(planning.get("trace_reference_fraction", 0.15))
    output_root = resolve_repo_path((ds.get("paths") or {}).get("output_root", "scenarios/Generated_Map_Space_v1"))
    osm_policy = ds.get("osm_generation_policy") or {}
    windows = [int(x) for x in osm_policy.get("window_sizes_m") or [500, 1000, 1500, 2500]]
    offsets = [int(x) for x in osm_policy.get("offset_distances_m") or [0, 200, 500, 1000]]
    variants = list(osm_policy.get("variant_types") or ["exact", "offset_n", "offset_e", "offset_s", "offset_w"])

    inventory = load_inventory(resolve_repo_path((ds.get("paths") or {})["trace_inventory"]))
    policy_raw = load_trace_policy(resolve_repo_path((ds.get("paths") or {})["trace_policy"]))
    policy_map = policy_by_trace(policy_raw)

    alloc_path = (ds.get("paths") or {}).get("archetype_source_allocation")
    allocation = load_archetype_source_allocation(
        resolve_repo_path(alloc_path) if alloc_path else None
    )

    osm_anchors = sorted(list(ds.get("osm_anchors") or []), key=lambda x: str(x["anchor_id"]))
    osm_by_id = {str(a["anchor_id"]): a for a in osm_anchors}
    osm_anchors_allowed = [
        a for a in osm_anchors if source_allowed(allocation, str(a["archetype"]), "osm")
    ]
    gen_specs = generator_spec_map(ds)
    gen_ids = set(gen_specs)
    known = known_generator_ids()
    gen_list = sorted(gen_specs.values(), key=lambda g: str(g["generator_id"]))
    gen_list_syn = [
        g for g in gen_list if source_allowed(allocation, str(g["archetype"]), "synthetic")
    ]

    issues: list[PlanValidationIssue] = []

    for arch in CANONICAL_ARCHETYPES:
        roles = {src: source_role(allocation, arch, src) for src in SOURCE_TYPES}
        if all(r == "none" for r in roles.values()):
            issues.append(
                PlanValidationIssue(
                    "CRITICAL",
                    "allocation_empty",
                    f"Archetype {arch} forbids all source types",
                )
            )

    for gid in gen_ids:
        if gid not in known:
            issues.append(PlanValidationIssue("CRITICAL", "unknown_generator", f"Configured generator not implemented: {gid}"))

    pol_errors = validate_policy_against_inventory(
        policy_map,
        inventory,
        generator_ids=gen_ids,
        osm_anchor_ids=set(osm_by_id),
        archetypes=set(CANONICAL_ARCHETYPES),
    )
    for msg in pol_errors:
        issues.append(PlanValidationIssue("CRITICAL", "policy_validation", msg))

    support: dict[str, list[str]] = defaultdict(list)
    extracted_cache: dict[str, dict[str, Any]] = {}

    for tid, entry in policy_map.items():
        if not entry.get("enabled"):
            continue
        role = entry.get("generation_role")
        if role == "osm_anchor_support":
            for aid in entry.get("target_osm_anchors") or []:
                support[str(aid)].append(tid)
            # Validate GPS / metadata extractors when present
            try:
                if entry.get("parameter_extractor") not in (None, "", "metadata_only_v1"):
                    extract_for_entry_cached(entry, dry_run=True)
            except ExtractorError as exc:
                issues.append(PlanValidationIssue("CRITICAL", "extractor_failed", f"{tid}: {exc}"))
        if role == "parameterize_generator":
            try:
                extracted_cache[tid] = extract_for_entry_cached(entry, dry_run=True)
            except ExtractorError as exc:
                issues.append(PlanValidationIssue("CRITICAL", "extractor_failed", f"{tid}: {exc}"))

    n_osm = int(round(target * osm_frac))
    n_trs = int(round(target * trs_frac))
    n_syn = max(0, target - n_osm - n_trs)

    candidates: list[PlannedCandidate] = []

    def _out_dir(idx: int, map_id: str) -> str:
        return str(output_root / f"batch_{_stage_target(idx, batch_targets):04d}" / "wkt" / map_id)

    def add(c: PlannedCandidate) -> None:
        candidates.append(c)

    # --- Minimum coverage seed (matrix-respecting) ---
    if planning.get("ensure_minimum_coverage", True):
        for a in osm_anchors_allowed:
            aid = str(a["anchor_id"])
            arch = str(a["archetype"])
            window = windows[0]
            map_id = f"v2_osm_{aid}_exact_{window}m_0m_seed"
            lat, lon = _anchor_center(a)
            idx = len(candidates)
            params = {
                "center_lat": round(lat, 6),
                "center_lon": round(lon, 6),
                "width_m": window,
                "height_m": window,
                "variant_type": "exact",
                "anchor_distance_m": 0.0,
                "window_size_m": float(window),
                "osm_network_type": str(a.get("network_type") or "drive"),
                "crs": a.get("crs"),
                "anchor_label": a.get("label"),
                "_allow_partitioned": bool((a.get("expected_topology") or {}).get("n_components_min", 0) >= 2),
            }
            add(
                PlannedCandidate(
                    planned_map_id=map_id,
                    archetype=arch,
                    source_type="osm",
                    anchor_id=aid,
                    trace_id="",
                    generator_type="",
                    seed=candidate_seed(
                        seed,
                        map_id=map_id,
                        archetype=arch,
                        source_type="osm",
                        trace_id="",
                        generator_type="",
                    ),
                    builder="osm",
                    input_reference=f"osm_anchor:{aid}",
                    output_directory=_out_dir(idx, map_id),
                    config_hash=ch,
                    enabled=True,
                    generator_parameters=params,
                    trace_support=tuple(support.get(aid, [])),
                    window_size_m=window,
                    variant_type="exact",
                    offset_m=0,
                    network_type=str(a.get("network_type") or "drive"),
                    batch_target=_stage_target(idx, batch_targets),
                )
            )
        for gspec in gen_list_syn:
            gid = str(gspec["generator_id"])
            arch = str(gspec["archetype"])
            params = _pick_discrete(gspec, 0)
            map_id = f"v2_syn_{gid}_seed"
            idx = len(candidates)
            add(
                PlannedCandidate(
                    planned_map_id=map_id,
                    archetype=arch,
                    source_type="synthetic",
                    anchor_id="",
                    trace_id="",
                    generator_type=gid,
                    seed=candidate_seed(
                        seed,
                        map_id=map_id,
                        archetype=arch,
                        source_type="synthetic",
                        trace_id="",
                        generator_type=gid,
                    ),
                    builder="synthetic",
                    input_reference=f"generator:{gid}",
                    output_directory=_out_dir(idx, map_id),
                    config_hash=ch,
                    enabled=True,
                    generator_parameters=params,
                    batch_target=_stage_target(idx, batch_targets),
                )
            )
        for tid, entry in sorted(policy_map.items()):
            if not entry.get("enabled") or entry.get("generation_role") != "parameterize_generator":
                continue
            if tid not in extracted_cache:
                continue
            for i, gid in enumerate(entry.get("target_generators") or []):
                if gid not in gen_specs:
                    continue
                archs = list(entry.get("target_archetypes") or [])
                arch = str(archs[i] if i < len(archs) else gen_specs[gid]["archetype"])
                if not source_allowed(allocation, arch, "trace_reference_synthetic"):
                    continue
                extracted = extracted_cache[tid]
                params = map_extracted_to_generator_params(gid, extracted, gen_specs[gid])
                map_id = f"v2_trs_{tid}_{gid}_seed"
                idx = len(candidates)
                add(
                    PlannedCandidate(
                        planned_map_id=map_id,
                        archetype=arch,
                        source_type="trace_reference_synthetic",
                        anchor_id=";".join(entry.get("target_osm_anchors") or []) or "",
                        trace_id=tid,
                        generator_type=gid,
                        seed=candidate_seed(
                            seed,
                            map_id=map_id,
                            archetype=arch,
                            source_type="trace_reference_synthetic",
                            trace_id=tid,
                            generator_type=gid,
                        ),
                        builder="trace_reference_synthetic",
                        input_reference=f"trace:{tid}|extractor:{entry.get('parameter_extractor')}",
                        output_directory=_out_dir(idx, map_id),
                        config_hash=ch,
                        enabled=True,
                        generator_parameters=params,
                        extracted_parameters=extracted,
                        parameter_extractor=str(entry.get("parameter_extractor") or ""),
                        batch_target=_stage_target(idx, batch_targets),
                    )
                )

    # Soft engineering quotas (fractions); matrix forbids none-role combinations.
    n_osm_have = sum(1 for c in candidates if c.source_type == "osm")
    n_syn_have = sum(1 for c in candidates if c.source_type == "synthetic")
    n_trs_have = sum(1 for c in candidates if c.source_type == "trace_reference_synthetic")
    n_osm = max(n_osm, n_osm_have)
    n_syn = max(n_syn, n_syn_have)
    n_trs = max(n_trs, n_trs_have)
    remaining = max(0, target - len(candidates))
    if remaining > 0:
        extra_osm = int(round(remaining * osm_frac))
        extra_trs = int(round(remaining * trs_frac))
        extra_syn = remaining - extra_osm - extra_trs
        n_osm = n_osm_have + extra_osm
        n_trs = n_trs_have + extra_trs
        n_syn = n_syn_have + extra_syn
    # If a soft quota cannot be filled under the matrix, redistribute leftovers.
    if not osm_anchors_allowed and n_osm > n_osm_have:
        spill = n_osm - n_osm_have
        n_osm = n_osm_have
        n_syn += spill
        issues.append(
            PlanValidationIssue(
                "HIGH",
                "soft_quota_redistributed",
                f"OSM soft quota reduced by {spill}; redistributed to synthetic (matrix)",
            )
        )
    if not gen_list_syn and n_syn > n_syn_have:
        spill = n_syn - n_syn_have
        n_syn = n_syn_have
        n_osm += spill
        issues.append(
            PlanValidationIssue(
                "HIGH",
                "soft_quota_redistributed",
                f"Synthetic soft quota reduced by {spill}; redistributed to OSM (matrix)",
            )
        )

    # --- OSM fill ---
    osm_i = 0
    while osm_anchors_allowed and len([c for c in candidates if c.source_type == "osm"]) < n_osm:
        a = osm_anchors_allowed[osm_i % len(osm_anchors_allowed)]
        aid = str(a["anchor_id"])
        arch = str(a["archetype"])
        window = windows[osm_i % len(windows)]
        variant = variants[osm_i % len(variants)]
        off = 0 if variant == "exact" else offsets_nonzero(offsets)[osm_i % max(1, len(offsets_nonzero(offsets)))]
        lat0, lon0 = _anchor_center(a)
        lat, lon = _apply_offset(lat0, lon0, variant, off)
        map_id = f"v2_osm_{aid}_{variant}_{window}m_{off}m_{osm_i:04d}"
        idx = len(candidates)
        params = {
            "center_lat": round(lat, 6),
            "center_lon": round(lon, 6),
            "width_m": window,
            "height_m": window,
            "variant_type": variant,
            "anchor_distance_m": float(off),
            "window_size_m": float(window),
            "osm_network_type": str(a.get("network_type") or "drive"),
            "crs": a.get("crs"),
            "anchor_label": a.get("label"),
            "_allow_partitioned": bool((a.get("expected_topology") or {}).get("n_components_min", 0) >= 2),
        }
        add(
            PlannedCandidate(
                planned_map_id=map_id,
                archetype=arch,
                source_type="osm",
                anchor_id=aid,
                trace_id="",
                generator_type="",
                seed=candidate_seed(
                    seed,
                    map_id=map_id,
                    archetype=arch,
                    source_type="osm",
                    trace_id="",
                    generator_type="",
                ),
                builder="osm",
                input_reference=f"osm_anchor:{aid}",
                output_directory=_out_dir(idx, map_id),
                config_hash=ch,
                enabled=True,
                generator_parameters=params,
                trace_support=tuple(support.get(aid, [])),
                window_size_m=window,
                variant_type=variant,
                offset_m=off,
                network_type=str(a.get("network_type") or "drive"),
                batch_target=_stage_target(idx, batch_targets),
            )
        )
        osm_i += 1

    # --- TRS fill ---
    trs_entries: list[tuple[str, dict[str, Any], str, str]] = []
    for tid, entry in sorted(policy_map.items()):
        if not entry.get("enabled") or entry.get("generation_role") != "parameterize_generator":
            continue
        if tid not in extracted_cache:
            continue
        gens = list(entry.get("target_generators") or [])
        archs = list(entry.get("target_archetypes") or [])
        for i, gid in enumerate(gens):
            if gid not in gen_specs:
                continue
            arch = str(archs[i] if i < len(archs) else gen_specs[gid]["archetype"])
            if not source_allowed(allocation, arch, "trace_reference_synthetic"):
                continue
            trs_entries.append((tid, entry, gid, arch))
    if not trs_entries and n_trs > 0:
        issues.append(PlanValidationIssue("CRITICAL", "trs_empty", "No trace_reference_synthetic candidates available"))
    trs_i = 0
    while trs_entries and len([c for c in candidates if c.source_type == "trace_reference_synthetic"]) < n_trs:
        tid, entry, gid, arch = trs_entries[trs_i % len(trs_entries)]
        extracted = extracted_cache[tid]
        gspec = gen_specs[gid]
        base = _pick_discrete(gspec, trs_i)
        overlay = map_extracted_to_generator_params(gid, extracted, gspec)
        params = {**base, **{k: overlay[k] for k in overlay if k in (gspec.get("parameters") or {}) or k in base}}
        map_id = f"v2_trs_{tid}_{gid}_{trs_i:04d}"
        idx = len(candidates)
        add(
            PlannedCandidate(
                planned_map_id=map_id,
                archetype=arch,
                source_type="trace_reference_synthetic",
                anchor_id=";".join(entry.get("target_osm_anchors") or []) or "",
                trace_id=tid,
                generator_type=gid,
                seed=candidate_seed(
                    seed,
                    map_id=map_id,
                    archetype=arch,
                    source_type="trace_reference_synthetic",
                    trace_id=tid,
                    generator_type=gid,
                ),
                builder="trace_reference_synthetic",
                input_reference=f"trace:{tid}|extractor:{entry.get('parameter_extractor')}",
                output_directory=_out_dir(idx, map_id),
                config_hash=ch,
                enabled=True,
                generator_parameters=params,
                extracted_parameters=extracted,
                parameter_extractor=str(entry.get("parameter_extractor") or ""),
                batch_target=_stage_target(idx, batch_targets),
            )
        )
        trs_i += 1

    # --- Synthetic fill ---
    syn_i = 0
    while gen_list_syn and len([c for c in candidates if c.source_type == "synthetic"]) < n_syn:
        gspec = gen_list_syn[syn_i % len(gen_list_syn)]
        gid = str(gspec["generator_id"])
        arch = str(gspec["archetype"])
        params = _pick_discrete(gspec, syn_i)
        map_id = f"v2_syn_{gid}_{syn_i:04d}"
        idx = len(candidates)
        add(
            PlannedCandidate(
                planned_map_id=map_id,
                archetype=arch,
                source_type="synthetic",
                anchor_id="",
                trace_id="",
                generator_type=gid,
                seed=candidate_seed(
                    seed,
                    map_id=map_id,
                    archetype=arch,
                    source_type="synthetic",
                    trace_id="",
                    generator_type=gid,
                ),
                builder="synthetic",
                input_reference=f"generator:{gid}",
                output_directory=_out_dir(idx, map_id),
                config_hash=ch,
                enabled=True,
                generator_parameters=params,
                batch_target=_stage_target(idx, batch_targets),
            )
        )
        syn_i += 1

    # Trim / pad to exact target while preserving archetype + source_type coverage
    if len(candidates) > target:
        kept: list[PlannedCandidate] = []
        seen_arch: set[str] = set()
        seen_src: set[str] = set()
        for c in candidates:
            need = c.archetype not in seen_arch or c.source_type not in seen_src
            if need:
                kept.append(c)
                seen_arch.add(c.archetype)
                seen_src.add(c.source_type)
            if len(kept) >= target and seen_arch >= set(CANONICAL_ARCHETYPES) and seen_src >= set(SOURCE_TYPES):
                break
        kept_ids = {c.planned_map_id for c in kept}
        for c in candidates:
            if len(kept) >= target:
                break
            if c.planned_map_id not in kept_ids:
                kept.append(c)
                kept_ids.add(c.planned_map_id)
        candidates = kept[:target]
    elif len(candidates) < target:
        syn_i = 0
        pad_pool = gen_list_syn or gen_list
        while len(candidates) < target and pad_pool:
            gspec = pad_pool[syn_i % len(pad_pool)]
            gid = str(gspec["generator_id"])
            arch = str(gspec["archetype"])
            if not source_allowed(allocation, arch, "synthetic"):
                syn_i += 1
                if syn_i > len(pad_pool) * 3:
                    break
                continue
            map_id = f"v2_syn_{gid}_pad_{syn_i:04d}"
            idx = len(candidates)
            candidates.append(
                PlannedCandidate(
                    planned_map_id=map_id,
                    archetype=arch,
                    source_type="synthetic",
                    anchor_id="",
                    trace_id="",
                    generator_type=gid,
                    seed=candidate_seed(
                        seed,
                        map_id=map_id,
                        archetype=arch,
                        source_type="synthetic",
                        trace_id="",
                        generator_type=gid,
                    ),
                    builder="synthetic",
                    input_reference=f"generator:{gid}",
                    output_directory=_out_dir(idx, map_id),
                    config_hash=ch,
                    enabled=True,
                    generator_parameters=_pick_discrete(gspec, syn_i),
                    batch_target=_stage_target(idx, batch_targets),
                )
            )
            syn_i += 1
    # Recompute batch targets after final order
    fixed: list[PlannedCandidate] = []
    for idx, c in enumerate(candidates):
        bt = _stage_target(idx, batch_targets)
        fixed.append(
            PlannedCandidate(
                **{
                    **c.__dict__,
                    "batch_target": bt,
                    "output_directory": str(output_root / f"batch_{bt:04d}" / "wkt" / c.planned_map_id),
                }
            )
        )
    candidates = fixed

    enabled = [c for c in candidates if c.enabled]
    by_arch = {c.archetype for c in enabled}
    by_src = {c.source_type for c in enabled}
    missing_arch = set(CANONICAL_ARCHETYPES) - by_arch
    if missing_arch and (ds.get("validation_policy") or {}).get("require_all_archetypes_covered", True):
        issues.append(PlanValidationIssue("CRITICAL", "archetype_coverage", f"Plan missing archetypes: {sorted(missing_arch)}"))
    missing_src = set(SOURCE_TYPES) - by_src
    if missing_src and (ds.get("validation_policy") or {}).get("require_all_source_types_present", True):
        issues.append(PlanValidationIssue("CRITICAL", "source_type_coverage", f"Plan missing source_types: {sorted(missing_src)}"))

    if (ds.get("validation_policy") or {}).get("require_archetype_source_matrix", True):
        for c in enabled:
            if not source_allowed(allocation, c.archetype, c.source_type):
                issues.append(
                    PlanValidationIssue(
                        "CRITICAL",
                        "matrix_violation",
                        f"{c.planned_map_id}: {c.source_type} forbidden for {c.archetype}",
                    )
                )

    # Soft-fraction INFO check (not a stopping rule)
    if enabled:
        n = len(enabled)
        actual = {s: sum(1 for c in enabled if c.source_type == s) / n for s in SOURCE_TYPES}
        soft = {"osm": osm_frac, "synthetic": syn_frac, "trace_reference_synthetic": trs_frac}
        for s, target_f in soft.items():
            if abs(actual.get(s, 0.0) - target_f) > 0.12:
                issues.append(
                    PlanValidationIssue(
                        "INFO",
                        "soft_fraction_drift",
                        f"{s} share {actual.get(s, 0.0):.2f} vs soft target {target_f:.2f} (matrix may dominate)",
                    )
                )

    ids = [c.planned_map_id for c in candidates]
    if len(ids) != len(set(ids)):
        issues.append(PlanValidationIssue("CRITICAL", "duplicate_ids", "Duplicate planned_map_id values"))

    for tid, entry in policy_map.items():
        role = entry.get("generation_role")
        if role in ("evidence_only", "future_candidate", "unsupported_for_generation"):
            for c in candidates:
                if c.trace_id == tid and c.enabled:
                    issues.append(
                        PlanValidationIssue(
                            "CRITICAL",
                            "non_generative_emitted",
                            f"Trace {tid} role={role} must not produce enabled maps",
                        )
                    )

    return GenerationPlan(candidates=candidates, issues=issues, config_hash=ch, seed=seed)


def offsets_nonzero(offsets: list[int]) -> list[int]:
    out = [o for o in offsets if o > 0]
    return out or [200]


def write_plan_csv(plan: GenerationPlan, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=PLAN_COLUMNS)
        w.writeheader()
        for c in plan.candidates:
            row = c.to_row()
            w.writerow({k: row.get(k, "") for k in PLAN_COLUMNS})


def write_plan_markdown(plan: GenerationPlan, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    enabled = [c for c in plan.candidates if c.enabled]
    lines = [
        "# Map generation v2 dry-run plan",
        "",
        f"- config_hash: `{plan.config_hash}`",
        f"- seed: `{plan.seed}`",
        f"- candidates: **{len(plan.candidates)}** (enabled {len(enabled)})",
        f"- critical issues: **{len(plan.critical_errors)}**",
        "",
        "## Counts by source_type",
        "",
    ]
    for k, v in plan.counts_by("source_type").items():
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Counts by archetype", ""]
    for k, v in plan.counts_by("archetype").items():
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Issues", ""]
    if not plan.issues:
        lines.append("- none")
    else:
        for i in plan.issues:
            lines.append(f"- **{i.severity}** `{i.code}`: {i.message}")
    lines += ["", "## Provenance samples", ""]
    for c in enabled[:3]:
        lines.append(f"### {c.planned_map_id}")
        lines.append("```json")
        lines.append(json.dumps(provenance_for_candidate(c), indent=2, sort_keys=True))
        lines.append("```")
        lines.append("")
    trs = sorted({c.trace_id for c in enabled if c.source_type == "trace_reference_synthetic" and c.trace_id})
    osm_supported = sorted({t for c in enabled for t in c.trace_support})
    lines += [
        "## Trace activation (this plan)",
        "",
        f"- parameterize → TRS maps: {', '.join(f'`{t}`' for t in trs) or '(none)'}",
        f"- osm_anchor_support attached: {', '.join(f'`{t}`' for t in osm_supported) or '(none)'}",
        "",
        "evidence_only / future_candidate / unsupported traces do not appear as enabled map rows.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_dry_run(
    *,
    design_space_path: Path | None = None,
    global_seed: int = 42,
    target_total: int | None = None,
    write_plan: bool = True,
) -> GenerationPlan:
    ds = load_revised_design_space(design_space_path)
    dry = ds.get("dry_run_policy") or {}
    if dry.get("allow_network"):
        raise RuntimeError("dry_run_policy.allow_network must be false for dry-run")
    plan = build_plan(design_space=ds, global_seed=global_seed, target_total=target_total)
    if write_plan and dry.get("write_plan", True):
        paths = ds.get("paths") or {}
        write_plan_csv(plan, resolve_repo_path(paths["plan_csv"]))
        write_plan_markdown(
            plan,
            resolve_repo_path(paths.get("plan_md", "scenarios/Generated_Map_Space_v1/docs/map_generation_v2_dry_run.md")),
        )
    return plan
