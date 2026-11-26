.DEFAULT_GOAL := help
SHELL := /bin/bash

IMAGE ?= insureiq-dev:local
COMPOSE ?= docker compose

.PHONY: help bootstrap doctor build test lint up down clean

help:
	@printf '%s\n' 'Targets: bootstrap doctor build test lint up down clean'

bootstrap:
	$(COMPOSE) build python

build:
	$(COMPOSE) build

doctor:
	$(COMPOSE) run --rm python python -m insureiq.cli doctor

test:
	$(COMPOSE) run --rm python pytest

lint:
	$(COMPOSE) run --rm python ruff check .

up:
	$(COMPOSE) --profile core up -d

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down --remove-orphans
