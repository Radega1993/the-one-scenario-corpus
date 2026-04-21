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
    # Core: world_area y aspect_ratio (definición única; ver features_core_vs_extended.md)
    area = Wx * Wy if not (np.isnan(Wx) or np.isnan(Wy)) else np.nan
    world_area = area  # Wx×Wy (m²)
    if not (np.isnan(Wx) or np.isnan(Wy)) and Wx > 0 and Wy > 0:
        aspect_ratio = min(Wx, Wy) / max(Wx, Wy)  # ∈ (0, 1]
    else:
        aspect_ratio = np.nan
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
    mm_Linear = 1 if "LinearMovement" in movement_models else 0

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
    # Segundo flujo de eventos (cuando Events.nrof >= 2 y no es filePath)
    event2_interval_mean = event2_size_mean = np.nan
    if nrof_events >= 2 and "Events2.filePath" not in d and "Events2.interval" in d and "Events2.size" in d:
        event2_interval_mean = _get_range_mean(d, "Events2.interval")
        event2_size_mean = _get_range_mean(d, "Events2.size")

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
    # WDM: office size, shops, car prob, wait/group sizes (relevantes para investigación)
    office_size = _get_float(d, "Group.officeSize")
    for i in range(1, n_groups + 1):
        if f"Group{i}.officeSize" in d:
            office_size = _get_float(d, f"Group{i}.officeSize")
            break
    nr_shops = _get_float(d, "Group.nrOfShops")
    for i in range(1, n_groups + 1):
        if f"Group{i}.nrOfShops" in d:
            nr_shops = _get_float(d, f"Group{i}.nrOfShops")
            break
    own_car_prob = _get_float(d, "Group.ownCarProb")
    for i in range(1, n_groups + 1):
        if f"Group{i}.ownCarProb" in d:
            own_car_prob = _get_float(d, f"Group{i}.ownCarProb")
            break
    shop_size = _get_float(d, "Group.shopSize")
    for i in range(1, n_groups + 1):
        if f"Group{i}.shopSize" in d:
            shop_size = _get_float(d, f"Group{i}.shopSize")
            break
    office_min_wait = _get_float(d, "Group.officeMinWaitTime")
    office_max_wait = _get_float(d, "Group.officeMaxWaitTime")
    for i in range(1, n_groups + 1):
        if f"Group{i}.officeMinWaitTime" in d:
            office_min_wait = _get_float(d, f"Group{i}.officeMinWaitTime")
            break
    for i in range(1, n_groups + 1):
        if f"Group{i}.officeMaxWaitTime" in d:
            office_max_wait = _get_float(d, f"Group{i}.officeMaxWaitTime")
            break
    office_wait_mean = (office_min_wait + office_max_wait) / 2.0 if not (np.isnan(office_min_wait) or np.isnan(office_max_wait)) else np.nan
    shop_min_wait = _get_float(d, "Group.shoppingMinWaitTime")
    shop_max_wait = _get_float(d, "Group.shoppingMaxWaitTime")
    for i in range(1, n_groups + 1):
        if f"Group{i}.shoppingMinWaitTime" in d:
            shop_min_wait = _get_float(d, f"Group{i}.shoppingMinWaitTime")
            break
    for i in range(1, n_groups + 1):
        if f"Group{i}.shoppingMaxWaitTime" in d:
            shop_max_wait = _get_float(d, f"Group{i}.shoppingMaxWaitTime")
            break
    shopping_wait_mean = (shop_min_wait + shop_max_wait) / 2.0 if not (np.isnan(shop_min_wait) or np.isnan(shop_max_wait)) else np.nan
    min_group_size = _get_float(d, "Group.minGroupSize")
    max_group_size = _get_float(d, "Group.maxGroupSize")
    for i in range(1, n_groups + 1):
        if f"Group{i}.minGroupSize" in d:
            min_group_size = _get_float(d, f"Group{i}.minGroupSize")
            break
    for i in range(1, n_groups + 1):
        if f"Group{i}.maxGroupSize" in d:
            max_group_size = _get_float(d, f"Group{i}.maxGroupSize")
            break
    evening_group_size_mean = (min_group_size + max_group_size) / 2.0 if not (np.isnan(min_group_size) or np.isnan(max_group_size)) else np.nan
    evening_min_wait = _get_float(d, "Group.minWaitTime")
    evening_max_wait = _get_float(d, "Group.maxWaitTime")
    for i in range(1, n_groups + 1):
        if f"Group{i}.minWaitTime" in d:
            evening_min_wait = _get_float(d, f"Group{i}.minWaitTime")
            break
    for i in range(1, n_groups + 1):
        if f"Group{i}.maxWaitTime" in d:
            evening_max_wait = _get_float(d, f"Group{i}.maxWaitTime")
            break
    evening_wait_mean = (evening_min_wait + evening_max_wait) / 2.0 if not (np.isnan(evening_min_wait) or np.isnan(evening_max_wait)) else np.nan
    # WDM: tiempo parada tras compras
    after_shopping_min = _get_float(d, "Group.minAfterShoppingStopTime")
    after_shopping_max = _get_float(d, "Group.maxAfterShoppingStopTime")
    for i in range(1, n_groups + 1):
        if f"Group{i}.minAfterShoppingStopTime" in d:
            after_shopping_min = _get_float(d, f"Group{i}.minAfterShoppingStopTime")
            break
    for i in range(1, n_groups + 1):
        if f"Group{i}.maxAfterShoppingStopTime" in d:
            after_shopping_max = _get_float(d, f"Group{i}.maxAfterShoppingStopTime")
            break
    after_shopping_stop_mean = (after_shopping_min + after_shopping_max) / 2.0 if not (np.isnan(after_shopping_min) or np.isnan(after_shopping_max)) else np.nan
    # ClusterMovement: radio medio de clusters (m)
    cluster_ranges = []
    for i in range(1, n_groups + 1):
        if d.get(f"Group{i}.movementModel") == "ClusterMovement" and f"Group{i}.clusterRange" in d:
            r = _get_float(d, f"Group{i}.clusterRange")
            if not np.isnan(r):
                cluster_ranges.append(r)
    cluster_range_mean = float(np.mean(cluster_ranges)) if cluster_ranges else np.nan
    # Si el escenario no usa WDM, estas claves no suelen existir -> quedan np.nan
    if mm_WDM == 0:
        work_day_length = time_diff_std = prob_go_shopping = nr_meeting_spots = nr_offices = np.nan
        office_size = nr_shops = own_car_prob = shop_size = np.nan
        office_wait_mean = shopping_wait_mean = evening_group_size_mean = evening_wait_mean = np.nan
        after_shopping_stop_mean = np.nan

    # ---- Extras ----
    end_time = _get_float(d, "Scenario.endTime")
    has_active_times = 1 if any(f"Group{i}.activeTimes" in d for i in range(1, n_groups + 1)) or "Group.activeTimes" in d else 0

    return {
        # Movilidad/espacio (core usa world_area, aspect_ratio; Wx,Wy no en core)
        "world_area": world_area,
        "aspect_ratio": aspect_ratio,
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
        "mm_Linear": mm_Linear,
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
        "officeSize": office_size,
        "nrOfShops": nr_shops,
        "ownCarProb": own_car_prob,
        "shopSize": shop_size,
        "officeWaitTime_mean": office_wait_mean,
        "shoppingWaitTime_mean": shopping_wait_mean,
        "eveningGroupSize_mean": evening_group_size_mean,
        "eveningWaitTime_mean": evening_wait_mean,
        "afterShoppingStopTime_mean": after_shopping_stop_mean,
        "clusterRange_mean": cluster_range_mean,
        "event2_interval_mean": event2_interval_mean,
        "event2_size_mean": event2_size_mean,
        # Extras
        "Scenario.endTime": end_time,
        "nrofHostGroups": n_groups,
        "has_active_times": has_active_times,
    }


# Conjuntos core (23) y reducido (17) para ablación y correlación feature–feature (features_core_vs_extended.md)
FEATURES_CORE_23 = [
    "world_area", "aspect_ratio", "N", "nrofHostGroups", "speed_mean", "wait_mean",
    "mm_WDM", "mm_RWP", "mm_MapRoute", "mm_Cluster", "mm_Bus", "mm_Linear",
    "transmitRange", "bufferSize", "transmitSpeed", "msgTtl",
    "event_interval_mean", "event_size_mean", "nrof_event_generators",
    "pattern_burst", "pattern_hub_target",
    "workDayLength", "ownCarProb",
]
# Subconjunto reducido 17 (alineado con el marco Diego Freire 2022, implementable
# con las features disponibles en este extractor basado en settings).
#
# Nota metodológica:
# - Diego combina directas + indirectas de trazas/contactos.
# - En este pipeline no se extraen métricas de centralidad/encuentros sobre trazas
#   (p. ej. betweenness, inter-contact explícito), por lo que usamos proxies
#   estructurales/operativos presentes en el vector de 46.
# - Referencia doctoral: freire2022thesis (scenarios/internal/12-references.bib).
FEATURES_REDUCED_17 = [
    # Espacio / población / organización
    "world_area", "aspect_ratio", "N", "nrofHostGroups", "density",
    # Movilidad y dinámica base
    "mm_WDM", "mm_RWP", "mm_MapRoute", "speed_mean", "wait_mean",
    # Proxies de interacción/contacto y temporalidad
    "contact_rate_proxy", "event_interval_mean", "nrof_event_generators",
    "pattern_burst", "pattern_hub_target",
    # Alcance físico + horizonte temporal
    "transmitRange", "Scenario.endTime",
]

# Metadatos para el informe de features: nombre -> (descripción, setting(s) origen)
FEATURE_METADATA = {
    "world_area": ("Área del mundo Wx×Wy (m²)", "MovementModel.worldSize"),
    "aspect_ratio": ("Relación de aspecto min(Wx,Wy)/max(Wx,Wy) ∈ (0,1]", "MovementModel.worldSize"),
    "N": ("Número de hosts", "Scenario.nrofHostGroups, Group*.nrofHosts"),
    "density": ("Densidad proxy (hosts/km²)", "N, world_area (derivado); excluida del core por redundancia"),
    "speed_mean": ("Velocidad media (m/s)", "Group*.speed"),
    "pause_ratio": ("Ratio pausa/(movimiento+pausa)", "Group*.waitTime (derivado)"),
    "wait_mean": ("Tiempo de espera medio (s)", "Group*.waitTime"),
    "mm_WDM": ("Usa WorkingDayMovement (0/1)", "Group*.movementModel"),
    "mm_RWP": ("Usa RandomWaypoint (0/1)", "Group*.movementModel"),
    "mm_MapRoute": ("Usa MapRouteMovement (0/1)", "Group*.movementModel"),
    "mm_Cluster": ("Usa ClusterMovement (0/1)", "Group*.movementModel"),
    "mm_Bus": ("Usa BusMovement (0/1)", "Group*.movementModel"),
    "mm_ShortestPath": ("Usa ShortestPathMapBasedMovement (0/1)", "Group*.movementModel"),
    "mm_External": ("Usa External/ExternalPathMovement (0/1)", "Group*.movementModel"),
    "mm_Linear": ("Usa LinearMovement (0/1)", "Group*.movementModel"),
    "transmitRange": ("Rango de transmisión (m)", "bt0.transmitRange / interface.transmitRange"),
    "contact_rate_proxy": ("Proxy tasa de contacto", "density, transmitRange, speed (derivado)"),
    "event_interval_mean": ("Intervalo medio entre mensajes (s)", "Events1.interval"),
    "event_size_mean": ("Tamaño medio de mensaje (bytes)", "Events1.size"),
    "msgTtl": ("TTL de mensajes (s)", "Group*.msgTtl"),
    "pattern_uniform": ("Patrón tráfico uniforme (0/1)", "Events* (sin time/tohosts)"),
    "pattern_burst": ("Patrón tráfico con ventana temporal (0/1)", "Events*.time"),
    "pattern_hub_target": ("Patrón tráfico dirigido a hubs (0/1)", "Events*.tohosts"),
    "nrof_event_generators": ("Número de generadores de eventos", "Events.nrof"),
    "bufferSize": ("Tamaño de buffer (bytes)", "Group*.bufferSize"),
    "transmitSpeed": ("Velocidad de transmisión (bytes/s)", "bt0.transmitSpeed"),
    "workDayLength": ("Duración jornada laboral (s); NaN si no WDM", "Group*.workDayLength"),
    "timeDiffSTD": ("Desv. estándar diferencia horaria (s); NaN si no WDM", "Group*.timeDiffSTD"),
    "probGoShoppingAfterWork": ("Prob. ir de compras; NaN si no WDM", "Group*.probGoShoppingAfterWork"),
    "nrOfMeetingSpots": ("Número de puntos de encuentro; NaN si no WDM", "Group*.nrOfMeetingSpots"),
    "nrOfOffices": ("Número de oficinas; NaN si no WDM", "Group*.nrOfOffices"),
    "officeSize": ("Tamaño de oficina (personas); NaN si no WDM", "Group*.officeSize"),
    "nrOfShops": ("Número de tiendas; NaN si no WDM", "Group*.nrOfShops"),
    "ownCarProb": ("Prob. poseer coche (0–1); relevante vehicular/WDM", "Group*.ownCarProb"),
    "shopSize": ("Tamaño de tienda (personas); NaN si no WDM", "Group*.shopSize"),
    "officeWaitTime_mean": ("Tiempo espera en oficina medio (s); NaN si no WDM", "Group*.officeMinWaitTime, officeMaxWaitTime"),
    "shoppingWaitTime_mean": ("Tiempo espera compras medio (s); NaN si no WDM", "Group*.shoppingMinWaitTime, shoppingMaxWaitTime"),
    "eveningGroupSize_mean": ("Tamaño grupo actividad evening medio; NaN si no WDM", "Group*.minGroupSize, maxGroupSize"),
    "eveningWaitTime_mean": ("Tiempo espera actividad evening medio (s); NaN si no WDM", "Group*.minWaitTime, maxWaitTime"),
    "afterShoppingStopTime_mean": ("Tiempo parada tras compras medio (s); NaN si no WDM", "Group*.minAfterShoppingStopTime, maxAfterShoppingStopTime"),
    "clusterRange_mean": ("Radio medio de clusters (m); NaN si no ClusterMovement", "Group*.clusterRange"),
    "event2_interval_mean": ("Intervalo medio 2.º flujo (s); NaN si Events.nrof<2 o Events2.filePath", "Events2.interval"),
    "event2_size_mean": ("Tamaño medio 2.º flujo (bytes); NaN si Events.nrof<2 o Events2.filePath", "Events2.size"),
    "Scenario.endTime": ("Duración de la simulación (s)", "Scenario.endTime"),
    "nrofHostGroups": ("Número de grupos de hosts", "Scenario.nrofHostGroups"),
    "has_active_times": ("Grupos con activeTimes definido (0/1)", "Group*.activeTimes"),
}

# Claves de settings que SÍ se usan para extraer features (alguna variante Group/Group1/bt0/etc.)
SETTINGS_KEYS_USED = {
    "Scenario.endTime", "Scenario.nrofHostGroups",
    "MovementModel.worldSize",
    "Group.nrofHosts", "Group.speed", "Group.waitTime", "Group.movementModel",
    "Group.interface1", "Group.bufferSize", "Group.msgTtl",
    "Group.workDayLength", "Group.timeDiffSTD", "Group.probGoShoppingAfterWork",
    "Group.nrOfMeetingSpots", "Group.nrOfOffices", "Group.officeSize", "Group.nrOfShops",
    "Group.ownCarProb", "Group.shopSize",
    "Group.officeMinWaitTime", "Group.officeMaxWaitTime",
    "Group.shoppingMinWaitTime", "Group.shoppingMaxWaitTime",
    "Group.minGroupSize", "Group.maxGroupSize", "Group.minWaitTime", "Group.maxWaitTime",
    "Group.minAfterShoppingStopTime", "Group.maxAfterShoppingStopTime",
    "Group.activeTimes",
    "Events.nrof", "Events1.interval", "Events1.size", "Events1.time", "Events1.tohosts",
    "bt0.transmitRange", "bt0.transmitSpeed",
}
# Añadir Group2..GroupN y Events2.. si existen en corpus
def _all_used_key_variants(keys_in_corpus: set[str]) -> set[str]:
    out = set(SETTINGS_KEYS_USED)
    used_suffixes = (
        ".nrofHosts", ".speed", ".waitTime", ".movementModel", ".workDayLength", ".timeDiffSTD",
        ".probGoShoppingAfterWork", ".nrOfMeetingSpots", ".nrOfOffices", ".bufferSize", ".msgTtl",
        ".interface1", ".activeTimes",
        ".officeSize", ".nrOfShops", ".ownCarProb", ".shopSize",
        ".officeMinWaitTime", ".officeMaxWaitTime", ".shoppingMinWaitTime", ".shoppingMaxWaitTime",
        ".minGroupSize", ".maxGroupSize", ".minWaitTime", ".maxWaitTime",
        ".minAfterShoppingStopTime", ".maxAfterShoppingStopTime",
        ".clusterRange",
    )
    for k in keys_in_corpus:
        if k.startswith("Group") and any(s in k for s in used_suffixes):
            out.add(k)
        if (k.startswith("Events") and (".interval" in k or ".size" in k or ".time" in k or ".tohosts" in k or k == "Events.nrof")):
            out.add(k)
        if k.startswith("Group") and ".clusterRange" in k:
            out.add(k)
        if "transmitRange" in k or "transmitSpeed" in k:
            out.add(k)
    return out

# Razones por las que un setting no se usa (decisión definitiva para la investigación; ver features_decision.md)
NOT_USED_REASONS: dict[str, str] = {
    "MovementModel.rngSeed": "DESCARTADO: Aleatoriedad; no caracteriza el escenario de forma estable.",
    "Scenario.name": "DESCARTADO: Identificador; no feature numérica.",
    "Scenario.simulateConnections": "DESCARTADO: Parámetro de simulación fijo en todo el corpus.",
    "Scenario.updateInterval": "DESCARTADO: Parámetro de simulación fijo.",
    "MapBasedMovement.nrofMapFiles": "DESCARTADO: Ruta/cantidad de ficheros; no comparable numéricamente entre mapas.",
    "MapBasedMovement.mapFile1": "DESCARTADO: Ruta de fichero; no comparable.",
    "Group.busControlSystemNr": "DESCARTADO: Referencia interna al sistema de buses.",
    "Group1.routeFile": "DESCARTADO: Ruta de fichero (depende del mapa).",
    "Group1.routeType": "DESCARTADO: Mismo valor (1) en escenarios con bus; sin variabilidad.",
    "Group1.groupID": "DESCARTADO: Identificador de grupo.",
    "Group1.busControlSystemNr": "DESCARTADO: Referencia interna.",
    "Group1.nrofHosts": "DESCARTADO: Usado indirectamente vía N (total).",
    "Group1.speed": "DESCARTADO: Usado si es el único grupo; si hay varios, se prioriza grupo principal.",
    "Group1.waitTime": "DESCARTADO: Idem.",
    "Group.nrofInterfaces": "DESCARTADO: Casi siempre 1; sin variabilidad útil.",
    "bt0.type": "DESCARTADO: Tipo de interfaz; mismo en todo el corpus.",
    "Report.nrofReports": "DESCARTADO: Configuración de salida, no de escenario.",
    "Report.reportDir": "DESCARTADO: Salida.",
    "Report.report1": "DESCARTADO: Salida.",
    "Report.report2": "DESCARTADO: Salida.",
    "Events1.class": "DESCARTADO: Tipo de generador; mismo en todo el corpus.",
    "Events1.hosts": "DESCARTADO: Redundante con N.",
    "Events1.prefix": "DESCARTADO: Identificador de mensajes.",
    "Group.router": "DESCARTADO: Mismo en todo el corpus (EpidemicRouter).",
    "Group.officeWaitTimeParetoCoeff": "DESCARTADO: Detalle de distribución; ya usamos officeWaitTime_mean.",
    "Group.eveningActivityControlSystemNr": "DESCARTADO: Referencia interna.",
    "Group.shoppingControlSystemNr": "DESCARTADO: Referencia interna.",
    "Group.shoppingWaitTimeParetoCoeff": "DESCARTADO: Ya usamos shoppingWaitTime_mean.",
    "Group.minAfterShoppingStopTime": "DESCARTADO: Incluido en feature afterShoppingStopTime_mean.",
    "Group.maxAfterShoppingStopTime": "DESCARTADO: Incluido en feature afterShoppingStopTime_mean.",
    "Group.homeLocationsFile": "DESCARTADO: Ruta de fichero; no comparable entre mapas.",
    "Group.officeLocationsFile": "DESCARTADO: Ruta de fichero; no comparable.",
    "Group.meetingSpotsFile": "DESCARTADO: Ruta de fichero; no comparable.",
    "Group.routeFile": "DESCARTADO: Ruta de fichero.",
    "Group.LinearMovement.startLocation": "DESCARTADO: Coordenadas; dependen del mapa.",
    "Group.LinearMovement.endLocation": "DESCARTADO: Coordenadas; dependen del mapa.",
    "Group.LinearMovement.initLocType": "DESCARTADO: Solo 1 escenario; sin variabilidad.",
    "Group.LinearMovement.targetType": "DESCARTADO: Solo 1 escenario; sin variabilidad.",
    "Events2.class": "DESCARTADO: Tipo/identificador; no comparable.",
    "Events2.filePath": "DESCARTADO: Tráfico desde fichero; no extraemos número comparable.",
    "Events2.hosts": "DESCARTADO: Redundante con N.",
    "Events2.nrofPreload": "DESCARTADO: No priorizado para diversidad.",
    "Events2.prefix": "DESCARTADO: Identificador.",
    "Group.okMaps": "DESCARTADO: No usado de forma relevante en el corpus.",
    "Group.routeType": "DESCARTADO: Sin variabilidad útil en el corpus.",
}
# Razón por defecto para claves no listadas (p. ej. Group2.*, Group3.*, ...)
NOT_USED_REASON_DEFAULT = "DESCARTADO: Ver ../docs/features_decision.md (variante de grupo o misma categoría que Group/Group1)."


def collect_all_settings_keys(corpus_dir: Path, scenario_paths: list[Path]) -> set[str]:
    """Recorre todos los .settings del corpus y devuelve el conjunto de claves (key=value)."""
    keys = set()
    for p in scenario_paths:
        d = load_settings(p)
        keys.update(d.keys())
    return keys


def run_phase_features_report(corpus_dir: Path, out_dir: Path, scenario_paths: list[Path]) -> bool:
    """
    Escribe reports/features_report.txt y reports/features_report.md:
    - Lista de los 33 features usados en correlación: nombre, descripción, setting(s) de origen.
    - Lista de settings presentes en el corpus que NO se usan y motivo.
    """
    out_dir = Path(out_dir)
    reports_dir = out_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    all_keys = collect_all_settings_keys(corpus_dir, scenario_paths)
    used_keys = _all_used_key_variants(all_keys)

    # Features usados (orden del vector)
    feature_order = list(settings_to_reportable_features(load_settings(scenario_paths[0])).keys())
    lines_txt = [
        "=== Informe de features (correlación y diversidad) ===",
        f"Generado por run_analysis.py --phase features_report. Corpus: {len(scenario_paths)} escenarios.",
        "",
        f"--- FEATURES UTILIZADOS ({len(feature_order)}) ---",
        "Estos features forman el vector por escenario y se usan para correlación Pearson/Spearman,",
        "distancia coseno, clustering y figuras.",
        "",
    ]
    for f in feature_order:
        desc, src = FEATURE_METADATA.get(f, ("—", "—"))
        lines_txt.append(f"  {f}")
        lines_txt.append(f"    Descripción: {desc}")
        lines_txt.append(f"    Origen:      {src}")
        lines_txt.append("")

    not_used = sorted(all_keys - used_keys)
    lines_txt.append("--- SETTINGS NO UTILIZADOS EN EL VECTOR DE FEATURES ---")
    lines_txt.append("Presentes en uno o más .settings del corpus pero DESCARTADOS de forma definitiva para el análisis.")
    lines_txt.append("Justificación metodológica completa: docs/features_decision.md")
    lines_txt.append("")
    for k in not_used:
        reason = NOT_USED_REASONS.get(k, NOT_USED_REASON_DEFAULT)
        lines_txt.append(f"  {k}")
        lines_txt.append(f"    Motivo: {reason}")
        lines_txt.append("")

    report_txt = "\n".join(lines_txt)
    (reports_dir / "features_report.txt").write_text(report_txt, encoding="utf-8")

    # Markdown
    md_lines = [
        "# Informe de features",
        "",
        "Features utilizados para correlación y diversidad, y settings no utilizados con motivo.",
        "",
        f"## Features utilizados ({len(feature_order)})",
        "",
        "| Feature | Descripción | Origen (setting) |",
        "|---------|-------------|------------------|",
    ]
    for f in feature_order:
        desc, src = FEATURE_METADATA.get(f, ("—", "—"))
        md_lines.append(f"| {f} | {desc} | {src} |")
    md_lines.append("")
    md_lines.append("## Settings no utilizados")
    md_lines.append("")
    md_lines.append("| Setting | Motivo |")
    md_lines.append("|---------|--------|")
    for k in not_used:
        reason = NOT_USED_REASONS.get(k, NOT_USED_REASON_DEFAULT)
        md_lines.append(f"| `{k}` | {reason} |")
    (reports_dir / "features_report.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Written {reports_dir / 'features_report.txt'} and features_report.md")
    return True


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


def zscore_normalize_per_feature(df: "pd.DataFrame", impute_nan_zero: bool = True) -> tuple["pd.DataFrame", "pd.DataFrame"]:
    """
    Normalización z-score por característica (por columna), política NaN según features_core_vs_extended.md §4:
    - μ_j, σ_j = media y desv. típica de la característica j solo sobre valores no-NaN.
    - Z_s,j = (X_s,j - μ_j) / σ_j; si σ_j = 0 (columna constante), Z_s,j = 0.
    - Tras normalizar, NaNs se imputan a 0 en el espacio estandarizado (features condicionales actúan como neutros).
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
    if impute_nan_zero:
        Z = Z.fillna(0.0)
    params_df = pd.DataFrame(params)
    return Z, params_df


def run_phase_normalize(out_dir: Path) -> bool:
    """
    Fase 2: lee data/features.csv, aplica z-score por característica (ignorando NaN),
    imputa NaN → 0 en espacio estandarizado (§4 features_core_vs_extended.md),
    escribe features_normalized.csv, normalization_params.csv, features_core.csv (23), features_reduced.csv (17).
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
    Z, params_df = zscore_normalize_per_feature(df, impute_nan_zero=True)
    Z.to_csv(data_dir / "features_normalized.csv")
    params_df.to_csv(data_dir / "normalization_params.csv", index=False)
    print(f"Written {data_dir / 'features_normalized.csv'} (shape {Z.shape}, NaN→0)")

    # Core 24 y reducido 17 para ablación y correlación feature–feature
    core_cols = [c for c in FEATURES_CORE_23 if c in Z.columns]
    red_cols = [c for c in FEATURES_REDUCED_17 if c in Z.columns]
    if len(core_cols) == 23:
        Z[core_cols].to_csv(data_dir / "features_core.csv")
        print(f"Written {data_dir / 'features_core.csv'} (23 core features)")
    else:
        print(f"Warning: only {len(core_cols)}/23 core columns in data (missing: {set(FEATURES_CORE_23) - set(Z.columns)})")
    if len(red_cols) == 17:
        Z[red_cols].to_csv(data_dir / "features_reduced.csv")
        print(f"Written {data_dir / 'features_reduced.csv'} (17 reduced features)")
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
    # Para distancias y clustering: NaN = ausencia de feature (p. ej. no-WDM) → 0 en espacio normalizado
    Z_arr_filled = np.nan_to_num(Z_arr, nan=0.0, posinf=0.0, neginf=0.0)

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

    # Distancia coseno (1 - cos_sim) y euclídea (sobre Z rellenado para evitar NaN)
    cos_dist = cosine_distance_matrix(Z_arr_filled)
    euc_dist = euclidean_distance_matrix(Z_arr_filled)
    pd.DataFrame(cos_dist, index=index_df, columns=index_df).to_csv(data_dir / "distance_cosine.csv")
    pd.DataFrame(euc_dist, index=index_df, columns=index_df).to_csv(data_dir / "distance_euclidean.csv")
    cos_flat = cos_dist[triu[0], triu[1]]
    euc_flat = euc_dist[triu[0], triu[1]]
    min_cos_dist = float(np.nanmin(cos_flat)) if len(cos_flat) else np.nan
    n_pairs_cos_below_005 = int(np.sum(cos_flat < 0.05))

    # Clustering sobre Z (ward) para diagnóstico de estructura.
    n_clusters = 7
    cluster_labels = None
    silhouette_score = np.nan
    if linkage is not None and fcluster is not None:
        try:
            link = linkage(Z_arr_filled, method="ward")
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
        "Diagnóstico: 0 rechazos no implica ausencia de correlación; con n=d la potencia depende de d (features).",
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

    # ----- Correlación y diversificación en espacio CORE 23 (referencia para investigación) -----
    path_core = data_dir / "features_core.csv"
    if path_core.exists() and pd is not None:
        Z_core = pd.read_csv(path_core, index_col=0)
        Z_core_arr = Z_core.values
        R_core23 = Z_core.T.corr()
        R_core23.to_csv(data_dir / "correlation_pearson_core23.csv")
        triu_c = np.triu_indices(n, k=1)
        r_core_flat = R_core23.values[triu_c[0], triu_c[1]]
        abs_r_core = np.abs(r_core_flat)
        n_above_core = int(np.sum(abs_r_core >= threshold))
        total_core = len(r_core_flat)
        max_abs_r_core = float(np.nanmax(abs_r_core)) if total_core else np.nan
        mean_abs_r_core = float(np.nanmean(abs_r_core)) if total_core else np.nan
        cos_dist_core = cosine_distance_matrix(Z_core_arr)
        pd.DataFrame(cos_dist_core, index=index_df, columns=index_df).to_csv(data_dir / "distance_cosine_core23.csv")
        min_cos_core = float(np.nanmin(cos_dist_core[triu_c[0], triu_c[1]])) if total_core else np.nan
        pairs_above_core = []
        for idx in np.where(abs_r_core >= threshold)[0]:
            i, k = triu_c[0][idx], triu_c[1][idx]
            pairs_above_core.append((labels[i], labels[k], float(R_core23.iloc[i, k])))
        silhouette_core23 = np.nan
        if linkage is not None and fcluster is not None:
            try:
                link_core = linkage(Z_core_arr, method="ward")
                cluster_core = fcluster(link_core, n_clusters, criterion="maxclust")
                silhouette_core23 = silhouette_from_distance(cos_dist_core, cluster_core)
                pd.DataFrame({"scenario": labels, "cluster": cluster_core}).to_csv(data_dir / "cluster_assignments_core23.csv", index=False)
            except Exception:
                pass
        report_core_lines = [
            "=== Correlación entre escenarios en espacio CORE 23 (referencia para investigación) ===",
            f"Vectores Z_core: n={n} escenarios, d=23 features. r(Si, Sk) = Pearson entre filas de Z_core.",
            "",
            f"  max |r| = {max_abs_r_core:.4f}",
            f"  media |r| = {mean_abs_r_core:.4f}",
            f"  Total pares: {total_core}",
            f"  Pares con |r| >= {threshold}: {n_above_core} ({100.0 * n_above_core / total_core:.1f}%)",
            "",
            f"  Distancia coseno mínima = {min_cos_core:.4f}",
            f"  Silhouette (Ward k={n_clusters} sobre Z_core) = {silhouette_core23:.4f}",
            "",
            "Objetivo investigación: diversidad y resultados se evalúan con las 23 core. Priorizar reducción de pares |r|>=0.7 en este espacio.",
        ]
        if pairs_above_core:
            report_core_lines.append("")
            report_core_lines.append(f"Pares con |r| >= {threshold} (máximo 30):")
            for (a, b, r) in sorted(pairs_above_core, key=lambda x: -abs(x[2]))[:30]:
                report_core_lines.append(f"  {a} <-> {b}  r = {r:.4f}")
            if len(pairs_above_core) > 30:
                report_core_lines.append(f"  ... y {len(pairs_above_core) - 30} más.")
        count_above_core = {s: 0 for s in labels}
        for (a, b, _) in pairs_above_core:
            count_above_core[a] += 1
            count_above_core[b] += 1
        scenarios_core_sorted = sorted(set(a for (a, b, _) in pairs_above_core) | set(b for (a, b, _) in pairs_above_core), key=lambda s: -count_above_core[s])
        diversify_core_lines = [
            "# Escenarios a diversificar (core 23) — aparecen en pares con |r| >= 0.7 en espacio de 23 features",
            f"# Referencia para investigación. Total: {len(scenarios_core_sorted)} escenarios.",
            "",
        ]
        for s in scenarios_core_sorted:
            diversify_core_lines.append(f"{s}  (# pares |r|>={threshold} en core23: {count_above_core[s]})")
        (reports_dir / "correlation_core23_report.txt").write_text("\n".join(report_core_lines), encoding="utf-8")
        (reports_dir / "scenarios_to_diversify_core23.txt").write_text("\n".join(diversify_core_lines), encoding="utf-8")
        print(f"Written correlation_core23_report.txt, scenarios_to_diversify_core23.txt ({len(scenarios_core_sorted)} escenarios), correlation_pearson_core23.csv, distance_cosine_core23.csv")

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


def run_phase_feature_feature_correlation(out_dir: Path) -> bool:
    """
    Correlación entre las 23 features del core (feature–feature), §5 features_core_vs_extended.md.
    Matriz 23×23 sobre escenarios (columnas = features). Salida: data/ y figures/heatmap_feature_feature_core.png.
    """
    if pd is None:
        print("pandas is required for --phase feature_correlation")
        return False
    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    figures_dir = out_dir / "figures"
    reports_dir = out_dir / "reports"
    path_core = data_dir / "features_core.csv"
    if not path_core.exists():
        print(f"Not found: {path_core}. Run --phase normalize first.")
        return False
    data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    Z = pd.read_csv(path_core, index_col=0)
    # Correlación entre columnas (features) sobre las filas (escenarios)
    R_ff = Z.corr()
    R_ff.to_csv(data_dir / "feature_feature_correlation_core.csv")
    abs_r = R_ff.abs()
    np.fill_diagonal(abs_r.values, 0)
    max_off_diag = float(abs_r.max().max())
    pairs_high = []
    for i in range(len(R_ff.columns)):
        for k in range(i + 1, len(R_ff.columns)):
            r = R_ff.iloc[i, k]
            if not pd.isna(r) and abs(r) >= 0.9:
                pairs_high.append((R_ff.columns[i], R_ff.columns[k], float(r)))
    report_lines = [
        "=== Correlación feature–feature (core 23) ===",
        "Matriz 23×23: correlación entre features sobre los escenarios (columnas de Z).",
        f"max |r| off-diagonal = {max_off_diag:.4f}",
        "",
        "Objetivo (§5): no pares con |r| > 0.9 (baja redundancia del core).",
        f"Pares con |r| >= 0.9: {len(pairs_high)}",
    ]
    if pairs_high:
        report_lines.append("")
        for a, b, r in sorted(pairs_high, key=lambda x: -abs(x[2])):
            report_lines.append(f"  {a} <-> {b}  r = {r:.4f}")
    report_text = "\n".join(report_lines)
    (reports_dir / "feature_feature_correlation_report.txt").write_text(report_text, encoding="utf-8")

    if plt is not None:
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        im = ax.imshow(R_ff.values, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(R_ff.columns)))
        ax.set_yticks(range(len(R_ff.columns)))
        ax.set_xticklabels(R_ff.columns, rotation=45, ha="right", fontsize=7)
        ax.set_yticklabels(R_ff.columns, fontsize=7)
        plt.colorbar(im, ax=ax, label="Pearson r (feature–feature)")
        ax.set_title("Correlación entre features del core (23×23)")
        plt.tight_layout()
        plt.savefig(figures_dir / "heatmap_feature_feature_core.png", dpi=150, bbox_inches="tight")
        plt.savefig(figures_dir / "heatmap_feature_feature_core.pdf", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Written {figures_dir / 'heatmap_feature_feature_core.png'}")
    print(report_text)
    print(f"Written {data_dir / 'feature_feature_correlation_core.csv'}, {reports_dir / 'feature_feature_correlation_report.txt'}")
    return True


def run_phase_ablation(out_dir: Path, threshold: float = 0.7, n_clusters: int = 7) -> bool:
    """
    Ablación 17 vs 23 vs 46 (§6 features_core_vs_extended.md).
    Métricas por conjunto: max |r|, media |r|, pares |r|>=threshold, Silhouette (Ward).
    Escribe reports/ablation_report.txt y data/ablation_metrics.csv.
    """
    if pd is None or linkage is None or fcluster is None:
        print("pandas and scipy.cluster required for --phase ablation")
        return False
    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    reports_dir = out_dir / "reports"
    path_norm = data_dir / "features_normalized.csv"
    path_core = data_dir / "features_core.csv"
    path_red = data_dir / "features_reduced.csv"
    if not path_norm.exists():
        print(f"Not found: {path_norm}. Run --phase normalize first.")
        return False
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    Z_full = pd.read_csv(path_norm, index_col=0)
    n_scenarios = len(Z_full)
    labels = Z_full.index.tolist()
    results = []

    def metrics_for_Z(Z_mat: np.ndarray, name: str, d: int) -> dict:
        R = np.corrcoef(Z_mat)
        triu = np.triu_indices(n_scenarios, k=1)
        r_flat = R[triu[0], triu[1]]
        abs_r = np.abs(r_flat)
        max_abs_r = float(np.nanmax(abs_r)) if len(abs_r) else np.nan
        mean_abs_r = float(np.nanmean(abs_r)) if len(abs_r) else np.nan
        n_above = int(np.sum(abs_r >= threshold))
        total = len(abs_r)
        cos_dist = cosine_distance_matrix(Z_mat)
        try:
            link = linkage(Z_mat, method="ward")
            cl = fcluster(link, n_clusters, criterion="maxclust")
            sil = silhouette_from_distance(cos_dist, cl)
        except Exception:
            sil = np.nan
        return {
            "set": name,
            "n_features": d,
            "max_abs_r": max_abs_r,
            "mean_abs_r": mean_abs_r,
            "pairs_r_above_threshold": n_above,
            "total_pairs": total,
            "pct_above": 100.0 * n_above / total if total else 0,
            "silhouette": sil,
        }

    # Reduced 17
    if path_red.exists():
        Z_red = pd.read_csv(path_red, index_col=0)
        if Z_red.shape[1] >= 17:
            res = metrics_for_Z(Z_red.values, "reduced_17", Z_red.shape[1])
            results.append(res)
    # Core 23
    if path_core.exists():
        Z_core = pd.read_csv(path_core, index_col=0)
        res = metrics_for_Z(Z_core.values, "core_23", Z_core.shape[1])
        results.append(res)
    # Full (46)
    res_full = metrics_for_Z(Z_full.values, "full_46", Z_full.shape[1])
    results.append(res_full)

    df_ablation = pd.DataFrame(results)
    df_ablation.to_csv(data_dir / "ablation_metrics.csv", index=False)

    report_lines = [
        "=== Ablación 17 vs 23 vs 46 (features_core_vs_extended.md §6) ===",
        f"Escenarios: n = {n_scenarios}. Umbral |r| = {threshold}. Clusters Ward k = {n_clusters}.",
        "",
        "Métricas por conjunto:",
    ]
    for r in results:
        report_lines.append(f"  {r['set']} (d={r['n_features']}): max|r|={r['max_abs_r']:.4f}, mean|r|={r['mean_abs_r']:.4f}, "
                            f"pares |r|>={threshold}={r['pairs_r_above_threshold']} ({r['pct_above']:.1f}%), silhouette={r['silhouette']:.4f}")
    report_lines.extend([
        "",
        "Objetivo: el core 23 ofrece mejor compromiso expresividad / redundancia / interpretabilidad.",
    ])
    report_text = "\n".join(report_lines)
    (reports_dir / "ablation_report.txt").write_text(report_text, encoding="utf-8")
    print(report_text)
    print(f"Written {data_dir / 'ablation_metrics.csv'}, {reports_dir / 'ablation_report.txt'}")
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

    # ---------- Figuras comparables por espacio (17 / 23 / 46) ----------
    by_space_dir = figures_dir / "by_space"
    by_space_dir.mkdir(parents=True, exist_ok=True)

    spaces: list[tuple[str, Path]] = [
        ("reduced_17", data_dir / "features_reduced.csv"),
        ("core_23", data_dir / "features_core.csv"),
        ("full_46", data_dir / "features_normalized.csv"),
    ]

    for space_name, path_space in spaces:
        if not path_space.exists():
            continue
        Zs_df = pd.read_csv(path_space, index_col=0)
        Zs = Zs_df.values
        labels_s = Zs_df.index.tolist()
        n_s, d_s = Zs.shape
        if n_s < 2 or d_s < 2:
            continue

        Rs = np.corrcoef(Zs)
        triu_s = np.triu_indices(n_s, k=1)
        rs_flat = Rs[triu_s[0], triu_s[1]]
        nbins_s = min(50, max(15, len(rs_flat) // 30))

        # Heatmap Pearson por espacio
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        im = ax.imshow(Rs, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(n_s))
        ax.set_yticks(range(n_s))
        ax.set_xticklabels(labels_s, rotation=45, ha="right", fontsize=6)
        ax.set_yticklabels(labels_s, fontsize=6)
        plt.colorbar(im, ax=ax, label="Pearson r")
        ax.set_title(f"Correlación entre escenarios (Pearson, {space_name}, d={d_s})")
        plt.tight_layout()
        plt.savefig(by_space_dir / f"heatmap_pearson_{space_name}.png", dpi=150, bbox_inches="tight")
        plt.savefig(by_space_dir / f"heatmap_pearson_{space_name}.pdf", dpi=150, bbox_inches="tight")
        plt.close()

        # Histograma Pearson por espacio
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        ax.hist(rs_flat, bins=nbins_s, color="steelblue", edgecolor="black", alpha=0.7)
        ax.axvline(threshold, color="red", linestyle="--", label=f"|r| = {threshold}")
        ax.axvline(-threshold, color="red", linestyle="--")
        ax.set_xlabel("Pearson r (pares de escenarios)")
        ax.set_ylabel("Frecuencia")
        ax.set_title(f"Distribución Pearson ({space_name}, d={d_s})")
        ax.legend()
        plt.tight_layout()
        plt.savefig(by_space_dir / f"histogram_correlations_pearson_{space_name}.png", dpi=150, bbox_inches="tight")
        plt.savefig(by_space_dir / f"histogram_correlations_pearson_{space_name}.pdf", dpi=150, bbox_inches="tight")
        plt.close()

        # PCA scatter por espacio
        Zs_centered = Zs - np.nanmean(Zs, axis=0)
        try:
            U_s, S_s, _Vt_s = np.linalg.svd(Zs_centered, full_matrices=False)
            pc1_s = U_s[:, 0] * S_s[0]
            pc2_s = U_s[:, 1] * S_s[1]
            if np.var(pc1_s) > 1e-10:
                r_pc_s = np.corrcoef(pc1_s, pc2_s)[0, 1]
                a_s = np.cov(pc1_s, pc2_s)[0, 1] / np.var(pc1_s)
                b_s = np.mean(pc2_s) - a_s * np.mean(pc1_s)
                x_line_s = np.linspace(pc1_s.min(), pc1_s.max(), 100)
                y_line_s = a_s * x_line_s + b_s
                r2_s = r_pc_s ** 2
            else:
                x_line_s = y_line_s = np.nan
                r2_s = np.nan
        except Exception:
            pc1_s = pc2_s = np.arange(n_s, dtype=float)
            x_line_s = y_line_s = np.nan
            r2_s = np.nan

        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        ax.scatter(pc1_s, pc2_s, s=60, alpha=0.8, edgecolors="black", linewidths=0.5)
        if not (np.any(np.isnan(x_line_s)) or np.any(np.isnan(y_line_s))):
            ax.plot(x_line_s, y_line_s, "r-", linewidth=2, label=f"Regresión (R² = {r2_s:.3f})")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_title(f"PCA 2D + regresión ({space_name}, d={d_s})")
        ax.legend(loc="best", fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
        ax.axvline(0, color="gray", linestyle=":", alpha=0.5)
        plt.tight_layout()
        plt.savefig(by_space_dir / f"scatter_pca_regression_{space_name}.png", dpi=150, bbox_inches="tight")
        plt.savefig(by_space_dir / f"scatter_pca_regression_{space_name}.pdf", dpi=150, bbox_inches="tight")
        plt.close()

    print(f"Written {len(list(figures_dir.glob('*.png')))} figures to {figures_dir}")
    return True


def run_phase_figures_paper(out_dir: Path, threshold: float = 0.7) -> bool:
    """
    Figuras "paper-ready" sin tocar figuras actuales:
    escribe solo en figures/paper/(main|supplementary) y genera versiones más limpias
    (anotaciones en histogramas, PCA por familia/cluster, plots de ablación).
    """
    if plt is None:
        print("matplotlib is required for --phase figures_paper")
        return False
    if pd is None:
        print("pandas is required for --phase figures_paper")
        return False

    out_dir = Path(out_dir)
    data_dir = out_dir / "data"
    figures_paper_dir = out_dir / "figures" / "paper"
    main_dir = figures_paper_dir / "main"
    supp_dir = figures_paper_dir / "supplementary"
    main_dir.mkdir(parents=True, exist_ok=True)
    supp_dir.mkdir(parents=True, exist_ok=True)

    def _save_png_pdf(fig, path_no_ext: Path) -> None:
        fig.savefig(path_no_ext.with_suffix(".png"), dpi=150, bbox_inches="tight")
        fig.savefig(path_no_ext.with_suffix(".pdf"), dpi=150, bbox_inches="tight")

    # ---------------- Inputs ----------------
    path_r = data_dir / "correlation_pearson.csv"
    path_rs = data_dir / "correlation_spearman.csv"
    path_z = data_dir / "features_normalized.csv"
    path_ablation = data_dir / "ablation_metrics.csv"
    path_clusters = data_dir / "cluster_assignments.csv"
    path_outputs = data_dir / "output_metrics.csv"
    path_ff_core = data_dir / "feature_feature_correlation_core.csv"

    if not path_r.exists():
        print(f"Not found: {path_r}. Run --phase correlation first.")
        return False

    R_pearson = pd.read_csv(path_r, index_col=0)
    labels = R_pearson.index.tolist()
    n = len(labels)
    triu = np.triu_indices(n, k=1)
    r_flat = R_pearson.values[triu[0], triu[1]]
    abs_r = np.abs(r_flat)
    n_pairs = int(len(r_flat))
    n_high = int(np.sum(abs_r >= threshold))
    pct_high = 100.0 * n_high / n_pairs if n_pairs else 0.0

    # ---------------- Histogram Pearson (paper) ----------------
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    nbins = min(50, max(15, len(r_flat) // 30))
    ax.hist(r_flat, bins=nbins, color="steelblue", edgecolor="black", alpha=0.7)
    ax.axvline(threshold, color="red", linestyle="--", label=f"|r| = {threshold}")
    ax.axvline(-threshold, color="red", linestyle="--")
    ax.set_xlabel("Pearson r (pares de escenarios)")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Distribución de correlaciones Pearson entre escenarios")
    ax.legend()
    ax.text(
        0.02,
        0.98,
        f"pares: {n_pairs}\\n|r|≥{threshold}: {n_high} ({pct_high:.1f}%)",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="none"),
    )
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    _save_png_pdf(fig, main_dir / "histogram_correlations_pearson_paper")
    plt.close(fig)

    # ---------------- Histogram Spearman (paper) ----------------
    if path_rs.exists():
        R_spearman = pd.read_csv(path_rs, index_col=0).values
        r_sp_flat = R_spearman[triu[0], triu[1]]
        abs_sp = np.abs(r_sp_flat)
        n_high_sp = int(np.sum(abs_sp >= threshold))
        pct_high_sp = 100.0 * n_high_sp / n_pairs if n_pairs else 0.0

        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        ax.hist(r_sp_flat, bins=nbins, color="seagreen", edgecolor="black", alpha=0.7)
        ax.axvline(threshold, color="red", linestyle="--", label=f"|r| = {threshold}")
        ax.axvline(-threshold, color="red", linestyle="--")
        ax.set_xlabel("Spearman r (pares de escenarios)")
        ax.set_ylabel("Frecuencia")
        ax.set_title("Distribución de correlaciones Spearman entre escenarios")
        ax.legend()
        ax.text(
            0.02,
            0.98,
            f"pares: {n_pairs}\\n|r|≥{threshold}: {n_high_sp} ({pct_high_sp:.1f}%)",
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=9,
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="none"),
        )
        ax.grid(True, alpha=0.2)
        fig.tight_layout()
        _save_png_pdf(fig, supp_dir / "histogram_correlations_spearman_paper")
        plt.close(fig)

    # ---------------- PCA by family / cluster ----------------
    if path_z.exists():
        Z_df = pd.read_csv(path_z, index_col=0)
        Z = Z_df.values
        scen = Z_df.index.tolist()

        # PCA via SVD (same as figures, but no per-point labels)
        Z_centered = Z - np.nanmean(Z, axis=0)
        try:
            U, S, _Vt = np.linalg.svd(Z_centered, full_matrices=False)
            pc1 = U[:, 0] * S[0]
            pc2 = U[:, 1] * S[1]
        except Exception:
            pc1 = np.arange(len(scen), dtype=float)
            pc2 = np.zeros(len(scen), dtype=float)

        family_map = {
            "U": "Urban",
            "C": "Campus",
            "V": "Vehicles",
            "R": "Rural",
            "D": "Disaster",
            "S": "Social",
            "T": "Traffic",
        }
        fam = []
        for s in scen:
            key = s[:1].upper() if s else "?"
            fam.append(family_map.get(key, "Other"))

        # PCA colored by family
        fam_order = [v for v in family_map.values()]
        fam_to_idx = {name: i for i, name in enumerate(fam_order)}
        colors = [fam_to_idx.get(x, len(fam_order)) for x in fam]
        cmap = plt.get_cmap("tab10")

        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        for name in fam_order:
            idx = [i for i, f in enumerate(fam) if f == name]
            if not idx:
                continue
            ax.scatter(
                pc1[idx],
                pc2[idx],
                s=60,
                alpha=0.85,
                edgecolors="black",
                linewidths=0.4,
                label=name,
                color=cmap(fam_to_idx[name] % 10),
            )
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_title("PCA 2D del corpus (coloreado por familia)")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best", fontsize=9)
        fig.tight_layout()
        _save_png_pdf(fig, main_dir / "pca_by_family")
        plt.close(fig)

        # PCA colored by cluster (if available)
        if path_clusters.exists():
            cl_df = pd.read_csv(path_clusters)
            cl_map = {row["scenario"]: int(row["cluster"]) for _i, row in cl_df.iterrows()}
            clusters = [cl_map.get(s, -1) for s in scen]
            uniq = sorted({c for c in clusters if c != -1})
            cmap2 = plt.get_cmap("tab10")

            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            for c in uniq:
                idx = [i for i, cc in enumerate(clusters) if cc == c]
                ax.scatter(
                    pc1[idx],
                    pc2[idx],
                    s=60,
                    alpha=0.85,
                    edgecolors="black",
                    linewidths=0.4,
                    label=f"Cluster {c}",
                    color=cmap2((c - 1) % 10),
                )
            ax.set_xlabel("PC1")
            ax.set_ylabel("PC2")
            ax.set_title("PCA 2D del corpus (coloreado por cluster Ward k=7)")
            ax.grid(True, alpha=0.25)
            ax.legend(loc="best", fontsize=9, ncol=2)
            fig.tight_layout()
            _save_png_pdf(fig, main_dir / "pca_by_cluster")
            plt.close(fig)

    # ---------------- Ablation plots ----------------
    if path_ablation.exists():
        df_ab = pd.read_csv(path_ablation)
        # stable order
        order = ["reduced_17", "core_23", "full_46"]
        df_ab["set"] = pd.Categorical(df_ab["set"], categories=order, ordered=True)
        df_ab = df_ab.sort_values("set")

        # % high pairs
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        ax.bar(df_ab["set"].astype(str), df_ab["pct_above"], color=["gray", "steelblue", "seagreen"], edgecolor="black")
        ax.set_ylabel(f"% pares con |r| ≥ {threshold}")
        ax.set_title("Ablación: redundancia (pares altos)")
        for i, v in enumerate(df_ab["pct_above"].tolist()):
            ax.text(i, v + 0.2, f"{v:.1f}%", ha="center", va="bottom", fontsize=9)
        ax.grid(True, axis="y", alpha=0.25)
        fig.tight_layout()
        _save_png_pdf(fig, main_dir / "ablation_pairs_high_bar")
        plt.close(fig)

        # silhouette
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        ax.bar(df_ab["set"].astype(str), df_ab["silhouette"], color=["gray", "steelblue", "seagreen"], edgecolor="black")
        ax.set_ylabel("Silhouette (Ward k=7)")
        ax.set_title("Ablación: estructura de clustering")
        for i, v in enumerate(df_ab["silhouette"].tolist()):
            ax.text(i, v + 0.01, f"{v:.3f}", ha="center", va="bottom", fontsize=9)
        ax.set_ylim(0, max(0.35, float(np.nanmax(df_ab["silhouette"])) + 0.05))
        ax.grid(True, axis="y", alpha=0.25)
        fig.tight_layout()
        _save_png_pdf(fig, main_dir / "ablation_silhouette_bar")
        plt.close(fig)

    # ---------------- Feature-feature core heatmap (paper copy) ----------------
    if path_ff_core.exists():
        ff = pd.read_csv(path_ff_core, index_col=0)
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        im = ax.imshow(ff.values, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(ff.columns)))
        ax.set_yticks(range(len(ff.columns)))
        ax.set_xticklabels(ff.columns, rotation=45, ha="right", fontsize=7)
        ax.set_yticklabels(ff.columns, fontsize=7)
        plt.colorbar(im, ax=ax, label="Pearson r (feature–feature)")
        ax.set_title("Correlación feature–feature (core 23)")
        fig.tight_layout()
        _save_png_pdf(fig, main_dir / "heatmap_feature_feature_core")
        plt.close(fig)

    # ---------------- Outputs heatmap (paper copy) ----------------
    if path_outputs.exists():
        out_df = pd.read_csv(path_outputs)
        if "scenario" in out_df.columns:
            out_df = out_df.set_index("scenario")
        # Keep only numeric columns
        out_num = out_df.select_dtypes(include=[np.number])
        if len(out_num.columns) >= 2 and len(out_num) >= 3:
            R_out = out_num.T.corr(method="pearson").values
            scen_out = out_num.index.tolist()
            fig, ax = plt.subplots(1, 1, figsize=(10, 8))
            im = ax.imshow(R_out, cmap="RdBu_r", vmin=-1, vmax=1)
            ax.set_xticks(range(len(scen_out)))
            ax.set_yticks(range(len(scen_out)))
            ax.set_xticklabels(scen_out, rotation=45, ha="right", fontsize=6)
            ax.set_yticklabels(scen_out, fontsize=6)
            plt.colorbar(im, ax=ax, label="Pearson r (outputs)")
            ax.set_title("Correlación entre escenarios en output-space (Pearson)")
            fig.tight_layout()
            _save_png_pdf(fig, supp_dir / "heatmap_pearson_outputs_paper")
            plt.close(fig)

    print(f"Written paper figures to {figures_paper_dir}")
    return True


def _parse_contact_times_histogram(path: Path) -> tuple[float, float, int]:
    """
    Parsea ContactTimesReport de The ONE en formato:
      <duration_seconds> <count>
    Devuelve:
      (contact_time_mean_s, total_encounters, valid_rows)
    """
    total_count = 0.0
    weighted_sum = 0.0
    valid_rows = 0
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            duration_s = float(parts[0])
            count = float(parts[1])
        except (TypeError, ValueError):
            continue
        if np.isnan(duration_s) or np.isnan(count):
            continue
        if count < 0:
            continue
        weighted_sum += duration_s * count
        total_count += count
        valid_rows += 1
    if total_count <= 0:
        return (np.nan, 0.0, valid_rows)
    return (weighted_sum / total_count, total_count, valid_rows)


def _parse_distribution_report(path: Path) -> tuple[list[tuple[float, int]], int]:
    """
    Parsea reportes de distribución de The ONE (formato 'value count').
    Devuelve:
      - lista de tuplas (value, count)
      - número de filas válidas
    """
    rows: list[tuple[float, int]] = []
    valid_rows = 0
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            value = float(parts[0])
            count = int(float(parts[1]))
        except (TypeError, ValueError):
            continue
        if count < 0:
            continue
        rows.append((value, count))
        valid_rows += 1
    return rows, valid_rows


def _weighted_mean_from_distribution(rows: list[tuple[float, int]]) -> float:
    total = sum(c for _, c in rows)
    if total <= 0:
        return np.nan
    return float(sum(v * c for v, c in rows) / total)


def _expand_distribution_values(rows: list[tuple[float, int]], max_expand: int = 200000) -> list[float]:
    """
    Expande una distribución (value,count) a lista de valores repetidos.
    Limita tamaño para evitar explosión.
    """
    out: list[float] = []
    n = 0
    for v, c in rows:
        reps = max(0, int(c))
        if reps == 0:
            continue
        if n + reps > max_expand:
            reps = max(0, max_expand - n)
        out.extend([float(v)] * reps)
        n += reps
        if n >= max_expand:
            break
    return out


def _brandes_betweenness_undirected(adj: dict[int, set[int]]) -> dict[int, float]:
    """
    Betweenness centrality no normalizada (Brandes) para grafo no dirigido.
    """
    nodes = list(adj.keys())
    bc = {v: 0.0 for v in nodes}
    for s in nodes:
        stack: list[int] = []
        pred: dict[int, list[int]] = {w: [] for w in nodes}
        sigma: dict[int, float] = {w: 0.0 for w in nodes}
        sigma[s] = 1.0
        dist: dict[int, int] = {w: -1 for w in nodes}
        dist[s] = 0
        q = [s]
        while q:
            v = q.pop(0)
            stack.append(v)
            for w in adj.get(v, set()):
                if dist[w] < 0:
                    q.append(w)
                    dist[w] = dist[v] + 1
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta: dict[int, float] = {w: 0.0 for w in nodes}
        while stack:
            w = stack.pop()
            for v in pred[w]:
                if sigma[w] > 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                bc[w] += delta[w]
    # Grafo no dirigido: dividir entre 2
    for v in bc:
        bc[v] /= 2.0
    return bc


def _parse_connectivity_one_report(path: Path, window_s: float = 3600.0) -> dict[str, Any]:
    """
    Parsea ConnectivityONEReport:
      "<time> CONN <a> <b> up|down"
    Devuelve métricas por escenario para indirectas tipo Diego.
    """
    import re

    line_re = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s+CONN\s+(\d+)\s+(\d+)\s+(up|down)\s*$", re.I)
    active: dict[tuple[int, int], float] = {}
    # métricas base
    encounter_events = 0
    contact_time_sum = 0.0
    intercontact_sum = 0.0
    intercontact_n = 0
    last_down: dict[tuple[int, int], float] = {}
    node_encounters: dict[int, int] = defaultdict(int)
    node_neighbors: dict[int, set[int]] = defaultdict(set)
    all_nodes: set[int] = set()
    static_adj: dict[int, set[int]] = defaultdict(set)
    window_edges: dict[int, set[tuple[int, int]]] = defaultdict(set)

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = line_re.match(raw.strip())
        if not m:
            continue
        t = float(m.group(1))
        a = int(m.group(2))
        b = int(m.group(3))
        state = m.group(4).lower()
        if a == b:
            continue
        u, v = (a, b) if a < b else (b, a)
        pair = (u, v)
        all_nodes.add(u)
        all_nodes.add(v)

        if state == "up":
            encounter_events += 1
            node_encounters[u] += 1
            node_encounters[v] += 1
            node_neighbors[u].add(v)
            node_neighbors[v].add(u)
            static_adj[u].add(v)
            static_adj[v].add(u)
            win = int(t // window_s)
            window_edges[win].add(pair)
            if pair in last_down and t >= last_down[pair]:
                intercontact_sum += (t - last_down[pair])
                intercontact_n += 1
            active[pair] = t
        elif state == "down":
            t0 = active.pop(pair, None)
            if t0 is not None and t >= t0:
                contact_time_sum += (t - t0)
            last_down[pair] = t

    # cerrar contactos abiertos al final con último timestamp observado si hay
    # (aquí no tenemos fin de simulación seguro; se omiten para evitar sesgo fuerte).

    # asegurar que nodos sin vecinos estén en adj
    for n in all_nodes:
        static_adj.setdefault(n, set())

    # betweenness global
    if all_nodes:
        bc = _brandes_betweenness_undirected(static_adj)
        betweenness_mean = float(np.mean(list(bc.values()))) if bc else np.nan
    else:
        bc = {}
        betweenness_mean = np.nan

    # centralidad por ventana
    win_means: list[float] = []
    for _w, edges in sorted(window_edges.items()):
        nodes_w: set[int] = set()
        for e in edges:
            nodes_w.update(e)
        if not nodes_w:
            continue
        adj_w: dict[int, set[int]] = {n: set() for n in nodes_w}
        for u, v in edges:
            adj_w[u].add(v)
            adj_w[v].add(u)
        bc_w = _brandes_betweenness_undirected(adj_w)
        if bc_w:
            win_means.append(float(np.mean(list(bc_w.values()))))
    window_centrality_mean = float(np.mean(win_means)) if win_means else np.nan

    n_nodes = len(all_nodes)
    if n_nodes > 1:
        ratio_contact_nodes = float(np.mean([len(node_neighbors.get(n, set())) / (n_nodes - 1) for n in all_nodes]))
        unique_ratios = sorted([len(node_neighbors.get(n, set())) / (n_nodes - 1) for n in all_nodes], reverse=True)
    else:
        ratio_contact_nodes = np.nan
        unique_ratios = []

    enc_values = sorted([node_encounters.get(n, 0) for n in all_nodes], reverse=True)
    k_top = max(1, int(np.ceil(0.1 * n_nodes))) if n_nodes else 0
    if k_top > 0 and enc_values:
        encounters_top10_mean = float(np.mean(enc_values[:k_top]))
        total_node_enc = float(sum(enc_values))
        sociability_top10_mean = float(np.mean([(v / total_node_enc) if total_node_enc > 0 else np.nan for v in enc_values[:k_top]]))
    else:
        encounters_top10_mean = np.nan
        sociability_top10_mean = np.nan

    if unique_ratios and k_top > 0:
        popularity_top10_ratio = float(np.mean(unique_ratios[:k_top]))
    else:
        popularity_top10_ratio = np.nan

    contact_time_mean = (contact_time_sum / encounter_events) if encounter_events > 0 else np.nan
    inter_contact_time_mean = (intercontact_sum / intercontact_n) if intercontact_n > 0 else np.nan

    return {
        "n_nodes_in_trace": n_nodes,
        "total_encounters": float(encounter_events),
        "contact_time_mean_s": float(contact_time_mean) if not np.isnan(contact_time_mean) else np.nan,
        "inter_contact_time_mean_s": float(inter_contact_time_mean) if not np.isnan(inter_contact_time_mean) else np.nan,
        "betweenness_centrality": betweenness_mean,
        "ratio_contact_nodes": ratio_contact_nodes,
        "popularity_top10_ratio": popularity_top10_ratio,
        "window_centrality_mean": window_centrality_mean,
        "encounters_top10_mean": encounters_top10_mean,
        "sociability_top10_mean": sociability_top10_mean,
    }


def run_phase_indirects(out_dir: Path, reports_dir: Path, scenario_paths: list[Path] | None = None) -> bool:
    """
    Calcula indirectas tipo Diego.
    Prioriza trazas ricas (ConnectivityONEReport) y usa fallback a reportes agregados
    (ContactTimes/InterContact/TotalEncounters/UniqueEncounters) cuando falten.
    """
    out_dir = Path(out_dir)
    reports_dir = Path(reports_dir)
    data_dir = out_dir / "data"
    reports_out_dir = out_dir / "reports"
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_out_dir.mkdir(parents=True, exist_ok=True)

    if not reports_dir.exists():
        print(f"Reports directory not found: {reports_dir}")
        return False

    # Map escenario -> endTime y n_hosts desde settings del corpus activo
    end_time_by_scenario: dict[str, float] = {}
    n_hosts_by_scenario: dict[str, int] = {}
    if scenario_paths:
        for p in scenario_paths:
            try:
                d = load_settings(p)
                sname = d.get("Scenario.name", p.stem)
                end_time_by_scenario[sname] = _get_float(d, "Scenario.endTime", np.nan)
                # Reusar extractor base para N
                vec = settings_to_reportable_features(d)
                n_hosts_by_scenario[sname] = int(vec.get("N", 0))
            except Exception:
                continue

    contact_files = {p.stem.replace("_ContactTimesReport", ""): p for p in sorted(reports_dir.glob("*_ContactTimesReport.txt"))}
    intercontact_files = {p.stem.replace("_InterContactTimesReport", ""): p for p in sorted(reports_dir.glob("*_InterContactTimesReport.txt"))}
    totalenc_files = {p.stem.replace("_TotalEncountersReport", ""): p for p in sorted(reports_dir.glob("*_TotalEncountersReport.txt"))}
    uniqueenc_files = {p.stem.replace("_UniqueEncountersReport", ""): p for p in sorted(reports_dir.glob("*_UniqueEncountersReport.txt"))}
    conn_files = {p.stem.replace("_ConnectivityONEReport", ""): p for p in sorted(reports_dir.glob("*_ConnectivityONEReport.txt"))}

    # Universe de escenarios del corpus activo (evitar stale reports)
    scenarios_active = sorted(end_time_by_scenario.keys()) if end_time_by_scenario else sorted(set(contact_files.keys()) | set(conn_files.keys()))
    if not scenarios_active:
        print("No active scenarios resolved for indirects phase.")
        return False

    rows: list[dict[str, Any]] = []
    n_from_conn = 0
    n_from_agg = 0
    for scenario in scenarios_active:
        end_time_s = end_time_by_scenario.get(scenario, np.nan)
        n_hosts = n_hosts_by_scenario.get(scenario, 0)

        # Defaults
        contact_time_mean_s = np.nan
        inter_contact_time_mean_s = np.nan
        total_encounters = np.nan
        betweenness_centrality = np.nan
        ratio_contact_nodes = np.nan
        popularity_top10_ratio = np.nan
        window_centrality_mean = np.nan
        encounters_top10_mean = np.nan
        sociability_top10_mean = np.nan
        contact_hist_rows = 0
        intercontact_hist_rows = 0
        trace_nodes = np.nan
        availability_note = ""

        if scenario in conn_files:
            met = _parse_connectivity_one_report(conn_files[scenario], window_s=3600.0)
            contact_time_mean_s = met["contact_time_mean_s"]
            inter_contact_time_mean_s = met["inter_contact_time_mean_s"]
            total_encounters = met["total_encounters"]
            betweenness_centrality = met["betweenness_centrality"]
            ratio_contact_nodes = met["ratio_contact_nodes"]
            popularity_top10_ratio = met["popularity_top10_ratio"]
            window_centrality_mean = met["window_centrality_mean"]
            encounters_top10_mean = met["encounters_top10_mean"]
            sociability_top10_mean = met["sociability_top10_mean"]
            trace_nodes = met["n_nodes_in_trace"]
            n_from_conn += 1
            availability_note = "Indirectas calculadas desde ConnectivityONEReport (traza por evento)."
        else:
            # Fallback agregado
            if scenario in contact_files:
                c_mean, c_total, c_rows = _parse_contact_times_histogram(contact_files[scenario])
                contact_time_mean_s = c_mean
                total_encounters = c_total
                contact_hist_rows = c_rows
            if scenario in intercontact_files:
                ic_rows, ic_valid = _parse_distribution_report(intercontact_files[scenario])
                inter_contact_time_mean_s = _weighted_mean_from_distribution(ic_rows)
                intercontact_hist_rows = ic_valid
            if scenario in totalenc_files:
                te_rows, _ = _parse_distribution_report(totalenc_files[scenario])
                # distribución encounters_por_nodo -> cantidad_nodos
                values = _expand_distribution_values(te_rows)
                if values:
                    total_encounters = float(np.sum(values) / 2.0)  # contar conexiones globales (no por nodo)
                    k_top = max(1, int(np.ceil(0.1 * len(values))))
                    top_vals = sorted(values, reverse=True)[:k_top]
                    encounters_top10_mean = float(np.mean(top_vals))
                    total_node_enc = float(np.sum(values))
                    sociability_top10_mean = float(np.mean([(v / total_node_enc) if total_node_enc > 0 else np.nan for v in top_vals]))
            if scenario in uniqueenc_files:
                ue_rows, _ = _parse_distribution_report(uniqueenc_files[scenario])  # promille, count_nodes
                ue_vals_promille = _expand_distribution_values(ue_rows)
                if ue_vals_promille:
                    ue_vals = [v / 1000.0 for v in ue_vals_promille]
                    ratio_contact_nodes = float(np.mean(ue_vals))
                    k_top = max(1, int(np.ceil(0.1 * len(ue_vals))))
                    popularity_top10_ratio = float(np.mean(sorted(ue_vals, reverse=True)[:k_top]))
            n_from_agg += 1
            availability_note = (
                "Fallback agregado (Contact/InterContact/Total/Unique reports). "
                "Centralidad real requiere ConnectivityONEReport."
            )

        if isinstance(end_time_s, (int, float)) and not np.isnan(end_time_s) and end_time_s > 0 and isinstance(total_encounters, (int, float)) and not np.isnan(total_encounters):
            contact_time_per_min = float(total_encounters / (end_time_s / 60.0)) if total_encounters > 0 else 0.0
            inter_contact_time_proxy_s = float(end_time_s / total_encounters) if total_encounters > 0 else np.nan
        else:
            contact_time_per_min = np.nan
            inter_contact_time_proxy_s = np.nan

        rows.append({
            "scenario": scenario,
            "N_hosts": n_hosts,
            "contact_time_mean_s": contact_time_mean_s,
            "inter_contact_time_mean_s": inter_contact_time_mean_s,
            "contact_time_per_min": contact_time_per_min,
            "total_encounters": total_encounters,
            "inter_contact_time_proxy_s": inter_contact_time_proxy_s,
            "betweenness_centrality": betweenness_centrality,
            "ratio_contact_nodes": ratio_contact_nodes,
            "popularity_top10_ratio": popularity_top10_ratio,
            "window_centrality_mean": window_centrality_mean,
            "encounters_top10_mean": encounters_top10_mean,
            "sociability_top10_mean": sociability_top10_mean,
            "availability_note": availability_note,
            "contact_hist_rows": contact_hist_rows,
            "intercontact_hist_rows": intercontact_hist_rows,
            "trace_nodes": trace_nodes,
            "scenario_end_time_s": end_time_s,
        })

    if pd is None:
        import csv
        out_csv = data_dir / "indirect_features_diego.csv"
        fieldnames = list(rows[0].keys()) if rows else []
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow(r)
    else:
        df = pd.DataFrame(rows).sort_values("scenario")
        out_csv = data_dir / "indirect_features_diego.csv"
        df.to_csv(out_csv, index=False)

    n_total = len(rows)
    n_with_contact = sum(1 for r in rows if isinstance(r["total_encounters"], (int, float)) and r["total_encounters"] > 0)
    n_with_endtime = sum(
        1 for r in rows
        if isinstance(r["scenario_end_time_s"], (int, float)) and not np.isnan(r["scenario_end_time_s"])
    )

    report_txt_lines = [
        "=== Indirectas tipo Diego (estado actual de datos) ===",
        f"Escenarios procesados: {n_total}",
        f"Calculados con ConnectivityONEReport: {n_from_conn}",
        f"Calculados con fallback agregado: {n_from_agg}",
        f"Con encounters > 0: {n_with_contact}",
        f"Con Scenario.endTime disponible: {n_with_endtime}",
        "",
        "Calculadas con datos actuales (cuando hay datos):",
        "  - contact_time_mean_s",
        "  - inter_contact_time_mean_s",
        "  - contact_time_per_min",
        "  - total_encounters",
        "  - inter_contact_time_proxy_s",
        "  - ratio_contact_nodes",
        "  - popularity_top10_ratio",
        "  - encounters_top10_mean",
        "  - sociability_top10_mean",
        "  - betweenness_centrality (solo con ConnectivityONEReport)",
        "  - window_centrality_mean (solo con ConnectivityONEReport)",
        "",
        "Para completar fase Diego17 real, ejecuta simulaciones con overrides:",
        "  scenarios/analysis/diego17_reports_overrides.txt",
        "Ejemplo:",
        "  python scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \\",
        "    --extra-settings scenarios/analysis/diego17_reports_overrides.txt",
        "",
        "Salida:",
        f"  - {out_csv}",
    ]
    report_txt = "\n".join(report_txt_lines)
    (reports_out_dir / "indirect_features_report.txt").write_text(report_txt, encoding="utf-8")

    report_md_lines = [
        "# Indirectas tipo Diego (estado actual de datos)",
        "",
        f"- Escenarios procesados: **{n_total}**",
        f"- Calculados con `ConnectivityONEReport`: **{n_from_conn}**",
        f"- Calculados con fallback agregado: **{n_from_agg}**",
        f"- Con encounters > 0: **{n_with_contact}**",
        f"- Con `Scenario.endTime` disponible: **{n_with_endtime}**",
        "",
        "## Calculadas con datos actuales (cuando hay datos)",
        "",
        "- `contact_time_mean_s`",
        "- `inter_contact_time_mean_s`",
        "- `contact_time_per_min`",
        "- `total_encounters`",
        "- `inter_contact_time_proxy_s`",
        "- `ratio_contact_nodes`",
        "- `popularity_top10_ratio`",
        "- `encounters_top10_mean`",
        "- `sociability_top10_mean`",
        "- `betweenness_centrality` (solo con `ConnectivityONEReport`)",
        "- `window_centrality_mean` (solo con `ConnectivityONEReport`)",
        "",
        "## Para completar Diego17 real",
        "",
        "Ejecuta simulaciones con overrides de reportes:",
        "",
        "```",
        "python scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \\",
        "  --extra-settings scenarios/analysis/diego17_reports_overrides.txt",
        "```",
        "",
        "Luego re-ejecuta `run_all_scenarios.py` y después `run_analysis.py --phase indirects`.",
        "",
        f"CSV: `{out_csv}`",
        "",
    ]
    (reports_out_dir / "indirect_features_report.md").write_text("\n".join(report_md_lines), encoding="utf-8")

    print(f"Written {out_csv}")
    print(f"Written {reports_out_dir / 'indirect_features_report.txt'} and indirect_features_report.md")
    return True


def _parse_feature_fichas_tecnicas(path: Path) -> dict[str, dict[str, str]]:
    """
    Parse de `scenarios/internal/*-feature_fichas_tecnicas*.md`.

    Devuelve dict:
      feature -> {
        "type": ...,
        "coverage": ...,
        "category": ...,
        "reason": ...
      }
    """
    import re

    txt = path.read_text(encoding="utf-8", errors="replace")
    features: dict[str, dict[str, str]] = {}

    current: dict[str, str] | None = None
    current_name: str | None = None

    for raw_line in txt.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        m_feat = re.match(r"^Feature:\s*`([^`]+)`\s*$", line)
        if m_feat:
            if current_name and current is not None:
                features[current_name] = current
            current_name = m_feat.group(1).strip()
            current = {}
            continue

        if current is None or current_name is None:
            continue

        if line.startswith("Tipo:"):
            current["type"] = line.split(":", 1)[1].strip()
        elif line.startswith("Cobertura:"):
            current["coverage"] = line.split(":", 1)[1].strip()
        elif line.startswith("Categoría metodológica:"):
            current["category"] = line.split(":", 1)[1].strip()
        elif line.startswith("Razón:"):
            current["reason"] = line.split(":", 1)[1].strip()

    if current_name and current is not None and current_name not in features:
        features[current_name] = current
    return features


def _parse_diversity_report(path: Path) -> dict[str, Any]:
    """
    Parsea `correlation_report.txt` o `correlation_core23_report.txt`.
    """
    import re

    txt = path.read_text(encoding="utf-8", errors="replace")
    # Escenarios y features: "Escenarios: n=60, features: d=46."
    m_nf = re.search(r"Escenarios:\s*n\s*=\s*(\d+)\s*,\s*features:\s*d\s*=\s*(\d+)", txt)
    if not m_nf:
        m_nf = re.search(r"Escenarios:\s*n\s*=\s*(\d+)\s*,\s*features:\s*d\s*=\s*(\d+)", txt.replace(" ", ""))
    n_scenarios = int(m_nf.group(1)) if m_nf else None
    n_features = int(m_nf.group(2)) if m_nf else None

    m_max = re.search(r"max\s*\|r\|\s*=\s*([0-9.]+)", txt)
    m_mean = re.search(r"media\s*\|r\|\s*=\s*([0-9.]+)", txt)
    max_abs_r = float(m_max.group(1)) if m_max else None
    mean_abs_r = float(m_mean.group(1)) if m_mean else None

    m_pairs = re.search(r"Pares con\s*\|r\|\s*>=\s*([0-9.]+):\s*(\d+)\s*\(([^%]+)%\)", txt)
    if m_pairs:
        thr = float(m_pairs.group(1))
        pairs = int(m_pairs.group(2))
        pct = float(m_pairs.group(3))
    else:
        # Fallback: "Pares con |r| >= 0.7: 46 (2.6%)"
        m_pairs2 = re.search(r"Pares con\s*\|r\|\s*>=\s*[0-9.]+:\s*(\d+)\s*\(([^%]+)%\)", txt)
        thr = 0.7
        pairs = int(m_pairs2.group(1)) if m_pairs2 else None
        pct = float(m_pairs2.group(2)) if m_pairs2 else None

    # min cosine distance: "Distancia coseno ... mín = 0.0620"
    m_mincos = re.search(r"Distancia coseno.*?mín\s*=\s*([0-9.]+)", txt, flags=re.S)
    min_cosine_distance = float(m_mincos.group(1)) if m_mincos else None

    # silhouette: "Silhouette (Ward...): 0.2929"
    m_sil = re.search(r"Silhouette.*?:\s*([0-9.]+)", txt)
    silhouette = float(m_sil.group(1)) if m_sil else None

    out = {
        "n_scenarios": n_scenarios,
        "n_features": n_features,
        "max_abs_r": max_abs_r,
        "mean_abs_r": mean_abs_r,
        "pairs_r_ge_threshold": pairs,
        "pct_pairs_r_ge_threshold": pct,
        "min_cosine_distance": min_cosine_distance,
        "silhouette": silhouette,
        "threshold": thr,
    }
    return out


def run_phase_tables_paper(out_dir: Path, threshold: float = 0.7) -> bool:
    """
    Genera tablas Markdown paper-ready dentro de:
      analysis/figures/paper/tables/
    Sin sobrescribir `analysis/figures/` (solo escribe .md en tablas/).
    """
    import re

    out_dir = Path(out_dir)
    figures_dir = out_dir / "figures"
    paper_dir = figures_dir / "paper"
    tables_dir = paper_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    # Inputs base
    data_dir = out_dir / "data"
    reports_dir = out_dir / "reports"

    corr_full_path = reports_dir / "correlation_report.txt"
    corr_core_path = reports_dir / "correlation_core23_report.txt"
    ablation_csv = data_dir / "ablation_metrics.csv"
    clusters_full_csv = data_dir / "cluster_assignments.csv"
    clusters_core_csv = data_dir / "cluster_assignments_core23.csv"  # existe en el snapshot

    features_norm_csv = data_dir / "features_normalized.csv"

    internal_dir = out_dir.parent / "internal"  # scenarios/internal
    fichas_path = internal_dir / "03-feature_fichas_tecnicas.md"

    # Basic checks
    required = [
        corr_full_path,
        corr_core_path,
        ablation_csv,
        clusters_full_csv,
        clusters_core_csv,
        features_norm_csv,
        fichas_path,
    ]
    missing = [p for p in required if not p.exists()]
    if missing:
        print("Missing inputs for tables_paper:")
        for p in missing:
            print(f"  - {p}")
        return False

    # Imports local to keep phase lean
    import pandas as pd

    # Feature metadata (core/extended)
    fichas = _parse_feature_fichas_tecnicas(fichas_path)

    # Features (all 46)
    Z_df = pd.read_csv(features_norm_csv, index_col=0)
    all_features = list(Z_df.columns)
    core_features = list(FEATURES_CORE_23)
    ext_features = [f for f in all_features if f not in set(core_features)]

    def _feature_row(feature_name: str) -> dict[str, str]:
        meta = fichas.get(feature_name, {})
        return {
            "feature": feature_name,
            "category": meta.get("category", "—"),
            "reason": meta.get("reason", "—"),
            "coverage": meta.get("coverage", "—"),
            "type": meta.get("type", "—"),
        }

    core_rows = [_feature_row(f) for f in core_features]
    ext_rows = [_feature_row(f) for f in ext_features]

    # Diversity metrics
    div_full = _parse_diversity_report(corr_full_path)
    div_core = _parse_diversity_report(corr_core_path)

    def _cluster_stats(path_csv: Path) -> dict[str, int]:
        df = pd.read_csv(path_csv)
        if "cluster" not in df.columns:
            return {"n_clusters": 0, "largest_cluster_size": 0}
        counts = df["cluster"].value_counts()
        return {
            "n_clusters": int(counts.shape[0]),
            "largest_cluster_size": int(counts.max()) if not counts.empty else 0,
        }

    cs_full = _cluster_stats(clusters_full_csv)
    cs_core = _cluster_stats(clusters_core_csv)

    # Ablation metrics
    df_ab = pd.read_csv(ablation_csv)
    order = ["reduced_17", "core_23", "full_46"]
    df_ab["set"] = pd.Categorical(df_ab["set"], categories=order, ordered=True)
    df_ab = df_ab.sort_values("set")

    # Families
    # ES file: Scenario-families-es.md, EN file: Scenario-families.md
    families_es_path = out_dir.parent / ".wiki-clone" / "05-corpus" / "Scenario-families-es.md"
    families_en_path = out_dir.parent / ".wiki-clone" / "05-corpus" / "Scenario-families.md"
    scenario_list_path = data_dir / "scenario_list.txt"
    if not families_es_path.exists() or not families_en_path.exists() or not scenario_list_path.exists():
        print("Missing families inputs for tables_paper:")
        for p in [families_es_path, families_en_path, scenario_list_path]:
            if not p.exists():
                print(f"  - {p}")
        return False

    scenario_list = scenario_list_path.read_text(encoding="utf-8", errors="replace").splitlines()
    scenario_list = [s.strip() for s in scenario_list if s.strip()]

    prefix_to_family = {
        "U": "Urban",
        "C": "Campus",
        "V": "Vehicles",
        "R": "Rural",
        "D": "Disaster",
        "S": "Social",
        "T": "Traffic",
    }

    fam_examples: dict[str, list[str]] = {k: [] for k in prefix_to_family.values()}
    for s in scenario_list:
        pref = s[:1]
        fam = prefix_to_family.get(pref)
        if fam is None:
            continue
        fam_examples[fam].append(s)

    for k in fam_examples:
        fam_examples[k] = fam_examples[k][:3]

    def _parse_families_md(path: Path) -> dict[str, dict[str, str]]:
        # Parse markdown table rows: | Urban | ... | 7 |
        out: dict[str, dict[str, str]] = {}
        txt = path.read_text(encoding="utf-8", errors="replace")
        for line in txt.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) != 3:
                continue
            family, goal, n_sc = cells
            family = family.strip()
            goal = goal.strip()
            out[family] = {"goal": goal, "n_scenarios": n_sc}
        return out

    fam_es = _parse_families_md(families_es_path)
    fam_en = _parse_families_md(families_en_path)

    def _families_table_rows(lang: str) -> list[dict[str, str]]:
        fam_map = fam_es if lang == "es" else fam_en
        # Ensure consistent family order
        fam_order = ["Urban", "Campus", "Vehicles", "Rural", "Disaster", "Social", "Traffic"]
        rows: list[dict[str, str]] = []
        for fam in fam_order:
            item = fam_map.get(fam)
            if not item:
                continue
            rows.append({
                "family": fam,
                "n_scenarios": item["n_scenarios"],
                "purpose": item["goal"],
                "dominant_traits": item["goal"],
                "example_scenarios": ", ".join(fam_examples.get(fam, [])),
            })
        return rows

    fam_rows_es = _families_table_rows("es")
    fam_rows_en = _families_table_rows("en")

    # ------------ Markdown writers ------------
    def _md_table(header: list[str], rows: list[list[Any]]) -> str:
        # rows already ordered
        sep = "|" + "|".join(["---"] * len(header)) + "|"
        out_lines = [
            "|" + "|".join(header) + "|",
            sep,
        ]
        for r in rows:
            out_lines.append("|" + "|".join(str(x).replace("\n", " ").replace("|", "/") for x in r) + "|")
        return "\n".join(out_lines)

    # ES: Core vs extended
    core_md_es = _md_table(
        ["feature", "categoría", "short_reason", "cobertura", "tipo"],
        [[r["feature"], r["category"], r["reason"], r["coverage"], r["type"]] for r in core_rows],
    )
    ext_md_es = _md_table(
        ["feature", "categoría", "short_reason", "cobertura", "tipo"],
        [[r["feature"], r["category"], r["reason"], r["coverage"], r["type"]] for r in ext_rows],
    )

    (tables_dir / "table_core_vs_extended_es.md").write_text(
        "\n".join([
            "# Core vs extended features (paper, ES)",
            "",
            "## Core",
            "",
            core_md_es,
            "",
            "## Extended",
            "",
            ext_md_es,
            "",
        ]),
        encoding="utf-8",
    )

    # EN: same content, different headings/labels only
    core_md_en = _md_table(
        ["feature", "category", "short_reason", "coverage", "type"],
        [[r["feature"], r["category"], r["reason"], r["coverage"], r["type"]] for r in core_rows],
    )
    ext_md_en = _md_table(
        ["feature", "category", "short_reason", "coverage", "type"],
        [[r["feature"], r["category"], r["reason"], r["coverage"], r["type"]] for r in ext_rows],
    )
    (tables_dir / "table_core_vs_extended_en.md").write_text(
        "\n".join([
            "# Core vs extended features (paper, EN)",
            "",
            "## Core",
            "",
            core_md_en,
            "",
            "## Extended",
            "",
            ext_md_en,
            "",
        ]),
        encoding="utf-8",
    )

    # Diversity metrics
    def _div_row(space: str, div: dict[str, Any], cs: dict[str, int]) -> list[Any]:
        return [
            space,
            div["n_scenarios"],
            div["n_features"],
            div["max_abs_r"],
            div["mean_abs_r"],
            div["pairs_r_ge_threshold"],
            div["pct_pairs_r_ge_threshold"],
            div["min_cosine_distance"],
            div["silhouette"],
            cs["n_clusters"],
            cs["largest_cluster_size"],
        ]

    div_table_es = _md_table(
        ["space", "n_scenarios", "n_features", "max_abs_r", "mean_abs_r", "pairs_r_ge_0.7", "pct_pairs_r_ge_0.7", "min_cosine_distance", "silhouette", "n_clusters", "largest_cluster_size"],
        [
            _div_row("full_46", div_full, cs_full),
            _div_row("core_23", div_core, cs_core),
        ],
    )
    (tables_dir / "table_diversity_metrics_es.md").write_text(
        "\n".join([
            "# Diversidad del corpus (paper, ES)",
            "",
            div_table_es,
            "",
        ]),
        encoding="utf-8",
    )

    div_table_en = _md_table(
        ["space", "n_scenarios", "n_features", "max_abs_r", "mean_abs_r", "pairs_r_ge_0.7", "pct_pairs_r_ge_0.7", "min_cosine_distance", "silhouette", "n_clusters", "largest_cluster_size"],
        [
            _div_row("full_46", div_full, cs_full),
            _div_row("core_23", div_core, cs_core),
        ],
    )
    (tables_dir / "table_diversity_metrics_en.md").write_text(
        "\n".join([
            "# Corpus diversity (paper, EN)",
            "",
            div_table_en,
            "",
        ]),
        encoding="utf-8",
    )

    # Ablation metrics
    ab_rows = []
    for _i, row in df_ab.iterrows():
        ab_rows.append([
            row["set"],
            int(row["n_features"]),
            float(row["max_abs_r"]),
            float(row["mean_abs_r"]),
            int(row["pairs_r_above_threshold"]),
            float(row["pct_above"]),
            float(row["silhouette"]) if not pd.isna(row["silhouette"]) else "—",
        ])
    ab_md = _md_table(
        ["feature_set", "n_features", "max_abs_r", "mean_abs_r", "pairs_r_ge_0.7", "pct_pairs_r_ge_0.7", "silhouette"],
        ab_rows,
    )
    (tables_dir / "table_ablation_metrics_es.md").write_text(
        "\n".join([
            "# Ablación (paper, ES)",
            "",
            ab_md,
            "",
        ]),
        encoding="utf-8",
    )
    (tables_dir / "table_ablation_metrics_en.md").write_text(
        "\n".join([
            "# Ablation (paper, EN)",
            "",
            ab_md,
            "",
        ]),
        encoding="utf-8",
    )

    # Families
    fam_md_es = _md_table(
        ["family", "n_scenarios", "purpose", "dominant_traits", "example_scenarios"],
        [[r["family"], r["n_scenarios"], r["purpose"], r["dominant_traits"], r["example_scenarios"]] for r in fam_rows_es],
    )
    (tables_dir / "table_families_es.md").write_text(
        "\n".join([
            "# Familias de escenarios (paper, ES)",
            "",
            fam_md_es,
            "",
        ]),
        encoding="utf-8",
    )

    fam_md_en = _md_table(
        ["family", "n_scenarios", "purpose", "dominant_traits", "example_scenarios"],
        [[r["family"], r["n_scenarios"], r["purpose"], r["dominant_traits"], r["example_scenarios"]] for r in fam_rows_en],
    )
    (tables_dir / "table_families_en.md").write_text(
        "\n".join([
            "# Scenario families (paper, EN)",
            "",
            fam_md_en,
            "",
        ]),
        encoding="utf-8",
    )

    # Optional README
    readme_path = tables_dir / "README.md"
    readme_path.write_text(
        "\n".join([
            "## Paper tables (Markdown)",
            "",
            "Generadas automáticamente por:",
            "",
            "```bash",
            "cd /home/raul/Documents/the-one/scenarios/analysis",
            "source /home/raul/Documents/the-one/venv/bin/activate",
            "python run_analysis.py --corpus corpus_v1 --phase tables_paper",
            "```",
            "",
            "Incluye (ES+EN):",
            "- Core vs extended features: `table_core_vs_extended_{es,en}.md`",
            "- Diversidad final: `table_diversity_metrics_{es,en}.md`",
            "- Ablación: `table_ablation_metrics_{es,en}.md`",
            "- Familias: `table_families_{es,en}.md`",
            "",
        ]),
        encoding="utf-8",
    )

    # QA: output count
    expected = [
        "table_core_vs_extended_es.md",
        "table_core_vs_extended_en.md",
        "table_diversity_metrics_es.md",
        "table_diversity_metrics_en.md",
        "table_ablation_metrics_es.md",
        "table_ablation_metrics_en.md",
        "table_families_es.md",
        "table_families_en.md",
    ]
    out_files = [f.name for f in tables_dir.glob("*.md")]
    missing = [f for f in expected if f not in out_files]
    if missing:
        print("tables_paper QA failed, missing:")
        for m in missing:
            print(f"  - {m}")
        return False

    print(f"Written paper tables to {tables_dir}")
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


def run_phase_output_metrics(out_dir: Path, reports_dir: Path, allowed_scenarios: set[str] | None = None) -> bool:
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
        if allowed_scenarios is not None and scenario not in allowed_scenarios:
            continue
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


def run_phase_results_actuales(
    out_dir: Path,
    corpus_name: str,
    threshold: float = 0.7,
    scenario_count: int | None = None,
) -> bool:
    """
    Genera/actualiza analysis/reports/RESULTADOS_ACTUALES.md a partir de los reportes
    generados en la misma ejecución (correlation_core23_report, correlation_report, etc.).

    Importante: no debe contener valores hardcodeados ni referencias a "corpus_dropped_v1"
    que dependan del estado histórico.
    """
    out_dir = Path(out_dir)
    reports_dir = out_dir / "reports"
    correlation_core_path = reports_dir / "correlation_core23_report.txt"
    correlation_full_path = reports_dir / "correlation_report.txt"
    ablation_path = reports_dir / "ablation_report.txt"

    if not correlation_core_path.exists() or not correlation_full_path.exists():
        print("Skip RESULTADOS_ACTUALES.md: missing correlation reports.")
        return False

    import re

    core_txt = correlation_core_path.read_text(encoding="utf-8", errors="replace")
    full_txt = correlation_full_path.read_text(encoding="utf-8", errors="replace")
    ablation_txt = ablation_path.read_text(encoding="utf-8", errors="replace") if ablation_path.exists() else ""

    # n de escenarios
    if scenario_count is None:
        m_core_n = re.search(r"Vectores Z_core:\s*n=(\d+)", core_txt)
        if m_core_n:
            scenario_count = int(m_core_n.group(1))
        else:
            m_full_n = re.search(r"Escenarios:\s*n=(\d+)", full_txt)
            scenario_count = int(m_full_n.group(1)) if m_full_n else None

    def _extract_float(pattern: str, text: str) -> float | None:
        m = re.search(pattern, text, flags=re.MULTILINE)
        if not m:
            return None
        return float(m.group(1))

    def _extract_int(pattern: str, text: str) -> int | None:
        m = re.search(pattern, text, flags=re.MULTILINE)
        if not m:
            return None
        return int(m.group(1))

    def _extract_pairs_ge(text: str) -> tuple[float | None, int | None, float | None]:
        # Devuelve (max_r, pares_ge, pct)
        max_r = _extract_float(r"max \|r\| = ([0-9.]+)", text)
        pairs = _extract_int(rf"Pares con \|r\| >= {re.escape(str(threshold))}:\s*([0-9]+)", text)
        pct = _extract_float(rf"Pares con \|r\| >= {re.escape(str(threshold))}:\s*[0-9]+\s*\(([0-9.]+)%\)", text)
        return max_r, pairs, pct

    max_core, pairs_core, pct_core = _extract_pairs_ge(core_txt)
    max_full, pairs_full, pct_full = _extract_pairs_ge(full_txt)

    # Métricas geométricas (desde correlation_report)
    cos_min = _extract_float(r"dist_coseno mínima\s*=\s*([0-9.]+)", full_txt)
    silhouette_full = _extract_float(r"Silhouette \(k=7 clusters, Ward\):\s*([0-9.]+)", full_txt)

    # Ablación (si existe)
    ablation_summary = ""
    if ablation_txt:
        # lines tipo:
        # core_23 (d=23): max|r|=..., mean|r|=..., pares |r|>=...=..., silhouette=...
        def _parse_set_line(set_name: str) -> dict[str, float | int] | None:
            m = re.search(
                rf"{re.escape(set_name)} \(d=\d+\): max\|r\|=([0-9.]+), mean\|r\|=([0-9.]+), pares \|r\|>={re.escape(str(threshold))}=([0-9]+)\s*\([0-9.]+%\), silhouette=([0-9.]+)",
                ablation_txt,
                flags=re.MULTILINE,
            )
            if not m:
                return None
            return {
                "max_r": float(m.group(1)),
                "mean_abs_r": float(m.group(2)),
                "pairs_ge": int(m.group(3)),
                "silhouette": float(m.group(4)),
            }

        reduced = _parse_set_line("reduced_17")
        core = _parse_set_line("core_23")
        full = _parse_set_line("full_46")
        if reduced or core or full:
            ablation_summary_lines = ["## Ablación (17 vs 23 vs 46, umbral |r|≥%.1f)" % threshold]
            if reduced:
                ablation_summary_lines.append(
                    f"- reduced_17: max|r|={reduced['max_r']:.4f}, pares≥={threshold}={reduced['pairs_ge']}, silhouette={reduced['silhouette']:.4f}"
                )
            if core:
                ablation_summary_lines.append(
                    f"- core_23: max|r|={core['max_r']:.4f}, pares≥={threshold}={core['pairs_ge']}, silhouette={core['silhouette']:.4f}"
                )
            if full:
                ablation_summary_lines.append(
                    f"- full_46: max|r|={full['max_r']:.4f}, pares≥={threshold}={full['pairs_ge']}, silhouette={full['silhouette']:.4f}"
                )
            ablation_summary = "\n".join(ablation_summary_lines)

    scenario_count_str = str(scenario_count) if scenario_count is not None else "?"
    total_pairs = int(scenario_count * (scenario_count - 1) / 2) if scenario_count is not None else None

    pairs_core_display = f"{pairs_core}" if pairs_core is not None else "—"
    pct_core_display = f" ({pct_core:.1f}%)" if pct_core is not None else ""

    pairs_full_display = f"{pairs_full}" if pairs_full is not None else "—"
    pct_full_display = f" ({pct_full:.1f}%)" if pct_full is not None else ""

    lines = [
        "# Resultados actuales del corpus (referencia única)",
        "",
        f"**Corpus:** {scenario_count_str} escenarios en `{corpus_name}/`.",
        f"**Umbral |r|:** {threshold}",
        "---",
            "## Métricas en espacio CORE (23 features)",
        f"| Métrica | Valor |",
        "|---|---|",
        f"| max |r| | {max_core if max_core is not None else '—'} |",
        f"| Pares con |r| ≥ {threshold} | {pairs_core_display}{pct_core_display} |",
        "",
    ]

    if total_pairs is not None:
        lines.append(f"Total pares (i<k): {total_pairs}")

    lines.extend(
        [
            "---",
            "## Métricas en espacio completo (46 features)",
            f"| Métrica | Valor |",
            "|---|---|",
            f"| max |r| | {max_full if max_full is not None else '—'} |",
            f"| Pares con |r| ≥ {threshold} | {pairs_full_display}{pct_full_display} |",
            "",
        ]
    )

    if cos_min is not None:
        lines.append(f"Distancia coseno mínima (geom): {cos_min:.4f}")
    if silhouette_full is not None:
        lines.append(f"Silhouette (Ward k=7): {silhouette_full:.4f}")

    lines.extend(
        [
            "---",
            "## Ablación y validación de correlación",
        ]
    )
    if ablation_summary:
        lines.append(ablation_summary)

    # Lista de informes (fija: no depende de datos)
    lines.extend(
        [
            "",
            "## Informes en este directorio (`reports/`)",
            "",
            "| Informe | Contenido |",
            "|---|---|",
            "| [correlation_core23_report.txt](correlation_core23_report.txt) | Pares con |r|≥umbral en core 23 |",
            "| [correlation_report.txt](correlation_report.txt) | Correlación en espacio completo (46 features) |",
            "| [ablation_report.txt](ablation_report.txt) | Ablación 17 vs 23 vs 46 |",
            "| [multiple_comparisons_report.txt](multiple_comparisons_report.txt) | FDR y Bonferroni |",
            "| [features_report.md](features_report.md) / [features_report.txt](features_report.txt) | Features usados / descartados |",
            "| [feature_feature_correlation_report.txt](feature_feature_correlation_report.txt) | Correlación feature–feature (core 23) |",
        ]
    )

    report_path = reports_dir / "RESULTADOS_ACTUALES.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written {report_path}")
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
    ap.add_argument("--phase", type=str, default="features",
                    choices=("features", "features_report", "normalize", "correlation", "feature_correlation", "ablation", "figures", "figures_paper", "tables_paper", "indirects", "output_metrics", "outputs", "all"),
                    help="Fase: features, normalize, correlation, feature_correlation (23×23), ablation (17 vs 23 vs 46), figures, figures_paper, tables_paper, indirects, output_metrics, outputs, all")
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

    scenario_paths = collect_scenario_files(corpus_dir)
    if not scenario_paths and args.phase in ("features", "features_report", "output_metrics", "outputs", "all"):
        print(f"No .settings found under {corpus_dir}")
        return 1
    if scenario_paths:
        print(f"Found {len(scenario_paths)} scenarios under {corpus_dir}")

    if args.phase == "features" or args.phase == "all":
        run_phase_features(scenario_paths, out_dir)
    if args.phase == "features_report" or args.phase == "all":
        if not scenario_paths:
            scenario_paths = collect_scenario_files(corpus_dir)
        if scenario_paths:
            run_phase_features_report(corpus_dir, out_dir, scenario_paths)
    if args.phase == "normalize" or args.phase == "all":
        if not run_phase_normalize(out_dir):
            return 1
    if args.phase == "correlation" or args.phase == "all":
        if not run_phase_correlation(out_dir, threshold=args.threshold, criterion_95=not args.strict, fdr_alpha=args.fdr_alpha):
            return 1
    if args.phase == "feature_correlation" or args.phase == "all":
        if not run_phase_feature_feature_correlation(out_dir):
            pass  # no fallar si falta features_core.csv
    if args.phase == "ablation" or args.phase == "all":
        if not run_phase_ablation(out_dir, threshold=args.threshold):
            pass
    if args.phase == "figures" or args.phase == "all":
        if not run_phase_figures(out_dir, threshold=args.threshold):
            return 1
    if args.phase == "figures_paper":
        if not run_phase_figures_paper(out_dir, threshold=args.threshold):
            return 1
    if args.phase == "tables_paper":
        if not run_phase_tables_paper(out_dir, threshold=args.threshold):
            return 1
    reports_dir = Path(args.reports_dir) if args.reports_dir else (base.parent.parent / "reports")
    if args.phase == "indirects":
        if not run_phase_indirects(out_dir, reports_dir, scenario_paths=scenario_paths):
            return 1
    if args.phase == "output_metrics" or args.phase == "all":
        allowed_scenarios = None
        if scenario_paths:
            allowed_scenarios = set()
            for p in scenario_paths:
                try:
                    s = load_settings(p)
                    allowed_scenarios.add(s.get("Scenario.name", p.stem))
                except Exception:
                    # Fallback: si un settings no parsea, al menos no bloqueamos el pipeline.
                    allowed_scenarios.add(p.stem)

        if not run_phase_output_metrics(out_dir, reports_dir, allowed_scenarios=allowed_scenarios):
            return 1
    if args.phase == "outputs":
        if not run_phase_outputs(out_dir, threshold=args.threshold):
            return 1
    if args.phase == "all":
        # Cálculo de indirectas (hasta donde permiten reportes agregados de contacto)
        run_phase_indirects(out_dir, reports_dir, scenario_paths=scenario_paths)

    # Documentación "siempre actual": genera/actualiza informes de referencia
    # a partir de los resultados calculados arriba.
    #
    # Excepción: --phase figures_paper está diseñado para no tocar artefactos
    # fuera de figures/paper/, así que saltamos el refresco automático.
    if args.phase not in ("figures_paper", "tables_paper", "indirects"):
        if scenario_paths:
            # features_report no depende de normalización/correlación; se refresca siempre que se ejecuta el script.
            run_phase_features_report(corpus_dir, out_dir, scenario_paths)

        # feature-feature correlation requiere features_core.csv (creada en normalize).
        # Si falta (por ejemplo al ejecutar una fase parcial), generamos lo necesario
        # para que el informe se actualice igualmente.
        core_path = out_dir / "data" / "features_core.csv"
        if core_path.exists():
            run_phase_feature_feature_correlation(out_dir)
        else:
            data_features_path = out_dir / "data" / "features.csv"
            if scenario_paths and not data_features_path.exists():
                # Necesario para poder hacer normalize
                run_phase_features(scenario_paths, out_dir)
            if scenario_paths:
                if run_phase_normalize(out_dir):
                    run_phase_feature_feature_correlation(out_dir)

        run_phase_results_actuales(
            out_dir,
            corpus_name=str(args.corpus),
            threshold=args.threshold,
            scenario_count=len(scenario_paths) if scenario_paths else None,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
