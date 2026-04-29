#!/usr/bin/env python3
"""
Generate corpus_v2: copy corpus_v1 mobility/settings but replace traffic (Events*) and TTL (Group*.msgTtl)
with 12 reproducible traffic profiles (TP01–TP12).

Usage:
  python3 scenarios/analysis/generate_corpus_v2_traffic.py \\
    --corpus-src corpus_v1 --corpus-dst corpus_v2 \\
    --repo-root .

Pilot (only three bases × 12):
  python3 ... --pilot
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


def parse_simple_settings(text: str) -> dict:
    """Minimal line-based parser: key -> last value (strings)."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        out[key.strip()] = val.strip()
    return out


def infer_total_hosts(kv: dict[str, str]) -> int | None:
    ng_raw = kv.get("Scenario.nrofHostGroups")
    if not ng_raw:
        return None
    try:
        n_groups = int(ng_raw)
    except ValueError:
        return None
    total = 0
    any_explicit = False
    for i in range(1, n_groups + 1):
        key = f"Group{i}.nrofHosts"
        if key in kv:
            total += int(kv[key].replace(",", "").split()[0])
            any_explicit = True
        elif i == 1 and "Group.nrofHosts" in kv:
            total += int(kv["Group.nrofHosts"].replace(",", "").split()[0])
            any_explicit = True
    if total > 0:
        return total
    # Fallback: single Group.nrofHosts
    if "Group.nrofHosts" in kv:
        return int(kv["Group.nrofHosts"].replace(",", "").split()[0])
    return None


def infer_end_time(kv: dict[str, str]) -> float:
    raw = kv.get("Scenario.endTime", "43200")
    try:
        return float(raw.replace(",", "").split()[0])
    except ValueError:
        return 43200.0


def hub_exclusive_upper(n: int) -> int | None:
    """Upper bound for hub receivers [0,h); senders use [h,N). None -> use plain random traffic."""
    if n < 4:
        return None
    h = min(10, max(2, n // 8))
    if h >= n - 2:
        h = max(2, min(n // 3, 8))
    if h < 1 or (n - h) < 2:
        return None
    if h >= n:
        return None
    return h


def replace_events_block(content: str, new_block: str) -> str:
    lines = content.splitlines(keepends=True)
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("Events.nrof"):
            start = i
            break
    if start is None:
        raise ValueError("No Events.nrof block found")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        s = lines[j].strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if s.startswith("Report."):
            end = j
            break
    new_lines = lines[:start] + [new_block.rstrip() + "\n\n"] + lines[end:]
    return "".join(new_lines)


def replace_msg_ttl_lines(content: str, ttl_minutes: int) -> str:
    """Set Group.msgTtl and GroupN.msgTtl to the same profile TTL."""

    def repl(m: re.Match) -> str:
        return f"{m.group(1)} = {ttl_minutes}"

    out = re.sub(r"^(Group\d*\.msgTtl)\s*=\s*\S+", repl, content, flags=re.MULTILINE)
    return out


def ensure_msg_ttl(content: str, ttl_minutes: int) -> str:
    """Ensure TTL is set: rewrite any Group*.msgTtl; insert Group.msgTtl if missing."""
    text = replace_msg_ttl_lines(content, ttl_minutes)
    if re.search(r"^Group\.msgTtl\s*=", text, flags=re.MULTILINE):
        return text
    ins = f"Group.msgTtl = {ttl_minutes}\n\n"
    pos = text.find("Events.nrof")
    if pos >= 0:
        return text[:pos] + ins + text[pos:]
    return text.rstrip() + "\n\n" + ins


def set_scenario_name(content: str, new_scenario_name: str) -> str:
    """Replace Scenario.name line to keep generated scenarios unique in reports."""

    def repl(m: re.Match) -> str:
        return f"{m.group(1)} = {new_scenario_name}"

    # Preserve key formatting (Scenario.name vs Scenario.name =)
    return re.sub(r"^(Scenario\.name)\s*=\s*.*$", lambda m: repl(m), content, flags=re.MULTILINE)


def build_events_block(
    tp_id: str,
    n: int,
    end_t: float,
    group1_hosts: int | None = None,
    group2_hosts: int | None = None,
) -> tuple[str, dict]:
    """Return (events_text, manifest_extra)."""
    meta: dict = {"Events.nrof": "", "Events1.interval": "", "Events1.size": "", "Group.msgTtl": ""}

    def rng_hosts() -> str:
        return f"0, {n}"

    # TP01 Baseline
    if tp_id == "TP01":
        block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 60, 120
Events1.size = 50k, 150k
Events1.hosts = {rng_hosts()}
Events1.prefix = M"""
        meta.update({"Events.nrof": "1", "Events1.interval": "60, 120", "Events1.size": "50k, 150k"})
        return block, meta

    if tp_id == "TP02":
        block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 300, 600
Events1.size = 10k, 100k
Events1.hosts = {rng_hosts()}
Events1.prefix = M"""
        meta.update({"Events.nrof": "1", "Events1.interval": "300, 600", "Events1.size": "10k, 100k"})
        return block, meta

    if tp_id == "TP03":
        block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 10, 30
Events1.size = 1k, 10k
Events1.hosts = {rng_hosts()}
Events1.prefix = M"""
        meta.update({"Events.nrof": "1", "Events1.interval": "10, 30", "Events1.size": "1k, 10k"})
        return block, meta

    if tp_id == "TP04":
        block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 180, 300
Events1.size = 1M, 5M
Events1.hosts = {rng_hosts()}
Events1.prefix = M"""
        meta.update({"Events.nrof": "1", "Events1.interval": "180, 300", "Events1.size": "1M, 5M"})
        return block, meta

    if tp_id == "TP05":
        block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 60, 120
Events1.size = 10k, 100k
Events1.hosts = {rng_hosts()}
Events1.prefix = M"""
        meta.update({"Events.nrof": "1", "Events1.interval": "60, 120", "Events1.size": "10k, 100k"})
        return block, meta

    if tp_id == "TP06":
        # OneToMany (1→n): 1 sender host to (N-1) destinations
        if n < 2:
            block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 60, 120
Events1.size = 50k, 150k
Events1.hosts = {rng_hosts()}
Events1.prefix = M"""
            meta["note"] = "one2many_fallback_random_n<2"
            meta.update({"Events.nrof": "1", "Events1.interval": "60, 120", "Events1.size": "50k, 150k"})
            return block, meta

        block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 30, 60
Events1.size = 10k, 100k
Events1.hosts = 0, 1
Events1.tohosts = 1, {n}
Events1.prefix = M"""
        meta.update({"Events.nrof": "1", "Events1.interval": "30, 60", "Events1.size": "10k, 100k", "Events1.hosts": "0, 1", "Events1.tohosts": f"1, {n}"})
        return block, meta

    if tp_id == "TP07":
        t0 = int(end_t * 0.20)
        t1 = int(end_t * 0.28)
        if t1 <= t0 + 30:
            t1 = min(int(end_t * 0.95), t0 + max(120, int(end_t * 0.05)))
        block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 5, 15
Events1.size = 50k, 150k
Events1.hosts = {rng_hosts()}
Events1.time = {t0}, {t1}
Events1.prefix = M"""
        meta.update({"Events.nrof": "1", "Events1.interval": "5, 15", "Events1.time": f"{t0}, {t1}"})
        return block, meta

    if tp_id == "TP08":
        h = hub_exclusive_upper(n)
        if h is None:
            block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 30, 60
Events1.size = 50k, 150k
Events1.hosts = {rng_hosts()}
Events1.prefix = M"""
            meta["note"] = "hub_fallback_random"
        else:
            block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 30, 60
Events1.size = 50k, 150k
Events1.hosts = {h}, {n}
Events1.tohosts = 0, {h}
Events1.prefix = M"""
            meta["Events1.hosts"] = f"{h}, {n}"
            meta["Events1.tohosts"] = f"0, {h}"
        meta.update({"Events.nrof": "1", "Events1.interval": "30, 60"})
        return block, meta

    if tp_id == "TP09":
        block = f"""Events.nrof = 2
Events1.class = MessageEventGenerator
Events1.interval = 60, 120
Events1.size = 10k, 50k
Events1.hosts = {rng_hosts()}
Events1.prefix = M

Events2.class = MessageEventGenerator
Events2.interval = 300, 600
Events2.size = 1M, 5M
Events2.hosts = {rng_hosts()}
Events2.prefix = N"""
        meta.update({"Events.nrof": "2"})
        return block, meta

    if tp_id == "TP10":
        block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 5, 10
Events1.size = 100k, 500k
Events1.hosts = {rng_hosts()}
Events1.prefix = M"""
        meta.update({"Events.nrof": "1", "Events1.interval": "5, 10", "Events1.size": "100k, 500k"})
        return block, meta

    if tp_id == "TP11":
        # ManyToOne (n→1): (N-1) sender hosts to 1 sink host (0)
        if n < 2:
            block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 30, 60
Events1.size = 10k, 100k
Events1.hosts = {rng_hosts()}
Events1.prefix = M"""
            meta["note"] = "many2one_fallback_random_n<2"
            meta.update({"Events.nrof": "1", "Events1.interval": "30, 60", "Events1.size": "10k, 100k"})
            return block, meta

        block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 30, 60
Events1.size = 10k, 100k
Events1.hosts = 1, {n}
Events1.tohosts = 0, 1
Events1.prefix = M"""
        meta.update({"Events.nrof": "1", "Events1.interval": "30, 60", "Events1.size": "10k, 100k", "Events1.hosts": f"1, {n}", "Events1.tohosts": "0, 1"})
        return block, meta

    if tp_id == "TP12":
        # GroupToGroup (community A→B): use host index ranges from Group1 and Group2 sizes (if inferrable).
        if group1_hosts is None or group2_hosts is None or group1_hosts < 1 or group2_hosts < 1 or (group1_hosts + group2_hosts) > n:
            # Fallback deterministic split
            g1 = max(1, n // 2)
            g2 = n - g1
        else:
            g1 = group1_hosts
            g2 = group2_hosts

        if g2 < 1 or (g1 + g2) > n:
            block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 60, 120
Events1.size = 50k, 150k
Events1.hosts = {rng_hosts()}
Events1.prefix = M"""
            meta["note"] = "grouptogroup_fallback_random_tiny_n"
            meta.update({"Events.nrof": "1", "Events1.interval": "60, 120", "Events1.size": "50k, 150k"})
            return block, meta

        to_end = g1 + g2
        block = f"""Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 60, 120
Events1.size = 50k, 150k
Events1.hosts = 0, {g1}
Events1.tohosts = {g1}, {to_end}
Events1.prefix = M"""
        meta.update({"Events.nrof": "1", "Events1.interval": "60, 120", "Events1.size": "50k, 150k", "Events1.hosts": f"0, {g1}", "Events1.tohosts": f"{g1}, {to_end}"})
        return block, meta

    raise ValueError(tp_id)


def profile_ttl_minutes(tp_id: str) -> int:
    """TTL in minutes for Group.msgTtl (The ONE convention)."""
    return {
        "TP01": 7200,
        "TP02": 21600,
        "TP03": 7200,
        "TP04": 14400,
        "TP05": 5,
        # TP06 replaced: OneToMany (1→n) — TTL can be large (direction dominates); keep comparable to baseline.
        "TP06": 7200,
        "TP07": 7200,
        "TP08": 7200,
        "TP09": 7200,
        "TP10": 60,
        "TP11": 7200,
        "TP12": 7200,
    }[tp_id]


PROFILE_ORDER = [
    ("TP01", "Baseline"),
    ("TP02", "LowLoad"),
    ("TP03", "ManySmall"),
    ("TP04", "FewLarge"),
    ("TP05", "CriticalTTL"),
    ("TP06", "OneToMany"),
    ("TP07", "BurstWindow"),
    ("TP08", "HubTarget"),
    ("TP09", "Bimodal"),
    ("TP10", "Storm"),
    ("TP11", "ManyToOne"),
    ("TP12", "GroupToGroup"),
]

PILOT_STEMS = {
    "U1_CBD_Commuting_HelsinkiMedium",
    "R1_Rural_RandomWaypoint",
    "D2_PartitionedCity_MuleBridge",
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate corpus_v2 traffic expansion from corpus_v1.")
    ap.add_argument("--repo-root", type=str, default=None, help="Repo root (default: parent of scenarios/)")
    ap.add_argument("--corpus-src", type=str, default="corpus_v1")
    ap.add_argument("--corpus-dst", type=str, default="corpus_v2")
    ap.add_argument("--pilot", action="store_true", help="Only generate pilot bases (3×12 scenarios)")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    scenarios_dir = here.parent
    repo_root = Path(args.repo_root).resolve() if args.repo_root else scenarios_dir.parent
    src_root = scenarios_dir / args.corpus_src
    dst_root = scenarios_dir / args.corpus_dst

    if not src_root.is_dir():
        print(f"Source corpus not found: {src_root}", file=sys.stderr)
        return 1

    settings_files = sorted(src_root.glob("**/*.settings"))
    if not settings_files:
        print(f"No .settings under {src_root}", file=sys.stderr)
        return 1

    manifest_rows: list[dict] = []

    written = 0
    for src_path in settings_files:
        rel_parent = src_path.parent.relative_to(src_root)
        stem = src_path.stem
        if args.pilot and stem not in PILOT_STEMS:
            continue

        text = src_path.read_text(encoding="utf-8", errors="replace")
        kv = parse_simple_settings(text)
        scenario_name = kv.get("Scenario.name", stem)
        n_hosts = infer_total_hosts(kv)
        if n_hosts is None:
            print(f"Skip (could not infer N): {src_path}", file=sys.stderr)
            continue
        end_t = infer_end_time(kv)

        def parse_group_hosts(group_idx: int) -> int | None:
            key = f"Group{group_idx}.nrofHosts"
            if key not in kv:
                return None
            raw = kv[key]
            # Format is usually "80" or "80, ..." (we only need first int)
            try:
                return int(raw.replace(",", "").split()[0])
            except Exception:
                return None

        g1_hosts = parse_group_hosts(1)
        g2_hosts = parse_group_hosts(2)

        for tp_id, short in PROFILE_ORDER:
            ttl = profile_ttl_minutes(tp_id)
            out_name = f"{scenario_name}__{tp_id}_{short}.settings"
            out_dir = dst_root / rel_parent
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / out_name

            events_block, ev_meta = build_events_block(
                tp_id, n_hosts, end_t, group1_hosts=g1_hosts, group2_hosts=g2_hosts
            )
            try:
                new_text = replace_events_block(text, events_block)
            except ValueError as e:
                print(f"Events replace failed {src_path}: {e}", file=sys.stderr)
                return 1
            new_text = ensure_msg_ttl(new_text, ttl)

            generated_scenario_name = f"{scenario_name}__{tp_id}_{short}"
            new_text = set_scenario_name(new_text, generated_scenario_name)
            if "# Corpus v2 traffic profile" not in new_text:
                banner = (
                    f"# Corpus v2 traffic profile ({tp_id} {short}) — generated from {args.corpus_src}. "
                    f"Mobility unchanged; Events* and Group*.msgTtl overridden.\n"
                )
                new_text = banner + new_text

            out_path.write_text(new_text, encoding="utf-8")
            written += 1

            manifest_rows.append(
                {
                    "family": str(rel_parent),
                    "scenario_base": scenario_name,
                    "scenario_name": generated_scenario_name,
                    "traffic_profile_id": tp_id,
                    "traffic_profile_name": short,
                    "settings_file": str(out_path.relative_to(repo_root)),
                    "n_hosts": str(n_hosts),
                    "Scenario.endTime": str(int(end_t)),
                    "Group.msgTtl_minutes": str(ttl),
                    "Events.nrof": ev_meta.get("Events.nrof", ""),
                    "Events1.interval": ev_meta.get("Events1.interval", ""),
                    "Events1.size": ev_meta.get("Events1.size", ""),
                    "note": ev_meta.get("note", ""),
                }
            )

    dst_root.mkdir(parents=True, exist_ok=True)
    manifest_path = dst_root / "manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()) if manifest_rows else [])
        if manifest_rows:
            w.writeheader()
            w.writerows(manifest_rows)

    mode = "pilot" if args.pilot else "full"
    print(f"Done ({mode}): {written} settings written under {dst_root.relative_to(repo_root)}")
    print(f"Manifest: {manifest_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
