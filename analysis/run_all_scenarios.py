#!/usr/bin/env python3
"""
Ejecuta todas las simulaciones del corpus de escenarios (The ONE).
Por cada .settings ejecuta one.sh en modo batch (-b 1, sin GUI) y genera los reportes en reports/ (MessageStatsReport, etc.).

Uso:
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --dry-run
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \\
    --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \\
    --extra-settings scenarios/analysis/spatial_occupancy_reports_overrides.txt
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \\
    --name-regex 'U1_CBD.*__TP03' --dry-run
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --gui \\
    --settings scenarios/corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium__TP01_Baseline.settings
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \\
    --settings path/a.settings --settings path/b.settings --jobs 2
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --family 01_urban
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --tp TP07
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \\
    --family 01_urban --tp TP01 --tp TP05
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \\
    --select-file scenarios/analysis/my_selection.txt

``--corpus corpus_v1`` runs the 540 environmental scenarios (families 01–06).

Benchmark-aware modes (use benchmark_definition.csv):
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --benchmark core
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --benchmark core --estimate-runtime
  python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --benchmark core \\
    --family 01_urban --tp TP01 --dry-run

Requisitos: Java, el ONE compilado (one.sh en la raíz del repo). Los reportes se escriben
en el directorio configurado en cada .settings (por defecto reports/ en la raíz).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCENARIOS_DIR = BASE.parent
REPO_ROOT = SCENARIOS_DIR.parent
DATA_DIR = BASE / "data"

if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from lib.benchmark_select import load_endtimes, select_by_benchmark  # noqa: E402
from lib.paths import (  # noqa: E402
    COMBINED_MANIFEST_CSV,
    DEFAULT_MANIFEST_V1,
    PAPER_BENCHMARK_CORPORA,
    build_combined_manifest_csv,
    collect_settings_paths,
    primary_corpus_dir,
)
from lib.scenario_select import (  # noqa: E402
    list_families,
    parse_select_file,
    select_scenario_paths,
)

# ── Reproducibility helpers ──────────────────────────────────────────────

def _get_git_hash(repo_root: Path) -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root, capture_output=True, text=True, timeout=5,
        )
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"

def _get_java_version() -> str:
    try:
        r = subprocess.run(
            ["java", "-version"],
            capture_output=True, text=True, timeout=5,
        )
        out = (r.stderr or r.stdout or "").strip()
        return out.splitlines()[0] if out else "unknown"
    except Exception:
        return "unknown"

def _get_one_version(repo_root: Path) -> str:
    hist = repo_root / "HISTORY.txt"
    if hist.is_file():
        for line in hist.read_text(errors="replace").splitlines():
            line = line.strip()
            if line:
                return line
    return "unknown"

def resolve_settings_path(settings_path: Path, repo_root: Path) -> tuple[Path, str]:
    """Return absolute path and repo-relative path string for one.sh."""
    path = Path(settings_path)
    if not path.is_absolute():
        path = repo_root / path
    if not path.exists():
        raise FileNotFoundError(str(path))
    try:
        rel = str(path.relative_to(repo_root))
    except ValueError:
        rel = str(path)
    return path, rel

def run_one_scenario(
    settings_path: Path,
    repo_root: Path,
    one_script: str,
    default_settings: str,
    extra_settings: list[str] | None,
    dry_run: bool,
    timeout_s: int,
    *,
    gui: bool = False,
) -> tuple[bool, str]:
    """Ejecuta una simulación. Devuelve (éxito, mensaje_error)."""
    try:
        _path, rel = resolve_settings_path(settings_path, repo_root)
    except FileNotFoundError:
        return False, "archivo no encontrado"
    if dry_run:
        mode = "GUI" if gui else "batch"
        print(f"  [dry-run/{mode}] {rel}")
        return True, ""
    if gui:
        cmd = [one_script, default_settings, rel]
    else:
        # -b 1 = batch mode (sin GUI), 1 run por archivo
        cmd = [one_script, "-b", "1", default_settings, rel]
    if extra_settings:
        cmd.extend(extra_settings)
    try:
        if gui:
            r = subprocess.run(cmd, cwd=repo_root)
            return r.returncode == 0, ""
        r = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        err = (r.stderr or "").strip()
        if r.returncode != 0 and err:
            return False, err
        return r.returncode == 0, err
    except subprocess.TimeoutExpired:
        return False, f"Timeout ({timeout_s}s): la simulación no terminó a tiempo; los reportes quedan vacíos."

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Ejecutar todas las simulaciones del corpus (The ONE).",
    )
    ap.add_argument(
        "--corpus",
        type=str,
        default="corpus_v1",
        help="Directorio del corpus bajo scenarios/ (default: corpus_v1)",
    )
    ap.add_argument(
        "--repo-dir",
        type=str,
        default=None,
        help="Raíz del repositorio (default: padre de scenarios/)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo listar escenarios, no ejecutar",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=7200,
        metavar="SEG",
        help="Timeout por escenario en segundos (default: 7200 = 2h). Si se supera, el proceso se mata y los reportes quedan vacíos.",
    )
    ap.add_argument(
        "--jobs",
        type=int,
        default=1,
        metavar="N",
        help="Numero de simulaciones en paralelo (default: 1).",
    )
    ap.add_argument(
        "--extra-settings",
        action="append",
        default=None,
        metavar="PATH",
        help=(
            "Settings adicional a aplicar al final (puede repetirse; orden importa). "
            "Útil para forzar Report.* y/o overlays de router/protocolo."
        ),
    )
    ap.add_argument(
        "--name-regex",
        type=str,
        default=None,
        metavar="REGEX",
        help="Si se define, solo ejecuta escenarios cuya ruta/nombre coincida (re.search)",
    )
    ap.add_argument(
        "--settings",
        action="append",
        default=None,
        metavar="PATH",
        help=(
            "Uno o más .settings concretos (puede repetirse). "
            "Si se usa, define la lista de escenarios (junto con --name-regex sobre esas rutas)."
        ),
    )
    ap.add_argument(
        "--gui",
        action="store_true",
        help="Modo visual (GUI de The ONE). Sin -b; no usar --jobs>1. Ignora timeout.",
    )
    ap.add_argument(
        "--family",
        action="append",
        default=None,
        metavar="ID",
        help="Solo escenarios bajo esta familia (carpeta bajo el corpus, ej. 01_urban). Repetible (OR).",
    )
    ap.add_argument(
        "--tp",
        "--traffic-profile",
        dest="traffic_profiles",
        action="append",
        default=None,
        metavar="TP",
        help="Solo escenarios con este perfil (ej. TP07 o 7). Repetible (OR).",
    )
    ap.add_argument(
        "--scenario-base",
        action="append",
        default=None,
        metavar="BASE",
        help="Solo escenarios con este nombre base (antes de __TP). Repetible (OR).",
    )
    ap.add_argument(
        "--select-file",
        type=str,
        default=None,
        metavar="PATH",
        help=(
            "Archivo de selección: líneas con rutas .settings, o family:01_urban, tp:TP07, "
            "base:Nombre, regex:patrón (ver lib/scenario_select.py)."
        ),
    )
    ap.add_argument(
        "--benchmark",
        choices=["core", "all"],
        default=None,
        help=(
            "Filtrar por tier de benchmark (benchmark_definition.csv). "
            "core/all = 540 escenarios ambientales en corpus_v1."
        ),
    )
    ap.add_argument(
        "--exclude-deprecated",
        action="store_true",
        default=False,
        help="Excluir escenarios marcados como deprecated en benchmark_definition.csv.",
    )
    ap.add_argument(
        "--estimate-runtime",
        action="store_true",
        help="Mostrar estimación de tiempo total de simulación y salir sin ejecutar.",
    )
    ap.add_argument(
        "--reproducibility-log",
        type=str,
        default=None,
        metavar="PATH",
        help="Escribir metadatos de reproducibilidad en JSON (default: reports/reproducibility_metadata.json).",
    )
    args = ap.parse_args()

    repo_root = Path(args.repo_dir).resolve() if args.repo_dir else REPO_ROOT
    if args.corpus in PAPER_BENCHMARK_CORPORA:
        corpus_dir = primary_corpus_dir(args.corpus)
        build_combined_manifest_csv()
    else:
        corpus_dir = SCENARIOS_DIR / args.corpus
        if not corpus_dir.exists():
            corpus_dir = Path(args.corpus)
    if not corpus_dir.exists() and args.corpus not in PAPER_BENCHMARK_CORPORA:
        print(f"Error: no existe el directorio del corpus: {corpus_dir}", file=sys.stderr)
        return 1

    one_script = repo_root / "one.sh"
    if not one_script.exists():
        print(f"Error: no encontrado {one_script}. Ejecuta desde el repo del ONE.", file=sys.stderr)
        return 1
    default_settings = "default_settings.txt"
    extra_settings_paths: list[str] = []
    if args.extra_settings:
        for raw in args.extra_settings:
            extra_path = Path(raw)
            if not extra_path.is_absolute():
                extra_path = repo_root / extra_path
            if not extra_path.exists():
                print(f"Error: no existe --extra-settings: {extra_path}", file=sys.stderr)
                return 1
            try:
                extra_settings_paths.append(str(extra_path.relative_to(repo_root)))
            except ValueError:
                extra_settings_paths.append(str(extra_path))

    explicit: list[Path] | None = None
    families = list(args.family) if args.family else None
    tps = list(args.traffic_profiles) if args.traffic_profiles else None
    bases = list(args.scenario_base) if args.scenario_base else None
    name_rx = args.name_regex

    if args.select_file:
        sf = Path(args.select_file)
        if not sf.is_absolute():
            sf = repo_root / sf
        if not sf.is_file():
            print(f"Error: no existe --select-file: {sf}", file=sys.stderr)
            return 1
        spec = parse_select_file(sf, repo_root)
        if spec.get("settings"):
            explicit = [Path(s) for s in spec["settings"]]
        if spec.get("families"):
            families = (families or []) + spec["families"]
        if spec.get("traffic_profiles"):
            tps = (tps or []) + spec["traffic_profiles"]
        if spec.get("scenario_bases"):
            bases = (bases or []) + spec["scenario_bases"]
        if spec.get("name_regex") and not name_rx:
            name_rx = spec["name_regex"]

    if args.settings:
        explicit = explicit or []
        for raw in args.settings:
            p = Path(raw)
            if not p.is_absolute():
                p = repo_root / p
            if not p.is_file():
                print(f"Error: no existe --settings: {p}", file=sys.stderr)
                return 1
            explicit.append(p)

    try:
        scenario_paths = select_scenario_paths(
            corpus_dir,
            repo_root,
            explicit_settings=explicit,
            families=families,
            traffic_profiles=tps,
            scenario_bases=bases,
            name_regex=name_rx,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # ── Benchmark-tier filtering ─────────────────────────────────────────
    bench_csv = DATA_DIR / "benchmark_definition.csv"
    if args.benchmark and bench_csv.is_file():
        bench_names = select_by_benchmark(
            bench_csv, args.benchmark,
            exclude_deprecated=True,
        )
        scenario_paths = [
            p for p in scenario_paths if p.stem in bench_names
        ]
    elif args.exclude_deprecated and bench_csv.is_file():
        all_active = select_by_benchmark(bench_csv, "all", exclude_deprecated=True)
        scenario_paths = [
            p for p in scenario_paths if p.stem in all_active
        ]

    if not scenario_paths:
        print("No hay escenarios que coincidan con los filtros.", file=sys.stderr)
        if not explicit and not families and not tps and not bases and not name_rx:
            fams = list_families(corpus_dir)
            if fams:
                print(f"Familias en corpus: {', '.join(fams)}", file=sys.stderr)
        return 0

    n = len(scenario_paths)
    print(f"Corpus: {corpus_dir.relative_to(repo_root) if repo_root in corpus_dir.parents else corpus_dir}")
    filters: list[str] = []
    if args.benchmark:
        filters.append(f"benchmark={args.benchmark}")
    if args.exclude_deprecated:
        filters.append("exclude-deprecated")
    if explicit:
        filters.append(f"{len(explicit)} ruta(s) explícita(s)")
    if families:
        filters.append(f"family={','.join(families)}")
    if tps:
        filters.append(f"tp={','.join(tps)}")
    if bases:
        filters.append(f"base={','.join(bases)}")
    if name_rx:
        filters.append(f"regex={name_rx!r}")
    if filters:
        print(f"Filtros: {'; '.join(filters)}")
    print(f"Escenarios: {n}")
    print(f"Repositorio: {repo_root}")

    # ── Estimate runtime ─────────────────────────────────────────────────
    if args.estimate_runtime:
        manifest = (
            COMBINED_MANIFEST_CSV
            if args.corpus in ("corpus_v1", "corpus_v1") and COMBINED_MANIFEST_CSV.is_file()
            else SCENARIOS_DIR / args.corpus / "manifest.csv"
        )
        if not manifest.is_file() and args.corpus in ("corpus_v1", "corpus_v1"):
            manifest = DEFAULT_MANIFEST_V1
        if manifest.is_file():
            endtimes = load_endtimes(manifest)
            names = [p.stem for p in scenario_paths]
            total_sim_s = sum(endtimes.get(name, 43200) for name in names)
            total_sim_h = total_sim_s / 3600
            print(f"\n--- Estimación de tiempo ---")
            print(f"Escenarios seleccionados: {n}")
            print(f"Tiempo simulado total: {total_sim_s:,} s ({total_sim_h:.1f} h)")
            print(f"Wall-clock estimado (1 worker, ~1x speed): ~{total_sim_h:.1f} h")
            jobs_est = max(1, args.jobs)
            if jobs_est > 1:
                print(f"Wall-clock estimado ({jobs_est} workers): ~{total_sim_h / jobs_est:.1f} h")
        else:
            print(f"Aviso: manifest no encontrado ({manifest}), no se puede estimar.")
        return 0

    print(f"Modo: {'GUI (visual)' if args.gui else 'batch (segundo plano)'}")
    if args.gui and args.jobs > 1:
        print("Aviso: modo GUI fuerza --jobs 1 (un escenario a la vez).", file=sys.stderr)
        args.jobs = 1
    if args.dry_run:
        print("Modo dry-run: no se ejecutan simulaciones.")
        for i, p in enumerate(scenario_paths, 1):
            try:
                rel = p.relative_to(repo_root)
            except ValueError:
                rel = p
            print(f"  {i:3d}/{n}  {rel}")
        return 0

    jobs = 1 if args.gui else max(1, args.jobs)
    ok = 0
    fail = 0
    t_start = time.monotonic()
    if jobs == 1:
        for i, p in enumerate(scenario_paths, 1):
            try:
                rel = p.relative_to(repo_root)
            except ValueError:
                rel = p
            print(f"[{i}/{n}] {rel} ... ", end="", flush=True)
            if args.gui:
                print("(GUI — cierra la ventana para continuar)")
            success, err_msg = run_one_scenario(
                p,
                repo_root,
                str(one_script),
                default_settings,
                extra_settings_paths if extra_settings_paths else None,
                dry_run=False,
                timeout_s=args.timeout,
                gui=args.gui,
            )
            if success:
                print("OK")
                ok += 1
            else:
                print("FALLO")
                if err_msg:
                    for line in err_msg.splitlines()[:5]:
                        print(f"    {line}")
                fail += 1
    else:
        print(f"Paralelo: {jobs} workers")
        future_map = {}
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            for i, p in enumerate(scenario_paths, 1):
                future = ex.submit(
                    run_one_scenario,
                    p,
                    repo_root,
                    str(one_script),
                    default_settings,
                    extra_settings_paths if extra_settings_paths else None,
                    False,
                    args.timeout,
                    gui=False,
                )
                future_map[future] = (i, p)

            done = 0
            for future in as_completed(future_map):
                done += 1
                i, p = future_map[future]
                try:
                    rel = p.relative_to(repo_root)
                except ValueError:
                    rel = p
                success, err_msg = future.result()
                if success:
                    print(f"[{done}/{n}] ({i}) {rel} ... OK")
                    ok += 1
                else:
                    print(f"[{done}/{n}] ({i}) {rel} ... FALLO")
                    if err_msg:
                        for line in err_msg.splitlines()[:5]:
                            print(f"    {line}")
                    fail += 1

    elapsed = time.monotonic() - t_start
    print("")
    print(f"Resumen: {ok} OK, {fail} fallos de {n} escenarios.")
    print(f"Tiempo total: {elapsed:.1f} s ({elapsed / 3600:.2f} h)")

    # ── Reproducibility metadata ─────────────────────────────────────────
    repro_path_str = args.reproducibility_log
    if repro_path_str is None and not args.dry_run:
        repro_path_str = str(repo_root / "reports" / "reproducibility_metadata.json")
    if repro_path_str and not args.dry_run:
        metadata = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command_line": sys.argv,
            "python_version": sys.version,
            "java_version": _get_java_version(),
            "one_version": _get_one_version(repo_root),
            "git_hash": _get_git_hash(repo_root),
            "benchmark_tier": args.benchmark or "unfiltered",
            "scenarios_run": n,
            "ok": ok,
            "fail": fail,
            "elapsed_seconds": round(elapsed, 2),
            "jobs": jobs,
            "filters": {
                "benchmark": args.benchmark,
                "exclude_deprecated": args.exclude_deprecated,
                "families": families,
                "traffic_profiles": tps,
                "scenario_bases": bases,
                "name_regex": name_rx,
            },
        }
        repro_path = Path(repro_path_str)
        if not repro_path.is_absolute():
            repro_path = repo_root / repro_path
        repro_path.parent.mkdir(parents=True, exist_ok=True)
        repro_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
        print(f"Metadatos de reproducibilidad: {repro_path}")

    return 0 if fail == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())