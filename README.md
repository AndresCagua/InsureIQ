# InsureIQ

Plataforma reproducible de análisis de riesgos y fraude para seguros.

## Inicio rápido

Requisitos mínimos:

- Docker 29 o compatible.
- Docker Compose v2 o superior.
- GNU Make.

La versión de Python del proyecto está fijada en Python 3.12 dentro de Docker. No es necesario instalar Python en el host para ejecutar el código del proyecto.

```bash
cp .env.example .env
make doctor
make bootstrap
make test
```

El desarrollo se ejecuta mediante contenedores. Los servicios y puertos se documentan en `odd/tasks/insureiq-platform.md` y se validan antes de iniciar Compose.

## Estado

La implementación sigue los slices definidos en `odd/tasks/insureiq-platform.md`. Este slice crea la base reproducible; los servicios de datos, ETL, modelos, API, BI y demo se incorporarán en slices posteriores.
