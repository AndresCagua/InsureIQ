# Artefactos BI

## Estado real

Este slice genera exports reproducibles y un fixture dorado de KPI. No se afirma publicación en Power BI ni Tableau Public: las cuentas, permisos, capacidades Fabric y derechos de publicación todavía no fueron verificados desde este entorno.

## Construcción local

```bash
make data-generate PROFILE=smoke
make etl
make bi-data
```

Los archivos se generan en `dashboards/exports/`:

- CSV de las tablas procesadas.
- `golden_kpis.json` con moneda, fuente, indicador sintético y totales.
- `manifest.json` con conteos exportados.

Los dashboards públicos deben usar solamente datos sintéticos o fuentes públicas aprobadas. Antes de publicar, comparar los KPI con `golden_kpis.json`, registrar la fuente y obtener aprobación del propietario.

## Power BI y Tableau

La autoría/publicación queda pendiente de un capability spike interactivo. No usar credenciales en el repositorio, no exponer PostgreSQL a Internet y no presentar archivos JSON/XML como prueba de un dashboard funcional. Si una plataforma no permite publicación automatizada, usar los CSV preparados y documentar los pasos manuales exactos.
