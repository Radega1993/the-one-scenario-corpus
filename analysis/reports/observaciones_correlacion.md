# Observaciones sobre la correlación entre escenarios

Documento para trabajo posterior: interpretación del análisis de correlación y líneas de mejora.

---

## Resultado actual (corpus_v1, 60 escenarios, 28 features)

- **max |r| = 1.0**: hay escenarios con el **mismo vector de features** (correlación perfecta entre pares de escenarios). En particular, varios escenarios urbanos (U1–U12) y de vehículos (V4–V8) comparten el mismo vector.
- **208 pares (11,8%)** con |r| ≥ 0,7 → no se cumple el criterio ni en versión estricta (100% de pares con |r| < 0,7) ni en versión flexible (≥95% de pares con |r| < 0,7). Actualmente solo ~88% de los pares cumplen |r| < 0,7.

---

## Interpretación

Es **esperable** con el corpus actual:

- Muchos escenarios **U1–U12** (urbanos) y **V4–V8** (vehículos) comparten el mismo mapa (Helsinki) y una estructura de grupos/movimiento muy similar. Las diferencias entre ellos (p. ej. workday length, retail, nightlife, road closure) no siempre se reflejan en el **vector de 28 features** que extraemos (p. ej. parámetros WDM como `workDayLength`, `probGoShoppingAfterWork`, `nrOfMeetingSpots` no están en el vector actual, o están poco diferenciados).
- Por tanto, el criterio de “no correlación lineal fuerte” (|r| < 0,7 en todos o en el 95% de los pares) **no se cumple** hasta que se diversifiquen escenarios o se amplíe/detalle el vector de características.

---

## Líneas de trabajo para más adelante

1. **Diversificar escenarios**
   - Revisar los escenarios que comparten exactamente el mismo vector (r = 1,0) y modificar .settings para que difieran en al menos algunas features (p. ej. distintos `speed`, `waitTime`, `bufferSize`, parámetros WDM, etc.) de forma que queden reflejados en el vector.

2. **Ampliar el vector de características**
   - Incluir más parámetros que ya existen en los .settings pero no se exportan como features (p. ej. parámetros específicos de WorkingDayMovement: `workDayLength`, `timeDiffSTD`, `probGoShoppingAfterWork`, `nrOfMeetingSpots`, `officeWaitTimeParetoCoeff`, `nrOfOffices`). Así escenarios que hoy son idénticos en el vector pasarían a diferenciarse.

3. **Refinar features existentes**
   - Cuando hay varios grupos, considerar agregaciones por grupo (p. ej. velocidad mín/máx entre grupos, o indicador de heterogeneidad) para que escenarios con “mismo mundo pero distintos roles” no colapsen al mismo vector.

4. **Criterio de benchmark**
   - Decidir si para el paper/tesis se exige cumplir |r| < 0,7 en el 100% de los pares o si es aceptable el 95%. Si se relaja, con las mejoras anteriores podría llegarse a ~95% sin eliminar escenarios; si se exige 100%, probablemente haga falta combinar diversificación + más features.

---

*Generado a partir del análisis con `run_analysis.py --phase correlation`. Actualizar este documento al re-ejecutar el análisis o al aplicar cambios en el corpus o en el vector de features.*
