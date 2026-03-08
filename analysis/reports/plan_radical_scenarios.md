# Plan: ~10 escenarios radicalmente distintos

Objetivo: bajar **max |r|** y **% de pares con |r| ≥ 0,7** introduciendo escenarios que cambien **estructura del grafo dinámico**, no solo parámetros de carga. Con ~10 así, el espacio de vectores Z se abre y la correlación estructural baja.

Cada idea debe materializarse en un `.settings` nuevo (o variante de uno existente) dentro del corpus, manteniendo compatibilidad con The ONE y con las **features que ya extrae** `run_analysis.py`.

---

## 1. Estructura espacial

| # | Idea | Qué cambia | Parámetros clave (.settings) |
|---|------|------------|------------------------------|
| 1 | **Partición permanente** (dos mundos sin puente) | Grafo desconectado en dos componentes; ningún mensaje puede cruzar. | Dos grupos en mapas/zonas que no se solapan; o mismo mapa con waypoints que nunca se encuentran. |
| 2 | **Partición con mule único** | Casi partición, pero un nodo (mule) conecta ambas partes de forma esporádica. | Un host con ruta que cruza; el resto en dos comunidades. |
| 3 | **Rango masivo (quasi fully connected)** | transmitRange muy alto respecto al tamaño del mapa → encuentros muy frecuentes. | transmitRange 200m+ en mapa pequeño; o mapa pequeño + muchos nodos. |
| 4 | **Grafo extremadamente esparso** | Rango muy bajo, encuentros raros. | transmitRange 5m; velocidad baja; mapa grande. |
| 5 | **2 super-hubs** | Dos nodos con mucha más centralidad (p. ej. siempre en sitios de alto tránsito). | MapBased con 2 waypoints fijos o de espera larga; resto se mueve hacia ellos. |
| 6 | **10 micro-comunidades** | Estructura en muchas comunidades pequeñas con poco flujo entre ellas. | Múltiples MapBased/zonas; probabilidades de transición bajas entre zonas. |

---

## 2. Régimen dinámico / temporal

| # | Idea | Qué cambia | Parámetros clave |
|---|------|------------|------------------|
| 7 | **TTL menor que tiempo medio de encuentro** | Mensajes expiran antes de poder ser reenviados en la mayoría de los casos. | msgTtl muy bajo (p. ej. 60–300 s) vs intervalos de encuentro típicos. |
| 8 | **TTL infinito** | Mensajes nunca expiran; carga acumulada en buffers. | msgTtl = 24h o máximo permitido por el motor. |
| 9 | **Movilidad determinista circular** | Sin aleatoriedad en rutas; nodos en órbitas fijas. | Ruta circular o Waypoint con repetición exacta; mismo periodo para todos o desfasados. |
| 10 | **Cambio de fase a mitad de simulación** | Primera mitad: un régimen (p. ej. estacionario); segunda mitad: otro (burst o distinta movilidad). | Dos fases en el mismo .settings si el motor lo permite; o dos grupos con activación temporal distinta. |

---

## 3. Régimen de recursos (extremos)

| # | Idea | Qué cambia | Parámetros clave |
|---|------|------------|------------------|
| 11 | **Buffer microscópico** | Buffer muy pequeño → descartes frecuentes. | bufferSize 256KB o menor. |
| 12 | **Buffer muy grande** | Poca presión de buffer; impacto en orden de envío/prioridad. | bufferSize 200MB (o máximo). |
| 13 | **Velocidad extrema baja** | 0,2 m/s → encuentros muy espaciados. | speed min/max muy bajos. |
| 14 | **Velocidad extrema alta** | 15 m/s → encuentros muy frecuentes en mapa pequeño. | speed alta; transmitSpeed acorde. |
| 15 | **transmitSpeed muy bajo vs muy alto** | Cuello de botella en transmisión vs. transmisión casi instantánea. | 256kbps vs 10Mbps. |

---

## Priorización para “~10 radicales”

Elegir **~10** de la tabla (mezclando ejes) para implementar primero, por ejemplo:

- **Estructura:** 1 (partición), 2 (mule), 3 (rango masivo), 5 (super-hubs) o 6 (micro-comunidades).
- **Dinámico:** 7 (TTL &lt; tiempo encuentro), 8 (TTL infinito), 9 (movilidad determinista).
- **Recursos:** 11 (buffer microscópico), 13 o 14 (velocidad extrema).

Al añadirlos al corpus, re-ejecutar:

```bash
run_analysis.py --corpus corpus_v1 --phase all
```

y comprobar: **max |r| < 0,85**, **pares con |r| ≥ 0,7 < 3%**, **cos_dist mín > 0,05**.
