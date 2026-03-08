# the-one-scenario-corpus — Wiki Inicio

**Español** | [English](Home)

---

## Resumen

**the-one-scenario-corpus** es un **corpus de escenarios y pipeline de análisis** para el simulador [The ONE](https://akeranen.github.io/the-one/) (Opportunistic Network Environment). Proporciona:

- **70 escenarios de simulación** (ficheros `.settings`) organizados en 7 familias
- **Extracción de features, análisis de correlación, clustering y validación basada en outputs**
- **Un dashboard interactivo** para explorar resultados

El objetivo es ofrecer un **benchmark reproducible** con **escenarios diversos y no redundantes** para evaluar protocolos de enrutamiento en redes oportunistas (DTN/OppNets)—por ejemplo para tesis o artículos.

---

## Por qué existe este corpus

- Los protocolos de enrutamiento deben probarse en escenarios **variados**; si todos son linealmente similares, los resultados son redundantes.
- Construimos un **vector de features** por escenario a partir de su `.settings` y comprobamos la **correlación** y **distancia** entre escenarios para que el corpus sea **diverso** y útil como benchmark.
- Criterios: baja correlación lineal (|r| < 0,7), distancia coseno mínima entre escenarios y (opcionalmente) clustering y análisis basado en outputs.

---

## Estado actual

| Concepto | Valor |
|----------|--------|
| **Corpus** | corpus_v1 |
| **Escenarios** | 70 |
| **Familias** | 7 (Urban, Campus, Vehicles, Rural, Disaster, Social, Traffic) |
| **Features por escenario** | 33 |
| **Implementado** | Extracción de features, normalización, correlación Pearson/Spearman, distancia coseno y euclídea, clustering Ward, figuras, métricas de salida, dashboard |

---

## Resultados clave (ejecución actual)

| Métrica | Valor |
|--------|--------|
| **Escenarios** | 70 |
| **Features (d)** | 33 |
| **Pearson max \|r\|** | 0,9475 |
| **Pearson media \|r\|** | 0,2842 |
| **Pares con \|r\| ≥ 0,7** | 153 (6,3 %) |
| **Pares con \|r\| < 0,7** | 93,7 % |
| **Objetivo** | \|r\| < 0,7 en ≥95 % de pares |
| **Distancia coseno (mín)** | 0,0534 (objetivo > 0,05) |
| **Pares con cos_dist < 0,05** | 0 |
| **Silhouette (k=7)** | 0,00 (objetivo > 0,3) |

**Criterios de diversidad:** Actualmente **no** cumplidos del todo: 93,7 % de pares tienen |r| < 0,7 (objetivo ≥95 %). La distancia coseno mínima está por encima de 0,05 (no hay pares casi idénticos). El trabajo continúa para diversificar los pares más correlacionados.

---

## Gráficos clave

Las 7 figuras se generan con el pipeline y están en `scenarios/analysis/figures/`. Página completa con leyendas, informes y datos: **[Figuras](Figures-es)**.

| Figura | Descripción |
|--------|-------------|
| **Heatmap Pearson** | Correlación entre vectores de features (70×70) |
| **Heatmap Spearman** | Correlación de rangos entre vectores de features |
| **Histograma Pearson** | Distribución del |r| por pares (objetivo: mayoría &lt; 0,7) |
| **Histograma Spearman** | Distribución del |r| de Spearman |
| **Scatter PCA** | Proyección 2D de escenarios en el espacio de features |
| **Scatter par max-|r|** | Los dos escenarios más correlacionados |
| **Heatmap outputs** | Correlación entre métricas de salida (delivery, latency, overhead, drops) |

![Heatmap Pearson](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/heatmap_pearson.png)  
![Histograma Pearson](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/histogram_correlations_pearson.png)  
![Scatter PCA](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/scatter_pca_regression.png)  
![Heatmap outputs](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/heatmap_pearson_outputs.png)

*También: [Heatmap Spearman](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/heatmap_spearman.png), [Histograma Spearman](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/histogram_correlations_spearman.png), [Scatter par max-r](https://github.com/Radega1993/the-one-scenario-corpus/raw/main/scenarios/analysis/figures/scatter_max_r_pair_regression.png) — ver [Figuras](Figures-es) para todas con leyendas.*

---

## Enlaces rápidos

| Página | Descripción |
|--------|-------------|
| [Quickstart](Quickstart-es) | Instalar, ejecutar escenarios, pipeline, dashboard |
| [Metodología](Methodology-es) | Diseño de escenarios y features; correlación, distancia, clustering |
| [Resumen de resultados](Results-overview-es) | Hallazgos principales y enlaces a resultados detallados |
| [Figuras](Figures-es) | Las 7 figuras, informes y datos (con imágenes) |
| [Visión del corpus](Corpus-overview-es) | Familias y diseño global del corpus |
| [Familias de escenarios](Corpus-overview-es#familias) | Una página por familia (Urban, Campus, …) |
| [Catálogo de escenarios](Scenario-catalog-es) | Listado detallado y fichas por escenario |

---

## Cómo empezar

1. **Clonar** el repositorio (y tener el simulador The ONE compilado).
2. Seguir **[Quickstart](Quickstart-es)** para ejecutar escenarios y el pipeline de análisis.
3. Abrir el **dashboard**: `streamlit run scenarios/analysis/dashboard.py`

Para documentación completa, ver el [README](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/README.md) en el repo.
