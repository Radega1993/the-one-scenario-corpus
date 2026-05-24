# Marginal test

Purpose: explain feature-wise add/remove evaluation logic.

## What it checks

A marginal test evaluates whether adding or removing one descriptor dimension changes diversity indicators in a meaningful way.

## Why it is useful

- Detects weakly informative or highly conditional dimensions.
- Supports, but does not replace, semantic and methodological judgment.

## Output interpretation

Changes are read in context of:

- pairs with high \|r\|,
- silhouette behavior,
- feature coverage and conditionality.
