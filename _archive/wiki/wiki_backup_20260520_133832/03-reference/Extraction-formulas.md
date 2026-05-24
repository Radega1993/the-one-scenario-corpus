# Extraction formulas

Purpose: summarize key descriptor formulas used in the pipeline.

## Core examples

- `world_area = Wx * Wy`
- `aspect_ratio = min(Wx, Wy) / max(Wx, Wy)`
- `event_interval_mean = mean(Events*.interval)`
- `event_size_mean = mean(Events*.size)`

## Notes

- Full implementation is in `analysis/run_analysis.py`.
- Normalization policy is documented in [NaN-and-normalization-policy](NaN-and-normalization-policy).
