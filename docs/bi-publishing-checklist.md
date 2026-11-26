# Checklist de publicación BI

## Antes de publicar

- [ ] Ejecutar `make public-data`.
- [ ] Confirmar `public_iowa_crashes_metadata.json`.
- [ ] Confirmar licencia CC BY 4.0 y atribución Iowa Data Hub / Iowa DOT.
- [ ] Confirmar que el dashboard dice que son accidentes, no claims de seguros.
- [ ] Verificar totales y filtros sin doble conteo.
- [ ] No incluir `.env`, credenciales ni datos raw innecesarios.

## Power BI Web

- [ ] Iniciar sesión en el workspace aprobado.
- [ ] Cargar `data/processed/public_iowa_crashes_summary.csv`.
- [ ] Aplicar las medidas de `dashboards/powerbi/InsureIQ_PublicCrashes_Measures.dax`.
- [ ] Crear las páginas definidas en `dashboards/powerbi/README.md`.
- [ ] Añadir atribución y limitación metodológica.
- [ ] Publicar sólo con aprobación del propietario.
- [ ] Registrar URL real, workspace y fecha de publicación.

## Tableau Web

- [ ] Elegir Tableau Public sólo si la publicación pública está aprobada.
- [ ] Si se usa Tableau Cloud/Server, confirmar workspace y permisos.
- [ ] Cargar `data/processed/public_iowa_crashes_summary.csv`.
- [ ] Abrir y verificar `dashboards/tableau/InsureIQ_PublicCrashes.twb` o recrear sus hojas.
- [ ] Añadir atribución y limitación metodológica.
- [ ] Registrar URL real, proyecto y fecha de publicación.

## Evidencia

Una publicación sólo se considera verificada cuando se observa el dashboard renderizado en la cuenta autorizada y se registra su URL real. Un archivo local, XML o JSON no prueba que un dashboard web esté publicado.
