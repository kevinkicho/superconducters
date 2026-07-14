"""Pure Quantum ESPRESSO input-file renderers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def generate_scf_input(
    structure: Mapping[str, Any],
    prefix: str = "scf",
    pseudo_dir: str = "./pseudo",
    ecutwfc: float = 60.0,
    ecutrho: float = 240.0,
    kpoints: Sequence[int] | None = None,
    occupations: str = "smearing",
    smearing: str = "gaussian",
    degauss: float = 0.01,
    conv_thr: float = 1e-8,
) -> str:
    _validate_structure(structure)
    grid = tuple(kpoints or (4, 4, 4, 0, 0, 0))
    if len(grid) != 6 or any(not isinstance(value, int) for value in grid):
        raise ValueError("kpoints must contain six integers")
    lines = [
        "&control",
        "    calculation = 'scf'",
        f"    prefix = '{prefix}'",
        f"    pseudo_dir = '{pseudo_dir}'",
        "    outdir = './out'",
        "    verbosity = 'high'",
        "/",
        "&system",
        "    ibrav = 0",
        f"    nat = {len(structure['atomic_positions'])}",
        f"    ntyp = {len(structure['atomic_species'])}",
        f"    ecutwfc = {ecutwfc}",
        f"    ecutrho = {ecutrho}",
        f"    occupations = '{occupations}'",
        f"    smearing = '{smearing}'",
        f"    degauss = {degauss}",
        "/",
        "&electrons",
        f"    conv_thr = {conv_thr}",
        "    mixing_beta = 0.7",
        "/",
        "CELL_PARAMETERS (alat)",
    ]
    lines.extend(
        "  " + "  ".join(f"{float(value):.10f}" for value in row)
        for row in structure["cell_parameters"]
    )
    lines.append("ATOMIC_SPECIES")
    lines.extend(
        f"  {species['element']}  {species['mass']}  {species['pseudo']}"
        for species in structure["atomic_species"]
    )
    lines.append("ATOMIC_POSITIONS (crystal)")
    lines.extend(
        f"  {position['element']}  {float(position['x']):.10f}  "
        f"{float(position['y']):.10f}  {float(position['z']):.10f}"
        for position in structure["atomic_positions"]
    )
    lines.extend(["K_POINTS (automatic)", "  " + " ".join(str(value) for value in grid)])
    return "\n".join(lines) + "\n"


def generate_ph_input(
    prefix: str,
    nq1: int = 4,
    nq2: int = 4,
    nq3: int = 4,
    tr2_ph: float = 1e-12,
    ldisp: bool = True,
    fildyn: str | None = None,
) -> str:
    return "\n".join(
        [
            "Phonon calculation",
            "&inputph",
            f"    prefix = '{prefix}'",
            "    outdir = './out'",
            f"    fildyn = '{fildyn or f'{prefix}.dyn'}'",
            f"    tr2_ph = {tr2_ph}",
            f"    ldisp = {'.true.' if ldisp else '.false.'}",
            f"    nq1 = {nq1}",
            f"    nq2 = {nq2}",
            f"    nq3 = {nq3}",
            "/",
            "",
        ]
    )


def generate_q2r_input(prefix: str) -> str:
    return f"&input\n  fildyn='{prefix}.dyn'\n  flfrc='{prefix}.fc'\n/\n"


def generate_matdyn_input(prefix: str, q_grid: Sequence[int] = (4, 4, 4)) -> str:
    nq1, nq2, nq3 = q_grid
    return (
        f"&input\n  asr='crystal'\n  flfrc='{prefix}.fc'\n  flfrq='{prefix}.freq'\n"
        f"  dos=.true.\n  fldos='{prefix}.dos'\n  nk1={nq1}\n  nk2={nq2}\n  nk3={nq3}\n/\n"
    )


def generate_elph_input(
    prefix: str,
    q_grid: Sequence[int] = (4, 4, 4),
    k_grid: Sequence[int] = (4, 4, 4),
) -> str:
    nq1, nq2, nq3 = q_grid
    nk1, nk2, nk3 = k_grid
    return "\n".join(
        [
            "Electron-phonon coupling calculation",
            "&inputlambda",
            f"    prefix = '{prefix}'",
            "    outdir = './out'",
            f"    fildyn = '{prefix}.dyn'",
            "    fildvscf = 'dvscf'",
            f"    nq1 = {nq1}",
            f"    nq2 = {nq2}",
            f"    nq3 = {nq3}",
            f"    nk1 = {nk1}",
            f"    nk2 = {nk2}",
            f"    nk3 = {nk3}",
            "/",
            "",
        ]
    )


def _validate_structure(structure: Mapping[str, Any]) -> None:
    required = {"cell_parameters", "atomic_positions", "atomic_species"}
    missing = required.difference(structure)
    if missing:
        raise ValueError(f"Structure is missing required fields: {', '.join(sorted(missing))}")
    cell = structure["cell_parameters"]
    if len(cell) != 3 or any(len(row) != 3 for row in cell):
        raise ValueError("cell_parameters must be a 3x3 matrix")
    if not structure["atomic_positions"] or not structure["atomic_species"]:
        raise ValueError("Structure must contain atomic positions and species")
