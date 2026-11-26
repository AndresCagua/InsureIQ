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

### S14 — Datos públicos reales y dashboards utilizables
Relacionado con la solicitud posterior del propietario y SPEC §4, §6, §10 y §11.

> "crea todo lo necesario para los dashboard ademas hay que cargarle data real que sea publica y gratuita, encargate de eso, sube, carga y crea todo lo necesario que sin eso el proyecto esta sin terminar"

Incorporar una fuente gubernamental pública y gratuita, separada de los datos sintéticos de seguros cuando no represente claims de seguros. Registrar URL, licencia, fecha de descarga, hash y limitaciones; descargar dentro del flujo reproducible, transformar a un extract BI y conectar el dashboard local. No inventar datos de pólizas ni claims a partir de accidentes. Los archivos PBIX/TWB sólo se pueden entregar si se crean en las herramientas propietarias correspondientes; generar en su lugar un dashboard local verificable y paquetes de datos/modelo documentados.

Salida: fuente pública descargable, extract reproducible, dashboard local con selector de fuente y documentación de carga para Power BI/Tableau.

### S15 — Artefactos nativos de Power BI y Tableau
Relacionado con la autorización posterior del propietario para preparar publicación web.

> "papito hermoso y lindo los dashboards mas importantes y reales son los de Power Bi y tableau eso lo necesito pero para ayer"

Crear artefactos reproducibles para Power BI y Tableau usando los extracts públicos preparados, con modelo, medidas, páginas/hojas y documentación de carga. No afirmar publicación ni inventar una cuenta; la publicación web requiere una sesión autenticada y autorización explícita en la plataforma.

Salida: paquete Power BI documentado, workbook Tableau verificable, checklist de publicación y evidencia separada de lo que fue creado localmente frente a lo publicado.

### S16 — Benchmark público de fraude y predicción real
Relacionado con la solicitud posterior del propietario y SPEC §9.1, §9.4.

> "pana esto no puede ser posible \"Pero está bloqueado hasta tener datos públicos de fraude correctamente verificados.\" debemos buscar data publica y crear las predicciones reales no nos podemos quedar con un posble dato"

Incorporar el dataset público Auto Insurance Claims de Zenodo, registro 13381118, acceso abierto y licencia CC BY 4.0. Descargarlo reproduciblemente, verificar checksum, documentar la fuente, convertirlo a un formato procesable y entrenar/evaluar el baseline de fraude. Reportar que la etiqueta es la del dataset publicado y que el benchmark puede no representar Ecuador ni producción.

Salida: benchmark descargable y verificado, modelo entrenado con métricas observadas, reporte de limitaciones y endpoint de predicción habilitado sólo cuando el artefacto local exista.

## Tasks

- T1 (S1): congelar alcance, idioma y convención de commits — ruta: documentación — commit: no aplica (slice documental completado).
- T2 (S2): crear base reproducible, configuración y comandos Make — ruta: estructura/configuración — commit: pendiente.
- T3 (S3): crear Compose por perfiles, healthchecks y `make doctor` con detección de puertos — ruta: `compose.yml`, infraestructura y documentación — commit: 20261126 implementar Compose y puertos.
- T4 (S4): validar capacidades, fuentes y procedencia — ruta: `data/`, `docs/` — commit: 20261126 registrar contrato de procedencia.
- T5 (S5): implementar generador y contratos de datos — ruta: `src/`, `configs/`, `database/`, `tests/` — commit: 20261126 implementar generador sintético y contratos.
- T6 (S6): implementar ETL, dbt, warehouse y DAGs — ruta: `src/`, `dbt/`, `airflow/`, `database/`, `tests/` — commit: 20261126 implementar ETL y almacén dimensional.
- T7 (S7): implementar estadística y notebooks reproducibles — ruta: `src/statistics/`, `notebooks/`, `reports/`, `tests/` — commit: 20261126 implementar estadística y notebook de calidad.
- T8 (S8): implementar fraude y tarjeta de modelo — ruta: `src/models/`, `src/evaluation/`, `reports/model_cards/`, `tests/` — commit: 20261126 implementar baseline de fraude.
- T9 (S9): implementar riesgo, severidad y prima pura — ruta: `src/models/`, `src/evaluation/`, `reports/model_cards/`, `tests/` — commit: 20261126 implementar riesgo severidad y prima pura.
- T10 (S10): implementar pronósticos y backtests — ruta: `src/models/`, `notebooks/`, `reports/`, `tests/` — commit: 20261126 implementar pronóstico y backtesting.
- T11 (S11): implementar API, Streamlit y MLOps — ruta: `src/api/`, `dashboards/streamlit/`, `infrastructure/`, `tests/` — commit: 20261126 implementar API y demo Streamlit.
- T12 (S12): preparar BI y validar capacidades reales — ruta: `dashboards/`, `docs/`, `tests/` — commit: 20261126 preparar exports BI y capacidades.
- T13 (S13): cerrar CI, seguridad, rendimiento y entrega — ruta: `.github/`, `docs/`, `reports/`, `README.md`, `tests/` — commit: 20261126 cerrar CI seguridad rendimiento y entrega.
- T14 (S14): incorporar fuente pública real y dashboards conectados — ruta: `data/`, `src/`, `dashboards/`, `docs/`, `tests/` — commit: 20261126 incorporar datos publicos y dashboards.
- T15 (S15): crear artefactos Power BI/Tableau y checklist de publicación — ruta: `dashboards/powerbi/`, `dashboards/tableau/`, `docs/` — commit: 20261126 preparar dashboards Power BI y Tableau.
- T16 (S16): incorporar benchmark público de fraude y predicción real — ruta: `data/`, `src/`, `reports/`, `tests/`, `docs/` — commit: pendiente.

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
- L11: S4 parcial verificado: `data/sources.yml` define el contrato de procedencia sin inventar licencias, versiones, hashes ni cantidades; `data/README.md` documenta la descarga manual y la exclusión de raw; `make data-fetch` falla explícitamente con código 2 mientras no haya fuentes verificadas.
- L12: S5 verificado: el generador smoke determinista produjo 1.000 clientes, 1.200 vehículos, 2.500 pólizas y 500 siniestros dentro del contenedor; `data/contracts.yml` cargó correctamente; pytest y Ruff pasaron. Las anomalías raw quedan marcadas para cuarentena posterior.
- L13: S6 verificado: `make etl` transformó el perfil smoke en 1.000 `dim_customer`, 1.200 `dim_vehicle`, 2.500 `dim_policy` y 500 `fact_claim`; produjo `etl_manifest.json`, cuarentena y tablas procesadas. El esquema dimensional SQL, proyecto dbt y DAG declarativo quedaron creados; pytest y Ruff pasaron.
- L14: S7 verificado: se generó el informe `reports/data_quality.json` con 5 tablas y resumen descriptivo de 500 siniestros; el notebook `notebooks/01_data_quality.ipynb` es JSON válido; pytest y Ruff pasaron dentro del contenedor.
- L15: S8 verificado: se implementó un baseline logístico con preprocesamiento dentro del pipeline, split estratificado y métricas ROC-AUC/average precision; pytest pasó 2 pruebas y Ruff pasó. `make fraud-train` falla claramente con código 2 cuando no existe el benchmark verificado, sin inventar datos ni métricas.
- L16: S9 verificado: se implementaron baselines Poisson de frecuencia y Gamma de severidad a granularidad de póliza, con exposición explícita y prima pura; el smoke produjo 2.500 años de exposición y pérdida anual predicha de 1.243.481,57 USD sintéticos. pytest pasó 3 pruebas y Ruff pasó; se documentó que no es validación actuarial ecuatoriana.
- L17: S10 verificado: se implementó serie mensual de siniestros, baseline naive estacional de 12 meses y backtesting rolling-origin de 48 puntos; MAE 3,4375, RMSE 4,0850 y cobertura ilustrativa 0,9792. pytest pasó 3 pruebas y Ruff pasó; los intervalos se etiquetan como no calibrados.
- L18: S11 parcial verificado: FastAPI versionada, health/ready/models/fraud/forecasts/metrics, correlation ID, demo Streamlit y perfiles Compose `demo` quedaron creados; pytest pasó 4 pruebas, Ruff pasó, `/health` devolvió `{"status":"ok"}` y API/Streamlit iniciaron en 58000/58501. La inferencia queda 503 hasta registrar un benchmark/modelo verificado; MLflow registry completo queda pendiente.
- L19: S12 verificado para preparación BI: `make bi-data` generó exports CSV, `golden_kpis.json` y `manifest.json`; los KPI smoke fueron 2.500 pólizas, 500 claims, 1.235.504,93 USD reclamados y 3.316.175,82 USD de prima emitida sintética. `dashboards/README.md` y `docs/bi-capabilities.md` declaran que Power BI/Tableau Public aún no fueron publicados ni verificados.
- L20: S13 verificado: `make security-check` pasó; `make performance` midió el smoke en 2,08 s y 42.112 KB; pytest pasó 4 pruebas y Ruff pasó. `docs/implementation-status.md` y `docs/runbook.md` documentan estado, limitaciones y comandos; Azure/BI/MLflow no se reportan como completados.
- L21: El propietario solicitó incorporar datos reales públicos y completar dashboards. Se selecciona como primera fuente verificable el dataset gubernamental Vehicle Crashes in Iowa, identificado en el catálogo Data.gov/Iowa Data Hub, con descarga CSV y licencia CC BY 4.0 según la evidencia web consultada. Se mantendrá separado de claims sintéticos porque accidentes públicos no son registros de seguros.
- L22: S16 verificado: Zenodo 13381118 se descargó y convirtió a CSV; 10.000 filas, licencia CC BY 4.0, MD5 publicado validado y SHA256 local `c1c2ac62dd3cf2089d4fff20bc12ce375fb61890c9bde83e496925193931cb21`. `make fraud-train` pasó con ROC-AUC 0,9840985, average precision 0,9146387 y 2.500 filas de prueba; se persistieron `fraud_model.joblib` y `model_registry.json`. `/ready` devolvió 200 y `/api/v1/fraud/predict` produjo probabilidad 0,00210189 y `STANDARD_REVIEW` para el claim de prueba. Se mantienen las limitaciones del benchmark publicado y la prohibición de rechazo automático.