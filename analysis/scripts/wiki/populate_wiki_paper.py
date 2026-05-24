#!/usr/bin/env python3
"""Rebuild scenarios/.wiki-clone with paper-oriented pages (after backup)."""

from __future__ import annotations

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import REPO_ROOT, SCENARIOS_DIR  # noqa: E402

REPO = REPO_ROOT
WIKI = SCENARIOS_DIR / ".wiki-clone"
ARCHIVE_ROUND2 = WIKI / "_legacy_pre_paper_rebuild" / "round2_20260523"

# Root pages superseded by round2 restructure (renamed or merged)
OBSOLETE_ROOT = frozenset(
    {
        "05-Mobility-and-Maps.md",
        "06-Spatial-Occupancy.md",
        "07-Simulation-Time-and-Warmup.md",
        "08-Message-Generation-and-Analysis-Window.md",
        "09-Evaluation-Metrics.md",
        "10-Results-Summary.md",
        "11-Protocol-Benchmarking-Plan.md",
        "12-Limitations-and-Threats-to-Validity.md",
        "13-Reproducibility.md",
    }
)


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


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
        purpose="Entry point for reviewers and thesis readers. Documents the **corpus_v2** benchmark (720 scenarios) for DTN/opportunistic routing research.",
        data_paths="""| Resource | Path |
|----------|------|
| Active corpus | `scenarios/corpus_v2/` (720 `.settings`, `manifest.csv`) |
| Canonical diversity metrics | [RESULTADOS_ACTUALES.md](../analysis/reports/RESULTADOS_ACTUALES.md) |
| Paper figures | [figures/paper/main/](../analysis/figures/paper/main/), [supplementary/](../analysis/figures/paper/supplementary/) |
| Paper tables | [figures/paper/tables/](../analysis/figures/paper/tables/) |
| Repo map | [INVENTARIO.md](../INVENTARIO.md) |
| Pipeline | [SCRIPTS_INDEX.md](../analysis/SCRIPTS_INDEX.md) |""",
        interpretation="""This project provides a **controlled synthetic / semi-synthetic benchmark** — **not an empirical mobility trace**.

| Component | Type |
|-----------|------|
| Map geometry (HelsinkiMedium, Manhattan WKT) | Real / map-constrained |
| Mobility (WDM, RWP, ClusterMovement, …) | Synthetic / semi-synthetic |
| Traffic (MessageEventGenerator, TP01–TP12) | Synthetic — **experimental factors** |
| Contacts and deliveries | Simulated (The ONE) |

Routing outputs serve **protocol benchmarking**, not claims of real-world deployment realism.""",
        current_status="""| Item | Value |
|------|-------|
| Active corpus | `corpus_v2` — **720** scenarios (60 bases × 12 TP) |
| Output metrics | **720/720** rows in `output_metrics.csv` |
| Spatial metrics | **720/720** rows in `spatial_occupancy_metrics.csv` |
| Diversity freeze | [RESULTADOS_ACTUALES.md](../analysis/reports/RESULTADOS_ACTUALES.md) |""",
        pending="""- Finalize **message analysis window** policy in the analysis pipeline before protocol comparison.
- Run protocol comparison experiments on `benchmark_split=main`.
- Freeze `manifest_revision.csv` into the main manifest for paper submission.""",
        status="draft",
        links="All numbered pages (01–14); [Glossary](Glossary); [References](References)",
        paper="Abstract, Introduction, Methods overview.",
    )

    _add(
        "01-Research-Goal.md",
        title="Research goal",
        purpose="Define the scientific question the corpus supports.",
        data_paths="- Corpus design: [corpus_v2/README.md](../corpus_v2/README.md)\n- Benchmark protocol plan: [12-Benchmark-Protocol-Comparison](12-Benchmark-Protocol-Comparison)",
        interpretation="""**Primary question:** How do opportunistic routing protocols behave under controlled diversity of mobility, connectivity, and traffic load?

**Secondary goals:**
1. Provide a reproducible scenario set (not a single map + RWP).
2. Separate **mobility base**, **traffic profile (TP)**, and **map** levers.
3. Enable fair protocol comparison with documented limitations.

**Non-goals:** emulating a specific real city; claiming empirical realism of contact traces.""",
        current_status="Corpus_v2 (720) is the active benchmark under methodological freeze/review.",
        pending="Exact protocol set and router list for the paper.",
        status="stable",
        links="[02-Corpus-Overview](02-Corpus-Overview), [12-Benchmark-Protocol-Comparison](12-Benchmark-Protocol-Comparison)",
        paper="Introduction, problem statement.",
    )

    _add(
        "02-Corpus-Overview.md",
        title="Corpus overview",
        purpose="Describe corpus versions, scale, and versioning policy.",
        data_paths="""| Version | Scenarios | Path | Role |
|---------|----------:|------|------|
| corpus_v1 | 60 | `scenarios/corpus_v1/` | Historical mobility base |
| corpus_v2 | **720** | `scenarios/corpus_v2/` | **Active** benchmark |
| corpus_dropped_v1 | 10 | `scenarios/corpus_dropped_v1/` | Archived v1 scenarios |

**Manifest:** `scenarios/corpus_v2/manifest.csv`  
**Revision sidecar:** `manifest_revision.csv` (`benchmark_split`: main / stress / control)  
**TP definitions:** `lib/traffic_profile_generator.py` (corpus frozen)  
**Changelog:** [corpus_v2_revision_changelog.md](../analysis/reports/project/corpus_v2_revision_changelog.md)

There is **no corpus_v3** — revisions are applied in-place to corpus_v2.""",
        interpretation="""Corpus_v2 expands each v1 mobility base with **12 traffic profiles (TP01–TP12)** as orthogonal experimental factors. Mobility and map settings come from v1; traffic overlays replace `Events*` blocks and adjust `Group*.msgTtl`.

Traces are **synthetic/semi-synthetic**: real map geometry constrains movement, but mobility patterns and messages are simulator-generated.""",
        current_status="720 `.settings` files and 720 manifest rows; consistent by family and TP.",
        pending="Freeze manifest after protocol comparison phase; merge `manifest_revision.csv` into main manifest.",
        status="stable",
        links="[03-Scenario-Families](03-Scenario-Families), [04-Traffic-Profiles](04-Traffic-Profiles)",
        paper="Methods — experimental setup.",
    )

    _add(
        "03-Scenario-Families.md",
        title="Scenario families",
        purpose="Taxonomy of the 60 scenario bases across 7 families.",
        data_paths="""| Family | Bases | Role |
|--------|------:|------|
| 01_urban | 7 | WDM / Helsinki (U2/U4 Manhattan) |
| 02_campus | 6 | RWP / LinearMovement, compact world |
| 03_vehicles | 5 | MapRoute, bus carriers |
| 04_rural | 12 | Sparse RWP, clusters, extremes |
| 05_disaster | 9 | Post-disaster mobility patterns |
| 06_social | 6 | Communities, mixing |
| 07_traffic | 15 | Traffic-pattern laboratory (stress) |

**Benchmark splits** (`manifest_revision.csv`):
- **main:** TP01–TP08 on viable bases
- **stress:** TP09–TP11, TP04–TP06 on load, all 07_traffic
- **control:** TP12 partition, R1/R11 extremes""",
        interpretation="Families cover distinct mobility regimes (urban WDM, campus RWP, vehicles, rural sparse, disaster, social clusters, traffic lab). Each base is crossed with all 12 TPs → 720 total scenarios (e.g. 01_urban: 7 bases × 12 TP = 84).",
        current_status="60 bases documented; family structure mirrors corpus_v1 layout.",
        pending="Finalize main benchmark base list (~40–45) for protocol comparison subset.",
        status="draft",
        links="[04-Traffic-Profiles](04-Traffic-Profiles), [05-Feature-Space](05-Feature-Space)",
        paper="Methods — scenario design table.",
    )

    _add(
        "04-Traffic-Profiles.md",
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

**Docs:** [corpus_v2/README.md](../corpus_v2/README.md)  
**Validation:** [tp_validation_report.md](../analysis/reports/validation/tp_validation_report.md)""",
        interpretation="""Traffic profiles are **designed experimental factors**, not empirical traffic traces. Each TP modifies message generation (`Events*`) and TTL (`Group*.msgTtl`) while holding mobility constant.

TP12 serves as a **partition control** (cross-group messaging); TP04/TP10 are **stress** tiers. Protocol comparisons should hold TP fixed when comparing routers.""",
        current_status="All 12 TPs applied to all 60 bases; validation report available.",
        pending="TP04 message sizes (500k–2M) sufficient after revision? TP05 msgTtl mismatches on U4/U6 documented as intentional.",
        status="stable",
        links="[09-Message-Creation-Time](09-Message-Creation-Time), [11-Message-Analysis-Window](11-Message-Analysis-Window)",
        paper="Methods — traffic workload; experimental design.",
    )

    _add(
        "05-Feature-Space.md",
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
        current_status="Feature extraction pipeline stable; 720 rows in features.csv for corpus_v2.",
        pending="Confirm core-23 list frozen for paper; document any post-revision feature drift.",
        status="stable",
        links="[06-Diversity-Validation](06-Diversity-Validation), [features_core_vs_extended.md](../analysis/docs/features_core_vs_extended.md)",
        paper="Methods — scenario representation; feature table.",
    )

    _add(
        "06-Diversity-Validation.md",
        title="Diversity validation",
        purpose="Document scenario–scenario diversity metrics for the 720-scenario corpus.",
        data_paths="""| Metric | Source |
|--------|--------|
| Canonical results | [RESULTADOS_ACTUALES.md](../analysis/reports/RESULTADOS_ACTUALES.md) |
| Core-23 correlation | [correlation_core23_report.txt](../analysis/reports/pipeline/correlation_core23_report.txt) |
| Full-46 correlation | [correlation_report.txt](../analysis/reports/pipeline/correlation_report.txt) |
| Ablation | [ablation_report.txt](../analysis/reports/pipeline/ablation_report.txt) |
| Feature–feature | [feature_feature_correlation_report.txt](../analysis/reports/pipeline/feature_feature_correlation_report.txt) |
| Paper figures | [figures/paper/main/](../analysis/figures/paper/main/) |

**Frozen metrics (720 scenarios, |r| threshold 0.7):**

| Space | max \\|r\\| | Pairs \\|r\\| ≥ 0.7 | Silhouette (Ward k=7) |
|-------|-----------|-------------------|----------------------|
| Core-23 | 1.0 | 11 325 (4.4%) | 0.3451 (ablation) |
| Full-46 | 1.0 | 8 356 (3.2%) | 0.2680 |

Feature–feature (core): `mm_WDM ↔ mm_Bus = 0.9393`.""",
        interpretation="""Diversity validation ensures scenarios are **not redundant** in configuration space. High |r| pairs indicate similar settings; the corpus aims for broad coverage without claiming uniform low correlation.

Ablation shows core-23 achieves better silhouette (0.3451) than full-46 (0.2680), supporting the 23-feature methodology choice.""",
        current_status="Metrics frozen in RESULTADOS_ACTUALES.md for 720 scenarios.",
        pending="Re-run correlation after any settings revision; update paper figures if metrics shift.",
        status="stable",
        links="[05-Feature-Space](05-Feature-Space), [07-Output-Metrics](07-Output-Metrics), [RESULTADOS_ACTUALES.md](../analysis/reports/RESULTADOS_ACTUALES.md)",
        paper="Methods — diversity validation; Results — correlation/ablation figures.",
    )

    _add(
        "07-Output-Metrics.md",
        title="Output metrics",
        purpose="Define routing benchmark metrics from simulation outputs.",
        data_paths="""| Artifact | Path |
|----------|------|
| Output CSV | `data/output_metrics.csv` (**720 rows**) |
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
        interpretation="""Output metrics measure **routing protocol performance** under each scenario×TP combination. They depend on the default router (EpidemicRouter in baseline runs) and are intended for **benchmark comparison**, not empirical realism claims.

Highlights (720 scenarios): zero delivery in structural cases (TP12), misconfiguration (R1/R11), short TTL; TP04 highest drops/overhead (stress); campus TP01 often high delivery (~0.8+).""",
        current_status="720/720 rows in output_metrics.csv; indirect features available.",
        pending="Apply message analysis window filter before protocol comparison; add hopcount to CSV export if needed.",
        status="needs validation",
        links="[11-Message-Analysis-Window](11-Message-Analysis-Window), [12-Benchmark-Protocol-Comparison](12-Benchmark-Protocol-Comparison)",
        paper="Methods — metrics; Results tables.",
    )

    _add(
        "08-Spatial-Occupancy.md",
        title="Spatial occupancy",
        purpose="Grid-based mobility coverage methodology.",
        data_paths="""| Artifact | Path |
|----------|------|
| Metrics CSV | `data/spatial_occupancy_metrics.csv` (**720 rows**) |
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
        current_status="**720/720** scenarios have spatial metrics and heatmaps.",
        pending="Document MAP_UNDERUSED patterns in revision plan; crop worldSize where recommended.",
        status="stable",
        links="[05-Feature-Space](05-Feature-Space), [10-Simulation-Time-Policy](10-Simulation-Time-Policy)",
        paper="Methods — spatial representativeness; Discussion.",
    )

    _add(
        "09-Message-Creation-Time.md",
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
        current_status="Audit complete for corpus_v2; temporal patterns documented per TP.",
        pending="Link creation-time filters to output_metrics pipeline.",
        status="draft",
        links="[04-Traffic-Profiles](04-Traffic-Profiles), [10-Simulation-Time-Policy](10-Simulation-Time-Policy), [11-Message-Analysis-Window](11-Message-Analysis-Window)",
        paper="Methods — traffic temporal design.",
    )

    _add(
        "10-Simulation-Time-Policy.md",
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
        links="[09-Message-Creation-Time](09-Message-Creation-Time), [11-Message-Analysis-Window](11-Message-Analysis-Window)",
        paper="Methods — simulation duration.",
    )

    _add(
        "11-Message-Analysis-Window.md",
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
        links="[09-Message-Creation-Time](09-Message-Creation-Time), [10-Simulation-Time-Policy](10-Simulation-Time-Policy), [12-Benchmark-Protocol-Comparison](12-Benchmark-Protocol-Comparison)",
        paper="Methods — metric window; required before Results.",
    )

    _add(
        "12-Benchmark-Protocol-Comparison.md",
        title="Benchmark protocol comparison",
        purpose="How to compare routing protocols fairly on corpus_v2.",
        data_paths="""| Artifact | Path |
|----------|------|
| Benchmark splits | `corpus_v2/manifest_revision.csv` |
| Protocol overlays | `analysis/protocol_overlays/` |

**Prerequisites:** message analysis window closed ([11-Message-Analysis-Window](11-Message-Analysis-Window)).""",
        interpretation="""1. **Subset:** `benchmark_split=main` (TP01–TP08, viable bases).
2. **Fixed settings:** same mobility, map, TP; only `Group.router` changes.
3. **Metrics:** primary four from [07-Output-Metrics](07-Output-Metrics).
4. **Window:** TTL-aware message filter (policy B).
5. **Runs:** N seeds or confidence intervals if time permits.

**Stress tier** (TP10, TP04, 07_traffic): report separately. **Control tier** (TP12): validate partition behavior, not delivery ranking.""",
        current_status="Plan documented; **no protocol comparison runs yet**.",
        pending="Select protocol set; run on main split after analysis window implemented.",
        status="draft",
        links="[07-Output-Metrics](07-Output-Metrics), [11-Message-Analysis-Window](11-Message-Analysis-Window), [14-Paper-Freeze-Checklist](14-Paper-Freeze-Checklist)",
        paper="Methods — protocol comparison; Results.",
    )

    _add(
        "13-Dashboard-and-Reproducibility.md",
        title="Dashboard and reproducibility",
        purpose="Interactive exploration and full reproduction pipeline.",
        data_paths="""| Resource | Path |
|----------|------|
| Dashboard | `scenarios/analysis/dashboard.py` (Streamlit) |
| Pipeline index | [SCRIPTS_INDEX.md](../analysis/SCRIPTS_INDEX.md) |
| Analysis README | [README.md](../analysis/README.md) |
| Repo map | [INVENTARIO.md](../INVENTARIO.md) |

**Dashboard pages:** Inicio · Perfiles TP · Explorador · Detalle escenario · Espacial · Auditoría · Pipeline clásico · Reportes crudos""",
        interpretation="""## Official pipeline (12 steps)

See [SCRIPTS_INDEX.md](../analysis/SCRIPTS_INDEX.md) for full commands.

1. Simulation — `run_all_scenarios.py --corpus corpus_v2` + Diego17 + spatial overlays
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
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \\
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \\
  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt
```

## Dashboard

```bash
./venv/bin/streamlit run scenarios/analysis/dashboard.py
```""",
        current_status="Pipeline documented; dashboard operational for corpus_v2 exploration.",
        pending="Pin ONE commit hash in paper; document exact venv/requirements versions.",
        status="stable",
        links="[14-Paper-Freeze-Checklist](14-Paper-Freeze-Checklist), [SCRIPTS_INDEX.md](../analysis/SCRIPTS_INDEX.md)",
        paper="Reproducibility appendix.",
    )

    _add(
        "14-Paper-Freeze-Checklist.md",
        title="Paper freeze checklist",
        purpose="Gate before claiming final results.",
        data_paths="See [paper_phase1_action_plan.md](../analysis/reports/paper_gate/paper_phase1_action_plan.md)",
        interpretation="All items must pass before submission claims.",
        current_status="""- [x] Regenerate output_metrics (720/720)
- [x] Regenerate spatial metrics (720/720)
- [x] Diversity metrics frozen ([RESULTADOS_ACTUALES.md](../analysis/reports/RESULTADOS_ACTUALES.md))
- [ ] **Message analysis window implemented in pipeline**
- [ ] Re-run diagnosis; P0 scenarios resolved or excluded
- [ ] Freeze `manifest_revision.csv` into main manifest
- [ ] Protocol comparison on main split complete
- [ ] Methods text matches actual scripts
- [ ] Limitations section includes map/traffic/synthetic disclaimers""",
        pending="Protocol comparison blocked until analysis window closed.",
        status="draft",
        links="[06-Diversity-Validation](06-Diversity-Validation), [11-Message-Analysis-Window](11-Message-Analysis-Window), [13-Dashboard-and-Reproducibility](13-Dashboard-and-Reproducibility)",
        paper="Internal checklist before submission.",
    )

    _add(
        "References.md",
        title="References",
        purpose="Pointers to external documentation.",
        data_paths="- The ONE Simulator — [GitHub](https://github.com/understandable-machine-intelligence-lab/one)\n- Repo: `scenarios/analysis/reports/` for generated methodology supplements",
        interpretation="Keränen et al. — opportunistic networking context.",
        current_status="Draft bibliography.",
        pending="Add BibTeX entries for paper.",
        status="draft",
        links="[Home](Home)",
        paper="Bibliography.",
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
        links="[Home](Home), [04-Traffic-Profiles](04-Traffic-Profiles)",
        paper="Optional glossary in thesis.",
    )

    _add(
        "CHANGELOG.md",
        title="Wiki changelog",
        purpose="Track wiki rebuild history.",
        data_paths="Backups: `scenarios/_archive/wiki/wiki_backup_*`",
        interpretation="N/A",
        current_status=f"""- **{_utc()}:** Round2 restructure — 18-page flat taxonomy (05-Feature-Space … 13-Dashboard-and-Reproducibility); metrics updated to 720; spatial 720/720.
- **2026-05-20 11:41 UTC:** Full rebuild (paper-oriented). Old wiki in `wiki_backup_20260520_133832/`.""",
        pending="N/A",
        status="draft",
        links="[Home](Home)",
        paper="N/A",
    )


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
    build_pages()
    if not WIKI.is_dir():
        print("Wiki dir missing", file=sys.stderr)
        return 1

    _archive_obsolete_root()

    for name, content in PAGES.items():
        (WIKI / name).write_text(content, encoding="utf-8")
        print(f"Wrote {WIKI / name}")

    (WIKI / "README.md").write_text(
        "# Wiki clone directory\n\n"
        "See [Home.md](Home.md) for the paper-oriented documentation.\n\n"
        "Structure: 18 flat EN pages (01–14 + Glossary + References + CHANGELOG).\n\n"
        "Legacy: `_legacy_pre_paper_rebuild/` (v1 wiki + round2 superseded pages).\n\n"
        "Backup: `scenarios/_archive/wiki/wiki_backup_20260523_*`.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
