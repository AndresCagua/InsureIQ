.DEFAULT_GOAL := help
SHELL := /bin/bash

IMAGE ?= insureiq-dev:local
COMPOSE ?= docker compose
PORTS_TO_CHECK ?= 55432 59000 59001 58080 55000 58000 58501 58888
PROFILE ?= smoke

.PHONY: help bootstrap doctor build test lint security-check performance data-fetch data-generate public-data public-fraud etl statistics notebooks fraud-train risk-train forecast bi-data api streamlit dbt-build up down clean

help:
	@printf '%s\n' 'Targets: bootstrap doctor build test lint security-check performance data-fetch data-generate public-data public-fraud etl statistics notebooks fraud-train risk-train forecast bi-data api streamlit dbt-build up down clean'

bootstrap:
	$(COMPOSE) build python

build:
	$(COMPOSE) build

doctor:
	@set -e; \
	conflicts=0; \
	owned_by_compose() { \
		case "$$1" in \
			55432) service=postgres; internal=5432 ;; \
			59000) service=minio; internal=9000 ;; \
			59001) service=minio; internal=9001 ;; \
			58000) service=api; internal=8000 ;; \
			58501) service=streamlit; internal=8501 ;; \
			*) return 1 ;; \
		esac; \
		$(COMPOSE) port "$$service" "$$internal" 2>/dev/null | grep -qE ":$$1$$"; \
	}; \
	for port in $(PORTS_TO_CHECK); do \
		if (echo >/dev/tcp/127.0.0.1/$$port) >/dev/null 2>&1; then \
			if owned_by_compose "$$port"; then \
				echo "Puerto ocupado por InsureIQ: $$port"; \
			else \
				echo "Puerto ocupado: $$port"; conflicts=1; \
			fi; \
		else \
			echo "Puerto disponible: $$port"; \
		fi; \
	done; \
	if [ $$conflicts -ne 0 ]; then \
		echo 'Hay conflictos de puertos. Ajusta las variables *_HOST_PORT antes de iniciar Compose.' >&2; \
		exit 1; \
	fi
	$(COMPOSE) run --rm python python -m insureiq.cli doctor

test:
	$(COMPOSE) run --rm python pytest

lint:
	$(COMPOSE) run --rm python ruff check .

security-check:
	@! git grep -nE '(AKIA[0-9A-Z]{16}|BEGIN (RSA|EC|OPENSSH) PRIVATE KEY|password[[:space:]]*=[[:space:]]*[^$#[:space:]]+)' -- ':!*.lock' ':!.env.example' || (echo 'Posible secreto encontrado' >&2; exit 1)
	@echo 'Secret scan estructural: OK'

performance:
	@/usr/bin/time -f 'elapsed_seconds=%e\nmax_memory_kb=%M' -o /tmp/insureiq-performance.txt $(MAKE) data-generate PROFILE=smoke
	@cat /tmp/insureiq-performance.txt
	@echo 'Medición temporal guardada en /tmp/insureiq-performance.txt'

data-fetch:
	@echo 'No hay fuentes públicas verificadas para descargar todavía.' >&2
	@echo 'Completa data/sources.yml después de verificar licencia, versión y URL resuelta.' >&2
	@exit 2

data-generate:
	$(COMPOSE) run --rm python python -m insureiq.cli generate --profile $(PROFILE)

public-data:
	$(COMPOSE) run --rm python python -m insureiq.cli public-data

public-fraud:
	$(COMPOSE) run --rm python python -m insureiq.cli public-fraud

etl:
	$(COMPOSE) run --rm python python -m insureiq.cli etl

statistics:
	$(COMPOSE) run --rm python python -m insureiq.cli stats

notebooks:
	@echo 'Ejecuta notebooks dentro del contenedor cuando JupyterLab esté habilitado.'
	$(COMPOSE) run --rm python python -m insureiq.cli stats

fraud-train: public-fraud
	$(COMPOSE) run --rm python python -m insureiq.cli fraud --benchmark data/processed/public_vehicle_fraud_benchmark.csv --report reports/fraud_metrics.json

risk-train:
	$(COMPOSE) run --rm python python -m insureiq.cli risk --report reports/risk_metrics.json

forecast:
	$(COMPOSE) run --rm python python -m insureiq.cli forecast --report reports/forecast_metrics.json

bi-data:
	$(COMPOSE) run --rm python python -m insureiq.cli bi

api:
	$(COMPOSE) --profile demo up api

streamlit:
	$(COMPOSE) --profile demo up streamlit

dbt-build:
	@echo 'dbt se habilitará al conectar el perfil de base de datos del almacén.'
	@exit 2

up:
	$(MAKE) doctor
	$(COMPOSE) --profile core up -d

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down --remove-orphans
