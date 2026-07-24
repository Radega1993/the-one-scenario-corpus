# Generated Map Space v1 (GMS)

Casa canónica del **Generated / Geometric Map Space v1**: pool de mapas generados, configs, scripts, docs, datos de saturación, figuras y trazas externas.

> Resumen operativo de la fase. Cada apartado enlaza al fichero con el detalle completo **dentro de este directorio**.
> TOC de comandos y docs: [`INDEX.md`](INDEX.md).

## 1. Identidad y estado

| Campo | Valor |
|------|--------|
| Directorio | este pack (`Generated_Map_Space_v1/`) |
| Nombre científico / IDs de artefacto | histórico `map_space_revised_v2_*` (no renombrados) |
| Decisión | **`STOP_AMENDED_CEILING_2000`** @ N=**1860** |
| GMS | **`freeze_candidate`** (falta aceptación explícita de freeze) |
| SMS | bloqueado hasta freeze GMS |
| Techo planificado | 2000 candidatos en manifest |

**Decisión oficial:** [`data/map_space_revised_v2_saturation_decision.json`](data/map_space_revised_v2_saturation_decision.json)  
**Go / no-go metodológico:** [`docs/map_generation_v2_methodological_readiness.md`](docs/map_generation_v2_methodological_readiness.md)  
**Decisión original (pre-enmienda):** [`data/map_space_revised_v2_saturation_decision_ceiling_no_stop.json`](data/map_space_revised_v2_saturation_decision_ceiling_no_stop.json) (`CEILING_2000_NO_STOP`)

## 2. Qué es esta fase

Objetivo: construir y **saturar empíricamente** un espacio geométrico de mapas para The ONE, con:

- **15 arquetipos** de topología (urban grid, campus, rural, hub-and-spoke, …)
- **3 fuentes de construcción:** `osm`, `synthetic`, `trace_reference_synthetic`
- Protocolo de saturación estratificada pre-registrado + enmienda documentada al techo 2000
- Pool de mapas WKT en `batch_*/wkt/` (+ previews, manifest, osm_cache)

**Arquitectura y diseño:** [`docs/map_generation_architecture_v2.md`](docs/map_generation_architecture_v2.md)  
**Justificación de arquetipos:** [`docs/history/map_archetype_justification_v1.md`](docs/history/map_archetype_justification_v1.md)
**Definiciones de arquetipo:** [`data/map_archetype_definitions_v1.csv`](data/map_archetype_definitions_v1.csv)

## 3. Pipeline de la fase

```mermaid
flowchart LR
  plan[Plan_dry_run]
  gen[Generate_pool]
  val[Validate]
  reval[Revalidate_attrition]
  feat[Extract_features]
  sat[Stratified_saturation]
  stop[STOP_amendment]
  plan --> gen --> val --> reval --> feat --> sat --> stop
```

| Etapa | Script / config | Resultado clave | Detalle completo |
|-------|-----------------|-----------------|------------------|
| Plan / dry-run | [`scripts/generate.py`](scripts/generate.py) + [`config/map_design_space.yaml`](config/map_design_space.yaml) | Plan reproducible (seed 42); sin descargas | [`docs/map_generation_v2_dry_run.md`](docs/map_generation_v2_dry_run.md) |
| Generación | `generate.py --generate` | Manifest 2000; OK **1865** (93.2%) | [`docs/map_generation_revised_v2_run.md`](docs/map_generation_revised_v2_run.md), [`manifest_maps_all.csv`](manifest_maps_all.csv) |
| Validación geométrica | [`scripts/validate.py`](scripts/validate.py) | PASS **1741** / STRESS **119** / FAIL **140** | [`docs/map_space_revised_v2_validation_report.md`](docs/map_space_revised_v2_validation_report.md) |
| Revalidación / attrition | [`scripts/analyze_revalidation.py`](scripts/analyze_revalidation.py) | Cobertura archetype×source OK; GO a saturación | [`docs/map_space_revised_v2_pool_revalidation_attrition.md`](docs/map_space_revised_v2_pool_revalidation_attrition.md) |
| Features | [`scripts/extract_features.py`](scripts/extract_features.py) | **1860** mapas × **33** dims; transform freeze n1117 | [`docs/map_space_revised_v2_saturation_features_report.md`](docs/map_space_revised_v2_saturation_features_report.md) |
| Saturación | [`scripts/analyze_saturation.py`](scripts/analyze_saturation.py) + [`config/saturation_protocol.yaml`](config/saturation_protocol.yaml) | C(ε)→1.0, D95→0 @1860; original `CEILING_2000_NO_STOP` | [`docs/map_space_revised_v2_saturation_report.md`](docs/map_space_revised_v2_saturation_report.md) |
| Diagnóstico STOP | enmienda [`config/saturation_protocol_amendment_ceiling_2000.yaml`](config/saturation_protocol_amendment_ceiling_2000.yaml) | `STOP_AMENDED_CEILING_2000` → freeze_candidate | [`docs/stop_diagnostics_ceiling_2000.md`](docs/stop_diagnostics_ceiling_2000.md) |

## 4. Inventario del directorio

| Path | Qué es |
|------|--------|
| [`config/`](config/) | Design space, protocolo de saturación (+ enmienda), allocation por arquetipo, política traza→mapa |
| [`scripts/`](scripts/) | CLI GMS: generate, validate, extract_features, analyze_*; paquete `map_generation/`; builders `map_space_*.py`; helpers OSM |
| [`docs/`](docs/) | Informes de fase (validación, features, saturación, STOP, arquitectura, audit) |
| [`docs/history/`](docs/history/) | Rationale de arquetipos, inventario de trazas, review traza→generación |
| [`data/`](data/) | Features, bands/metrics, decisions, transform freeze, plan CSV, revalidation CSVs |
| [`figures/saturation/`](figures/saturation/) | Curvas C(ε), D95, ΔC/100 vs N |
| [`downloaded_external_traces/`](downloaded_external_traces/) | Registry + raw/processed de trazas reales usadas por GMS |
| `batch_0100` … `batch_2000/` | Pool WKT + metadata por tramo de generación |
| [`previews/`](previews/) | PNGs de mapa generados |
| [`osm_cache/`](osm_cache/) | Caché de descargas OSM (grande; regenerable) |
| [`manifest_maps_all.csv`](manifest_maps_all.csv) | Inventario completo de candidatos (OK + FAIL) |
| [`ops/`](ops/) | Logs operativos (p.ej. expansiones OSM) |

## 5. Resultados por etapa (números congelados)

### 5.1 Generación @ techo 2000

- Filas en manifest: **2000**
- OK: **1865** (OSM 847 / synthetic 715 / TRS 303; cifras de revalidación)
- Fallos documentados: **135** (83 `FAIL_BUILD_SYNTHETIC_DEGENERATE` + 52 `FAIL_BUILD_OSM`)
- Fallos se conservan en manifest (sin sesgo de supervivencia documental)

Completo: [`docs/map_space_revised_v2_pool_revalidation_attrition.md`](docs/map_space_revised_v2_pool_revalidation_attrition.md)  
Fallos sintéticos: [`docs/synthetic_generation_failure_analysis_v2.md`](docs/synthetic_generation_failure_analysis_v2.md)

### 5.2 Validación

Sobre 2000 mapas validados:

| Outcome | N |
|---------|--:|
| PASS | 1741 |
| STRESS | 119 |
| FAIL | 140 |

Por fuente (PASS/STRESS/FAIL): OSM 847/0/52; synthetic 629/81/88; TRS 265/38/0.

Completo: [`docs/map_space_revised_v2_validation_report.md`](docs/map_space_revised_v2_validation_report.md) · CSV [`data/map_space_revised_v2_validation.csv`](data/map_space_revised_v2_validation.csv)

### 5.3 Features

- Mapas con features: **1860** (PASS+STRESS usable; 140 FAIL excluidos)
- Dimensiones geométricas: **33** (sin one-hot de `source_type`)
- Transform freeze: [`data/map_space_revised_v2_feature_transform_freeze_n1117.json`](data/map_space_revised_v2_feature_transform_freeze_n1117.json)
- ε (percentil 20 de distancias 5-NN): **≈ 0.3566**

Completo: [`docs/map_space_revised_v2_saturation_features_report.md`](docs/map_space_revised_v2_saturation_features_report.md) · [`data/map_space_revised_v2_saturation_features.csv`](data/map_space_revised_v2_saturation_features.csv)

### 5.4 Saturación estratificada

- Permutaciones R=**100** (nested round-robin estratificado)
- Escalera hasta N=1860: C(ε) mediana → **1.0**, D95 → **0**
- STOP **original** no metido → `CEILING_2000_NO_STOP`
- Tras enmienda documentada (suelo D95≤ε, cola ΔC, ΔC raw en peldaño corto, need=2) → **`STOP_AMENDED_CEILING_2000`**
- Strata críticas: **no hot** → no `TARGETED_EXPAND`

Completo: [`docs/map_space_revised_v2_saturation_report.md`](docs/map_space_revised_v2_saturation_report.md)  
Diagnóstico: [`docs/stop_diagnostics_ceiling_2000.md`](docs/stop_diagnostics_ceiling_2000.md)  
Figuras: [`figures/saturation/`](figures/saturation/) (`coverage_C_eps_vs_N.png`, `D95_vs_N.png`, `delta_C_per_100_vs_N.png`)  
Bands/metrics: [`data/map_space_revised_v2_saturation_bands.csv`](data/map_space_revised_v2_saturation_bands.csv), [`data/map_space_revised_v2_saturation_metrics.csv`](data/map_space_revised_v2_saturation_metrics.csv)

## 6. Configs, scripts e history

### Config

| Fichero | Rol |
|---------|-----|
| [`config/map_design_space.yaml`](config/map_design_space.yaml) | Espacio de diseño (clave histórica `map_design_space_revised_v2`) |
| [`config/saturation_protocol.yaml`](config/saturation_protocol.yaml) | STOP pre-registrado |
| [`config/saturation_protocol_amendment_ceiling_2000.yaml`](config/saturation_protocol_amendment_ceiling_2000.yaml) | Enmienda post-hoc al techo 2000 |
| [`config/archetype_source_allocation.yaml`](config/archetype_source_allocation.yaml) | Cuotas archetype × source |
| [`config/trace_to_map_generation_policy.yaml`](config/trace_to_map_generation_policy.yaml) | Roles de trazas → generación |

Rationale allocation: [`docs/archetype_source_allocation_rationale_v2.md`](docs/archetype_source_allocation_rationale_v2.md)  
Mapeo traza→parámetros: [`docs/trace_to_geometry_parameter_mapping_v2.md`](docs/trace_to_geometry_parameter_mapping_v2.md)

### Scripts principales

| Script | Rol |
|--------|-----|
| [`scripts/generate.py`](scripts/generate.py) | Plan / dry-run / generate |
| [`scripts/map_generation/`](scripts/map_generation/) | Planner, executor, builders, traces, provenance |
| [`scripts/validate.py`](scripts/validate.py) | Validación del pool |
| [`scripts/extract_features.py`](scripts/extract_features.py) | Features de saturación |
| [`scripts/analyze_saturation.py`](scripts/analyze_saturation.py) | Curvas + decisión STOP |
| [`scripts/analyze_revalidation.py`](scripts/analyze_revalidation.py) | Attrition / cobertura |
| [`scripts/map_space_osm_builder.py`](scripts/map_space_osm_builder.py) / [`map_space_synthetic*.py`](scripts/map_space_synthetic.py) / [`map_space_topology.py`](scripts/map_space_topology.py) / [`map_space_preview.py`](scripts/map_space_preview.py) | Builders y topología del pool (viven en este pack) |
| [`scripts/watch_osm_progress.sh`](scripts/watch_osm_progress.sh) / [`run_osm_until_ok.sh`](scripts/run_osm_until_ok.sh) | Ops OSM |

`PYTHONPATH` incluye `../setup` solo por el helper compartido `map_geometry` (no es artefacto GMS).

### History (rationale de fase)

- [`docs/history/map_archetype_justification_v1.md`](docs/history/map_archetype_justification_v1.md)
- [`docs/history/map_real_trace_inventory_and_anchor_rationale_v1.md`](docs/history/map_real_trace_inventory_and_anchor_rationale_v1.md)
- [`docs/history/trace_to_map_generation_review_v1.md`](docs/history/trace_to_map_generation_review_v1.md)

Otros docs útiles: audit [`docs/map_generation_audit_v2.md`](docs/map_generation_audit_v2.md), changelog refactor [`docs/map_generator_refactor_changelog_v2.md`](docs/map_generator_refactor_changelog_v2.md), OSM anchors [`docs/osm_anchor_redundancy_review_v2.md`](docs/osm_anchor_redundancy_review_v2.md).

## 7. Comandos (desde este pack)

```bash
cd scenarios/Generated_Map_Space_v1
# scripts = pack; ../setup = solo map_geometry (compartido)
export PYTHONPATH=scripts:../setup

# Dry-run
python scripts/generate.py \
  --config config/map_design_space.yaml \
  --dry-run --write-plan --target-total 90 --seed 42

# Generar / validar / features / saturación
python scripts/generate.py \
  --config config/map_design_space.yaml \
  --generate --source synthetic --target-total 1600 --seed 42
python scripts/validate.py
python scripts/extract_features.py --geometry-only-normalized
python scripts/analyze_saturation.py

# OSM
bash scripts/watch_osm_progress.sh --once
```

## 8. Alcance de este directorio

Este directorio es la **casa canónica** de GMS-v1: pool, config, scripts (incl. builders), docs, data, figures y trazas.

## 9. Siguiente acción humana

Aceptar el **freeze** formal de GMS-v1 (bloquear pool + artefactos de decisión). Hasta entonces SMS-v1 no arranca.
