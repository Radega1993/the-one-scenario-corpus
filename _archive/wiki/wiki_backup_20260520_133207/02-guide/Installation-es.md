# Instalación

**Español** | [English](Installation)

---

Pasos para dejar listo el corpus de escenarios y el pipeline de análisis. Ver también [Quickstart](Quickstart-es) para los comandos mínimos.

---

## 1. Clonar y compilar The ONE

1. **Clonar The ONE** (si aún no lo tienes):
   ```bash
   git clone https://github.com/akeranen/the-one.git
   cd the-one
   ```
2. **Compilar:**
   ```bash
   chmod +x compile.sh
   ./compile.sh
   ```
3. Comprobar que **Java** (p. ej. OpenJDK 11+) está instalado: `java -version`.

---

## 2. Obtener el corpus de escenarios

**Opción A — Corpus dentro del repo del ONE**

Clona o copia la carpeta `scenarios/` (corpus + analysis) en la raíz del ONE, p. ej.:

```
the-one/
├── one.sh
├── compile.sh
├── default_settings.txt
├── reports/
└── scenarios/          ← corpus_v1/, analysis/, wiki/, README, etc.
```

**Opción B — Corpus en repo separado**

Clona el repo del corpus (p. ej. `the-one-scenario-corpus`) donde quieras. Al ejecutar los scripts, usa la ruta completa al corpus: `--corpus /ruta/a/the-one-scenario-corpus/corpus_v1` (o pon `scenarios/` como directorio actual y usa `--corpus corpus_v1` desde el padre que lo contiene).

---

## 3. Entorno Python

1. **Crear un entorno virtual** (recomendado):
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   # o: venv\Scripts\activate  # Windows
   ```
2. **Instalar dependencias:**
   ```bash
   pip install numpy pandas scipy matplotlib streamlit
   ```
   Si el proyecto tiene `requirements.txt` en la raíz o en `scenarios/`:
   ```bash
   pip install -r requirements.txt
   ```

---

## 4. Verificar

- **Ejecutar un escenario** (desde la raíz del ONE):
  ```bash
  ./one.sh -b 1 scenarios/corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings
  ```
  Comprobar que en `reports/` (o el directorio configurado en el .settings) aparecen ficheros de salida.

- **Ejecutar una fase del análisis** (desde la raíz del repo que contiene `scenarios/`):
  ```bash
  python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features
  ```
  Comprobar que se crean `scenarios/analysis/data/features.csv` y `scenario_list.txt`.

---

## Ver también

- [Quickstart](Quickstart-es) — Comandos para todos los escenarios y el pipeline
- [Reproducibilidad](Reproducibility-es) — Regenerar el análisis desde cero
