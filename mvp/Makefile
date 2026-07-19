# VNBOT — Makefile for common dev commands
# Usage: make <target>

.PHONY: help install dev build test test-cov lint typecheck migrate migrate-new seed e2e e2e-ui axe clean

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	 awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies (frontend + backend)
	pnpm install
	uv sync --all-packages
	pnpm exec playwright install --with-deps chromium

dev:  ## Start frontend + backend in parallel (with hot reload)
	@echo "Starting VNBOT dev environment..."
	@trap 'kill 0' EXIT; \
	pnpm --filter ./apps/web dev & \
	uv run uvicorn services.api.app.main:app --reload --port 8000 --app-dir services/api & \
	wait

build:  ## Build all packages for production
	pnpm -r run build

test:  ## Run all unit tests
	pnpm -r run test
	uv run pytest services/api/tests/unit packages/domain/tests

test-cov:  ## Run tests with coverage report
	pnpm -r run test:unit
	uv run pytest services/api/tests/unit --cov=services/api/app --cov-report=html

lint:  ## Run all linters
	pnpm -r run lint
	uv run ruff check services/api packages/domain
	uv run mypy services/api packages/domain

typecheck:  ## TypeScript strict typecheck
	pnpm -r run typecheck

migrate:  ## Run database migrations
	uv run alembic upgrade head -c services/api/alembic.ini

migrate-new:  ## Create new migration (usage: make migrate-new name="add_xxx")
	uv run alembic revision --autogenerate -m "$(name)" -c services/api/alembic.ini

seed:  ## Seed database with demo data (for dev only)
	uv run python -m services.api.app.scripts.seed

e2e:  ## Run Playwright E2E tests
	pnpm e2e

e2e-ui:  ## Run Playwright E2E tests with UI
	pnpm exec playwright test --ui

axe:  ## Run axe-core accessibility scan
	pnpm exec playwright test --grep "@axe"

clean:  ## Clean all build artifacts
	rm -rf **/node_modules **/dist **/.turbo **/__pycache__ **/.pytest_cache **/.coverage **/htmlcov
	rm -rf data/*.db data/files/*
