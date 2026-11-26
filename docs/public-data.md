# Datos públicos reales

## Fuente incorporada

- Dataset: **Vehicle Crashes in Iowa**.
- Catálogo: <https://catalog.data.gov/dataset/vehicle-crashes-in-iowa>.
- Descarga: <https://idh-be.iowa.gov/api/v1/datasets/13/rows.csv>.
- Licencia: CC BY 4.0.
- Atribución: Iowa Data Hub / Iowa Department of Transportation.
- Cobertura publicada: desde 2014-12-31; actualización semanal.

La descarga requiere un `User-Agent` HTTP y llega como ZIP con varios CSV. El comando del proyecto maneja esa respuesta automáticamente.

## Descargar y preparar

```bash
make public-data
```

El proceso descarga el archivo raw en `data/raw/public_iowa_vehicle_crashes/` y genera localmente:

- `data/processed/public_iowa_crashes_summary.csv`: agregado por severidad, condado y mes.
- `data/processed/public_iowa_crashes_sample.csv`: muestra de hasta 50.000 filas para inspección y BI.
- `data/processed/public_iowa_crashes_metadata.json`: procedencia, licencia, conteo y limitaciones.

Los datos raw y derivados públicos no se versionan en Git por su tamaño; se regeneran con `make public-data`.

## Limitación de interpretación

Estos son accidentes vehiculares públicos, no reclamos de compañías de seguros. Se muestran como una fuente real de seguridad vial/riesgo contextual y se mantienen separados de `synthetic_ecuador_insurer`. No deben mezclarse para afirmar frecuencia, severidad o fraude asegurador.

## Dashboard

Después de descargar:

```bash
docker compose --profile demo up -d api streamlit
```

Abrí `http://127.0.0.1:58501` y elegí **Accidentes públicos de Iowa** en el selector de fuente.
