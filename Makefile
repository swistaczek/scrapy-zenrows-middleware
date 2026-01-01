.PHONY: build clean lint lint-fix format test test-unit test-integration test-all test-cov publish publish-test

build:
	python -m build

clean:
	rm -rf dist build scrapy_zenrows.egg-info .pytest_cache .ruff_cache .coverage htmlcov
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true

lint:
	ruff check setup.py scrapy_zenrows examples tests

lint-fix:
	ruff check --fix setup.py scrapy_zenrows examples tests

format:
	ruff format setup.py scrapy_zenrows examples tests

# Run unit tests only (no API key required)
test:
	pytest tests -v --ignore=tests/integration

# Run unit tests (alias)
test-unit:
	pytest tests -v --ignore=tests/integration

# Run integration tests (requires ZENROWS_API_KEY)
test-integration:
	pytest tests/integration -v -m integration

# Run all tests including slow ones
test-all:
	pytest tests -v

# Run tests with coverage report
test-cov:
	pytest tests -v --ignore=tests/integration --cov=scrapy_zenrows --cov-report=term-missing --cov-report=html

# Publish to PyPI (requires ~/.pypirc or TWINE_USERNAME/TWINE_PASSWORD)
publish: clean build
	twine upload dist/*

# Publish to TestPyPI first (for testing)
publish-test: clean build
	twine upload --repository testpypi dist/*
