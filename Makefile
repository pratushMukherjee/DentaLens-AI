.PHONY: install dev seed api frontend test lint format clean

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

seed:
	python scripts/seed_vectorstore.py

api:
	uvicorn src.dentalens.api.app:create_app --factory --reload --host 0.0.0.0 --port 8000

frontend:
	streamlit run src/dentalens/frontend/app.py

test:
	pytest tests/ -v --cov=src/dentalens

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

clean:
	rm -rf data/chroma_store/ __pycache__ .pytest_cache .mypy_cache .coverage htmlcov
