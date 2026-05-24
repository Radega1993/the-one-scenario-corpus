# the-one-scenario-corpus — Wiki Inicio

**Español** | [English](Home)

---

## En 2 Minutos

Este proyecto ofrece un corpus reproducible para investigación DTN/OppNets en The ONE, junto con un pipeline de análisis y documentación lista para paper.

Estado actual para publicación:

- **60 escenarios** en **7 familias**
- Análisis de diversidad en espacios **full-46** y **core-23**
- Freeze declarado como **baseline final optimizado** (publicable, no óptimo final)

---

## Snapshot Final (oficial)

| Métrica | Valor |
|------|--------|
| full-46 max \|r\| | `0.9377` |
| full-46 pares \|r\| >= 0,7 | `46/1770 (2,6%)` |
| full-46 coseno mínimo | `0.0620` |
| full-46 silhouette (Ward k=7) | `0.2929` |
| core-23 max \|r\| | `0.9829` |
| core-23 pares \|r\| >= 0,7 | `58/1770 (3,3%)` |
| core-23 silhouette (Ward k=7) | `0.2681` |
| feature-feature core | `mm_WDM <-> mm_Bus = 0.9393` |

Los números oficiales del freeze se mantienen en [Final-frozen-results-es](Final-frozen-results-es).

---

## Enfoque de Investigación

- Construir un conjunto de escenarios amplio para benchmark sin colapso por redundancia lineal.
- Mantener una metodología transparente (features, NaN/normalización, correlación, clustering, ablation).
- Garantizar trazabilidad desde los `.settings` hasta los artefactos y conclusiones.

---

## Navegación Rápida

### Visión del Proyecto
- [Research-goals-es](Research-goals-es)
- [Thesis-phases-es](Thesis-phases-es)
- [Contributions-es](Contributions-es)
- [Repository-structure-es](Repository-structure-es)

### Corpus
- [Corpus-overview-es](Corpus-overview-es)
- [Scenario-families-es](Scenario-families-es)
- [Corpus-versioning-es](Corpus-versioning-es)
- [Dropped-scenarios-evolution-es](Dropped-scenarios-evolution-es)
- [Scenario-catalog-es](Scenario-catalog-es)

### Metodología
- [Scenario-representation-es](Scenario-representation-es)
- [Core-vs-extended-features-es](Core-vs-extended-features-es)
- [Feature-selection-rationale-es](Feature-selection-rationale-es)
- [NaN-and-normalization-policy-es](NaN-and-normalization-policy-es)
- [Diversity-analysis-methodology-es](Diversity-analysis-methodology-es)
- [Marginal-test-es](Marginal-test-es)
- [Ablation-methodology-es](Ablation-methodology-es)
- [Methodological-limitations-es](Methodological-limitations-es)

### Resultados
- [Results-overview-es](Results-overview-es)
- [Final-frozen-results-es](Final-frozen-results-es)
- [Optimization-history-es](Optimization-history-es)
- [Feature-feature-analysis-es](Feature-feature-analysis-es)
- [Clustering-analysis-es](Clustering-analysis-es)
- [Output-space-analysis-es](Output-space-analysis-es)
- [Figures-es](Figures-es)

### Reproducibilidad
- [Quickstart-es](Quickstart-es)
- [Running-analysis-pipeline-es](Running-analysis-pipeline-es)
- [Generating-figures-es](Generating-figures-es)
- [Using-corpus-in-the-one-es](Using-corpus-in-the-one-es)
- [Data-and-artifacts-es](Data-and-artifacts-es)

