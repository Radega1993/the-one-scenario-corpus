# Guía de documentación de escenarios

Esta guía define la **estructura estándar, lista para paper** para documentar cada escenario en la wiki, y de dónde debe salir cada sección (settings vs artefactos del análisis).

## Qué documentar por escenario (mínimo recomendado)

Usa la plantilla por escenario en `05-corpus/scenarios-es/Scenario-template-es.md` (y su equivalente EN).

### 1) Visión general (narrativa)

- **Fuente:** la intención del escenario (racional de diseño).
- **Incluye:** qué fenómeno modela, por qué existe en el corpus, y qué “palanca(s)” controla (p. ej. TTL, tasa de tráfico, régimen de movilidad, mapa).

### 2) Configuración del escenario (core 23)

- **Fuente (valores):** `scenarios/analysis/data/features.csv` (valores extraídos raw), usando la **lista core 23** de `scenarios/analysis/reports/RESULTADOS_ACTUALES.md`.
- **Cómo:** copia las 23 features core del escenario a la tabla; mantén unidades consistentes (m, s, bytes).
- **Por qué:** es la vista más compacta y comparable (base directa del paper).

### 3) Modelo de movilidad (descripción “en humano”)

- **Fuente:** el fichero `.settings`, sobre todo `MovementModel.*` y `Group*.movementModel` (más parámetros específicos del modelo).
- **Incluye:** tamaño/mapa, régimen de movimiento, heterogeneidad (múltiples grupos), y el ritmo diario (si WDM).

### 4) Patrón de tráfico (humano + settings clave)

- **Fuente:** el `.settings`, sobre todo `Events.nrof`, `Events1.*`, y opcional `Events2.*`.
- **Incluye:** intervalo/tasa, rango/distribución de tamaños, patrón (uniform vs burst vs hub-target), y nº de flujos.

### 5) Características distintivas (bullets)

- **Fuente:** tu intención + la tabla core 23.
- **Incluye:** 3–6 bullets describiendo diferencias estructurales (no solo “tocar un parámetro”).

### 6) Correlación con otros escenarios (core 23)

- **Fuente:** `scenarios/analysis/data/correlation_pearson_core23.csv` (o el resumen en `scenarios/analysis/reports/correlation_core23_report.txt`).
- **Incluye:** top-3 más similares y top-3 más diferentes (por menor \(|r|\)).
- **Por qué:** conecta la narrativa con la validación de diversidad.

### 7) Asignación de cluster

- **Fuente:** `scenarios/analysis/data/cluster_assignments_core23.csv` (Ward, k=7).
- **Incluye:** id de cluster y una interpretación corta (basada en los miembros del cluster).

### 8) Posición PCA (opcional)

- **Fuente:** `scenarios/analysis/figures/` (scatter PCA) o una tabla exportada en el futuro.
- **Incluye:** PC1/PC2 si decidís “congelar” esas coordenadas para el paper.

### 9) Parámetros adicionales no-core (opcional, pero útil)

- **Fuente:** campos de `.settings` importantes para interpretar pero no incluidos en core 23 (p. ej. detalles WDM como `nrOfOffices`, `nrOfMeetingSpots`, colas pesadas).
- **Regla:** incluir solo parámetros que cambien la interpretación científica.

### 10) Outputs de simulación (opcional, si existe)

- **Fuente:** `scenarios/analysis/data/output_metrics.csv`.
- **Incluye:** delivery ratio, latency mean, overhead ratio, drop ratio.
- **Nota:** los outputs dependen del protocolo y de la ejecución; dejarlos claramente como “opcional”.

## Regla de bilingüismo (EN/ES)

- **Mantener numeración idéntica** entre páginas EN y ES (facilita diffs y export al paper).
- **Tablas alineadas** (mismo orden de filas) para core 23 y outputs.
- **Traducir narrativa, no nombres de variables:** mantener los nombres de features (`world_area`, `event_interval_mean`, etc.) sin traducir.

## Checklist de consistencia (copy/paste)

- [ ] Scenario ID, nombre, familia y ruta del settings correctos.
- [ ] La tabla core 23 coincide con `analysis/data/features.csv`.
- [ ] La sección de correlación cita artefactos core23.
- [ ] El cluster coincide con `cluster_assignments_core23.csv`.
- [ ] Los outputs (si están) coinciden con `output_metrics.csv`.
