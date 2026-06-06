#!/usr/bin/env python3
"""Regenerate D8 corpus TP01-TP12 from base scenario with preserved backbone events."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scenarios" / "analysis" / "lib"))

from traffic_profile_generator import (  # noqa: E402
    PROFILE_ORDER,
    append_external_events_queue,
    build_events_block,
    ensure_msg_ttl,
    infer_end_time,
    infer_total_hosts,
    parse_simple_settings,
    profile_ttl_minutes,
    set_scenario_name,
)

BASE = REPO / "scenarios/base_scenarios/05_disaster/D8_EmergencyBackbone_IntermittentBridges.settings"
OUT_DIR = REPO / "scenarios/corpus_v1/05_disaster"
EVENTS_FILE = "scenarios/corpus_v1/05_disaster/D8_emergency_backbone_events.txt"
SCENARIO_BASE = "D8_EmergencyBackbone_IntermittentBridges"


def regenerate() -> int:
    if not BASE.is_file():
        raise SystemExit(f"Missing base: {BASE}")

    base_text = BASE.read_text(encoding="utf-8")
    kv = parse_simple_settings(base_text)
    n_hosts = infer_total_hosts(kv) or 80
    end_t = infer_end_time(kv)
    g1 = int(kv.get("Group1.nrofHosts", "40"))
    g2 = int(kv.get("Group2.nrofHosts", "40"))

    # Remove old D8 corpus settings only (keep events .txt)
    for old in OUT_DIR.glob("D8_*.settings"):
        old.unlink()

    n = 0
    for tp_id, tp_label in PROFILE_ORDER:
        scenario_name = f"{SCENARIO_BASE}__{tp_id}_{tp_label}"
        out_path = OUT_DIR / f"{scenario_name}.settings"

        text = base_text
        text = set_scenario_name(text, scenario_name)
        ttl = profile_ttl_minutes(tp_id, SCENARIO_BASE)
        text = ensure_msg_ttl(text, ttl)

        events_block, _meta = build_events_block(
            tp_id, n_hosts, end_t, group1_hosts=g1, group2_hosts=g2
        )
        text = append_external_events_queue(text, events_block, EVENTS_FILE)

        header = (
            f"# Corpus v1 traffic profile ({tp_id} {tp_label}) — generated from base.\n"
            f"# Mobility and backbone events unchanged; Events1* and Group.msgTtl overridden.\n"
        )
        if not text.startswith("# Corpus"):
            text = header + text
        else:
            text = re.sub(r"^#.*\n", header, text, count=1)

        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {out_path.relative_to(REPO)}")
        n += 1

    print(f"Done: {n} settings in {OUT_DIR.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(regenerate())
