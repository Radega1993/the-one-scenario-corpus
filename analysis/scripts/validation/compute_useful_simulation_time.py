#!/usr/bin/env python3
"""
Compute useful simulation time metrics from ConnectivityONEReport traces.

Outputs:
  data/useful_simulation_time_metrics.csv
  reports/useful_simulation_time_report.md

Position logs are not in the current report pipeline; spatial exploration uses
pair-coverage over contact graph as proxy.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.connectivity_timeline import classify_useful_time, parse_connectivity_timeline
from lib.paths import (
    CORPUS_V1_DIR,
    DATA_DIR,
    REPORTS_DIR,
)
from lib.report_paths import USEFUL_SIMULATION_TIME_REPORT  # noqa: E402

REPORTS_OUT = USEFUL_SIMULATION_TIME_REPORT.parent

def parse_settings(text: str) -> dict[str, str]:
    d: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        d[k.strip()] = v.strip()
    return d

def infer_n_hosts(kv: dict[str, str]) -> int | None:
    ng = kv.get("Scenario.nrofHostGroups")
    if not ng:
        if "Group.nrofHosts" in kv:
            try:
                return int(kv["Group.nrofHosts"].split(",")[0])
            except ValueError:
                return None
        return None
    try:
        n_groups = int(ng)
    except ValueError:
        return None
    total = 0
    for i in range(1, n_groups + 1):
        key = f"Group{i}.nrofHosts"
        if key in kv:
            try:
                total += int(kv[key].replace(",", "").split()[0])
            except ValueError:
                pass
        elif i == 1 and "Group.nrofHosts" in kv:
            try:
                total += int(kv["Group.nrofHosts"].replace(",", "").split()[0])
            except ValueError:
                pass
    return total if total > 0 else None

def parse_scenario_name(name: str) -> tuple[str, str]:
    m = re.search(r"__(TP\d{2}_[A-Za-z0-9]+)$", name)
    if not m:
        return name, ""
    return name[: m.start()], m.group(1).split("_", 1)[0]

def _fnum(x) -> float | None:
    if x is None or x == "":
        return None
    try:
        v = float(x)
        return None if v != v else v
    except (TypeError, ValueError):
        return None

def load_settings_index(corpus_dir: Path) -> dict[str, Path]:
    return {p.stem: p for p in corpus_dir.rglob("*.settings")}

def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "scenario",
        "base_scenario",
        "traffic_profile",
        "end_time",
        "first_contact_time",
        "last_contact_time",
        "total_encounters",
        "contact_time_per_min",
        "ratio_contact_nodes",
        "pct_nodes_ever_contacted",
        "time_to_50pct_contact_nodes",
        "time_to_80pct_contact_nodes",
        "time_to_90pct_contact_nodes",
        "first_contact_time_median",
        "pair_coverage_final_pct",
        "time_to_90pct_pair_coverage",
        "useful_time_recommendation",
        "useful_time_ratio",
        "tail_time_ratio",
        "classification",
        "data_source",
        "spatial_data_available",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

def write_report(rows: list[dict], path: Path) -> None:
    by_class = defaultdict(list)
    by_base: dict[str, dict] = {}
    for r in rows:
        by_class[r["classification"]].append(r)
        base = r["base_scenario"]
        if base not in by_base:
            by_base[base] = r

    disconnected = [b for b, r in by_base.items() if r["classification"] == "disconnected"]
    sufficient = [b for b, r in by_base.items() if r["classification"] == "sufficient_activity"]
    late = sorted(b for b, r in by_base.items() if r["classification"] == "late_exploration")
    early_tail = [b for b, r in by_base.items() if r["classification"] == "early_saturation_long_tail"]

    ratios = [_fnum(r["useful_time_ratio"]) for r in by_base.values()]
    ratios = [x for x in ratios if x is not None]
    tails = [_fnum(r["tail_time_ratio"]) for r in by_base.values() if r["classification"] != "disconnected"]
    tails = [x for x in tails if x is not None]

    lines = [
        "# Tiempo útil de simulación — informe metodológico",
        "",
        f"Generado: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## 1. Fuentes de datos auditadas",
        "",
        "| Fuente | Disponible en pipeline actual | Uso en este informe |",
        "|--------|------------------------------|---------------------|",
        "| `ConnectivityONEReport` | Sí (720/720 en corpus_v1 con Diego17 overrides) | **Principal** — traza `CONN up/down` |",
        "| `MessageStatsReport` | Sí | No usado aquí (entrega, no exploración) |",
        "| `ContactTimesReport` / `TotalEncountersReport` | Sí | Fallback posible; no necesario con traza ONE |",
        "| Logs de posiciones (`MovementReport`, GPS) | **No** | Ocupación espacial vía **cobertura de pares** en grafo de contactos |",
        "",
        "## 2. Definición de tiempo útil",
        "",
        "En DTN, simular \"hasta el infinito\" haría converger muchas entregas; el `Scenario.endTime` debe ser "
        "**suficiente** para observar exploración de la red oportunista y un **cola de entrega**, sin ser arbitrariamente largo.",
        "",
        "### Métricas derivadas de conectividad",
        "",
        "| Métrica | Definición |",
        "|---------|------------|",
        "| `first_contact_time` | Primer evento `CONN … up` en la traza |",
        "| `last_contact_time` | Último evento de la traza (up o down) |",
        "| `total_encounters` | Número de eventos `CONN up` |",
        "| `contact_time_per_min` | `total_encounters / (end_time / 60)` |",
        "| `ratio_contact_nodes` | Grado medio normalizado en grafo de contactos (trace) |",
        "| `pct_nodes_ever_contacted` | % de hosts configurados con ≥1 contacto |",
        "| `time_to_Xpct_contact_nodes` | Primer instante en que X% de hosts han tenido su primer contacto |",
        "| `pair_coverage_final_pct` | Pares únicos observados / pares posibles (proxy espacial) |",
        "| `time_to_90pct_pair_coverage` | Instante en que se ha visto el 90% de pares que aparecerán |",
        "",
        "### Tiempo útil recomendado",
        "",
        "```",
        "useful_time_recommendation = min(end_time, max(time_to_90pct_contact_nodes, last_contact_time))",
        "```",
        "",
        "- **`useful_time_ratio`** = `useful_time_recommendation / end_time`",
        "- **`tail_time_ratio`** = `(end_time - useful_time_recommendation) / end_time` — cola reservada a entregas tardías / tráfico ya inyectado",
        "",
        "Interpretación:",
        "- **`tail_time_ratio` alto** (p. ej. >0.5): la simulación explora la red pronto y deja mucho margen para entrega (habitual en campus/urbano).",
        "- **`late_exploration`**: el 90% de nodos no se ha contactado hasta >90% de `endTime` — el `endTime` puede ser corto para la movilidad.",
        "- **`disconnected`**: sin eventos `CONN` — no hay tiempo útil oportunista (control negativo, p. ej. `R1`).",
        "",
        "## 3. Clasificación por escenario base",
        "",
        "| Clase | Criterio | Escenarios base (n) |",
        "|-------|----------|---------------------|",
        f"| `disconnected` | `total_encounters = 0` | {len(disconnected)} |",
        f"| `marginal_connectivity` | `<15%` nodos contactados | {len([b for b,r in by_base.items() if r['classification']=='marginal_connectivity'])} |",
        f"| `sufficient_activity` | ≥100 encuentros y ≥30% nodos | {len(sufficient)} |",
        f"| `late_exploration` | `t_90` > 90% `end_time` | {len(late)} |",
        f"| `early_saturation_long_tail` | `t_90` < 40% `end_time` y cola >50% | {len(early_tail)} |",
        f"| `moderate_activity` | resto | {len([b for b,r in by_base.items() if r['classification']=='moderate_activity'])} |",
        "",
    ]
    if late:
        lines += ["Bases `late_exploration`: " + ", ".join(f"`{b}`" for b in late) + ".", ""]

    if disconnected:
        lines += ["### Escenarios desconectados o casi desconectados", ""]
        lines += [f"- `{b}`" for b in sorted(disconnected)]
        lines += [""]

    if sufficient:
        lines += ["### Escenarios con actividad suficiente (muestra)", ""]
        for b in sorted(sufficient)[:15]:
            r = by_base[b]
            lines.append(
                f"- `{b}`: encounters={r['total_encounters']:.0f}, "
                f"pct_nodes={r['pct_nodes_ever_contacted']:.1f}%, "
                f"useful_ratio={float(r['useful_time_ratio']):.2f}"
            )
        if len(sufficient) > 15:
            lines.append(f"- … (+{len(sufficient) - 15} más en CSV)")
        lines += [""]

    lines += [
        "## 4. Agregados (60 bases, deduplicado por movilidad)",
        "",
        f"- Media `useful_time_ratio`: **{mean(ratios):.3f}** (mediana {median(ratios):.3f})" if ratios else "",
        f"- Media `tail_time_ratio` (con contacto): **{mean(tails):.3f}**" if tails else "",
        "",
        "**Nota:** la conectividad depende del escenario base (movilidad), no del perfil TP. "
        "En el CSV hay 720 filas (una por simulación); las métricas de contacto son **idénticas por base** "
        "salvo variación numérica entre corridas. Para el paper, reportar por **escenario base**.",
        "",
        "## 5. Política metodológica propuesta (paper / tesis)",
        "",
        "1. **Fijar `Scenario.endTime` por familia** (12 h estándar, ventanas cortas en C4/C6/T4…) como horizonte máximo.",
        "2. **Declarar tiempo útil** como el intervalo `[first_contact_time, useful_time_recommendation]` "
        "en el que la red oportunista ha sido explorada al 90% de nodos participantes.",
        "3. **Excluir o etiquetar** escenarios `disconnected` en agregados de protocolo (`R1` como control).",
        "4. **Justificar duración:** mostrar que `tail_time_ratio` deja margen para entrega DTN "
        "(no cortar la simulación en el pico de exploración).",
        "5. **No afirmar cobertura espacial real** sin logs GPS; citar `pair_coverage_final_pct` como proxy de diversidad de contactos.",
        "",
        "## 6. Limitaciones",
        "",
        "- Sin trazas de posición → no hay grid de ocupación real; solo proxy por pares de contacto.",
        "- Contactos abiertos al final de la simulación no suman duración (sesgo conservador en `contact_time_sum`).",
        "- El perfil de tráfico (TP) **no debería** alterar la movilidad; pequeñas diferencias entre corridas TP reflejan no-determinismo de ejecución, no diseño.",
        "- `useful_time_recommendation` no sustituye análisis de entrega: un escenario puede tener cola larga y aun así TTL crítico (TP05).",
        "",
        "## 7. Artefactos",
        "",
        "- CSV: `data/useful_simulation_time_metrics.csv`",
        "- Script: `compute_useful_simulation_time.py`",
        "- Parser: `lib/connectivity_timeline.py`",
        "",
        "## 8. Tabla resumen por escenario base",
        "",
        "| Base | end_time | encounters | % nodos | t_90 (s) | useful_ratio | class |",
        "|------|----------|------------|--------:|---------:|-------------:|-------|",
    ]

    for base in sorted(by_base.keys()):
        r = by_base[base]
        t90 = _fnum(r.get("time_to_90pct_contact_nodes"))
        t90s = f"{t90:.0f}" if t90 is not None else "—"
        lines.append(
            f"| `{base}` | {float(r['end_time']):.0f} | {float(r['total_encounters']):.0f} | "
            f"{float(r['pct_nodes_ever_contacted']):.1f} | {t90s} | "
            f"{float(r['useful_time_ratio']):.2f} | {r['classification']} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser(description="Compute useful simulation time metrics.")
    ap.add_argument("--corpus-dir", type=Path, default=CORPUS_V1_DIR)
    ap.add_argument("--reports-dir", type=Path, default=REPORTS_DIR)
    ap.add_argument("--data-dir", type=Path, default=DATA_DIR)
    ap.add_argument("--reports-out", type=Path, default=REPORTS_OUT)
    args = ap.parse_args()

    settings_index = load_settings_index(args.corpus_dir)
    rows: list[dict] = []

    for settings_path in sorted(args.corpus_dir.rglob("*.settings")):
        kv = parse_settings(settings_path.read_text(encoding="utf-8", errors="replace"))
        scenario = kv.get("Scenario.name", settings_path.stem)
        base, tp = parse_scenario_name(scenario)
        end_time = float(kv.get("Scenario.endTime", "43200").replace(",", "").split()[0])
        n_hosts = infer_n_hosts(kv)

        conn_path = args.reports_dir / f"{scenario}_ConnectivityONEReport.txt"
        metrics = parse_connectivity_timeline(conn_path, end_time, n_hosts=n_hosts)
        classification = classify_useful_time(metrics, end_time)

        rows.append({
            "scenario": scenario,
            "base_scenario": base,
            "traffic_profile": tp,
            "end_time": end_time,
            "first_contact_time": metrics["first_contact_time"],
            "last_contact_time": metrics["last_contact_time"],
            "total_encounters": metrics["total_encounters"],
            "contact_time_per_min": round(metrics["contact_time_per_min"], 4),
            "ratio_contact_nodes": round(metrics["ratio_contact_nodes"], 4),
            "pct_nodes_ever_contacted": round(metrics["pct_nodes_ever_contacted"], 2),
            "time_to_50pct_contact_nodes": metrics["time_to_50pct_contact_nodes"],
            "time_to_80pct_contact_nodes": metrics["time_to_80pct_contact_nodes"],
            "time_to_90pct_contact_nodes": metrics["time_to_90pct_contact_nodes"],
            "first_contact_time_median": metrics["first_contact_time_median"],
            "pair_coverage_final_pct": round(metrics["pair_coverage_final_pct"], 2),
            "time_to_90pct_pair_coverage": metrics["time_to_90pct_pair_coverage"],
            "useful_time_recommendation": round(metrics["useful_time_recommendation"], 2),
            "useful_time_ratio": round(metrics["useful_time_ratio"], 4),
            "tail_time_ratio": round(metrics["tail_time_ratio"], 4),
            "classification": classification,
            "data_source": "ConnectivityONEReport",
            "spatial_data_available": "no",
        })

    out_csv = args.data_dir / "useful_simulation_time_metrics.csv"
    write_csv(rows, out_csv)
    out_md = USEFUL_SIMULATION_TIME_REPORT if args.reports_out == REPORTS_OUT else args.reports_out / "useful_simulation_time_report.md"
    write_report(rows, out_md)

    print(f"Wrote {out_csv} ({len(rows)} rows)")
    print(f"Wrote {out_md}")
    from collections import Counter

    bases = {r["base_scenario"]: r["classification"] for r in rows}
    print("Classification (unique bases):", dict(Counter(bases.values())))
    return 0

if __name__ == "__main__":
    sys.exit(main())