# Overlays de simulación (`--extra-settings`)

Un **overlay** es un fichero `.txt` con fragmentos de configuración The ONE que se **fusionan encima** del `.settings` del escenario al lanzar `run_all_scenarios.py`. No modifica el corpus; solo añade o sustituye claves para esa ejecución.

Orden típico (cada `--extra-settings` se aplica después del anterior):

1. `routing_contact_reports_overrides.txt` — 7 reportes: MessageStats, tiempos de contacto, encuentros, ConnectivityONE.
2. `spatial_occupancy_reports_overrides.txt` — extiende a 9 reportes: NodePosition + SpatialOccupancy (requiere el preset 1 antes).
3. `created_messages_report_overrides.txt` — opcional: CreatedMessagesReport para auditoría de tiempos de creación.

Ejemplo desde la raíz del repo:

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt
```

Constantes en código: `lib.paths.ROUTING_CONTACT_REPORTS_OVERLAY`, `SPATIAL_OVERLAY`, `CREATED_MESSAGES_OVERLAY`.