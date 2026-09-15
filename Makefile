.PHONY: help install run test lint format docker compose-up compose-down clean

help:
	@echo "Available commands:"
	@echo "  make install      Install application and development dependencies"
	@echo "  make run          Run the FastAPI application locally"
	@echo "  make test         Execute pytest test suite"
	@echo "  make lint         Run code linting with ruff"
	@echo "  make format       Format codebase using black and ruff"
	@echo "  make docker       Build local Docker image"
	@echo "  make compose-up   Start services via docker-compose"
	@echo "  make compose-down Stop docker-compose services"
	@echo "  make clean        Remove cache files and build artifacts"

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
	python -m pip install -e .[dev]

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

test:
	pytest -v

lint:
	ruff check .

format:
	black .
	ruff check --fix .

docker:
	docker build -t llm-inference-engine:latest .

compose-up:
	docker compose up -d --build

compose-down:
	docker compose down

infra-init:
	cd infra/terraform && terraform init

infra-plan:
	cd infra/terraform && terraform plan

infra-apply:
	cd infra/terraform && terraform apply -auto-approve

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

