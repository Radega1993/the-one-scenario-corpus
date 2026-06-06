#!/usr/bin/env python3
"""Validate D8_EmergencyBackbone_IntermittentBridges smoke/full simulation results."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
REPORTS = REPO / "reports"
DATA_OUT = REPO / "scenarios/analysis/data/D8_backbone_validation.csv"
MD_OUT = REPO / "scenarios/analysis/reports/D8_backbone_validation.md"

BACKBONE_START = 21600.0
PARTITION_BOUNDARY = 40

LINE_RE = re.compile(
    r"^\s*([0-9]+(?:\.[0-9]+)?)\s+CONN\s+(\d+)\s+(\d+)\s+(up|down)(?:\s+\S+)?\s*$",
    re.I,
)

MSG_RE = {
    "sim_time": re.compile(r"^sim_time:\s*([\d.]+)"),
    "created": re.compile(r"^created:\s*(\d+)"),
    "relayed": re.compile(r"^relayed:\s*(\d+)"),
    "delivered": re.compile(r"^delivered:\s*(\d+)"),
    "delivery_prob": re.compile(r"^delivery_prob:\s*([\d.]+)"),
    "latency_avg": re.compile(r"^latency_avg:\s*([\d.]+|NaN)"),
    "overhead_ratio": re.compile(r"^overhead_ratio:\s*([\d.]+|NaN)"),
}


def is_inter_partition(a: int, b: int) -> bool:
    return (a < PARTITION_BOUNDARY) != (b < PARTITION_BOUNDARY)


def parse_connectivity(path: Path) -> dict:
    ups_before = ups_after = 0
    inter_before = inter_after = 0
    total_ups = 0
    active: dict[tuple[int, int], float] = {}
    max_inter_uptime = 0.0
    open_inter_at_end = 0

    if not path.exists():
        return {
            "total_contacts": 0,
            "contacts_before_backbone": 0,
            "contacts_after_backbone": 0,
            "inter_partition_contacts_before": 0,
            "inter_partition_contacts_after": 0,
            "max_inter_partition_uptime_s": 0.0,
            "open_inter_links_at_end": 0,
        }

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE_RE.match(raw.strip())
        if not m:
            continue
        t = float(m.group(1))
        a, b = int(m.group(2)), int(m.group(3))
        state = m.group(4).lower()
        u, v = (a, b) if a < b else (b, a)
        pair = (u, v)
        inter = is_inter_partition(u, v)

        if state == "up":
            total_ups += 1
            if t < BACKBONE_START:
                ups_before += 1
                if inter:
                    inter_before += 1
            else:
                ups_after += 1
                if inter:
                    inter_after += 1
            active[pair] = t
        else:
            t0 = active.pop(pair, None)
            if t0 is not None and inter and t >= t0:
                uptime = t - t0
                if uptime > max_inter_uptime:
                    max_inter_uptime = uptime

    for pair, t0 in active.items():
        u, v = pair
        if is_inter_partition(u, v):
            open_inter_at_end += 1
            max_inter_uptime = max(max_inter_uptime, 43200.0 - t0)

    return {
        "total_contacts": total_ups,
        "contacts_before_backbone": ups_before,
        "contacts_after_backbone": ups_after,
        "inter_partition_contacts_before": inter_before,
        "inter_partition_contacts_after": inter_after,
        "max_inter_partition_uptime_s": max_inter_uptime,
        "open_inter_links_at_end": open_inter_at_end,
    }


def parse_message_stats(path: Path) -> dict:
    out = {
        "relayed_messages": 0,
        "delivered_messages": 0,
        "delivery_ratio": 0.0,
        "latency_avg": float("nan"),
        "overhead_ratio": float("nan"),
    }
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        for key, rx in MSG_RE.items():
            m = rx.match(raw.strip())
            if m:
                val = m.group(1)
                if key in ("latency_avg", "overhead_ratio") and val == "NaN":
                    out[key] = float("nan")
                elif key == "delivery_prob":
                    out["delivery_ratio"] = float(val)
                elif key == "sim_time":
                    pass
                elif key == "relayed":
                    out["relayed_messages"] = int(val)
                elif key == "delivered":
                    out["delivered_messages"] = int(val)
                elif key in ("latency_avg", "overhead_ratio"):
                    out[key] = float(val) if val != "NaN" else float("nan")
    return out


def traffic_profile_from_name(name: str) -> str:
    m = re.search(r"__TP(\d+)_", name)
    return f"TP{m.group(1)}" if m else "base"


def validate_row(name: str, conn: dict, msg: dict) -> tuple[str, str]:
    tp = traffic_profile_from_name(name)
    notes = []

    if conn["inter_partition_contacts_before"] > 2:
        notes.append(f"pre_backbone_inter={conn['inter_partition_contacts_before']}")
    if conn["inter_partition_contacts_after"] < 10 and tp in ("base", "TP01"):
        notes.append(f"low_post_backbone_inter={conn['inter_partition_contacts_after']}")
    if conn["max_inter_partition_uptime_s"] > 900:
        notes.append(f"long_uptime={conn['max_inter_partition_uptime_s']:.0f}s")
    if conn["open_inter_links_at_end"] > 0:
        notes.append(f"open_at_end={conn['open_inter_links_at_end']}")
    if msg["relayed_messages"] == 0:
        notes.append("no_relay")
    if msg["delivered_messages"] == 0 and tp not in ("TP12",):
        notes.append("zero_delivery")

    fail = False
    if conn["inter_partition_contacts_before"] > 2:
        fail = True
    if tp in ("base", "TP01") and conn["inter_partition_contacts_after"] < 10:
        fail = True
    if conn["max_inter_partition_uptime_s"] > 900:
        fail = True
    if conn["open_inter_links_at_end"] > 0:
        fail = True
    if msg["delivered_messages"] == 0 and tp in ("TP01", "TP03", "TP07", "TP10"):
        fail = True
    if tp in ("base", "TP01") and not (0.55 <= msg["delivery_ratio"] <= 0.95):
        if msg["delivery_ratio"] < 0.55:
            notes.append(f"delivery_low={msg['delivery_ratio']:.4f}")

    status = "FAIL" if fail else "PASS"
    if not notes:
        notes.append("ok")
    return status, "; ".join(notes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenarios",
        nargs="*",
        default=None,
        help="Scenario stems (default: all D8_Emergency* in reports)",
    )
    args = parser.parse_args()

    if args.scenarios:
        stems = args.scenarios
    else:
        stems = sorted(
            p.stem.replace("_ConnectivityONEReport", "")
            for p in REPORTS.glob("D8_EmergencyBackbone_*_ConnectivityONEReport.txt")
        )
        if not stems:
            stems = sorted(
                p.stem.replace("_MessageStatsReport", "")
                for p in REPORTS.glob("D8_EmergencyBackbone_*_MessageStatsReport.txt")
            )

    rows = []
    for stem in stems:
        conn_path = REPORTS / f"{stem}_ConnectivityONEReport.txt"
        msg_path = REPORTS / f"{stem}_MessageStatsReport.txt"
        conn = parse_connectivity(conn_path)
        msg = parse_message_stats(msg_path)
        status, notes = validate_row(stem, conn, msg)
        rows.append({
            "scenario_name": stem,
            "traffic_profile": traffic_profile_from_name(stem),
            **conn,
            **msg,
            "validation_status": status,
            "notes": notes,
        })

    fieldnames = [
        "scenario_name", "traffic_profile", "total_contacts",
        "contacts_before_backbone", "contacts_after_backbone",
        "inter_partition_contacts_before", "inter_partition_contacts_after",
        "max_inter_partition_uptime_s", "relayed_messages", "delivered_messages",
        "delivery_ratio", "latency_avg", "overhead_ratio",
        "validation_status", "notes",
    ]
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    with DATA_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    n_pass = sum(1 for r in rows if r["validation_status"] == "PASS")
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D8 backbone validation",
        "",
        f"Scenarios validated: **{len(rows)}** | PASS: **{n_pass}** | FAIL: **{len(rows) - n_pass}**",
        "",
        f"Data: [`D8_backbone_validation.csv`](../data/D8_backbone_validation.csv)",
        "",
        "| Scenario | TP | Inter pre | Inter post | Delivery | Status |",
        "|----------|-----|-----------|------------|----------|--------|",
    ]
    for r in rows:
        lines.append(
            f"| `{r['scenario_name']}` | {r['traffic_profile']} | "
            f"{r['inter_partition_contacts_before']} | {r['inter_partition_contacts_after']} | "
            f"{r['delivery_ratio']:.4f} | {r['validation_status']} |"
        )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {DATA_OUT} ({len(rows)} rows, {n_pass} PASS)")
    print(f"Wrote {MD_OUT}")
    return 0 if n_pass == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
