#!/usr/bin/env python3
"""
DFT Calculator module for Quantum ESPRESSO.
Generates input files, runs calculations, and extracts phonon frequencies
and electron-phonon coupling constants (lambda).
"""

import os
import subprocess
import re
import json
from typing import Dict, List, Optional, Tuple

# Default pseudopotential directory (adjust as needed)
PSEUDO_DIR = os.environ.get("QE_PSEUDO_DIR", "./pseudo")

# Default Quantum ESPRESSO binaries (adjust as needed)
PW_BIN = os.environ.get("QE_PW", "pw.x")
PH_BIN = os.environ.get("QE_PH", "ph.x")
Q2R_BIN = os.environ.get("QE_Q2R", "q2r.x")
MATDYN_BIN = os.environ.get("QE_MATDYN", "matdyn.x")
LAMBDA_BIN = os.environ.get("QE_LAMBDA", "lambda.x")


def generate_scf_input(
    structure: Dict,
    prefix: str = "scf",
    pseudo_dir: str = PSEUDO_DIR,
    ecutwfc: float = 60.0,
    ecutrho: float = 240.0,
    kpoints: List[int] = [4, 4, 4, 0, 0, 0],
    occupations: str = "smearing",
    smearing: str = "gaussian",
    degauss: float = 0.01,
    conv_thr: float = 1e-8,
) -> str:
    """
    Generate a Quantum ESPRESSO SCF input file.

    Args:
        structure: Dictionary with keys 'cell_parameters', 'atomic_positions', 'atomic_species'.
                   cell_parameters: 3x3 list of floats (alat units).
                   atomic_positions: list of dicts with 'element', 'x', 'y', 'z' (crystal or alat).
                   atomic_species: list of dicts with 'element', 'mass', 'pseudo'.
        prefix: Calculation prefix.
        pseudo_dir: Path to pseudopotential directory.
        ecutwfc: Wavefunction cutoff (Ry).
        ecutrho: Charge density cutoff (Ry).
        kpoints: Monkhorst-Pack grid (6 ints).
        occupations: 'smearing' or 'fixed'.
        smearing: Type of smearing.
        degauss: Smearing width (Ry).
        conv_thr: Convergence threshold.

    Returns:
        String containing the input file content.
    """
    lines = []
    lines.append(f"&control")
    lines.append(f"    calculation = 'scf'")
    lines.append(f"    prefix = '{prefix}'")
    lines.append(f"    pseudo_dir = '{pseudo_dir}'")
    lines.append(f"    outdir = './out'")
    lines.append(f"    verbosity = 'high'")
    lines.append(f"/")
    lines.append(f"&system")
    lines.append(f"    ibrav = 0")
    lines.append(f"    nat = {len(structure['atomic_positions'])}")
    lines.append(f"    ntyp = {len(structure['atomic_species'])}")
    lines.append(f"    ecutwfc = {ecutwfc}")
    lines.append(f"    ecutrho = {ecutrho}")
    lines.append(f"    occupations = '{occupations}'")
    lines.append(f"    smearing = '{smearing}'")
    lines.append(f"    degauss = {degauss}")
    lines.append(f"/")
    lines.append(f"&electrons")
    lines.append(f"    conv_thr = {conv_thr}")
    lines.append(f"    mixing_beta = 0.7")
    lines.append(f"/")
    lines.append(f"CELL_PARAMETERS (alat)")
    for row in structure['cell_parameters']:
        lines.append(f"  {row[0]:.10f}  {row[1]:.10f}  {row[2]:.10f}")
    lines.append(f"ATOMIC_SPECIES")
    for sp in structure['atomic_species']:
        lines.append(f"  {sp['element']}  {sp['mass']}  {sp['pseudo']}")
    lines.append(f"ATOMIC_POSITIONS (crystal)")
    for pos in structure['atomic_positions']:
        lines.append(f"  {pos['element']}  {pos['x']:.10f}  {pos['y']:.10f}  {pos['z']:.10f}")
    lines.append(f"K_POINTS (automatic)")
    lines.append(f"  {kpoints[0]} {kpoints[1]} {kpoints[2]} {kpoints[3]} {kpoints[4]} {kpoints[5]}")
    return "\n".join(lines) + "\n"


def generate_ph_input(
    prefix: str,
    nq1: int = 4,
    nq2: int = 4,
    nq3: int = 4,
    tr2_ph: float = 1e-12,
    ldisp: bool = True,
    fildyn: str = "matdyn",
) -> str:
    """
    Generate a Quantum ESPRESSO ph.x input file for phonon calculation.

    Args:
        prefix: Same as SCF prefix.
        nq1, nq2, nq3: q-point grid.
        tr2_ph: Convergence threshold for phonons.
        ldisp: If True, use q-point grid.
        fildyn: Dynamical matrix file prefix.

    Returns:
        String containing the input file content.
    """
    lines = []
    lines.append("Phonon calculation")
    lines.append("&inputph")
    lines.append(f"    prefix = '{prefix}'")
    lines.append(f"    outdir = './out'")
    lines.append(f"    fildyn = '{fildyn}'")
    lines.append(f"    tr2_ph = {tr2_ph}")
    lines.append(f"    ldisp = {'.true.' if ldisp else '.false.'}")
    lines.append(f"    nq1 = {nq1}")
    lines.append(f"    nq2 = {nq2}")
    lines.append(f"    nq3 = {nq3}")
    lines.append("/")
    return "\n".join(lines) + "\n"


def generate_elph_input(
    prefix: str,
    fildyn: str = "matdyn",
    fildvscf: str = "dvscf",
    nq1: int = 4,
    nq2: int = 4,
    nq3: int = 4,
    nk1: int = 4,
    nk2: int = 4,
    nk3: int = 4,
    ntempx: int = 10,
    tempx_min: float = 10.0,
    tempx_max: float = 300.0,
    deltae: float = 0.001,
) -> str:
    """
    Generate a Quantum ESPRESSO lambda.x input file for electron-phonon coupling.

    Args:
        prefix: Same as SCF prefix.
        fildyn: Dynamical matrix file prefix.
        fildvscf: Prefix for dvscf files.
        nq1, nq2, nq3: q-point grid for phonons.
        nk1, nk2, nk3: k-point grid for electrons.
        ntempx: Number of temperature points.
        tempx_min, tempx_max: Temperature range (K).
        deltae: Energy step for integration (Ry).

    Returns:
        String containing the input file content.
    """
    lines = []
    lines.append("Electron-phonon coupling calculation")
    lines.append("&inputlambda")
    lines.append(f"    prefix = '{prefix}'")
    lines.append(f"    outdir = './out'")
    lines.append(f"    fildyn = '{fildyn}'")
    lines.append(f"    fildvscf = '{fildvscf}'")
    lines.append(f"    nq1 = {nq1}")
    lines.append(f"    nq2 = {nq2}")
    lines.append(f"    nq3 = {nq3}")
    lines.append(f"    nk1 = {nk1}")
    lines.append(f"    nk2 = {nk2}")
    lines.append(f"    nk3 = {nk3}")
    lines.append(f"    ntempx = {ntempx}")
    lines.append(f"    tempx_min = {tempx_min}")
    lines.append(f"    tempx_max = {tempx_max}")
    lines.append(f"    deltae = {deltae}")
    lines.append("/")
    return "\n".join(lines) + "\n"


def run_pw(input_file: str, output_file: str, binary: str = PW_BIN) -> None:
    """Run pw.x calculation."""
    cmd = [binary, "-in", input_file, ">", output_file]
    subprocess.run(" ".join(cmd), shell=True, check=True)


def run_ph(input_file: str, output_file: str, binary: str = PH_BIN) -> None:
    """Run ph.x calculation."""
    cmd = [binary, "-in", input_file, ">", output_file]
    subprocess.run(" ".join(cmd), shell=True, check=True)


def run_q2r(input_file: str, output_file: str, binary: str = Q2R_BIN) -> None:
    """Run q2r.x to generate force constants."""
    cmd = [binary, "-in", input_file, ">", output_file]
    subprocess.run(" ".join(cmd), shell=True, check=True)


def run_matdyn(input_file: str, output_file: str, binary: str = MATDYN_BIN) -> None:
    """Run matdyn.x to compute phonon dispersion."""
    cmd = [binary, "-in", input_file, ">", output_file]
    subprocess.run(" ".join(cmd), shell=True, check=True)


def run_lambda(input_file: str, output_file: str, binary: str = LAMBDA_BIN) -> None:
    """Run lambda.x to compute electron-phonon coupling."""
    cmd = [binary, "-in", input_file, ">", output_file]
    subprocess.run(" ".join(cmd), shell=True, check=True)


def extract_phonon_frequencies(ph_output: str) -> List[float]:
    """
    Extract phonon frequencies (cm^-1) from ph.x output file.

    Args:
        ph_output: Path to ph.x output file.

    Returns:
        List of phonon frequencies in cm^-1.
    """
    frequencies = []
    with open(ph_output, "r") as f:
        content = f.read()
    # Pattern: "freq (    1) =  123.456 [THz]" or "freq (    1) =  123.456 [cm-1]"
    # We'll look for lines with "freq" and extract the value.
    pattern = r"freq\s*\(\s*\d+\s*\)\s*=\s*([\d.\-]+)\s*\[cm-1\]"
    matches = re.findall(pattern, content)
    for m in matches:
        frequencies.append(float(m))
    return frequencies


def extract_lambda(lambda_output: str) -> Dict:
    """
    Extract electron-phonon coupling constant lambda from lambda.x output.

    Args:
        lambda_output: Path to lambda.x output file.

    Returns:
        Dictionary with keys 'lambda', 'omega_log' (K), and 'Tc' (K) if available.
    """
    result = {}
    with open(lambda_output, "r") as f:
        content = f.read()
    # Look for "lambda = 0.1234"
    match = re.search(r"lambda\s*=\s*([\d.]+)", content)
    if match:
        result["lambda"] = float(match.group(1))
    # Look for "omega_log = 123.45 K"
    match = re.search(r"omega_log\s*=\s*([\d.]+)\s*K", content)
    if match:
        result["omega_log"] = float(match.group(1))
    # Look for "Tc = 123.45 K"
    match = re.search(r"Tc\s*=\s*([\d.]+)\s*K", content)
    if match:
        result["Tc"] = float(match.group(1))
    return result


def run_full_dft_calculation(
    structure: Dict,
    prefix: str = "scf",
    workdir: str = "./dft_work",
    ecutwfc: float = 60.0,
    ecutrho: float = 240.0,
    kpoints: List[int] = [4, 4, 4, 0, 0, 0],
    nq1: int = 4,
    nq2: int = 4,
    nq3: int = 4,
    tr2_ph: float = 1e-12,
) -> Dict:
    """
    Run a full DFT calculation: SCF -> phonon -> electron-phonon coupling.

    Args:
        structure: Dictionary describing the crystal (see generate_scf_input).
        prefix: Calculation prefix.
        workdir: Working directory for input/output files.
        ecutwfc, ecutrho: Cutoffs.
        kpoints: K-point grid.
        nq1, nq2, nq3: Q-point grid for phonons.
        tr2_ph: Phonon convergence threshold.

    Returns:
        Dictionary with keys 'phonon_frequencies' (list) and 'elph' (dict from extract_lambda).
    """
    os.makedirs(workdir, exist_ok=True)
    os.chdir(workdir)

    # Generate SCF input
    scf_input = generate_scf_input(structure, prefix=prefix, ecutwfc=ecutwfc, ecutrho=ecutrho, kpoints=kpoints)
    with open(f"{prefix}.scf.in", "w") as f:
        f.write(scf_input)
    run_pw(f"{prefix}.scf.in", f"{prefix}.scf.out")

    # Generate phonon input
    ph_input = generate_ph_input(prefix, nq1=nq1, nq2=nq2, nq3=nq3, tr2_ph=tr2_ph)
    with open(f"{prefix}.ph.in", "w") as f:
        f.write(ph_input)
    run_ph(f"{prefix}.ph.in", f"{prefix}.ph.out")

    # Extract phonon frequencies
    phonon_freqs = extract_phonon_frequencies(f"{prefix}.ph.out")

    # Generate q2r input (simple, for force constants)
    q2r_input = f"&input\n  fildyn='{prefix}.dyn'\n  flfrc='{prefix}.fc'\n/\n"
    with open(f"{prefix}.q2r.in", "w") as f:
        f.write(q2r_input)
    run_q2r(f"{prefix}.q2r.in", f"{prefix}.q2r.out")

    # Generate matdyn input for phonon DOS (optional, but needed for lambda)
    matdyn_input = f"&input\n  asr='crystal'\n  flfrc='{prefix}.fc'\n  flfrq='{prefix}.freq'\n  dos=.true.\n  fldos='{prefix}.dos'\n  nk1={nq1}\n  nk2={nq2}\n  nk3={nq3}\n/\n"
    with open(f"{prefix}.matdyn.in", "w") as f:
        f.write(matdyn_input)
    run_matdyn(f"{prefix}.matdyn.in", f"{prefix}.matdyn.out")

    # Generate lambda input
    elph_input = generate_elph_input(prefix, nq1=nq1, nq2=nq2, nq3=nq3, nk1=kpoints[0], nk2=kpoints[1], nk3=kpoints[2])
    with open(f"{prefix}.lambda.in", "w") as f:
        f.write(elph_input)
    run_lambda(f"{prefix}.lambda.in", f"{prefix}.lambda.out")

    # Extract lambda
    elph_result = extract_lambda(f"{prefix}.lambda.out")

    os.chdir("..")
    return {
        "phonon_frequencies": phonon_freqs,
        "elph": elph_result,
    }


if __name__ == "__main__":
    # Example: simple cubic hydrogen (H) at high pressure (placeholder)
    # This is a dummy structure; real usage requires proper lattice parameters.
    example_structure = {
        "cell_parameters": [
            [2.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 2.0],
        ],
        "atomic_species": [
            {"element": "H", "mass": 1.00794, "pseudo": "H.pbe-rrkjus_psl.1.0.0.UPF"},
        ],
        "atomic_positions": [
            {"element": "H", "x": 0.0, "y": 0.0, "z": 0.0},
        ],
    }
    result = run_full_dft_calculation(example_structure, prefix="test_H", workdir="./test_H_work")
    print(json.dumps(result, indent=2))
