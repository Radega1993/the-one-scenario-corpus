# Decision de escalado: corpus_v2 (12 perfiles)

Generado: 2026-04-29 12:55

## Decision

**GO condicionado** para escalar conceptualmente a todos los escenarios con `TP01..TP12`.

## Evidencia minima

- Piloto ejecutado: `36/36` escenarios con metricas en `output_metrics.csv`.
- Escenarios con contacto (`total_encounters>0`): `24`.
- Escenarios sin contacto: `12` (control desconectado, principalmente `R1`).
- Nuevos perfiles direccionales activos y diferenciadores: `TP06_OneToMany`, `TP11_ManyToOne`, `TP12_GroupToGroup`.

## Condiciones antes de escalar operativo completo

1. Mantener `R1` etiquetado como **disconnected control scenario** (no usarlo como unico representante rural).
2. Incluir al menos un rural adicional con contactos para validacion de perfiles (p.ej. `R2` o `R3`).
3. Reportar dos vistas por TP: global y excluyendo no-contacto.
4. Ejecutar multiples seeds en benchmark final (min 3, recomendado 5).

## Alcance sugerido de escalado

- Escalado conceptual inmediato: `60 x 12` perfiles por protocolo.
- Escalado metodologico recomendado: `60 x 12 x P protocolos x S seeds`.
- Arranque pragmatica: `S=3` y subset de protocolos; luego expandir a `S=5`.
