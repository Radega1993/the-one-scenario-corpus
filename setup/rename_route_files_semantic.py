#!/usr/bin/env python3
"""Rename route WKT files to semantic names and update routeFile in .settings."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import DATA_DIR, SCENARIOS_DIR, WKT_DIR  # noqa: E402
from route_semantic_config import ROUTE_SEMANTIC_ROWS, SETTINGS_PATH_RENAMES  # noqa: E402

REPORTS_DIR = SCENARIOS_DIR / "analysis" / "reports" / "maps"
CHANGELOG = REPORTS_DIR / "route_file_renaming_changelog.md"

TREES = (
    SCENARIOS_DIR / "base_scenarios",
    SCENARIOS_DIR / "corpus_v1",
)

ROUTE_FILE_RE = re.compile(r"^Group\d+\.routeFile$")

def load_settings_flat(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()

def count_settings_renames() -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for old, new in SETTINGS_PATH_RENAMES.items():
        for root in TREES:
            if not root.is_dir():
                continue
            for sp in root.rglob("*.settings"):
                text = sp.read_text(encoding="utf-8", errors="replace")
                if old in text:
                    counts[old] += text.count(old)
    return counts

def rename_on_disk(map_name: str, old: str, new: str, apply: bool) -> bool:
    changed = False
    for base in (WKT_DIR / map_name, DATA_DIR / map_name):
        if not base.is_dir():
            continue
        src, dst = base / old, base / new
        if src.is_file() and not dst.is_file():
            if apply:
                src.rename(dst)
            changed = True
        elif src.is_file() and dst.is_file() and apply:
            src.unlink()
            changed = True
    return changed

def patch_settings(apply: bool) -> list[tuple[Path, str, str]]:
    edits: list[tuple[Path, str, str]] = []
    for root in TREES:
        if not root.is_dir():
            continue
        for sp in sorted(root.rglob("*.settings")):
            lines = load_settings_flat(sp)
            new_lines: list[str] = []
            file_changed = False
            for line in lines:
                stripped = line.split("#", 1)[0].strip()
                if "=" in stripped:
                    key, val = stripped.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    if ROUTE_FILE_RE.match(key) and val in SETTINGS_PATH_RENAMES:
                        new_val = SETTINGS_PATH_RENAMES[val]
                        if new_val != val:
                            line = line.replace(val, new_val)
                            edits.append((sp, val, new_val))
                            file_changed = True
                new_lines.append(line)
            if file_changed and apply:
                sp.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return edits

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--install", action="store_true", help="Alias: also patch data/ (done with disk rename)")
    args = ap.parse_args()

    if not args.dry_run and not args.apply:
        print("Specify --dry-run or --apply")
        return 1

    counts = count_settings_renames()
    renames = [(m, c, r) for m, c, r, _ in ROUTE_SEMANTIC_ROWS if c != r]

    print("Planned file renames:")
    for m, old, new in renames:
        n = counts.get(f"data/{m}/{old}", 0)
        print(f"  {m}: {old} -> {new}  ({n} settings refs)")

    if args.apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = WKT_DIR / f"_backup_route_rename_{stamp}"
        backup.mkdir(parents=True, exist_ok=True)
        for m, old, new in renames:
            src_dir = WKT_DIR / m
            if src_dir.is_dir():
                shutil.copytree(src_dir, backup / m, dirs_exist_ok=True)
        print(f"Backup -> {backup}")

    disk_changes = 0
    for m, old, new in renames:
        if rename_on_disk(m, old, new, apply=args.apply):
            disk_changes += 1

    edits = patch_settings(apply=args.apply)
    unique_settings = len({e[0] for e in edits})

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Route file renaming changelog",
        "",
        f"Date: {datetime.now().isoformat(timespec='seconds')}",
        f"Mode: {'apply' if args.apply else 'dry-run'}",
        "",
        "## File renames",
        "",
    ]
    for m, old, new in renames:
        lines.append(f"- `{m}/{old}` → `{m}/{new}`")
    lines.extend(["", "## Settings updates", ""])
    for sp, old, new in edits[:50]:
        lines.append(f"- `{sp.relative_to(SCENARIOS_DIR.parent)}`: `{old}` → `{new}`")
    if len(edits) > 50:
        lines.append(f"- … and {len(edits) - 50} more substitutions")
    lines.append(f"\nTotal settings files touched: {unique_settings}")
    lines.append(f"Disk rename operations: {disk_changes}")
    CHANGELOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {CHANGELOG}")
    print(f"Settings substitutions: {len(edits)} in {unique_settings} files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())