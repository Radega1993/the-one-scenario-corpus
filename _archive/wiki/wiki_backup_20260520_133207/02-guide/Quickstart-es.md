# Quickstart

**Español** | [English](Quickstart)

---

Poner en marcha el corpus: instalar dependencias, ejecutar escenarios, ejecutar el pipeline de análisis y abrir el dashboard.

---

## Requisitos

Ver **[Instalación](Installation-es)** para configuración paso a paso (clonar ONE, compilar, venv Python, verificar).

- **Java** (p. ej. OpenJDK 11+) — para el simulador The ONE
- **The ONE** — compilado desde fuentes (`./compile.sh` en la raíz del ONE)
- **Python 3** con: `numpy`, `pandas`, `scipy`, `matplotlib`, `streamlit`
- **Repositorio** — solo el corpus de escenarios o el repo completo del ONE con `scenarios/` dentro (o enlazado)

---

## Estructura del proyecto

Estructura típica:

- **Raíz del ONE** (p. ej. `the-one/` o `the-one-scenario-corpus/`) — contiene `one.sh`, `compile.sh`, `default_settings.txt`, `reports/` (donde el ONE escribe los reportes)
- **scenarios/** — contiene `corpus_v1/`, `analysis/`, README, ROADMAP y esta wiki

Si el corpus de escenarios es un **repo separado**, ejecuta el ONE desde su repo y apunta los scripts a la ruta donde clonaste los scenarios (p. ej. `--corpus /ruta/a/scenarios/corpus_v1`).

---

## 1. Ejecutar escenarios (The ONE)

**Un solo escenario** (desde la raíz del ONE):

```bash
./one.sh -b 1 scenarios/corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings
```

**Todos los escenarios (70)** (desde la raíz del repo que contiene `scenarios/`):

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1
```

- Los reportes (p. ej. `*_MessageStatsReport.txt`) se escriben en el directorio configurado en cada `.settings` (suele ser `reports/` en la raíz del ONE).
- Solo listar sin ejecutar: añadir `--dry-run`.

---

## 2. Ejecutar el pipeline de análisis

Desde la **raíz del repositorio** (padre de `scenarios/`):

```bash
# Extraer features → analysis/data/features.csv
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features

# Normalizar (z-score) → analysis/data/features_normalized.csv
python3 scenarios/analysis/run_analysis.py --phase normalize

# Matrices de correlación e informes → analysis/data/*.csv, analysis/reports/*.txt
python3 scenarios/analysis/run_analysis.py --phase correlation

# Figuras → analysis/figures/*.png, *.pdf
python3 scenarios/analysis/run_analysis.py --phase figures

# Generar output_metrics.csv desde reportes del ONE (si existe reports/)
python3 scenarios/analysis/run_analysis.py --phase output_metrics

# Correlación basada en outputs (requiere output_metrics.csv)
python3 scenarios/analysis/run_analysis.py --phase outputs
```

**Ejecutar todo (features hasta output_metrics) de una vez:**

```bash
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all
```

La fase `outputs` se ejecuta por separado cuando ya tengas `analysis/data/output_metrics.csv` (tras ejecutar escenarios y la fase output_metrics).

---

## 3. Usar el dashboard

Desde la **raíz del repositorio**:

```bash
streamlit run scenarios/analysis/dashboard.py
```

- Abre el navegador con: resumen, resultados por fase, vista por escenario, comparación entre escenarios.
- Requiere `streamlit` y `pandas` (y el mismo entorno Python que el pipeline).

---

## Dónde se guardan las salidas

| Salida | Ruta (relativa al repo) |
|--------|--------------------------|
| CSV de features, normalizado, matrices | `scenarios/analysis/data/` |
| Figuras (heatmaps, scatter, histogramas) | `scenarios/analysis/figures/` |
| Informes de texto (correlación, clustering, etc.) | `scenarios/analysis/reports/` |
| Reportes del ONE | Normalmente `reports/` en la raíz del ONE (configurable en .settings) |

---

## Errores habituales

- **Java/ONE no encontrado** — Ejecutar desde el directorio que contiene `one.sh`; asegurar que el ONE está compilado.
- **Módulo Python no encontrado** — Usar un venv e instalar dependencias: `pip install numpy pandas scipy matplotlib streamlit`.
- **Ruta del corpus** — Usar `--corpus corpus_v1` si ejecutas desde la raíz del repo y `corpus_v1` está en `scenarios/corpus_v1`. Si no, usar la ruta absoluta al directorio del corpus.
- **Fase output_metrics** — Necesita los reportes del ONE (p. ej. `*_MessageStatsReport.txt`) en el directorio de reportes; ejecutar antes los escenarios o usar `--reports-dir` si los reportes están en otra ruta.

---

## Siguientes pasos

- [Instalación](Installation-es) — Configuración paso a paso
- [Reproducibilidad](Reproducibility-es) — Regenerar análisis desde cero
- [Metodología](Methodology-es) — Cómo funcionan los features y la correlación  
- [Resumen de resultados](Results-overview-es) — Resultados principales y figuras  
- [Visión del corpus](Corpus-overview-es) — Familias de escenarios y diseño  
