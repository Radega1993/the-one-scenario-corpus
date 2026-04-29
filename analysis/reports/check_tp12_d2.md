# Check tecnico TP12 en D2 (GroupToGroup)

Generado: 2026-04-29 12:55

## Configuracion verificada

- `Group1.nrofHosts = 35`
- `Group2.nrofHosts = 35`
- `Events1.hosts = 0, 35`
- `Events1.tohosts = 35, 70`

Interpretacion de rangos (The ONE): limite superior exclusivo.
- Fuentes en `[0,35)` => Grupo A (35 nodos).
- Destinos en `[35,70)` => Grupo B (35 nodos).
- El mule (nodo 70) no esta en origen ni destino en este perfil, por diseno.

## Resultado observado en piloto

- `delivery_ratio = 0.0000`
- `drop_ratio = 0.0000`
- `total_encounters = 1699.0`

## Diagnostico

- Los rangos **si son validos** y corresponden a GroupToGroup A->B.
- `delivery_ratio=0` con `total_encounters>0` sugiere **particion efectiva + puente insuficiente** para ese patron de trafico (resultado plausible, no bug evidente de indices).
- Mantener TP12 y marcarlo como perfil exigente de intercomunidad en escenarios particionados.

## Siguiente validacion recomendada

- Repetir D2 TP12 con 3-5 seeds para confirmar estabilidad del `delivery_ratio` cercano a 0.
- Probar variante TP12b incluyendo mule como posible relay/destino (`tohosts = 35,71`) si se quiere una version menos extrema.
