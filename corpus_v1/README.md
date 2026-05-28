# corpus_v1 — Benchmark ambiental con Traffic Profiles (paper)

`corpus_v1/` contiene **540** escenarios del benchmark ambiental (familias `01_urban` … `06_social`) con perfiles de tráfico (TP) aplicados según `analysis/data/benchmark_definition.csv`.

Los **15 escenarios de laboratorio** de la familia `07_stress_controls` viven en [`../stress_controls/`](../stress_controls/) (30 simulaciones: TP01 + TP10).

Las **45 bases estructurales** sin TP están en [`../base_scenarios/`](../base_scenarios/).

**Total paper benchmark:** **570** simulaciones (`corpus_v1` + `stress_controls`). El nombre histórico `corpus_v2` fue renombrado en la reorganización de 2026-05-27 (ver [`../CHANGELOG.md`](../CHANGELOG.md)).

---

## Estado actual

- Bases estructurales: [`../base_scenarios/`](../base_scenarios/) (45 `.settings`)
- Benchmark TP ambiental: este directorio (540 `.settings`)
- Stress/control: [`../stress_controls/`](../stress_controls/) (30 `.settings`)
- Manifest combinado: [`../analysis/data/corpus_v1_combined_manifest.csv`](../analysis/data/corpus_v1_combined_manifest.csv)
- Definiciones TP: [`../analysis/lib/traffic_profile_generator.py`](../analysis/lib/traffic_profile_generator.py)
- Validación bases: [`../analysis/reports/base_scenarios_validation.md`](../analysis/reports/base_scenarios_validation.md)

---

## Organización del directorio

Solo familias ambientales (sin `07_stress_controls`):

- `01_urban/`
- `02_campus/`
- `03_vehicles/`
- `04_rural/`
- `05_disaster/`
- `06_social/`

Cada archivo representa `escenario_base + perfil_de_trafico`, p. ej.:

`U1_CBD_Commuting_HelsinkiDowntown__TP03_ManySmall.settings`

---

## Campos nuevos / cambios clave en .settings

### 1) `Scenario.name` unico por perfil

Para evitar sobrescritura de reportes en `reports/`, cada variante incorpora el perfil en
`Scenario.name`:

- base: `U1_CBD_Commuting_HelsinkiMedium`
- variante: `U1_CBD_Commuting_HelsinkiMedium__TP03_ManySmall`

Esto permite correr varios TP del mismo escenario y conservar resultados separados.

### 2) Bloque `Events*` reemplazado por perfil

El generador sustituye el bloque de trafico por uno definido por TP:

- `Events.nrof`
- `Events1/Events2.class`
- `Events*.interval`
- `Events*.size`
- `Events*.hosts`
- `Events*.tohosts`
- `Events*.time` (cuando aplica, p.ej. burst)
- `Events*.prefix`

### 3) TTL por `Group*.msgTtl` (no por `Events1.ttl`)

En este fork de The ONE, `MessageEventGenerator` no expone `Events1.ttl`.
El TTL efectivo se controla con:

- `Group.msgTtl`
- `GroupN.msgTtl`

El generador sobrescribe esos campos por perfil, y si no existe `Group.msgTtl`, lo inserta.

### 4) `manifest.csv`

Incluye (minimo):

- `family`
- `scenario_base`
- `scenario_name`
- `traffic_profile_id`
- `traffic_profile_name`
- `settings_file`
- `n_hosts`
- `Scenario.endTime`
- `Group.msgTtl_minutes`
- campos de `Events` relevantes
- `note` para fallbacks

---

## Perfiles TP (decision actual)

Actualmente el benchmark usa **12 perfiles**:

- `TP01_Baseline`
- `TP02_LowLoad`
- `TP03_ManySmall`
- `TP04_FewLarge`
- `TP05_CriticalTTL`
- `TP06_OneToMany` (reemplaza el antiguo LongTTL por redundancia)
- `TP07_BurstWindow`
- `TP08_HubTarget`
- `TP09_Bimodal`
- `TP10_Storm`
- `TP11_ManyToOne`
- `TP12_GroupToGroup`

Decisiones importantes:

- Se detecto que `TP06_LongTTL` era practicamente redundante con `TP01` en el piloto inicial.
- Se priorizo direccionalidad explicita (`1->n`, `n->1`, `group->group`) por valor para Fase 2.
- **Battery freeze (trafico):** `Traffic Profiles v1.0 = TP01..TP12`.

---

## Piloto en validacion (36 escenarios)

Mientras validamos, el foco es:

- U1 (urbano)
- D2 (disaster)
- R1 (rural extremo, usado como **disconnected control scenario**)

con `TP01..TP12`.

Comando de piloto:

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
  --name-regex '(U1_CBD_Commuting_HelsinkiMedium|R1_Rural_RandomWaypoint|D2_PartitionedCity_MuleBridge)__TP' \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --timeout 14400 --jobs 6
```

Analisis tras simulacion:

```bash
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase output_metrics
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase indirects
```

Reportes resultantes del piloto:

- `scenarios/_archive/reports/piloto_corpus_v1_36_resultados.md`
- `scenarios/_archive/reports/go_no_go_corpus_v1_12perfiles.md`
- `scenarios/analysis/reports/_archive_local/check_tp12_d2.md`
- `scenarios/analysis/reports/_archive_local/resumen_tp_excluyendo_no_contacto.md`

---

## Criterios antes de escalar a todo el corpus

Checklist metodologico para ejecuciones masivas (por protocolo/seed):

- Verificar que los nuevos TP (`TP06/TP11/TP12`) diferencian resultados de forma no trivial.
- Confirmar que no hay sobrescritura en `reports/` (garantizado por `Scenario.name` unico).
- Revisar cobertura rural (R1 como control extremo y al menos un rural con contactos reales).
- Validar que `output_metrics.csv` e `indirect_features_diego.csv` reflejan el piloto esperado.

Recomendación operacional para ejecución masiva:

- Usar paralelización con `--jobs` en `run_all_scenarios.py` (inicio sugerido: `--jobs 4` o `--jobs 6`).
- En esta máquina (`16` cores), un rango estable suele ser `--jobs 6..8`.
- No ejecutar dos barridos completos simultáneos sobre el mismo `reports/`.

Reportes de decision/check del piloto:

- `scenarios/_archive/reports/go_no_go_corpus_v1_12perfiles.md`
- `scenarios/analysis/reports/_archive_local/check_tp12_d2.md`
- `scenarios/analysis/reports/_archive_local/resumen_tp_excluyendo_no_contacto.md`

---

## Regeneracion

El corpus está **congelado** (720 escenarios). El generador histórico `generate_corpus_v1_traffic.py` fue eliminado; recuperar desde `analysis/scripts_backup_20260524_184900.tar.gz` o git si hace falta regenerar desde `corpus_v1`.
