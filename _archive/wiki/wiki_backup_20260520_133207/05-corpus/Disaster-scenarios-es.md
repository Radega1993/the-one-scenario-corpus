## Escenarios Disaster (9)

Esta página resume los escenarios de la **familia Disaster** y enlaza a la documentación completa por escenario (ES). Cubren regímenes DTN complementarios en condiciones de desastre: hotspots de refugio, ciudades particionadas con mules puente, movilidad errática post-réplica, triaje médico, mules UAV, mensajería crítica con TTL corto, tormentas de tráfico, recuperación de infraestructura y TTL extremo de 1 min.

### Índice

| ID | Escenario (página) | Fichero settings | Idea central |
|----|--------------------|------------------|---------------|
| D1 | [D1_ShelterHotspots_Clusters](scenarios-es/disaster/D1_ShelterHotspots_Clusters-es) | `corpus_v1/05_disaster/D1_ShelterHotspots_Clusters.settings` | Hotspots de refugio + voluntarios móviles que conectan clusters |
| D2 | [D2_PartitionedCity_MuleBridge](scenarios-es/disaster/D2_PartitionedCity_MuleBridge-es) | `corpus_v1/05_disaster/D2_PartitionedCity_MuleBridge.settings` | Dos particiones + un único mule puente |
| D3 | [D3_Aftershock_ErraticMobility](scenarios-es/disaster/D3_Aftershock_ErraticMobility-es) | `corpus_v1/05_disaster/D3_Aftershock_ErraticMobility.settings` | Movilidad errática, rango amplio velocidad/espera, TTL corto |
| D4 | [D4_MedicalTriage_TwoClasses](scenarios-es/disaster/D4_MedicalTriage_TwoClasses-es) | `corpus_v1/05_disaster/D4_MedicalTriage_TwoClasses.settings` | Dos clases de tráfico (crítico vs rutinario), hub-target |
| D5 | [D5_UAVMule_FastRoute_HelsinkiMedium](scenarios-es/disaster/D5_UAVMule_FastRoute_HelsinkiMedium-es) | `corpus_v1/05_disaster/D5_UAVMule_FastRoute_HelsinkiMedium.settings` | Mules UAV en mapa sobre rutas largas rápidas |
| D6 | [D6_ShortTtlCritical_5to10min](scenarios-es/disaster/D6_ShortTtlCritical_5to10min-es) | `corpus_v1/05_disaster/D6_ShortTtlCritical_5to10min.settings` | TTL crítico 5–10 min, cargas pequeñas |
| D7 | [D7_HighLoad_TrafficStorm](scenarios-es/disaster/D7_HighLoad_TrafficStorm-es) | `corpus_v1/05_disaster/D7_HighLoad_TrafficStorm.settings` | Tasa de mensajes muy alta, estrés de buffer |
| D8 | [D8_InfrastructureReturns_BackboneLinks](scenarios-es/disaster/D8_InfrastructureReturns_BackboneLinks-es) | `corpus_v1/05_disaster/D8_InfrastructureReturns_BackboneLinks.settings` | Particionado + enlaces backbone vía eventos externos |
| D9 | [D9_Critical_1minTTL](scenarios-es/disaster/D9_Critical_1minTTL-es) | `corpus_v1/05_disaster/D9_Critical_1minTTL.settings` | TTL extremo 1 min, esperas erráticas |
