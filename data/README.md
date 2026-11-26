# Datos y procedencia

Este directorio separa fuentes públicas, datos procesados y datos sintéticos. Los archivos raw y los artefactos grandes no se confirman en Git.

## Registro de fuentes

`sources.yml` es el contrato de procedencia. Cada fuente pública debe completar la URL resuelta, versión, licencia, atribución, fecha de recuperación, SHA256, esquema, cantidad de filas, geografía, moneda, definición del objetivo y política de redistribución antes de usarse en resultados.

No se debe marcar una fuente como verificada basándose únicamente en el nombre del dataset o en un archivo descargado. La verificación debe registrar evidencia reproducible y dejar `verified: false` mientras esté pendiente.

## Descarga

1. Ejecutar `make data-fetch` cuando el comando esté disponible.
2. Si una fuente requiere login, descargarla manualmente desde su sitio oficial.
3. Colocar el archivo en `data/raw/<source_dataset>/` sin renombrar la fuente registrada.
4. Calcular SHA256 y completar el registro antes de transformar.
5. No subir archivos raw ni credenciales.

Si una fuente no está disponible, el pipeline debe fallar con un mensaje accionable o usar únicamente el fallback sintético documentado. El fallback sintético no reemplaza la evidencia de un benchmark público.
