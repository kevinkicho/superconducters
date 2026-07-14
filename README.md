# Superconductor Candidate Toolkit

This repository provides a small supported application for loading, filtering,
ranking, estimating, and reporting on superconductor candidates. DFT and
external-integration prototypes remain available as optional modules.

The supported core is deliberately dependency-free. It reads the candidate
database, normalizes the legacy records into one domain model, applies screening
criteria, and returns ranked results through a CLI or FastAPI service.

> Predictions and simulations in this repository are research aids. They are not
> experimental confirmation of superconductivity.

See [`docs/SCIENTIFIC_SCOPE.md`](docs/SCIENTIFIC_SCOPE.md) for the executable
evidence standard and external scientific gates. Retracted and disputed records
are retained for auditability but excluded from default screening.
Progress against the nine principal discovery barriers is tracked in
[`docs/DISCOVERY_GAP_TRACKER.md`](docs/DISCOVERY_GAP_TRACKER.md).

## Quick start

Python 3.10 or newer is required.

```bash
python run_pipeline.py --min-tc 100 --max-pressure 200 --limit 10
python run_pipeline.py --min-tc 200 --json
python run_pipeline.py --validate
python run_pipeline.py --evidence-audit unclassified --limit 20 --json
python run_pipeline.py --objective ambient-room-temperature --json
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

Available extras are `api`, `ui`, `ml`, `analysis`, `dft`, `reports`, and `dev`.
Keeping them separate prevents a basic database query from importing the full
ML, web, dashboard, and scientific-analysis stack.

## Structure

```text
superconductors/
  api/
    app.py        FastAPI application factory
    auth.py       API-key and expiring-token authentication
    routes.py     HTTP endpoints
    schemas.py    validated request and response contracts
    services.py   application workflows and stable identities
    store.py      transactional SQLite application state
  analysis.py     deterministic sensitivity-analysis helpers
  announcements.py provenance-aware screening summaries
  cli.py          command-line interface
  config.py       environment-based settings
  evidence.py     evidence classification and quarantine
  experiments.py  raw-data manifests and replication checks
  dft/
    inputs.py     pure Quantum ESPRESSO input rendering
    parsing.py    output parsers and Tc calculation
    runner.py     explicit, injectable process execution
    ml.py         optional lazy Torch fine-tuning helpers
  generation.py   curated candidate hypotheses
  integrations.py external literature/materials adapters
  models.py       shared candidate model
  multifidelity.py optional Gaussian Process implementation
  objectives.py   explicit success gates and Pareto screening
  pipeline.py     deterministic screening workflow
  prediction.py   bounded benchmark lookup and opt-in heuristic
  query.py        raw-record filtering
  reporting.py    Markdown and optional PDF reports
  repository.py   validated, atomic JSON persistence
  scientific_workflow.py structure-to-experiment evidence gates
  validation.py   database quality checks and summaries
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

Raw experimental artifacts can be registered with a content hash and
calibration reference. Registration does not mark a result as confirmed:

```bash
python scripts/ingest_experiment.py raw.csv --sample-id sample-1 --formula H3S \
  --laboratory "Independent Lab A" --pressure-gpa 155 \
  --measurement-type resistivity --calibration-reference calibration-2026-01
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

`POST /login` accepts credentials in a JSON body and returns a signed access
token that expires after one hour. Login attempts are rate limited. The static
API key remains valid for service-to-service clients.

Research records in `data/superconductor_database.json` are read-only from the
API. Candidates created through the API and synthesis submissions are stored
transactionally in `OUTPUT_DIR/application.sqlite3`. Existing research records
receive deterministic UUIDs without rewriting the source dataset. New clients
should submit UUID candidate IDs; positive numeric IDs remain a compatibility
bridge for older clients.

The application database carries an explicit schema version and refuses newer
or incomplete schemas instead of failing later during a request. Authenticated
clients can read persisted submissions from `GET /submissions`. Candidate and
submission list endpoints accept bounded `offset` and `limit` pagination.
SQLite runs in write-ahead logging mode with a bounded busy timeout; concurrent
candidate and submission writes are covered by contention tests.

`temperature` remains a deprecated response and request alias for `tc`. New
clients should use `tc` to avoid confusion with synthesis temperature.

Interactive API documentation is available at `http://localhost:8000/docs`.

## Configuration

The core application recognizes:

- `DATA_DIR`: directory containing `superconductor_database.json`
- `OUTPUT_DIR`: generated-output directory
- `SUPERCONDUCTOR_API_KEY`: API authentication secret
- `CLOUD_LAB_API_URL`: reserved configuration only; no cloud-lab submission
  provider is implemented

`--validate` performs a read-only schema, duplicate, encoding, provenance, and
evidence-status check. Conservative inference classifies the current 204-record
legacy database as 10 measured records, 27 unverified calculations, 159 cited
records awaiting manual evidence classification, and 8 records linked to
retracted claims. A citation alone is not treated as proof of measurement. None
meets the default independently replicated, ambient-pressure room-temperature
objective. Raw records are retained rather than silently rewritten;
quarantined records are excluded from normal ranking.

`--evidence-audit` produces a deterministic, read-only review queue. Use
`unclassified` to prioritize missing evidence labels, `quarantined` to inspect
disputed and retracted claims, or `all` for a compact inventory. Each item keeps
its original record index, citation, DOI, inferred classification, and reason so
that a reviewed classification can be traced back to the source record.

Generated output, built documentation, logs, virtual environments, and local
agent state are excluded from source control.

## Development

```bash
python -m pip install -e ".[api,dev]"
ruff check superconductors app.py run_pipeline.py streamlit_dashboard.py
ruff format --check .
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

All maintained tests under `tests/` are discovered automatically by the CI gate.

The reproducibility folder contains Docker, Conda, and Makefile examples for the
broader scientific environment.

## License

See [LICENSE](LICENSE).
