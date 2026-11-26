# Tableau — InsureIQ Public Crashes

## Estado

`InsureIQ_PublicCrashes.twb` es un workbook XML fuente para abrir/verificar en Tableau Desktop. El enlace a la fuente es relativo a `data/processed/public_iowa_crashes_summary.csv`; si Tableau no lo resuelve, elegí **Edit Connection** y seleccioná ese CSV.

## Carga

1. Ejecutá `make public-data`.
2. Abrí `InsureIQ_PublicCrashes.twb` en Tableau Desktop, o creá un workbook nuevo en Tableau Web.
3. Si usás Tableau Web, cargá `data/processed/public_iowa_crashes_summary.csv` como fuente.
4. Usá `dimension` como filtro y `category` como dimensión.
5. Usá `crashes` como medida.
6. Creá hojas de resumen, severidad, condado y tendencia mensual.

## Advertencia de doble conteo

La tabla contiene agregados de tres dimensiones. Para un KPI, filtrá una dimensión:

- `severity` para severidad.
- `county` para condado.
- `month_severity` para tendencia mensual.

No sumes las tres dimensiones juntas.

## Métricas ML

Después de ejecutar `make fraud-train` y `make bi-data`, agregá la fuente:

```text
dashboards/exports/ml_fraud_metrics.csv
```

Creá una hoja **Métricas ML** con `metric` en filas y `value` en texto, filtrando `model = fraud-baseline-public`. Mostrá una nota: **Benchmark ML público — no producción**.

## Publicación

Tableau Public hace el contenido público. Tableau Cloud/Server requiere workspace y permisos. La publicación queda pendiente de una sesión autenticada del propietario.
