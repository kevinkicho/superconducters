# Room-Temperature Superconductor Discovery Gap Tracker

This tracker prevents software completeness from being confused with scientific
discovery capability. `Mitigated` means the repository has an enforceable
safeguard; `partial` means a real provider, dataset, or laboratory is still
required.

| # | Barrier | Status | Repository capability | Still required |
|---|---|---|---|---|
| 1 | Vague success criterion | Mitigated | The objective requires Tc ≥ 273.15 K, pressure ≤ 1 GPa, physical evidence, and independent replication. | Scientific review as the program evolves. |
| 2 | Mixed-provenance data | Partial | Evidence classification, retraction quarantine, validation, and a review queue. | Review 159 unclassified records against primary sources and publish a versioned dataset. |
| 3 | Unvalidated Tc prediction | Partial | Prediction is bounded to benchmarks; unsupported inputs fail closed and the old heuristic reports zero confidence. | A preregistered, structure-aware model with held-out-family and prospective validation. |
| 4 | No variable-composition structure search | Partial | A provider contract exists, synthetic fallback is prohibited, and outputs require intact artifacts. | Connect and validate a real CSP engine under appropriate licensing. |
| 5 | Incomplete first-principles thermodynamics | Partial | DFT boundaries, parsing, hull gates, and content-addressed provenance exist. | Converged production calculations, pressure grids, reference states, and cross-code checks. |
| 6 | Missing phonon, anharmonic, and EPC proof | Partial | Stability and EPC gates reject missing or tampered artifacts. | Production DFPT/SSCHA, convergence studies, uncertainty bounds, and expert review. |
| 7 | Weak uncertainty and applicability controls | Partial | Unsupported predictions fail closed; multi-fidelity modeling is isolated. | Calibrated uncertainty, leakage-resistant splits, applicability metrics, and prospective error tracking. |
| 8 | No closed experimental feedback loop | Partial | Raw-data hashes, calibration, sample identity, and electrical/magnetic evidence are supported. | Instrument adapters, laboratory SOPs, automated QC, and a governed training dataset. |
| 9 | No independent replication pathway | Partial | The gate requires zero resistance and Meissner evidence from at least two labs. | Partner labs, blinded sample exchange, preregistration, and public raw-data deposition. |

## Current priority order

1. Curate the evidence queue so invalid labels cannot contaminate modeling.
2. Connect a real structure-search provider and require reproducible artifacts.
3. Run converged stability and electron-phonon benchmarks before scaling.
4. Establish prospective experimental and replication partners.

No status in this table is evidence that a new superconducting material has
been discovered.
