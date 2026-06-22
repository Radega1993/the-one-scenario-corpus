# map_generation_recovery_plan_v1.md

## Recommended order
1. Plan without network:
```bash
python3 scenarios/setup/generate_map_space_saturation_v1.py --plan-only --target-total 800 --seed 42
```
2. Build synthetics offline:
```bash
python3 scenarios/setup/generate_map_space_saturation_v1.py --build --source synthetic --seed 42
```
3. Validate synthetics:
```bash
python3 scenarios/setup/validate_map_space_saturation_v1.py
```
4. Extract features from valid maps:
```bash
python3 scenarios/setup/extract_map_space_saturation_features.py
```
5. Acquire OSM in small batches:
```bash
python3 scenarios/setup/generate_map_space_saturation_v1.py --acquire-osm --max-downloads 25 --retry-transient --retry-attempts 2 --retry-backoff-seconds 30 --seed 42
```
6. Build OSM from cache:
```bash
python3 scenarios/setup/generate_map_space_saturation_v1.py --build --source osm --seed 42
```

## Saturation decision
Continue feature-space analysis with maps in `OK` / validation `PASS` even if some OSM downloads remain transient failures.

