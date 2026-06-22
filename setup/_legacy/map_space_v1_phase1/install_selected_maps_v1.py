#!/usr/bin/env python3
"""Install selected map_space_v1 maps into data/ for The ONE."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_asset_generator_v1 import generate_assets_for_map, load_asset_policy  # noqa: E402

REPO_ROOT = _SETUP.parent.parent
DATA_DIR = REPO_ROOT / "data"
SCENARIOS_DIR = _SETUP.parent
DEFAULT_MANIFEST = SCENARIOS_DIR / "map_space_v1" / "selected_maps" / "manifest_maps_selected.csv"
MAP_SPACE_ROOT = SCENARIOS_DIR / "map_space_v1"


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def install_map(row: dict[str, str], *, generate_assets: bool, seed: int) -> Path:
    map_id = row["map_id"]
    wkt_rel = row.get("wkt_dir", "")
    src_dir = MAP_SPACE_ROOT / wkt_rel
    if not src_dir.is_dir():
        raise FileNotFoundError(f"Missing wkt dir: {src_dir}")

    dst_dir = DATA_DIR / map_id
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    dst_dir.mkdir(parents=True)
    shutil.copy2(src_dir / "roads.wkt", dst_dir / "roads.wkt")
    if (src_dir / "metadata.json").is_file():
        shutil.copy2(src_dir / "metadata.json", dst_dir / "metadata.json")

    for preview_root in ("synthetic/previews", "real_osm/previews"):
        preview = MAP_SPACE_ROOT / preview_root / f"{map_id}.png"
        if preview.is_file():
            shutil.copy2(preview, dst_dir / f"{map_id}_preview.png")
            break

    for asset in src_dir.glob("A_*.wkt"):
        shutil.copy2(asset, dst_dir / asset.name)

    if generate_assets:
        policy = load_asset_policy()
        generate_assets_for_map(dst_dir, policy=policy, seed=seed)

    meta = json.loads((dst_dir / "metadata.json").read_text(encoding="utf-8"))
    meta["name"] = map_id
    meta["installed_from"] = str(src_dir)
    (dst_dir / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return dst_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Install selected maps into data/")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--generate-assets", action="store_true", default=True)
    parser.add_argument("--no-generate-assets", action="store_false", dest="generate_assets")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rows = load_manifest(args.manifest)
    installed = 0
    for row in rows:
        if row.get("status", "ok") not in ("ok", "PASS", "selected"):
            continue
        try:
            install_map(row, generate_assets=args.generate_assets, seed=args.seed)
            installed += 1
            print(f"Installed {row['map_id']}")
        except Exception as exc:
            print(f"SKIP {row['map_id']}: {exc}")

    print(f"Done: {installed}/{len(rows)} maps → {DATA_DIR}")


if __name__ == "__main__":
    main()
