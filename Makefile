.PHONY: install test lint format run docker-up docker-down frontend

install:
	cd backend && pip install -r requirements/dev.txt
	cd frontend && npm install

test:
	cd backend && pytest tests/ -v

lint:
	cd backend && ruff check app tests && black --check app tests

format:
	cd backend && black app tests && ruff check --fix app tests

run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build

docker-down:
	docker compose down
