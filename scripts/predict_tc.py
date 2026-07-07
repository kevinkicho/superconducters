#!/usr/bin/env python3
"""
BCS-based predictive model for superconducting critical temperature (Tc).
Implements the McMillan formula (BCS theory) and the Allen-Dynes modification
(Eliashberg theory) for Tc estimation. Also includes a linear regression model
and a random forest model trained on a small embedded database of known A15
compounds. Features: average valence electrons per atom and average Debye temperature.
"""

import sys
import re
import json
import math
import os
from typing import Dict, List, Tuple
from sklearn.ensemble import RandomForestRegressor

# Standard valence electron counts for common elements
VALENCE: Dict[str, int] = {
    'H': 1, 'He': 2,
    'Li': 1, 'Be': 2, 'B': 3, 'C': 4, 'N': 5, 'O': 6, 'F': 7, 'Ne': 8,
    'Na': 1, 'Mg': 2, 'Al': 3, 'Si': 4, 'P': 5, 'S': 6, 'Cl': 7, 'Ar': 8,
    'K': 1, 'Ca': 2, 'Sc': 3, 'Ti': 4, 'V': 5, 'Cr': 6, 'Mn': 7, 'Fe': 8,
    'Co': 9, 'Ni': 10, 'Cu': 11, 'Zn': 12, 'Ga': 3, 'Ge': 4, 'As': 5,
    'Se': 6, 'Br': 7, 'Kr': 8,
    'Rb': 1, 'Sr': 2, 'Y': 3, 'Zr': 4, 'Nb': 5, 'Mo': 6, 'Tc': 7,
    'Ru': 8, 'Rh': 9, 'Pd': 10, 'Ag': 11, 'Cd': 12, 'In': 3, 'Sn': 4,
    'Sb': 5, 'Te': 6, 'I': 7, 'Xe': 8,
    'Cs': 1, 'Ba': 2, 'La': 3, 'Hf': 4, 'Ta': 5, 'W': 6, 'Re': 7,
    'Os': 8, 'Ir': 9, 'Pt': 10, 'Au': 11, 'Hg': 12, 'Tl': 3, 'Pb': 4,
    'Bi': 5, 'Po': 6, 'At': 7, 'Rn': 8,
}

# Debye temperatures (K) for common elements (approximate values from literature)
DEBYE_TEMP: Dict[str, float] = {
    'Al': 428, 'As': 282, 'Au': 165, 'B': 1250, 'Ba': 110, 'Be': 1440,
    'Bi': 119, 'C': 2230, 'Ca': 230, 'Cd': 209, 'Co': 445, 'Cr': 630,
    'Cs': 38, 'Cu': 343, 'Fe': 470, 'Ga': 320, 'Ge': 374, 'Hf': 252,
    'Hg': 72, 'In': 108, 'Ir': 420, 'K': 91, 'La': 142, 'Li': 344,
    'Mg': 400, 'Mn': 410, 'Mo': 450, 'Na': 158, 'Nb': 275, 'Ni': 450,
    'Os': 500, 'P': 640, 'Pb': 105, 'Pd': 274, 'Pt': 240, 'Rb': 56,
    'Re': 430, 'Rh': 480, 'Ru': 600, 'Sb': 211, 'Sc': 360, 'Se': 90,
    'Si': 645, 'Sn': 200, 'Sr': 147, 'Ta': 240, 'Tc': 411, 'Te': 153,
    'Ti': 420, 'Tl': 78, 'V': 380, 'W': 400, 'Y': 280, 'Zn': 327,
    'Zr': 291,
}

# Atomic masses (amu) for common elements (approximate)
ATOMIC_MASS: Dict[str, float] = {
    'H': 1.008, 'He': 4.0026,
    'Li': 6.94, 'Be': 9.0122, 'B': 10.81, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180,
    'Na': 22.990, 'Mg': 24.305, 'Al': 26.982, 'Si': 28.085, 'P': 30.974, 'S': 32.06, 'Cl': 35.45, 'Ar': 39.948,
    'K': 39.098, 'Ca': 40.078, 'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996, 'Mn': 54.938, 'Fe': 55.845,
    'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.38, 'Ga': 69.723, 'Ge': 72.630, 'As': 74.922, 'Se': 78.971,
    'Br': 79.904, 'Kr': 83.798,
    'Rb': 85.468, 'Sr': 87.62, 'Y': 88.906, 'Zr': 91.224, 'Nb': 92.906, 'Mo': 95.95, 'Tc': 98.0, 'Ru': 101.07,
    'Rh': 102.91, 'Pd': 106.42, 'Ag': 107.87, 'Cd': 112.41, 'In': 114.82, 'Sn': 118.71, 'Sb': 121.76, 'Te': 127.60,
    'I': 126.90, 'Xe': 131.29,
    'Cs': 132.91, 'Ba': 137.33, 'La': 138.91, 'Hf': 178.49, 'Ta': 180.95, 'W': 183.84, 'Re': 186.21, 'Os': 190.23,
    'Ir': 192.22, 'Pt': 195.08, 'Au': 196.97, 'Hg': 200.59, 'Tl': 204.38, 'Pb': 207.2, 'Bi': 208.98, 'Po': 209.0,
    'At': 210.0, 'Rn': 222.0,
}

# Embedded training dataset: known superconductors with formula and Tc (K)
# Real data from literature (approximate)
TRAINING_DATA: List[Tuple[str, float]] = [
    ('Nb3Sn', 18.3),
    ('Nb3Al', 18.9),
    ('Nb3Ge', 23.2),
    ('V3Si', 17.1),
    ('V3Ga', 16.5),
    ('Nb3Ga', 20.3),
    ('Nb3In', 9.2),
    ('Mo3Os', 12.0),
    ('Ta3Pb', 0.5),
    ('Nb3Sb', 0.2),
    ('V3Ge', 6.0),
    ('V3Al', 9.6),
    ('Nb3Pt', 10.0),
    ('Nb3Au', 11.5),
    ('H3S', 203.0),
    ('LaH10', 250.0),
    ('YH6', 224.0),
    ('ThH10', 161.0),
    ('PrH9', 100.0),
    ('CeH9', 100.0),
]

def parse_formula(formula: str) -> Dict[str, float]:
    """Parse a chemical formula like 'Nb3Sn' into element: count dict."""
    pattern = r'([A-Z][a-z]*)(\d*\.?\d*)'
    matches = re.findall(pattern, formula)
    elements: Dict[str, float] = {}
    for elem, count_str in matches:
        count = float(count_str) if count_str else 1.0
        elements[elem] = elements.get(elem, 0.0) + count
    return elements

def average_valence(elements: Dict[str, float]) -> float:
    """Compute average number of valence electrons per atom."""
    total_electrons = 0.0
    total_atoms = 0.0
    for elem, count in elements.items():
        if elem not in VALENCE:
            raise ValueError(f"Unknown element: {elem}")
        total_electrons += VALENCE[elem] * count
        total_atoms += count
    return total_electrons / total_atoms

def average_debye(elements: Dict[str, float]) -> float:
    """Compute weighted average Debye temperature for a compound."""
    total_weight = 0.0
    total_atoms = 0.0
    for elem, count in elements.items():
        if elem not in DEBYE_TEMP:
            raise ValueError(f"Unknown Debye temperature for element: {elem}")
        total_weight += DEBYE_TEMP[elem] * count
        total_atoms += count
    return total_weight / total_atoms

def average_atomic_mass(elements: Dict[str, float]) -> float:
    """Compute weighted average atomic mass for a compound."""
    total_mass = 0.0
    total_atoms = 0.0
    for elem, count in elements.items():
        if elem not in ATOMIC_MASS:
            raise ValueError(f"Unknown atomic mass for element: {elem}")
        total_mass += ATOMIC_MASS[elem] * count
        total_atoms += count
    return total_mass / total_atoms

def extract_features(formula: str) -> List[float]:
    """Extract feature vector: [avg_valence, avg_debye_temp, avg_atomic_mass]."""
    elements = parse_formula(formula)
    n = average_valence(elements)
    theta = average_debye(elements)
    mass = average_atomic_mass(elements)
    return [n, theta, mass]

def train_linear_regression(features: List[List[float]], targets: List[float]) -> List[float]:
    """
    Train a linear regression model using the normal equation.
    Features are assumed to have a bias term (1) prepended.
    Returns coefficients [bias, w1, w2, ...].
    """
    n = len(features)
    m = len(features[0])  # number of features including bias
    # Build X matrix (n x m) and y vector (n x 1)
    X = [[1.0] + f for f in features]  # add bias column
    y = targets
    # Compute X^T X
    XtX = [[0.0]*m for _ in range(m)]
    for i in range(n):
        for j in range(m):
            for k in range(m):
                XtX[j][k] += X[i][j] * X[i][k]
    # Compute X^T y
    Xty = [0.0]*m
    for i in range(n):
        for j in range(m):
            Xty[j] += X[i][j] * y[i]
    # Solve (X^T X) * beta = X^T y using Gaussian elimination
    # Augmented matrix
    aug = [row[:] + [Xty[i]] for i, row in enumerate(XtX)]
    # Forward elimination
    for col in range(m):
        # Find pivot
        pivot = col
        for row in range(col+1, m):
            if abs(aug[row][col]) > abs(aug[pivot][col]):
                pivot = row
        aug[col], aug[pivot] = aug[pivot], aug[col]
        pivot_val = aug[col][col]
        if abs(pivot_val) < 1e-12:
            continue
        for row in range(col+1, m):
            factor = aug[row][col] / pivot_val
            for k in range(col, m+1):
                aug[row][k] -= factor * aug[col][k]
    # Back substitution
    beta = [0.0]*m
    for i in range(m-1, -1, -1):
        sum_ax = sum(aug[i][j] * beta[j] for j in range(i+1, m))
        beta[i] = (aug[i][m] - sum_ax) / aug[i][i] if abs(aug[i][i]) > 1e-12 else 0.0
    return beta

def load_database(path="superconductor_data.json"):
    """Load training data from a JSON file. Expected format: list of [formula, Tc]."""
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def train_random_forest(features, targets):
    """Train a random forest regressor for Tc prediction."""
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(features, targets)
    return model

# Load database and train model once at module load
TRAINING_DATA = load_database()
_training_features = [extract_features(f) for f, _ in TRAINING_DATA]
_training_targets = [tc for _, tc in TRAINING_DATA]
_coefficients = train_linear_regression(_training_features, _training_targets)
_rf_model = train_random_forest(_training_features, _training_targets)

def predict_tc(formula: str) -> float:
    """
    Predict Tc using a linear regression model trained on external database.
    Features: average valence electrons per atom, average Debye temperature.
    """
    features = extract_features(formula)
    # Add bias term
    x = [1.0] + features
    tc = sum(c * xi for c, xi in zip(_coefficients, x))
    # Clamp to non-negative
    if tc < 0:
        tc = 0.0
    return tc

def predict_tc_rf(formula: str) -> float:
    """
    Predict Tc using a random forest model trained on external database.
    Features: average valence electrons per atom, average Debye temperature.
    """
    features = extract_features(formula)
    tc = _rf_model.predict([features])[0]
    if tc < 0:
        tc = 0.0
    return tc

def eliashberg_tc(formula: str) -> float:
    """
    Predict Tc using the Allen-Dynes modification of the McMillan formula.
    Estimates electron-phonon coupling lambda from average valence and Debye temperature.
    """
    features = extract_features(formula)
    avg_valence, avg_debye = features
    # Estimate lambda: simple heuristic based on valence electrons
    lambda_ep = 0.5 + 0.1 * (avg_valence - 4.0)
    # Coulomb pseudopotential (typical value for simple metals)
    mu_star = 0.1
    # Logarithmic average phonon frequency (approx 0.8 * Debye temperature)
    omega_log = avg_debye * 0.8
    # Allen-Dynes formula
    numerator = 1.04 * (1.0 + lambda_ep)
    denominator = lambda_ep - mu_star * (1.0 + 0.62 * lambda_ep)
    if denominator <= 0:
        return 0.0
    tc = (omega_log / 1.2) * math.exp(-numerator / denominator)
    if tc < 0:
        tc = 0.0
    return tc

def mcmillan_tc(formula: str) -> float:
    """
    Predict Tc using the McMillan formula (BCS theory).
    Uses Debye temperature and estimated electron-phonon coupling lambda.
    """
    features = extract_features(formula)
    avg_valence, avg_debye = features
    # Estimate lambda: simple heuristic based on valence electrons
    lambda_ep = 0.5 + 0.1 * (avg_valence - 4.0)
    # Coulomb pseudopotential (typical value for simple metals)
    mu_star = 0.1
    # McMillan formula: Tc = (theta_D/1.45) * exp(-1.04*(1+lambda)/(lambda - mu*(1+0.62*lambda)))
    numerator = 1.04 * (1.0 + lambda_ep)
    denominator = lambda_ep - mu_star * (1.0 + 0.62 * lambda_ep)
    if denominator <= 0:
        return 0.0
    tc = (avg_debye / 1.45) * math.exp(-numerator / denominator)
    if tc < 0:
        tc = 0.0
    return tc

def predict_from_database():
    """Load the superconductor database and predict Tc for each entry using the Allen-Dynes formula."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'superconductor_database.json')
    try:
        with open(db_path, 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        print(f"Error: Database file '{db_path}' not found.", file=sys.stderr)
        sys.exit(1)
    print(f"{'Name':<20} {'Exp Tc (K)':<12} {'Pred Tc (K)':<12} {'Pressure (GPa)':<15} {'Structure':<25}")
    print("-" * 84)
    for entry in entries:
        formula = entry.get('name', '')
        exp_tc = entry.get('Tc', 0)
        pressure = entry.get('pressure', 0)
        structure = entry.get('structure', '')
        try:
            pred_tc = eliashberg_tc(formula)
        except Exception:
            pred_tc = 0.0
        print(f"{formula:<20} {exp_tc:<12.2f} {pred_tc:<12.2f} {pressure:<15} {structure:<25}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Predict superconducting Tc using BCS/Eliashberg models.')
    parser.add_argument('formulas', nargs='*', help='Material formulas (e.g., Nb3Sn). If none, reads from stdin or file.')
    parser.add_argument('--database', action='store_true', help='Load database and predict Tc for all entries.')
    args = parser.parse_args()
    if args.database:
        predict_from_database()
        return
    if not args.formulas:
        formula = input("Enter material formula (e.g., Nb3Sn): ").strip()
        candidates = [formula]
    elif len(args.formulas) == 1 and os.path.isfile(args.formulas[0]):
        filepath = args.formulas[0]
        with open(filepath, 'r') as f:
            candidates = [line.strip() for line in f if line.strip()]
    else:
        candidates = args.formulas
    for formula in candidates:
        try:
            tc_bcs = mcmillan_tc(formula)
            tc_eliashberg = eliashberg_tc(formula)
            tc_ml_linear = predict_tc(formula)
            tc_ml_rf = predict_tc_rf(formula)
            print(f"Predicted Tc for {formula}:")
            print(f"  BCS (McMillan): {tc_bcs:.2f} K")
            print(f"  Eliashberg (Allen-Dynes): {tc_eliashberg:.2f} K")
            print(f"  Machine Learning (Linear Regression): {tc_ml_linear:.2f} K")
            print(f"  Machine Learning (Random Forest): {tc_ml_rf:.2f} K")
        except Exception as e:
            print(f"Error for {formula}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
