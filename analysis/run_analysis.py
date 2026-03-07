#!/usr/bin/env python3
"""
Análisis del corpus de escenarios por partes.
Extrae features estables y reportables, correlaciones y reportes.
Salida en analysis/data/, analysis/figures/, analysis/reports/.

Uso:
  python run_analysis.py --corpus corpus_v1 --phase features
  python run_analysis.py --corpus corpus_v1 --phase all

Requiere: numpy, pandas (opcional: matplotlib, scipy para fases posteriores)
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from scipy import stats as scipy_stats
    from scipy.cluster.hierarchy import linkage, fcluster
except ImportError:
    scipy_stats = None
    linkage = fcluster = None

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


# ---------- Parser de settings (reutilizado del script de correlación) ----------

def _parse_size(value: str) -> float:
    """Parsea 50M, 2M, 250k, 1G (bytes o bytes/s)."""
    value = value.strip()
    mult = 1
    if value.endswith("k"):
        mult = 1000
        value = value[:-1]
    elif value.endswith("M"):
        mult = 1_000_000
        value = value[:-1]
    elif value.endswith("G"):
        mult = 1_000_000_000
        value = value[:-1]
    elif value.endswith("kiB"):
        mult = 1024
        value = value[:-3]
    elif value.endswith("MiB"):
        mult = 1024 ** 2
        value = value[:-3]
    elif value.endswith("GiB"):
        mult = 1024 ** 3
        value = value[:-3]
    try:
        return float(value) * mult
    except ValueError:
        return np.nan


def _parse_range(value: str) -> float:
    """Parsea 'a, b' -> media; valor único -> float. Acepta sufijos k, M."""
    parts = [p.strip() for p in value.split(",")]
    if len(parts) == 1:
        try:
            return float(parts[0])
        except ValueError:
            return _parse_size(parts[0])
    try:
        a = _parse_size(parts[0]) if any(c in parts[0].rstrip() for c in "kMG") else float(parts[0])
        b = _parse_size(parts[1]) if any(c in parts[1].rstrip() for c in "kMG") else float(parts[1])
        return (float(a) + float(b)) / 2.0
    except (ValueError, IndexError, TypeError):
        return np.nan


def load_settings(path: Path) -> dict[str, Any]:
    """Carga un .settings en un dict plano key -> value (strings)."""
    out: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.split("#")[0].strip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _get_float(d: dict[str, Any], key: str, default: float = np.nan) -> float:
    try:
        return float(d[key])
    except (KeyError, ValueError):
        return default


def _get_range_mean(d: dict[str, Any], key: str, default: float = np.nan) -> float:
    if key not in d:
        return default
    val = _parse_range(d[key])
    return val if isinstance(val, (int, float)) else val


def _get_size(d: dict[str, Any], key: str, default: float = np.nan) -> float:
    if key not in d:
        return default
    return _parse_size(d[key])


# ---------- Features estables y reportables (ver README.md) ----------

def settings_to_reportable_features(d: dict[str, Any]) -> dict[str, float | int]:
    """
    Construye el vector de features estables y reportables a partir del settings.
    Agrupación: Movilidad/espacio, Contacto esperado, Tráfico, Recursos + extras.
    """
    n_groups = int(d.get("Scenario.nrofHostGroups", 1))
    n_hosts = 0
    for i in range(1, n_groups + 1):
        n_hosts += int(d.get(f"Group{i}.nrofHosts", d.get("Group.nrofHosts", 0)))
    if n_hosts == 0:
        n_hosts = int(d.get("Group.nrofHosts", 0)) * max(1, n_groups)

    # ---- 1. Movilidad / espacio ----
    world = d.get("MovementModel.worldSize", "")
    if "," in world:
        parts = [float(x.strip()) for x in world.split(",")[:2]]
        Wx, Wy = parts[0], parts[1]
    else:
        Wx = Wy = np.nan
    area = Wx * Wy if not (np.isnan(Wx) or np.isnan(Wy)) else np.nan
    density = (n_hosts / area * 1e6) if area and area > 0 else np.nan  # proxy nodos/km²

    speed_mean = _get_range_mean(d, "Group.speed")
    for i in range(1, n_groups + 1):
        if f"Group{i}.speed" in d:
            speed_mean = _get_range_mean(d, f"Group{i}.speed")
            break
    wait_mean = _get_range_mean(d, "Group.waitTime")
    for i in range(1, n_groups + 1):
        if f"Group{i}.waitTime" in d:
            wait_mean = _get_range_mean(d, f"Group{i}.waitTime")
            break
    t_move_proxy = 60.0  # segmento típico de movimiento entre pausas (s)
    pause_ratio = wait_mean / (wait_mean + t_move_proxy) if not np.isnan(wait_mean) and wait_mean >= 0 else np.nan

    movement_models = set()
    for key in ("Group.movementModel",) + tuple(f"Group{i}.movementModel" for i in range(1, n_groups + 1)):
        if key in d:
            movement_models.add(d[key].strip())
    mm_WDM = 1 if "WorkingDayMovement" in movement_models else 0
    mm_RWP = 1 if "RandomWaypoint" in movement_models else 0
    mm_MapRoute = 1 if "MapRouteMovement" in movement_models else 0
    mm_Cluster = 1 if "ClusterMovement" in movement_models else 0
    mm_Bus = 1 if "BusMovement" in movement_models else 0
    mm_ShortestPath = 1 if "ShortestPathMapBasedMovement" in movement_models else 0
    mm_External = 1 if ("ExternalMovement" in movement_models or "ExternalPathMovement" in movement_models) else 0

    # ---- 2. Contacto esperado ----
    iface_id = d.get("Group.interface1", d.get("Group1.interface1", ""))
    transmit_range = _get_float(d, f"{iface_id}.transmitRange") if iface_id else np.nan
    if np.isnan(transmit_range) and "bt0.transmitRange" in d:
        transmit_range = _get_float(d, "bt0.transmitRange")
    contact_rate_proxy = np.nan
    if not (np.isnan(density) or np.isnan(transmit_range) or np.isnan(speed_mean)):
        contact_rate_proxy = density * (transmit_range ** 2) * speed_mean * 1e-6

    # ---- 3. Tráfico ----
    event_interval_mean = _get_range_mean(d, "Events1.interval")
    event_size_mean = _get_range_mean(d, "Events1.size")
    msg_ttl = _get_float(d, "Group.msgTtl")
    if np.isnan(msg_ttl):
        msg_ttl = _get_float(d, "Group1.msgTtl")
    if np.isnan(msg_ttl) or msg_ttl <= 0:
        msg_ttl = 10000.0  # "infinito" para el vector

    nrof_events = int(d.get("Events.nrof", 1))
    has_time_window = any(d.get(f"Events{i}.time") for i in range(1, nrof_events + 1) if f"Events{i}.time" in d)
    has_tohosts = any(d.get(f"Events{i}.tohosts") for i in range(1, nrof_events + 1) if f"Events{i}.tohosts" in d)
    # Patrón: si tiene ventana de tiempo -> burst; si tiene tohosts -> hub_target; si no -> uniform
    pattern_burst = 1 if has_time_window else 0
    pattern_hub_target = 1 if has_tohosts else 0
    pattern_uniform = 1 if not has_time_window and not has_tohosts else 0

    # ---- 4. Recursos ----
    buffer_size = _get_size(d, "Group.bufferSize")
    if np.isnan(buffer_size):
        buffer_size = _get_size(d, "Group1.bufferSize")
    transmit_speed = _get_size(d, f"{iface_id}.transmitSpeed") if iface_id else np.nan
    if np.isnan(transmit_speed) and "bt0.transmitSpeed" in d:
        transmit_speed = _get_size(d, "bt0.transmitSpeed")

    # ---- 5. WDM / actividad (WorkingDayMovement; np.nan si no aplica) ----
    work_day_length = _get_float(d, "Group.workDayLength")
    for i in range(1, n_groups + 1):
        if f"Group{i}.workDayLength" in d:
            work_day_length = _get_float(d, f"Group{i}.workDayLength")
            break
    time_diff_std = _get_float(d, "Group.timeDiffSTD")
    for i in range(1, n_groups + 1):
        if f"Group{i}.timeDiffSTD" in d:
            time_diff_std = _get_float(d, f"Group{i}.timeDiffSTD")
            break
    prob_go_shopping = _get_float(d, "Group.probGoShoppingAfterWork")
    for i in range(1, n_groups + 1):
        if f"Group{i}.probGoShoppingAfterWork" in d:
            prob_go_shopping = _get_float(d, f"Group{i}.probGoShoppingAfterWork")
            break
    nr_meeting_spots = _get_float(d, "Group.nrOfMeetingSpots")
    for i in range(1, n_groups + 1):
        if f"Group{i}.nrOfMeetingSpots" in d:
            nr_meeting_spots = _get_float(d, f"Group{i}.nrOfMeetingSpots")
            break
    nr_offices = _get_float(d, "Group.nrOfOffices")
    for i in range(1, n_groups + 1):
        if f"Group{i}.nrOfOffices" in d:
            nr_offices = _get_float(d, f"Group{i}.nrOfOffices")
            break
    # Si el escenario no usa WDM, estas claves no suelen existir -> quedan np.nan
    if mm_WDM == 0:
        work_day_length = time_diff_std = prob_go_shopping = nr_meeting_spots = nr_offices = np.nan

    # ---- Extras ----
    end_time = _get_float(d, "Scenario.endTime")
    has_active_times = 1 if any(f"Group{i}.activeTimes" in d for i in range(1, n_groups + 1)) or "Group.activeTimes" in d else 0

    return {
        # Movilidad/espacio
        "Wx": Wx,
        "Wy": Wy,
        "N": n_hosts,
        "density": density,
        "speed_mean": speed_mean,
        "pause_ratio": pause_ratio,
        "wait_mean": wait_mean,
        "mm_WDM": mm_WDM,
        "mm_RWP": mm_RWP,
        "mm_MapRoute": mm_MapRoute,
        "mm_Cluster": mm_Cluster,
        "mm_Bus": mm_Bus,
        "mm_ShortestPath": mm_ShortestPath,
        "mm_External": mm_External,
        # Contacto esperado
        "transmitRange": transmit_range,
        "contact_rate_proxy": contact_rate_proxy,
        # Tráfico
        "event_interval_mean": event_interval_mean,
        "event_size_mean": event_size_mean,
        "msgTtl": msg_ttl,
        "pattern_uniform": pattern_uniform,
        "pattern_burst": pattern_burst,
        "pattern_hub_target": pattern_hub_target,
        "nrof_event_generators": nrof_events,
        # Recursos
        "bufferSize": buffer_size,
        "transmitSpeed": transmit_speed,
        # WDM / actividad (np.nan si no usa WorkingDayMovement)
        "workDayLength": work_day_length,
        "timeDiffSTD": time_diff_std,
        "probGoShoppingAfterWork": prob_go_shopping,
        "nrOfMeetingSpots": nr_meeting_spots,
        "nrOfOffices": nr_offices,
        # Extras
        "Scenario.endTime": end_time,
        "nrofHostGroups": n_groups,
        "has_active_times": has_active_times,
    }


def collect_scenario_files(corpus_dir: Path, pattern: str = "**/*.settings") -> list[Path]:
    """Lista de .settings bajo corpus_dir (recursivo)."""
    if not corpus_dir.is_absolute():
        corpus_dir = Path.cwd() / corpus_dir
    return sorted(corpus_dir.glob(pattern))


def run_phase_features(scenario_paths: list[Path], out_dir: Path) -> None:
    """Fase 1: extraer features y guardar data/features.csv y data/scenario_list.txt."""
    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    labels = []
    for p in scenario_paths:
        d = load_settings(p)
        vec = settings_to_reportable_features(d)
        rows.append(vec)
        labels.append(d.get("Scenario.name", p.stem))
    if not rows:
        print("No scenarios to process.")
        return

    if pd is not None:
        df = pd.DataFrame(rows, index=labels)
        df.to_csv(data_dir / "features.csv")
        print(f"Written {data_dir / 'features.csv'} ({len(df)} scenarios, {len(df.columns)} features)")
    else:
        # Sin pandas: escribir CSV a mano
        cols = list(rows[0].keys())
        with open(data_dir / "features.csv", "w", encoding="utf-8") as f:
            f.write("scenario," + ",".join(cols) + "\n")
            for lb, row in zip(labels, rows):
                f.write(lb + "," + ",".join(str(row.get(c, "")) for c in cols) + "\n")
        print(f"Written {data_dir / 'features.csv'} ({len(labels)} scenarios)")

    with open(data_dir / "scenario_list.txt", "w", encoding="utf-8") as f:
        for p in scenario_paths:
            f.write(f"{p}\n")
    print(f"Written {data_dir / 'scenario_list.txt'}")


def zscore_normalize_per_feature(df: "pd.DataFrame") -> tuple["pd.DataFrame", "pd.DataFrame"]:
    """
    Normalización z-score por característica (por columna):
      X_s,j_norm = (X_s,j - μ_j) / σ_j
    μ_j, σ_j = media y desv. típica de la característica j sobre todos los escenarios s.
    Si σ_j = 0 (columna constante), se asigna 0.
    Devuelve (DataFrame normalizado, DataFrame de parámetros: feature, mean, std).
    """
    if pd is None:
        raise RuntimeError("pandas required for normalization")
    params = []
    Z = df.copy()
    for col in Z.columns:
        mu = Z[col].mean(skipna=True)
        sigma = Z[col].std(skipna=True)
        if pd.isna(sigma) or sigma == 0:
            Z[col] = 0.0
            sigma = 0.0 if not pd.isna(sigma) else np.nan
        else:
            Z[col] = (Z[col] - mu) / sigma
        params.append({"feature": col, "mean": mu, "std": sigma})
    params_df = pd.DataFrame(params)
    return Z, params_df


def run_phase_normalize(out_dir: Path) -> bool:
    """
    Fase 2: lee data/features.csv, aplica z-score por característica,
    escribe data/features_normalized.csv y data/normalization_params.csv.
    Devuelve True si se ejecutó correctamente (existía features.csv).
    """
    if pd is None:
        print("pandas is required for --phase normalize")
        return False
    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    features_path = data_dir / "features.csv"
    if not features_path.exists():
        print(f"Not found: {features_path}. Run --phase features first.")
        return False
    data_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(features_path, index_col=0)
    Z, params_df = zscore_normalize_per_feature(df)
    Z.to_csv(data_dir / "features_normalized.csv")
    params_df.to_csv(data_dir / "normalization_params.csv", index=False)
    print(f"Written {data_dir / 'features_normalized.csv'} (shape {Z.shape})")
    print(f"Written {data_dir / 'normalization_params.csv'} ({len(params_df)} features)")
    return True


def pearson_pvalue_from_r(r: float, n: int) -> float:
    """P-value (two-tailed) para H0: rho=0, dado r de Pearson con n observaciones. n = número de puntos (p. ej. d features)."""
    if np.isnan(r) or n < 3:
        return np.nan
    r2 = r * r
    if r2 >= 1.0:
        return 0.0
    t_stat = r * np.sqrt((n - 2) / (1.0 - r2))
    if scipy_stats is not None:
        return float(2 * (1 - scipy_stats.t.cdf(np.abs(t_stat), n - 2)))
    return np.nan


def spearman_matrix_rows(Z: np.ndarray) -> np.ndarray:
    """Correlación de Spearman entre filas de Z (n×d). Devuelve (n×n)."""
    if pd is not None:
        df = pd.DataFrame(Z)
        return df.T.corr(method="spearman").values
    if scipy_stats is None:
        return np.corrcoef(Z)
    n = Z.shape[0]
    R = np.eye(n)
    for i in range(n):
        for k in range(i + 1, n):
            r, _ = scipy_stats.spearmanr(Z[i], Z[k], nan_policy="omit")
            R[i, k] = r if not np.isnan(r) else 0.0
            R[k, i] = R[i, k]
    return R


def cosine_distance_matrix(Z: np.ndarray) -> np.ndarray:
    """Distancia coseno entre filas: 1 - cos_sim. (n×n). cos_sim = (Zi·Zk)/(|Zi||Zk|)."""
    norms = np.linalg.norm(Z, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    U = Z / norms
    sim = U @ U.T
    return 1.0 - sim


def euclidean_distance_matrix(Z: np.ndarray) -> np.ndarray:
    """Distancia euclídea entre filas. (n×n)."""
    a = Z[:, np.newaxis, :]
    b = Z[np.newaxis, :, :]
    return np.sqrt(np.nansum((a - b) ** 2, axis=2))


def silhouette_from_distance(D: np.ndarray, labels: np.ndarray) -> float:
    """
    Silhouette score a partir de matriz de distancias D (n×n) y etiquetas de cluster.
    s(i) = (b(i)-a(i)) / max(a(i),b(i)); a(i)=dist media intra-cluster, b(i)=dist media al cluster más cercano.
    Clusters de un solo elemento: s(i)=0.
    """
    n = D.shape[0]
    labels = np.asarray(labels, dtype=int)
    unique = np.unique(labels)
    s = np.zeros(n)
    for i in range(n):
        c = labels[i]
        same = labels == c
        other = ~same
        if np.sum(same) <= 1:
            s[i] = 0.0
            continue
        a_i = np.mean(D[i, same & (np.arange(n) != i)])
        if not np.any(other):
            s[i] = 0.0
            continue
        b_vals = []
        for k in unique:
            if k == c:
                continue
            mask = labels == k
            b_vals.append(np.mean(D[i, mask]))
        b_i = min(b_vals) if b_vals else 0.0
        denom = max(a_i, b_i)
        s[i] = (b_i - a_i) / denom if denom > 0 else 0.0
    return float(np.nanmean(s))


def benjamini_hochberg(pvalues_flat: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    """FDR Benjamini-Hochberg. pvalues_flat: 1d. Devuelve máscara booleana: True = rechazar H0."""
    p = np.asarray(pvalues_flat, dtype=float).ravel()
    p = np.nan_to_num(p, nan=1.0, posinf=1.0, neginf=1.0)
    m = len(p)
    order = np.argsort(p)
    p_sorted = p[order]
    k_max = -1
    for i in range(m):
        if p_sorted[i] <= (i + 1) / m * alpha:
            k_max = i
    rej = np.zeros(m, dtype=bool)
    if k_max >= 0:
        rej[order[: k_max + 1]] = True
    return rej


def run_phase_correlation(out_dir: Path, threshold: float = 0.7, criterion_95: bool = True, fdr_alpha: float = 0.05) -> bool:
    """
    Fase 3: matriz de correlación entre escenarios.
    Z (n×d): cada fila = vector de un escenario. r(Si, Sk) = corr(Zi, Zk).
    Criterio: |r| < threshold para todos los pares, o para al menos 95% de los pares.
    Escribe data/correlation_pearson.csv y reports/correlation_report.txt.
    """
    if pd is None:
        print("pandas is required for --phase correlation")
        return False
    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    reports_dir = out_dir / "reports"
    path_z = data_dir / "features_normalized.csv"
    if not path_z.exists():
        print(f"Not found: {path_z}. Run --phase normalize first.")
        return False
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    Z = pd.read_csv(path_z, index_col=0)
    n, d = Z.shape
    Z_arr = Z.values
    labels = Z.index.tolist()
    index_df = pd.Index(labels)

    # Pearson entre filas (escenarios): R[i,k] = corr(Zi, Zk)
    R = Z.T.corr()
    R.to_csv(data_dir / "correlation_pearson.csv")

    triu = np.triu_indices(n, k=1)
    r_flat = R.values[triu[0], triu[1]]

    # Spearman entre filas
    R_spearman = spearman_matrix_rows(Z_arr)
    R_sp_df = pd.DataFrame(R_spearman, index=index_df, columns=index_df)
    R_sp_df.to_csv(data_dir / "correlation_spearman.csv")
    r_sp_flat = R_spearman[triu[0], triu[1]]

    # Distancia coseno (1 - cos_sim) y euclídea
    cos_dist = cosine_distance_matrix(Z_arr)
    euc_dist = euclidean_distance_matrix(Z_arr)
    pd.DataFrame(cos_dist, index=index_df, columns=index_df).to_csv(data_dir / "distance_cosine.csv")
    pd.DataFrame(euc_dist, index=index_df, columns=index_df).to_csv(data_dir / "distance_euclidean.csv")
    cos_flat = cos_dist[triu[0], triu[1]]
    euc_flat = euc_dist[triu[0], triu[1]]
    min_cos_dist = float(np.nanmin(cos_flat)) if len(cos_flat) else np.nan
    n_pairs_cos_below_005 = int(np.sum(cos_flat < 0.05))

    # Clustering sobre Z (ward) para diagnóstico de estructura. Ward no admite NaN → rellenar con 0.
    n_clusters = 7
    cluster_labels = None
    silhouette_score = np.nan
    if linkage is not None and fcluster is not None:
        try:
            Z_ward = np.nan_to_num(Z_arr, nan=0.0, posinf=0.0, neginf=0.0)
            link = linkage(Z_ward, method="ward")
            cluster_labels = fcluster(link, n_clusters, criterion="maxclust")
            silhouette_score = silhouette_from_distance(cos_dist, cluster_labels)
        except Exception:
            pass

    abs_r = np.abs(r_flat)
    total_pairs = len(r_flat)
    n_above = int(np.sum(abs_r >= threshold))
    frac_above = n_above / total_pairs if total_pairs else 0.0
    max_abs_r = float(np.nanmax(abs_r)) if total_pairs else np.nan
    mean_abs_r = float(np.nanmean(abs_r)) if total_pairs else np.nan

    # Criterio: todos |r| < 0.7 O al menos 95% de pares con |r| < 0.7
    criterion_all = n_above == 0
    criterion_95_pct = frac_above <= 0.05
    criterion_met = criterion_all if not criterion_95 else (criterion_all or criterion_95_pct)

    # Lista de pares con |r| >= threshold
    above_mask = abs_r >= threshold
    pairs_above = []
    for idx in np.where(above_mask)[0]:
        i, k = triu[0][idx], triu[1][idx]
        pairs_above.append((labels[i], labels[k], float(R.iloc[i, k])))

    # ----- Test estadístico y corrección por comparaciones múltiples -----
    # Para cada par (i,k), p-value de H0: rho=0. n = d (correlación sobre d features).
    p_flat = np.array([pearson_pvalue_from_r(float(r_flat[j]), d) for j in range(total_pairs)])
    p_flat = np.nan_to_num(p_flat, nan=1.0, posinf=1.0, neginf=1.0)
    rej_fdr = benjamini_hochberg(p_flat, alpha=fdr_alpha)
    # Bonferroni: rechazar H0 si p < alpha/m
    rej_bonf = p_flat < (fdr_alpha / total_pairs)
    n_rej_fdr = int(np.sum(rej_fdr))
    n_rej_bonf = int(np.sum(rej_bonf))
    # Objetivo: no haya pares con |r| alto Y significativo tras corrección
    high_r = abs_r >= threshold
    n_high_r_and_sig_fdr = int(np.sum(high_r & rej_fdr))
    n_high_r_and_sig_bonf = int(np.sum(high_r & rej_bonf))
    # Guardar p-values (triángulo superior en mismo orden que r_flat)
    if pd is not None:
        p_df = pd.DataFrame(index=R.index, columns=R.columns, dtype=float)
        p_df.values[:] = np.nan
        for idx in range(total_pairs):
            i, k = triu[0][idx], triu[1][idx]
            p_df.iloc[i, k] = p_flat[idx]
            p_df.iloc[k, i] = p_flat[idx]
        p_df.to_csv(data_dir / "correlation_pearson_pvalues.csv")

    report_lines = [
        f"=== Correlación entre escenarios (vectores Z, {n}×d) ===",
        f"r(Si, Sk) = corr(Zi, Zk).  Escenarios: n={n}, features: d={d}.",
        "",
        "Matriz de Pearson:",
        f"  max |r| = {max_abs_r:.4f}",
        f"  media |r| = {mean_abs_r:.4f}",
        f"  Total pares (i<k): {total_pairs}",
        f"  Pares con |r| >= {threshold}: {n_above} ({100*frac_above:.1f}%)",
        "",
        "Criterio: |r| < 0.7 para todos los pares O para ≥95% de los pares.",
        f"  ¿Todos |r| < {threshold}? {criterion_all}",
        f"  ¿Al menos 95% con |r| < {threshold}? {frac_above <= 0.05} ({100*(1-frac_above):.1f}% cumplen)",
        f"  Criterio cumplido: {criterion_met}",
        "",
        "Spearman (correlación de rangos entre vectores Z):",
        f"  max |r| = {float(np.nanmax(np.abs(r_sp_flat))):.4f}",
        f"  media |r| = {float(np.nanmean(np.abs(r_sp_flat))):.4f}",
        f"  Pares con |r| >= {threshold}: {int(np.sum(np.abs(r_sp_flat) >= threshold))}",
        "",
        "Métricas geométricas (sobre Z normalizado):",
        "  Distancia coseno (1 - cos_sim; 0=idénticos, 2=opuestos):",
        f"    mín = {float(np.nanmin(cos_flat)):.4f}, media = {float(np.nanmean(cos_flat)):.4f}",
        "  Distancia euclídea:",
        f"    mín = {float(np.nanmin(euc_flat)):.4f}, media = {float(np.nanmean(euc_flat)):.4f}",
        "",
        "Criterios de diversidad geométrica (objetivo: espacio bien distribuido):",
        f"  dist_coseno mínima = {min_cos_dist:.4f}  (objetivo: > 0.05; si < 0.05 hay pares casi idénticos)",
        f"  Pares con cos_dist < 0.05: {n_pairs_cos_below_005}",
        (f"  Silhouette (k={n_clusters} clusters, Ward): {silhouette_score:.4f}  (objetivo > 0.3)" if cluster_labels is not None else "  Silhouette: no calculado (clustering no disponible o falló)"),
        "  Objetivos realistas: max |r| < 0.85, pares |r|>=0.7 < 3%, cos_dist mín > 0.05, silhouette > 0.3",
        "",
    ]
    if pairs_above:
        report_lines.append(f"Pares con |r| >= {threshold} (máximo 20 mostrados):")
        for (a, b, r) in sorted(pairs_above, key=lambda x: -abs(x[2]))[:20]:
            report_lines.append(f"  {a} <-> {b}  r = {r:.4f}")
        if len(pairs_above) > 20:
            report_lines.append(f"  ... y {len(pairs_above) - 20} más.")
    else:
        report_lines.append(f"Ningún par con |r| >= {threshold}.")

    report_lines.extend([
        "",
        "--- Test estadístico y corrección por comparaciones múltiples ---",
        f"Pares: m = {total_pairs} = C({n},2). Para cada par, p-value de H0: rho=0 (Pearson, n=d={d}).",
        "",
        f"FDR (Benjamini-Hochberg, alpha={fdr_alpha}):",
        f"  Rechazos (pares significativos): {n_rej_fdr}",
        f"  Pares con |r| >= {threshold} Y significativos (FDR): {n_high_r_and_sig_fdr}",
        "",
        f"Bonferroni (alpha/{total_pairs} = {fdr_alpha/total_pairs:.6f}):",
        f"  Rechazos: {n_rej_bonf}",
        f"  Pares con |r| >= {threshold} Y significativos (Bonferroni): {n_high_r_and_sig_bonf}",
        "",
        "Objetivo: demostrar que no hay pares con |r| alto y significativo tras corrección.",
        f"  Tras FDR: {'Sí (0 pares alto |r| significativos)' if n_high_r_and_sig_fdr == 0 else f'No ({n_high_r_and_sig_fdr} pares con |r|>={threshold} significativos)'}.",
        f"  Tras Bonferroni: {'Sí (0 pares alto |r| significativos)' if n_high_r_and_sig_bonf == 0 else f'No ({n_high_r_and_sig_bonf} pares con |r|>={threshold} significativos)'}.",
        "",
        "Diagnóstico: 0 rechazos no implica ausencia de correlación; con n=d=33 la potencia es baja.",
        "El problema real es geométrico: escenarios casi colineales (mismo subespacio).",
        "Estrategia: diversificar estructura (mapa, régimen dinámico, recursos extremos), no solo parámetros.",
    ])
    report_text = "\n".join(report_lines)
    (reports_dir / "correlation_report.txt").write_text(report_text, encoding="utf-8")

    # Escenarios que aparecen en algún par con |r| >= threshold (para diversificar)
    scenarios_above = set()
    for (a, b, _) in pairs_above:
        scenarios_above.add(a)
        scenarios_above.add(b)
    # Número de pares "malos" por escenario (prioridad: los que más aparecen)
    count_above = {s: 0 for s in labels}
    for (a, b, _) in pairs_above:
        count_above[a] += 1
        count_above[b] += 1
    scenarios_sorted = sorted(scenarios_above, key=lambda s: -count_above[s])
    diversify_lines = [
        f"# Escenarios a diversificar (aparecen en pares con |r| >= {threshold})",
        f"# Generado por run_analysis.py --phase correlation. Total: {len(scenarios_sorted)} escenarios.",
        f"# Criterio: trabajar en estos para que su vector de features difiera del resto y baje |r|.",
        "",
    ]
    for s in scenarios_sorted:
        diversify_lines.append(f"{s}  (# pares con |r|>={threshold}: {count_above[s]})")
    (reports_dir / "scenarios_to_diversify.txt").write_text("\n".join(diversify_lines), encoding="utf-8")
    print(f"Written {reports_dir / 'scenarios_to_diversify.txt'} ({len(scenarios_sorted)} escenarios a diversificar)")

    # Asignación a clusters y reporte por cluster (para diversificar: 3-4 representantes por cluster, empujar el resto)
    if cluster_labels is not None and pd is not None:
        cl_df = pd.DataFrame({"scenario": labels, "cluster": cluster_labels})
        cl_df.to_csv(data_dir / "cluster_assignments.csv", index=False)
        by_cluster = defaultdict(list)
        for scen, c in zip(labels, cluster_labels):
            by_cluster[int(c)].append(scen)
        cluster_report = [
            f"# Clustering Ward sobre Z (k={n_clusters}), silhouette = {silhouette_score:.4f}",
            "# De cada cluster: mantener 3-4 representantes; modificar el resto para empujarlos fuera.",
            "",
        ]
        for c in sorted(by_cluster.keys()):
            cluster_report.append(f"## Cluster {c} ({len(by_cluster[c])} escenarios)")
            for s in sorted(by_cluster[c]):
                cluster_report.append(f"  {s}")
            cluster_report.append("")
        (reports_dir / "clustering_report.txt").write_text("\n".join(cluster_report), encoding="utf-8")
        print(f"Written {data_dir / 'cluster_assignments.csv'}, {reports_dir / 'clustering_report.txt'}")

    if pd is not None:
        (reports_dir / "multiple_comparisons_report.txt").write_text(
            "\n".join([
                "=== Corrección por comparaciones múltiples (correlación entre escenarios) ===",
                f"m = {total_pairs} pares. alpha = {fdr_alpha}.",
                "",
                "FDR (Benjamini-Hochberg):",
                f"  Número de rechazos H0 (correlación significativa): {n_rej_fdr}",
                f"  Pares con |r| >= {threshold} y significativos (FDR): {n_high_r_and_sig_fdr}",
                "",
                "Bonferroni:",
                f"  Número de rechazos: {n_rej_bonf}",
                f"  Pares con |r| >= {threshold} y significativos (Bonferroni): {n_high_r_and_sig_bonf}",
                "",
                "Conclusión:",
                "  Objetivo = no pares con |r| alto y significativo tras corrección.",
                f"  FDR: {'Cumplido (0 pares alto |r| significativos)' if n_high_r_and_sig_fdr == 0 else f'No cumplido: {n_high_r_and_sig_fdr} pares.'}",
                f"  Bonferroni: {'Cumplido (0 pares alto |r| significativos)' if n_high_r_and_sig_bonf == 0 else f'No cumplido: {n_high_r_and_sig_bonf} pares.'}",
            ]), encoding="utf-8")
    print(report_text)
    print(f"Written {data_dir / 'correlation_pearson.csv'}, correlation_spearman.csv, distance_cosine.csv, distance_euclidean.csv")
    if pd is not None:
        print(f"Written {data_dir / 'correlation_pearson_pvalues.csv'}")
    print(f"Written {reports_dir / 'correlation_report.txt'}")
    if pd is not None:
        print(f"Written {reports_dir / 'multiple_comparisons_report.txt'}")
    return True


def run_phase_figures(out_dir: Path, threshold: float = 0.7) -> bool:
    """
    Fase 4: gráficos a partir de data/ (correlaciones, Z).
    Requiere que existan features_normalized.csv y correlation_pearson.csv (ejecutar --phase correlation antes).
    """
    if plt is None:
        print("matplotlib is required for --phase figures")
        return False
    if pd is None:
        print("pandas is required for --phase figures")
        return False
    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    figures_dir = out_dir / "figures"
    path_z = data_dir / "features_normalized.csv"
    path_r = data_dir / "correlation_pearson.csv"
    path_rs = data_dir / "correlation_spearman.csv"
    if not path_z.exists() or not path_r.exists():
        print(f"Not found: {path_z} or {path_r}. Run --phase correlation first.")
        return False
    figures_dir.mkdir(parents=True, exist_ok=True)

    Z_df = pd.read_csv(path_z, index_col=0)
    Z = Z_df.values
    labels = Z_df.index.tolist()
    n, d = Z.shape
    R_pearson = pd.read_csv(path_r, index_col=0).values
    R_spearman = pd.read_csv(path_rs, index_col=0).values if path_rs.exists() else None

    triu = np.triu_indices(n, k=1)
    r_flat = R_pearson[triu[0], triu[1]]

    # ---------- Heatmap Pearson ----------
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    im = ax.imshow(R_pearson, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=6)
    ax.set_yticklabels(labels, fontsize=6)
    plt.colorbar(im, ax=ax, label="Pearson r")
    ax.set_title("Correlación entre escenarios (Pearson, vectores Z)")
    plt.tight_layout()
    plt.savefig(figures_dir / "heatmap_pearson.png", dpi=150, bbox_inches="tight")
    plt.savefig(figures_dir / "heatmap_pearson.pdf", dpi=150, bbox_inches="tight")
    plt.close()

    # ---------- Heatmap Spearman ----------
    if R_spearman is not None:
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        im = ax.imshow(R_spearman, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=6)
        ax.set_yticklabels(labels, fontsize=6)
        plt.colorbar(im, ax=ax, label="Spearman r")
        ax.set_title("Correlación entre escenarios (Spearman, vectores Z)")
        plt.tight_layout()
        plt.savefig(figures_dir / "heatmap_spearman.png", dpi=150, bbox_inches="tight")
        plt.savefig(figures_dir / "heatmap_spearman.pdf", dpi=150, bbox_inches="tight")
        plt.close()

    # ---------- Histograma Pearson r ----------
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    nbins = min(50, max(15, len(r_flat) // 30))
    ax.hist(r_flat, bins=nbins, color="steelblue", edgecolor="black", alpha=0.7)
    ax.axvline(threshold, color="red", linestyle="--", label=f"|r| = {threshold}")
    ax.axvline(-threshold, color="red", linestyle="--")
    ax.set_xlabel("Pearson r (pares de escenarios)")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Distribución de correlaciones Pearson entre escenarios")
    ax.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "histogram_correlations_pearson.png", dpi=150, bbox_inches="tight")
    plt.savefig(figures_dir / "histogram_correlations_pearson.pdf", dpi=150, bbox_inches="tight")
    plt.close()

    # ---------- Histograma Spearman r ----------
    if R_spearman is not None:
        r_sp_flat = R_spearman[triu[0], triu[1]]
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        ax.hist(r_sp_flat, bins=nbins, color="seagreen", edgecolor="black", alpha=0.7)
        ax.axvline(threshold, color="red", linestyle="--", label=f"|r| = {threshold}")
        ax.axvline(-threshold, color="red", linestyle="--")
        ax.set_xlabel("Spearman r (pares de escenarios)")
        ax.set_ylabel("Frecuencia")
        ax.set_title("Distribución de correlaciones Spearman entre escenarios")
        ax.legend()
        plt.tight_layout()
        plt.savefig(figures_dir / "histogram_correlations_spearman.png", dpi=150, bbox_inches="tight")
        plt.savefig(figures_dir / "histogram_correlations_spearman.pdf", dpi=150, bbox_inches="tight")
        plt.close()

    # ---------- Scatter PCA 2D + regresión ----------
    Z_centered = Z - np.nanmean(Z, axis=0)
    try:
        U, S, Vt = np.linalg.svd(Z_centered, full_matrices=False)
        pc1 = U[:, 0] * S[0]
        pc2 = U[:, 1] * S[1]
        if np.var(pc1) > 1e-10:
            r_pc = np.corrcoef(pc1, pc2)[0, 1]
            a = np.cov(pc1, pc2)[0, 1] / np.var(pc1)
            b = np.mean(pc2) - a * np.mean(pc1)
            x_line = np.linspace(pc1.min(), pc1.max(), 100)
            y_line = a * x_line + b
            r2_pc = r_pc ** 2
        else:
            x_line = y_line = np.nan
            r2_pc = np.nan
    except Exception:
        pc1 = pc2 = np.arange(n, dtype=float)
        x_line = y_line = np.nan
        r2_pc = np.nan

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax.scatter(pc1, pc2, s=60, alpha=0.8, edgecolors="black", linewidths=0.5)
    if not (np.any(np.isnan(x_line)) or np.any(np.isnan(y_line))):
        ax.plot(x_line, y_line, "r-", linewidth=2, label=f"Regresión (R² = {r2_pc:.3f})")
    for i, lb in enumerate(labels):
        ax.annotate(lb, (pc1[i], pc2[i]), fontsize=5, xytext=(3, 3), textcoords="offset points", alpha=0.85)
    ax.set_xlabel("PC1 (primera componente principal)")
    ax.set_ylabel("PC2 (segunda componente principal)")
    ax.set_title("Escenarios en espacio PCA 2D + regresión\n(R² bajo ⇒ escenarios no alineados en una recta)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax.axvline(0, color="gray", linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(figures_dir / "scatter_pca_regression.png", dpi=150, bbox_inches="tight")
    plt.savefig(figures_dir / "scatter_pca_regression.pdf", dpi=150, bbox_inches="tight")
    plt.close()

    # ---------- Scatter par con mayor |r| (por feature) + regresión ----------
    imax = np.argmax(np.abs(r_flat))
    i, k = triu[0][imax], triu[1][imax]
    r_val = R_pearson[i, k]
    x_pair = Z[i, :]
    y_pair = Z[k, :]
    if np.var(x_pair) > 1e-12:
        a_pair = np.cov(x_pair, y_pair)[0, 1] / np.var(x_pair)
        b_pair = np.mean(y_pair) - a_pair * np.mean(x_pair)
        x_ln = np.linspace(x_pair.min(), x_pair.max(), 100)
        y_ln = a_pair * x_ln + b_pair
    else:
        x_ln = y_ln = np.array([])

    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    ax.scatter(x_pair, y_pair, s=40, alpha=0.7, edgecolors="black", linewidths=0.3)
    if len(x_ln) > 0:
        ax.plot(x_ln, y_ln, "r-", linewidth=2, label=f"Regresión (r = {r_val:.3f})")
    ax.set_xlabel(f"Escenario: {labels[i]}")
    ax.set_ylabel(f"Escenario: {labels[k]}")
    ax.set_title("Par con mayor |r|: scatter por feature + regresión\n(Puntos sobre la recta ⇒ correlación lineal fuerte)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax.axvline(0, color="gray", linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(figures_dir / "scatter_max_r_pair_regression.png", dpi=150, bbox_inches="tight")
    plt.savefig(figures_dir / "scatter_max_r_pair_regression.pdf", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Written {len(list(figures_dir.glob('*.png')))} figures to {figures_dir}")
    return True


# Columnas esperadas en output_metrics.csv (nombres alternativos aceptados)
OUTPUT_METRIC_COLUMNS = [
    ("delivery_ratio", ["delivery_ratio", "delivery_prob", "delivery prob"]),
    ("latency_mean", ["latency_mean", "latency_avg", "latency_avg", "latency average"]),
    ("overhead_ratio", ["overhead_ratio", "overhead_ratio", "overhead ratio"]),
    ("drop_ratio", ["drop_ratio", "drop_ratio", "dropped", "drop ratio"]),
]


def _parse_message_stats_report(path: Path) -> dict[str, Any]:
    """
    Parsea un fichero MessageStatsReport.txt (formato key: value).
    Devuelve dict con delivery_ratio, latency_mean, overhead_ratio, drop_ratio
    (delivery_prob -> delivery_ratio, latency_avg -> latency_mean; drop_ratio = dropped/created).
    """
    import re
    raw: dict[str, Any] = {}
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, v = [x.strip() for x in line.split(":", 1)]
        if v.lower() == "nan":
            raw[k] = np.nan
            continue
        try:
            if re.fullmatch(r"-?\d+", v):
                raw[k] = int(v)
            else:
                raw[k] = float(v)
        except (ValueError, TypeError):
            raw[k] = v

    created = raw.get("created")
    dropped = raw.get("dropped")
    if created is not None and isinstance(created, (int, float)) and created > 0 and dropped is not None:
        try:
            drop_ratio = float(dropped) / float(created)
        except (TypeError, ZeroDivisionError):
            drop_ratio = np.nan
    else:
        drop_ratio = np.nan

    return {
        "delivery_ratio": raw.get("delivery_prob", np.nan),
        "latency_mean": raw.get("latency_avg", np.nan),
        "overhead_ratio": raw.get("overhead_ratio", np.nan),
        "drop_ratio": drop_ratio,
    }


def run_phase_output_metrics(out_dir: Path, reports_dir: Path) -> bool:
    """
    Rellena data/output_metrics.csv a partir de los MessageStatsReport en reports_dir.
    Busca *_MessageStatsReport.txt, extrae escenario del nombre del fichero y parsea
    delivery_prob -> delivery_ratio, latency_avg -> latency_mean, overhead_ratio, drop_ratio = dropped/created.
    """
    out_dir = Path(out_dir)
    reports_dir = Path(reports_dir)
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    if not reports_dir.exists():
        print(f"Reports directory not found: {reports_dir}")
        return False
    report_files = sorted(reports_dir.glob("*_MessageStatsReport.txt"))
    if not report_files:
        print(f"No *_MessageStatsReport.txt found in {reports_dir}")
        return False
    rows = []
    for path in report_files:
        scenario = path.stem.replace("_MessageStatsReport", "")
        metrics = _parse_message_stats_report(path)
        rows.append({"scenario": scenario, **metrics})
    if pd is None:
        import csv
        out_csv = data_dir / "output_metrics.csv"
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["scenario", "delivery_ratio", "latency_mean", "overhead_ratio", "drop_ratio"])
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"Written {out_csv} ({len(rows)} scenarios from {reports_dir})")
        return True
    df = pd.DataFrame(rows)
    out_csv = data_dir / "output_metrics.csv"
    df.to_csv(out_csv, index=False)
    print(f"Written {out_csv} ({len(rows)} scenarios from {reports_dir})")
    return True


def run_phase_outputs(out_dir: Path, threshold: float = 0.7) -> bool:
    """
    Validación sobre outputs: vectores Y_s por escenario (delivery ratio, latency media,
    overhead ratio, drop ratio) y correlaciones entre escenarios.
    Mismo procedimiento que con parámetros: normalización z-score, Pearson, Spearman,
    distancias; objetivo: demostrar que los resultados no siguen una relación lineal trivial.
    Lee data/output_metrics.csv (primera columna = nombre escenario, resto = métricas).
    """
    if pd is None:
        print("pandas is required for --phase outputs")
        return False
    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    reports_dir = out_dir / "reports"
    path_csv = data_dir / "output_metrics.csv"
    if not path_csv.exists():
        print(f"Not found: {path_csv}. Create it with one row per scenario and columns:")
        print("  scenario, delivery_ratio, latency_mean, overhead_ratio, drop_ratio")
        print("  (from MessageStatsReport: delivery_prob, latency_avg, overhead_ratio; drop_ratio = dropped/created)")
        return False
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(path_csv)
    if df.shape[1] < 2:
        print("output_metrics.csv must have at least 2 columns (scenario + one metric)")
        return False
    # Primera columna = escenario
    scenario_col = df.columns[0]
    Y_df = df.set_index(scenario_col)
    # Solo columnas numéricas
    Y_df = Y_df.select_dtypes(include=[np.number])
    if Y_df.shape[1] == 0:
        print("No numeric columns found in output_metrics.csv")
        return False
    labels = Y_df.index.astype(str).tolist()
    n, p = Y_df.shape
    # Imputar NaN con mediana y normalizar z-score por columna
    Y_imputed = Y_df.fillna(Y_df.median())
    Y_arr = Y_imputed.values
    Y_norm = np.zeros_like(Y_arr, dtype=float)
    for j in range(p):
        mu, sig = np.nanmean(Y_arr[:, j]), np.nanstd(Y_arr[:, j])
        if sig and sig > 0:
            Y_norm[:, j] = (Y_arr[:, j] - mu) / sig
        else:
            Y_norm[:, j] = 0.0
    pd.DataFrame(Y_norm, index=Y_df.index, columns=Y_df.columns).to_csv(data_dir / "output_metrics_normalized.csv")

    # Correlación entre filas (escenarios)
    R_pearson = pd.DataFrame(Y_norm.T).corr().values
    R_spearman = spearman_matrix_rows(Y_norm)
    cos_dist = cosine_distance_matrix(Y_norm)
    euc_dist = euclidean_distance_matrix(Y_norm)

    index_df = pd.Index(labels)
    pd.DataFrame(R_pearson, index=index_df, columns=index_df).to_csv(data_dir / "correlation_pearson_outputs.csv")
    pd.DataFrame(R_spearman, index=index_df, columns=index_df).to_csv(data_dir / "correlation_spearman_outputs.csv")
    pd.DataFrame(cos_dist, index=index_df, columns=index_df).to_csv(data_dir / "distance_cosine_outputs.csv")
    pd.DataFrame(euc_dist, index=index_df, columns=index_df).to_csv(data_dir / "distance_euclidean_outputs.csv")

    triu = np.triu_indices(n, k=1)
    r_flat = R_pearson[triu[0], triu[1]]
    r_sp_flat = R_spearman[triu[0], triu[1]]
    cos_flat = cos_dist[triu[0], triu[1]]
    euc_flat = euc_dist[triu[0], triu[1]]
    total_pairs = len(r_flat)

    max_abs_r = float(np.nanmax(np.abs(r_flat))) if total_pairs else np.nan
    mean_abs_r = float(np.nanmean(np.abs(r_flat))) if total_pairs else np.nan
    n_above = int(np.sum(np.abs(r_flat) >= threshold))
    frac_above = n_above / total_pairs if total_pairs else 0.0

    report_lines = [
        "=== Validación sobre outputs (vectores Y por escenario) ===",
        f"Métricas: {list(Y_df.columns)}. Escenarios: n={n}, métricas: p={p}.",
        "Mismo procedimiento que con parámetros: z-score por columna, correlación entre vectores de escenario.",
        "",
        "Pearson (entre vectores de salida):",
        f"  max |r| = {max_abs_r:.4f}",
        f"  media |r| = {mean_abs_r:.4f}",
        f"  Pares con |r| >= {threshold}: {n_above} ({100*frac_above:.1f}%)",
        "",
        "Spearman:",
        f"  max |r| = {float(np.nanmax(np.abs(r_sp_flat))):.4f}",
        f"  media |r| = {float(np.nanmean(np.abs(r_sp_flat))):.4f}",
        "",
        "Distancias (sobre Y normalizado):",
        f"  Coseno: mín = {float(np.nanmin(cos_flat)):.4f}, media = {float(np.nanmean(cos_flat)):.4f}",
        f"  Euclídea: mín = {float(np.nanmin(euc_flat)):.4f}, media = {float(np.nanmean(euc_flat)):.4f}",
        "",
        "Objetivo: demostrar que los resultados (delivery ratio, latency, overhead, drop) no siguen",
        "una relación lineal trivial entre escenarios. Criterio |r| < 0.7 igual que para parámetros.",
    ]
    report_text = "\n".join(report_lines)
    (reports_dir / "outputs_correlation_report.txt").write_text(report_text, encoding="utf-8")
    print(report_text)
    print(f"Written {data_dir / 'correlation_pearson_outputs.csv'}, correlation_spearman_outputs.csv, distance_*_outputs.csv")
    print(f"Written {data_dir / 'output_metrics_normalized.csv'}")
    print(f"Written {reports_dir / 'outputs_correlation_report.txt'}")

    if plt is not None:
        figures_dir = out_dir / "figures"
        figures_dir.mkdir(parents=True, exist_ok=True)
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        im = ax.imshow(R_pearson, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=6)
        ax.set_yticklabels(labels, fontsize=6)
        plt.colorbar(im, ax=ax, label="Pearson r")
        ax.set_title("Correlación entre escenarios (vectores de salida Y)\ndelivery_ratio, latency_mean, overhead_ratio, drop_ratio")
        plt.tight_layout()
        plt.savefig(figures_dir / "heatmap_pearson_outputs.png", dpi=150, bbox_inches="tight")
        plt.savefig(figures_dir / "heatmap_pearson_outputs.pdf", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Written {figures_dir / 'heatmap_pearson_outputs.png'}")

    return True


def main():
    ap = argparse.ArgumentParser(description="Análisis del corpus de escenarios (por partes).")
    ap.add_argument("--corpus", type=str, default="corpus_v1", help="Directorio del corpus (p. ej. corpus_v1)")
    ap.add_argument("--phase", type=str, default="features", choices=("features", "normalize", "correlation", "figures", "output_metrics", "outputs", "all"),
                    help="Fase: features, normalize, correlation, figures, output_metrics (rellenar CSV desde reports), outputs (validación Y), all")
    ap.add_argument("--threshold", type=float, default=0.7,
                    help="Umbral |r| para criterio de correlación (default 0.7)")
    ap.add_argument("--strict", action="store_true",
                    help="Exigir |r|<threshold en el 100%% de pares; si no, se acepta ≥95%%")
    ap.add_argument("--fdr-alpha", type=float, default=0.05,
                    help="Alpha para FDR y Bonferroni (default 0.05)")
    ap.add_argument("--out-dir", type=str, default=None,
                    help="Directorio base de salida (default: directorio analysis/ donde está este script)")
    ap.add_argument("--reports-dir", type=str, default=None,
                    help="Directorio con *_MessageStatsReport.txt para --phase output_metrics (default: repo/reports)")
    args = ap.parse_args()

    base = Path(__file__).resolve().parent
    corpus_dir = base.parent / args.corpus  # corpus bajo scenarios/
    if not corpus_dir.exists():
        corpus_dir = Path(args.corpus)
    out_dir = Path(args.out_dir) if args.out_dir else base

    scenario_paths = collect_scenario_files(corpus_dir) if args.phase in ("features", "all") else []
    if args.phase in ("features", "all") and not scenario_paths:
        print(f"No .settings found under {corpus_dir}")
        return 1
    if scenario_paths:
        print(f"Found {len(scenario_paths)} scenarios under {corpus_dir}")

    if args.phase == "features" or args.phase == "all":
        run_phase_features(scenario_paths, out_dir)
    if args.phase == "normalize" or args.phase == "all":
        if not run_phase_normalize(out_dir):
            return 1
    if args.phase == "correlation" or args.phase == "all":
        if not run_phase_correlation(out_dir, threshold=args.threshold, criterion_95=not args.strict, fdr_alpha=args.fdr_alpha):
            return 1
    if args.phase == "figures" or args.phase == "all":
        if not run_phase_figures(out_dir, threshold=args.threshold):
            return 1
    reports_dir = Path(args.reports_dir) if args.reports_dir else (base.parent.parent / "reports")
    if args.phase == "output_metrics" or args.phase == "all":
        if not run_phase_output_metrics(out_dir, reports_dir):
            return 1
    if args.phase == "outputs":
        if not run_phase_outputs(out_dir, threshold=args.threshold):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
