# User Manual: Room-Temperature Superconductor Discovery Pipeline

## Introduction

This manual describes the installation, configuration, and operation of the autonomous materials discovery pipeline for room-temperature superconductors. The pipeline integrates machine learning, density functional theory (DFT) calculations, cloud lab integration, and continuous learning to accelerate the discovery and manufacturing of novel superconducting compounds.

## Installation

### Prerequisites
- Python 3.9 or later
- Git
- (Optional) Quantum ESPRESSO for DFT calculations
- (Optional) Access to cloud lab APIs (e.g., Emerald Cloud Lab)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/superconductor-pipeline.git
   cd superconductor-pipeline
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Install Quantum ESPRESSO and ensure `pw.x` is in your PATH.

## Configuration

All configuration is done via environment variables or a `.env` file in the project root. Copy the template:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | API key for LLM-based hypothesis generation | Yes |
| `SUPERCON_API_KEY` | API key for SuperCon database access | No (falls back to local data) |
| `EMERALD_CLOUD_API_KEY` | API key for cloud lab submission | No (falls back to simulation) |
| `DFT_EXECUTABLE` | Path to Quantum ESPRESSO `pw.x` | No (DFT disabled if not set) |
| `ADMIN_USER` | Username for admin role (RBAC) | No |
| `ADMIN_PASS` | Password for admin role | No |
| `RESEARCHER_USER` | Username for researcher role | No |
| `RESEARCHER_PASS` | Password for researcher role | No |
| `VIEWER_USER` | Username for viewer role | No |
| `VIEWER_PASS` | Password for viewer role | No |

### Role-Based Access Control (RBAC) with OAuth2

The Streamlit dashboard supports OAuth2 authentication via providers such as Google, GitHub, and Microsoft Azure AD. This provides secure, token-based access without managing passwords.

#### Configuration

1. Register an OAuth2 application with your provider (e.g., Google Cloud Console, GitHub OAuth Apps).
2. Set the following environment variables in your `.env` file:

| Variable | Description | Required |
|----------|-------------|----------|
| `OAUTH2_CLIENT_ID` | Client ID from the OAuth2 provider | Yes |
| `OAUTH2_CLIENT_SECRET` | Client secret from the OAuth2 provider | Yes |
| `OAUTH2_AUTHORIZE_URL` | Authorization endpoint (e.g., `https://accounts.google.com/o/oauth2/auth`) | Yes |
| `OAUTH2_TOKEN_URL` | Token endpoint (e.g., `https://oauth2.googleapis.com/token`) | Yes |
| `OAUTH2_USERINFO_URL` | User info endpoint (e.g., `https://www.googleapis.com/oauth2/v2/userinfo`) | Yes |
| `OAUTH2_SCOPE` | Space-separated list of scopes (e.g., `openid email profile`) | Yes |
| `OAUTH2_REDIRECT_URI` | Callback URL (e.g., `https://your-app.com/oauth2/callback`) | Yes |

3. The dashboard will automatically redirect unauthenticated users to the OAuth2 provider's login page.
4. After successful authentication, the user's email and roles are extracted from the user info response.

#### Role Mapping

Roles are assigned based on the user's email domain or a predefined mapping file. By default:
- Users with email ending in `@admin.org` are assigned the **Admin** role.
- Users with email ending in `@researcher.org` are assigned the **Researcher** role.
- All other authenticated users are assigned the **Viewer** role.

You can customize role mapping by setting the `OAUTH2_ROLE_MAPPING` environment variable to a JSON file path containing a dictionary of email patterns to roles.

#### Fallback to Environment Variable Authentication

If OAuth2 is not configured (i.e., `OAUTH2_CLIENT_ID` is not set), the dashboard falls back to the legacy environment variable authentication using `ADMIN_USER`, `ADMIN_PASS`, etc. as described in the Configuration section above.

## Running the Pipeline

### Basic Execution

Run the main pipeline with default settings:

```bash
python run_pipeline.py
```

This will:
1. Scrape arXiv for recent superconductor papers.
2. Generate candidate materials using LLM and random structure search.
3. Screen candidates with machine learning models.
4. Perform DFT validation (if configured).
5. Rank candidates using TOPSIS multi-criteria decision analysis.
6. Submit top candidates to cloud lab (if configured) or simulate experiments.
7. Update `candidate_materials.md` with results.
8. Retrain models with new data.

### Advanced Options

```bash
python run_pipeline.py --candidates 100 --dft-only --skip-cloud
```

- `--candidates N`: Number of candidates to generate (default: 50).
- `--dft-only`: Run only DFT calculations on existing candidates.
- `--skip-cloud`: Skip cloud lab submission.
- `--retrain`: Force retraining of ML models.

### Continuous Autonomous Loop

The pipeline can run on a schedule using GitHub Actions. The workflow `.github/workflows/ci.yml` includes a scheduled trigger (daily at midnight). To enable, push to the main branch and ensure secrets are set in the repository settings.

## Interpreting Results

### Candidate Materials Table

The file `candidate_materials.md` contains a table with all generated candidates and their properties:

| Column | Description |
|--------|-------------|
| Formula | Chemical formula of the candidate |
| Predicted Tc (K) | Critical temperature predicted by ML |
| DFT Tc (K) | Critical temperature from DFT (if available) |
| DFT Consistency | Agreement between ML and DFT predictions |
| SuperCon Validation | Comparison with known superconductor database |
| DecisionRank | TOPSIS rank (lower is better) |
| PredictedStructure | Crystal structure from random search |

### Dashboard

Launch the Streamlit dashboard:

```bash
streamlit run dashboard.py
```

The dashboard provides:
- Real-time pipeline status
- Interactive candidate exploration
- Feedback submission (admin/researcher)
- Performance metrics

### Collaboration Features

The dashboard now supports real-time collaboration via WebSockets. Multiple users can view, annotate, and interact with plots simultaneously.

#### Enabling Collaboration

1. Ensure the WebSocket server is running (it starts automatically with the dashboard).
2. Open the dashboard in multiple browser tabs or on different machines.
3. Navigate to the **Collaboration Hub** tab.

#### Features

- **Shared Plot Area**: All users see the same interactive plot. Any user can select data points, zoom, or pan, and changes are broadcast to all connected clients.
- **Annotations**: Users can add text annotations to the plot. Annotations are visible to all users in real time.
- **Role-Based Access**: The collaboration hub respects the user's role (viewer, contributor, admin). Only contributors and admins can add annotations or submit sample requests.

#### Usage

1. In the Collaboration Hub tab, you will see a shared plot of candidate materials.
2. To annotate, select a data point and click "Add Annotation" or use the annotation input box.
3. All changes are synchronized across sessions.

#### Troubleshooting

- If the plot does not update, check that the WebSocket server is running (port 8765 by default).
- Ensure all users are connected to the same network and the WebSocket server is accessible.

### Logs

Pipeline logs are written to `pipeline.log`. Use `tail -f pipeline.log` to monitor progress.

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Ensure virtual environment is activated and dependencies installed. |
| API key errors | Check `.env` file and environment variables. |
| DFT calculation fails | Verify Quantum ESPRESSO installation and path in `DFT_EXECUTABLE`. |
| Cloud lab submission fails | Check network connectivity and API key validity. |
| Dashboard authentication loop | Clear browser cookies and restart dashboard. |

### Debugging

Set `LOG_LEVEL=DEBUG` in `.env` for verbose output. Run individual components:

```bash
python -m src.scraper  # Test arXiv scraping
python -m src.dft_calculator --candidate "YBa2Cu3O7"  # Test DFT on a specific compound
```

## Examples

### Example 1: Quick Start

```bash
# Install and run with default settings
python run_pipeline.py
```

Expected output (first few lines):
```
[INFO] Starting pipeline...
[INFO] Scraping arXiv for superconductor papers...
[INFO] Found 12 new papers.
[INFO] Generating candidates...
...
```

### Example 2: Custom Candidate Generation

```bash
python run_pipeline.py --candidates 200 --skip-cloud
```

This generates 200 candidates without cloud lab submission. Results are saved to `candidate_materials.md`.

### Example 3: DFT Validation Only

```bash
python run_pipeline.py --dft-only
```

Runs DFT on all candidates in `candidate_materials.md` that lack DFT results.

## Tutorial

This tutorial walks you through a complete example of using the Room-Temperature Superconductor Discovery Pipeline, from installation to viewing results.

### Step 1: Installation

Follow the installation steps in the [Installation](#installation) section. Ensure you have Python 3.9+ and Git installed.

![Installation](screenshots/installation.png)

### Step 2: Configuration

Copy the `.env.example` to `.env` and set your API keys. For this tutorial, you only need `OPENAI_API_KEY`. Set `LOG_LEVEL=INFO`.

![Configuration](screenshots/configuration.png)

### Step 3: Running the Pipeline

Run the pipeline with default settings:

```bash
python run_pipeline.py
```

You will see output similar to:

```
[INFO] Starting pipeline...
[INFO] Scraping arXiv for superconductor papers...
[INFO] Found 12 new papers.
[INFO] Generating candidates...
...
[INFO] Pipeline complete. Results saved to candidate_materials.md.
```

![Pipeline Output](screenshots/pipeline_output.png)

### Step 4: Viewing Results

Open `candidate_materials.md` to see the generated candidates. Launch the dashboard:

```bash
streamlit run dashboard.py
```

Navigate to the Dashboard Overview tab to explore candidates interactively.

![Dashboard Overview](screenshots/dashboard_overview.png)

### Step 5: Next Steps

- Review the [Interpreting Results](#interpreting-results) section for detailed explanations.
- Try the advanced options described in [Running the Pipeline](#running-the-pipeline).
- Contribute feedback via the dashboard to improve the ML models.

## Support

For issues, open a GitHub issue or contact the development team.

## API Reference

### Live API Endpoint

The pipeline can be accessed via a REST API at:

```
https://api.superconductor-pipeline.example.com
```

(Replace with actual deployed URL.)

### Authentication

All API requests require an API key passed via the `X-API-Key` header.

```bash
curl -H "X-API-Key: YOUR_API_KEY" https://api.superconductor-pipeline.example.com/health
```

To obtain an API key, contact the development team or set the `PIPELINE_API_KEYS` environment variable on the server.

### Example Requests

#### Health Check

```bash
curl -H "X-API-Key: YOUR_API_KEY" https://api.superconductor-pipeline.example.com/health
```

Response:
```json
{"status": "ok", "service": "superconductor-pipeline"}
```

#### Trigger Pipeline

```bash
curl -X POST -H "X-API-Key: YOUR_API_KEY" https://api.superconductor-pipeline.example.com/run-pipeline
```

Response:
```json
{"message": "Pipeline triggered. Check logs for progress."}
```

#### Run Benchmark

```bash
curl -H "X-API-Key: YOUR_API_KEY" https://api.superconductor-pipeline.example.com/benchmark
```

Response:
```json
{"message": "Benchmark completed. Check data/model_performance_log.json"}
```

#### Get Candidates

```bash
curl -H "X-API-Key: YOUR_API_KEY" https://api.superconductor-pipeline.example.com/candidates
```

Response:
```json
{"candidates": ["LaH10", "H3S", ...], "count": 2}
```

#### Submit Candidate

```bash
curl -X POST -H "X-API-Key: YOUR_API_KEY" -H "Content-Type: application/json" -d '{"material": "YBa2Cu3O7", "tc": 93, "pressure": 0, "notes": "Test submission"}' https://api.superconductor-pipeline.example.com/submit
```

Response:
```json
{"message": "Candidate submitted successfully", "entry": {"material": "YBa2Cu3O7", "tc": 93, "pressure": 0, "notes": "Test submission", "timestamp": "2025-03-25T12:00:00"}}
```

### Data Versioning

The pipeline includes a data versioning module (`DataVersioning` class) that automatically creates versioned snapshots of data files (e.g., experimental results) whenever a new candidate is submitted. Versions are stored in `data/versions/` with metadata including timestamp, content hash, and description.

To manually create a version of a file, use the `save_version` method:

```python
from run_pipeline import DataVersioning
DataVersioning.save_version("data/experimental_results.json", description="Manual backup")
```

To list all versions of a file:

```python
versions = DataVersioning.list_versions("data/experimental_results.json")
for v in versions:
    print(v["version_id"], v["timestamp"])
```

### Self-Optimizing Pipeline

The pipeline can automatically tune its hyperparameters using Bayesian optimization. Run the pipeline in `optimize` mode:

```bash
python run_pipeline.py --mode optimize
```

This will perform 20 iterations of Bayesian optimization to find the best combination of learning rate, batch size, dropout rate, and number of estimators. Results are logged to `data/optimization_log.json`.

You can also call the optimization function programmatically:

```python
from run_pipeline import self_optimize_pipeline
best_params = self_optimize_pipeline(n_calls=30, random_state=123)
print(best_params)
```

### Structured Logging

The pipeline now uses structured JSON logging. To enable it, call `setup_logging()` at the start of your script:

```python
from run_pipeline import setup_logging
setup_logging(level=logging.INFO, log_file="logs/pipeline.log")
```

All log messages will be output as JSON objects with timestamp, level, logger name, message, module, function name, and line number.

### Deployment

The API is deployed on AWS Lambda using Mangum. Environment variables for configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Host to bind (for local uvicorn) | `0.0.0.0` |
| `PORT` | Port to bind (for local uvicorn) | `8000` |
| `PIPELINE_API_KEYS` | Comma-separated list of valid API keys | `dev-key-123` |


### Batch Predict API

The `/batch_predict` endpoint allows you to submit multiple materials for Tc prediction in a single request. This is useful for high-throughput screening.

#### Endpoint

`POST /batch_predict`

#### Authentication

Requires a valid API key (see API Key Authentication above) or OAuth2 bearer token.

#### Request Body

The request body must be a JSON object with a `materials` array. Each material is an object with the following fields:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `formula` | string | Chemical formula (e.g., `LaH10`) | Yes |
| `pressure` | number | Pressure in GPa | Yes |
| `temperature` | number | Temperature in K (optional, default 0) | No |
| `structure` | string | Crystal structure type (e.g., `fcc`, `bcc`, `hcp`) | No |

#### Example Request

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_OAUTH2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "materials": [
      {"formula": "LaH10", "pressure": 150, "temperature": 0, "structure": "fcc"},
      {"formula": "H3S", "pressure": 200, "temperature": 0, "structure": "bcc"},
      {"formula": "YBa2Cu3O7", "pressure": 0, "temperature": 93, "structure": "orthorhombic"}
    ]
  }' \
  https://api.superconductor-pipeline.example.com/batch_predict
```

#### Example Response

```json
{
  "predictions": [
    {
      "formula": "LaH10",
      "pressure": 150,
      "predicted_tc": 250.3,
      "confidence": 0.92,
      "model_version": "v2.1.0"
    },
    {
      "formula": "H3S",
      "pressure": 200,
      "predicted_tc": 203.5,
      "confidence": 0.88,
      "model_version": "v2.1.0"
    },
    {
      "formula": "YBa2Cu3O7",
      "pressure": 0,
      "predicted_tc": 92.0,
      "confidence": 0.95,
      "model_version": "v2.1.0"
    }
  ],
  "request_id": "batch-20250325-abc123",
  "timestamp": "2025-03-25T12:00:00Z"
}
```

#### Error Handling

If any material in the batch fails validation (e.g., invalid formula), the entire batch is rejected with a 400 status code and an error message indicating which material failed.

```json
{
  "error": "Invalid material at index 1: formula 'H3S' is not recognized",
  "request_id": "batch-20250325-def456"
}
```

#### Rate Limiting

The batch predict endpoint is rate-limited to 10 requests per minute per API key. Exceeding this limit returns a 429 status code.
