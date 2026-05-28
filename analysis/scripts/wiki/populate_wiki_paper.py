#!/usr/bin/env python3
"""Rebuild scenarios/.wiki-clone with paper-oriented pages (after backup)."""

from __future__ import annotations

import argparse
import csv
import shutil
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import ANALYSIS_DIR, REPO_ROOT, SCENARIOS_DIR  # noqa: E402

REPO = REPO_ROOT
WIKI = SCENARIOS_DIR / ".wiki-clone"
DATA = ANALYSIS_DIR / "data"
DIVERSITY_N = 540  # canonical diversity scope: corpus_v1 only
COMBINED_N = 570  # corpus_v1 (540) + stress_controls (30)
WIKI_DIV_ASSETS = WIKI / "assets" / "diversity"
PAPER_MAIN = ANALYSIS_DIR / "figures" / "paper" / "main"
ARCHIVE_ROUND2 = WIKI / "_legacy_pre_paper_rebuild" / "round2_20260523"

# Link rewrite mode (used to generate GitHub-wiki-friendly links).
LINK_MODE = "local"  # local | github-wiki
REPO_BASE_URL: str | None = None  # e.g. https://github.com/ORG/REPO
REPO_BRANCH = "main"

# Root pages superseded by round2 restructure (renamed or merged)
OBSOLETE_ROOT = frozenset(
    {
        "06-Mobility-and-Maps.md",
        "07-Spatial-Occupancy.md",
        "08-Simulation-Time-and-Warmup.md",
        "09-Message-Generation-and-Analysis-Window.md",
        "10-Evaluation-Metrics.md",
        "11-Results-Summary.md",
        "12-Protocol-Benchmarking-Plan.md",
        "13-Limitations-and-Threats-to-Validity.md",
        "14-Reproducibility.md",
    }
)


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _csv_data_rows(path: Path) -> int:
    """Return number of data rows in a CSV (excluding header), or -1 if missing."""
    if not path.is_file():
        return -1
    try:
        with path.open(newline="", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in csv.DictReader(f))
    except OSError:
        return -1


def _load_ablation_metrics() -> list[dict[str, str]]:
    path = DATA / "ablation_metrics.csv"
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def _diversity_snapshot_table() -> str:
    """Markdown table 17/23/46 from canonical ablation_metrics.csv."""
    label = {"reduced_17": "Reduced-17", "core_23": "Core-23", "full_46": "Full-46"}
    lines = [
        "| Espacio | Pares |r| ≥ 0.7 | % | Silhouette |",
        "|---------|----------------:|---:|-----------:|",
    ]
    for key in ("reduced_17", "core_23", "full_46"):
        row = next((r for r in _load_ablation_metrics() if r.get("set") == key), None)
        if not row:
            continue
        pairs = row.get("pairs_r_above_threshold", "—")
        pct = row.get("pct_above", "—")
        if pct != "—":
            try:
                pct = f"{float(pct):.1f}%"
            except ValueError:
                pct = f"{pct}%"
        sil = row.get("silhouette", "—")
        if sil != "—":
            try:
                sil = f"{float(sil):.4f}"
            except ValueError:
                pass
        lines.append(f"| **{label[key]}** | {pairs} | {pct} | {sil} |")
    return "\n".join(lines)


def _home_current_status_block() -> str:
    """Build Home status table from live analysis/data counts."""
    n_feat = _csv_data_rows(DATA / "features.csv")
    n_out = _csv_data_rows(DATA / "output_metrics.csv")
    n_spat = _csv_data_rows(DATA / "spatial_occupancy_metrics.csv")
    n_manifest = _csv_data_rows(DATA / "corpus_v1_combined_manifest.csv")

    out_note = ""
    if n_out >= 0 and n_out != COMBINED_N:
        out_note = f" (objetivo {COMBINED_N}; pendiente regenerar)"

    spat_note = ""
    if n_spat == 720:
        spat_note = " (legacy 720; pendiente alinear a 540/570)"
    elif n_spat >= 0 and n_spat != COMBINED_N:
        spat_note = f" (objetivo {COMBINED_N})"

    if n_feat == DIVERSITY_N:
        div_val = (
            f"**{DIVERSITY_N}** escenarios (`corpus_v1`, sin stress) — "
            "[Resultados-Actuales](Resultados-Actuales)"
        )
    elif n_feat >= 0:
        div_val = (
            f"**{n_feat}** rows en `features.csv` (esperado {DIVERSITY_N}) — "
            "revisar pipeline `--no-stress`"
        )
    else:
        div_val = f"**{DIVERSITY_N}** (sin `features.csv`)"

    return f"""| Item | Value |
|------|-------|
| Combined paper benchmark | **{COMBINED_N}** = {DIVERSITY_N} `corpus_v1` + 30 `stress_controls` |
| Structural bases | 45 en `base_scenarios/` (sin TP) |
| Combined manifest | {n_manifest if n_manifest >= 0 else '—'} rows en `corpus_v1_combined_manifest.csv` |
| Diversity validation | {div_val} |
| Output metrics | {n_out if n_out >= 0 else '—'}/{COMBINED_N}{out_note} en `output_metrics.csv` |
| Spatial metrics | {n_spat if n_spat >= 0 else '—'}{spat_note} en `spatial_occupancy_metrics.csv` |

### Diversity freeze (540) — resumen

{_diversity_snapshot_table()}

Ver detalle: [Resultados-Actuales](Resultados-Actuales), [Figuras-y-Tablas](Figuras-y-Tablas)."""


def _csv_rows_label(path: Path, target: int) -> str:
    """Human-readable row count for wiki tables (e.g. '566 rows (objetivo 570)')."""
    n = _csv_data_rows(path)
    if n < 0:
        return f"missing (objetivo {target})"
    if n == target:
        return f"{n} rows"
    legacy = path.name == "spatial_occupancy_metrics.csv" and n == 720
    suffix = " — legacy 720" if legacy else f" — objetivo {target}"
    return f"{n} rows{suffix}"


def _output_metrics_status_line() -> str:
    n = _csv_data_rows(DATA / "output_metrics.csv")
    if n == COMBINED_N:
        return f"{n}/{COMBINED_N} rows in output_metrics.csv; indirect features available."
    if n < 0:
        return f"output_metrics.csv missing (objetivo {COMBINED_N})."
    return (
        f"{n}/{COMBINED_N} rows in output_metrics.csv "
        f"(pendiente regenerar hasta {COMBINED_N}); indirect features available."
    )


def _spatial_metrics_status_line() -> str:
    n = _csv_data_rows(DATA / "spatial_occupancy_metrics.csv")
    if n == COMBINED_N:
        return f"**{n}/{COMBINED_N}** scenarios have spatial metrics and heatmaps."
    if n == 720:
        return (
            "**720** rows in spatial_occupancy_metrics.csv (legacy 720; "
            f"pendiente alinear a {COMBINED_N}). Heatmaps disponibles."
        )
    if n < 0:
        return f"spatial_occupancy_metrics.csv missing (objetivo {COMBINED_N})."
    return f"**{n}/{COMBINED_N}** rows in spatial_occupancy_metrics.csv (pendiente alinear)."


def _paper_freeze_metrics_checklist() -> str:
    n_out = _csv_data_rows(DATA / "output_metrics.csv")
    n_spat = _csv_data_rows(DATA / "spatial_occupancy_metrics.csv")
    chk_out = "[x]" if n_out == COMBINED_N else "[ ]"
    chk_spat = "[x]" if n_spat == COMBINED_N else "[ ]"
    out_label = f"{n_out}/{COMBINED_N}" if n_out >= 0 else f"missing/{COMBINED_N}"
    if n_spat == 720:
        spat_label = "720 rows (legacy; objetivo 570)"
    elif n_spat >= 0:
        spat_label = f"{n_spat}/{COMBINED_N}"
    else:
        spat_label = f"missing/{COMBINED_N}"
    return f"""- {chk_out} Regenerate output_metrics ({out_label})
- {chk_spat} Regenerate spatial metrics ({spat_label})
- [x] Diversity metrics frozen ({DIVERSITY_N}, [RESULTADOS_ACTUALES.md](../analysis/reports/RESULTADOS_ACTUALES.md))
- [ ] **Message analysis window implemented in pipeline**
- [ ] Re-run diagnosis; P0 scenarios resolved or excluded
- [ ] Freeze `manifest_revision.csv` into main manifest
- [ ] Protocol comparison on main split complete
- [ ] Methods text matches actual scripts
- [ ] Limitations section includes map/traffic/synthetic disclaimers"""


def _rewrite_repo_links_for_github_wiki(text: str) -> str:
    """Rewrite markdown links that currently use ../analysis/... for GitHub Wiki.

    The wiki pages in GitHub Wiki are not located under the repo subdirectory
    structure, so relative paths like ../analysis/... resolve incorrectly.
    """

    if not REPO_BASE_URL:
        raise SystemExit(
            "populate_wiki_paper.py: --link-mode github-wiki requires --repo-base-url"
        )

    base = REPO_BASE_URL.rstrip("/")

    # Matches any markdown link target: ](<target>)
    link_target_re = re.compile(r"\]\(([^)]+)\)")

    def rewrite_target(target: str) -> str | None:
        # repo path: scenarios/analysis/... or scenarios/<file> (for top-level files)
        if target.startswith("../analysis/"):
            rel = target[len("../analysis/") :]
            is_dir = rel.endswith("/")
            rel_clean = rel.rstrip("/")
            repo_path = f"scenarios/analysis/{rel_clean}"
            if is_dir:
                # GitHub directory listing
                return f"{base}/tree/{REPO_BRANCH}/{repo_path}/"
            return f"{base}/blob/{REPO_BRANCH}/{repo_path}"

        if target == "../INVENTARIO.md":
            return f"{base}/blob/{REPO_BRANCH}/scenarios/INVENTARIO.md"

        if target.startswith("../corpus_v1/"):
            rel = target[len("../") :]  # corpus_v1/README.md, etc.
            return f"{base}/blob/{REPO_BRANCH}/scenarios/{rel}"

        # Unrecognized relative target -> keep as-is.
        return None

    def repl(m: re.Match[str]) -> str:
        target = m.group(1)
        new_target = rewrite_target(target)
        if not new_target:
            return m.group(0)
        return f"]({new_target})"

    return link_target_re.sub(repl, text)


def _page(
    title: str,
    purpose: str,
    data_paths: str,
    interpretation: str,
    current_status: str,
    pending: str,
    status: str,
    links: str,
    paper: str,
) -> str:
    return f"""# {title}

**Status:** {status} | **Updated:** {_utc()}

## Purpose

{purpose}

## Relevant data and paths

{data_paths}

## Methodological interpretation

{interpretation}

## Current status

{current_status}

## Pending items

{pending}

## Internal links

{links}

## Paper usage

{paper}
"""


PAGES: dict[str, str] = {}


def _add(name: str, **kwargs) -> None:
    PAGES[name] = _page(**kwargs)


def build_pages() -> None:
    _add(
        "Home.md",
        title="The ONE Scenario Corpus — Wiki",
        purpose=(
            "Entry point for reviewers and thesis readers. Documents the **combined paper benchmark** "
            f"(**{COMBINED_N}** scenarios: {DIVERSITY_N} `corpus_v1` + 30 `stress_controls`) and the "
            f"**diversity-validation freeze** ({DIVERSITY_N} scenarios, `corpus_v1` only, sin stress) "
            "for DTN/opportunistic routing research."
        ),
        data_paths="""| Resource | Path |
|----------|------|
| Paper benchmark (TP) | `scenarios/corpus_v1/` (540 `.settings`) + `scenarios/stress_controls/` (30) |
| Structural bases (no TP) | `scenarios/base_scenarios/` (45 `.settings`) |
| Combined manifest | `scenarios/analysis/data/corpus_v1_combined_manifest.csv` (570 rows) |
| Canonical diversity metrics | [Resultados actuales (wiki)](Resultados-Actuales) |
| Paper figures and interpretation | [Figuras-y-Tablas](Figuras-y-Tablas) |
| Paper tables | [Figuras-y-Tablas](Figuras-y-Tablas) |
| Repo map | [Repo-Map](Repo-Map) |
| Pipeline | [Pipeline](Pipeline) |""",
        interpretation="""This project provides a **controlled synthetic / semi-synthetic benchmark** — **not an empirical mobility trace**.

| Component | Type |
|-----------|------|
| Map geometry (HelsinkiMedium, Manhattan WKT) | Real / map-constrained |
| Mobility (WDM, RWP, ClusterMovement, …) | Synthetic / semi-synthetic |
| Traffic (MessageEventGenerator, TP01–TP12) | Synthetic — **experimental factors** |
| Contacts and deliveries | Simulated (The ONE) |

Routing outputs serve **protocol benchmarking**, not claims of real-world deployment realism.

**Wiki maintenance:** páginas generadas por `scenarios/analysis/scripts/wiki/populate_wiki_paper.py` a partir de plantillas + conteos/métricas en `scenarios/analysis/data/` (regenerar tras cambios en el pipeline).""",
        current_status=_home_current_status_block(),
        pending="""- Finalize **message analysis window** policy in the analysis pipeline before protocol comparison.
- Run protocol comparison experiments on `benchmark_split=main`.
- Freeze `manifest_revision.csv` into the main manifest for paper submission.""",
        status="draft",
        links="All numbered pages (01–15); [Resultados-Actuales](Resultados-Actuales); [Figuras-y-Tablas](Figuras-y-Tablas); [Repo-Map](Repo-Map); [Pipeline](Pipeline); [Glossary](Glossary); [References](References)",
        paper="Abstract, Introduction, Methods overview.",
    )

    _add(
        "01-Research-Goal.md",
        title="Research goal",
        purpose="Define the scientific question the corpus supports.",
        data_paths="- Corpus design: [corpus_v1/README.md](../corpus_v1/README.md)\n- Benchmark protocol plan: [13-Benchmark-Protocol-Comparison](13-Benchmark-Protocol-Comparison)",
        interpretation="""**Primary question:** How do opportunistic routing protocols behave under controlled diversity of mobility, connectivity, and traffic load?

**Secondary goals:**
1. Provide a reproducible scenario set (not a single map + RWP).
2. Separate **mobility base**, **traffic profile (TP)**, and **map** levers.
3. Enable fair protocol comparison with documented limitations.

**Non-goals:** emulating a specific real city; claiming empirical realism of contact traces.""",
        current_status="Paper benchmark (570) is the active benchmark under methodological freeze/review.",
        pending="Exact protocol set and router list for the paper.",
        status="stable",
        links="[02-Corpus-Overview](02-Corpus-Overview), [13-Benchmark-Protocol-Comparison](13-Benchmark-Protocol-Comparison)",
        paper="Introduction, problem statement.",
    )

    _add(
        "02-Corpus-Overview.md",
        title="Corpus overview",
        purpose="Describe corpus versions, scale, and versioning policy.",
        data_paths="""| Layer | Scenarios | Path | Role |
|-------|----------:|------|------|
| **base_scenarios** | 45 | `scenarios/base_scenarios/` | Structural mobility bases (no `__TP`); families 01–06 |
| **corpus_v1** | 540 | `scenarios/corpus_v1/` | Environmental benchmark with Traffic Profiles |
| **stress_controls** | 30 | `scenarios/stress_controls/` | Stress/control laboratory (TP01 + TP10 only) |
| legacy archive | 60 | `scenarios/_archive/legacy_corpus_v1_pre_rename/` | Pre-rename mobility corpus |
| dropped | 10 | `scenarios/corpus_dropped_v1/` | Archived v1 scenarios |

**Manifests:** `corpus_v1/manifest.csv`, `stress_controls/manifest.csv`, combined `analysis/data/corpus_v1_combined_manifest.csv`  
**Revision sidecar:** `manifest_revision.csv` per directory (`benchmark_split`: main / stress / control)  
**TP definitions:** `lib/traffic_profile_generator.py`  
**Changelog:** [corpus_reorganization_final_report.md](../analysis/reports/corpus_reorganization_final_report.md)

The retired legacy benchmark name is now split into `corpus_v1` + `stress_controls`.""",
        interpretation="""Each structural base in `base_scenarios/` is crossed with an **active subset** of traffic profiles (TP01–TP12) per `benchmark_definition.csv`, yielding **540** environmental simulations plus **30** stress/control runs.

Mobility and map settings originate from the legacy mobility corpus (migrated maps/worldSize); traffic overlays replace `Events*` blocks and adjust `Group*.msgTtl`.

Traces are **synthetic/semi-synthetic**: real map geometry constrains movement, but mobility patterns and messages are simulator-generated.""",
        current_status="570 `.settings` files and 570 combined-manifest rows; 45 structural bases validated in `base_scenarios/`.",
        pending="Freeze manifest after protocol comparison phase; merge `manifest_revision.csv` into main manifest.",
        status="stable",
        links="[03-Base-Scenarios](03-Base-Scenarios), [04-Scenario-Families](04-Scenario-Families), [05-Traffic-Profiles](05-Traffic-Profiles)",
        paper="Methods — experimental setup.",
    )

    _add(
        "03-Base-Scenarios.md",
        title="Base scenarios (structural)",
        purpose="Document the 45 mobility-only scenario bases used to derive the TP benchmark.",
        data_paths="""| Item | Path |
|------|------|
| Directory | `scenarios/base_scenarios/` |
| Manifest | `scenarios/base_scenarios/manifest.csv` |
| Validation | [base_scenarios_validation.md](../analysis/reports/base_scenarios_validation.md) |
| Generator | `scenarios/setup/migrate_base_scenarios_maps.py` |

**Scope:** families `01_urban` … `06_social` only — **no** `07_stress_controls`, **no** `__TP` suffix in filenames.""",
        interpretation="""Base scenarios hold **mobility, map, and default traffic blocks** before Traffic Profile overlays. They are the structural reference layer for the paper: same map migration (`HelsinkiMedium`/`Manhattan` → final maps) as the active benchmark, but without TP experimental factors.

Use `base_scenarios/` to inspect mobility design; use `corpus_v1/` + `stress_controls/` for routing benchmark runs.""",
        current_status="45/45 bases pass automated validation (`validate_base_scenarios.py`).",
        pending="None for structural layer; TP assignments tracked in `benchmark_definition.csv`.",
        status="stable",
        links="[02-Corpus-Overview](02-Corpus-Overview), [04-Scenario-Families](04-Scenario-Families)",
        paper="Methods — scenario design (mobility bases).",
    )

    _add(
        "04-Scenario-Families.md",
        title="Scenario families",
        purpose="Taxonomy of scenario bases: 45 environmental + 15 stress/control.",
        data_paths="""| Family | Bases | Role |
|--------|------:|------|
| 01_urban | 7 | WDM / Helsinki (U2/U4 Manhattan) |
| 02_campus | 6 | RWP / LinearMovement, compact world |
| 03_vehicles | 5 | MapRoute, bus carriers |
| 04_rural | 12 | Sparse RWP, clusters, extremes |
| 05_disaster | 9 | Post-disaster mobility patterns |
| 06_social | 6 | Communities, mixing |
| 07_stress_controls | 15 | Stress/control laboratory — lives under `stress_controls/` (not in `corpus_v1/`) |

**Benchmark splits** (`manifest_revision.csv`):
- **main:** TP01–TP08 on viable bases
- **stress:** TP09–TP11, TP04–TP06 on load, all 07_stress_controls
- **control:** TP12 partition, R1/R11 extremes""",
        interpretation="Families cover distinct mobility regimes. Environmental families (01–06) contribute **45** bases × active TP assignments → **540** runs in `corpus_v1/`. Family **07_stress_controls** contributes **15** bases × {TP01, TP10} → **30** runs in `stress_controls/`.",
        current_status="60 unique scenario bases in the combined paper benchmark (45 + 15 stress).",
        pending="Finalize main benchmark base list (~40–45) for protocol comparison subset.",
        status="draft",
        links="[05-Traffic-Profiles](05-Traffic-Profiles), [06-Feature-Space](06-Feature-Space)",
        paper="Methods — scenario design table.",
    )

    _add(
        "05-Traffic-Profiles.md",
        title="Traffic profiles (TP01–TP12)",
        purpose="Document traffic overlays as **experimental factors**.",
        data_paths="""| TP | Name | Intent |
|----|------|--------|
| TP01 | Baseline | Reference load |
| TP02 | LowLoad | Sparse messages |
| TP03 | ManySmall | High rate, small size |
| TP04 | FewLarge | Large messages (stress) |
| TP05 | CriticalTTL | Short TTL |
| TP06 | OneToMany | Fan-out |
| TP07 | BurstWindow | Mid-sim burst |
| TP08 | HubTarget | Hub traffic |
| TP09 | Bimodal | Two generators |
| TP10 | Storm | Congestion |
| TP11 | ManyToOne | Many-to-one |
| TP12 | GroupToGroup | Cross-group (partition control) |

**Docs:** [corpus_v1/README.md](../corpus_v1/README.md)  
**Validation:** [tp_validation_report.md](../analysis/reports/validation/tp_validation_report.md)""",
        interpretation="""Traffic profiles are **designed experimental factors**, not empirical traffic traces. Each TP modifies message generation (`Events*`) and TTL (`Group*.msgTtl`) while holding mobility constant.

TP12 serves as a **partition control** (cross-group messaging); TP04/TP10 are **stress** tiers. Protocol comparisons should hold TP fixed when comparing routers.""",
        current_status="Active TP assignments per `benchmark_definition.csv` (540 + 30 stress); validation report available.",
        pending="TP04 message sizes (500k–2M) sufficient after revision? TP05 msgTtl mismatches on U4/U6 documented as intentional.",
        status="stable",
        links="[10-Message-Creation-Time](10-Message-Creation-Time), [12-Message-Analysis-Window](12-Message-Analysis-Window)",
        paper="Methods — traffic workload; experimental design.",
    )

    _add(
        "06-Feature-Space.md",
        title="Feature space",
        purpose="Define the 46 extended / 23 core feature vector extracted from `.settings`.",
        data_paths="""| Artifact | Path |
|----------|------|
| Methodology | [features_core_vs_extended.md](../analysis/docs/features_core_vs_extended.md) |
| Feature list | [features_report.md](../analysis/reports/pipeline/features_report.md) |
| Extracted CSV | `data/features.csv`, `features_core.csv` (23 cols), `features_reduced.csv` (17 cols) |
| Normalization | `data/features_normalized.csv`, `normalization_params.csv` |

**46 features:** space (world_area, aspect_ratio, N, density, speed, pause, movement-model one-hot), contact (transmitRange, contact_rate_proxy), traffic (interval, size, msgTtl, patterns), resources (buffer, speed), WDM, cluster.""",
        interpretation="""Features describe **scenario configuration**, not simulation outcomes. The **23 core features** are used for diversity validation and paper methodology; **46 extended** for exploration.

**NaN policy:** z-score per column ignoring NaN; impute NaN → 0 in standardized space (see features_core_vs_extended §4).

Space uses **world_area** (Wx×Wy) and **aspect_ratio** = min(Wx,Wy)/max(Wx,Wy). Density is excluded from core due to redundancy with N and world_area.""",
        current_status=f"Feature extraction stable; {DIVERSITY_N} rows in features.csv for diversity scope (corpus_v1, --no-stress).",
        pending="Confirm core-23 list frozen for paper; document any post-revision feature drift.",
        status="stable",
        links="[07-Diversity-Validation](07-Diversity-Validation), [features_core_vs_extended.md](../analysis/docs/features_core_vs_extended.md)",
        paper="Methods — scenario representation; feature table.",
    )

    _add(
        "07-Diversity-Validation.md",
        title="Diversity validation",
        purpose=f"Document scenario–scenario diversity metrics for the {DIVERSITY_N}-scenario corpus (`corpus_v1` only).",
        data_paths="""| Metric | Source |
|--------|--------|
| Canonical results | [Resultados actuales (wiki)](Resultados-Actuales) |
| Core-23 correlation | `scenarios/analysis/reports/pipeline/correlation_core23_report.txt` |
| Full-46 correlation | `scenarios/analysis/reports/pipeline/correlation_report.txt` |
| Ablation | `scenarios/analysis/reports/pipeline/ablation_report.txt` |
| Feature–feature | `scenarios/analysis/reports/pipeline/feature_feature_correlation_report.txt` |
| Paper figures | [Figuras-y-Tablas](Figuras-y-Tablas) |

**Frozen metrics (540 scenarios, |r| threshold 0.7):**

| Space | max \\|r\\| | Pairs \\|r\\| ≥ 0.7 | Silhouette (Ward k=7) |
|-------|-----------|-------------------|----------------------|
| Core-23 | 1.0 | 5 029 (3.5%) | 0.3045 |
| Full-46 | 1.0 | 3 378 (2.3%) | 0.2354 |
| Reduced-17 | 1.0 | 7 425 (5.1%) | 0.3355 |

Feature–feature (core): `mm_WDM ↔ mm_Bus = 0.9354`. Stress controls (30) excluded.""",
        interpretation="""Diversity validation ensures scenarios are **not redundant** in configuration space. High |r| pairs indicate similar settings; the corpus aims for broad coverage without claiming uniform low correlation.

Ablation shows **core-23** offers the best interpretability trade-off: lower redundancy than reduced-17 on high-|r| pairs while keeping silhouette above full-46 (0.3045 vs 0.2354).""",
        current_status=f"Metrics frozen in RESULTADOS_ACTUALES.md for {DIVERSITY_N} scenarios (corpus_v1).",
        pending="Re-run correlation after any settings revision; update paper figures if metrics shift.",
        status="stable",
        links="[06-Feature-Space](06-Feature-Space), [08-Output-Metrics](08-Output-Metrics), [Resultados-Actuales](Resultados-Actuales), [Figuras-y-Tablas](Figuras-y-Tablas)",
        paper="Methods — diversity validation; Results — correlation/ablation figures.",
    )

    _add(
        "Resultados-Actuales.md",
        title="Resultados actuales del corpus",
        purpose="Referencia wiki de resultados congelados para paper, sin depender de enlaces a `.txt`.",
        data_paths="""| Recurso | Ubicacion |
|---------|-----------|
| Resumen canonico | `scenarios/analysis/reports/RESULTADOS_ACTUALES.md` |
| Correlacion core-23 | `scenarios/analysis/reports/pipeline/correlation_core23_report.txt` |
| Correlacion full-46 | `scenarios/analysis/reports/pipeline/correlation_report.txt` |
| Ablacion 17/23/46 | `scenarios/analysis/reports/pipeline/ablation_report.txt` |
| Correlacion feature-feature | `scenarios/analysis/reports/pipeline/feature_feature_correlation_report.txt` |
| Figuras paper | `scenarios/analysis/figures/paper/main/`, `.../supplementary/` |
| Tablas paper | `scenarios/analysis/figures/paper/tables/` |

**Nota:** esta pagina es el punto de entrada de lectura para resultados; los `.txt` quedan como anexos tecnicos.""",
        interpretation="""## Freeze activo (diversidad)

- Scope: **540** escenarios en `corpus_v1/` (sin `stress_controls`).
- Umbral de diversidad: **|r| >= 0.7**.
- Pares totales: C(540,2) = **145 530**.

## Metricas principales (17 / 23 / 46)

| Espacio | max |r| | Pares |r| >= 0.7 | Silhouette (Ward k=7) |
|---------|----------|-------------------|------------------------|
| **Reduced-17** | 1.0 | 7,425 (5.1%) | 0.3355 |
| **Core-23** | 1.0 | 5,029 (3.5%) | 0.3045 |
| **Full-46** | 1.0 | 3,378 (2.3%) | 0.2354 |

**Feature-feature (core):** `mm_WDM ↔ mm_Bus = 0.9354`

Interpretacion: **core-23** es el compromiso metodologico recomendado (interpretable y silhouette > full-46). Los 30 escenarios de stress se documentan aparte.""",
        current_status="""- [x] Metricas de diversidad congeladas para el benchmark activo.
- [x] Punto de entrada wiki habilitado (sin redireccion a `.txt`).
- [x] Enlaces a reportes tecnicos mantenidos como soporte.""",
        pending="- Revalidar esta pagina si cambian settings/manifests o se vuelve a correr el pipeline de diversidad.",
        status="stable",
        links="[Home](Home), [07-Diversity-Validation](07-Diversity-Validation), [08-Output-Metrics](08-Output-Metrics)",
        paper="Results (diversity) y Methods (validacion de representatividad).",
    )

    _add(
        "Figuras-y-Tablas.md",
        title="Figuras y tablas (paper)",
        purpose="Presentar resultados en formato visual dentro de la wiki, sin enlaces externos ni dependencia de rutas rotas.",
        data_paths="""| Item | Fuente canonica |
|------|------------------|
| Diversity table | `scenarios/analysis/figures/paper/tables/table_diversity_metrics_en.md` |
| Ablation table | `scenarios/analysis/figures/paper/tables/table_ablation_metrics_en.md` |
| Core vs extended table | `scenarios/analysis/figures/paper/tables/table_core_vs_extended_en.md` |

Figuras embebidas desde `assets/diversity/` (copiadas del pipeline paper).""",
        interpretation="""## Figuras principales (embebidas)

![Histograma Pearson](assets/diversity/histogram_correlations_pearson_paper.png)

![Ablacion pares |r|>=0.7](assets/diversity/ablation_pairs_high_bar.png)

![Ablacion silhouette](assets/diversity/ablation_silhouette_bar.png)

![PCA por familia](assets/diversity/pca_by_family.png)

![Heatmap feature-feature core](assets/diversity/heatmap_feature_feature_core.png)

![Histograma Spearman (supplementary)](assets/diversity/histogram_correlations_spearman_paper.png)

Interpretacion: el corpus cumple el criterio operativo (>=95% pares con |r|<0.7 en full-46); los pares TP06↔TP11 con r=1 son redundancias estructurales documentadas.""",
        current_status="""## Tabla de diversidad (540 escenarios)

| space | n_scenarios | n_features | max_abs_r | pairs_r_ge_0.7 | pct | silhouette |
|---|---:|---:|---:|---:|---:|---:|
| full_46 | 540 | 46 | 1.0 | 3378 | 2.3% | 0.2354 |
| core_23 | 540 | 23 | 1.0 | 5029 | 3.5% | 0.3045 |

## Tabla de ablacion (paper)

| feature_set | n_features | pairs_r_ge_0.7 | pct | silhouette |
|---|---:|---:|---:|---:|
| reduced_17 | 17 | 7425 | 5.1% | 0.3355 |
| core_23 | 23 | 5029 | 3.5% | 0.3045 |
| full_46 | 46 | 3378 | 2.3% | 0.2354 |""",
        pending="- Revisar figuras PCA/cluster tras cambios de clustering.",
        status="stable",
        links="[Home](Home), [Resultados-Actuales](Resultados-Actuales), [07-Diversity-Validation](07-Diversity-Validation)",
        paper="Results section: tablas de diversidad/ablacion y narrativa metodologica.",
    )

    _add(
        "Repo-Map.md",
        title="Repo map (wiki)",
        purpose="Mapa navegable del repositorio para trabajar desde la wiki sin salir a rutas externas.",
        data_paths="""| Ruta | Rol |
|------|-----|
| `scenarios/base_scenarios/` | 45 bases estructurales (sin TP) |
| `scenarios/corpus_v1/` | 540 escenarios ambientales |
| `scenarios/stress_controls/` | 30 escenarios stress/control |
| `scenarios/analysis/data/` | CSV de análisis y manifiestos |
| `scenarios/analysis/reports/` | reportes canónicos y validaciones |
| `scenarios/analysis/figures/` | tablas/figuras generadas |
| `scenarios/setup/` | scripts de generación y migración |""",
        interpretation="""Esta página resume la topología operativa del benchmark:

1. Capa estructural: `base_scenarios`
2. Capa benchmark: `corpus_v1` + `stress_controls`
3. Capa analítica: `analysis/data`, `analysis/reports`, `analysis/figures`

Objetivo: trazabilidad rápida de artefactos para redacción de paper.""",
        current_status="""- [x] Mapa funcional para scope 45/540/30/570
- [x] Sin dependencia de enlaces externos a GitHub
- [x] Navegable desde Home""",
        pending="- Mantener sincronizado con `02-Corpus-Overview` ante futuros cambios de estructura.",
        status="stable",
        links="[Home](Home), [02-Corpus-Overview](02-Corpus-Overview), [Pipeline](Pipeline)",
        paper="Appendix de organización y trazabilidad del repositorio.",
    )

    _add(
        "Pipeline.md",
        title="Pipeline (wiki)",
        purpose="Flujo de ejecución y validación del benchmark explicado en formato wiki.",
        data_paths="""## Etapas

1. **Simulación** (`run_all_scenarios.py`)
2. **Extracción/medición** (`run_analysis.py` fases)
3. **Validación** (`scripts/validation/*`)
4. **Síntesis paper** (`Resultados-Actuales`, `Figuras-y-Tablas`, checklist)

## Artefactos clave

| Etapa | Salidas |
|------|---------|
| Simulación | reportes crudos The ONE (`reports/`) |
| Métricas | `analysis/data/output_metrics.csv`, `indirect_features_diego.csv` |
| Diversidad | reportes de correlación + ablación |
| Espacial | `spatial_occupancy_metrics.csv` |
| Wiki | páginas 01–15 + páginas temáticas""",
        interpretation="""El pipeline separa claramente generación de datos, control de calidad y comunicación de resultados. Esta separación evita mezclar artefactos históricos con el estado activo del benchmark.""",
        current_status="""- [x] Flujo documentado y enlazado desde Home
- [x] Integrado con páginas internas de resultados y figuras
- [x] Preparado para reproducibilidad de paper""",
        pending="- Agregar comandos canónicos finales por fase cuando cierres completamente el set de ejecución para paper.",
        status="stable",
        links="[Home](Home), [14-Dashboard-and-Reproducibility](14-Dashboard-and-Reproducibility), [15-Paper-Freeze-Checklist](15-Paper-Freeze-Checklist)",
        paper="Methods/Reproducibility workflow del paper.",
    )

    _add(
        "08-Output-Metrics.md",
        title="Output metrics",
        purpose="Define routing benchmark metrics from simulation outputs.",
        data_paths=f"""| Artifact | Path |
|----------|------|
| Output CSV | `data/output_metrics.csv` (**{_csv_rows_label(DATA / "output_metrics.csv", COMBINED_N)}**) |
| Indirect (Diego-style) | `data/indirect_features_diego.csv` |
| Review | [evaluation_metrics_review.md](../analysis/reports/validation/evaluation_metrics_review.md) |
| Diagnosis | [scenario_diagnosis.md](../analysis/reports/validation/scenario_diagnosis.md) |
| Paper tables | [figures/paper/tables/](../analysis/figures/paper/tables/) |

**Primary metrics (protocol comparison):**

| Metric | Source |
|--------|--------|
| delivery_ratio | MessageStatsReport |
| latency_mean | MessageStatsReport |
| overhead_ratio | MessageStatsReport |
| drop_ratio | derived (dropped/created) |

**Secondary:** hopcount_avg, created, started, relayed, delivered  
**Diagnostic (context only):** total_encounters, spatial coverage — do not rank protocols on these alone.""",
        interpretation=f"""Output metrics measure **routing protocol performance** under each scenario×TP combination. They depend on the default router (EpidemicRouter in baseline runs) and are intended for **benchmark comparison**, not empirical realism claims.

Highlights ({COMBINED_N} scenarios): zero delivery in structural cases (TP12), misconfiguration (R1/R11), short TTL; TP04 highest drops/overhead (stress); campus TP01 often high delivery (~0.8+).""",
        current_status=_output_metrics_status_line(),
        pending="Apply message analysis window filter before protocol comparison; add hopcount to CSV export if needed.",
        status="needs validation",
        links="[12-Message-Analysis-Window](12-Message-Analysis-Window), [13-Benchmark-Protocol-Comparison](13-Benchmark-Protocol-Comparison)",
        paper="Methods — metrics; Results tables.",
    )

    _add(
        "09-Spatial-Occupancy.md",
        title="Spatial occupancy",
        purpose="Grid-based mobility coverage methodology.",
        data_paths=f"""| Artifact | Path |
|----------|------|
| Metrics CSV | `data/spatial_occupancy_metrics.csv` (**{_csv_rows_label(DATA / "spatial_occupancy_metrics.csv", COMBINED_N)}**) |
| Heatmaps | `figures/spatial_heatmaps/` |
| Methodology | [spatial_occupancy_report.md](../analysis/reports/spatial/spatial_occupancy_report.md) |

**Reports:** `SpatialOccupancyReport` + `NodePositionReport` (overlays: `spatial_occupancy_reports_overrides.txt`)

**Key metrics:**
- `final_coverage_pct` — fraction of grid cells visited
- `time_to_50/80/90pct` — time to coverage milestones
- `coverage_accessible_ratio` — visited cells on road bbox vs full world
- `cells_visited_pct`, `map_dataset`""",
        interpretation="""| Observation | Meaning |
|-------------|---------|
| Low world coverage (~8–10%) on WDM | Nodes use **roads**, not full rectangle world |
| High accessible ratio | Visited area is on streets, not empty space |
| **Low coverage ≠ low connectivity** | Mobility can be active but world grid is oversized |

Spatial occupancy measures **where nodes move**, not **who meets whom**. Do not use coverage alone as a connectivity proxy.""",
        current_status=_spatial_metrics_status_line(),
        pending="Document MAP_UNDERUSED patterns in revision plan; crop worldSize where recommended.",
        status="stable",
        links="[06-Feature-Space](06-Feature-Space), [11-Simulation-Time-Policy](11-Simulation-Time-Policy)",
        paper="Methods — spatial representativeness; Discussion.",
    )

    _add(
        "10-Message-Creation-Time.md",
        title="Message creation time",
        purpose="When messages are created during simulation.",
        data_paths="""| Artifact | Path |
|----------|------|
| Audit | [message_creation_time_audit.md](../analysis/reports/validation/message_creation_time_audit.md) |
| Summary CSV | `data/message_creation_time_summary.csv` |

**Default:** `Scenario.endTime = 43200` s (12 h).""",
        interpretation="""**Messages are NOT all injected at t=0.** First creation ≥ `interval_min` after sim start.

| TP | Temporal behavior |
|----|-------------------|
| TP01–TP06, TP08–TP12 | Spread across simulation (~median 50% endTime) |
| TP07 | Burst window ~20–28% endTime |
| TP02 | Often latest creations near end (long intervals) |

~10% of messages may appear in the last 10% of simulation for many TPs — affects latency interpretation.""",
        current_status="Audit complete for corpus_v1; temporal patterns documented per TP.",
        pending="Link creation-time filters to output_metrics pipeline.",
        status="draft",
        links="[05-Traffic-Profiles](05-Traffic-Profiles), [11-Simulation-Time-Policy](11-Simulation-Time-Policy), [12-Message-Analysis-Window](12-Message-Analysis-Window)",
        paper="Methods — traffic temporal design.",
    )

    _add(
        "11-Simulation-Time-Policy.md",
        title="Simulation time policy",
        purpose="Define useful simulation duration and warmup.",
        data_paths="""| Artifact | Path |
|----------|------|
| Policy | [simulation_time_policy.md](../analysis/reports/policies/simulation_time_policy.md) |
| Useful time CSV | `data/useful_simulation_time_metrics.csv` |
| Policy CSV | `data/simulation_time_policy.csv` |""",
        interpretation="""Default `Scenario.endTime = 43200` s (12 h). **Useful time** (from connectivity): most scenarios show activity until near end.

**Policy:**
- Warmup: first **5%** of endTime excluded from message outcome metrics
- Analysis cutoff: **90%** of endTime for delivery/latency aggregates
- Extend endTime only after fixing mobility (not for oversized worlds)""",
        current_status="12 h default sufficient per useful_simulation_time analysis.",
        pending="Per-family warmup overrides if needed.",
        status="draft",
        links="[10-Message-Creation-Time](10-Message-Creation-Time), [12-Message-Analysis-Window](12-Message-Analysis-Window)",
        paper="Methods — simulation duration.",
    )

    _add(
        "12-Message-Analysis-Window.md",
        title="Message analysis window",
        purpose="Which messages to include when comparing routing outcomes.",
        data_paths="""| Artifact | Path |
|----------|------|
| Policy | [message_analysis_window_policy.md](../analysis/reports/canonical/message_analysis_window_policy.md) |

**Recommended policy B: TTL-aware window + 5% warmup**

```
valid message m iff 0.05*endTime <= t_create(m) <= endTime - msgTtl
```

Late messages in last 10%: label **censored_late**, exclude from latency comparison.""",
        interpretation="""Without a consistent analysis window, protocol comparisons are **biased** by late-created messages that cannot deliver before simulation end. Policy B accounts for TTL and warmup.

**Do not compare routing protocols until this window is implemented in the output_metrics pipeline.**""",
        current_status="Policy documented; **not yet enforced** in automated analysis.",
        pending="""- **Blocker:** Implement window filter in `output_metrics` / protocol comparison scripts.
- Validate censored_late counts per TP before paper results.""",
        status="draft",
        links="[10-Message-Creation-Time](10-Message-Creation-Time), [11-Simulation-Time-Policy](11-Simulation-Time-Policy), [13-Benchmark-Protocol-Comparison](13-Benchmark-Protocol-Comparison)",
        paper="Methods — metric window; required before Results.",
    )

    _add(
        "13-Benchmark-Protocol-Comparison.md",
        title="Benchmark protocol comparison",
        purpose="How to compare routing protocols fairly on corpus_v1.",
        data_paths="""| Artifact | Path |
|----------|------|
| Benchmark splits | `corpus_v1/manifest_revision.csv` |
| Protocol overlays | `analysis/protocol_overlays/` |

**Prerequisites:** message analysis window closed ([12-Message-Analysis-Window](12-Message-Analysis-Window)).""",
        interpretation="""1. **Subset:** `benchmark_split=main` (TP01–TP08, viable bases).
2. **Fixed settings:** same mobility, map, TP; only `Group.router` changes.
3. **Metrics:** primary four from [08-Output-Metrics](08-Output-Metrics).
4. **Window:** TTL-aware message filter (policy B).
5. **Runs:** N seeds or confidence intervals if time permits.

**Stress tier** (TP10, TP04, 07_stress_controls): report separately. **Control tier** (TP12): validate partition behavior, not delivery ranking.""",
        current_status="Plan documented; **no protocol comparison runs yet**.",
        pending="Select protocol set; run on main split after analysis window implemented.",
        status="draft",
        links="[08-Output-Metrics](08-Output-Metrics), [12-Message-Analysis-Window](12-Message-Analysis-Window), [15-Paper-Freeze-Checklist](15-Paper-Freeze-Checklist)",
        paper="Methods — protocol comparison; Results.",
    )

    _add(
        "14-Dashboard-and-Reproducibility.md",
        title="Dashboard and reproducibility",
        purpose="Interactive exploration and full reproduction pipeline.",
        data_paths="""| Resource | Path |
|----------|------|
| Dashboard | `scenarios/analysis/dashboard.py` (Streamlit) |
| Pipeline index | [Pipeline](Pipeline) |
| Analysis README | [Pipeline](Pipeline) |
| Repo map | [Repo-Map](Repo-Map) |

**Dashboard pages:** Inicio · Perfiles TP · Explorador · Detalle escenario · Espacial · Auditoría · Pipeline clásico · Reportes crudos""",
        interpretation="""## Official pipeline (12 steps)

See [Pipeline](Pipeline) for canonical execution overview.

1. Simulation — `run_all_scenarios.py --corpus corpus_v1` + Diego17 + spatial overlays
2. Output metrics — `run_analysis.py --phase output_metrics` (+ `indirects`)
3. Features — `--phase features` → `normalize` → `correlation` → `feature_correlation` → `ablation`
4. Spatial — `analyze_spatial_occupancy.py`
5. Message creation — `analyze_message_creation_times.py`
6. TP validation — `validate_traffic_profiles.py`
7. Figures — `--phase figures_paper` + `run_figures_aggregated.py`
8. Tables — `--phase tables_paper`
9. Wiki — `build_wiki_research_reports.py` → `populate_wiki_paper.py`

## Quick simulation

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \\
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \\
  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt
```

## Dashboard

```bash
./venv/bin/streamlit run scenarios/analysis/dashboard.py
```""",
        current_status="Pipeline documented; dashboard operational for corpus_v1 exploration.",
        pending="Pin ONE commit hash in paper; document exact venv/requirements versions.",
        status="stable",
        links="[15-Paper-Freeze-Checklist](15-Paper-Freeze-Checklist), [Pipeline](Pipeline), [Repo-Map](Repo-Map)",
        paper="Reproducibility appendix.",
    )

    _add(
        "15-Paper-Freeze-Checklist.md",
        title="Paper freeze checklist",
        purpose="Gate before claiming final results.",
        data_paths="See [paper_phase1_action_plan.md](../analysis/reports/paper_gate/paper_phase1_action_plan.md)",
        interpretation="All items must pass before submission claims.",
        current_status=_paper_freeze_metrics_checklist(),
        pending="Protocol comparison blocked until analysis window closed.",
        status="draft",
        links="[07-Diversity-Validation](07-Diversity-Validation), [12-Message-Analysis-Window](12-Message-Analysis-Window), [14-Dashboard-and-Reproducibility](14-Dashboard-and-Reproducibility)",
        paper="Internal checklist before submission.",
    )

    _add(
        "References.md",
        title="References",
        purpose="Pointers to external documentation.",
        data_paths="""- Core methodology sources in this wiki: [Resultados-Actuales](Resultados-Actuales), [Figuras-y-Tablas](Figuras-y-Tablas), [Pipeline](Pipeline), [Repo-Map](Repo-Map)
- Analysis supplements in repository path notation: `scenarios/analysis/reports/`""",
        interpretation="""Internal bibliographic anchors for writing:

1. Corpus and benchmark design: [02-Corpus-Overview](02-Corpus-Overview), [04-Scenario-Families](04-Scenario-Families), [05-Traffic-Profiles](05-Traffic-Profiles)
2. Diversity and representation: [06-Feature-Space](06-Feature-Space), [07-Diversity-Validation](07-Diversity-Validation), [Resultados-Actuales](Resultados-Actuales)
3. Metrics and reproducibility: [08-Output-Metrics](08-Output-Metrics), [11-Simulation-Time-Policy](11-Simulation-Time-Policy), [12-Message-Analysis-Window](12-Message-Analysis-Window), [Pipeline](Pipeline)""",
        current_status="Internal references consolidated for wiki-first navigation.",
        pending="Add formal BibTeX/citation style section when final paper bibliography is frozen.",
        status="draft",
        links="[Home](Home), [Glossary](Glossary), [Pipeline](Pipeline)",
        paper="Bibliography and citation map (internal working version).",
    )

    _add(
        "Glossary.md",
        title="Glossary",
        purpose="Term definitions for wiki readers.",
        data_paths="N/A",
        interpretation="""| Term | Meaning |
|------|---------|
| TP | Traffic profile overlay (TP01–TP12) — **experimental factor** |
| WDM | WorkingDayMovement |
| DTN | Delay-tolerant networking |
| Synthetic / semi-synthetic | Map may be real; mobility and messages are simulator-generated |
| benchmark_split | main / stress / control in manifest_revision |
| censored_late | Message created too late for fair latency comparison |
| Spatial occupancy | Grid coverage of visited cells — **not** connectivity |""",
        current_status="Core terms defined.",
        pending="Expand as paper terminology stabilizes.",
        status="draft",
        links="[Home](Home), [05-Traffic-Profiles](05-Traffic-Profiles)",
        paper="Optional glossary in thesis.",
    )

    _add(
        "CHANGELOG.md",
        title="Wiki changelog",
        purpose="Track wiki rebuild history.",
        data_paths="Backups: `scenarios/_archive/wiki/wiki_backup_*`",
        interpretation="N/A",
        current_status=f"""- **{_utc()}:** Diversity freeze documented (540 corpus_v1); wiki status reads live CSV counts (output/spatial may lag combined benchmark 570).
- **2026-06-20 11:41 UTC:** Full rebuild (paper-oriented). Old wiki in `wiki_backup_20260520_133832/`.""",
        pending="N/A",
        status="draft",
        links="[Home](Home)",
        paper="N/A",
    )


def _sync_wiki_diversity_assets() -> None:
    """Copy canonical paper diversity PNGs into wiki assets for inline display."""
    WIKI_DIV_ASSETS.mkdir(parents=True, exist_ok=True)
    stems = [
        "histogram_correlations_pearson_paper.png",
        "histogram_correlations_spearman_paper.png",
        "ablation_pairs_high_bar.png",
        "ablation_silhouette_bar.png",
        "heatmap_feature_feature_core.png",
        "pca_by_family.png",
        "pca_by_cluster.png",
    ]
    for stem in stems:
        src_main = PAPER_MAIN / stem
        src_supp = ANALYSIS_DIR / "figures" / "paper" / "supplementary" / stem
        src = src_main if src_main.is_file() else src_supp
        if src.is_file():
            shutil.copy2(src, WIKI_DIV_ASSETS / stem)


def _archive_obsolete_root() -> None:
    """Move superseded root .md pages to round2 archive folder."""
    ARCHIVE_ROUND2.mkdir(parents=True, exist_ok=True)
    for name in OBSOLETE_ROOT:
        src = WIKI / name
        if src.is_file():
            dest = ARCHIVE_ROUND2 / name
            if dest.exists():
                dest.unlink()
            shutil.move(str(src), str(dest))
            print(f"Archived {name} -> {dest.relative_to(WIKI)}")


def main() -> int:
    global LINK_MODE, REPO_BASE_URL, REPO_BRANCH

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--link-mode",
        choices=["local", "github-wiki"],
        default="local",
        help="local=keep relative links; github-wiki=emit absolute URLs to repo files/dirs.",
    )
    parser.add_argument(
        "--repo-base-url",
        default="",
        help="GitHub base URL, e.g. https://github.com/ORG/REPO (required for github-wiki).",
    )
    parser.add_argument(
        "--repo-branch",
        default="main",
        help="GitHub branch name used for /blob/ and /tree/. Default: main",
    )
    args = parser.parse_args()
    LINK_MODE = args.link_mode
    REPO_BASE_URL = args.repo_base_url or None
    REPO_BRANCH = args.repo_branch

    build_pages()
    if not WIKI.is_dir():
        print("Wiki dir missing", file=sys.stderr)
        return 1

    _archive_obsolete_root()
    _sync_wiki_diversity_assets()

    for name, content in PAGES.items():
        if LINK_MODE == "github-wiki":
            content = _rewrite_repo_links_for_github_wiki(content)
        (WIKI / name).write_text(content, encoding="utf-8")
        print(f"Wrote {WIKI / name}")

    (WIKI / "README.md").write_text(
        "# Wiki clone directory\n\n"
        "See [Home.md](Home.md) for the paper-oriented documentation.\n\n"
        "Structure: 23 flat EN pages (01–15 + Resultados-Actuales + Figuras-y-Tablas + Repo-Map + Pipeline + Glossary + References + CHANGELOG).\n\n"
        "Legacy: `_legacy_pre_paper_rebuild/` (v1 wiki + round2 superseded pages).\n\n"
        "Backup: `scenarios/_archive/wiki/wiki_backup_20260523_*`.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
