#!/usr/bin/env python3
"""Audit the official map selection pool (@1200 valid maps)."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_selection_v1_common import (  # noqa: E402
    DEFAULT_FEATURES,
    DEFAULT_MANIFEST,
    DEFAULT_POOL_CSV,
    DEFAULT_VALIDATION,
    OFFICIAL_MAX_BATCH,
    SCENARIOS_DIR,
    load_official_pool,
)

REPORT_PATH = SCENARIOS_DIR / "analysis" / "reports" / "map_selection_pool_v1_audit.md"
DECISION_PATH = SCENARIOS_DIR / "analysis" / "data" / "map_space_saturation_decision.json"
EXPECTED_POOL_SIZE = 1055


def main() -> None:
    pool = load_official_pool(DEFAULT_MANIFEST, DEFAULT_VALIDATION, DEFAULT_FEATURES, OFFICIAL_MAX_BATCH)
    n = len(pool)
    pool.to_csv(DEFAULT_POOL_CSV, index=False)

    features_all = pd.read_csv(DEFAULT_FEATURES)
    validation = pd.read_csv(DEFAULT_VALIDATION)
    manifest = pd.read_csv(DEFAULT_MANIFEST)

    ext_pool = features_all.merge(validation[["map_id", "status"]], on="map_id", how="left")
    ext_pool = ext_pool[ext_pool["batch_target"] <= 2000]
    ext_valid = ext_pool[ext_pool["status"].isin({"PASS", "WARNING", "STRESS"})]
    ext_only = ext_valid[ext_valid["batch_target"] > OFFICIAL_MAX_BATCH]

    excluded_fail = features_all.merge(validation[["map_id", "status"]], on="map_id", how="left")
    excluded_fail = excluded_fail[
        (excluded_fail["batch_target"] <= OFFICIAL_MAX_BATCH) & (excluded_fail["status"] == "FAIL")
    ]

    arch_tbl = pool["archetype"].value_counts().sort_index()
    st_tbl = pool["source_type"].value_counts()
    anchor_tbl = (
        pool[pool["anchor_id"].notna() & (pool["anchor_id"] != "")]["anchor_id"].value_counts().sort_index()
    )
    status_tbl = pool["validation_status"].value_counts()

    decision_note = ""
    if DECISION_PATH.exists():
        import json

        doc = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        decision_note = doc.get("decision", "unknown")

    lines = [
        "# Map selection pool audit (v1)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## 1. Pool definition",
        "",
        f"- **Official selection pool:** `batch_target <= {OFFICIAL_MAX_BATCH}` and validation in PASS/WARNING/STRESS.",
        f"- **Pool size:** {n} maps (expected ~{EXPECTED_POOL_SIZE}).",
        f"- **Phase 1 saturation decision:** `{decision_note}`.",
        "",
        "### Why 1200 and not 2000?",
        "",
        "Phase 1 extended generation to 2000 candidates as a **robustness check**, not as the design pool.",
        "The decision `stop_at_1200_confirmed_by_2000` confirms that saturation metrics stabilised before 1200;",
        "maps added only in batches 1600–2000 are excluded from representative selection to avoid",
        "contaminating the official design space with post-saturation redundancy.",
        "",
        f"- Valid maps @2000 (reference): {len(ext_valid)}",
        f"- Valid maps added post-1200 only: {len(ext_only)}",
        f"- Excluded from pool (FAIL @≤1200): {len(excluded_fail)}",
        "",
        "## 2. Coverage summary",
        "",
        f"- Archetypes: **{pool['archetype'].nunique()}/15**",
        f"- Source types: **{pool['source_type'].nunique()}/3** ({', '.join(f'{k}={v}' for k, v in st_tbl.items())})",
        f"- Documented anchors present: **{len(anchor_tbl)}**",
        "",
        "## 3. Validation status",
        "",
        "| status | count |",
        "|--------|------:|",
    ]
    for status, cnt in status_tbl.items():
        lines.append(f"| {status} | {cnt} |")
    lines.extend(
        [
            "",
            "WARNING and STRESS maps are **included** because they remain structurally usable for scenario design;",
            "FAIL maps are excluded.",
            "",
            "## 4. Archetype distribution",
            "",
            "| archetype | count |",
            "|-----------|------:|",
        ]
    )
    for arch, cnt in arch_tbl.items():
        lines.append(f"| {arch} | {cnt} |")

    lines.extend(["", "## 5. Source type distribution", "", "| source_type | count |", "|-------------|------:|"])
    for st, cnt in st_tbl.items():
        lines.append(f"| {st} | {cnt} |")

    lines.extend(["", "## 6. Anchor distribution", "", "| anchor_id | count |", "|-----------|------:|"])
    for aid, cnt in anchor_tbl.items():
        lines.append(f"| {aid} | {cnt} |")

    lines.extend(
        [
            "",
            "## 7. Excluded maps",
            "",
            f"- FAIL with batch ≤ {OFFICIAL_MAX_BATCH}: {len(excluded_fail)}",
            f"- Valid maps only in extension batches (>1200): {len(ext_only)} (reference only)",
            "",
            "## 8. Output",
            "",
            f"- Pool CSV: `{DEFAULT_POOL_CSV.relative_to(SCENARIOS_DIR.parent)}`",
        ]
    )

    if n != EXPECTED_POOL_SIZE:
        lines.extend(
            [
                "",
                f"> **Note:** pool size {n} differs from expected {EXPECTED_POOL_SIZE} by {n - EXPECTED_POOL_SIZE}.",
            ]
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Pool: {n} maps -> {DEFAULT_POOL_CSV}")
    print(f"Report -> {REPORT_PATH}")


if __name__ == "__main__":
    main()
