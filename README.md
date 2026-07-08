# Project Overview

This repository documents a research project on room-temperature superconductivity. It includes the following key documents:

- [literature_review.md](literature_review.md): Comprehensive review of existing literature on room-temperature superconductivity.
- [theoretical_framework.md](theoretical_framework.md): Theoretical models and frameworks guiding the research.
- [candidate_materials.md](candidate_materials.md): List and properties of candidate materials for room-temperature superconductivity.
- [synthesis_methods.md](synthesis_methods.md): Methods and procedures for synthesizing candidate materials.
- [characterization_techniques.md](characterization_techniques.md): Techniques used to characterize superconducting properties.
- [roadmap.md](roadmap.md): Project roadmap and future milestones.
- [proposed_chemistry_physics.md](proposed_chemistry_physics.md): Proposed chemistry and physics for discovering and manufacturing room-temperature superconducting compounds.
- [presentation.md](presentation.md): Generated slide deck summarizing the research.

## Navigation

Start with the literature review to understand the current state of research, then explore the theoretical framework. Next, review candidate materials and synthesis methods. The characterization techniques document explains how we verify superconductivity, and the roadmap outlines next steps.

Additionally, see the following key documents: [discovery_strategy.md](docs/discovery_strategy.md), [online_research_summary.md](docs/online_research_summary.md), [manufacturing_scalability.md](docs/manufacturing_scalability.md), [experimental_protocol_hydride.md](docs/experimental_protocol_hydride.md), and [novel_mechanism.md](docs/novel_mechanism.md).


## Testing

Unit tests are located in the `tests/` directory. To run all tests, use:
```
pytest tests/
```
To run a specific test file, e.g., `test_predict_tc.py`:
```
pytest tests/test_predict_tc.py
```
Ensure you have the required dependencies installed. For test coverage, you can use `pytest --cov=scripts tests/`. See the [experimental feedback loop guide](docs/experimental_feedback_loop.md) for more details.

## How to Contribute

We welcome contributions! To propose changes, please open an issue describing your idea before submitting a pull request. Report bugs by creating a detailed issue with steps to reproduce. When submitting a pull request, ensure your code follows the project's style and includes relevant tests. All new features must include unit tests in the `tests/` directory. Run the full test suite before submitting to ensure nothing is broken. For more information, see our [experimental feedback loop guide](docs/experimental_feedback_loop.md).


## User Manual

### Installation

Ensure you have Python 3.8+ installed. Clone the repository and install required packages:

```
pip install -r requirements.txt
```

If you do not have a `requirements.txt`, install the core dependencies manually:

```
pip install numpy scipy matplotlib pandas scikit-learn pytest
```

### Configuration

The pipeline uses a configuration file `config.yaml` (if present) or environment variables. Key settings include:

- `DATA_DIR`: Directory for input data (default: `data/`)
- `OUTPUT_DIR`: Directory for output reports (default: `output/`)
- `MAX_CANDIDATES`: Maximum number of candidates to evaluate (default: 10)

You can override these by setting environment variables or editing `config.yaml`.

### Running the Pipeline

Execute the main pipeline script:

```
python scripts/run_pipeline.py
```

This will:

1. Load candidate materials from `candidate_materials.md` (or a database).
2. Run simulations (Monte Carlo for manufacturing, active learning for discovery).
3. Generate updated reports in `candidate_materials.md`, `roadmap.md`, and other output files.

To run a specific candidate, use:

```
python scripts/run_pipeline.py --candidate "YH3"
```

### Interpreting Results

After running the pipeline, check the following files:

- `candidate_materials.md`: Updated list of candidates with predicted Tc, synthesis parameters, and sensitivity analysis.
- `roadmap.md`: Updated project roadmap with milestones and validation plan.
- `output/`: Contains log files, plots (e.g., `sensitivity_top_candidate.png`), and simulation results.

Key metrics to look for:

- **Predicted Tc**: The critical temperature from the PINN model.
- **Yield**: Manufacturing yield from Monte Carlo simulation.
- **Cost**: Estimated cost per gram.

### Examples

**Example 1: Basic run**

```
python scripts/run_pipeline.py
```

Expected output: Console logs showing progress, and updated markdown files.

**Example 2: Run with custom configuration**

```
CONFIG_PATH=my_config.yaml python scripts/run_pipeline.py
```

### Troubleshooting

- **ModuleNotFoundError**: Ensure all dependencies are installed. Run `pip install -r requirements.txt`.
- **FileNotFoundError**: Check that `candidate_materials.md` exists in the project root. If not, create it with initial candidates.
- **Simulation fails**: Check the log file `output/pipeline.log` for error details. Ensure input data is valid.
- **Unexpected results**: Verify that the configuration parameters are reasonable. For Tc predictions, ensure the candidate material is in the supported list.

For further assistance, open an issue on the repository.


## Reproducibility

[![Reproducibility](https://img.shields.io/badge/Reproducibility-Yes-brightgreen)](https://github.com/yourusername/yourrepo)

To reproduce the results in this repository, you can use the provided Dockerfile or conda environment.

### Using Docker

1. Ensure Docker is installed on your system.
2. Build the Docker image:
   ```
   docker build -t superconductivity-research .
   ```
3. Run the container:
   ```
   docker run --rm -v $(pwd):/workspace superconductivity-research
   ```

### Using Conda

1. Install Miniconda or Anaconda.
2. Create the environment from the provided `environment.yml`:
   ```
   conda env create -f environment.yml
   ```
3. Activate the environment:
   ```
   conda activate superconductivity
   ```
4. Run the pipeline as described in the User Manual.

For more details, see the [Dockerfile](Dockerfile) and [environment.yml](environment.yml) in the repository root.


## Business Plan

A comprehensive business plan for the top candidate material is available in [business_plan.md](business_plan.md).

## Press Release

A press release announcing the discovery of the top candidate material is available in [press_release.md](press_release.md).

## Public Outreach

A public outreach document is available in [public_outreach.md](public_outreach.md).

## Executive Summary

An executive summary of the project is available in [executive_summary.md](executive_summary.md). See the [slide deck](presentation.md) for a visual summary.

## Final Report

The final report of the project is available in [final_report.md](final_report.md).


## Audit Trail

All pipeline runs and experimental results are logged to `output/pipeline.log` and `output/audit.json`. The audit log records timestamps, input parameters, candidate materials evaluated, simulation results, and any errors or warnings. To view the latest audit trail:

```
cat output/audit.json | jq .
```

For a human-readable summary, see `output/audit_summary.md` (generated after each pipeline run).

## Version-Controlled Pipeline

The entire pipeline is version-controlled via Git. To set up automatic commits after each pipeline run, add a post-run hook or use a CI/CD workflow. Example using a simple shell script:

```bash
#!/bin/bash
# After running the pipeline, commit and push changes
git add -A
git commit -m "Auto-commit: pipeline run $(date +%Y-%m-%d_%H:%M:%S)"
git push origin main
```

For a more robust setup, configure a GitHub Actions workflow (see `.github/workflows/ci.yml`) that triggers on push and runs the pipeline, then commits any updated output files back to the repository. Ensure that `config.yaml` includes a `version_control` section with `auto_commit: true` to enable automatic commits.
