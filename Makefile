.PHONY: help run-api run-worker run-beat install clean test quality schemas schemas-v1 generate-orders-schemas-v1 generate-analytics-schemas-v1 db initialize-db migrate seed-data services-up services-down  monitor open-docs

# Variables
DATABASE_URL := postgres://user:pass@localhost:5432/restaurant
REDIS_URL := redis://localhost:6379/0
LOG_LEVEL := debug
REDIS_HOST := localhost
REDIS_PORT := 6379
REDIS_DB := 0
REDIS_EXPIRATION_TIME := 3600
PYTHON := poetry run
UVICORN := $(PYTHON) uvicorn
PORT := 8090

# Help command
help: ## Display this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# App commands
run-api: ## Start development server with auto-reload
	DATABASE_URL=$(DATABASE_URL) \
	REDIS_URL=$(REDIS_URL) \
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port $(PORT)

run-worker: ## Start Celery worker for development
	DATABASE_URL=$(DATABASE_URL) \
	REDIS_URL=$(REDIS_URL) \
	$(PYTHON) python -m celery -A app.core.celery worker --loglevel=$(LOG_LEVEL) --concurrency=1

run-beat: ## Start Celery beat only for development
	DATABASE_URL=$(DATABASE_URL) \
	REDIS_URL=$(REDIS_URL) \
	$(PYTHON) python -m celery -A app.core.celery beat --loglevel=$(LOG_LEVEL)

install: ## Install project dependencies
	poetry install

clean: ## Remove build artifacts and cache directories
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache

# Testing & linting
test: ## Run test suite
	$(PYTHON) pytest -s

quality: ## Run code quality checks
	$(PYTHON) ruff check .
	$(PYTHON) mypy app

# Schema generation
schemas: schemas-v1 ## Generate all API schemas

schemas-v1: generate-orders-schemas-v1 generate-analytics-schemas-v1 ## Generate v1 API schemas

generate-orders-schemas-v1: ## Generate order schemas for v1 API
	$(PYTHON) datamodel-codegen \
	  --input openapi/v1/orders.yaml \
	  --output app/api/v1/orders/schemas.py \
	  --class-name OrderSchema \
	  --use-schema-description \
	  --input-file-type openapi

generate-analytics-schemas-v1: ## Generate analytics schemas for v1 API
	$(PYTHON) datamodel-codegen \
	  --input openapi/v1/analytics.yaml \
	  --output app/api/v1/analytics/schemas.py \
	  --class-name AnalyticsSchema \
	  --use-schema-description \
	  --input-file-type openapi

# Database commands
db: initialize-db migrate ## Run all database commands

initialize-db: ## Initialize Aerich and create initial migration
	DATABASE_URL=$(DATABASE_URL) $(PYTHON) aerich init -t app.core.database.TORTOISE_ORM
	DATABASE_URL=$(DATABASE_URL) $(PYTHON) aerich init-db

migrate: ## Generate and apply migrations
	DATABASE_URL=$(DATABASE_URL) $(PYTHON) aerich migrate
	DATABASE_URL=$(DATABASE_URL) $(PYTHON) aerich upgrade

seed-data:
	DATABASE_URL=$(DATABASE_URL) $(PYTHON) python -m scripts.seed_data

# Docker commands
services-up: ## Start all required services with Docker
	docker-compose up -d --build

services-down: ## Stop all Docker services
	docker-compose down
	docker-compose -f docker-compose.monitoring.yml down

monitor: ## Start monitoring stack
	docker-compose -f docker-compose.monitoring.yml up -d

open-docs: ## Open FastAPI docs in browser
	@python -c "import webbrowser; webbrowser.open('http://localhost:8000/docs')"

.DEFAULT_GOAL := help
