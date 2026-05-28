#!/usr/bin/env python3
"""Validate structural base_scenarios/ (no Traffic Profiles)."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

_ANALYSIS = Path(__file__).resolve().parent
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import BASE_SCENARIOS_DIR, CORPUS_V1_DIR, DATA_DIR, REPO_ROOT, SCENARIOS_DIR  # noqa: E402

sys.path.insert(0, str(SCENARIOS_DIR / "setup"))
from migrate_corpus_maps import FAMILY_MAP  # noqa: E402
from regenerate_manifests import parse_settings  # noqa: E402

EXPECTED_FAMILIES = frozenset(FAMILY_MAP.keys()) - {"07_stress_controls"}
TP_IN_NAME = re.compile(r"__TP\d{2}_")
BENCH_CSV = DATA_DIR / "benchmark_definition.csv"
OUT_CSV = DATA_DIR / "base_scenarios_validation.csv"
OUT_MD = _ANALYSIS / "reports" / "base_scenarios_validation.md"

# Optional warnings (legacy bases may still use multi-generator or targeted hosts)
TP_WARN_PATTERNS = [
    (re.compile(r"^Events1\.time\s*=", re.M), "warn_Events1.time"),
    (re.compile(r"^Events2\.", re.M), "warn_Events2"),
    (re.compile(r"^Events1\.tohosts\s*=", re.M), "warn_Events1.tohosts"),
]


def load_benchmark_bases() -> dict[str, set[str]]:
    """scenario_base -> set of active TP ids in corpus_v1 benchmark."""
    out: dict[str, set[str]] = {}
    if not BENCH_CSV.is_file():
        return out
    with BENCH_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("deprecated", "").upper() == "TRUE":
                continue
            name = row.get("scenario_name", "")
            m = re.search(r"^(.*)__(TP\d{2})_", name)
            if not m:
                continue
            base, tp = m.group(1), m.group(2)
            out.setdefault(base, set()).add(tp)
    return out


def expected_world_size(family: str) -> tuple[int, int] | None:
    pol = FAMILY_MAP.get(family)
    if not pol:
        return None
    return pol["world_size"]


def validate_file(path: Path, family: str) -> dict:
    issues: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    kv = parse_settings(text)
    name = kv.get("Scenario.name", path.stem)
    if TP_IN_NAME.search(name) or TP_IN_NAME.search(path.stem):
        issues.append("name_contains_TP")
    if "__TP" in path.stem:
        issues.append("filename_contains_TP")
    warnings: list[str] = []
    for rx, label in TP_WARN_PATTERNS:
        if rx.search(text):
            warnings.append(label)
    exp_ws = expected_world_size(family)
    ws_raw = kv.get("MovementModel.worldSize", "")
    if exp_ws and ws_raw:
        parts = [p.strip() for p in ws_raw.split(",")]
        if len(parts) >= 2:
            try:
                wx, wy = int(float(parts[0])), int(float(parts[1]))
                if (wx, wy) != exp_ws:
                    issues.append(f"worldSize_mismatch:got={wx},{wy},exp={exp_ws[0]},{exp_ws[1]}")
            except ValueError:
                issues.append("worldSize_parse_error")
    map_file = kv.get("MapBasedMovement.mapFile1", "")
    exp_map = FAMILY_MAP.get(family, {}).get("data_dir", "")
    if exp_map and map_file and not map_file.startswith(exp_map):
        issues.append(f"map_mismatch:{map_file}")
    for old in ("HelsinkiMedium", "Manhattan/"):
        if old in text and "HelsinkiDowntown" not in text and family == "01_urban":
            if "HelsinkiMedium" in text:
                issues.append("stale_HelsinkiMedium_ref")
    status = "ok" if not issues else "fail"
    return {
        "settings_file": str(path.relative_to(REPO_ROOT)),
        "family": family,
        "scenario_base": name,
        "status": status,
        "issues": "; ".join(issues),
        "warnings": "; ".join(warnings),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate base_scenarios/")
    ap.add_argument("--expected-count", type=int, default=45)
    args = ap.parse_args()

    settings = [
        sf
        for sf in sorted(BASE_SCENARIOS_DIR.rglob("*.settings"))
        if not any(p.startswith("_") or "backup" in p.lower() for p in sf.parts)
    ]
    rows = []
    for sf in settings:
        fam = sf.parent.name
        if fam not in EXPECTED_FAMILIES:
            continue
        rows.append(validate_file(sf, fam))

    bench_bases = load_benchmark_bases()
    for row in rows:
        base = row["scenario_base"]
        if base in bench_bases:
            row["corpus_v1_tp_count"] = len(bench_bases[base])
            row["corpus_v1_coverage"] = "yes"
        else:
            row["corpus_v1_tp_count"] = 0
            row["corpus_v1_coverage"] = "no"
            row["status"] = "fail"
            row["issues"] = (row["issues"] + "; no_corpus_v1_TP_variants").strip("; ")

    n_ok = sum(1 for r in rows if r["status"] == "ok")
    n_fail = len(rows) - n_ok

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# base_scenarios validation",
        "",
        f"- **Expected count:** {args.expected_count}",
        f"- **Found:** {len(rows)}",
        f"- **OK:** {n_ok}",
        f"- **Fail:** {n_fail}",
        "",
        f"Detail: `{OUT_CSV.relative_to(REPO_ROOT)}`",
        "",
    ]
    if n_fail:
        lines.append("## Failures")
        for r in rows:
            if r["status"] != "ok":
                lines.append(f"- `{r['scenario_base']}`: {r['issues']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_CSV} and {OUT_MD}")
    print(f"Summary: {n_ok} ok, {n_fail} fail (expected {args.expected_count})")
    return 0 if len(rows) == args.expected_count and n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
