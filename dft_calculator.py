#!/usr/bin/env python3
"""Compatibility surface for the modular Quantum ESPRESSO workflow."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from superconductors.dft.inputs import generate_elph_input, generate_ph_input, generate_scf_input
from superconductors.dft.ml import fine_tune_pinn_on_real_data, get_device
from superconductors.dft.parsing import compute_tc, extract_lambda, extract_phonon_frequencies
from superconductors.dft.runner import (
    DFTExecutionError,
    QuantumEspressoBinaries,
    run_dft_pipeline,
)
from superconductors.dft.runner import (
    run_full_dft_calculation as _run_full_dft_calculation,
)

PSEUDO_DIR = os.getenv("QE_PSEUDO_DIR", "./pseudo")
PW_BIN = os.getenv("QE_PW", "pw.x")
PH_BIN = os.getenv("QE_PH", "ph.x")
Q2R_BIN = os.getenv("QE_Q2R", "q2r.x")
MATDYN_BIN = os.getenv("QE_MATDYN", "matdyn.x")
LAMBDA_BIN = os.getenv("QE_LAMBDA", "lambda.x")

__all__ = [
    "DFTExecutionError",
    "QuantumEspressoBinaries",
    "compute_tc",
    "compute_tc_mcmillan_allen_dynes",
    "extract_lambda",
    "extract_phonon_frequencies",
    "fine_tune_pinn_on_real_data",
    "generate_elph_input",
    "generate_ph_input",
    "generate_scf_input",
    "get_device",
    "run",
    "run_dft_pipeline",
    "run_full_dft_calculation",
]


def run_full_dft_calculation(
    structure: Mapping[str, Any],
    prefix: str = "scf",
    workdir: str | Path = "./dft_work",
    ecutwfc: float = 60.0,
    ecutrho: float = 240.0,
    kpoints: Sequence[int] | None = None,
    nq1: int = 4,
    nq2: int = 4,
    nq3: int = 4,
    tr2_ph: float = 1e-12,
    *,
    execute: bool = False,
    runner=None,
) -> dict[str, Any]:
    """Adapt the legacy signature to the safe modular runner."""
    return _run_full_dft_calculation(
        structure,
        prefix=prefix,
        workdir=workdir,
        ecutwfc=ecutwfc,
        ecutrho=ecutrho,
        kpoints=kpoints,
        q_grid=(nq1, nq2, nq3),
        pseudo_dir=PSEUDO_DIR,
        tr2_ph=tr2_ph,
        execute=execute,
        runner=runner,
    )


def compute_tc_mcmillan_allen_dynes(
    lambda_val: float, omega_log: float, mu_star: float = 0.1
) -> float:
    return compute_tc(lambda_val, omega_log, mu_star)


def run(compound: Mapping[str, Any], **kwargs: Any) -> dict[str, float | str]:
    return run_dft_pipeline(compound, **kwargs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Quantum ESPRESSO DFT workflow")
    parser.add_argument("structure", help="Path to a JSON structure description")
    parser.add_argument("--prefix", default="dft")
    parser.add_argument("--workdir", default="./dft_work")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Confirm execution of external Quantum ESPRESSO binaries",
    )
    args = parser.parse_args(argv)
    if not args.execute:
        parser.error("DFT execution requires the explicit --execute flag")
    with Path(args.structure).open("r", encoding="utf-8") as handle:
        structure = json.load(handle)
    result = run_full_dft_calculation(
        structure,
        prefix=args.prefix,
        workdir=args.workdir,
        execute=True,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
