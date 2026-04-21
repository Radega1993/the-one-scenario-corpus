#!/usr/bin/env python3
"""
Ejecuta todas las simulaciones del corpus de escenarios (The ONE).
Por cada .settings ejecuta one.sh en modo batch (-b 1, sin GUI) y genera los reportes en reports/ (MessageStatsReport, etc.).

Uso:
  python run_all_scenarios.py --corpus corpus_v1
  python run_all_scenarios.py --corpus corpus_v1 --dry-run
  python run_all_scenarios.py --corpus corpus_v1 --timeout 14400   # 4 h por escenario

Requisitos: Java, el ONE compilado (one.sh en la raíz del repo). Los reportes se escriben
en el directorio configurado en cada .settings (por defecto reports/ en la raíz).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCENARIOS_DIR = BASE.parent
REPO_ROOT = SCENARIOS_DIR.parent


def collect_scenario_files(corpus_dir: Path, pattern: str = "**/*.settings") -> list[Path]:
    """Lista de .settings bajo corpus_dir (recursivo)."""
    return sorted(corpus_dir.glob(pattern))


def run_one_scenario(
    settings_path: Path,
    repo_root: Path,
    one_script: str,
    default_settings: str,
    extra_settings: str | None,
    dry_run: bool,
    timeout_s: int,
) -> tuple[bool, str]:
    """Ejecuta una simulación. Devuelve (éxito, mensaje_error)."""
    path = Path(settings_path)
    if not path.is_absolute():
        path = repo_root / path
    if not path.exists():
        return False, "archivo no encontrado"
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        rel = path
    if dry_run:
        print(f"  [dry-run] {rel}")
        return True, ""
    # -b 1 = batch mode (sin GUI), 1 run por archivo
    cmd = [one_script, "-b", "1", default_settings, str(rel)]
    if extra_settings:
        cmd.append(extra_settings)
    try:
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
        "--extra-settings",
        type=str,
        default=None,
        help="Settings adicional a aplicar al final (sobrescribe claves del escenario). Útil para forzar Report.* en todos los escenarios.",
    )
    args = ap.parse_args()

    repo_root = Path(args.repo_dir).resolve() if args.repo_dir else REPO_ROOT
    corpus_dir = SCENARIOS_DIR / args.corpus
    if not corpus_dir.exists():
        corpus_dir = Path(args.corpus)
    if not corpus_dir.exists():
        print(f"Error: no existe el directorio del corpus: {corpus_dir}", file=sys.stderr)
        return 1

    one_script = repo_root / "one.sh"
    if not one_script.exists():
        print(f"Error: no encontrado {one_script}. Ejecuta desde el repo del ONE.", file=sys.stderr)
        return 1
    default_settings = "default_settings.txt"
    extra_settings = args.extra_settings
    if extra_settings:
        extra_path = Path(extra_settings)
        if not extra_path.is_absolute():
            extra_path = repo_root / extra_path
        if not extra_path.exists():
            print(f"Error: no existe --extra-settings: {extra_path}", file=sys.stderr)
            return 1
        try:
            extra_settings = str(extra_path.relative_to(repo_root))
        except ValueError:
            extra_settings = str(extra_path)

    scenario_paths = collect_scenario_files(corpus_dir)
    if not scenario_paths:
        print(f"No hay archivos .settings en {corpus_dir}")
        return 0

    n = len(scenario_paths)
    print(f"Corpus: {corpus_dir.relative_to(repo_root) if repo_root in corpus_dir.parents else corpus_dir}")
    print(f"Escenarios: {n}")
    print(f"Repositorio: {repo_root}")
    if args.dry_run:
        print("Modo dry-run: no se ejecutan simulaciones.")
        for i, p in enumerate(scenario_paths, 1):
            try:
                rel = p.relative_to(repo_root)
            except ValueError:
                rel = p
            print(f"  {i:3d}/{n}  {rel}")
        return 0

    ok = 0
    fail = 0
    for i, p in enumerate(scenario_paths, 1):
        try:
            rel = p.relative_to(repo_root)
        except ValueError:
            rel = p
        print(f"[{i}/{n}] {rel} ... ", end="", flush=True)
        success, err_msg = run_one_scenario(
            p, repo_root, str(one_script), default_settings, extra_settings, dry_run=False, timeout_s=args.timeout
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

    print("")
    print(f"Resumen: {ok} OK, {fail} fallos de {n} escenarios.")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
