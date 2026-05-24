# Política de NaN y normalización

Propósito: documentar la política de preprocesado usada por el pipeline de análisis.

## Política NaN

- NaN indica **no aplicabilidad estructural**, no ausencia aleatoria de datos.
- Casos típicos: descriptores condicionales (por ejemplo campos WDM fuera de escenarios WDM).

## Política de normalización

1. Calcular media/desviación por feature usando valores no-NaN.
2. Aplicar z-score sobre entradas válidas.
3. Reemplazar NaN restantes por `0` en el espacio estandarizado.

Es una decisión metodológica para mantener comparabilidad de escenarios en una geometría común.
