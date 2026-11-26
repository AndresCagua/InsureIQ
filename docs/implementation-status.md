# Estado de implementación

## Resumen

InsureIQ tiene una base contenerizada reproducible con Python 3.12, generación sintética, ETL, almacén dimensional inicial, análisis estadístico, baselines de fraude/riesgo/pronóstico, API local, Streamlit y exports BI.

## Verificaciones ejecutadas

- Docker Compose config: correcto.
- Imagen Python 3.12: construida.
- `make doctor`: puertos configurados disponibles antes del arranque.
- `pytest`: pruebas del proyecto ejecutadas dentro del contenedor.
- Ruff: sin errores en los checks realizados.
- PostgreSQL y MinIO: healthchecks `healthy`.
- API `/health`: respondió `{"status":"ok"}`.
- Streamlit: inició en el perfil `demo`.

## Limitaciones y bloqueos

- Las fuentes públicas de fraude no están verificadas ni descargadas; `make fraud-train` falla claramente hasta completar `data/sources.yml`.
- Las métricas actuales de riesgo, pronóstico y BI son sintéticas y no son validación ecuatoriana.
- MLflow registry, publicación Power BI y Tableau Public requieren capability spikes y credenciales/permisos interactivos; no se afirma que estén publicados.
- Azure queda como arquitectura opcional, no como despliegue realizado.

## Próximos pasos

1. Verificar fuentes públicas y licencias.
2. Completar modelos con benchmark aprobado.
3. Ejecutar capability spikes interactivos de BI.
4. Añadir cobertura y pruebas de integración contra PostgreSQL/MinIO/dbt.
