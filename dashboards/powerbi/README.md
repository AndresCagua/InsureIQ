# Power BI — InsureIQ Public Crashes

## Estado

Este directorio contiene el paquete reproducible de fuente, modelo, medidas y layout. No contiene un `.pbix`: ese formato se genera dentro de Power BI Desktop y no se debe fingir un binario que no fue abierto y validado.

## Carga rápida en Power BI Web

1. Ejecutá `make public-data`.
2. En Power BI Web elegí **Nuevo → Cargar un archivo**.
3. Cargá `data/processed/public_iowa_crashes_summary.csv`.
4. Renombrá la tabla a `public_iowa_crashes_summary`.
5. Copiá las medidas desde `InsureIQ_PublicCrashes_Measures.dax`.
6. Creá las páginas según `InsureIQ_PublicCrashes_Model.json`.
7. Cargá `data/processed/public_iowa_crashes_metadata.json` sólo como referencia de procedencia.

## Modelo

La tabla tiene cuatro campos: `dimension`, `category`, `period` y `crashes`. El campo `dimension` separa los agregados de mes/severidad, severidad y condado. No sumes simultáneamente todas las dimensiones para reportar un KPI: filtra una dimensión específica para evitar doble conteo.

## Métricas ML

Después de ejecutar `make fraud-train` y `make bi-data`, cargá también:

```text
dashboards/exports/ml_fraud_metrics.csv
```

Usá las medidas de `InsureIQ_ML_Measures.dax` para mostrar ROC-AUC, average precision, filas de prueba y modelo activo. Etiquetá la página como **Benchmark ML público — no producción**.

## Publicación

La publicación requiere una cuenta/workspace autenticado y aprobación del propietario. No se ejecuta desde el repositorio ni se guardan credenciales.
