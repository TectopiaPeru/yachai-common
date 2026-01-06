.PHONY: help install install-dev test lint format clean build upload

help:
	@echo "Available commands:"
	@echo "  install     Install package"
	@echo "  install-dev Install package with dev dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean build artifacts"
	@echo "  build       Build package"
	@echo "  upload      Upload to PyPI"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest -v

lint:
	flake8 yachai_common tests
	black --check yachai_common tests
	isort --check-only yachai_common tests

format:
	black yachai_common tests
	isort yachai_common tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

upload-test: build
	python -m twine upload --repository testpypi dist/*
