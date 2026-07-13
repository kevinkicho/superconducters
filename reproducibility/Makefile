ROOT := ..
PYTHON := $(ROOT)/.venv/Scripts/python.exe
ifeq ($(OS),Windows_NT)
	RUN_PYTHON := $(PYTHON)
else
	PYTHON := $(ROOT)/.venv/bin/python
	RUN_PYTHON := $(PYTHON)
endif

.PHONY: help setup run test lint clean docker-build docker-run

help:
	@echo "setup run test lint clean docker-build docker-run"

setup:
	python -m venv $(ROOT)/.venv
	$(RUN_PYTHON) -m pip install -e "$(ROOT)[api,dev]"

run:
	$(RUN_PYTHON) $(ROOT)/run_pipeline.py --limit 20

test:
	$(RUN_PYTHON) -m pytest $(ROOT)/tests/test_run_pipeline.py $(ROOT)/tests/test_repository.py $(ROOT)/tests/test_api_endpoints.py

lint:
	$(RUN_PYTHON) -m ruff check $(ROOT)/superconductors $(ROOT)/app.py $(ROOT)/run_pipeline.py

clean:
	$(RUN_PYTHON) -c "import shutil; [shutil.rmtree(path, ignore_errors=True) for path in ['../.pytest_cache', '../htmlcov', '../output']]"

docker-build:
	docker build -f Dockerfile -t superconductor-toolkit $(ROOT)

docker-run:
	docker run --rm superconductor-toolkit --limit 10
