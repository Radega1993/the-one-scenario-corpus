#!/usr/bin/env python3
"""Stratified incremental saturation for map_space_revised_v2 (geometry-only).

Protocol: scenarios/analysis/config/map_saturation_protocol_revised_v2.yaml
Does not close GMS-v1 or run SMS; emits STOP/EXPAND decision from pre-registered rules.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import yaml

_SCRIPTS = Path(__file__).resolve().parent
_PACK = _SCRIPTS.parent
_SCENARIOS = _PACK.parent
_SETUP = _SCENARIOS / "setup"
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

SCENARIOS = _SCENARIOS
DEFAULT_PROTOCOL = _PACK / "config" / "saturation_protocol.yaml"
DEFAULT_FEATURES = _PACK / "data" / "map_space_revised_v2_saturation_features.csv"
DEFAULT_FREEZE = _PACK / "data" / "map_space_revised_v2_pool_freeze.json"
DEFAULT_TRANSFORM = _PACK / "data" / "map_space_revised_v2_feature_transform.json"
DEFAULT_METRICS = _PACK / "data" / "map_space_revised_v2_saturation_metrics.csv"
DEFAULT_BANDS = _PACK / "data" / "map_space_revised_v2_saturation_bands.csv"
DEFAULT_AUDIT = _PACK / "data" / "map_space_revised_v2_saturation_audit_order.csv"
DEFAULT_DECISION = _PACK / "data" / "map_space_revised_v2_saturation_decision.json"
DEFAULT_REPORT = _PACK / "docs" / "map_space_revised_v2_saturation_report.md"
DEFAULT_FIGURES = _PACK / "figures" / "saturation"

NUMERIC_FALLBACK = [
    "world_size_x", "world_size_y", "world_area", "bbox_width", "bbox_height",
    "useful_area", "useful_area_ratio", "n_nodes", "n_edges", "total_road_length_m",
    "road_density", "avg_edge_length_m", "median_edge_length_m", "avg_degree",
    "max_degree", "dead_end_ratio", "intersection_ratio", "n_components",
    "largest_component_ratio", "bridge_edges_count", "bridge_edges_ratio",
    "articulation_points_count", "articulation_points_ratio", "graph_diameter_approx",
    "avg_shortest_path_approx", "circuity_approx", "orientation_entropy",
    "gridness_score", "corridor_score", "radial_score", "partition_score",
    "community_score", "tree_like_score",
]


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("map_saturation_protocol_revised_v2") or data


def _read_features(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _f(v: str) -> float:
    if v is None or v == "" or v == "NaN":
        return float("nan")
    return float(v)


def fit_transform(
    rows: list[dict[str, str]],
    cols: list[str],
    log1p_cols: list[str],
) -> tuple[np.ndarray, dict[str, Any], list[str]]:
    """log1p selected cols then robust (x-median)/IQR. Returns Z, params, used_cols."""
    n = len(rows)
    used = [c for c in cols if c in rows[0]]
    raw = np.zeros((n, len(used)), dtype=np.float64)
    for j, c in enumerate(used):
        for i, r in enumerate(rows):
            raw[i, j] = _f(r.get(c, ""))
    # Impute nan with column median of finite values
    for j in range(raw.shape[1]):
        col = raw[:, j]
        finite = col[np.isfinite(col)]
        fill = float(np.median(finite)) if len(finite) else 0.0
        col[~np.isfinite(col)] = fill
        raw[:, j] = col

    log_set = set(log1p_cols)
    for j, c in enumerate(used):
        if c in log_set:
            raw[:, j] = np.log1p(np.maximum(raw[:, j], 0.0))

    med = np.median(raw, axis=0)
    q1 = np.percentile(raw, 25, axis=0)
    q3 = np.percentile(raw, 75, axis=0)
    iqr = q3 - q1
    iqr[iqr < 1e-12] = 1.0
    z = (raw - med) / iqr

    # Drop near-constant columns (IQR tiny before clamp OR all equal)
    keep = []
    for j, c in enumerate(used):
        if np.nanstd(raw[:, j]) < 1e-12:
            continue
        keep.append(j)
    if not keep:
        keep = list(range(len(used)))
    z = z[:, keep]
    used_kept = [used[j] for j in keep]
    params = {
        "columns": used_kept,
        "log1p_features": [c for c in used_kept if c in log_set],
        "median": {used_kept[i]: float(med[keep[i]]) for i in range(len(keep))},
        "iqr": {used_kept[i]: float(iqr[keep[i]]) for i in range(len(keep))},
        "scaling": "robust_median_iqr",
        "n_maps": n,
        "n_dims": len(used_kept),
    }
    # Feature QA
    params["qa"] = {
        "missing_rate_pre_impute": 0.0,
        "nearly_constant_dropped": [used[j] for j in range(len(used)) if j not in keep],
        "finite_ok": bool(np.all(np.isfinite(z))),
    }
    return z, params, used_kept


def apply_transform(
    rows: list[dict[str, str]],
    transform: dict[str, Any],
) -> tuple[np.ndarray, list[str]]:
    """Apply a frozen robust transform (same median/IQR/log1p) to new feature rows."""
    used = list(transform["columns"])
    log_set = set(transform.get("log1p_features") or [])
    med = np.array([float(transform["median"][c]) for c in used], dtype=np.float64)
    iqr = np.array([float(transform["iqr"][c]) for c in used], dtype=np.float64)
    iqr[iqr < 1e-12] = 1.0
    n = len(rows)
    raw = np.zeros((n, len(used)), dtype=np.float64)
    for j, c in enumerate(used):
        for i, r in enumerate(rows):
            raw[i, j] = _f(r.get(c, ""))
        finite = raw[np.isfinite(raw[:, j]), j]
        fill = float(np.median(finite)) if len(finite) else float(med[j])
        raw[~np.isfinite(raw[:, j]), j] = fill
        if c in log_set:
            raw[:, j] = np.log1p(np.maximum(raw[:, j], 0.0))
    z = (raw - med) / iqr
    return z, used


def pairwise_l2(z: np.ndarray) -> np.ndarray:
    # (a-b)^2 = a^2 + b^2 - 2ab
    sq = np.sum(z * z, axis=1, keepdims=True)
    d2 = np.maximum(sq + sq.T - 2.0 * (z @ z.T), 0.0)
    return np.sqrt(d2)


def knn_distances(D: np.ndarray, k: int) -> np.ndarray:
    n = D.shape[0]
    out = np.zeros(n)
    for i in range(n):
        row = np.partition(D[i], min(k, n - 1))
        # skip self (0); take k-th neighbor among others
        sorted_row = np.sort(D[i])
        out[i] = sorted_row[min(k, n - 1)]
    return out


def stratified_order(
    rows: list[dict[str, str]],
    seed: int,
    cell_order: list[tuple[str, str]],
) -> list[int]:
    """Round-robin one per cell (shuffled within cell), then remaining shuffled within cells."""
    rng = np.random.default_rng(seed)
    by_cell: dict[tuple[str, str], list[int]] = defaultdict(list)
    for i, r in enumerate(rows):
        by_cell[(r.get("archetype", ""), r.get("source_type", ""))].append(i)
    for cell in by_cell:
        rng.shuffle(by_cell[cell])

    # Round-robin first pass
    order: list[int] = []
    used = set()
    pools = {c: list(idxs) for c, idxs in by_cell.items()}
    active = [c for c in cell_order if pools.get(c)]
    while active:
        next_active = []
        for c in active:
            if pools[c]:
                idx = pools[c].pop(0)
                order.append(idx)
                used.add(idx)
                if pools[c]:
                    next_active.append(c)
        active = next_active

    # Remaining: concatenate remaining pools in cell_order (already shuffled)
    for c in cell_order:
        for idx in pools.get(c, []):
            if idx not in used:
                order.append(idx)
                used.add(idx)
    # Any leftover cells not in cell_order
    for c, idxs in pools.items():
        for idx in idxs:
            if idx not in used:
                order.append(idx)
    return order


def audit_order(rows: list[dict[str, str]]) -> list[int]:
    keyed = sorted(
        range(len(rows)),
        key=lambda i: (int(rows[i].get("batch_target") or 0), rows[i].get("map_id") or ""),
    )
    return keyed


def coverage_stats(D: np.ndarray, S_idx: list[int], eps: float) -> dict[str, float]:
    """For all x in P, d(x,S); return D50/90/95/max and C(eps)."""
    if not S_idx:
        return {"D50": float("nan"), "D90": float("nan"), "D95": float("nan"), "Dmax": float("nan"), "C_eps": 0.0}
    S = np.array(S_idx, dtype=int)
    dmin = D[:, S].min(axis=1)
    return {
        "D50": float(np.percentile(dmin, 50)),
        "D90": float(np.percentile(dmin, 90)),
        "D95": float(np.percentile(dmin, 95)),
        "Dmax": float(np.max(dmin)),
        "C_eps": float(np.mean(dmin <= eps)),
    }


def novelty_block(D: np.ndarray, S_prev: list[int], block: list[int], eps: float) -> dict[str, float]:
    if not block:
        return {"nov_median": 0.0, "nov_p90": 0.0, "nov_p95": 0.0, "nov_max": 0.0, "frac_gt_eps": 0.0}
    if not S_prev:
        vals = np.full(len(block), np.inf)
    else:
        Sp = np.array(S_prev, dtype=int)
        vals = D[np.array(block), :][:, Sp].min(axis=1)
    finite = vals[np.isfinite(vals)]
    if len(finite) == 0:
        return {"nov_median": float("inf"), "nov_p90": float("inf"), "nov_p95": float("inf"), "nov_max": float("inf"), "frac_gt_eps": 1.0}
    return {
        "nov_median": float(np.median(finite)),
        "nov_p90": float(np.percentile(finite, 90)),
        "nov_p95": float(np.percentile(finite, 95)),
        "nov_max": float(np.max(finite)),
        "frac_gt_eps": float(np.mean(finite > eps)),
    }


def categorical_coverage(rows: list[dict[str, str]], idxs: list[int]) -> dict[str, Any]:
    sub = [rows[i] for i in idxs]
    archs = {r.get("archetype") for r in sub}
    srcs = {r.get("source_type") for r in sub}
    cells = {(r.get("archetype"), r.get("source_type")) for r in sub}
    return {
        "n_archetypes": len(archs),
        "n_sources": len(srcs),
        "n_cells": len(cells),
    }


def stratum_mask(rows: list[dict[str, str]], arch: str, src: str) -> np.ndarray:
    return np.array([r.get("archetype") == arch and r.get("source_type") == src for r in rows], dtype=bool)


def quantiles(vals: list[float]) -> tuple[float, float, float]:
    a = np.array(vals, dtype=float)
    a = a[np.isfinite(a)]
    if len(a) == 0:
        return float("nan"), float("nan"), float("nan")
    return float(np.percentile(a, 2.5)), float(np.median(a)), float(np.percentile(a, 97.5))


def delta_C_per_100(c_now: float, c_prev: float, n_now: int, n_prev: int) -> float:
    dn = max(n_now - n_prev, 1)
    return 100.0 * (c_now - c_prev) / dn


def _merge_stop_cfg(protocol: dict[str, Any], amendment: dict[str, Any] | None) -> dict[str, Any]:
    stop = dict(protocol.get("stop") or {})
    if not amendment:
        return stop
    am = amendment.get("map_saturation_protocol_amendment_ceiling_2000") or amendment
    am_stop = dict(am.get("stop") or {})
    stop.update(am_stop)
    stop["_amendment"] = am
    return stop


def decide(
    ladder: list[int],
    bands: list[dict[str, Any]],
    protocol: dict[str, Any],
    stratum_novelty: dict[str, list[float]],
    *,
    n_maps: int = 0,
    amendment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stop_cfg = _merge_stop_cfg(protocol, amendment)
    need = int(stop_cfg.get("consecutive_steps_required", 3))
    dC_max = float(stop_cfg.get("delta_C_per_100_max", 0.005))
    d95_rel_max = float(stop_cfg.get("d95_relative_improvement_max", 0.02))
    c_min = float(stop_cfg.get("coverage_C_eps_min", 0.98))
    d95_floor = bool(stop_cfg.get("d95_pass_if_leq_epsilon", False))
    tail = stop_cfg.get("delta_C_per_100_max_when_C_ge") or {}
    tail_C = float(tail.get("C_eps_min", 1.01)) if tail else 1.01
    tail_dC = float(tail.get("max", dC_max)) if tail else dC_max
    min_step = int(stop_cfg.get("min_step_size_for_delta_C_per_100", 1))
    use_raw_short = bool(stop_cfg.get("use_raw_delta_C_when_step_below_min", False))
    raw_dC_max = float(stop_cfg.get("raw_delta_C_max", dC_max))

    by_n = {int(b["N"]): b for b in bands}
    eps = float(bands[-1].get("eps", bands[0].get("eps", 0.0))) if bands else 0.0
    consecutive = 0
    stop_at: int | None = None
    for i in range(1, len(ladder)):
        n = ladder[i]
        n_prev = ladder[i - 1]
        b = by_n[n]
        bp = by_n[n_prev]
        c_eps = float(b.get("C_eps_median", 0.0))
        c_prev = float(bp.get("C_eps_median", 0.0))
        dC = float(b.get("delta_C_per_100_median", 1.0))
        d95 = float(b.get("D95_median", 0.0))
        d95p = float(bp.get("D95_median", d95))
        step = n - n_prev
        raw = c_eps - c_prev

        thr = tail_dC if c_eps >= tail_C else dC_max
        if use_raw_short and step < min_step:
            ok_dC = raw < raw_dC_max
        else:
            ok_dC = dC < thr

        rel = 0.0 if d95p <= 1e-12 else (d95p - d95) / d95p
        if d95_floor:
            ok_d95 = (d95 <= eps) or (rel < d95_rel_max)
        else:
            ok_d95 = rel < d95_rel_max

        ok = ok_dC and ok_d95 and (c_eps >= c_min)
        consecutive = consecutive + 1 if ok else 0
        if consecutive >= need:
            stop_at = n
            break

    # Stratum novelty: last step median novelty
    hot_strata = []
    for key, series in stratum_novelty.items():
        if series and series[-1] > float(bands[-1].get("eps", 0) or 0):
            if series[-1] > 1.5 * float(bands[-1].get("eps", 1e-9)):
                hot_strata.append(key)

    am = (amendment or {}).get("map_saturation_protocol_amendment_ceiling_2000") or amendment
    if stop_at is not None and not hot_strata:
        if am:
            decision = str((am.get("decision_if_stop") or {}).get("label") or "STOP")
            rationale = (
                f"Amended STOP met for {need} consecutive ladder steps ending at N={stop_at} "
                f"(D95 floor / tail ΔC / short-step raw ΔC). No hot critical strata. "
                f"See {am.get('diagnostics_report', 'stop diagnostics')}."
            )
        else:
            decision = "STOP"
            rationale = (
                f"Pre-registered stop met for {need} consecutive ladder steps ending at N={stop_at}; "
                "no critical strata with persistent high novelty."
            )
        expand = None
    elif stop_at is not None and hot_strata:
        decision = "TARGETED_EXPAND"
        rationale = (
            f"Global stop-like signal at N={stop_at}, but critical strata still novel: {hot_strata}."
        )
        expand = {"mode": "targeted", "cells": hot_strata}
    elif hot_strata and len(hot_strata) <= 3:
        decision = "TARGETED_EXPAND"
        rationale = f"Marginal gain persists mainly in strata: {hot_strata}."
        expand = {"mode": "targeted", "cells": hot_strata}
    else:
        # Balanced expansion ladder: 1200→1600→2000 (no auto beyond 2000).
        if n_maps >= 1800 or (ladder and int(ladder[-1]) >= 1800):
            decision = "CEILING_2000_NO_STOP"
            rationale = (
                "Planned ceiling N=2000 reached without meeting operational STOP "
                f"({need} consecutive steps with ΔC^(100)<{dC_max}, D95 rel.<{d95_rel_max}, C≥{c_min}). "
                "Do not auto-expand further; consider TARGETED_EXPAND only if strata warrant it, "
                "or revisit protocol thresholds before claiming GMS freeze."
            )
            expand = {"mode": "none_at_ceiling", "planned_ceiling": 2000}
        elif n_maps >= 1400 or (ladder and int(ladder[-1]) >= 1400):
            decision = "BALANCED_2000"
            rationale = (
                "After balanced expansion to planned N=1600, global marginal gain still above "
                "operational thresholds at full OK∩valid pool; recommend balanced expansion to "
                "planned N=2000 (protocol case4_2000)."
            )
            expand = {"mode": "balanced", "next_planned": 2000}
        else:
            decision = "BALANCED_1600"
            rationale = (
                "Global marginal gain still above operational thresholds at full OK pool; "
                "recommend balanced expansion to planned N=1600 (2000 only if gain persists)."
            )
            expand = {"mode": "balanced", "next_planned": 1600}

    gms = "freeze_candidate" if decision in ("STOP", "STOP_AMENDED_CEILING_2000") else "open"
    sms = "unblocked_after_gms_freeze" if gms == "freeze_candidate" else "blocked"
    if am and decision in ("STOP", "STOP_AMENDED_CEILING_2000"):
        di = am.get("decision_if_stop") or {}
        gms = di.get("gms_status", gms)
        sms = di.get("sms_status", sms)

    out = {
        "decision": decision,
        "rationale": rationale,
        "stop_at_N": stop_at,
        "expansion": expand,
        "gms_status": gms,
        "sms_status": sms,
        "gms_closure_language": (protocol.get("expansion") or {}).get("gms_closure_language")
        or (protocol.get("gms_closure_language") if False else None),
        "note": (
            "GMS-v1 is closed only on explicit STOP. Absolute saturation of all possible maps "
            "is not claimed."
        ),
    }
    if am:
        out["protocol_amendment"] = {
            "status": am.get("status"),
            "path": am.get("diagnostics_report"),
            "label": (am.get("decision_if_stop") or {}).get("label"),
        }
    return out


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def plot_bands(bands: list[dict[str, Any]], figures: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    figures.mkdir(parents=True, exist_ok=True)
    ns = [int(b["N"]) for b in bands]

    def band_plot(y_med, y_lo, y_hi, ylabel, fname):
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.fill_between(ns, y_lo, y_hi, alpha=0.25, label="Q2.5–Q97.5")
        ax.plot(ns, y_med, marker="o", label="median")
        ax.set_xlabel("N (OK prefix)")
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(figures / fname, dpi=120)
        plt.close(fig)

    band_plot(
        [float(b["C_eps_median"]) for b in bands],
        [float(b["C_eps_q025"]) for b in bands],
        [float(b["C_eps_q975"]) for b in bands],
        "C_N(ε)",
        "coverage_C_eps_vs_N.png",
    )
    band_plot(
        [float(b["D95_median"]) for b in bands],
        [float(b["D95_q025"]) for b in bands],
        [float(b["D95_q975"]) for b in bands],
        "D95(N)",
        "D95_vs_N.png",
    )
    band_plot(
        [float(b["delta_C_per_100_median"]) for b in bands],
        [float(b["delta_C_per_100_q025"]) for b in bands],
        [float(b["delta_C_per_100_q975"]) for b in bands],
        "ΔC^(100)",
        "delta_C_per_100_vs_N.png",
    )


def render_report(
    *,
    protocol: dict[str, Any],
    transform: dict[str, Any],
    bands: list[dict[str, Any]],
    audit: list[dict[str, Any]],
    decision: dict[str, Any],
    eps: float,
    n_maps: int,
    R: int,
) -> str:
    lines = [
        "# Stratified saturation report — map_space_revised_v2",
        "",
        "**Role:** empirical saturation analysis under a pre-registered protocol.",
        "**GMS-v1:** not closed unless decision is STOP.",
        "**SMS-v1:** blocked until GMS freeze.",
        "",
        f"- Pool OK maps analysed: **{n_maps}**",
        f"- Permutations R: **{R}** (stratified nested round-robin)",
        f"- Geometry dims: **{transform.get('n_dims')}** (no source_type one-hot)",
        f"- ε (20th pct of 5-NN distances on full pool): **{eps:.6f}**",
        f"- Decision: **`{decision.get('decision')}`**",
        "",
        "## Protocol (frozen)",
        "",
        f"- Config: `scenarios/Generated_Map_Space_v1/config/saturation_protocol.yaml`",
        f"- Freeze: `scenarios/Generated_Map_Space_v1/data/map_space_revised_v2_pool_freeze.json`",
        f"- Transform: `scenarios/Generated_Map_Space_v1/data/map_space_revised_v2_feature_transform_freeze_n1117.json` (applied; ε recomputed on current pool)",
        f"- Figures: `scenarios/Generated_Map_Space_v1/figures/saturation/`",
        "",
        "## Primary curves (median over R; bands Q2.5–Q97.5)",
        "",
        "| N | C(ε) med | C q025 | C q975 | D95 med | ΔC^(100) med | n_arch med | n_cells med |",
        "|--:|---------:|-------:|-------:|--------:|-------------:|-----------:|------------:|",
    ]
    for b in bands:
        lines.append(
            f"| {b['N']} | {float(b['C_eps_median']):.4f} | {float(b['C_eps_q025']):.4f} | "
            f"{float(b['C_eps_q975']):.4f} | {float(b['D95_median']):.4f} | "
            f"{float(b['delta_C_per_100_median']):.4f} | {b['n_archetypes_median']} | {b['n_cells_median']} |"
        )
    lines += [
        "",
        "Categorical coverage (archetypes/cells) is a **design condition**, not primary saturation evidence.",
        "",
        "## Audit order (batch_target → map_id) — not primary",
        "",
        "| N | C(ε) | D95 | n_arch | n_cells |",
        "|--:|-----:|----:|-------:|--------:|",
    ]
    for a in audit:
        lines.append(
            f"| {a['N']} | {float(a['C_eps']):.4f} | {float(a['D95']):.4f} | "
            f"{a['n_archetypes']} | {a['n_cells']} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        f"**`{decision.get('decision')}`** — {decision.get('rationale')}",
        "",
        f"- gms_status: `{decision.get('gms_status')}`",
        f"- sms_status: `{decision.get('sms_status')}`",
        "",
        "Defendable closure language (only if STOP):",
        "",
        "> The configured map-generation design space reached empirical saturation under the "
        "declared generator families, parameter ranges, source allocation policy, feature "
        "representation, and operational stopping criteria.",
        "",
        "## Deferred",
        "",
        "- PCA as primary deliverable",
        "- Separability analysis",
        "- Actual expansion execution (recommendation only in decision.json)",
        "- SMS-v1 selection",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    ap.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    ap.add_argument("--freeze", type=Path, default=DEFAULT_FREEZE)
    ap.add_argument("--transform-out", type=Path, default=DEFAULT_TRANSFORM)
    ap.add_argument(
        "--transform-in",
        type=Path,
        default=None,
        help="Reuse a frozen feature transform (median/IQR/log1p); do not refit. "
        "Epsilon is still computed on the current full pool under that transform.",
    )
    ap.add_argument("--metrics-out", type=Path, default=DEFAULT_METRICS)
    ap.add_argument("--bands-out", type=Path, default=DEFAULT_BANDS)
    ap.add_argument("--audit-out", type=Path, default=DEFAULT_AUDIT)
    ap.add_argument("--decision-out", type=Path, default=DEFAULT_DECISION)
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    ap.add_argument("--figures", type=Path, default=DEFAULT_FIGURES)
    ap.add_argument("--R", type=int, default=None, help="Override permutations (default from protocol)")
    ap.add_argument(
        "--amendment",
        type=Path,
        default=None,
        help="Optional post-hoc STOP amendment YAML (e.g. saturation_protocol_amendment_ceiling_2000.yaml).",
    )
    ap.add_argument(
        "--redecide-from-bands",
        action="store_true",
        help="Skip R permutations; re-apply decide() on existing bands CSV (+ optional --amendment).",
    )
    args = ap.parse_args()

    if args.redecide_from_bands:
        import yaml as _yaml

        protocol = _load_yaml(args.protocol)
        amendment = None
        if args.amendment is not None:
            amendment = _yaml.safe_load(args.amendment.read_text(encoding="utf-8"))
        bands = list(_read_features(args.bands_out) if False else [])
        with args.bands_out.open(encoding="utf-8") as f:
            bands = list(csv.DictReader(f))
        if not bands:
            raise SystemExit(f"No bands in {args.bands_out}")
        ladder = [int(float(b["N"])) for b in bands]
        critical = [
            (s["archetype"], s["source_type"])
            for s in (protocol.get("stop") or {}).get("critical_strata") or []
        ]
        stratum_nov_series = {f"{a}|{s}": [0.0] * len(bands) for a, s in critical}
        n_maps = int(float(bands[-1]["N"]))
        decision = decide(
            ladder, bands, protocol, stratum_nov_series, n_maps=n_maps, amendment=amendment
        )
        decision["epsilon"] = float(bands[0].get("eps", 0.0))
        decision["R"] = int(float(bands[0].get("R", 0) or 0))
        decision["n_maps"] = n_maps
        decision["protocol"] = str(args.protocol)
        if args.amendment is not None:
            decision["protocol_amendment_path"] = str(args.amendment)
        args.decision_out.parent.mkdir(parents=True, exist_ok=True)
        args.decision_out.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
        print(f"Decision: {decision['decision']}")
        print(f"stop_at_N={decision.get('stop_at_N')} gms={decision.get('gms_status')}")
        print(f"Decision JSON: {args.decision_out}")
        return

    protocol = _load_yaml(args.protocol)
    amendment = None
    if args.amendment is not None:
        import yaml as _yaml

        amendment = _yaml.safe_load(args.amendment.read_text(encoding="utf-8"))
    feats_cfg = protocol.get("features") or {}
    cols = list(feats_cfg.get("numeric_feature_columns") or NUMERIC_FALLBACK)
    # dedupe accidental duplicates in YAML
    seen = set()
    cols = [c for c in cols if not (c in seen or seen.add(c))]
    log1p_cols = list(feats_cfg.get("log1p_features") or [])
    ladder = [int(x) for x in (protocol.get("ladder") or [])]
    perm_cfg = protocol.get("permutations") or {}
    R = int(args.R if args.R is not None else perm_cfg.get("R", 100))
    seed_base = int(perm_cfg.get("seed_base", 42))
    eps_cfg = protocol.get("epsilon") or {}
    knn_k = int(eps_cfg.get("knn_k", 5))
    eps_pct = float(eps_cfg.get("percentile", 20))

    rows = _read_features(args.features)
    if not rows:
        raise SystemExit(f"No feature rows in {args.features}")

    if args.transform_in is not None:
        frozen = json.loads(args.transform_in.read_text(encoding="utf-8"))
        z, used_cols = apply_transform(rows, frozen)
        transform = dict(frozen)
        transform["n_maps"] = len(rows)
        transform["n_dims"] = len(used_cols)
        transform["reused_from"] = str(args.transform_in)
        transform["fit_mode"] = "frozen_apply"
    else:
        z, transform, used_cols = fit_transform(rows, cols, log1p_cols)
        transform["fit_mode"] = "fit_on_current_pool"

    D = pairwise_l2(z)
    knn = knn_distances(D, knn_k)
    eps = float(np.percentile(knn, eps_pct))
    transform["epsilon"] = eps
    transform["epsilon_rule"] = eps_cfg.get("rule")
    transform["knn_k"] = knn_k
    transform["epsilon_percentile"] = eps_pct
    # When reusing a freeze, write a companion artifact; keep the freeze file intact.
    out_tf = args.transform_out
    if args.transform_in is not None:
        out_tf = args.transform_out.with_name(
            args.transform_out.stem + "_applied_n" + str(len(rows)) + args.transform_out.suffix
        )
    out_tf.parent.mkdir(parents=True, exist_ok=True)
    out_tf.write_text(json.dumps(transform, indent=2) + "\n", encoding="utf-8")
    transform["artifact_path"] = str(out_tf)

    # Canonical cell order
    cells = sorted({(r.get("archetype", ""), r.get("source_type", "")) for r in rows})
    critical = [
        (s["archetype"], s["source_type"])
        for s in (protocol.get("stop") or {}).get("critical_strata") or []
    ]

    # --- Stratified permutations ---
    per_N: dict[int, list[dict[str, float]]] = {n: [] for n in ladder}
    stratum_nov_series: dict[str, list[float]] = {f"{a}|{s}": [] for a, s in critical}

    for r in range(R):
        order = stratified_order(rows, seed_base + r, cells)
        prev_n = 0
        prev_C = 0.0
        for n in ladder:
            n_eff = min(n, len(order))
            S = order[:n_eff]
            block = order[prev_n:n_eff]
            cov = coverage_stats(D, S, eps)
            nov = novelty_block(D, order[:prev_n], block, eps)
            cat = categorical_coverage(rows, S)
            dC = delta_C_per_100(cov["C_eps"], prev_C, n_eff, prev_n) if prev_n else float("nan")
            rec = {
                **cov,
                **nov,
                **{f"cat_{k}": v for k, v in cat.items()},
                "delta_C_per_100": dC,
                "N_eff": n_eff,
            }
            # stratum coverage for critical cells
            for a, s in critical:
                mask = stratum_mask(rows, a, s)
                idxs = np.where(mask)[0]
                if len(idxs) == 0:
                    rec[f"C_eps_{a}|{s}"] = float("nan")
                else:
                    Sarr = np.array(S, dtype=int)
                    dmin = D[np.ix_(idxs, Sarr)].min(axis=1)
                    rec[f"C_eps_{a}|{s}"] = float(np.mean(dmin <= eps))
                # novelty of block members in stratum
                block_in = [i for i in block if rows[i].get("archetype") == a and rows[i].get("source_type") == s]
                if block_in and prev_n > 0:
                    nv = novelty_block(D, order[:prev_n], block_in, eps)
                    key = f"{a}|{s}"
                    # store last-step later; accumulate mean novelty per step across R at end
                    rec[f"nov_{key}"] = nv["nov_median"]
                else:
                    rec[f"nov_{a}|{s}"] = 0.0
            per_N[n].append(rec)
            prev_C = cov["C_eps"]
            prev_n = n_eff

    # Aggregate bands
    bands: list[dict[str, Any]] = []
    for n in ladder:
        samples = per_N[n]
        def col(name: str) -> list[float]:
            return [float(s.get(name, float("nan"))) for s in samples]

        c_lo, c_med, c_hi = quantiles(col("C_eps"))
        d_lo, d_med, d_hi = quantiles(col("D95"))
        dc_lo, dc_med, dc_hi = quantiles(col("delta_C_per_100"))
        bands.append(
            {
                "N": n,
                "eps": eps,
                "C_eps_q025": c_lo,
                "C_eps_median": c_med,
                "C_eps_q975": c_hi,
                "D50_median": quantiles(col("D50"))[1],
                "D90_median": quantiles(col("D90"))[1],
                "D95_q025": d_lo,
                "D95_median": d_med,
                "D95_q975": d_hi,
                "Dmax_median": quantiles(col("Dmax"))[1],
                "delta_C_per_100_q025": dc_lo,
                "delta_C_per_100_median": dc_med,
                "delta_C_per_100_q975": dc_hi,
                "nov_median_median": quantiles(col("nov_median"))[1],
                "nov_p95_median": quantiles(col("nov_p95"))[1],
                "n_archetypes_median": quantiles(col("cat_n_archetypes"))[1],
                "n_cells_median": quantiles(col("cat_n_cells"))[1],
                "R": R,
            }
        )
        for a, s in critical:
            key = f"{a}|{s}"
            stratum_nov_series[key].append(quantiles(col(f"nov_{key}"))[1])

    # Audit order
    aord = audit_order(rows)
    audit_rows: list[dict[str, Any]] = []
    prev_n = 0
    prev_C = 0.0
    for n in ladder:
        n_eff = min(n, len(aord))
        S = aord[:n_eff]
        cov = coverage_stats(D, S, eps)
        cat = categorical_coverage(rows, S)
        dC = delta_C_per_100(cov["C_eps"], prev_C, n_eff, prev_n) if prev_n else float("nan")
        audit_rows.append(
            {
                "N": n,
                "C_eps": cov["C_eps"],
                "D95": cov["D95"],
                "D50": cov["D50"],
                "delta_C_per_100": dC,
                "n_archetypes": cat["n_archetypes"],
                "n_cells": cat["n_cells"],
                "order": "batch_target_then_map_id",
            }
        )
        prev_C = cov["C_eps"]
        prev_n = n_eff

    decision = decide(
        ladder, bands, protocol, stratum_nov_series, n_maps=len(rows), amendment=amendment
    )
    decision["epsilon"] = eps
    decision["R"] = R
    decision["n_maps"] = len(rows)
    decision["protocol"] = str(args.protocol)
    decision["features"] = str(args.features)
    if protocol.get("gms_closure_language"):
        decision["gms_closure_language"] = protocol["gms_closure_language"]
    else:
        decision["gms_closure_language"] = (
            "The configured map-generation design space reached empirical saturation under the "
            "declared generator families, parameter ranges, source allocation policy, feature "
            "representation, and operational stopping criteria."
        )

    write_csv(
        args.bands_out,
        bands,
        list(bands[0].keys()) if bands else ["N"],
    )
    write_csv(
        args.audit_out,
        audit_rows,
        list(audit_rows[0].keys()) if audit_rows else ["N"],
    )
    # Flatten per-permutation metrics (sample: store medians already in bands; write summary metrics)
    write_csv(args.metrics_out, bands, list(bands[0].keys()) if bands else ["N"])

    args.decision_out.parent.mkdir(parents=True, exist_ok=True)
    args.decision_out.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")

    plot_bands(bands, args.figures)
    report = render_report(
        protocol=protocol,
        transform=transform,
        bands=bands,
        audit=audit_rows,
        decision=decision,
        eps=eps,
        n_maps=len(rows),
        R=R,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")

    print(f"Decision: {decision['decision']}")
    print(f"eps={eps:.6f} dims={transform['n_dims']} R={R} n={len(rows)}")
    print(f"Report: {args.report}")
    print(f"Decision JSON: {args.decision_out}")


if __name__ == "__main__":
    main()
