.PHONY: install test lint format run docker-up docker-down frontend

install:
	cd backend && pip install -r requirements/dev.txt && pip install -e . --no-deps
	cd frontend && npm install

test:
	cd backend && pytest tests/ -v

lint:
	cd backend && ruff check app cli tests && black --check app cli tests

format:
	cd backend && black app cli tests && ruff check --fix app cli tests

run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

extension:
	cd extension && npm install && npm run compile

extension-dev:
	cd extension && npm run watch

docker-up:
	docker compose up --build

docker-down:
	docker compose down
