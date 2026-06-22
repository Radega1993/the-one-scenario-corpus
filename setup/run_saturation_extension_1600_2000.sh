#!/usr/bin/env bash
# Extensión map_space_saturation_v1: 1200 → 1600 → 2000 + análisis de saturación.
# Tolerante a fallos: continúa tras errores parciales (OSM, build, FAIL validation).
# Reanudable: --from-phase=C salta fases ya completadas.
#
# Uso (desde la raíz del repo):
#   source venv/bin/activate
#   bash scenarios/setup/run_saturation_extension_1600_2000.sh
#   bash scenarios/setup/run_saturation_extension_1600_2000.sh --from-phase=E
#   bash scenarios/setup/run_saturation_extension_1600_2000.sh --skip-synth-rebuild
#
# Salida de reproducibilidad:
#   scenarios/analysis/data/map_space_saturation_extension_2000_run_manifest.json

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
if [[ -x "$REPO_ROOT/venv/bin/python" ]]; then
  PYTHON="${PYTHON:-$REPO_ROOT/venv/bin/python}"
elif [[ -x "$REPO_ROOT/scenarios/analysis/.venv/bin/python" ]]; then
  PYTHON="${PYTHON:-$REPO_ROOT/scenarios/analysis/.venv/bin/python}"
else
  PYTHON="${PYTHON:-python3}"
fi
GEN="$REPO_ROOT/scenarios/setup/generate_map_space_saturation_v1.py"
VALIDATE="$REPO_ROOT/scenarios/setup/validate_map_space_saturation_v1.py"
EXTRACT="$REPO_ROOT/scenarios/setup/extract_map_space_saturation_features.py"
ANALYZE="$REPO_ROOT/scenarios/setup/analyze_map_space_saturation_v1.py"
MAP_ROOT="$REPO_ROOT/scenarios/map_space_saturation_v1"
MANIFEST_JSON="$REPO_ROOT/scenarios/analysis/data/map_space_saturation_extension_2000_run_manifest.json"
LOG_DIR="$REPO_ROOT/scenarios/analysis/logs"
RUN_LOG="$LOG_DIR/map_space_saturation_extension_2000.log"

SEED="${SEED:-42}"
TARGET_TOTAL="${TARGET_TOTAL:-2000}"
FROM_PHASE="${FROM_PHASE:-A}"
SKIP_SYNTH_REBUILD=false
MAX_OSM_ROUNDS="${MAX_OSM_ROUNDS:-60}"
OSM_BATCH="${OSM_BATCH:-25}"

declare -A PHASE_STATUS=()
declare -A PHASE_EXIT=()
PIPELINE_EXIT=0
START_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for arg in "$@"; do
  case "$arg" in
    --skip-synth-rebuild) SKIP_SYNTH_REBUILD=true ;;
    --target-total=*) TARGET_TOTAL="${arg#*=}" ;;
    --from-phase=*) FROM_PHASE="${arg#*=}" ;;
    --seed=*) SEED="${arg#*=}" ;;
    -h|--help)
      cat <<'EOF'
Uso: run_saturation_extension_1600_2000.sh [opciones]

Opciones:
  --from-phase=A|B|C|D|E   Reanudar desde fase (A=plan, B=synth, C=osm, D=build, E=analysis)
  --skip-synth-rebuild     No regenerar sintéticos con --force
  --target-total=2000      Total de candidatos planificados
  --seed=42                Semilla global

Fases:
  A plan-only
  B build synthetic --force
  C acquire-osm + build osm (bucle tolerante a fallos)
  D build all
  E validate + extract + analyze + manifest

El pipeline NO aborta por FAIL de validación ni por rondas OSM fallidas.
EOF
      exit 0
      ;;
  esac
done

mkdir -p "$LOG_DIR"
: >"$RUN_LOG"

log() {
  local msg="[$(date -u +%H:%M:%S)] $*"
  echo "$msg" | tee -a "$RUN_LOG"
}

phase_ge() {
  local current="$1" start="$2"
  local -A order=([A]=1 [B]=2 [C]=3 [D]=4 [E]=5)
  [[ "${order[$current]:-99}" -ge "${order[$start]:-0}" ]]
}

run_phase() {
  local name="$1"
  shift
  if ! phase_ge "$name" "$FROM_PHASE"; then
    PHASE_STATUS["$name"]="skip"
    PHASE_EXIT["$name"]=0
    log ">> [$name] omitido (--from-phase=$FROM_PHASE)"
    return 0
  fi
  log ">> [$name] $*"
  set +e
  "$@" >>"$RUN_LOG" 2>&1
  local ec=$?
  PHASE_EXIT["$name"]=$ec
  if [[ $ec -eq 0 ]]; then
    PHASE_STATUS["$name"]="ok"
    log "   [$name] OK (exit 0)"
  else
    PHASE_STATUS["$name"]="fail"
    log "   [$name] FAIL (exit $ec) — continuando pipeline"
    PIPELINE_EXIT=1
  fi
  return 0
}

log "=== Saturación extensión 1600→2000 target_total=$TARGET_TOTAL seed=$SEED from_phase=$FROM_PHASE ==="
log "Python: $PYTHON"
log "Log: $RUN_LOG"

run_phase A "$PYTHON" "$GEN" --plan-only --target-total "$TARGET_TOTAL" --seed "$SEED"

if [[ "$SKIP_SYNTH_REBUILD" == "true" ]]; then
  PHASE_STATUS[B]="skip"
  PHASE_EXIT[B]=0
  log ">> [B] omitido (--skip-synth-rebuild)"
elif phase_ge B "$FROM_PHASE"; then
  run_phase B "$PYTHON" "$GEN" --build --source synthetic \
    --target-total "$TARGET_TOTAL" --seed "$SEED" --force
else
  PHASE_STATUS[B]="skip"
  PHASE_EXIT[B]=0
fi

if phase_ge C "$FROM_PHASE"; then
  log ">> [C] acquire-osm + build osm (max $MAX_OSM_ROUNDS rondas)"
  osm_round=0
  osm_stall=0
  prev_pending=-1
  while (( osm_round < MAX_OSM_ROUNDS )); do
    osm_round=$((osm_round + 1))
    pending="$(MAP_ROOT="$MAP_ROOT" "$PYTHON" - <<'PY'
import csv, os
from pathlib import Path
q = Path(os.environ["MAP_ROOT"]) / "osm_download_queue.csv"
if not q.is_file():
    print(0)
    raise SystemExit
rows = list(csv.DictReader(q.open()))
print(sum(1 for r in rows if r["status"] in ("PENDING", "FAILED_TRANSIENT")))
PY
)"
    if [[ "$pending" == "0" ]]; then
      log "   [C] cola OSM vacía"
      break
    fi
    if [[ "$pending" == "$prev_pending" ]]; then
      osm_stall=$((osm_stall + 1))
      if (( osm_stall >= 5 )); then
        log "   [C] sin progreso en cola ($osm_stall rondas) — siguiendo"
        break
      fi
    else
      osm_stall=0
    fi
    prev_pending="$pending"
    log "   [C] ronda $osm_round pending=$pending"
    set +e
    "$PYTHON" "$GEN" --acquire-osm --max-downloads "$OSM_BATCH" --retry-transient \
      --retry-attempts 2 --retry-backoff-seconds 30 --osm-pause 10 \
      --target-total "$TARGET_TOTAL" --seed "$SEED" >>"$RUN_LOG" 2>&1
    acq_ec=$?
    "$PYTHON" "$GEN" --build --source osm \
      --target-total "$TARGET_TOTAL" --seed "$SEED" >>"$RUN_LOG" 2>&1
    bld_ec=$?
    set -e
    if [[ $acq_ec -ne 0 || $bld_ec -ne 0 ]]; then
      log "   [C] ronda $osm_round acquire=$acq_ec build=$bld_ec (continuando)"
      PIPELINE_EXIT=1
    fi
  done
  PHASE_STATUS[C]="ok"
  PHASE_EXIT[C]=0
else
  PHASE_STATUS[C]="skip"
  PHASE_EXIT[C]=0
  log ">> [C] omitido (--from-phase=$FROM_PHASE)"
fi

run_phase D "$PYTHON" "$GEN" --build --source all \
  --target-total "$TARGET_TOTAL" --seed "$SEED"

if phase_ge E "$FROM_PHASE"; then
  run_phase E1 "$PYTHON" "$VALIDATE"
  run_phase E2 "$PYTHON" "$EXTRACT"
  run_phase E3 "$PYTHON" "$ANALYZE"
  if [[ "${PHASE_EXIT[E3]:-1}" -eq 0 ]]; then
    PHASE_STATUS[E]="ok"
    PHASE_EXIT[E]=0
  else
    PHASE_STATUS[E]="fail"
    PHASE_EXIT[E]="${PHASE_EXIT[E3]}"
    PIPELINE_EXIT=1
  fi
else
  PHASE_STATUS[E]="skip"
  PHASE_EXIT[E]=0
fi

END_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
REPO_ROOT="$REPO_ROOT" SEED="$SEED" TARGET_TOTAL="$TARGET_TOTAL" \
  START_TS="$START_TS" END_TS="$END_TS" PIPELINE_EXIT="$PIPELINE_EXIT" \
  RUN_LOG="$RUN_LOG" MANIFEST_JSON="$MANIFEST_JSON" \
  PHASE_A="${PHASE_STATUS[A]:-skip}" PHASE_B="${PHASE_STATUS[B]:-skip}" \
  PHASE_C="${PHASE_STATUS[C]:-skip}" PHASE_D="${PHASE_STATUS[D]:-skip}" \
  PHASE_E="${PHASE_STATUS[E]:-skip}" \
  "$PYTHON" - <<'PY'
import csv, json, os
from pathlib import Path

repo = Path(os.environ["REPO_ROOT"])
manifest_path = repo / "scenarios/map_space_saturation_v1/manifest_maps_all.csv"
val_path = repo / "scenarios/analysis/data/map_space_saturation_validation.csv"
decision_path = repo / "scenarios/analysis/data/map_space_saturation_decision.json"
out_path = Path(os.environ["MANIFEST_JSON"])

def count_manifest():
    if not manifest_path.is_file():
        return {}
    rows = list(csv.DictReader(manifest_path.open()))
    from collections import Counter
    st = Counter(r.get("generation_status", "") for r in rows)
    ok = sum(v for k, v in st.items() if k in ("OK", "SKIPPED_EXISTING_OK"))
    fail = sum(v for k, v in st.items() if str(k).startswith("FAIL"))
    return {"rows": len(rows), "ok_or_skipped": ok, "fail_build": fail, "by_status": dict(st)}

def count_validation():
    if not val_path.is_file():
        return {}
    rows = list(csv.DictReader(val_path.open()))
    from collections import Counter
    st = Counter(r.get("status", "") for r in rows)
    return {
        "rows": len(rows),
        "PASS": st.get("PASS", 0),
        "WARNING": st.get("WARNING", 0),
        "STRESS": st.get("STRESS", 0),
        "FAIL": st.get("FAIL", 0),
        "fail_fraction": round(st.get("FAIL", 0) / max(len(rows), 1), 4),
    }

decision = {}
if decision_path.is_file():
    decision = json.loads(decision_path.read_text())

doc = {
    "pipeline": "map_space_saturation_extension_1600_2000",
    "seed": int(os.environ["SEED"]),
    "target_total": int(os.environ["TARGET_TOTAL"]),
    "started_at": os.environ["START_TS"],
    "finished_at": os.environ["END_TS"],
    "pipeline_exit_code": int(os.environ["PIPELINE_EXIT"]),
    "fault_tolerant": True,
    "phases": {
        "A_plan": os.environ["PHASE_A"],
        "B_synth_rebuild": os.environ["PHASE_B"],
        "C_osm_loop": os.environ["PHASE_C"],
        "D_build_all": os.environ["PHASE_D"],
        "E_analysis": os.environ["PHASE_E"],
    },
    "manifest_generation": count_manifest(),
    "validation": count_validation(),
    "saturation_decision": {
        k: decision.get(k)
        for k in (
            "decision", "recommended_stop_batch", "stop_rule_mode",
            "extension_confirmed", "robustness_extension_confirmed",
            "decision_tier", "max_batch_evaluated", "max_generated",
            "max_valid_maps", "max_invalid_maps",
            "marginal_valid_maps_after_1200",
        )
    },
    "log_file": os.environ["RUN_LOG"],
    "reproducibility_note": (
        "Partial generation/validation failures are expected and recorded; "
        "saturation analysis uses only PASS/WARNING/STRESS maps. "
        "Re-run with --from-phase to resume without repeating completed steps."
    ),
}
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
print(json.dumps(doc["saturation_decision"], indent=2))
print(f"Run manifest: {out_path}")
PY

log ""
log "=== Resumen ==="
REPO_ROOT="$REPO_ROOT" "$PYTHON" - <<'PY'
import csv, json, os
from pathlib import Path
repo = Path(os.environ["REPO_ROOT"])
feat = repo / "scenarios/analysis/data/map_space_saturation_features.csv"
val = repo / "scenarios/analysis/data/map_space_saturation_validation.csv"
decision = repo / "scenarios/analysis/data/map_space_saturation_decision.json"
arch = repo / "scenarios/analysis/data/map_archetype_definitions_v1.csv"
declared = {r["archetype"] for r in csv.DictReader(arch.open()) if r.get("archetype")}
present = {r["archetype"] for r in csv.DictReader(feat.open()) if r.get("archetype")} if feat.is_file() else set()
val_rows = list(csv.DictReader(val.open())) if val.is_file() else []
print(f"Validation: PASS={sum(1 for r in val_rows if r.get('status')=='PASS')} "
      f"FAIL={sum(1 for r in val_rows if r.get('status')=='FAIL')} / {len(val_rows)}")
print(f"Archetypes: {len(present)}/{len(declared)}")
if decision.is_file():
    d = json.loads(decision.read_text())
    print(f"Decision: {d.get('decision')} @ batch {d.get('recommended_stop_batch')} "
          f"tier={d.get('decision_tier')} mode={d.get('stop_rule_mode')}")
PY

log "Manifest: $MANIFEST_JSON"
log "Pipeline exit: $PIPELINE_EXIT (0=análisis OK; 1=hubo fallos parciales tolerados)"
exit "$PIPELINE_EXIT"
