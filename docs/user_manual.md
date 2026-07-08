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

### Role-Based Access Control (RBAC)

The Streamlit dashboard supports three roles:
- **Admin**: Full access to all features, including pipeline execution and configuration.
- **Researcher**: Can view results, run experiments, and provide feedback.
- **Viewer**: Read-only access to dashboards and reports.

Set the corresponding environment variables to enable authentication. If not set, the dashboard runs in open mode.

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
