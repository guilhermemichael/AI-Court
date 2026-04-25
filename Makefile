SHELL := /bin/bash

.PHONY: setup up down logs migrate test lint typecheck frontend-typecheck clean

setup:
	cp -n backend/.env.example backend/.env || true
	docker compose build

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

migrate:
	docker compose exec backend alembic upgrade head

test:
	docker compose exec backend pytest -q

lint:
	docker compose exec backend ruff check app tests

typecheck:
	docker compose exec backend mypy app

frontend-typecheck:
	docker compose exec frontend npm run typecheck

clean:
	docker compose down -v --remove-orphans
