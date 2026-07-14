"""Safe, injectable execution boundary for Quantum ESPRESSO."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .inputs import (
    generate_elph_input,
    generate_matdyn_input,
    generate_ph_input,
    generate_q2r_input,
    generate_scf_input,
)
from .parsing import compute_tc, extract_lambda, extract_phonon_frequencies


class DFTExecutionError(RuntimeError):
    """Raised when an external Quantum ESPRESSO step fails."""


@dataclass(frozen=True, slots=True)
class QuantumEspressoBinaries:
    pw: str = os.getenv("QE_PW", "pw.x")
    ph: str = os.getenv("QE_PH", "ph.x")
    q2r: str = os.getenv("QE_Q2R", "q2r.x")
    matdyn: str = os.getenv("QE_MATDYN", "matdyn.x")
    lambda_: str = os.getenv("QE_LAMBDA", "lambda.x")


ProcessRunner = Callable[[Sequence[str], Path], str]


def run_program(
    binary: str,
    input_path: Path,
    output_path: Path,
    *,
    workdir: Path,
    runner: ProcessRunner | None = None,
) -> None:
    execute = runner or _subprocess_runner
    try:
        stdout = execute([binary, "-in", input_path.name], workdir)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise DFTExecutionError(f"{binary} failed: {exc}") from exc
    output_path.write_text(stdout, encoding="utf-8")


def run_full_dft_calculation(
    structure: Mapping[str, Any],
    prefix: str = "scf",
    workdir: str | Path = "./dft_work",
    ecutwfc: float = 60.0,
    ecutrho: float = 240.0,
    kpoints: Sequence[int] | None = None,
    q_grid: Sequence[int] = (4, 4, 4),
    pseudo_dir: str = "./pseudo",
    tr2_ph: float = 1e-12,
    *,
    execute: bool = False,
    binaries: QuantumEspressoBinaries | None = None,
    runner: ProcessRunner | None = None,
) -> dict[str, Any]:
    if not execute:
        raise DFTExecutionError("DFT execution requires execute=True")
    directory = Path(workdir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    grid = tuple(kpoints or (4, 4, 4, 0, 0, 0))
    q_grid = tuple(q_grid)
    tools = binaries or QuantumEspressoBinaries()

    inputs = {
        "scf": generate_scf_input(
            structure,
            prefix=prefix,
            pseudo_dir=pseudo_dir,
            ecutwfc=ecutwfc,
            ecutrho=ecutrho,
            kpoints=grid,
        ),
        "ph": generate_ph_input(prefix, *q_grid, tr2_ph=tr2_ph),
        "q2r": generate_q2r_input(prefix),
        "matdyn": generate_matdyn_input(prefix, q_grid),
        "lambda": generate_elph_input(prefix, q_grid, grid[:3]),
    }
    binaries_by_step = {
        "scf": tools.pw,
        "ph": tools.ph,
        "q2r": tools.q2r,
        "matdyn": tools.matdyn,
        "lambda": tools.lambda_,
    }
    for step, content in inputs.items():
        input_path = directory / f"{prefix}.{step}.in"
        output_path = directory / f"{prefix}.{step}.out"
        input_path.write_text(content, encoding="utf-8")
        run_program(
            binaries_by_step[step],
            input_path,
            output_path,
            workdir=directory,
            runner=runner,
        )

    return {
        "phonon_frequencies": extract_phonon_frequencies(directory / f"{prefix}.ph.out"),
        "elph": extract_lambda(directory / f"{prefix}.lambda.out"),
        "workdir": str(directory),
    }


def run_dft_pipeline(
    structure: Mapping[str, Any],
    *,
    mu_star: float = 0.1,
    execute: bool = False,
    **kwargs: Any,
) -> dict[str, float | str]:
    result = run_full_dft_calculation(structure, execute=execute, **kwargs)
    coupling = result["elph"]
    lambda_val = coupling.get("lambda")
    omega_log = coupling.get("omega_log")
    if lambda_val is None or omega_log is None:
        raise DFTExecutionError("Quantum ESPRESSO output did not contain lambda and omega_log")
    return {
        "lambda": lambda_val,
        "omega_log": omega_log,
        "tc": compute_tc(lambda_val, omega_log, mu_star),
        "workdir": result["workdir"],
    }


def _subprocess_runner(command: Sequence[str], workdir: Path) -> str:
    completed = subprocess.run(
        list(command),
        cwd=workdir,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout
