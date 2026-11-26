# Plan de slices — InsureIQ

Especificación de trabajo derivada de `SPEC.md` para implementar el proyecto de forma incremental, verificable y sin choques de infraestructura.
La ejecución debe seguir el orden de dependencias; cada slice incluye código, pruebas y documentación de su comportamiento.

## Specs

### S1 — Alcance y reglas de trabajo
> "listo mi pana, a esos sepcs realizale el trabajo de separacion de tareas en slices para comenzar a trabajar, ojo revisa si en los specs se debe trabajar todo en contenedores de docker y debes revisar que puertos esten disponibles para que no choque nada"

> "Todo el código fuente debe estar en ingles, pero comentarios del código, identificadores, interfaz de usuario, documentación y mensajes de commit deben estar en español y los mensaje del commit debe seguir este formato: yyyymmdd y mensaje bastante descriptivo de lo hecho en el commit,esto es una regla obligatoria siempre revisar la fecha antes de hacer commit para colocar la fecha correcta."

Criterios: respetar el alcance de `SPEC.md`, usar commits con fecha `yyyymmdd` y descripción en español cuando se llegue a la etapa de commits, y registrar toda desviación o bloqueo.

### S2 — Base reproducible y configuración
Relacionado con SPEC §3, §12, §13 y §18.

Crear estructura inicial, `pyproject.toml`, lockfile, `.env.example`, `.gitignore`, `Makefile`, `compose.yml`, perfiles Compose, configuración smoke/full/models, CI mínima y documentación de arranque. Verificar versiones de Python, Docker y Docker Compose. Los comandos deben fallar con diagnósticos accionables.

Salida: checkout limpio que instala dependencias y ejecuta validaciones estructurales sin datos reales.

### S3 — Servicios locales en contenedores y puertos
Relacionado con SPEC §3, §6, §10, §11, §13, §14 y §15.

Implementar Compose como runtime canónico local. Todo el código Python debe ejecutarse dentro de contenedores para fijar la versión, dependencias y herramientas del proyecto; no se debe depender de la instalación de Python del usuario que haga fork. Los servicios persistentes y de infraestructura deben ejecutarse en contenedores separados: PostgreSQL, MinIO, Airflow cuando se active `orchestration`, MLflow cuando se active `mlops` y la aplicación Streamlit/API cuando se active `demo`. Los notebooks y comandos de desarrollo deben invocar el entorno Python contenerizado mediante Compose o una imagen de desarrollo reproducible.

Reglas:
- Comunicación entre servicios mediante nombres DNS internos de Compose; no usar puertos del host para conexiones entre contenedores.
- Publicar puertos del host solamente para interfaces que el desarrollador necesite.
- Bind local a `127.0.0.1` por defecto; no publicar bases de datos, MLflow o Airflow sin autenticación.
- Hacer configurables los puertos mediante variables de entorno y documentarlos.
- Añadir healthchecks, volúmenes persistentes, inicialización e idempotencia.

Asignación propuesta, elegida para evitar los puertos ocupados detectados:

| Servicio | Puerto interno | Puerto host propuesto | Perfil | Motivo |
|---|---:|---:|---|---|
| PostgreSQL | 5432 | 55432 | `core` | El host ya tiene ocupado 5432 |
| MinIO API | 9000 | 59000 | `core` | El host ya tiene ocupados 9000 y 9001 |
| MinIO Console | 9001 | 59001 | `core` | Separado del API y del MinIO existente |
| Airflow webserver | 8080 | 58080 | `orchestration` | El host ya tiene ocupado 8080 |
| Airflow metadata PostgreSQL | 5432 | sin publicación | `orchestration` | Acceso interno por red Compose |
| MLflow | 5000 | 55000 | `mlops` | El host ya tiene ocupados 5000 y 5001 |
| FastAPI | 8000 | 58000 | `demo` | El host reporta 8000 libre |
| Streamlit | 8501 | 58501 | `demo` | El host reporta 8501 libre |
| JupyterLab opcional | 8888 | 58888 | desarrollo | El host reporta 8888 libre; no arranca por defecto |

Antes de levantar cualquier perfil, `make doctor` debe comprobar disponibilidad de los puertos configurados y devolver una lista clara de conflictos. No asumir que un puerto libre durante esta inspección seguirá libre al iniciar.

Salida: `docker compose config` válido, perfiles aislables, servicios healthy y guía de puertos actualizada.

### S4 — Capacidad y procedencia de datos
Relacionado con SPEC §4 y fase 0.

Implementar `make doctor`, verificación de dependencias, `data/sources.yml`, políticas de licencias/procedencia, `make data-fetch` y colocación manual. Registrar resultados reales de capacidad de datasets y cuentas BI. No incluir datasets raw ni secretos.

Salida: informe de capacidad y procedencia reproducible, con fallos explícitos cuando una fuente no esté disponible.

### S5 — Generador sintético y contratos de datos
Relacionado con SPEC §4, §5 y §6.

Implementar perfiles smoke/full deterministas, entidades y relaciones, anomalías controladas, esquemas, validaciones y cuarentena. Crear contratos para dimensiones y hechos, restricciones, claves, granularidades y diccionario de datos.

Salida: generación smoke repetible, integridad referencial validada y reporte de calidad.

### S6 — Ingesta, transformación y almacén dimensional
Relacionado con SPEC §5 y §6.

Implementar ingesta pública, capas Bronze/Silver/Gold, PostgreSQL staging, dbt, marts Gold, idempotencia, auditoría, rollback de publicación Gold y pruebas de reconciliación. Añadir DAGs de Airflow sólo después de que el flujo local directo sea reproducible.

Salida: `make etl` y `make dbt-build` funcionan con fixtures y perfil smoke sin fan-out financiero.

### S7 — Estadística, EDA y notebooks reproducibles
Relacionado con SPEC §8 y fase 2.

Implementar notebooks parametrizados y lógica reusable en `src`, EDA, pruebas estadísticas justificadas, incertidumbre, tamaños de efecto, corrección múltiple, auditoría de leakage y exportación de resultados. Verificar ejecución desde entorno limpio.

Salida: hallazgos reales, notebooks ejecutados y limitaciones documentadas.

### S8 — Modelos de fraude
Relacionado con SPEC §9.1, §9.4 y fase 3.

Implementar baseline/challengers, split temporal o agrupado, pipeline sin leakage, métricas de clasificación, calibración, umbral basado en capacidad, SHAP, evaluación de subgrupos y tarjeta de modelo. La salida sólo puede recomendar `MANUAL_REVIEW` o `STANDARD_REVIEW`.

Salida: evaluación reproducible en holdout y modelo versionado sin rechazo automático.

### S9 — Riesgo, frecuencia, severidad y prima pura
Relacionado con SPEC §9.2 y fase 4.

Implementar modelos conscientes de exposición, frecuencia, severidad y prima pura, con calibración, métricas actuariales, diagnósticos, sensibilidad de cola y separación explícita de resultados franceses frente a conclusiones ecuatorianas.

Salida: comparación contra baselines y evaluación documentada sin afirmar validación ecuatoriana.

### S10 — Pronóstico financiero y de siniestros
Relacionado con SPEC §9.3 y fase 5.

Implementar series mensuales, baselines, backtesting rolling-origin, horizontes 1/3/6, intervalos de predicción y reporte de quiebres estructurales. La liquidez usa pagos; los costos incurridos quedan separados.

Salida: informe de backtest con cobertura de intervalos y metodología explícita.

### S11 — API, Streamlit y MLOps
Relacionado con SPEC §10, §9.4 y fase 7.

Implementar endpoints versionados, esquemas Pydantic, errores 422/503, correlation ID, límites de batch, disponibilidad de modelos, scoring reproducible, tracking MLflow, monitoreo de drift y páginas Streamlit con estados de carga/error/vacío.

Salida: pruebas de API y demo local conectada a modelos reales.

### S12 — Exportaciones BI y capability spikes
Relacionado con SPEC §11 y fase 6.

Generar exports CSV/Parquet, fixtures KPI, diccionario, medidas, relaciones y artefactos fuente. Ejecutar primero los capability spikes de Power BI y Tableau; documentar capacidades reales, bloqueos y pasos manuales. No afirmar publicación ni renderizado sin verificación.

Salida: `dashboards/README.md`, reconciliación entre herramientas y estado verificable de cada dashboard.

### S13 — CI, seguridad, rendimiento y entrega
Relacionado con SPEC §14, §15, §16, §17 y §18.

Completar CI Ubuntu, Ruff, pytest, dbt tests, smoke pipeline, secret/dependency scan, cobertura real, mediciones ETL/memoria/latencia, README, informes, capturas reales, plan Azure y checklist final. El despliegue Azure queda opcional y requiere aprobación independiente.

Salida: definición de terminado comprobada y lista de desviaciones, comandos, artefactos, enlaces y acciones manuales.

## Tasks

- T1 (S1): congelar alcance, idioma y convención de commits — ruta: documentación — commit: no aplica (slice documental completado).
- T2 (S2): crear base reproducible, configuración y comandos Make — ruta: estructura/configuración — commit: pendiente.
- T3 (S3): crear Compose por perfiles, healthchecks y `make doctor` con detección de puertos — ruta: `compose.yml`, infraestructura y documentación — commit: 20261126 implementar Compose y puertos.
- T4 (S4): validar capacidades, fuentes y procedencia — ruta: `data/`, `docs/` — commit: pendiente.
- T5 (S5): implementar generador y contratos de datos — ruta: `src/`, `configs/`, `database/`, `tests/` — commit: pendiente.
- T6 (S6): implementar ETL, dbt, warehouse y DAGs — ruta: `src/`, `dbt/`, `airflow/`, `database/`, `tests/` — commit: pendiente.
- T7 (S7): implementar estadística y notebooks reproducibles — ruta: `src/statistics/`, `notebooks/`, `reports/`, `tests/` — commit: pendiente.
- T8 (S8): implementar fraude y tarjeta de modelo — ruta: `src/models/`, `src/evaluation/`, `reports/model_cards/`, `tests/` — commit: pendiente.
- T9 (S9): implementar riesgo, severidad y prima pura — ruta: `src/models/`, `src/evaluation/`, `reports/model_cards/`, `tests/` — commit: pendiente.
- T10 (S10): implementar pronósticos y backtests — ruta: `src/models/`, `notebooks/`, `reports/`, `tests/` — commit: pendiente.
- T11 (S11): implementar API, Streamlit y MLOps — ruta: `src/api/`, `dashboards/streamlit/`, `infrastructure/`, `tests/` — commit: pendiente.
- T12 (S12): preparar BI y validar capacidades reales — ruta: `dashboards/`, `docs/`, `tests/` — commit: pendiente.
- T13 (S13): cerrar CI, seguridad, rendimiento y entrega — ruta: `.github/`, `docs/`, `reports/`, `README.md`, `tests/` — commit: pendiente.

## Log

- L1: "listo mi pana, a esos sepcs realizale el trabajo de separacion de tareas en slices para comenzar a trabajar, ojo revisa si en los specs se debe trabajar todo en contenedores de docker y debes revisar que puertos esten disponibles para que no choque nada"
- L2: Se inspeccionó el repositorio: solamente `SPEC.md` y `.atl/` estaban presentes; todavía no existe `compose.yml` ni código de aplicación.
- L3: Docker disponible: Docker 29.7.2 y Docker Compose v5.4.0.
- L4: Puertos ocupados detectados en el host: 5432, 9000, 9001, 8080, 8088, 5000, 5001, 6379, 27017, 27018, 4200, 8443, 9070, 8025, 1025, 1880, 3306, 7070, 8092, 80 y otros. También hay contenedores activos de otros proyectos.
- L5: Puertos libres durante la inspección: 8000, 8501, 7860, 3000, 8793, 8794, 8795, 8888, 5002 y 5050. La asignación propuesta usa puertos alternativos y debe volver a comprobarse justo antes de levantar servicios.
- L6: Decisión corregida: todo el código Python, notebooks y comandos Python deben ejecutarse dentro de contenedores para fijar la versión y dependencias del proyecto. Los servicios persistentes y de infraestructura también deben estar contenerizados; el host sólo orquesta Docker, edita archivos y ejecuta comandos de entrada como `docker compose`/`make` que delegan al contenedor. Compose es el runtime local canónico y los perfiles controlan el consumo de recursos.
- L7: "no todo lo de python que se corra desde contenedores, xq se debe usar la version de python adecuada para el proyecto y no podemos confiar en la version de pyhton del cliente que haga un fork del proyecto"
- L8: S1 verificado: `SPEC.md` y este plan fijan el alcance del proyecto, la separación entre código fuente en inglés y documentación/UI/commits en español, la convención de commits `yyyymmdd descripción`, la ejecución de Python dentro de contenedores y la prohibición de inventar evidencia. No se creó código porque S1 es un slice de alcance y reglas.
- L9: S2 verificado y confirmado en el commit `b1caccc`: imagen Python 3.12 construida, `uv.lock` generado, Compose válido, diagnóstico, pytest y Ruff exitosos. `.env.example` fue creado manualmente por el propietario.
- L10: S3 verificado: Compose core levantó PostgreSQL y MinIO con healthchecks healthy en 55432, 59000 y 59001; `make doctor` validó los puertos libres antes del arranque. La imagen de MinIO se fijó a una etiqueta existente después de que la etiqueta inicial no estuviera disponible.
