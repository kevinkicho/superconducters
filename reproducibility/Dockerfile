FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY superconductors ./superconductors
COPY run_pipeline.py app.py ./
COPY data ./data

RUN python -m pip install --no-cache-dir ".[api]"

ENTRYPOINT ["superconductors"]
CMD ["--help"]
