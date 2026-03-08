# Objetivos de diversidad y cómo cumplirlos

Resumen de métricas actuales vs objetivo y pasos para acercarse a los resultados esperados.

## Estado actual vs objetivo

| Métrica | Actual | Objetivo | Cumplido |
|---------|--------|----------|----------|
| Escenarios | 70 | — | ✓ |
| Features (d) | 46 | — | ✓ |
| Pearson max \|r\| | 0,938 | &lt; 0,85 (realista) | No |
| Pares con \|r\| ≥ 0,7 | 98 (4,1 %) | &lt; 3 % (~72 pares) | En progreso |
| Pares con \|r\| &lt; 0,7 | 95,9 % | ≥ 95 % | ✓ |
| Distancia coseno mín | 0,0527 | &gt; 0,05 | ✓ |
| Pares con cos_dist &lt; 0,05 | 0 | 0 | ✓ |
| Silhouette (k=7) | 0,294 | &gt; 0,3 | Cercano |

## Cómo trabajar para cumplir los objetivos

### 1. Reducir pares con |r| ≥ 0,7 (objetivo ≥95 % con |r| &lt; 0,7)

- **Lista de trabajo:** `reports/scenarios_to_diversify.txt` — escenarios que más contribuyen a pares correlacionados (ordenados por número de pares con |r| ≥ 0,7).
- **Acción:** Modificar esos escenarios para que su **vector de features** difiera más del resto:
  - Cambiar mapa o tamaño del mundo (Wx, Wy) donde sea razonable.
  - Variar movilidad (speed, waitTime, modelo de movimiento) sin romper el concepto del escenario.
  - Variar tráfico (interval, size, msgTtl, patrón burst/hub) o recursos (bufferSize, transmitSpeed, transmitRange).
- **Prioridad:** Empezar por los que tienen más pares altos (V4_MixedBusPed, U4_RainyDay, V6_CarOwnership_0, etc.).

### 2. Mejorar Silhouette (k=7)

- Silhouette bajo indica que los clusters (Ward, k=7) no están bien separados: muchos escenarios están “entre” clusters.
- **Acción:** Aumentar la diversidad **entre familias** (Urban, Campus, Vehicle, Rural, Disaster, Social, Traffic): que cada familia tenga un perfil de features más distintivo (por ejemplo, más variación en mm_*, density, event_interval_mean, msgTtl entre familias).

### 3. No empeorar lo que ya cumple

- **Distancia coseno mín &gt; 0,05:** Mantener; no añadir escenarios casi idénticos en features.
- **Features utilizados:** Ver `reports/features_report.md` (46 features) y `reports/features_decision.md` (decisión AÑADIR/DESCARTAR por setting).

## Trabajo en escenarios (en curso)

- **Prioridad 1:** Pares con mayor |r|: ver `reports/correlation_report.txt` y `scenarios_to_diversify.txt`.
- **Acción:** Modificar uno de los dos escenarios del par para que el vector de features difiera (**worldSize**, nrOfHosts, transmitRange, speed, waitTime, event interval/size, bufferSize, msgTtl), **sin sacar el escenario de su grupo** (Traffic, Social, Rural, Disaster, Vehicle, Campus, Urban).
- **Hecho (diversificación estructural como en V4–V5, en todos los pares de alta correlación):**
  - **HelsinkiMedium (Urban/Vehicle):** V5 worldSize 6000×5000, N=59; U4 5500×4500; U6 7000×6000; U7 7200×6200; V6 6500×5500; V8 5800×4800; U8 6600×5600; U9 7400×6400; U12 7700×6700.
  - **Traffic (07_traffic):** T10 6600×4200 N=48; T15 3800×3000 N=28; T5 5500×4500 N=40; T9 6200×4800 N=48; T13 7200×5600 N=30; T11 4200×3400 N=30; T12 5800×4800 N=42; T14 4600×3600 N=46; T4 6000×4400 N=42; T6 5600×4600 N=42; T1 5000×3800 N=36.
  - **Social (06_social):** S3 4000×3200 N=50; S4 6800×5300 N=60.
  - **Rural (04_rural):** R10 7600×5600 N=32; R11 10500×8500 N=28; R5 8500×6000 N=26; R7 9500×7500 N=38; R4 7800×6800 (HelsinkiMedium).
  - **Disaster (05_disaster):** D3 6600×5600 N=54; D9 7800×5800 N=44; D6 6800×5000 N=54; D5 8200×7200 (HelsinkiMedium); D1 5600×4600.
  - **Vehicle (03_vehicles):** V2 6200×5200 N=26 (HelsinkiMedium).
  - **Campus (02_campus):** C2 750×550 N=48; C7 550×450 N=42; C5 8000×7000; C6 8200×7200 (HelsinkiMedium).
- **Resultado:** max |r| 0,949 → **0,938**; pares con |r|≥0,7: 106 → **98**; cos mín > 0,05 (0 pares con cos_dist < 0,05). Todos los escenarios siguen en su grupo (carpeta/familia).
- Tras cada cambio: `run_analysis.py --corpus corpus_v1 --phase all` y revisar `correlation_report.txt`.

## Regenerar métricas

Tras cambiar escenarios o añadir nuevos:

```bash
cd scenarios
python3 analysis/run_analysis.py --corpus corpus_v1 --phase all
```

Los números actualizados estarán en `reports/correlation_report.txt` y en las figuras en `figures/`.
