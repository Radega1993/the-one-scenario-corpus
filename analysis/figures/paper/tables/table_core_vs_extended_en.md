# Core vs extended features (paper, EN)

## Core


| feature               | category              | short_reason                                                                             | coverage | type            |
| --------------------- | --------------------- | ---------------------------------------------------------------------------------------- | -------- | --------------- |
| world_area            | empírica              | escala espacial base del escenario.                                                      | 60/60    | continua        |
| aspect_ratio          | empírica              | geometría espacial independiente del área.                                               | 60/60    | continua        |
| N                     | empírica              | carga poblacional del sistema.                                                           | 60/60    | discreta/entera |
| nrofHostGroups        | mixta                 | heterogeneidad organizativa por grupos.                                                  | 60/60    | discreta/entera |
| speed_mean            | empírica              | ritmo de movilidad e interacción.                                                        | 60/60    | continua        |
| wait_mean             | empírica              | persistencia temporal de nodos.                                                          | 60/60    | continua        |
| mm_WDM                | semántica estructural | indica régimen laboral de movilidad.                                                     | 60/60    | binaria         |
| mm_RWP                | semántica estructural | indica régimen aleatorio base.                                                           | 60/60    | binaria         |
| mm_MapRoute           | semántica estructural | indica movilidad restringida por mapa/rutas.                                             | 60/60    | binaria         |
| mm_Cluster            | semántica estructural | segregación espacial explícita por clusters.                                             | 60/60    | binaria         |
| mm_Bus                | semántica estructural | movilidad vehicular periódica como relé.                                                 | 60/60    | binaria         |
| mm_Linear             | semántica estructural | trayectoria extrema diferencial.                                                         | 60/60    | binaria         |
| transmitRange         | empírica              | cobertura física local de conectividad.                                                  | 60/60    | continua        |
| bufferSize            | empírica              | capacidad de almacenamiento/congestión.                                                  | 60/60    | continua        |
| transmitSpeed         | empírica              | capacidad de servicio del enlace.                                                        | 60/60    | continua        |
| msgTtl                | semántica estructural | restricción temporal fundamental de validez en DTN.                                      | 60/60    | continua        |
| event_interval_mean   | empírica              | intensidad temporal del tráfico.                                                         | 60/60    | continua        |
| event_size_mean       | empírica              | volumen de carga por mensaje.                                                            | 60/60    | continua        |
| nrof_event_generators | empírica              | multiplicidad de flujos de entrada.                                                      | 60/60    | discreta/entera |
| pattern_burst         | empírica              | clasificación semántica propia del corpus para tráfico con ventana temporal.             | 60/60    | binaria         |
| pattern_hub_target    | empírica              | clasificación semántica propia del corpus para tráfico dirigido a destinos concentrados. | 60/60    | binaria         |
| workDayLength         | mixta                 | ventana temporal laboral relevante en WDM.                                               | 9/60     | condicional     |
| ownCarProb            | mixta                 | mezcla modal peatón/vehículo en WDM.                                                     | 9/60     | condicional     |


## Extended


| feature                    | category | short_reason                                                                                                                                    | coverage | type                        |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | -------- | --------------------------- |
| density                    | empírica | proxy de concentración espacial (redundante con core).                                                                                          | 60/60    | derivada                    |
| pause_ratio                | empírica | resume inmovilidad relativa (redundante con `wait_mean`).                                                                                       | 60/60    | derivada                    |
| mm_ShortestPath            | mixta    | submodelo útil pero no núcleo corpus-wide.                                                                                                      | 60/60    | binaria                     |
| mm_External                | mixta    | submodelo externo útil para casos concretos.                                                                                                    | 60/60    | binaria                     |
| contact_rate_proxy         | empírica | señal sintética de frecuencia de contacto.                                                                                                      | 60/60    | derivada                    |
| pattern_uniform            | empírica | clasificación semántica propia del corpus; no es etiqueta nativa de The ONE.                                                                    | 60/60    | binaria                     |
| timeDiffSTD                | empírica | dispersión horaria entre agentes WDM.                                                                                                           | 9/60     | condicional                 |
| probGoShoppingAfterWork    | empírica | conducta social post-trabajo específica.                                                                                                        | 9/60     | condicional                 |
| nrOfMeetingSpots           | empírica | granularidad de puntos de encuentro.                                                                                                            | 9/60     | condicional discreta/entera |
| nrOfOffices                | empírica | infraestructura laboral del submodelo WDM.                                                                                                      | 9/60     | condicional discreta/entera |
| officeSize                 | empírica | escala espacial del área de oficina en el submodelo WDM.                                                                                        | 9/60     | condicional                 |
| nrOfShops                  | empírica | infraestructura comercial del submodelo WDM.                                                                                                    | 9/60     | condicional discreta/entera |
| shopSize                   | empírica | parámetro condicional del proyecto para escala/capacidad de tienda en WDM; no documentado explícitamente en ejemplos base revisados de The ONE. | 9/60     | condicional                 |
| officeWaitTime_mean        | empírica | permanencia media en oficinas.                                                                                                                  | 9/60     | condicional                 |
| shoppingWaitTime_mean      | empírica | permanencia media en compras.                                                                                                                   | 9/60     | condicional                 |
| eveningGroupSize_mean      | empírica | tamaño de grupos de actividad evening.                                                                                                          | 9/60     | condicional                 |
| eveningWaitTime_mean       | empírica | permanencia media en actividad evening.                                                                                                         | 9/60     | condicional                 |
| afterShoppingStopTime_mean | empírica | parada media tras compras.                                                                                                                      | 9/60     | condicional                 |
| clusterRange_mean          | empírica | alcance espacial de clusters; baja cobertura corpus-wide.                                                                                       | 6/60     | condicional                 |
| event2_interval_mean       | empírica | periodicidad del segundo flujo, cuando existe.                                                                                                  | 4/60     | condicional                 |
| event2_size_mean           | empírica | volumen del segundo flujo, cuando existe.                                                                                                       | 4/60     | condicional                 |
| Scenario.endTime           | mixta    | horizonte temporal total de simulación.                                                                                                         | 60/60    | continua                    |
| has_active_times           | mixta    | indica si hay ventanas activas definidas.                                                                                                       | 60/60    | binaria                     |


