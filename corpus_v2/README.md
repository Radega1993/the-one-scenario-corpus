# corpus_v2 — Benchmark de trafico (v1.0, generado completo)

`corpus_v2` es la expansion de `corpus_v1` para comparar protocolos de routing bajo
perfiles de mensajes controlados.

La idea es separar:

- **Escenario base**: movilidad, mapa, nodos, interfaces, buffers.
- **Perfil de trafico**: generacion de mensajes (`Events*`) y TTL (`Group*.msgTtl`).

Estado actual: corpus completo generado (**60 escenarios base x 12 perfiles = 720 escenarios**).
El piloto de 36 simulaciones se mantiene como evidencia de validacion inicial.

---

## Estado actual

- Base de generacion: [`../corpus_v1`](../corpus_v1)
- Generador: [`../analysis/generate_corpus_v2_traffic.py`](../analysis/generate_corpus_v2_traffic.py)
- Artefacto de trazabilidad: `manifest.csv` (una fila por `.settings` generado)
- Documentacion metodologica extensa: [`../internal/15-corpus_v2_traffic_benchmark.md`](../internal/15-corpus_v2_traffic_benchmark.md)
- Conteo actual: **720** `.settings` y **720** filas en `manifest.csv` (consistente por familia y TP).

---

## Organizacion del directorio

Se mantiene el espejo por familias de `corpus_v1`:

- `01_urban/`
- `02_campus/`
- `03_vehicles/`
- `04_rural/`
- `05_disaster/`
- `06_social/`
- `07_traffic/`

Cada archivo representa:

`escenario_base + perfil_de_trafico`

Ejemplo:

`U1_CBD_Commuting_HelsinkiMedium__TP03_ManySmall.settings`

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
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --name-regex '(U1_CBD_Commuting_HelsinkiMedium|R1_Rural_RandomWaypoint|D2_PartitionedCity_MuleBridge)__TP' \
  --extra-settings scenarios/analysis/diego17_reports_overrides.txt \
  --timeout 14400
```

Analisis tras simulacion:

```bash
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase output_metrics
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase indirects
```

Reportes resultantes del piloto:

- `scenarios/analysis/reports/piloto_corpus_v2_36_resultados.md`
- `scenarios/analysis/reports/go_no_go_corpus_v2_12perfiles.md`
- `scenarios/analysis/reports/check_tp12_d2.md`
- `scenarios/analysis/reports/resumen_tp_excluyendo_no_contacto.md`

---

## Criterios antes de escalar a todo el corpus

Checklist metodologico para ejecuciones masivas (por protocolo/seed):

- Verificar que los nuevos TP (`TP06/TP11/TP12`) diferencian resultados de forma no trivial.
- Confirmar que no hay sobrescritura en `reports/` (garantizado por `Scenario.name` unico).
- Revisar cobertura rural (R1 como control extremo y al menos un rural con contactos reales).
- Validar que `output_metrics.csv` e `indirect_features_diego.csv` reflejan el piloto esperado.

Reportes de decision/check del piloto:

- `scenarios/analysis/reports/go_no_go_corpus_v2_12perfiles.md`
- `scenarios/analysis/reports/check_tp12_d2.md`
- `scenarios/analysis/reports/resumen_tp_excluyendo_no_contacto.md`

---

## Regeneracion

Regenerar todo `corpus_v2` (sobrescribe carpeta + `manifest.csv`):

```bash
python3 scenarios/analysis/generate_corpus_v2_traffic.py
```

Nota: si cambias definicion de perfiles, recomienda borrar y regenerar:

```bash
rm -rf scenarios/corpus_v2
python3 scenarios/analysis/generate_corpus_v2_traffic.py
```
