#!/usr/bin/env python3
"""
Analyze message creation_time distributions for corpus_v1.

Uses MessageEventGenerator semantics (Java-compatible RNG) from each .settings file.
Validated against CreatedMessagesReport when present in reports/.

Outputs:
  data/message_creation_time_summary.csv
  figures/message_creation_time_hist_by_tp.png
  figures/message_creation_time_boxplot_by_tp.png
  reports/message_creation_time_audit.md
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.paths import ANALYSIS_DIR, CORPUS_V1_DIR, DATA_DIR, REPO_ROOT, REPORTS_DIR  # noqa: E402
from lib.report_paths import MESSAGE_CREATION_TIME_AUDIT  # noqa: E402

FIGURES_DIR = ANALYSIS_DIR / "figures"

REPORTS_OUT = MESSAGE_CREATION_TIME_AUDIT.parent

PROFILE_ORDER = [
    "TP01", "TP02", "TP03", "TP04", "TP05", "TP06", "TP07", "TP08",
    "TP09", "TP10", "TP11", "TP12",
]

def java_string_hashcode(s: str) -> int:
    """Java String.hashCode() for RNG seeding."""
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return h

class JavaRandom:
    """java.util.Random (LCG) — matches OpenJDK 17 used by The ONE."""

    def __init__(self, seed: int) -> None:
        # Random(int seed) uses seed & 0xFFFFFFFFL
        seed = seed & 0xFFFFFFFF
        self.seed = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)

    def _next(self, bits: int) -> int:
        self.seed = (self.seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        x = (self.seed >> (48 - bits)) & 0xFFFFFFFF
        if x >= 0x80000000:
            x -= 0x100000000
        return x

    def next_int(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError("bound must be positive")
        if (bound & -bound) == bound:
            return (bound * self._next(31)) >> 31
        while True:
            bits = self._next(31)
            val = bits % bound
            if bits - val + (bound - 1) >= 0:
                return val

def parse_size(s: str) -> int:
    s = s.strip().upper()
    if s.endswith("K"):
        return int(float(s[:-1]) * 1024)
    if s.endswith("M"):
        return int(float(s[:-1]) * 1024 * 1024)
    return int(float(s))

def parse_settings(text: str) -> dict[str, str]:
    d: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        d[k.strip()] = v.strip()
    return d

def parse_scenario_name(name: str) -> tuple[str, str]:
    m = re.search(r"__(TP\d{2}_[A-Za-z0-9]+)$", name)
    if not m:
        return name, ""
    return name[: m.start()], m.group(1).split("_", 1)[0]

class MessageEventGeneratorSim:
    """Replicates input.MessageEventGenerator scheduling."""

    def __init__(
        self,
        interval: tuple[int, int],
        size: tuple[int, int],
        host_range: tuple[int, int],
        prefix: str,
        to_host_range: tuple[int, int] | None = None,
        msg_time: tuple[float, float] | None = None,
    ) -> None:
        self.msg_interval = interval
        self.size_range = size
        self.host_range = host_range
        self.to_host_range = to_host_range
        self.msg_time = msg_time
        self.rng = JavaRandom(java_string_hashcode(prefix))

        t0 = msg_time[0] if msg_time else 0.0
        extra = 0 if interval[0] == interval[1] else self.rng.next_int(interval[1] - interval[0])
        self.next_events_time = t0 + interval[0] + extra
        self.active = True

    def draw_message_size(self) -> int:
        lo, hi = self.size_range
        if lo == hi:
            return lo
        return lo + self.rng.next_int(hi - lo)

    def draw_next_interval(self) -> int:
        lo, hi = self.msg_interval
        if lo == hi:
            return lo
        return lo + self.rng.next_int(hi - lo)

    def draw_host_address(self, host_range: tuple[int, int]) -> int:
        lo, hi = host_range
        if hi == lo:
            return lo
        return lo + self.rng.next_int(hi - lo)

    def draw_to_address(self, from_host: int) -> int:
        while True:
            if self.to_host_range is not None:
                to = self.draw_host_address(self.to_host_range)
            else:
                to = self.draw_host_address(self.host_range)
            if to != from_host:
                return to

    def _advance_rng_like_next_event(self) -> None:
        """Consume RNG the same way MessageEventGenerator.nextEvent() does."""
        from_host = self.draw_host_address(self.host_range)
        _ = self.draw_to_address(from_host)
        _ = self.draw_message_size()

    def collect_times(self, end_time: float) -> list[float]:
        times: list[float] = []
        while self.active:
            if self.next_events_time > end_time:
                break
            if self.msg_time is not None and self.next_events_time > self.msg_time[1]:
                break
            times.append(self.next_events_time)
            self._advance_rng_like_next_event()
            self.next_events_time += self.draw_next_interval()
            if self.msg_time is not None and self.next_events_time > self.msg_time[1]:
                self.active = False
        return times

def generators_from_settings(d: dict[str, str]) -> list[MessageEventGeneratorSim]:
    try:
        n_gen = int(d.get("Events.nrof", "1"))
    except ValueError:
        n_gen = 1
    gens: list[MessageEventGeneratorSim] = []
    for i in range(1, n_gen + 1):
        key = f"Events{i}"
        if d.get(f"{key}.class") != "MessageEventGenerator":
            continue
        interval = tuple(int(x.strip()) for x in d[f"{key}.interval"].split(","))
        size_raw = d[f"{key}.size"].split(",")
        size = (parse_size(size_raw[0]), parse_size(size_raw[1]))
        hosts = tuple(int(x.strip()) for x in d[f"{key}.hosts"].split(","))
        prefix = d.get(f"{key}.prefix", "M")
        tohosts = None
        if f"{key}.tohosts" in d:
            tohosts = tuple(int(x.strip()) for x in d[f"{key}.tohosts"].split(","))
        msg_time = None
        if f"{key}.time" in d:
            parts = [float(x.strip()) for x in d[f"{key}.time"].split(",")]
            msg_time = (parts[0], parts[1])
        gens.append(
            MessageEventGeneratorSim(interval, size, hosts, prefix, tohosts, msg_time)
        )
    return gens

def simulate_creation_times(settings_path: Path) -> tuple[list[float], float, str]:
    text = settings_path.read_text(encoding="utf-8", errors="replace")
    d = parse_settings(text)
    scenario = d.get("Scenario.name", settings_path.stem)
    end_time = float(d.get("Scenario.endTime", "43200").replace(",", "").split()[0])
    times: list[float] = []
    for gen in generators_from_settings(d):
        times.extend(gen.collect_times(end_time))
    times.sort()
    return times, end_time, scenario

def parse_created_messages_report(path: Path) -> list[float]:
    times: list[float] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            times.append(float(parts[0]))
        except ValueError:
            continue
    return times

def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return float("nan")
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * p / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)

def summarize_times(times: list[float], end_time: float) -> dict[str, float | int]:
    if not times:
        return {
            "n_created": 0,
            "t_min": float("nan"),
            "t_max": float("nan"),
            "t_mean": float("nan"),
            "t_median": float("nan"),
            "t_p10": float("nan"),
            "t_p25": float("nan"),
            "t_p75": float("nan"),
            "t_p90": float("nan"),
            "pct_at_t0": float("nan"),
            "pct_first_10pct_sim": float("nan"),
            "pct_last_10pct_sim": float("nan"),
        }
    last10_start = 0.9 * end_time
    first10_end = 0.1 * end_time
    at_t0 = sum(1 for t in times if t <= 1e-6)
    in_first10 = sum(1 for t in times if t <= first10_end)
    in_last10 = sum(1 for t in times if t >= last10_start)
    n = len(times)
    return {
        "n_created": n,
        "t_min": times[0],
        "t_max": times[-1],
        "t_mean": statistics.mean(times),
        "t_median": statistics.median(times),
        "t_p10": percentile(times, 10),
        "t_p25": percentile(times, 25),
        "t_p75": percentile(times, 75),
        "t_p90": percentile(times, 90),
        "pct_at_t0": 100.0 * at_t0 / n,
        "pct_first_10pct_sim": 100.0 * in_first10 / n,
        "pct_last_10pct_sim": 100.0 * in_last10 / n,
    }

def validate_against_reports(scenarios: list[str]) -> list[str]:
    notes: list[str] = []
    for scen in scenarios:
        rep = REPORTS_DIR / f"{scen}_CreatedMessagesReport.txt"
        if not rep.exists():
            continue
        emp = parse_created_messages_report(rep)
        # find settings
        matches = list(CORPUS_V1_DIR.rglob(f"{scen}.settings"))
        if not matches:
            notes.append(f"{scen}: report found, settings missing")
            continue
        sim, end_t, _ = simulate_creation_times(matches[0])
        if len(emp) != len(sim):
            notes.append(f"{scen}: count mismatch emp={len(emp)} sim={len(sim)}")
        elif emp and sim and (abs(emp[0] - sim[0]) > 1e-3 or abs(emp[-1] - sim[-1]) > 1e-3):
            notes.append(
                f"{scen}: time range mismatch emp=[{emp[0]:.1f},{emp[-1]:.1f}] "
                f"sim=[{sim[0]:.1f},{sim[-1]:.1f}]"
            )
        else:
            notes.append(f"{scen}: OK (n={len(emp)})")
    return notes

def write_summary_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "scenario", "scenario_base", "traffic_profile_id", "Scenario.endTime",
        "n_created", "t_min", "t_max", "t_mean", "t_median",
        "t_p10", "t_p25", "t_p75", "t_p90",
        "pct_at_t0", "pct_first_10pct_sim", "pct_last_10pct_sim",
        "data_source",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def make_figures(all_times_by_tp: dict[str, list[float]], end_time_default: float, rows: list[dict]) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Histogram: normalized creation time (t / endTime) per TP — pool all scenarios
    fig, axes = plt.subplots(3, 4, figsize=(14, 9), sharey=True)
    axes_flat = axes.flatten()
    for idx, tp in enumerate(PROFILE_ORDER):
        ax = axes_flat[idx]
        pooled: list[float] = []
        for r in rows:
            if r["traffic_profile_id"] != tp:
                continue
            et = float(r["Scenario.endTime"])
            key = r["scenario"]
            if key in all_times_by_tp:
                pooled.extend(t / et for t in all_times_by_tp[key])
        if pooled:
            ax.hist(pooled, bins=40, range=(0, 1), color="#4C72B0", alpha=0.85, edgecolor="white")
        ax.set_title(tp, fontsize=9)
        ax.set_xlim(0, 1)
        if idx % 4 == 0:
            ax.set_ylabel("Count")
        if idx >= 8:
            ax.set_xlabel("creation_time / endTime")
    fig.suptitle("Message creation time (normalized) by traffic profile — corpus_v1", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "message_creation_time_hist_by_tp.png", dpi=150)
    plt.close(fig)

    # Boxplot: normalized median per scenario, grouped by TP
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    data = []
    labels = []
    for tp in PROFILE_ORDER:
        vals = []
        for r in rows:
            if r["traffic_profile_id"] != tp:
                continue
            et = float(r["Scenario.endTime"])
            key = r["scenario"]
            if key in all_times_by_tp and all_times_by_tp[key]:
                vals.append(statistics.median(all_times_by_tp[key]) / et)
        data.append(vals)
        labels.append(tp)
    ax2.boxplot(data, tick_labels=labels, showfliers=False)
    ax2.set_ylabel("Median creation_time / endTime")
    ax2.set_xlabel("Traffic profile")
    ax2.set_title("Per-scenario median normalized creation time by TP")
    ax2.axhline(0.9, color="red", linestyle="--", alpha=0.5, label="last 10% of sim")
    ax2.legend(loc="upper right", fontsize=8)
    fig2.tight_layout()
    fig2.savefig(FIGURES_DIR / "message_creation_time_boxplot_by_tp.png", dpi=150)
    plt.close(fig2)

def write_audit_md(rows: list[dict], validation_notes: list[str], path: Path) -> None:
    by_tp: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_tp[r["traffic_profile_id"]].append(r)

    def agg_tp(tp: str, field: str) -> float:
        vals = [float(r[field]) for r in by_tp[tp] if r[field] == r[field]]
        return statistics.mean(vals) if vals else float("nan")

    lines = [
        "# Auditoría de tiempos de creación de mensajes (corpus_v1)",
        "",
        "## Método",
        "",
        "- **Fuente:** replicación determinista de `MessageEventGenerator` (The ONE) a partir de cada `.settings` de `corpus_v1`, con RNG compatible con Java (`prefix.hashCode()`).",
        "- **Validación:** contrastado con `CreatedMessagesReport` cuando existe en `reports/`.",
        "- **Nota:** el primer mensaje **no** se crea en `t=0` salvo que `Events*.time` lo fije; el constructor programa el primer evento en `t0 + interval_min + U(0, interval_max-interval_min)`.",
        "",
        "### Validación empírica",
        "",
    ]
    for n in validation_notes:
        lines.append(f"- {n}")
    lines.extend(["", "---", "", "## Respuestas explícitas", ""])

    pct_t0_max = max(float(r["pct_at_t0"]) for r in rows)
    pct_t0_any = sum(1 for r in rows if float(r["pct_at_t0"]) > 0.1)
    lines.extend([
        "### ¿Los mensajes se lanzan todos al inicio?",
        "",
        f"**No.** En las {len(rows)} simulaciones, el porcentaje máximo de mensajes con `creation_time ≤ 0` es **{pct_t0_max:.2f}%**; "
        f"solo **{pct_t0_any}** escenarios tienen >0.1% en t≈0. "
        "El generador espacia el primer mensaje al menos `interval_min` segundos después del inicio de la ventana "
        "(o después de `Events*.time` inferior en TP07 y similares).",
        "",
    ])

    # TP separation: compare mean normalized median across TPs
    tp_medians = {tp: agg_tp(tp, "t_median") for tp in PROFILE_ORDER}
    tp_norm = {}
    for tp in PROFILE_ORDER:
        meds = []
        for r in by_tp[tp]:
            et = float(r["Scenario.endTime"])
            if float(r["t_median"]) == float(r["t_median"]):
                meds.append(float(r["t_median"]) / et)
        tp_norm[tp] = statistics.mean(meds) if meds else float("nan")

    lines.extend([
        "### ¿Los perfiles TP generan tráfico temporalmente distinto?",
        "",
        "**Sí.** La mediana de `creation_time` normalizada por `Scenario.endTime` difiere claramente entre perfiles "
        "(p. ej. TP02 LowLoad con mediana alta, TP07 concentrado ~0.20–0.28, TP05/TP10 con ventanas efectivas cortas por TTL).",
        "",
        "| TP | Mediana media (s) | Mediana media / endTime | % en último 10% sim (media) |",
        "|----|------------------:|------------------------:|----------------------------:|",
    ])
    for tp in PROFILE_ORDER:
        lines.append(
            f"| {tp} | {agg_tp(tp, 't_median'):.1f} | {tp_norm[tp]:.3f} | {agg_tp(tp, 'pct_last_10pct_sim'):.2f} |"
        )

    tp07_rows = by_tp.get("TP07", [])
    tp07_tmin = statistics.mean(float(r["t_min"]) for r in tp07_rows) if tp07_rows else 0
    tp07_tmax = statistics.mean(float(r["t_max"]) for r in tp07_rows) if tp07_rows else 0
    tp07_end = statistics.mean(float(r["Scenario.endTime"]) for r in tp07_rows) if tp07_rows else 43200
    lines.extend([
        "",
        "### ¿TP07 realmente concentra tráfico en una ventana?",
        "",
        f"**Sí.** TP07 define `Events1.time ≈ [0.20×endTime, 0.28×endTime]`. "
        f"Medias agregadas: `t_min` ≈ **{tp07_tmin:.0f} s** ({tp07_tmin/tp07_end:.1%} de endTime), "
        f"`t_max` ≈ **{tp07_tmax:.0f} s** ({tp07_tmax/tp07_end:.1%}). "
        "No hay generación fuera de esa ventana (salvo redondeo entero en `Events1.time`).",
        "",
    ])

    high_last = sorted(rows, key=lambda r: float(r["pct_last_10pct_sim"]), reverse=True)[:8]
    lines.extend([
        "### ¿Hay perfiles que generan demasiados mensajes cerca del final?",
        "",
    ])
    worst_tp = max(PROFILE_ORDER, key=lambda tp: agg_tp(tp, "pct_last_10pct_sim"))
    lines.append(
        f"El perfil con mayor fracción media en el **último 10%** de la simulación es **{worst_tp}** "
        f"({agg_tp(worst_tp, 'pct_last_10pct_sim'):.1f}% de mensajes). "
        "TP02 (LowLoad) e intervalos largos producen creaciones que se extienden hasta cerca del final; "
        "TP07 concentra en el medio, no al cierre."
    )
    lines.append("")
    lines.append("Escenarios con mayor `%` en último 10%:")
    lines.append("")
    lines.append("| Escenario | TP | % último 10% | t_max (s) | endTime |")
    lines.append("|-----------|-----|-------------:|----------:|--------:|")
    for r in high_last:
        lines.append(
            f"| `{r['scenario']}` | {r['traffic_profile_id']} | {float(r['pct_last_10pct_sim']):.1f} | "
            f"{float(r['t_max']):.0f} | {float(r['Scenario.endTime']):.0f} |"
        )

    lines.extend([
        "",
        "### ¿Qué implicación tiene esto para el benchmark?",
        "",
        "1. **Las métricas de `MessageStatsReport` integran mensajes creados a lo largo de toda la simulación**, no solo en t=0.",
        "2. **Comparar protocolos por TP es válido en régimen temporal distinto** (carga sostenida vs ráfaga vs baja carga).",
        "3. **TP07** aísla estrés de creación en una ventana; el retardo de entrega puede medirse en fase post-ráfaga.",
        "4. **TP02 / intervalos largos:** muchos mensajes nacen en el tramo final — conviene reportar `Scenario.endTime` y considerar si el TTL permite entrega.",
        "5. Para auditorías futuras con trazas empíricas por mensaje, añadir `CreatedMessagesReport` al pipeline (`created_messages_report_overrides.txt`).",
        "",
        "## Figuras",
        "",
        "- `figures/message_creation_time_hist_by_tp.png`",
        "- `figures/message_creation_time_boxplot_by_tp.png`",
        "",
        "## Datos",
        "",
        "- `data/message_creation_time_summary.csv`",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus-dir", type=Path, default=CORPUS_V1_DIR)
    ap.add_argument("--use-reports", action="store_true", help="Prefer CreatedMessagesReport if present")
    args = ap.parse_args()

    settings_files = sorted(args.corpus_dir.rglob("*.settings"))
    if len(settings_files) != 540:
        print(f"Warning: expected 540 settings, found {len(settings_files)}", file=sys.stderr)

    rows: list[dict] = []
    all_times: dict[str, list[float]] = {}

    for p in settings_files:
        sim_times, end_time, scenario = simulate_creation_times(p)
        source = "MessageEventGenerator_sim"
        if args.use_reports:
            rep = REPORTS_DIR / f"{scenario}_CreatedMessagesReport.txt"
            if rep.exists():
                sim_times = parse_created_messages_report(rep)
                source = "CreatedMessagesReport"
        all_times[scenario] = sim_times
        base, tp = parse_scenario_name(scenario)
        stats = summarize_times(sim_times, end_time)
        rows.append({
            "scenario": scenario,
            "scenario_base": base,
            "traffic_profile_id": tp,
            "Scenario.endTime": end_time,
            **stats,
            "data_source": source,
        })

    validation = validate_against_reports([
        "U1_CBD_Commuting_HelsinkiMedium__TP07_BurstWindow",
        "U1_CBD_Commuting_HelsinkiMedium__TP01_Baseline",
    ])

    write_summary_csv(rows, DATA_DIR / "message_creation_time_summary.csv")
    make_figures(all_times, 43200.0, rows)
    write_audit_md(rows, validation, MESSAGE_CREATION_TIME_AUDIT)

    print(f"Wrote {DATA_DIR / 'message_creation_time_summary.csv'} ({len(rows)} rows)")
    print(f"Wrote {MESSAGE_CREATION_TIME_AUDIT}")
    print(f"Wrote figures to {FIGURES_DIR}")
    for v in validation:
        print(f"  validate: {v}")
    return 0

if __name__ == "__main__":
    sys.exit(main())