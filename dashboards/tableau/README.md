# Tableau — InsureIQ Public Crashes

## Estado

`InsureIQ_PublicCrashes.twb` es un workbook XML fuente para abrir/verificar en Tableau Desktop. El enlace a la fuente es relativo a `data/processed/public_iowa_crashes_summary.csv`; si Tableau no lo resuelve, elija **Edit Connection** y seleccione ese CSV.

## Carga

1. Ejecute `make public-data`.
2. Abra `InsureIQ_PublicCrashes.twb` en Tableau Desktop, o cree un workbook nuevo en Tableau Web.
3. Si utiliza Tableau Web, cargue `data/processed/public_iowa_crashes_summary.csv` como fuente.
4. Utilice `dimension` como filtro y `category` como dimensión.
5. Utilice `crashes` como medida.
6. Cree hojas de resumen, severidad, condado y tendencia mensual.

## Advertencia de doble conteo

La tabla contiene agregados de tres dimensiones. Para un KPI, filtrá una dimensión:

- `severity` para severidad.
- `county` para condado.
- `month_severity` para tendencia mensual.

No sumes las tres dimensiones juntas.

## Métricas ML

Después de ejecutar `make fraud-train` y `make bi-data`, agregue la fuente:

```text
dashboards/exports/ml_fraud_metrics.csv
```

Cree una hoja **Métricas ML** con `metric` en filas y `value` en texto, filtrando `model = fraud-baseline-public`. Agregue `dashboards/exports/fraud_review_queue.csv` como fuente para una hoja **Cola de revisión manual**, mostrando `policy_number`, `fraud_probability`, `recommendation` y `incident_severity`. Muestre una nota: **Benchmark ML público — no producción**.

## Publicación

Tableau Public hace el contenido público. Tableau Cloud/Server requiere workspace y permisos. La publicación queda pendiente de una sesión autenticada del propietario.
