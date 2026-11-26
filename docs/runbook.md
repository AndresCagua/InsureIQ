# Runbook local

## Arranque

```bash
cp .env.example .env
make doctor
make bootstrap
make up
```

`make doctor` debe ejecutarse antes de iniciar los perfiles y valida los puertos host configurados. No se deben modificar servicios de otros proyectos para resolver un conflicto: cambiar las variables `*_HOST_PORT` en `.env`.

## Smoke reproducible

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
