# Project Overview

This repository documents a research project on room-temperature superconductivity. It includes the following key documents:

- [literature_review.md](literature_review.md): Comprehensive review of existing literature on room-temperature superconductivity.
- [theoretical_framework.md](theoretical_framework.md): Theoretical models and frameworks guiding the research.
- [candidate_materials.md](candidate_materials.md): List and properties of candidate materials for room-temperature superconductivity.
- [synthesis_methods.md](synthesis_methods.md): Methods and procedures for synthesizing candidate materials.
- [characterization_techniques.md](characterization_techniques.md): Techniques used to characterize superconducting properties.
- [roadmap.md](roadmap.md): Project roadmap and future milestones.
- [proposed_chemistry_physics.md](proposed_chemistry_physics.md): Proposed chemistry and physics for discovering and manufacturing room-temperature superconducting compounds.

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
