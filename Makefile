.PHONY: install test lint format run clean

install:
	pip install -e '.[dev]'

test:
	pytest tests/ -v --cov=reliability_layer

lint:
	ruff check . && ruff format --check .

format:
	ruff format .

run:
	uvicorn reliability_layer.api:app --reload --port 8000

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
