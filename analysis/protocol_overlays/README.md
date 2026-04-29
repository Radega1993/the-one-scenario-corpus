# Protocol overlays (routing)

Small settings fragments meant to be appended **after** the scenario file via `run_all_scenarios.py --extra-settings` (repeatable).

Each file sets `Group.router` and `Group1.router` … `Group12.router` so multi-group scenarios (up to 12 groups in this corpus) switch router consistently.

Example:

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --extra-settings scenarios/analysis/diego17_reports_overrides.txt \
  --extra-settings scenarios/analysis/protocol_overlays/router_prophet.txt
```

Files:

- `router_epidemic.txt` — Epidemic (baseline in many scenarios).
- `router_prophet.txt` — ProphetRouter.
- `router_sprayandwait.txt` — SprayAndWaitRouter (`nrofCopies = 6`).
- `router_maxprop.txt` — MaxPropRouter.

Tune router-specific parameters by editing these files or adding another overlay loaded last.
