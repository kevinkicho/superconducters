# Reproducibility Makefile for Superconductor Discovery Pipeline

.PHONY: help setup run test clean docker-build docker-run

help:
	@echo "Available targets:"
	@echo "  setup       - Create conda environment and install dependencies"
	@echo "  run         - Run the full pipeline"
	@echo "  test        - Run unit tests"
	@echo "  clean       - Remove generated files and caches"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run pipeline in Docker container"

setup:
	conda env create -f environment.yml
	@echo "Environment created. Activate with: conda activate superconductor"

run:
	python run_pipeline.py --export-format json --export-format csv

test:
	pytest tests/ -v --cov=.

clean:
	rm -rf __pycache__ .pytest_cache
	rm -rf exports/
	rm -rf output/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

docker-build:
	docker build -t superconductor-pipeline .

docker-run:
	docker run --rm -v $(PWD)/output:/app/output superconductor-pipeline python run_pipeline.py
