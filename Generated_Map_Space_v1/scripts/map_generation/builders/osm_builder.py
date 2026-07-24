"""OSM builder facade for revised v2 (reuses map_space_osm_builder)."""

from __future__ import annotations

from typing import Any

from map_generation.models import PlannedCandidate
from map_generation.provenance import provenance_for_candidate


def plan_osm_metadata(cand: PlannedCandidate, anchor: dict[str, Any]) -> dict[str, Any]:
    """Build provenance/metadata without network I/O (dry-run safe)."""
    bbox = anchor.get("bbox") or {}
    center_lat = (float(bbox.get("south", 0)) + float(bbox.get("north", 0))) / 2.0
    center_lon = (float(bbox.get("west", 0)) + float(bbox.get("east", 0))) / 2.0
    prov = provenance_for_candidate(cand)
    prov["osm_query"]["place"] = anchor.get("place_name")
    prov["osm_query"]["bbox"] = dict(bbox) if bbox else None
    prov["center_lat"] = center_lat
    prov["center_lon"] = center_lon
    prov["crs"] = anchor.get("crs")
    return prov


def build_osm_candidate(
    cand: PlannedCandidate,
    *,
    anchor: dict[str, Any],
    output_root: Any,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Dry-run returns provenance only. Full build is handled by map_generation.executor."""
    meta = plan_osm_metadata(cand, anchor)
    if dry_run:
        meta["status"] = "dry_run_no_download"
        return meta
    meta["status"] = "use_executor_for_full_build"
    return meta
