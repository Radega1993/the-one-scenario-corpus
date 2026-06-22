#!/usr/bin/env python3
"""Archive legacy OSM maps (no anchor_id) from map_space_v1 and rebuild manifest."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
MAP_SPACE = REPO / "scenarios" / "map_space_v1"
ARCHIVE_TAG = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def is_legacy_osm(map_id: str, meta: dict | None, row: dict | None) -> bool:
    if not map_id.startswith("OSM_"):
        return False
    if row and (row.get("anchor_id") or "").strip():
        return False
    if meta and (meta.get("anchor_id") or ""):
        return False
    return True


def load_meta(wkt_dir: Path) -> dict | None:
    p = wkt_dir / "metadata.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def archive_legacy(*, dry_run: bool = False) -> dict:
    archive_root = MAP_SPACE / f"_archive/legacy_osm_pool_{ARCHIVE_TAG}"
    manifest_path = MAP_SPACE / "manifest_maps.csv"
    rows: list[dict[str, str]] = []
    if manifest_path.is_file():
        with manifest_path.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

    row_by_id = {r["map_id"]: r for r in rows}
    legacy_ids: list[str] = []

    osm_wkt = MAP_SPACE / "real_osm" / "wkt"
    for d in sorted(osm_wkt.iterdir()) if osm_wkt.is_dir() else []:
        if not d.is_dir():
            continue
        mid = d.name
        meta = load_meta(d)
        row = row_by_id.get(mid)
        if is_legacy_osm(mid, meta, row):
            legacy_ids.append(mid)

    # Also catch manifest-only legacy rows
    for r in rows:
        if r["source_type"] == "osm" and not (r.get("anchor_id") or "").strip():
            if r["map_id"] not in legacy_ids:
                legacy_ids.append(r["map_id"])

    legacy_ids = sorted(set(legacy_ids))
    kept_rows = [r for r in rows if r["map_id"] not in legacy_ids]

    stats = {
        "legacy_archived": len(legacy_ids),
        "manifest_before": len(rows),
        "manifest_after": len(kept_rows),
        "archive_root": str(archive_root),
    }

    if dry_run:
        stats["dry_run"] = True
        stats["legacy_sample"] = legacy_ids[:15]
        return stats

    archive_root.mkdir(parents=True, exist_ok=True)
    for sub in ("real_osm/wkt", "real_osm/raw", "real_osm/previews", "previews_validation"):
        (archive_root / sub).mkdir(parents=True, exist_ok=True)

    # Backup manifest
    if manifest_path.is_file():
        shutil.copy2(manifest_path, archive_root / "manifest_maps_before_cleanup.csv")

    legacy_manifest = [row_by_id[mid] for mid in legacy_ids if mid in row_by_id]
    if legacy_manifest:
        cols = list(legacy_manifest[0].keys())
        with (archive_root / "manifest_legacy_archived.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(legacy_manifest)

    for mid in legacy_ids:
        for rel in (
            f"real_osm/wkt/{mid}",
            f"real_osm/raw/{mid}.graphml",
            f"real_osm/previews/{mid}.png",
            f"previews_validation/{mid}_validation.png",
        ):
            src = MAP_SPACE / rel
            if src.is_file() or src.is_dir():
                dst = archive_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.move(str(src), str(dst))
                else:
                    shutil.move(str(src), str(dst))

    # Write cleaned manifest
    if kept_rows:
        cols = list(rows[0].keys()) if rows else [
            "map_id", "map_name", "source_type", "anchor_id", "anchor_label", "dataset_basis",
            "archetype", "generator_type", "wkt_dir", "roads_wkt", "world_size_x", "world_size_y",
            "crs", "network_type", "bbox_or_generator_params", "seed", "n_nodes", "n_edges",
            "status", "notes",
        ]
        with manifest_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(kept_rows)

    # Archive stale selected_maps
    sel = MAP_SPACE / "selected_maps"
    if sel.is_dir() and any(sel.iterdir()):
        dst_sel = archive_root / "selected_maps_before_cleanup"
        if dst_sel.exists():
            shutil.rmtree(dst_sel)
        shutil.move(str(sel), str(dst_sel))
        sel.mkdir()

    (archive_root / "README.md").write_text(
        f"""# Legacy OSM pool archive

**Date:** {datetime.now(timezone.utc).isoformat()}

Archived **{len(legacy_ids)}** OSM maps without `anchor_id` (region_pool / seed_osm_cache era).
These maps often share identical GraphML cache and duplicate topology.

Kept pool: anchor-based OSM + synthetic only.

## Restore (if needed)

```bash
# Move wkt/raw/previews back under map_space_v1/
```
""",
        encoding="utf-8",
    )

    return stats


def main() -> None:
    p = argparse.ArgumentParser(description="Archive legacy OSM maps from map_space_v1")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    stats = archive_legacy(dry_run=args.dry_run)
    for k, v in stats.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
