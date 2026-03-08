# Metodología

**Español** | [English](Methodology)

---

Esta sección describe cómo se **diseña** y **evalúa** el corpus: diseño de escenarios, extracción de features, normalización, correlación, métricas de distancia, clustering, análisis basado en outputs y criterios de diversidad.

---

## Metodología de diseño de escenarios

- **Un escenario** = un fichero `.settings`. Cada fichero define una simulación completa del ONE: modelo de movimiento, grupos, interfaces, eventos de mensajes, reportes, etc.
- **Objetivo de diseño:** Cubrir distintas **familias** (urban, campus, vehicles, rural, disaster, social, traffic) para que los protocolos de enrutamiento se prueben en regímenes de movilidad, tráfico y recursos variados.
- **Objetivo de diversidad:** Los escenarios no deben ser **linealmente redundantes** (alta correlación en el espacio de features). Se diversifica cambiando estructura (mapa, régimen de movilidad, recursos), no solo parámetros sueltos.
- **Versionado:** El corpus se llama **corpus_v1** para poder convivir con versiones futuras (p. ej. corpus_v2); los scripts usan `--corpus corpus_v1`.

---

## Extracción de features

- Cada `.settings` se **parsea** y se convierte en un **vector de features** de longitud fija.
- Los features son **estables** (reproducibles a partir del fichero) y **reportables** (útiles para papers).
- **Grupos de features:**
  1. **Movilidad / espacio:** tamaño del mundo (Wx, Wy), número de nodos (N), densidad, velocidad media, ratio de pausa, wait mean, one-hot de modelo de movimiento (WDM, RWP, MapRoute, Cluster, Bus, ShortestPath, External).
  2. **Contacto:** rango de transmisión, proxy de tasa de contacto (densidad × rango² × velocidad).
  3. **Tráfico:** intervalo medio de eventos, tamaño medio de mensaje, msgTtl, patrón de tráfico (uniform / burst / hub_target), número de generadores de eventos.
  4. **Recursos:** tamaño de buffer, velocidad de transmisión.
  5. **WDM (WorkingDayMovement):** workDayLength, timeDiffSTD, probGoShoppingAfterWork, nrOfMeetingSpots, nrOfOffices (cuando aplica).

- **Número actual:** 33 features por escenario. La lista exacta está en `scenarios/analysis/` (ver [Referencia del pipeline](Analysis-pipeline-reference-es) o README del repo).

---

## Normalización

- Tras la extracción, la matriz de features **X** (una fila por escenario, una columna por feature) se **normaliza con z-score** por feature:
  - \( Z_{s,j} = (X_{s,j} - \mu_j) / \sigma_j \)
- Si un feature tiene varianza cero, se deja en 0.
- **Salida:** `features_normalized.csv` y `normalization_params.csv` (medias y desviaciones típicas). La correlación y la distancia se calculan sobre **Z**.

---

## Análisis de correlación

- **Correlación entre escenarios** = correlación entre sus **vectores de features** (filas de Z).
- Para cada par de escenarios (i, k): **Pearson** r(Z_i, Z_k) y **Spearman** (correlación de rangos).
- **Umbral:** Objetivo **|r| < 0,7** en al menos el 95 % de los pares (o 100 % con `--strict`). Un |r| alto indica que los dos escenarios son linealmente similares en el espacio de parámetros.
- **Comparaciones múltiples:** Hay m = n(n−1)/2 pares. Para cada par se contrasta H₀: ρ = 0. Se aplican **FDR (Benjamini–Hochberg)** y **Bonferroni** para controlar falsos descubrimientos. El objetivo es que ningún par tenga a la vez |r| alto y significación tras corrección.

---

## Métricas de distancia

- **Distancia coseno:** 1 − cos_sim(Z_i, Z_k). Mide el **ángulo** entre vectores (0 = misma dirección, 2 = opuestos).
- **Distancia euclídea:** ||Z_i − Z_k||. Mide la diferencia en **magnitud**.
- **Criterio de diversidad:** Distancia coseno mínima **> 0,05**; **ningún par** con cos_dist < 0,05 (no escenarios casi idénticos).

---

## Clustering

- **Método:** Ward (jerárquico) sobre la matriz de features normalizada Z.
- **Salida:** `cluster_assignments.csv` (escenario → cluster), `clustering_report.txt`.
- **Uso:** Identificar clusters de escenarios similares; elegir representantes; diversificar el resto (ver “escenarios a diversificar”).

---

## Análisis basado en outputs

- **Outputs** = métricas de resultado del ONE por escenario: delivery ratio, latency mean, overhead ratio, drop ratio (a partir de MessageStatsReport).
- Se construye un **vector por escenario** con estas métricas, se normaliza y se calculan **Pearson/Spearman y distancias** entre vectores de salida. Así se comprueba redundancia en **comportamiento** (entrega, latencia, etc.), no solo en **parámetros**.

---

## Criterios de diversidad (resumen)

| Criterio | Objetivo |
|----------|----------|
| **Pearson \|r\|** | < 0,7 en ≥95 % de pares (o 100 %) |
| **Distancia coseno (mín)** | > 0,05 |
| **Pares con cos_dist < 0,05** | 0 |
| **Silhouette (opcional)** | > 0,3 para calidad del clustering |

**“Escenario a diversificar”:** Un escenario que aparece en muchos pares con |r| alto o en un cluster denso; se modifican sus `.settings` (speed, waitTime, transmitRange, workDayLength, TTL, buffer, etc.) para alejarlo en el espacio de features. La lista está en `analysis/reports/scenarios_to_diversify.txt`.

---

## Ver también

- [Resumen de resultados](Results-overview-es) — Números y figuras actuales  
- [Visión del corpus](Corpus-overview-es) — Familias y diseño  
- [Referencia del pipeline](Analysis-pipeline-reference-es) — Fases y artefactos  
