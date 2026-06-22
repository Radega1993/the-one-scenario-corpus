#!/usr/bin/env bash
# Script temporal: descarga OSM en tandas y construye WKT hasta agotar la cola.
# Uso (desde la raíz del repo):
#   bash scenarios/setup/tmp_run_osm_until_ok.sh
#
# Requiere red (Overpass). Usa el venv con osmnx.
# Eliminar cuando ya no haga falta.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="${PYTHON:-$REPO_ROOT/scenarios/analysis/.venv/bin/python}"
GEN="$REPO_ROOT/scenarios/setup/generate_map_space_saturation_v1.py"
MAP_ROOT="$REPO_ROOT/scenarios/map_space_saturation_v1"
QUEUE="$MAP_ROOT/osm_download_queue.csv"
MANIFEST="$MAP_ROOT/manifest_maps_all.csv"

MAX_DOWNLOADS="${MAX_DOWNLOADS:-25}"
OSM_PAUSE="${OSM_PAUSE:-10}"
RETRY_ATTEMPTS="${RETRY_ATTEMPTS:-2}"
RETRY_BACKOFF="${RETRY_BACKOFF:-30}"
SEED="${SEED:-42}"
MAX_ROUNDS="${MAX_ROUNDS:-80}"
STALL_ROUNDS="${STALL_ROUNDS:-5}"

if [[ ! -x "$PYTHON" ]]; then
  echo "No se encuentra el venv: $PYTHON" >&2
  exit 1
fi

count_queue_pending() {
  "$PYTHON" - <<'PY'
import csv
from collections import Counter
from pathlib import Path
import os
q = Path(os.environ["QUEUE"])
rows = list(csv.DictReader(q.open()))
c = Counter(r["status"] for r in rows)
pending = c.get("PENDING", 0) + c.get("FAILED_TRANSIENT", 0)
downloaded = c.get("DOWNLOADED", 0)
print(f"{pending}\t{downloaded}\t{c.get('FAILED_PERMANENT', 0)}")
PY
}

count_osm_ok() {
  "$PYTHON" - <<'PY'
import csv
from pathlib import Path
import os
m = Path(os.environ["MANIFEST"])
rows = list(csv.DictReader(m.open()))
osm = [r for r in rows if r.get("source_type") == "osm"]
ok = sum(1 for r in osm if r.get("generation_status") in ("OK", "SKIPPED_EXISTING_OK"))
fail_dl = sum(1 for r in osm if r.get("generation_status") == "FAIL_DOWNLOAD_TRANSIENT")
fail_build = sum(1 for r in osm if r.get("generation_status") == "FAIL_BUILD_OSM")
print(f"{ok}\t{fail_dl}\t{fail_build}\t{len(osm)}")
PY
}

export QUEUE MANIFEST

echo "=== tmp_run_osm_until_ok ==="
echo "Repo: $REPO_ROOT"
echo "max_downloads=$MAX_DOWNLOADS  max_rounds=$MAX_ROUNDS  stall_rounds=$STALL_ROUNDS"
echo ""

round=0
stall=0
prev_ok=-1

while (( round < MAX_ROUNDS )); do
  round=$((round + 1))
  read -r q_pending q_downloaded q_permanent <<< "$(count_queue_pending)"
  read -r osm_ok fail_dl fail_build osm_total <<< "$(count_osm_ok)"

  echo "--- Ronda $round/$MAX_ROUNDS ---"
  echo "  Cola: pending/transient=$q_pending  downloaded=$q_downloaded  permanent=$q_permanent"
  echo "  Manifest OSM: OK=$osm_ok  FAIL_DOWNLOAD_TRANSIENT=$fail_dl  FAIL_BUILD_OSM=$fail_build  total=$osm_total"

  if (( q_pending == 0 )); then
    echo "Cola OSM sin PENDING/FAILED_TRANSIENT. Fin."
    break
  fi

  echo ">> acquire-osm (max $MAX_DOWNLOADS)"
  "$PYTHON" "$GEN" \
    --acquire-osm \
    --max-downloads "$MAX_DOWNLOADS" \
    --retry-transient \
    --retry-attempts "$RETRY_ATTEMPTS" \
    --retry-backoff-seconds "$RETRY_BACKOFF" \
    --osm-pause "$OSM_PAUSE" \
    --seed "$SEED"

  echo ">> build --source osm"
  "$PYTHON" "$GEN" \
    --build \
    --source osm \
    --seed "$SEED"

  read -r osm_ok fail_dl fail_build osm_total <<< "$(count_osm_ok)"
  echo "  Tras build: OSM OK=$osm_ok  FAIL_DOWNLOAD_TRANSIENT=$fail_dl  FAIL_BUILD_OSM=$fail_build"

  if (( osm_ok == prev_ok )); then
    stall=$((stall + 1))
    echo "  Sin progreso en OK ($stall/$STALL_ROUNDS)"
    if (( stall >= STALL_ROUNDS )); then
      echo "Demasiadas rondas sin progreso (Overpass inestable?). Parando."
      break
    fi
  else
    stall=0
  fi
  prev_ok=$osm_ok
  echo ""
done

echo ""
echo "=== Resumen final ==="
read -r q_pending q_downloaded q_permanent <<< "$(count_queue_pending)"
read -r osm_ok fail_dl fail_build osm_total <<< "$(count_osm_ok)"
echo "Cola: pending/transient=$q_pending  downloaded=$q_downloaded"
echo "OSM manifest: OK=$osm_ok / $osm_total  (FAIL_BUILD_OSM=$fail_build)"

echo ""
echo ">> validate"
"$PYTHON" "$REPO_ROOT/scenarios/setup/validate_map_space_saturation_v1.py" || true

echo ""
echo "Listo. Si quedan FAIL_DOWNLOAD_TRANSIENT, reintenta más tarde o sube STALL_ROUNDS."
echo "Los FAIL_BUILD_OSM y sintéticos degenerados no se arreglan con este script."
