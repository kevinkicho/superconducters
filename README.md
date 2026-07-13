# Superconductor Candidate Toolkit

This repository provides a small supported application for loading, filtering,
ranking, estimating, and reporting on superconductor candidates. DFT and
external-integration prototypes remain available as optional modules.

The supported core is deliberately dependency-free. It reads the candidate
database, normalizes the legacy records into one domain model, applies screening
criteria, and returns ranked results through a CLI or FastAPI service.

> Predictions and simulations in this repository are research aids. They are not
> experimental confirmation of superconductivity.

## Quick start

Python 3.10 or newer is required.

```bash
python run_pipeline.py --min-tc 100 --max-pressure 200 --limit 10
python run_pipeline.py --min-tc 200 --json
```

The installed command is equivalent:

```bash
python -m pip install -e .
superconductors --help
```

## Installation profiles

Install only the capabilities you need:

```bash
# Core CLI only
python -m pip install -e .

# API and development tools
python -m pip install -e ".[api,dev]"

# Dashboard
python -m pip install -e ".[ui]"

# Complete research environment
python -m pip install -r requirements.txt
```

Available extras are `api`, `ui`, `ml`, `dft`, `integrations`, `reports`, and
`dev`. Keeping them separate prevents a basic database query from importing the
full ML, web, dashboard, and laboratory stack.

## Structure

```text
superconductors/
  cli.py          command-line interface
  config.py       environment-based settings
  generation.py   curated candidate hypotheses
  integrations.py external literature/materials adapters
  models.py       shared candidate model
  pipeline.py     deterministic screening workflow
  prediction.py   transparent formula heuristic
  query.py        raw-record filtering
  reporting.py    Markdown and optional PDF reports
  repository.py   validated, atomic JSON persistence
app.py            FastAPI service
run_pipeline.py   compatibility CLI wrapper
scripts/          optional and legacy research commands
data/             candidate and experimental data
docs/             research narratives and protocols
tests/            automated tests
```

`scripts/run_pipeline.py` is a compatibility wrapper. There is one canonical
pipeline implementation in `superconductors.pipeline`.

Feature-specific compatibility commands remain available:

```bash
python scripts/query_database.py --tc-min 100 --json
python scripts/predict_tc.py H3S LaH10
python scripts/generate_candidates.py --limit 3
python scripts/generate_report.py --min-tc 100
python scripts/arxiv_scraper.py "superconductivity hydrides" --max-results 5
python scripts/generate_changelog.py --limit 50
```

## API

Install the API profile and configure a secret key:

```bash
python -m pip install -e ".[api]"
set SUPERCONDUCTOR_API_KEY=replace-with-a-long-random-value
uvicorn app:app --reload --port 8000
```

Send the key in the `X-API-Key` header. The API does not ship with default
credentials. Optional login configuration uses:

- `SUPERCONDUCTOR_ADMIN_USERNAME`
- `SUPERCONDUCTOR_ADMIN_PASSWORD`
- `SUPERCONDUCTOR_API_KEY`

Interactive API documentation is available at `http://localhost:8000/docs`.

## Configuration

The core application recognizes:

- `DATA_DIR`: directory containing `superconductor_database.json`
- `OUTPUT_DIR`: generated-output directory
- `SUPERCONDUCTOR_API_KEY`: API authentication secret
- `CLOUD_LAB_API_URL`: optional external laboratory endpoint

Generated output, built documentation, logs, virtual environments, and local
agent state are excluded from source control.

## Development

```bash
python -m pip install -e ".[api,dev]"
ruff check superconductors app.py run_pipeline.py streamlit_dashboard.py
pytest
python -m compileall -q superconductors app.py run_pipeline.py scripts tests
```

CI runs linting, tests, and coverage on Python 3.10–3.12.

## Optional research modules

The dashboard is a thin UI over the supported repository, pipeline, and
prediction services:

```bash
streamlit run streamlit_dashboard.py
```

The DFT and specialized experimental helpers remain optional research modules.
They may require models, external executables, instruments, network credentials,
or dependency extras. Their outputs should identify provenance as measured,
DFT-calculated, ML-predicted, or simulated.

External-service behavior is explicit:

- arXiv uses its Atom API and converts transport failures into a stable integration error.
- Materials Project uses the official `mp-api` summary search client.
- ICSD access requires an explicitly configured `ICSD_API_URL`; no unofficial endpoint is assumed.
- Tests inject transports and never make live network requests.

Quantum ESPRESSO execution requires a structure JSON file and an explicit confirmation flag:

```bash
python dft_calculator.py structure.json --execute
```

Without `--execute`, the DFT command exits before launching external binaries.

Their historical tests remain under `tests/` but are not part of the core CI
gate until each prototype is migrated behind a stable interface.

The reproducibility folder contains Docker, Conda, and Makefile examples for the
broader scientific environment.

## License

See [LICENSE](LICENSE).
