install:
	cd backend && pip install -r requirements/dev.txt
test:
	cd backend && pytest tests/ -v
