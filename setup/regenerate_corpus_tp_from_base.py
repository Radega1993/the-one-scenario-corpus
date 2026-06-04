#!/usr/bin/env python3
"""Regenerate corpus_v1 TP variants from base_scenarios (mobility unchanged, Events/TTL from TP defs)."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
_SCENARIOS = _SETUP.parent
_REPO = _SCENARIOS.parent
_ANALYSIS = _SCENARIOS / "analysis"
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import build_combined_manifest_csv  # noqa: E402
from lib.traffic_profile_generator import (  # noqa: E402
    PROFILE_ORDER,
    build_events_block,
    ensure_msg_ttl,
    infer_end_time,
    infer_total_hosts,
    parse_simple_settings,
    profile_ttl_minutes,
    set_scenario_name,
)

BASE = _SCENARIOS / "base_scenarios"
CORPUS = _SCENARIOS / "corpus_v1"
MANIFEST = CORPUS / "manifest.csv"
BENCH = _ANALYSIS / "data" / "benchmark_definition.csv"

# scenario_base -> (family_dir, corpus radio overrides)
CORPUS_RADIO: dict[str, dict[str, str]] = {
    "06_social": {"bt0.transmitRange": "25", "bt0.transmitSpeed": "2M"},
    "05_disaster": {"bt0.transmitRange": "10", "bt0.transmitSpeed": "2M"},
    "04_rural": {"bt0.transmitRange": "10", "bt0.transmitSpeed": "2M"},
}

OLD_TO_NEW: dict[str, str] = {
    "S1_StrongCommunities_SeparateClusters": "S1_StrongCommunities_LimitedMixing",
    "S6_FamilyGroups_SmallPersistent": "S6_FamilyGroups_LocalRoutines",
    "D1_ShelterHotspots_Clusters": "D1_ShelterHotspots_EmergencyMobility",
    "R2_VillagesTrails_ThreeClusters": "R2_VillagesTrails_InterVillage",
}

NEW_BASES = list(OLD_TO_NEW.values())

def _family_for_base(base: str) -> str:
    if base.startswith("S"):
        return "06_social"
    if base.startswith("D"):
        return "05_disaster"
    if base.startswith("R"):
        return "04_rural"
    raise ValueError(base)

def mobility_prefix(content: str) -> str:
    """Everything before Events.nrof (exclusive)."""
    m = re.search(r"^Events\.nrof\s*=", content, flags=re.MULTILINE)
    if not m:
        raise ValueError("No Events.nrof in base settings")
    return content[: m.start()]

def apply_corpus_radio(prefix: str, family: str) -> str:
    overrides = CORPUS_RADIO.get(family, {})
    lines = prefix.splitlines(keepends=True)
    out: list[str] = []
    for ln in lines:
        stripped = ln.split("#", 1)[0].strip()
        replaced = False
        for key, val in overrides.items():
            if stripped.startswith(key + " ="):
                out.append(f"{key} = {val}\n")
                replaced = True
                break
        if not replaced:
            out.append(ln)
    return "".join(out)

def group_host_counts(kv: dict[str, str]) -> tuple[int | None, int | None]:
    ng = int(kv.get("Scenario.nrofHostGroups", "1"))
    g1 = int(kv["Group1.nrofHosts"]) if "Group1.nrofHosts" in kv else None
    g2 = int(kv["Group2.nrofHosts"]) if "Group2.nrofHosts" in kv else None
    return g1, g2

def generate_one(base_path: Path, tp_id: str, tp_label: str) -> str:
    base_stem = base_path.stem
    family = _family_for_base(base_stem)
    raw = base_path.read_text(encoding="utf-8")
    prefix = apply_corpus_radio(mobility_prefix(raw), family)
    kv = parse_simple_settings(raw)
    n = infer_total_hosts(kv) or 0
    end_t = infer_end_time(kv)
    g1, g2 = group_host_counts(kv)
    events_block, _ = build_events_block(tp_id, n, end_t, g1, g2)
    ttl = profile_ttl_minutes(tp_id, base_stem)
    prefix_ttl = ensure_msg_ttl(prefix, ttl)
    body = prefix_ttl + events_block + "\n\n"
    body = set_scenario_name(body, f"{base_stem}__{tp_id}_{tp_label}")
    header = (
        f"# Corpus traffic profile ({tp_id} {tp_label}) — generated from base; "
        f"mobility unchanged; Events* and Group*.msgTtl overridden.\n"
    )
    idx = raw.find("\n\n")
    comment = raw[: idx + 1] if idx > 0 and raw.lstrip().startswith("#") else ""
    return header + comment + body + (
        "Report.nrofReports = 2\n"
        "Report.reportDir = reports/\n"
        "Report.report1 = MessageStatsReport\n"
        "Report.report2 = ContactTimesReport\n"
    )

def remove_old_corpus(stems: list[str]) -> int:
    n = 0
    for old in stems:
        for p in CORPUS.rglob(f"{old}__*.settings"):
            p.unlink()
            n += 1
    return n

def write_corpus_variants(bases: list[str], dry_run: bool) -> list[dict]:
    rows: list[dict] = []
    for base in bases:
        family = _family_for_base(base)
        base_path = BASE / family / f"{base}.settings"
        if not base_path.is_file():
            raise FileNotFoundError(base_path)
        for tp_id, tp_label in PROFILE_ORDER:
            scen = f"{base}__{tp_id}_{tp_label}"
            out_path = CORPUS / family / f"{scen}.settings"
            content = generate_one(base_path, tp_id, tp_label)
            if not dry_run:
                out_path.write_text(content, encoding="utf-8")
            kv = parse_simple_settings(content)
            n_hosts = infer_total_hosts(kv)
            rows.append(
                {
                    "family": family,
                    "scenario_base": base,
                    "scenario_name": scen,
                    "traffic_profile_id": tp_id,
                    "traffic_profile_name": tp_label,
                    "settings_file": str(out_path.relative_to(_REPO)),
                    "n_hosts": n_hosts or "",
                    "Scenario.endTime": kv.get("Scenario.endTime", ""),
                    "Group.msgTtl_minutes": profile_ttl_minutes(tp_id, base),
                }
            )
    return rows

def update_manifest(new_rows: list[dict], old_stems: list[str]) -> None:
    if not MANIFEST.is_file():
        return
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        existing = [r for r in reader if r.get("scenario_base") not in old_stems]
    new_map = {r["scenario_name"]: r for r in new_rows}
    # drop old scenario names that match old bases
    existing = [r for r in existing if not any(r.get("scenario_name", "").startswith(o) for o in old_stems)]
    merged = existing + new_rows
    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(merged)

def update_benchmark(new_rows: list[dict], old_stems: list[str]) -> None:
    if not BENCH.is_file():
        return
    with BENCH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        kept = [
            r
            for r in reader
            if not any(str(r.get("scenario_name", "")).startswith(o) for o in old_stems)
        ]
    for r in new_rows:
        kept.append(
            {
                "scenario_name": r["scenario_name"],
                "family": r["family"],
                "benchmark_split": "environmental",
                "traffic_profile_id": r["traffic_profile_id"],
                "include": "TRUE",
                "deprecated": "FALSE",
                "stress_only": "FALSE",
                "notes": "",
            }
        )
    with BENCH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(kept)

def update_base_manifest() -> None:
    bm = BASE / "manifest.csv"
    if not bm.is_file():
        return
    text = bm.read_text(encoding="utf-8")
    for old, new in OLD_TO_NEW.items():
        text = text.replace(old, new)
    bm.write_text(text, encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bases", nargs="*", default=NEW_BASES)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--keep-old-corpus", action="store_true", help="Do not delete old TP files")
    args = ap.parse_args()
    old_stems = list(OLD_TO_NEW.keys())
    if not args.keep_old_corpus and not args.dry_run:
        removed = remove_old_corpus(old_stems)
        print(f"Removed {removed} old corpus settings")
    rows = write_corpus_variants(args.bases, args.dry_run)
    if not args.dry_run:
        update_manifest(rows, old_stems)
        update_benchmark(rows, old_stems)
        update_base_manifest()
        for old in old_stems:
            for p in BASE.rglob(f"{old}.settings"):
                p.unlink()
                print(f"Removed old base {p.name}")
        build_combined_manifest_csv()
        print(f"Wrote {len(rows)} corpus settings; manifest updated")
    else:
        print(f"Dry-run: would write {len(rows)} files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())