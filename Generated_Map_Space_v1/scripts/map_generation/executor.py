"""Execute planned map generation into map_space_revised_v2/."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

from map_generation.config import load_revised_design_space, resolve_repo_path
from map_generation.models import GenerationPlan, PlannedCandidate
from map_generation.planner import build_plan, write_plan_csv, write_plan_markdown
from map_generation.provenance import write_provenance

logger = logging.getLogger(__name__)

MANIFEST_COLUMNS = [
    "map_id",
    "batch_target",
    "source_type",
    "anchor_id",
    "trace_id",
    "archetype",
    "generator_type",
    "seed",
    "generation_status",
    "error_notes",
    "wkt_path",
    "metadata_path",
]


def execute_plan(
    plan: GenerationPlan,
    *,
    design_space: dict[str, Any],
    source: str = "all",
    force: bool = False,
    max_osm_downloads: int = 0,
    osm_timeout: int = 180,
    osm_pause: float = 2.0,
    write_previews: bool = True,
) -> list[dict[str, str]]:
    """Build WKT/metadata for planned candidates. OSM downloads bounded by max_osm_downloads."""
    from map_space_osm_builder import (
        OsmBuildContext,
        build_osm_map_from_cache,
        download_osm_graph_for_candidate,
    )
    from map_space_synthetic_builder import SyntheticBuildContext, build_synthetic_map

    osm_by_id = {str(a["anchor_id"]): a for a in (design_space.get("osm_anchors") or [])}
    output_root = resolve_repo_path((design_space.get("paths") or {}).get("output_root", "scenarios/Generated_Map_Space_v1"))
    preview_dir = output_root / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    (output_root / "osm_cache").mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    osm_downloads = 0

    for cand in plan.candidates:
        if not cand.enabled:
            continue
        if source == "osm" and cand.source_type != "osm":
            continue
        if source == "synthetic" and cand.source_type not in ("synthetic", "trace_reference_synthetic"):
            continue

        wkt_dir = Path(cand.output_directory)
        roads = wkt_dir / "roads.wkt"
        meta_path = wkt_dir / "metadata.json"
        status = "OK"
        err = ""

        if roads.is_file() and meta_path.is_file() and not force:
            status = "OK"  # keep OK on re-run (do not demote to SKIPPED_EXISTING_OK in manifest)
        elif cand.source_type == "osm":
            status, err, osm_downloads = _build_osm(
                cand,
                osm_by_id=osm_by_id,
                output_root=output_root,
                preview_dir=preview_dir,
                max_osm_downloads=max_osm_downloads,
                osm_downloads=osm_downloads,
                osm_timeout=osm_timeout,
                osm_pause=osm_pause,
                write_previews=write_previews,
            )
        else:
            status, err = _build_synthetic_like(cand, preview_dir=preview_dir, write_previews=write_previews)

        if status == "OK" or status == "SKIPPED_EXISTING_OK":
            try:
                write_provenance(wkt_dir / "provenance.json", cand)
            except Exception as exc:
                logger.warning("provenance write failed for %s: %s", cand.planned_map_id, exc)

        # Enrich metadata with v2 provenance fields when present
        if meta_path.is_file() and cand.source_type == "trace_reference_synthetic":
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                meta["trace_id"] = cand.trace_id
                meta["parameter_extractor"] = cand.parameter_extractor
                meta["extracted_parameters"] = cand.extracted_parameters
                meta["config_hash"] = cand.config_hash
                meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
            except Exception:
                pass

        rows.append(
            {
                "map_id": cand.planned_map_id,
                "batch_target": str(cand.batch_target),
                "source_type": cand.source_type,
                "anchor_id": cand.anchor_id,
                "trace_id": cand.trace_id,
                "archetype": cand.archetype,
                "generator_type": cand.generator_type,
                "seed": str(cand.seed),
                "generation_status": status,
                "error_notes": err,
                "wkt_path": str(roads) if roads.is_file() else "",
                "metadata_path": str(meta_path) if meta_path.is_file() else "",
            }
        )
        logger.info("%s %s %s", cand.planned_map_id, status, err[:80] if err else "")

    manifest = output_root / "manifest_maps_all.csv"
    _write_manifest(manifest, rows)
    return rows


def _build_osm(
    cand: PlannedCandidate,
    *,
    osm_by_id: dict[str, dict[str, Any]],
    output_root: Path,
    preview_dir: Path,
    max_osm_downloads: int,
    osm_downloads: int,
    osm_timeout: int,
    osm_pause: float,
    write_previews: bool,
) -> tuple[str, str, int]:
    from map_space_osm_builder import OsmBuildContext, build_osm_map_from_cache, download_osm_graph_for_candidate

    anchor = osm_by_id.get(cand.anchor_id)
    if not anchor:
        return "FAIL_UNKNOWN", f"missing anchor {cand.anchor_id}", osm_downloads
    params = dict(cand.generator_parameters or {})
    wkt_dir = Path(cand.output_directory)
    # Acquire
    cached = (output_root / "osm_cache" / f"{cand.planned_map_id}.graphml").is_file()
    if not cached:
        if max_osm_downloads <= 0 or osm_downloads >= max_osm_downloads:
            return "FAIL_DOWNLOAD_SKIPPED", "max OSM downloads reached or disabled", osm_downloads
        result = download_osm_graph_for_candidate(
            map_id=cand.planned_map_id,
            params=params,
            network_type=cand.network_type or "drive",
            output_root=output_root,
            timeout=osm_timeout,
            pause_seconds=osm_pause,
            use_cache=True,
        )
        osm_downloads += 1
        if not result.success:
            return "FAIL_DOWNLOAD_TRANSIENT", result.error_message or result.error_kind or "download failed", osm_downloads

    ctx = OsmBuildContext(
        map_id=cand.planned_map_id,
        source_type="osm",
        anchor_id=cand.anchor_id,
        anchor_label=str(params.get("anchor_label") or cand.anchor_id),
        archetype=cand.archetype,
        crs=str(params.get("crs") or anchor.get("crs") or "EPSG:3857"),
        network_type=cand.network_type or "drive",
        params=params,
        allow_partitioned=bool(params.get("_allow_partitioned")),
        topology_flags=list(params.get("_topology_flags") or []),
        variant_type=cand.variant_type or "exact",
        anchor_distance_m=float(cand.offset_m),
        window_size_m=float(cand.window_size_m or params.get("window_size_m") or 1000),
        seed=int(cand.seed),
    )
    try:
        status, msg = build_osm_map_from_cache(
            ctx=ctx,
            output_root=output_root,
            wkt_dir=wkt_dir,
            preview_dir=preview_dir if write_previews else preview_dir,
        )
        return status, msg, osm_downloads
    except Exception as exc:
        return "FAIL_BUILD_OSM", str(exc), osm_downloads


def _build_synthetic_like(
    cand: PlannedCandidate,
    *,
    preview_dir: Path,
    write_previews: bool,
) -> tuple[str, str]:
    from map_space_synthetic_builder import SyntheticBuildContext, build_synthetic_map

    ctx = SyntheticBuildContext(
        map_id=cand.planned_map_id,
        source_type=cand.source_type,
        anchor_id=cand.anchor_id or "",
        anchor_label=cand.trace_id or cand.anchor_id or "",
        archetype=cand.archetype,
        generator_type=cand.generator_type,
        params=dict(cand.generator_parameters or {}),
        seed=int(cand.seed),
    )
    wkt_dir = Path(cand.output_directory)
    try:
        return build_synthetic_map(
            ctx=ctx,
            wkt_dir=wkt_dir,
            preview_dir=preview_dir,
            global_seed=int(cand.seed),
        )
    except Exception as exc:
        return "FAIL_BUILD_SYNTHETIC_DEGENERATE", str(exc)


def _write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_id: dict[str, dict[str, str]] = {}
    if path.is_file():
        with path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                mid = r.get("map_id") or ""
                if mid:
                    by_id[mid] = {k: r.get(k, "") for k in MANIFEST_COLUMNS}
    for r in rows:
        by_id[r["map_id"]] = {k: r.get(k, "") for k in MANIFEST_COLUMNS}
    merged = sorted(by_id.values(), key=lambda x: x.get("map_id", ""))
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        w.writeheader()
        for r in merged:
            w.writerow(r)


def run_revised_generation(
    *,
    config_path: Path,
    seed: int = 42,
    target_total: int = 1200,
    source: str = "all",
    force: bool = False,
    max_osm_downloads: int = 50,
    osm_timeout: int = 180,
    osm_pause: float = 2.0,
    plan_only: bool = False,
    acquire_osm: bool = False,
    build: bool = False,
    generate: bool = False,
) -> int:
    ds = load_revised_design_space(config_path)
    plan = build_plan(design_space=ds, global_seed=seed, target_total=target_total)
    paths = ds.get("paths") or {}
    write_plan_csv(plan, resolve_repo_path(paths["plan_csv"]))
    write_plan_markdown(plan, resolve_repo_path(paths.get("plan_md", "scenarios/Generated_Map_Space_v1/docs/map_generation_v2_dry_run.md")))

    if plan.critical_errors:
        for i in plan.critical_errors:
            logger.error("[%s] %s: %s", i.severity, i.code, i.message)
        return 1

    if plan_only and not (acquire_osm or build or generate):
        logger.info("Plan-only: %s candidates written", len(plan.candidates))
        return 0

    do_build = build or generate
    do_acquire = acquire_osm or (generate and max_osm_downloads > 0)
    # For generate without acquire flag, still build synthetics/TRS; OSM needs cache or downloads
    max_dl = max_osm_downloads if do_acquire else (max_osm_downloads if generate else 0)
    if generate and not do_acquire:
        max_dl = max_osm_downloads  # honor CLI max downloads during generate

    rows = execute_plan(
        plan,
        design_space=ds,
        source=source,
        force=force,
        max_osm_downloads=max_dl if (do_acquire or generate) else 0,
        osm_timeout=osm_timeout,
        osm_pause=osm_pause,
    )
    ok = sum(1 for r in rows if r["generation_status"] in ("OK", "SKIPPED_EXISTING_OK"))
    logger.info("Generation complete: %s/%s OK", ok, len(rows))
    _write_run_report(plan, rows, resolve_repo_path("scenarios/Generated_Map_Space_v1/docs/map_generation_revised_v2_run.md"))
    return 0 if ok > 0 or not do_build else 1


def _write_run_report(plan: GenerationPlan, rows: list[dict[str, str]], path: Path) -> None:
    from collections import Counter

    path.parent.mkdir(parents=True, exist_ok=True)
    output_root = resolve_repo_path("scenarios/Generated_Map_Space_v1")
    manifest = output_root / "manifest_maps_all.csv"
    report_rows = rows
    if manifest.is_file():
        with manifest.open(newline="", encoding="utf-8") as f:
            report_rows = list(csv.DictReader(f))
    status = Counter(r.get("generation_status", "") for r in report_rows)
    ok_statuses = ("OK", "SKIPPED_EXISTING_OK")
    by_src = Counter(
        r.get("source_type", "") for r in report_rows if r.get("generation_status") in ok_statuses
    )
    by_arch = Counter(
        r.get("archetype", "") for r in report_rows if r.get("generation_status") in ok_statuses
    )
    osm_ok = sum(
        1
        for r in report_rows
        if r.get("source_type") == "osm" and r.get("generation_status") in ok_statuses
    )
    osm_skip = sum(1 for r in report_rows if r.get("generation_status") == "FAIL_DOWNLOAD_SKIPPED")
    lines = [
        "# Map generation revised v2 run",
        "",
        "**Pool role:** engineering validation pool (not a scientific stopping point).",
        f"**N={len(plan.candidates)}:** initial_engineering_target; saturation ladder may continue beyond.",
        "",
        f"- planned: {len(plan.candidates)}",
        f"- attempted (manifest rows): {len(report_rows)}",
        f"- config_hash: `{plan.config_hash}`",
        f"- seed: {plan.seed}",
        f"- osm_ok: {osm_ok}",
        f"- osm_download_skipped_remaining: {osm_skip}",
        "",
        "## Status counts",
        "",
    ]
    for k, v in sorted(status.items()):
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## OK by source_type", ""]
    for k, v in sorted(by_src.items()):
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## OK by archetype", ""]
    for k, v in sorted(by_arch.items()):
        lines.append(f"- `{k}`: {v}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
