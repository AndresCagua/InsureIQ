.DEFAULT_GOAL := help
SHELL := /bin/bash

IMAGE ?= insureiq-dev:local
COMPOSE ?= docker compose
PORTS_TO_CHECK ?= 55432 59000 59001 58080 55000 58000 58501 58888

.PHONY: help bootstrap doctor build test lint data-fetch up down clean

help:
	@printf '%s\n' 'Targets: bootstrap doctor build test lint data-fetch up down clean'

bootstrap:
	$(COMPOSE) build python

build:
	$(COMPOSE) build

doctor:
	@set -e; \
	conflicts=0; \
	for port in $(PORTS_TO_CHECK); do \
		if (echo >/dev/tcp/127.0.0.1/$$port) >/dev/null 2>&1; then \
			echo "Puerto ocupado: $$port"; conflicts=1; \
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

data-fetch:
	@echo 'No hay fuentes públicas verificadas para descargar todavía.' >&2
	@echo 'Completa data/sources.yml después de verificar licencia, versión y URL resuelta.' >&2
	@exit 2

up:
	$(MAKE) doctor
	$(COMPOSE) --profile core up -d

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down --remove-orphans
