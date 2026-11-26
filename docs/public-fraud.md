# Benchmark público de fraude

## Fuente

- Dataset: **Auto Insurance Claims**.
- Registro: Zenodo `13381118`.
- DOI: `10.5281/zenodo.13381118`.
- URL: <https://zenodo.org/records/13381118>.
- Licencia: CC BY 4.0.
- Archivo: `US Insurance Claims Data.xlsx`.
- Filas convertidas: 10.000.
- SHA256: `c1c2ac62dd3cf2089d4fff20bc12ce375fb61890c9bde83e496925193931cb21`.

## Descargar y entrenar

```bash
make public-fraud
make fraud-train
```

`make public-fraud` descarga el XLSX dentro del contenedor, verifica el checksum MD5 publicado y genera:

```text
data/processed/public_vehicle_fraud_benchmark.csv
data/processed/public_vehicle_fraud_benchmark_metadata.json
```

`make fraud-train` entrena el baseline logístico, guarda métricas y persiste localmente:

```text
reports/fraud_metrics.json
reports/fraud_model.joblib
reports/model_registry.json
```

Después de `make bi-data`, el scoring batch genera también:

```text
dashboards/exports/fraud_review_queue.csv
```

Contiene los casos del benchmark con probabilidad `>= 0,5`, ordenados de mayor a menor, junto con `policy_number`, monto, severidad, tipo de incidente, etiqueta publicada, probabilidad y recomendación. Es una cola de priorización del benchmark, no una decisión real de aseguramiento.

## Etiqueta

La columna original `fraud_reported` se conserva semánticamente y se transforma así:

```text
Y → 1
N → 0
```

El modelo produce una probabilidad de la etiqueta publicada. La salida operativa sólo recomienda:

```text
MANUAL_REVIEW
STANDARD_REVIEW
```

Nunca rechaza automáticamente un claim.

## Resultado observado

En la ejecución reproducible del split estratificado 75/25:

- ROC-AUC: `0.9840985076222708`
- Average Precision: `0.9146386805980439`
- Filas de prueba: `2.500`

Estas métricas corresponden a este benchmark y split; no son validación ecuatoriana, no prueban causalidad y no garantizan rendimiento productivo.

## API

Después de entrenar y recrear la API:

```bash
docker compose --profile demo up -d --force-recreate api
```

Endpoint:

```text
POST http://127.0.0.1:58000/api/v1/fraud/predict
```

Ejemplo:

```json
{
  "claim_id": "ZENODO-DEMO-001",
  "features": {
    "total_claim_amount": 67253,
    "incident_severity": "Total Loss",
    "number_of_vehicles_involved": 1,
    "property_damage": "YES"
  }
}
```

La API puede completar variables no enviadas mediante la imputación del pipeline. Para una evaluación seria, enviar el esquema completo del benchmark y monitorear datos faltantes.
