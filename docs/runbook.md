# Runbook local

## Arranque

```bash
cp .env.example .env
make doctor
make bootstrap
make up
```

`make doctor` debe ejecutarse antes de iniciar los perfiles y valida los puertos host configurados. Si un puerto ya pertenece a un contenedor de InsureIQ, lo informa como `ocupado por InsureIQ` y lo acepta; sólo bloquea puertos ocupados por otro proceso. No se deben modificar servicios de otros proyectos para resolver un conflicto: cambiar las variables `*_HOST_PORT` en `.env`.

## Credenciales locales de MinIO

Con la configuración predeterminada de desarrollo:

- Consola: `http://127.0.0.1:59001`
- API S3: `http://127.0.0.1:59000`
- Usuario: `insureiq`
- Clave: `local-only-change-me`

Estas credenciales son únicamente valores locales de desarrollo definidos por Compose. Si `.env` contiene `MINIO_ROOT_USER` o `MINIO_ROOT_PASSWORD`, prevalecen esos valores. No uses la clave predeterminada en un entorno compartido o productivo y no la publiques en Git.

## Smoke reproducible

Ejecute los comandos en este orden:

```bash
make data-generate PROFILE=smoke
make etl
make statistics
make risk-train
make forecast
make bi-data
make test
make lint
```

Descripción:

| Comando | Función |
|---|---|
| `make data-generate PROFILE=smoke` | Genera fixtures sintéticos pequeños y deterministas. |
| `make etl` | Valida, transforma y separa registros rechazados. |
| `make statistics` | Genera el informe de calidad descriptiva. |
| `make risk-train` | Calcula los baselines de frecuencia, severidad y prima pura. |
| `make forecast` | Ejecuta pronóstico naive estacional y backtesting. |
| `make bi-data` | Exporta CSV y KPI dorados en `dashboards/exports/`. |
| `make test` | Ejecuta pytest dentro del contenedor Python 3.12. |
| `make lint` | Ejecuta Ruff dentro del contenedor. |
| `make security-check` | Busca patrones básicos de secretos en archivos versionados. |
| `make performance` | Mide tiempo y memoria del smoke y escribe el resultado en `/tmp`. |

## Demo

```bash
make api
make streamlit
```

API: `http://127.0.0.1:58000`.
Streamlit: `http://127.0.0.1:58501`.

## Apagado y limpieza

```bash
docker compose --profile core --profile demo down --remove-orphans
make clean
```

`make clean` no elimina datos externos ni hace reset destructivo de volúmenes. Los volúmenes se deben eliminar explícitamente y con autorización del propietario.
