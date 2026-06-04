#!/usr/bin/env python3
"""Regenerate manifest.csv (and optional manifest_revision.csv) from .settings on disk."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCENARIOS_DIR = REPO_ROOT / "scenarios"

TP_RE = re.compile(r"__(TP\d{2})_([A-Za-z0-9]+)$")
TP_NAMES = {
    "TP01": "Baseline",
    "TP02": "LowLoad",
    "TP03": "ManySmall",
    "TP04": "FewLarge",
    "TP05": "CriticalTTL",
    "TP06": "OneToMany",
    "TP07": "BurstWindow",
    "TP08": "HubTarget",
    "TP09": "Bimodal",
    "TP10": "Storm",
    "TP11": "ManyToOne",
    "TP12": "GroupToGroup",
}

def parse_settings(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.split("#")[0].strip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def infer_hosts(kv: dict[str, str]) -> int:
    try:
        ng = int(kv.get("Scenario.nrofHostGroups", "0") or "0")
    except ValueError:
        ng = 0
    total = 0
    for i in range(1, ng + 1):
        key = f"Group{i}.nrofHosts"
        if key in kv:
            try:
                total += int(kv[key].replace(",", "").split()[0])
            except ValueError:
                pass
    if total > 0:
        return total
    if "Group.nrofHosts" in kv:
        try:
            return int(kv["Group.nrofHosts"].replace(",", "").split()[0])
        except ValueError:
            pass
    return 0

def parse_scenario(stem: str) -> tuple[str, str, str]:
    m = TP_RE.search(stem)
    if not m:
        return stem, "", ""
    base = stem[: m.start()]
    tp_id = m.group(1)
    tp_name = m.group(2)
    return base, tp_id, tp_name

def corpus_prefix(corpus_dir: Path) -> str:
    try:
        rel = corpus_dir.relative_to(REPO_ROOT)
        return str(rel).replace("\\", "/")
    except ValueError:
        return str(corpus_dir)

def build_manifest_rows(
    corpus_dir: Path,
    families: list[str] | None = None,
    *,
    flat_family: str | None = None,
) -> list[dict]:
    prefix = corpus_prefix(corpus_dir)
    rows: list[dict] = []

    # Flat layout: *.settings directly under corpus_dir (e.g. 07_)
    root_settings = sorted(corpus_dir.glob("*.settings"))
    if root_settings:
        fam_name = flat_family or corpus_dir.name
        for sf in root_settings:
            text = sf.read_text(encoding="utf-8", errors="replace")
            kv = parse_settings(text)
            scenario_name = kv.get("Scenario.name", sf.stem)
            base, tp_id, tp_label = parse_scenario(scenario_name)
            rel_path = f"{prefix}/{sf.name}"
            rows.append(
                {
                    "family": fam_name,
                    "scenario_base": base,
                    "scenario_name": scenario_name,
                    "traffic_profile_id": tp_id,
                    "traffic_profile_name": TP_NAMES.get(tp_id, tp_label),
                    "settings_file": rel_path,
                    "n_hosts": infer_hosts(kv),
                    "Scenario.endTime": kv.get("Scenario.endTime", ""),
                    "Group.msgTtl_minutes": kv.get("Group.msgTtl", kv.get("Group1.msgTtl", "")),
                    "Events.nrof": kv.get("Events.nrof", ""),
                    "Events1.interval": kv.get("Events1.interval", ""),
                    "Events1.size": kv.get("Events1.size", ""),
                    "note": "",
                }
            )
        return rows

    fam_dirs = sorted(corpus_dir.iterdir()) if families is None else [
        corpus_dir / f for f in families if (corpus_dir / f).is_dir()
    ]
    for fam_dir in fam_dirs:
        if not fam_dir.is_dir() or fam_dir.name.startswith("_") or fam_dir.name.startswith("."):
            continue
        if families and fam_dir.name not in families:
            continue
        for sf in sorted(fam_dir.glob("*.settings")):
            text = sf.read_text(encoding="utf-8", errors="replace")
            kv = parse_settings(text)
            scenario_name = kv.get("Scenario.name", sf.stem)
            base, tp_id, tp_label = parse_scenario(scenario_name)
            if not tp_id:
                tp_id = ""
                tp_label = ""
            rel_path = f"{prefix}/{fam_dir.name}/{sf.name}"
            rows.append(
                {
                    "family": fam_dir.name,
                    "scenario_base": base,
                    "scenario_name": scenario_name,
                    "traffic_profile_id": tp_id,
                    "traffic_profile_name": TP_NAMES.get(tp_id, tp_label),
                    "settings_file": rel_path,
                    "n_hosts": infer_hosts(kv),
                    "Scenario.endTime": kv.get("Scenario.endTime", ""),
                    "Group.msgTtl_minutes": kv.get("Group.msgTtl", kv.get("Group1.msgTtl", "")),
                    "Events.nrof": kv.get("Events.nrof", ""),
                    "Events1.interval": kv.get("Events1.interval", ""),
                    "Events1.size": kv.get("Events1.size", ""),
                    "note": "",
                }
            )
    return rows

def write_manifest(path: Path, rows: list[dict]) -> None:
    cols = [
        "family",
        "scenario_base",
        "scenario_name",
        "traffic_profile_id",
        "traffic_profile_name",
        "settings_file",
        "n_hosts",
        "Scenario.endTime",
        "Group.msgTtl_minutes",
        "Events.nrof",
        "Events1.interval",
        "Events1.size",
        "note",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

def patch_revision_paths(rev_path: Path, rows: list[dict]) -> None:
    if not rev_path.is_file():
        return
    by_name = {r["scenario_name"]: r for r in rows}
    with rev_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        old_rows = list(reader)
    if not fieldnames:
        return
    for row in old_rows:
        name = row.get("scenario_name", "")
        if name in by_name:
            row["settings_file"] = by_name[name]["settings_file"]
            row["scenario_base"] = by_name[name]["scenario_base"]
            row["family"] = by_name[name]["family"]
    with rev_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(old_rows)

def main() -> int:
    ap = argparse.ArgumentParser(description="Regenerate corpus manifest from disk.")
    ap.add_argument(
        "--corpus-dir",
        type=Path,
        required=True,
        help="Corpus directory (e.g. scenarios/corpus_v1)",
    )
    ap.add_argument(
        "--families",
        nargs="*",
        default=None,
        help="Optional family subdirs to include",
    )
    ap.add_argument(
        "--patch-revision",
        action="store_true",
        help="Update settings_file paths in existing manifest_revision.csv",
    )
    ap.add_argument(
        "--flat-family",
        type=str,
        default=None,
        help="Family id when .settings live directly under corpus-dir",
    )
    args = ap.parse_args()
    corpus_dir = args.corpus_dir
    if not corpus_dir.is_absolute():
        corpus_dir = REPO_ROOT / corpus_dir
    if not corpus_dir.is_dir():
        print(f"ERROR: not a directory: {corpus_dir}", file=sys.stderr)
        return 1
    rows = build_manifest_rows(corpus_dir, args.families, flat_family=args.flat_family)
    manifest_path = corpus_dir / "manifest.csv"
    write_manifest(manifest_path, rows)
    print(f"Wrote {manifest_path} ({len(rows)} rows)")
    rev_path = corpus_dir / "manifest_revision.csv"
    if args.patch_revision and rev_path.is_file():
        # filter revision to scenarios still present
        names = {r["scenario_name"] for r in rows}
        with rev_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            kept = [row for row in reader if row.get("scenario_name") in names]
        patch_revision_paths(rev_path, rows)
        with rev_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(kept)
        print(f"Patched {rev_path} ({len(kept)} rows)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())