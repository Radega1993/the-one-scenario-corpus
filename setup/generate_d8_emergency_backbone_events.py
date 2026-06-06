#!/usr/bin/env python3
"""Generate intermittent bb0 backbone CONN events for D8_EmergencyBackbone_IntermittentBridges."""

from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "scenarios/corpus_v1/05_disaster/D8_emergency_backbone_events.txt"

BACKBONE_START = 21600
SIM_END = 43200
WINDOW_DURATION = 600
GAP_BETWEEN_WINDOWS = 1200
INTERFACE = "bb0"

# Gateway hosts: partition A (0-39), partition B (40-79)
PAIRS = [
    (0, 40),
    (5, 45),
    (10, 50),
    (15, 55),
    (0, 50),
    (10, 40),
]


def generate_events(
    start: int = BACKBONE_START,
    end: int = SIM_END,
    window: int = WINDOW_DURATION,
    gap: int = GAP_BETWEEN_WINDOWS,
) -> list[str]:
    lines = [
        "# D8 emergency backbone — intermittent bb0 links (StandardEventsReader)",
        "# Format: time CONN host1 host2 up|down bb0",
        "# Partition A: hosts 0-39; partition B: hosts 40-79",
        f"# Windows: {window}s up, {gap}s gap, rotating gateway pairs from t={start}",
        "",
    ]
    t = start
    pair_idx = 0
    while t + window <= end:
        ha, hb = PAIRS[pair_idx % len(PAIRS)]
        lines.append(f"{t} CONN {ha} {hb} up {INTERFACE}")
        lines.append(f"{t + window} CONN {ha} {hb} down {INTERFACE}")
        t += window + gap
        pair_idx += 1
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--start", type=int, default=BACKBONE_START)
    parser.add_argument("--end", type=int, default=SIM_END)
    parser.add_argument("--window", type=int, default=WINDOW_DURATION)
    parser.add_argument("--gap", type=int, default=GAP_BETWEEN_WINDOWS)
    args = parser.parse_args()

    lines = generate_events(args.start, args.end, args.window, args.gap)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    n_events = sum(1 for ln in lines if ln and not ln.startswith("#"))
    print(f"Wrote {n_events} events to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
