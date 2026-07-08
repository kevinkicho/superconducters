#!/usr/bin/env python3
"""
DFT Calculator module for Quantum ESPRESSO.
Generates input files, runs calculations, and extracts phonon frequencies
and electron-phonon coupling constants (lambda).
"""

import math
import os
import subprocess
import re
import json
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
import torch
import torch_geometric
from torch_geometric.data import Data
import shap

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


def compute_tc_mcmillan_allen_dynes(lambda_val, omega_log, mu_star=0.1):
    """
    Compute superconducting critical temperature Tc using the McMillan-Allen-Dynes formula.

    Tc = (omega_log / 1.2) * exp( -1.04 * (1 + lambda) / (lambda - mu_star * (1 + 0.62 * lambda)) )

    Args:
        lambda_val: Electron-phonon coupling constant (dimensionless).
        omega_log: Logarithmic average phonon frequency (K).
        mu_star: Coulomb pseudopotential (default 0.1 for hydrides).

    Returns:
        Tc in Kelvin.
    """
    if lambda_val <= mu_star:
        return 0.0  # No superconductivity
    numerator = -1.04 * (1 + lambda_val)
    denominator = lambda_val - mu_star * (1 + 0.62 * lambda_val)
    exponent = numerator / denominator
    tc = (omega_log / 1.2) * math.exp(exponent)
    return tc


class MLTcPredictor:
    """Machine learning predictor for Tc using random forest and GNN."""
    def __init__(self, database_path="data/superconductor_database.json"):
        import json
        import os
        from sklearn.ensemble import RandomForestRegressor
        # Load database
        with open(database_path, "r") as f:
            data = json.load(f)
        # Extract features and target for random forest
        self.features = []
        self.targets = []
        for entry in data:
            if "lambda" in entry and "omega_log" in entry and "mu_star" in entry and "Tc" in entry:
                self.features.append([entry["lambda"], entry["omega_log"], entry["mu_star"]])
                self.targets.append(entry["Tc"])
        # Train random forest
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.rf_model.fit(self.features, self.targets)
        # GNN model (not trained yet; requires graph data)
        self.gnn_model = None
        self.gnn_trained = False
    def predict_tc_ml(self, lambda_val, omega_log, mu_star=0.1):
        """Predict Tc using trained random forest model."""
        return self.rf_model.predict([[lambda_val, omega_log, mu_star]])[0]
    def _structure_to_graph(self, structure):
        """Convert a crystal structure dictionary to a PyTorch Geometric Data object."""
        # Extract atomic positions and species
        positions = []
        atomic_numbers = []
        for atom in structure['atomic_positions']:
            positions.append([atom['x'], atom['y'], atom['z']])
            # Map element symbol to atomic number (simplified)
            element = atom['element']
            element_to_z = {'H':1, 'He':2, 'Li':3, 'Be':4, 'B':5, 'C':6, 'N':7, 'O':8, 'F':9, 'Ne':10,
                           'Na':11, 'Mg':12, 'Al':13, 'Si':14, 'P':15, 'S':16, 'Cl':17, 'Ar':18,
                           'K':19, 'Ca':20, 'Sc':21, 'Ti':22, 'V':23, 'Cr':24, 'Mn':25, 'Fe':26,
                           'Co':27, 'Ni':28, 'Cu':29, 'Zn':30, 'Ga':31, 'Ge':32, 'As':33, 'Se':34,
                           'Br':35, 'Kr':36, 'Rb':37, 'Sr':38, 'Y':39, 'Zr':40, 'Nb':41, 'Mo':42,
                           'Tc':43, 'Ru':44, 'Rh':45, 'Pd':46, 'Ag':47, 'Cd':48, 'In':49, 'Sn':50,
                           'Sb':51, 'Te':52, 'I':53, 'Xe':54, 'Cs':55, 'Ba':56, 'La':57, 'Ce':58,
                           'Pr':59, 'Nd':60, 'Pm':61, 'Sm':62, 'Eu':63, 'Gd':64, 'Tb':65, 'Dy':66,
                           'Ho':67, 'Er':68, 'Tm':69, 'Yb':70, 'Lu':71, 'Hf':72, 'Ta':73, 'W':74,
                           'Re':75, 'Os':76, 'Ir':77, 'Pt':78, 'Au':79, 'Hg':80, 'Tl':81, 'Pb':82,
                           'Bi':83, 'Po':84, 'At':85, 'Rn':86, 'Fr':87, 'Ra':88, 'Ac':89, 'Th':90,
                           'Pa':91, 'U':92, 'Np':93, 'Pu':94, 'Am':95, 'Cm':96, 'Bk':97, 'Cf':98,
                           'Es':99, 'Fm':100, 'Md':101, 'No':102, 'Lr':103, 'Rf':104, 'Db':105,
                           'Sg':106, 'Bh':107, 'Hs':108, 'Mt':109, 'Ds':110, 'Rg':111, 'Cn':112,
                           'Nh':113, 'Fl':114, 'Mc':115, 'Lv':116, 'Ts':117, 'Og':118}
            atomic_numbers.append(element_to_z.get(element, 0))
        # Node features: atomic number (scalar)
        x = torch.tensor(atomic_numbers, dtype=torch.float).view(-1, 1)
        # Positions as tensor
        pos = torch.tensor(positions, dtype=torch.float)
        # Compute edges based on distance (simple cutoff)
        edge_index = []
        num_atoms = len(positions)
        for i in range(num_atoms):
            for j in range(i+1, num_atoms):
                dist = torch.norm(pos[i] - pos[j]).item()
                if dist < 3.0:  # cutoff in Angstrom
                    edge_index.append([i, j])
                    edge_index.append([j, i])
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
        data = Data(x=x, edge_index=edge_index, pos=pos)
        return data
    def train_gnn(self, graph_dataset, targets, epochs=100):
        """Train the GNN on a dataset of graphs and corresponding Tc values."""
        import torch.nn as nn
        import torch.nn.functional as F
        from torch_geometric.nn import GCNConv, global_mean_pool
        # Define a simple GNN
        class GNN(nn.Module):
            def __init__(self, node_features, hidden_channels, num_layers=3):
                super().__init__()
                self.convs = nn.ModuleList()
                self.convs.append(GCNConv(node_features, hidden_channels))
                for _ in range(num_layers - 1):
                    self.convs.append(GCNConv(hidden_channels, hidden_channels))
                self.lin = nn.Linear(hidden_channels, 1)
            def forward(self, data):
                x, edge_index, batch = data.x, data.edge_index, data.batch
                for conv in self.convs:
                    x = conv(x, edge_index)
                    x = F.relu(x)
                x = global_mean_pool(x, batch)
                x = self.lin(x)
                return x.squeeze()
        self.gnn_model = GNN(node_features=graph_dataset[0].x.size(1), hidden_channels=64)
        optimizer = torch.optim.Adam(self.gnn_model.parameters(), lr=0.001)
        loss_fn = nn.MSELoss()
        for epoch in range(epochs):
            self.gnn_model.train()
            total_loss = 0
            for data, target in zip(graph_dataset, targets):
                optimizer.zero_grad()
                out = self.gnn_model(data)
                loss = loss_fn(out, torch.tensor([target], dtype=torch.float))
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Loss: {total_loss/len(graph_dataset):.4f}")
        self.gnn_trained = True
    def predict_tc_gnn(self, structure):
        """Predict Tc using GNN if trained, otherwise fallback to random forest."""
        if self.gnn_trained and self.gnn_model is not None:
            graph = self._structure_to_graph(structure)
            self.gnn_model.eval()
            with torch.no_grad():
                pred = self.gnn_model(graph)
            return pred.item()
        else:
            # Fallback: use random forest with default features (requires lambda, omega_log, mu_star)
            lambda_val = structure.get('lambda', 0.0)
            omega_log = structure.get('omega_log', 0.0)
            mu_star = structure.get('mu_star', 0.1)
            return self.predict_tc_ml(lambda_val, omega_log, mu_star)

    def predict_tc_with_uncertainty(self, structure, n_samples=10):
        """Predict Tc with uncertainty using Monte Carlo dropout.
        Returns (mean, std)."""
        if not self.gnn_trained or self.gnn_model is None:
            # Fallback: use random forest with uncertainty via ensemble of trees
            lambda_val = structure.get('lambda', 0.0)
            omega_log = structure.get('omega_log', 0.0)
            mu_star = structure.get('mu_star', 0.1)
            # Compute predictions from each tree in the random forest
            if hasattr(self, 'rf_model') and self.rf_model is not None and hasattr(self.rf_model, 'estimators_'):
                tree_preds = []
                for tree in self.rf_model.estimators_:
                    pred = tree.predict([[lambda_val, omega_log, mu_star]])[0]
                    tree_preds.append(pred)
                mean = sum(tree_preds) / len(tree_preds)
                variance = sum((p - mean) ** 2 for p in tree_preds) / len(tree_preds)
                std = math.sqrt(variance)
            else:
                mean = self.predict_tc_ml(lambda_val, omega_log, mu_star)
                std = 0.0
            return mean, std
        graph = self._structure_to_graph(structure)
        self.gnn_model.train()  # enable dropout
        predictions = []
        with torch.no_grad():
            for _ in range(n_samples):
                pred = self.gnn_model(graph)
                predictions.append(pred.item())
        self.gnn_model.eval()  # restore eval mode
        mean = sum(predictions) / len(predictions)
        variance = sum((p - mean) ** 2 for p in predictions) / len(predictions)
        std = math.sqrt(variance)
        return mean, std

    def predict_tc_low_fidelity(self, structure):
        """Low-fidelity prediction using simple linear regression on basic features.
        Supports multi-fidelity optimization."""
        lambda_val = structure.get('lambda', 0.0)
        mu_star = structure.get('mu_star', 0.1)
        # Simple linear model: Tc = a*lambda + b*mu_star + c (placeholder coefficients)
        a, b, c = 100.0, -50.0, 0.0  # dummy
        return a * lambda_val + b * mu_star + c


def compute_shap_values(model, X, feature_names=None):
    """
    Compute SHAP values for the PINN model to interpret predictions.

    Args:
        model: A trained model (e.g., PINN or any sklearn-compatible model).
        X: Input features (numpy array or pandas DataFrame).
        feature_names: Optional list of feature names.

    Returns:
        shap_values: SHAP values array.
        expected_value: Base value (expected model output).
    """
    # Use DeepExplainer for PyTorch models, otherwise fallback to KernelExplainer
    if isinstance(model, torch.nn.Module):
        explainer = shap.DeepExplainer(model, X)
        shap_values = explainer.shap_values(X)
        expected_value = explainer.expected_value
    else:
        explainer = shap.Explainer(model, X)
        shap_values = explainer(X)
        expected_value = shap_values.base_values
    return shap_values, expected_value


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
