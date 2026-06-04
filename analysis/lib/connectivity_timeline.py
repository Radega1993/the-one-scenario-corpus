#!/usr/bin/env python3
"""
Parse ConnectivityONEReport traces and derive useful-simulation-time metrics.

Format: "<time> CONN <host_a> <host_b> up|down"
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

LINE_RE = re.compile(
    r"^\s*([0-9]+(?:\.[0-9]+)?)\s+CONN\s+(\d+)\s+(\d+)\s+(up|down)\s*$",
    re.I,
)

def parse_connectivity_timeline(
    path: Path,
    end_time: float,
    n_hosts: int | None = None,
) -> dict[str, Any]:
    """
    Build connectivity timeline metrics from a ConnectivityONEReport file.

    Returns dict with scalar metrics and optional empty flag when no events.
    """
    active: dict[tuple[int, int], float] = {}
    last_down: dict[tuple[int, int], float] = {}

    encounter_events = 0
    contact_time_sum = 0.0
    intercontact_sum = 0.0
    intercontact_n = 0

    all_nodes: set[int] = set()
    node_neighbors: dict[int, set[int]] = defaultdict(set)
    node_first_contact: dict[int, float] = {}
    pairs_ever: set[tuple[int, int]] = set()

    event_times: list[float] = []
    first_contact_time = float("nan")
    last_event_time = float("nan")

    if not path.exists() or path.stat().st_size == 0:
        return _empty_result(end_time, n_hosts)

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE_RE.match(raw.strip())
        if not m:
            continue
        t = float(m.group(1))
        a, b = int(m.group(2)), int(m.group(3))
        state = m.group(4).lower()
        if a == b:
            continue
        u, v = (a, b) if a < b else (b, a)
        pair = (u, v)
        all_nodes.add(u)
        all_nodes.add(v)
        event_times.append(t)
        if state == "up":
            encounter_events += 1
            pairs_ever.add(pair)
            for node in (u, v):
                if node not in node_first_contact:
                    node_first_contact[node] = t
                node_neighbors[node].add(u if node == v else v)
            if pair in last_down and t >= last_down[pair]:
                intercontact_sum += t - last_down[pair]
                intercontact_n += 1
            active[pair] = t
        else:
            t0 = active.pop(pair, None)
            if t0 is not None and t >= t0:
                contact_time_sum += t - t0
            last_down[pair] = t

    if not event_times:
        return _empty_result(end_time, n_hosts)

    first_contact_time = min(event_times)
    last_event_time = max(event_times)
    last_contact_time = last_event_time  # last up or down in trace

    n_trace = len(all_nodes)
    n_denom = n_hosts if n_hosts and n_hosts > 0 else n_trace
    nodes_ever = set(node_first_contact.keys())
    pct_nodes_ever = (len(nodes_ever) / n_denom) if n_denom > 0 else float("nan")

    if n_trace > 1:
        ratio_contact_nodes = float(
            sum(len(node_neighbors.get(n, set())) for n in all_nodes) / (n_trace * (n_trace - 1))
        )
    else:
        ratio_contact_nodes = 0.0

    contact_time_per_min = (
        float(encounter_events / (end_time / 60.0)) if end_time > 0 and encounter_events > 0 else 0.0
    )
    closed_contact_per_min = (
        float(contact_time_sum / (end_time / 60.0)) if end_time > 0 and contact_time_sum > 0 else 0.0
    )

    # Time to reach X% of nodes that eventually participate in >=1 contact
    targets = _time_to_pct_contact_nodes(node_first_contact, nodes_ever, n_denom, (0.5, 0.8, 0.9))

    # Pair-coverage proxy for spatial exploration (no GPS in pipeline)
    max_pairs = (n_denom * (n_denom - 1) / 2) if n_denom > 1 else 1
    pair_coverage_final = len(pairs_ever) / max_pairs if max_pairs > 0 else 0.0
    time_to_90pct_pairs = _time_to_pct_pairs(path, pairs_ever, n_denom, end_time, 0.9)

    # Useful time: through 90% node exploration and last observed contact activity
    t90 = targets.get("time_to_90pct_contact_nodes", float("nan"))
    if encounter_events == 0:
        useful_time = 0.0
    elif t90 == t90:  # not NaN
        useful_time = min(end_time, max(t90, last_contact_time))
    else:
        useful_time = min(end_time, last_contact_time)

    first_contact_median = _median(list(node_first_contact.values()))

    return {
        "n_nodes_trace": n_trace,
        "n_hosts_denom": n_denom,
        "first_contact_time": first_contact_time,
        "last_contact_time": last_contact_time,
        "total_encounters": float(encounter_events),
        "contact_time_sum_s": contact_time_sum,
        "contact_time_per_min": contact_time_per_min,
        "closed_contact_time_per_min": closed_contact_per_min,
        "ratio_contact_nodes": ratio_contact_nodes,
        "pct_nodes_ever_contacted": pct_nodes_ever * 100.0,
        "time_to_50pct_contact_nodes": targets.get("time_to_50pct_contact_nodes", float("nan")),
        "time_to_80pct_contact_nodes": targets.get("time_to_80pct_contact_nodes", float("nan")),
        "time_to_90pct_contact_nodes": t90,
        "first_contact_time_median": first_contact_median,
        "pair_coverage_final_pct": pair_coverage_final * 100.0,
        "time_to_90pct_pair_coverage": time_to_90pct_pairs,
        "useful_time_recommendation": useful_time,
        "useful_time_ratio": (useful_time / end_time) if end_time > 0 else float("nan"),
        "tail_time_s": end_time - useful_time if end_time > 0 else float("nan"),
        "tail_time_ratio": ((end_time - useful_time) / end_time) if end_time > 0 else float("nan"),
    }

def _empty_result(end_time: float, n_hosts: int | None) -> dict[str, Any]:
    nan = float("nan")
    return {
        "n_nodes_trace": 0,
        "n_hosts_denom": n_hosts or 0,
        "first_contact_time": nan,
        "last_contact_time": nan,
        "total_encounters": 0.0,
        "contact_time_sum_s": 0.0,
        "contact_time_per_min": 0.0,
        "closed_contact_time_per_min": 0.0,
        "ratio_contact_nodes": 0.0,
        "pct_nodes_ever_contacted": 0.0,
        "time_to_50pct_contact_nodes": nan,
        "time_to_80pct_contact_nodes": nan,
        "time_to_90pct_contact_nodes": nan,
        "first_contact_time_median": nan,
        "pair_coverage_final_pct": 0.0,
        "time_to_90pct_pair_coverage": nan,
        "useful_time_recommendation": 0.0,
        "useful_time_ratio": 0.0,
        "tail_time_s": end_time,
        "tail_time_ratio": 1.0 if end_time > 0 else nan,
    }

def _median(vals: list[float]) -> float:
    if not vals:
        return float("nan")
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    if n % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0

def _time_to_pct_contact_nodes(
    node_first: dict[int, float],
    nodes_ever: set[int],
    n_denom: int,
    pcts: tuple[float, ...],
) -> dict[str, float]:
    out: dict[str, float] = {}
    if not node_first or n_denom <= 0:
        for p in pcts:
            out[f"time_to_{int(p * 100)}pct_contact_nodes"] = float("nan")
        return out

    ordered_times = sorted(node_first.values())
    for p in pcts:
        key = f"time_to_{int(p * 100)}pct_contact_nodes"
        need = max(1, int(math.ceil(p * n_denom)))
        if len(ordered_times) >= need:
            out[key] = ordered_times[need - 1]
        else:
            out[key] = float("nan")
    return out

def _time_to_pct_pairs(
    path: Path,
    pairs_final: set[tuple[int, int]],
    n_denom: int,
    end_time: float,
    pct: float,
) -> float:
    """First time cumulative unique pair count reaches pct of final pairs observed."""
    if not pairs_final or n_denom <= 1:
        return float("nan")
    target = max(1, int(math.ceil(pct * len(pairs_final))))
    seen: set[tuple[int, int]] = set()
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE_RE.match(raw.strip())
        if not m or m.group(4).lower() != "up":
            continue
        a, b = int(m.group(2)), int(m.group(3))
        if a == b:
            continue
        pair = (a, b) if a < b else (b, a)
        seen.add(pair)
        if len(seen) >= target:
            return float(m.group(1))
    return float("nan")

def classify_useful_time(
    metrics: dict[str, Any],
    end_time: float,
) -> str:
    enc = metrics.get("total_encounters", 0) or 0
    pct_nodes = metrics.get("pct_nodes_ever_contacted", 0) or 0
    t90 = metrics.get("time_to_90pct_contact_nodes", float("nan"))
    tail_ratio = metrics.get("tail_time_ratio", float("nan"))

    if enc == 0:
        return "disconnected"
    if pct_nodes < 15.0:
        return "marginal_connectivity"
    if t90 == t90 and end_time > 0 and t90 > 0.9 * end_time:
        return "late_exploration"
    if t90 == t90 and end_time > 0 and t90 < 0.4 * end_time and tail_ratio > 0.5:
        return "early_saturation_long_tail"
    if enc >= 100 and pct_nodes >= 30.0:
        return "sufficient_activity"
    return "moderate_activity"