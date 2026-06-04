#!/usr/bin/env python3
"""
Menú interactivo (español) para lanzar los scripts de scenarios/analysis/
sin importar módulos pesados: cada opción delega en subprocess.

Uso (desde la raíz del repo):
  python3 scenarios/analysis/analysis_menu.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

_ANALYSIS = Path(__file__).resolve().parent
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import (  # noqa: E402
    ANALYSIS_DIR,
    DEFAULT_MANIFEST_V1,
    ROUTING_CONTACT_REPORTS_OVERLAY,
    REPO_ROOT,
    SELECTION_EXAMPLE,
    SPATIAL_OVERLAY,
)
from lib.scenario_select import list_families  # noqa: E402

# Submenú 4 — Paper y validación (id → metadatos para lanzar script)
SCRIPT_CATALOG: dict[str, dict[str, object]] = {
    "4a": {
        "title": "Validar perfiles de tráfico (TP01–TP12)",
        "script": ANALYSIS_DIR / "scripts/validation/validate_traffic_profiles.py",
        "desc": [
            "Compara Events/TTL de cada .settings con las definiciones canónicas (lib/traffic_profile_generator).",
            "Entrada: corpus_v1 + data/output_metrics.csv. Salida: data/tp_validation_*.csv, reports/validation/tp_validation_report.md.",
        ],
        "args": [],
    },
    "4b": {
        "title": "Rellenar output_metrics.csv (MessageStats)",
        "script": ANALYSIS_DIR / "run_analysis.py",
        "desc": [
            "Fase output_metrics de run_analysis: lee *MessageStatsReport.txt en reports/ y actualiza data/output_metrics.csv.",
            "Requiere simulaciones completadas. Salida principal: data/output_metrics.csv (benchmark/routing; no cierra diversidad por sí solo).",
        ],
        "args": ["--corpus", "corpus_v1", "--phase", "output_metrics"],
        "interactive": "output_metrics",
    },
    "4c": {
        "title": "Validación benchmark corpus_v1",
        "script": ANALYSIS_DIR / "scripts/validation/validate_corpus_benchmark.py",
        "desc": [
            "Clasifica cada escenario (ok / extremo / error) cruzando manifiesto y CSVs de métricas.",
            "Salida: data/corpus_benchmark_validation.csv, reports/canonical/corpus_benchmark_validation.md.",
        ],
        "args": [],
    },
    "4d": {
        "title": "KPIs por perfil de tráfico",
        "script": ANALYSIS_DIR / "scripts/paper/analyze_traffic_profile_kpis.py",
        "desc": [
            "Estadísticas y recomendaciones por TP vs referencia TP01 (delivery, overhead, latencia…).",
            "Salida: data/traffic_profile_*.csv, reports/policies/traffic_profile_kpi_analysis.md.",
        ],
        "args": [],
    },
    "4e": {
        "title": "Política KPI protocolos",
        "script": ANALYSIS_DIR / "scripts/paper/build_protocol_benchmark_kpi_policy.py",
        "desc": [
            "Define KPIs núcleo y reglas de comparación entre protocolos para el paper.",
            "Salida: data/protocol_benchmark_kpi_*.csv, reports/policies/protocol_benchmark_kpi_policy.md.",
        ],
        "args": [],
    },
    "4f": {
        "title": "Ventana de análisis de mensajes",
        "script": ANALYSIS_DIR / "scripts/paper/build_message_analysis_window_policy.py",
        "desc": [
            "Política de ventana temporal para analizar creación/entrega de mensajes por escenario y TP.",
            "Salida: data/message_analysis_window_*.csv, reports/policies/message_analysis_window_policy.md.",
        ],
        "args": [],
    },
    "4g": {
        "title": "Espacial vs rendimiento",
        "script": ANALYSIS_DIR / "scripts/paper/analyze_spatial_vs_performance.py",
        "desc": [
            "Correlaciona cobertura espacial (heatmaps/metrics) con delivery y latencia.",
            "Salida: reports/spatial/spatial_vs_performance_analysis.md (+ resumen espacial).",
        ],
        "args": [],
    },
    "4h": {
        "title": "Índice figuras/tablas paper",
        "script": ANALYSIS_DIR / "scripts/paper/build_paper_figures_tables_index.py",
        "desc": [
            "Audita figuras paper, promueve agregadas y escribe índice + informe de readiness.",
            "Salida: figures/paper/, reports/paper_gate/paper_figures_tables_readiness.md.",
        ],
        "args": [],
    },
    "4i": {
        "title": "Checklist freeze paper",
        "script": ANALYSIS_DIR / "scripts/paper/build_paper_freeze_checklist.py",
        "desc": [
            "Gate estricto antes de congelar el paper: datos, informes, figuras y wiki.",
            "Salida: reports/paper_freeze_checklist.md, data/paper_freeze_checklist.csv.",
        ],
        "args": [],
    },
    "4j": {
        "title": "Auditoría .settings",
        "script": ANALYSIS_DIR / "scripts/validation/audit_settings.py",
        "desc": [
            "Recorre corpus_v1 y extrae flags/claves relevantes a settings_audit.csv.",
            "Salida: data/settings_audit.csv.",
        ],
        "args": [],
    },
    "4k": {
        "title": "Diagnóstico de escenarios",
        "script": ANALYSIS_DIR / "scripts/validation/diagnose_scenarios.py",
        "desc": [
            "Cruza auditoría de settings con métricas → scenario_diagnosis.csv y informe MD.",
            "Salida: data/scenario_diagnosis.csv, reports/pipeline/scenario_diagnosis.md.",
        ],
        "args": [],
    },
    "4l": {
        "title": "Reconstruir wiki paper",
        "script": ANALYSIS_DIR / "scripts/wiki/populate_wiki_paper.py",
        "desc": [
            "Regenera páginas en scenarios/.wiki-clone/ orientadas al paper (tras backup).",
            "Salida: .wiki-clone/*.md (no toca corpus ni simulaciones).",
        ],
        "args": [],
    },
    "4m": {
        "title": "Informes wiki_meta / validación",
        "script": ANALYSIS_DIR / "scripts/wiki/build_wiki_research_reports.py",
        "desc": [
            "Genera auditorías e informes auxiliares para la wiki (fases 1 y 4–8).",
            "Salida: reports/wiki_meta/, reports/validation/ (varios MD).",
        ],
        "args": [],
    },
    "4n": {
        "title": "Conteos para INVENTARIO",
        "script": ANALYSIS_DIR / "scripts/paper/build_inventory_update_report.py",
        "desc": [
            "Cuenta ficheros actuales (corpus, data, reports, figuras) y escribe inventory_update_report.md.",
            "Salida: reports/project/inventory_update_report.md (actualizar INVENTARIO.md a mano).",
        ],
        "args": [],
    },
}

def _ask(prompt: str, default: str | None = None) -> str:
    hint = f" [{default}]" if default is not None else ""
    raw = input(f"{prompt}{hint}: ").strip()
    if not raw and default is not None:
        return default
    return raw

def _ask_yes(prompt: str, default: bool = False) -> bool:
    d = "s/N" if not default else "S/n"
    raw = input(f"{prompt} ({d}): ").strip().lower()
    if not raw:
        return default
    return raw in ("s", "si", "sí", "y", "yes", "1", "true")

def _is_back_choice(choice: str) -> bool:
    return choice.strip().lower() in ("0", "", "q", "b", "back", "m", "menu")

def _rel_repo(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)

_MENU_WIDTH = 58

def _menu_box_line(text: str) -> str:
    """Una línea interior del marco (ancho fijo)."""
    t = text.strip()
    if len(t) > _MENU_WIDTH:
        t = t[: _MENU_WIDTH - 1] + "…"
    return f"║ {t:<{_MENU_WIDTH}} ║"

def _print_main_menu() -> None:
    items = [
        "1) Simular: corpus completo (batch)",
        "2) Simular: escenario, familia, TP o lista (GUI/batch)",
        "3) Pipeline por fases (run_analysis)",
        "4) Paper y validación (submenú)",
        "5) Tiempo útil de simulación (connectivity)",
        "6) Tiempos de creación de mensajes",
        "7) Ocupación espacial (coverage_road_cells_pct, zoom roads)",
        "8) Dashboard (Streamlit)",
        "9) Figuras agregadas / paper",
        "10) Ruta paper-ready guiada (540/540)",
        "11) Simular con protocolo (overlay)",
        "0) Salir",
    ]
    bar = "═" * _MENU_WIDTH
    print()
    print(f"╔{bar}╗")
    print(_menu_box_line("The ONE — menú de análisis (scenarios/analysis)"))
    print(f"╠{bar}╣")
    for line in items:
        print(_menu_box_line(line))
    print(f"╚{bar}╝")
    print(f"Repo: {REPO_ROOT}")
    print(f"Analysis: {ANALYSIS_DIR}")
    print()

def _run_script(args: list[str], *, cwd: Path | None = None) -> int:
    cmd = [sys.executable, *args]
    print("\n→", " ".join(cmd), "\n")
    r = subprocess.run(cmd, cwd=cwd or REPO_ROOT)
    return int(r.returncode)

def _collect_extra_settings() -> list[str]:
    """Pregunta presets de reportes y rutas manuales; devuelve flags --extra-settings."""
    print(
        "\nPreset de reportes (--extra-settings):\n"
        "  0 = ninguno\n"
        "  1 = routing/contacto (MessageStats, contactos, ConnectivityONE, …)\n"
        "  2 = routing/contacto + ocupación espacial (NodePosition + SpatialOccupancy)\n"
    )
    preset = _ask("Elige preset", "1").strip() or "0"
    extra: list[str] = []
    if preset == "1":
        if ROUTING_CONTACT_REPORTS_OVERLAY.is_file():
            extra.extend(["--extra-settings", _rel_repo(ROUTING_CONTACT_REPORTS_OVERLAY)])
        else:
            print(f"Aviso: no existe {ROUTING_CONTACT_REPORTS_OVERLAY}", file=sys.stderr)
    elif preset == "2":
        for p in (ROUTING_CONTACT_REPORTS_OVERLAY, SPATIAL_OVERLAY):
            if p.is_file():
                extra.extend(["--extra-settings", _rel_repo(p)])
            else:
                print(f"Aviso: no existe {p}", file=sys.stderr)
    manual = _ask("Rutas extra de settings (separadas por coma; vacío = no)", "")
    if manual.strip():
        for part in manual.split(","):
            part = part.strip()
            if part:
                extra.extend(["--extra-settings", part])
    return extra

def _corpus_dir(corpus: str) -> Path:
    d = REPO_ROOT / "scenarios" / corpus
    if not d.is_dir():
        d = Path(corpus)
        if not d.is_absolute():
            d = REPO_ROOT / d
    return d

def _resolve_selection(corpus: str, selection: str) -> dict:
    """
    Devuelve kwargs para _run_simulations_cmd:
      settings_paths, families, traffic_profiles, scenario_bases, name_regex, select_file
    """
    empty: dict = {
        "settings_paths": None,
        "families": None,
        "traffic_profiles": None,
        "scenario_bases": None,
        "name_regex": None,
        "select_file": None,
    }
    corpus_dir = _corpus_dir(corpus)
    all_files = sorted(corpus_dir.glob("**/*.settings")) if corpus_dir.is_dir() else []
    sel = selection.strip()

    if sel == "1":
        raw = _ask("Ruta al .settings (relativa al repo o absoluta)", "")
        if not raw.strip():
            return empty
        p = Path(raw.strip())
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.is_file():
            print(f"No existe: {p}", file=sys.stderr)
            return empty
        return {**empty, "settings_paths": [_rel_repo(p)]}

    if sel == "2":
        fams = list_families(corpus_dir)
        if fams:
            print("Familias:", ", ".join(fams))
        fam = _ask("Familia (carpeta bajo el corpus, ej. 01_urban)", "01_urban")
        if not fam.strip():
            return empty
        return {**empty, "families": [fam.strip()]}

    if sel == "3":
        raw = _ask("Perfil TP (ej. TP07; varios separados por coma)", "TP07")
        tps = [t.strip() for t in raw.split(",") if t.strip()]
        if not tps:
            return empty
        return {**empty, "traffic_profiles": tps}

    if sel == "4":
        fams = list_families(corpus_dir)
        if fams:
            print("Familias:", ", ".join(fams))
        fam = _ask("Familia", "01_urban")
        raw = _ask("Perfil(es) TP (coma)", "TP01")
        tps = [t.strip() for t in raw.split(",") if t.strip()]
        if not fam.strip() or not tps:
            return empty
        return {**empty, "families": [fam.strip()], "traffic_profiles": tps}

    if sel == "5":
        raw = _ask("Rutas .settings separadas por coma", "")
        out: list[str] = []
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            p = Path(part)
            if not p.is_absolute():
                p = REPO_ROOT / p
            if p.is_file():
                out.append(_rel_repo(p))
            else:
                print(f"Aviso: no existe {p}", file=sys.stderr)
        return {**empty, "settings_paths": out or None}

    if sel == "6":
        sf = _ask(
            "Ruta al archivo de selección (family:/tp:/base:/regex:/ruta.settings)",
            _rel_repo(SELECTION_EXAMPLE),
        )
        if not sf.strip():
            return empty
        p = Path(sf.strip())
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.is_file():
            print(f"No existe: {p}", file=sys.stderr)
            return empty
        return {**empty, "select_file": _rel_repo(p)}

    if sel == "7":
        name_rx = _ask("Regex (ej. U2_SparseSuburb|TP07)", "") or None
        if not name_rx:
            return empty
        return {**empty, "name_regex": name_rx}

    if sel == "8":
        name_rx = _ask("Filtrar lista por regex (vacío = todos)", "") or None
        shown = all_files
        if name_rx:
            rx = re.compile(name_rx)
            shown = [p for p in shown if rx.search(p.as_posix())]
        if not shown:
            print("Ningún escenario coincide.")
            return []
        page_size = 25
        for start in range(0, len(shown), page_size):
            chunk = shown[start : start + page_size]
            for i, p in enumerate(chunk, start + 1):
                try:
                    rel = p.relative_to(REPO_ROOT)
                except ValueError:
                    rel = p
                print(f"  {i:4d}. {rel}")
            if start + page_size >= len(shown):
                break
            if not _ask_yes("¿Ver más?", default=False):
                break
        raw = _ask("Números a ejecutar (ej. 1,3,5-8) o 'all'", "all")
        if raw.strip().lower() == "all":
            return {**empty, "settings_paths": [_rel_repo(p) for p in shown]}
        indices: set[int] = set()
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                try:
                    lo, hi = int(a), int(b)
                    indices.update(range(lo, hi + 1))
                except ValueError:
                    pass
            else:
                try:
                    indices.add(int(part))
                except ValueError:
                    pass
        out: list[str] = []
        for i in sorted(indices):
            if 1 <= i <= len(shown):
                out.append(_rel_repo(shown[i - 1]))
        return {**empty, "settings_paths": out or None}

    return empty

def _run_simulations_cmd(
    *,
    corpus: str,
    gui: bool,
    dry_run: bool,
    jobs: str,
    timeout: str,
    extra: list[str],
    settings_paths: list[str] | None = None,
    families: list[str] | None = None,
    traffic_profiles: list[str] | None = None,
    scenario_bases: list[str] | None = None,
    name_regex: str | None = None,
    select_file: str | None = None,
    benchmark: str | None = None,
    exclude_deprecated: bool = False,
    estimate_runtime: bool = False,
) -> list[str]:
    cmd = [
        str(ANALYSIS_DIR / "run_all_scenarios.py"),
        "--corpus",
        corpus,
        "--jobs",
        jobs,
        "--timeout",
        timeout,
    ]
    if gui:
        cmd.append("--gui")
    if dry_run:
        cmd.append("--dry-run")
    if benchmark:
        cmd.extend(["--benchmark", benchmark])
    if exclude_deprecated:
        cmd.append("--exclude-deprecated")
    if estimate_runtime:
        cmd.append("--estimate-runtime")
    if name_regex:
        cmd.extend(["--name-regex", name_regex])
    if select_file:
        cmd.extend(["--select-file", select_file])
    if families:
        for f in families:
            cmd.extend(["--family", f])
    if traffic_profiles:
        for t in traffic_profiles:
            cmd.extend(["--tp", t])
    if scenario_bases:
        for b in scenario_bases:
            cmd.extend(["--scenario-base", b])
    if settings_paths:
        for sp in settings_paths:
            cmd.extend(["--settings", sp])
    cmd.extend(extra)
    return cmd

def menu_run_selected_scenarios() -> None:
    print("\n--- Simular escenarios (selección flexible) ---")
    print(
        "Modo de ejecución:\n"
        "  1 = batch (segundo plano, sin ventana)\n"
        "  2 = GUI (visual; cierra la ventana del ONE entre escenarios)\n"
    )
    mode = _ask("Elige modo", "1")
    gui = mode == "2"

    corpus = _ask("Carpeta del corpus bajo scenarios/", "corpus_v1")
    print(
        "\nQué ejecutar:\n"
        "  1 = un escenario (ruta .settings)\n"
        "  2 = una familia (ej. 01_urban → 60 escenarios)\n"
        "  3 = un perfil TP (ej. TP07 → todos los escenarios con ese TP)\n"
        "  4 = familia + TP (ej. 01_urban + TP01)\n"
        "  5 = conjunto explícito (varias rutas separadas por coma)\n"
        "  6 = archivo de selección (family:/tp:/regex:/rutas)\n"
        "  7 = regex sobre rutas del corpus\n"
        "  8 = listar numerados y elegir (1,3,5-8 o all)\n"
    )
    sel_mode = _ask("Elige selección", "2")
    sel = _resolve_selection(corpus, sel_mode)
    if not any(
        [
            sel.get("settings_paths"),
            sel.get("families"),
            sel.get("traffic_profiles"),
            sel.get("scenario_bases"),
            sel.get("name_regex"),
            sel.get("select_file"),
        ]
    ):
        print("No hay selección válida.")
        input("Enter para volver al menú…")
        return

    dry = _ask_yes("¿Solo listar (dry-run)?", default=True)
    jobs_s = "1" if gui else _ask("Paralelismo (--jobs, solo batch)", "1")
    timeout_s = _ask("Timeout por escenario en batch (s)", "7200")
    extra = _collect_extra_settings()

    cmd = _run_simulations_cmd(
        corpus=corpus,
        gui=gui,
        dry_run=dry,
        jobs=jobs_s,
        timeout=timeout_s,
        extra=extra,
        **sel,
    )
    rc = _run_script(cmd)
    print(f"\n(código salida {rc})")
    input("Enter para volver al menú…")

def menu_run_all_scenarios() -> None:
    print("\n--- Ejecutar todas las simulaciones ---")
    corpus = _ask("Carpeta del corpus bajo scenarios/", "corpus_v1")
    corpus_dir = _corpus_dir(corpus)
    fams = list_families(corpus_dir)
    if fams:
        print(f"Familias disponibles: {', '.join(fams)}")

    print(
        "\nBenchmark tier:\n"
        "  0 = sin filtro (todo el corpus)\n"
        "  1 = core (540 escenarios ambientales)\n"
        "  2 = all (alias de core, 540)\n"
    )
    bench_choice = _ask("Benchmark tier", "0")
    benchmark_map = {"0": None, "1": "core", "2": "all"}
    benchmark = benchmark_map.get(bench_choice)

    fam_filter = _ask("Limitar a familia (vacío = todo el corpus)", "") or None
    tp_filter = _ask("Limitar a TP (vacío = todos, ej. TP07)", "") or None
    dry = _ask_yes("¿Solo listar (dry-run)?", default=False)
    estimate = _ask_yes("¿Estimar tiempo de ejecución?", default=False)
    jobs_s = _ask("Paralelismo (--jobs)", "1")
    timeout_s = _ask("Timeout por escenario (s)", "7200")
    name_rx = _ask("Filtrar además por regex (vacío = no)", "") or None
    extra = _collect_extra_settings()

    cmd = _run_simulations_cmd(
        corpus=corpus,
        gui=False,
        dry_run=dry,
        jobs=jobs_s,
        timeout=timeout_s,
        extra=extra,
        families=[fam_filter] if fam_filter else None,
        traffic_profiles=[tp_filter] if tp_filter else None,
        name_regex=name_rx,
        benchmark=benchmark,
        exclude_deprecated=benchmark is not None,
        estimate_runtime=estimate,
    )
    rc = _run_script(cmd)
    print(f"\n(código salida {rc})")
    input("Enter para volver al menú…")

def menu_run_analysis() -> None:
    print("\n--- Pipeline run_analysis.py ---")
    corpus = _ask("Corpus", "corpus_v1")
    print(
        "Fases: features | features_report | normalize | correlation | "
        "feature_correlation | ablation | figures | figures_paper | figures_aggregated | "
        "tables_paper | indirects | output_metrics | outputs | all"
    )
    phase = _ask("Fase", "features")
    rc = _run_script(
        [str(ANALYSIS_DIR / "run_analysis.py"), "--corpus", corpus, "--phase", phase]
    )
    print(f"\n(código salida {rc})")
    input("Enter para volver al menú…")

def _paper_ready_steps() -> list[tuple[str, list[str]]]:
    return [
        ("output_metrics (benchmark/routing)", [str(ANALYSIS_DIR / "run_analysis.py"), "--corpus", "corpus_v1", "--phase", "output_metrics"]),
        ("features (diversidad 540)", [str(ANALYSIS_DIR / "run_analysis.py"), "--corpus", "corpus_v1", "--phase", "features"]),
        ("normalize", [str(ANALYSIS_DIR / "run_analysis.py"), "--corpus", "corpus_v1", "--phase", "normalize"]),
        ("correlation", [str(ANALYSIS_DIR / "run_analysis.py"), "--corpus", "corpus_v1", "--phase", "correlation"]),
        ("feature_correlation", [str(ANALYSIS_DIR / "run_analysis.py"), "--corpus", "corpus_v1", "--phase", "feature_correlation"]),
        ("ablation", [str(ANALYSIS_DIR / "run_analysis.py"), "--corpus", "corpus_v1", "--phase", "ablation"]),
        ("figures_paper", [str(ANALYSIS_DIR / "run_analysis.py"), "--corpus", "corpus_v1", "--phase", "figures_paper"]),
        ("tables_paper", [str(ANALYSIS_DIR / "run_analysis.py"), "--corpus", "corpus_v1", "--phase", "tables_paper"]),
        ("build_paper_figures_tables_index", [str(ANALYSIS_DIR / "scripts/paper/build_paper_figures_tables_index.py")]),
        ("build_paper_freeze_checklist", [str(ANALYSIS_DIR / "scripts/paper/build_paper_freeze_checklist.py")]),
        ("validate_diversity_readiness", [str(ANALYSIS_DIR / "scripts/paper/validate_diversity_readiness.py")]),
        ("populate_wiki_paper", [str(ANALYSIS_DIR / "scripts/wiki/populate_wiki_paper.py")]),
    ]

def menu_paper_ready_flow() -> None:
    print("\n--- Ruta paper-ready (orden recomendado) ---")
    print("Scope benchmark: 540 escenarios en corpus_v1 (seis familias ambientales).")
    steps = _paper_ready_steps()
    for i, (label, cmd) in enumerate(steps, start=1):
        print(f"{i:2d}. {label}")
        print(f"    {sys.executable} {' '.join(cmd)}")

    if _ask_yes("¿Solo mostrar comandos (sin ejecutar)?", default=True):
        input("Enter para volver al menú…")
        return

    ask_each = _ask_yes("¿Pedir confirmación en cada paso?", default=True)
    for i, (label, cmd) in enumerate(steps, start=1):
        if ask_each and not _ask_yes(f"[{i}/{len(steps)}] Ejecutar {label}?", default=True):
            print("Saltado.")
            continue
        rc = _run_script(cmd)
        if rc != 0:
            if not _ask_yes("Este paso falló. ¿Continuar con el siguiente?", default=False):
                break
    input("Enter para volver al menú…")

def _router_overlay_options() -> dict[str, Path]:
    base = ANALYSIS_DIR / "protocol_overlays"
    options: dict[str, Path] = {}
    for name in ("router_epidemic.txt", "router_prophet.txt", "router_maxprop.txt", "router_sprayandwait.txt"):
        p = base / name
        if p.is_file():
            key = name.replace("router_", "").replace(".txt", "")
            options[key] = p
    return options

def _write_report_dir_overlay(report_dir: str) -> Path:
    gen = ANALYSIS_DIR / "overlays" / "_generated"
    gen.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", report_dir.strip())
    overlay_path = gen / f"report_dir_{safe}.txt"
    overlay_path.write_text(f"Report.reportDir = {report_dir}\n", encoding="utf-8")
    return overlay_path

def menu_protocol_overlay_runs() -> None:
    print("\n--- Simular con protocolo (overlay, sin editar .settings) ---")
    options = _router_overlay_options()
    if not options:
        print("No hay overlays en scenarios/analysis/protocol_overlays/")
        input("Enter para volver…")
        return

    keys = list(options.keys())
    for i, k in enumerate(keys, start=1):
        print(f"  {i}) {k}")
    raw = _ask("Elige protocolo", "1")
    try:
        selected = keys[int(raw) - 1]
    except Exception:
        print("Selección inválida.")
        input("Enter para volver…")
        return

    print(
        "\nScope de simulación:\n"
        "  1 = corpus_v1 completo (540)\n"
        "  2 = selección manual (familia/TP/regex/lista)\n"
    )
    scope = _ask("Scope", "1").strip()
    dry = _ask_yes("¿Solo listar (dry-run)?", default=True)
    jobs_s = _ask("Paralelismo (--jobs)", "4")
    timeout_s = _ask("Timeout por escenario (s)", "43200")

    print("\nAviso de reproducibilidad: no mezclar protocolos en el mismo reportDir.")
    separate = _ask_yes("¿Añadir overlay temporal para Report.reportDir por protocolo?", default=True)

    extra = [
        "--extra-settings", _rel_repo(ROUTING_CONTACT_REPORTS_OVERLAY),
        "--extra-settings", _rel_repo(options[selected]),
    ]
    if separate:
        default_report_dir = f"reports_{selected}/"
        report_dir = _ask("Report.reportDir para este protocolo", default_report_dir).strip() or default_report_dir
        report_overlay = _write_report_dir_overlay(report_dir)
        extra.extend(["--extra-settings", _rel_repo(report_overlay)])

    if scope == "1":
        cmd = _run_simulations_cmd(
            corpus="corpus_v1",
            gui=False,
            dry_run=dry,
            jobs=jobs_s,
            timeout=timeout_s,
            extra=extra,
            benchmark="core",
            exclude_deprecated=True,
        )
    elif scope == "2":
        corpus = _ask("Corpus para selección manual", "corpus_v1")
        print("Selección manual: 1=.settings, 2=familia, 3=TP, 4=familia+TP, 5=lista, 6=archivo, 7=regex, 8=numerado")
        sel_mode = _ask("Modo de selección", "2")
        sel = _resolve_selection(corpus, sel_mode)
        cmd = _run_simulations_cmd(
            corpus=corpus,
            gui=False,
            dry_run=dry,
            jobs=jobs_s,
            timeout=timeout_s,
            extra=extra,
            **sel,
        )
    else:
        print("Scope no válido.")
        input("Enter para volver…")
        return

    rc = _run_script(cmd)
    print(f"\n(código salida {rc})")
    input("Enter para volver al menú…")

def _print_paper_submenu() -> None:
    print("\n--- Paper y validación ---")
    print("Estado actual: benchmark 540 escenarios (corpus_v1).\n")
    for key in sorted(SCRIPT_CATALOG.keys()):
        entry = SCRIPT_CATALOG[key]
        print(f"  {key}) {entry['title']}")
    print("  0|b|back|m|menu|q) Volver al menú principal")

def _run_catalog_entry(catalog_id: str) -> None:
    entry = SCRIPT_CATALOG.get(catalog_id)
    if not entry:
        print("Opción no reconocida.")
        return
    print(f"\n--- {entry['title']} ---")
    for line in entry.get("desc", []):
        print(f"  {line}")
    script = Path(str(entry["script"]))
    if not script.is_file():
        print(f"\nError: no existe el script {script}", file=sys.stderr)
        input("Enter para volver…")
        return
    args: list[str] = [str(script)]
    default_args = list(entry.get("args", []))
    if entry.get("interactive") == "output_metrics":
        corpus = _ask("Corpus", "corpus_v1")
        args.extend(["--corpus", corpus, "--phase", "output_metrics"])
    else:
        args.extend(str(a) for a in default_args)
    if catalog_id == "4c" and _ask_yes("¿Refrescar diagnose_scenarios antes (--refresh-diagnosis)?", default=False):
        args.append("--refresh-diagnosis")
    rc = _run_script(args)
    print(f"\n(código salida {rc})")
    input("Enter para volver…")

def menu_paper_validation() -> None:
    while True:
        _print_paper_submenu()
        choice = _ask("Opción", "0").strip().lower()
        if _is_back_choice(choice):
            return
        if choice in SCRIPT_CATALOG:
            _run_catalog_entry(choice)
        else:
            print("Opción no reconocida. Usa 4a..4n o 0/back/menu.")

def menu_useful_time() -> None:
    print("\n--- Tiempo útil (ConnectivityONEReport) ---")
    corpus = _ask("Directorio corpus", _rel_repo(REPO_ROOT / "scenarios" / "corpus_v1"))
    reports = _ask("Directorio de reportes ONE", "reports")
    corpus_path = Path(corpus)
    reports_path = Path(reports)
    if not corpus_path.is_absolute():
        corpus_path = REPO_ROOT / corpus_path
    if not reports_path.is_absolute():
        reports_path = REPO_ROOT / reports_path
    rc = _run_script(
        [
            str(ANALYSIS_DIR / "scripts/validation/compute_useful_simulation_time.py"),
            "--corpus-dir",
            str(corpus_path),
            "--reports-dir",
            str(reports_path),
        ]
    )
    print(f"\n(código salida {rc})")
    input("Enter para volver al menú…")

def menu_message_creation() -> None:
    print("\n--- Tiempos de creación de mensajes ---")
    use_rep = _ask_yes("¿Usar CreatedMessagesReport si existe (--use-reports)?", default=False)
    cmd = [str(ANALYSIS_DIR / "scripts/validation/analyze_message_creation_times.py")]
    if use_rep:
        cmd.append("--use-reports")
    rc = _run_script(cmd)
    print(f"\n(código salida {rc})")
    input("Enter para volver al menú…")

def menu_spatial() -> None:
    print("\n--- Ocupación espacial (heatmaps / CSV agregados) ---")
    manifest = _ask("Manifiesto CSV", _rel_repo(DEFAULT_MANIFEST_V1))
    reports = _ask("Carpeta reportes (relativa al repo)", "reports")
    families = _ask("Familias (coma, vacío = todas)", "") or None
    manifest_path = Path(manifest)
    if not manifest_path.is_absolute():
        manifest_path = REPO_ROOT / manifest_path
    cmd = [
        str(ANALYSIS_DIR / "scripts/validation/analyze_spatial_occupancy.py"),
        "--reports-dir",
        reports,
        "--manifest",
        str(manifest_path),
        "--zoom-mode",
        "roads",
    ]
    if families:
        cmd.extend(["--families", families])
    rc = _run_script(cmd)
    print(f"\n(código salida {rc})")
    input("Enter para volver al menú…")

def menu_figures_guide() -> None:
    print("\n--- Guía de figuras ---")
    readme = ANALYSIS_DIR / "figures" / "README.md"
    if readme.is_file():
        print(f"Catálogo: {_rel_repo(readme)}")
        print("(Abre el archivo en el editor o en el dashboard → Figuras)\n")
    else:
        print("Aviso: aún no existe figures/README.md\n")
    if _ask_yes("¿Regenerar figuras agregadas (run_figures_aggregated.py)?", default=True):
        corpus = _ask("Corpus", "corpus_v1")
        block = _ask_yes(
            "¿Incluir heatmap de bloques N×N (--include-block-heatmap, puede ser pesado)?",
            default=False,
        )
        cmd = [
            str(ANALYSIS_DIR / "run_figures_aggregated.py"),
            "--corpus",
            corpus,
        ]
        if block:
            cmd.append("--include-block-heatmap")
        rc = _run_script(cmd)
        print(f"\n(código salida {rc})")
    if _ask_yes("¿Regenerar paquete paper (figures_paper)?", default=False):
        corpus = _ask("Corpus", "corpus_v1")
        rc = _run_script(
            [str(ANALYSIS_DIR / "run_analysis.py"), "--corpus", corpus, "--phase", "figures_paper"]
        )
        print(f"\n(código salida {rc})")
    input("Enter para volver al menú…")

def menu_dashboard() -> None:
    print("\n--- Dashboard Streamlit ---")
    dash = ANALYSIS_DIR / "dashboard.py"
    if shutil.which("streamlit") is None:
        chk = subprocess.run(
            [sys.executable, "-m", "streamlit", "--version"],
            cwd=REPO_ROOT,
            capture_output=True,
        )
        if chk.returncode != 0:
            print(
                "No se encontró `streamlit`. Instala con:\n"
                "  python3 -m pip install streamlit\n"
                "o usa el venv: scenarios/analysis/.venv/bin/pip install streamlit",
                file=sys.stderr,
            )
            input("Enter para volver…")
            return
        cmd = [sys.executable, "-m", "streamlit", "run", str(dash)]
    else:
        cmd = ["streamlit", "run", str(dash)]

    print("\n→", " ".join(cmd), "(cwd=", REPO_ROOT, ")\n")
    subprocess.run(cmd, cwd=REPO_ROOT)
    input("Enter para volver al menú…")

def main() -> int:
    while True:
        _print_main_menu()
        choice = _ask("Opción", "0").strip()
        if choice == "0":
            print("Adiós.")
            return 0
        if choice == "1":
            menu_run_all_scenarios()
        elif choice == "2":
            menu_run_selected_scenarios()
        elif choice == "3":
            menu_run_analysis()
        elif choice == "4":
            menu_paper_validation()
        elif choice == "5":
            menu_useful_time()
        elif choice == "6":
            menu_message_creation()
        elif choice == "7":
            menu_spatial()
        elif choice == "8":
            menu_dashboard()
        elif choice == "9":
            menu_figures_guide()
        elif choice == "10":
            menu_paper_ready_flow()
        elif choice == "11":
            menu_protocol_overlay_runs()
        else:
            print("Opción no reconocida.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrumpido.")
        raise SystemExit(130) from None