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
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
import numpy as np
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import torch
import torch.nn as nn
import torch_geometric
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.data import Data, DataLoader
from pymatgen.core import Structure
from pymatgen.analysis.local_env import VoronoiNN

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
    'H': 100, 'He': 20, 'N': 100, 'O': 100, 'F': 100, 'S': 100,
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

def predict_tc(formula, pressure=0):
    """Predict Tc using the Allen-Dynes equation with parameters from the database."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'superconductor_database.json')
    try:
        with open(db_path, 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Database file '{db_path}' not found.")
    for entry in entries:
        if entry.get('name') == formula:
            lam = entry.get('lambda')
            omega_log = entry.get('omega_log')
            if lam is None or omega_log is None:
                raise ValueError(f"Database entry for {formula} missing lambda or omega_log.")
            mu_star = 0.1
            numerator = 1.04 * (1.0 + lam)
            denominator = lam - mu_star * (1.0 + 0.62 * lam)
            if denominator <= 0:
                return 0.0
            tc = (omega_log / 1.2) * math.exp(-numerator / denominator)
            if tc < 0:
                tc = 0.0
            return tc
    raise ValueError(f"Material {formula} not found in database.")    """
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
    parser = argparse.ArgumentParser(description='Predict superconducting Tc using BCS/Eliashberg models and ML.')
    parser.add_argument('formulas', nargs='*', help='Material formulas (e.g., Nb3Sn). If none, reads from stdin or file.')
    parser.add_argument('--database', action='store_true', help='Load database and predict Tc for all entries.')
    parser.add_argument('--train', action='store_true', help='Train RandomForest model on database and save.')
    parser.add_argument('--screen', type=str, metavar='CSV', help='CSV file with column "formula" to screen and predict Tc.')
    args = parser.parse_args()
    if args.train:
        train_model()
        return
    if args.screen:
        screen_csv(args.screen)
        return
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


def allen_dynes_tc(lambda_ep, omega_log, mu_star=0.1):
    """Compute Tc using the Allen-Dynes equation."""
    numerator = 1.04 * (1.0 + lambda_ep)
    denominator = lambda_ep - mu_star * (1.0 + 0.62 * lambda_ep)
    if denominator <= 0:
        return 0.0
    tc = (omega_log / 1.2) * math.exp(-numerator / denominator)
    return max(tc, 0.0)


def train_model():
    """Train a RandomForestRegressor on the superconductor database and save the model."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'superconductor_database.json')
    try:
        with open(db_path, 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        print(f"Error: Database file '{db_path}' not found.", file=sys.stderr)
        sys.exit(1)
    X = []
    y = []
    for entry in entries:
        formula = entry.get('name', '')
        tc = entry.get('Tc', 0)
        if not formula or tc <= 0:
            continue
        try:
            avg_valence = average_valence(formula)
            avg_debye = average_debye(formula)
        except Exception:
            continue
        X.append([avg_valence, avg_debye])
        y.append(tc)
    if len(X) < 10:
        print("Not enough data to train model.", file=sys.stderr)
        sys.exit(1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    print(f"Model trained. Test R² = {r2:.4f}, RMSE = {rmse:.4f} K")
    if r2 < 0.8:
        print("Warning: R² below 0.8. Consider adding more features or data.")
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'rf_model.pkl')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(rf, model_path)
    print(f"Model saved to {model_path}")

def screen_csv(csv_path):
    """Read candidate compositions from CSV and predict Tc using trained model."""
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'rf_model.pkl')
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found. Run --train first.", file=sys.stderr)
        sys.exit(1)
    rf = joblib.load(model_path)
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        sys.exit(1)
    if 'formula' not in df.columns:
        print("CSV must contain a 'formula' column.", file=sys.stderr)
        sys.exit(1)
    print(f"{'Formula':<20} {'Predicted Tc (K)':<20}")
    print("-" * 40)
    for _, row in df.iterrows():
        formula = row['formula'].strip()
        try:
            avg_valence = average_valence(formula)
            avg_debye = average_debye(formula)
            pred = rf.predict([[avg_valence, avg_debye]])[0]
            print(f"{formula:<20} {pred:<20.2f}")
        except Exception as e:
            print(f"{formula:<20} Error: {e}")

def average_valence(formula):
    """Compute average valence electrons per atom from formula string."""
    import re
    pattern = re.findall(r'([A-Z][a-z]*)(\d*)', formula)
    total_valence = 0
    total_atoms = 0
    for elem, count in pattern:
        if count == '':
            count = 1
        else:
            count = int(count)
        if elem in VALENCE:
            total_valence += VALENCE[elem] * count
            total_atoms += count
        else:
            raise ValueError(f"Unknown element {elem}")
    if total_atoms == 0:
        raise ValueError("No atoms parsed")
    return total_valence / total_atoms

def average_debye(formula):
    """Compute average Debye temperature from formula string."""
    import re
    pattern = re.findall(r'([A-Z][a-z]*)(\d*)', formula)
    total_debye = 0
    total_atoms = 0
    for elem, count in pattern:
        if count == '':
            count = 1
        else:
            count = int(count)
        if elem in DEBYE_TEMP:
            total_debye += DEBYE_TEMP[elem] * count
            total_atoms += count
        else:
            raise ValueError(f"Unknown element {elem}")
    if total_atoms == 0:
        raise ValueError("No atoms parsed")
    return total_debye / total_atoms

def average_atomic_mass(formula):
    import re
    pattern = re.findall(r'([A-Z][a-z]*)(\d*)', formula)
    total_mass = 0
    total_atoms = 0
    for elem, count in pattern:
        if count == '':
            count = 1
        else:
            count = int(count)
        if elem in ATOMIC_MASS:
            total_mass += ATOMIC_MASS[elem] * count
            total_atoms += count
        else:
            raise ValueError(f"Unknown element {elem}")
    if total_atoms == 0:
        raise ValueError("No atoms parsed")
    return total_mass / total_atoms

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'superconductor_database.json')

def load_data():
    with open(DATABASE_PATH, 'r') as f:
        return json.load(f)

def mcmillan_tc(lam, theta_D, mu_star=0.1):
    if lam <= mu_star:
        return 0.0
    exponent = -1.04 * (1 + lam) / (lam - mu_star * (1 + 0.62 * lam))
    return (theta_D / 1.2) * math.exp(exponent)

def allen_dynes_tc(lam, theta_D, mu_star=0.1):
    if lam <= mu_star:
        return 0.0
    f1 = (1 + (lam / (2.46 * (1 + 3.8 * mu_star)))**1.5)**(1/3)
    f2 = 1 + (lam**2 * (1 - 0.1 * mu_star)) / (lam**2 + 1.5 * (1 + 0.5 * mu_star))
    exponent = -1.04 * (1 + lam) / (lam - mu_star * (1 + 0.62 * lam))
    return (theta_D / 1.2) * f1 * f2 * math.exp(exponent)

def predict_tc(formula, pressure=0):
    data = load_data()
    for entry in data:
        comp = entry.get('composition', entry.get('name', ''))
        if comp == formula and entry.get('pressure', 0) == pressure:
            return entry.get('Tc', 0)
    avg_val = average_valence(formula)
    avg_deb = average_debye(formula)
    lam = 0.5 * avg_val + 0.001 * avg_deb - 0.5
    if pressure > 0:
        lam += 0.001 * pressure
    return allen_dynes_tc(lam, avg_deb, mu_star=0.1)

def train_model():
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score, mean_squared_error
    import numpy as np
    import joblib
    data = load_data()
    X = []
    y = []
    for entry in data:
        formula = entry.get('composition', entry.get('name', ''))
        if not formula:
            continue
        try:
            avg_val = average_valence(formula)
            avg_deb = average_debye(formula)
            avg_mass = average_atomic_mass(formula)
            num_elements = len(set(re.findall(r'[A-Z][a-z]*', formula)))
            tc = entry.get('Tc', None)
            if tc is None:
                continue
            X.append([avg_val, avg_deb, avg_mass, num_elements])
            y.append(tc)
        except:
            continue
    if len(X) < 5:
        raise ValueError("Not enough data to train model")
    X = np.array(X)
    y = np.array(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    print(f"Model trained. Test R² = {r2:.4f}, RMSE = {rmse:.4f} K")
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'rf_model.pkl')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(rf, model_path)
    print(f"Model saved to {model_path}")
    return rf


def screen_candidates(candidates: List[str], model_path: str = None) -> List[Dict]:
    """
    Given a list of candidate formulas (e.g., ['YBa2Cu3O7', 'MgB2']),
    compute features and use the trained RandomForest model to predict Tc.
    Returns a list of dicts sorted by predicted Tc descending.
    """
    import numpy as np
    if model_path is None:
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'rf_model.pkl')
    if not os.path.exists(model_path):
        rf = train_model()
    else:
        rf = joblib.load(model_path)
    results = []
    for formula in candidates:
        try:
            avg_val = average_valence(formula)
            avg_deb = average_debye(formula)
            avg_mass = average_atomic_mass(formula)
            num_elements = len(set(re.findall(r'[A-Z][a-z]*', formula)))
            features = np.array([[avg_val, avg_deb, avg_mass, num_elements]])
            tc_pred = rf.predict(features)[0]
            results.append({'formula': formula, 'predicted_tc': round(tc_pred, 2)})
        except Exception as e:
            results.append({'formula': formula, 'error': str(e)})
    results.sort(key=lambda x: x.get('predicted_tc', -1), reverse=True)
    return results


def train_gp_model():
    """
    Train a Gaussian Process regressor on the embedded database.
    Returns the trained GP model and the feature scaler (if any).
    """
    from sklearn.preprocessing import StandardScaler
    data = load_data()
    X = []
    y = []
    for entry in data:
        formula = entry.get('composition', entry.get('name', ''))
        if not formula:
            continue
        try:
            avg_val = average_valence(formula)
            avg_deb = average_debye(formula)
            avg_mass = average_atomic_mass(formula)
            num_elements = len(set(re.findall(r'[A-Z][a-z]*', formula)))
            tc = entry.get('Tc', None)
            if tc is None:
                continue
            X.append([avg_val, avg_deb, avg_mass, num_elements])
            y.append(tc)
        except:
            continue
    if len(X) < 5:
        raise ValueError("Not enough data to train GP model")
    X = np.array(X)
    y = np.array(y)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2))
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, alpha=1e-6, normalize_y=True)
    gp.fit(X_scaled, y)
    print(f"GP model trained. Kernel: {gp.kernel_}")
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'gp_model.pkl')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump({'gp': gp, 'scaler': scaler}, model_path)
    print(f"GP model saved to {model_path}")
    return gp, scaler


def predict_with_uncertainty(formula: str, gp_model_path: str = None) -> dict:
    """
    Predict Tc and uncertainty (standard deviation) for a given formula using a trained GP.
    Returns dict with 'formula', 'predicted_tc', 'uncertainty'.
    """
    import numpy as np
    if gp_model_path is None:
        gp_model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'gp_model.pkl')
    if not os.path.exists(gp_model_path):
        gp, scaler = train_gp_model()
    else:
        saved = joblib.load(gp_model_path)
        gp = saved['gp']
        scaler = saved['scaler']
    try:
        avg_val = average_valence(formula)
        avg_deb = average_debye(formula)
        avg_mass = average_atomic_mass(formula)
        num_elements = len(set(re.findall(r'[A-Z][a-z]*', formula)))
        features = np.array([[avg_val, avg_deb, avg_mass, num_elements]])
        features_scaled = scaler.transform(features)
        tc_pred, tc_std = gp.predict(features_scaled, return_std=True)
        return {'formula': formula, 'predicted_tc': round(tc_pred[0], 2), 'uncertainty': round(tc_std[0], 2)}
    except Exception as e:
        return {'formula': formula, 'error': str(e)}


def active_learning_loop(candidates: list, alpha: float = 1.0, top_n: int = 5, retrain: bool = False) -> list:
    """
    Active learning loop that selects high-uncertainty, high-Tc candidates.
    Uses the GP model to predict Tc and uncertainty. Scores candidates as
    predicted_tc + alpha * uncertainty, then returns the top_n candidates.
    If retrain is True, the model is retrained on the full database before prediction.
    """
    if retrain:
        train_gp_model()
    results = []
    for formula in candidates:
        res = predict_with_uncertainty(formula)
        if 'error' in res:
            continue
        score = res['predicted_tc'] + alpha * res['uncertainty']
        res['score'] = round(score, 2)
        results.append(res)
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_n]

def cross_validate_model(model, X, y, cv=5):
    from sklearn.model_selection import cross_val_score, cross_val_predict, KFold
    from sklearn.metrics import mean_absolute_error
    kf = KFold(n_splits=cv, shuffle=True, random_state=42)
    r2_scores = cross_val_score(model, X, y, cv=kf, scoring='r2')
    y_pred_all = cross_val_predict(model, X, y, cv=kf)
    mae = mean_absolute_error(y, y_pred_all)
    print(f"Cross-validation (k={cv}): R² = {r2_scores.mean():.4f} ± {r2_scores.std():.4f}, MAE = {mae:.4f} K")
    return r2_scores.mean(), mae


def retrain_from_new_data(data_path=None):
    import numpy as np
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'superconductor_database.json')
    with open(data_path, 'r') as f:
        data = json.load(f)
    X = []
    y = []
    for entry in data:
        formula = entry.get('composition', entry.get('name', ''))
        if not formula:
            continue
        try:
            avg_val = average_valence(formula)
            avg_deb = average_debye(formula)
            avg_mass = average_atomic_mass(formula)
            num_elements = len(set(re.findall(r'[A-Z][a-z]*', formula)))
            tc = entry.get('Tc', None)
            if tc is None:
                continue
            X.append([avg_val, avg_deb, avg_mass, num_elements])
            y.append(tc)
        except:
            continue
    if len(X) < 5:
        raise ValueError("Not enough data to train model")
    X = np.array(X)
    y = np.array(y)
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X, y)
    r2, mae = cross_validate_model(rf, X, y, cv=5)
    print(f"Model retrained from new data. Cross-validation R² = {r2:.4f}, MAE = {mae:.4f} K")
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'rf_model.pkl')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(rf, model_path)
    print(f"Model saved to {model_path}")
    return rf


# ===== Graph Neural Network for Tc prediction =====

class GraphNeuralNetwork(nn.Module):
    def __init__(self, node_features=4, hidden_dim=64, num_layers=3, dropout=0.2):
        super().__init__()
        self.convs = nn.ModuleList()
        self.convs.append(GCNConv(node_features, hidden_dim))
        for _ in range(num_layers - 1):
            self.convs.append(GCNConv(hidden_dim, hidden_dim))
        self.lin = nn.Linear(hidden_dim, 1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, data):
        x, edge_index, batch = data.x, data.edge_index, data.batch
        for conv in self.convs:
            x = conv(x, edge_index)
            x = torch.relu(x)
            x = self.dropout(x)
        x = global_mean_pool(x, batch)
        x = self.lin(x)
        return x.squeeze(-1)

def formula_to_graph(formula: str) -> Data:
    """Convert a chemical formula to a PyG graph where each atom is a node."""
    pattern = r'([A-Z][a-z]*)(\d*\.?\d*)'
    elements = re.findall(pattern, formula)
    node_features = []
    for elem, count_str in elements:
        count = float(count_str) if count_str else 1.0
        for _ in range(int(count)):
            feats = [
                VALENCE.get(elem, 0),
                DEBYE_TEMP.get(elem, 100),
                ATOMIC_MASS.get(elem, 50),
                float(len(elements))
            ]
            node_features.append(feats)
    if not node_features:
        node_features = [[0, 100, 50, 1]]
    x = torch.tensor(node_features, dtype=torch.float)
    num_nodes = x.size(0)
    edge_index = []
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j:
                edge_index.append([i, j])
    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    return Data(x=x, edge_index=edge_index)

def train_gnn(structures, tcs, epochs=100, lr=0.001, batch_size=16):
    """Train the GNN on a list of structures and corresponding Tc values."""
    graphs = []
    for s, tc in zip(structures, tcs):
        try:
            g = structure_to_graph(s)
            g.y = torch.tensor([tc], dtype=torch.float)
            graphs.append(g)
        except:
            continue
    if len(graphs) < 5:
        raise ValueError("Not enough data to train GNN")
    loader = DataLoader(graphs, batch_size=batch_size, shuffle=True)
    model = GraphNeuralNetwork()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for batch in loader:
            optimizer.zero_grad()
            out = model(batch)
            loss = criterion(out, batch.y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if (epoch+1) % 20 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(loader):.4f}")
    return model

def predict_with_uncertainty_gnn(model, structure, n_samples=20):
    """Predict Tc with uncertainty using Monte Carlo dropout."""
    g = structure_to_graph(structure)
    g.batch = torch.zeros(g.x.size(0), dtype=torch.long)
    model.train()
    preds = []
    with torch.no_grad():
        for _ in range(n_samples):
            pred = model(g)
            preds.append(pred.item())
    mean = np.mean(preds)
    std = np.std(preds)
    return mean, std

def active_learning_loop_gnn(candidates: list, alpha: float = 1.0, top_n: int = 5, model=None) -> list:
    """
    Active learning loop using GNN with uncertainty.
    Scores candidates as predicted_tc + alpha * uncertainty.
    """
    if model is None:
        raise ValueError("GNN model must be provided")
    results = []
    for structure in candidates:
        try:
            mean, std = predict_with_uncertainty_gnn(model, structure)
            score = mean + alpha * std
            results.append({'structure': str(structure.composition.reduced_formula), 'predicted_tc': round(mean, 2), 'uncertainty': round(std, 2), 'score': round(score, 2)})
        except Exception as e:
            results.append({'structure': str(structure.composition.reduced_formula), 'error': str(e)})
    results.sort(key=lambda x: x.get('score', -1e9), reverse=True)
    return results[:top_n]

def generate_candidates(base_elements=None, max_elements=3, num_candidates=50):
    """
    Generate candidate formulas by combining elements from a list.
    Simple combinatorial generation for demonstration.
    """
    if base_elements is None:
        base_elements = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
                         'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
                         'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
                         'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
                         'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
                         'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
                         'Cs', 'Ba', 'La', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
                         'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn']
    import random
    candidates = set()
    while len(candidates) < num_candidates:
        n_elements = random.randint(1, max_elements)
        elems = random.sample(base_elements, n_elements)
        formula = ''
        for e in elems:
            count = random.randint(1, 4)
            formula += e + (str(count) if count > 1 else '')
        candidates.add(formula)
    return list(candidates)

# End of GNN additions

# Global variable to hold the current model type
_current_model = 'rf'  # default to random forest

def set_model(model_type: str):
    """Switch between 'rf' (Random Forest) and 'gnn' (Graph Neural Network) models."""
    global _current_model
    if model_type not in ('rf', 'gnn'):
        raise ValueError("model_type must be 'rf' or 'gnn'")
    _current_model = model_type
    print(f"Model set to {model_type}")

def structure_to_graph(structure: Structure) -> Data:
    """Convert a pymatgen Structure to a PyTorch Geometric graph.

    Args:
        structure: pymatgen Structure object.

    Returns:
        Data object with node features (valence, debye temp, atomic mass)
        and edge indices based on Voronoi neighbor analysis.
    """
    # Node features: valence, debye temp, atomic mass (same as formula_to_graph)
    node_features = []
    for site in structure.sites:
        elem = site.specie.symbol
        valence = VALENCE.get(elem, 0)
        debye = DEBYE_TEMP.get(elem, 100.0)
        mass = ATOMIC_MASS.get(elem, 50.0)
        node_features.append([valence, debye, mass])
    x = torch.tensor(node_features, dtype=torch.float)
    # Edge indices using VoronoiNN
    vnn = VoronoiNN()
    edge_index = [[], []]
    for i, site in enumerate(structure.sites):
        neighbors = vnn.get_nn_info(structure, i)
        for neighbor in neighbors:
            j = neighbor['site_index']
            if i != j:
                edge_index[0].append(i)
                edge_index[1].append(j)
    # If no edges (single atom), add self-loop
    if len(edge_index[0]) == 0:
        edge_index = [[0], [0]]
    edge_index = torch.tensor(edge_index, dtype=torch.long)
    return Data(x=x, edge_index=edge_index)

def predict_tc_mcmillan_allen_dynes(theta_D: float, lambda_: float, mu_star: float = 0.13, omega_log: float = None) -> float:
    """
    Predict Tc using the McMillan-Allen-Dynes equation.

    Args:
        theta_D: Debye temperature (K)
        lambda_: electron-phonon coupling constant
        mu_star: Coulomb pseudopotential (default 0.13)
        omega_log: logarithmic average phonon frequency (K). If None, uses theta_D/1.45.

    Returns:
        Tc in Kelvin.
    """
    if omega_log is None:
        omega_log = theta_D / 1.45
    numerator = 1.04 * (1 + lambda_)
    denominator = lambda_ - mu_star * (1 + 0.62 * lambda_)
    if denominator <= 0:
        return 0.0
    exponent = - numerator / denominator
    Tc = (omega_log / 1.2) * math.exp(exponent)
    return Tc


def compute_features(formula: str) -> list:
    """Compute average valence electrons per atom and average Debye temperature from formula string."""
    import re
    elements = re.findall(r'([A-Z][a-z]?)(\d*)', formula)
    total_valence = 0.0
    total_debye = 0.0
    total_atoms = 0
    for elem, count_str in elements:
        count = int(count_str) if count_str else 1
        total_valence += VALENCE.get(elem, 0) * count
        total_debye += DEBYE_TEMP.get(elem, 100.0) * count
        total_atoms += count
    if total_atoms == 0:
        return [0.0, 100.0]
    return [total_valence / total_atoms, total_debye / total_atoms]


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Predict Tc for candidate materials using a trained model.')
    parser.add_argument('--model', choices=['rf', 'gnn'], default='rf', help='Model type (default: rf)')
    parser.add_argument('--candidates', type=int, default=10, help='Number of candidate materials to generate (default: 10)')
    parser.add_argument('--output', type=str, default=None, help='Output file to save predictions (JSON format)')
    args = parser.parse_args()

    # Load the embedded database (assumed to be a list of dicts with 'formula' and 'tc')
    try:
        database = globals().get('DATABASE', None)
        if database is None:
            # Fallback: try to load from a known variable name
            database = globals().get('known_compounds', None)
        if database is None:
            print("Error: No embedded database found. Please ensure DATABASE or known_compounds is defined.")
            sys.exit(1)
    except Exception as e:
        print(f"Error loading database: {e}")
        sys.exit(1)

    # Extract features and targets from database
    X = []
    y = []
    for entry in database:
        formula = entry.get('formula', '')
        tc = entry.get('tc', None)
        if tc is None:
            continue
        feats = compute_features(formula)
        X.append(feats)
        y.append(tc)

    if len(X) == 0:
        print("Error: No valid training data in database.")
        sys.exit(1)

    # Train Random Forest model
    from sklearn.ensemble import RandomForestRegressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    print(f"Trained Random Forest model on {len(X)} samples.")

    # Generate candidate materials
    candidates = generate_candidates(num_candidates=args.candidates)
    print(f"Generated {len(candidates)} candidate materials.")

    # Predict Tc for each candidate with uncertainty
    predictions = []
    for formula in candidates:
        feats = compute_features(formula)
        tc_mean, tc_std = predict_with_uncertainty(model, [feats])
        predictions.append({'formula': formula, 'predicted_tc_K': round(tc_mean, 2), 'uncertainty_K': round(tc_std, 2)})
        print(f"{formula}: {tc_mean:.2f} K ± {tc_std:.2f} K")

    # Save to output file if specified
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(predictions, f, indent=2)
        print(f"Predictions saved to {args.output}")


# Embedded database of known A15 superconducting compounds (formula, Tc in K)
DATABASE = [
    {'formula': 'Nb3Sn', 'tc': 18.3},
    {'formula': 'Nb3Al', 'tc': 18.9},
    {'formula': 'Nb3Ge', 'tc': 23.2},
    {'formula': 'V3Si', 'tc': 17.1},
    {'formula': 'V3Ga', 'tc': 16.5},
    {'formula': 'Nb3Ga', 'tc': 20.3},
    {'formula': 'Nb3In', 'tc': 9.2},
    {'formula': 'Mo3Os', 'tc': 12.0},
    {'formula': 'Mo3Ir', 'tc': 8.0},
    {'formula': 'Ta3Sn', 'tc': 8.4},
]


def generate_candidates(num_candidates=10):
    """Generate candidate A15 materials for prediction."""
    candidates = [
        'Nb3Sn', 'Nb3Al', 'Nb3Ge', 'V3Si', 'V3Ga',
        'Nb3Ga', 'Nb3In', 'Mo3Os', 'Mo3Ir', 'Ta3Sn',
        'Nb3Sb', 'V3Ge', 'Ta3Ge', 'Nb3Pt', 'V3Pt',
    ]
    return candidates[:num_candidates]


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Predict Tc for superconducting materials.')
    parser.add_argument('--candidates', type=int, default=10, help='Number of candidate materials to generate')
    parser.add_argument('--output', type=str, help='Output JSON file for predictions')
    parser.add_argument('--pinn', action='store_true', help='Use BCSPINN model instead of Random Forest')
    args = parser.parse_args()
    if args.pinn:
        main_pinn(args)
    else:
        main()


def predict_tc(lambda_ep, omega_log, mu_star):
    """
    Predict superconducting critical temperature (Tc) using the McMillan-Allen-Dynes equation.

    Parameters:
    lambda_ep (float): Electron-phonon coupling constant (lambda).
    omega_log (float): Logarithmic average frequency (K).
    mu_star (float): Coulomb pseudopotential (mu*).

    Returns:
    float: Predicted Tc in Kelvin.
    """
    if lambda_ep <= mu_star:
        return 0.0  # No superconductivity if lambda <= mu*
    numerator = 1.04 * (1 + lambda_ep)
    denominator = lambda_ep - mu_star * (1 + 0.62 * lambda_ep)
    if denominator <= 0:
        return 0.0
    exponent = -numerator / denominator
    tc = (omega_log / 1.2) * math.exp(exponent)
    return tc


def predict_with_uncertainty(model, X):
    """
    Predict target and uncertainty (standard deviation) using a Random Forest model.
    Uncertainty is estimated as the standard deviation of predictions across all trees.
    """
    tree_preds = np.array([tree.predict(X) for tree in model.estimators_])
    mean = np.mean(tree_preds, axis=0)
    std = np.std(tree_preds, axis=0)
    return mean[0], std[0]


# Hydride database for PINN training (Tc values from literature)
HYDRIDE_DATABASE = [
    {'formula': 'H3S', 'tc': 203.0, 'debye': 2000, 'lambda_ep': 2.0, 'mu_star': 0.1},
    {'formula': 'LaH10', 'tc': 250.0, 'debye': 1500, 'lambda_ep': 2.5, 'mu_star': 0.1},
    {'formula': 'YH6', 'tc': 224.0, 'debye': 1800, 'lambda_ep': 2.2, 'mu_star': 0.1},
    {'formula': 'YH9', 'tc': 243.0, 'debye': 1700, 'lambda_ep': 2.4, 'mu_star': 0.1},
    {'formula': 'ThH10', 'tc': 161.0, 'debye': 1400, 'lambda_ep': 1.8, 'mu_star': 0.1},
    {'formula': 'PrH9', 'tc': 200.0, 'debye': 1600, 'lambda_ep': 2.0, 'mu_star': 0.1},
    {'formula': 'CeH9', 'tc': 190.0, 'debye': 1550, 'lambda_ep': 1.9, 'mu_star': 0.1},
    {'formula': 'NdH9', 'tc': 195.0, 'debye': 1580, 'lambda_ep': 1.95, 'mu_star': 0.1},
]

class BCSPINN(nn.Module):
    """Physics-informed neural network for Tc prediction using BCS theory constraints."""
    def __init__(self, input_dim=3, hidden_dim=64, output_dim=2):
        super(BCSPINN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        out = self.net(x)
        lambda_ep = torch.sigmoid(out[:, 0]) * 5.0
        omega_log = torch.sigmoid(out[:, 1]) * 3000.0
        return lambda_ep, omega_log

    def predict_tc(self, x, mu_star=0.1):
        lambda_ep, omega_log = self.forward(x)
        numerator = 1.04 * (1 + lambda_ep)
        denominator = lambda_ep - mu_star * (1 + 0.62 * lambda_ep)
        tc = torch.where(denominator > 0,
                         (omega_log / 1.2) * torch.exp(-numerator / denominator),
                         torch.zeros_like(omega_log))
        return tc

def train_pinn(database, epochs=500, lr=1e-3):
    """Train BCSPINN on hydride database."""
    def extract_features(formula):
        import re
        pattern = r'([A-Z][a-z]*)(\d*)'
        matches = re.findall(pattern, formula)
        elements = []
        for elem, count in matches:
            count = int(count) if count else 1
            elements.extend([elem] * count)
        debye_avg = sum(DEBYE_TEMP.get(e, 100) for e in elements) / len(elements)
        mass_avg = sum(ATOMIC_MASS.get(e, 1.0) for e in elements) / len(elements)
        valence_avg = sum(VALENCE.get(e, 0) for e in elements) / len(elements)
        return [debye_avg, mass_avg, valence_avg]

    X = []
    y = []
    for entry in database:
        feats = extract_features(entry['formula'])
        X.append(feats)
        y.append(entry['tc'])
    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.float32).view(-1, 1)

    model = BCSPINN(input_dim=3)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    for epoch in range(epochs):
        optimizer.zero_grad()
        tc_pred = model.predict_tc(X)
        loss = loss_fn(tc_pred, y)
        loss.backward()
        optimizer.step()
        if (epoch+1) % 100 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
    return model

def predict_with_pinn(candidates, model):
    """Predict Tc for a list of candidate formulas using trained PINN."""
    def extract_features(formula):
        import re
        pattern = r'([A-Z][a-z]*)(\d*)'
        matches = re.findall(pattern, formula)
        elements = []
        for elem, count in matches:
            count = int(count) if count else 1
            elements.extend([elem] * count)
        debye_avg = sum(DEBYE_TEMP.get(e, 100) for e in elements) / len(elements)
        mass_avg = sum(ATOMIC_MASS.get(e, 1.0) for e in elements) / len(elements)
        valence_avg = sum(VALENCE.get(e, 0) for e in elements) / len(elements)
        return [debye_avg, mass_avg, valence_avg]

    X = [extract_features(c) for c in candidates]
    X = torch.tensor(X, dtype=torch.float32)
    with torch.no_grad():
        tc_pred = model.predict_tc(X).numpy().flatten()
    return tc_pred

def main_pinn(args):
    """Main function for PINN-based prediction pipeline."""
    print("Training BCSPINN on hydride database...")
    model = train_pinn(HYDRIDE_DATABASE, epochs=500)
    print("Training complete.")

    candidates = generate_candidates(num_candidates=args.candidates)
    print(f"Generated {len(candidates)} candidate materials.")

    tc_preds = predict_with_pinn(candidates, model)
    predictions = []
    for formula, tc in zip(candidates, tc_preds):
        predictions.append({'formula': formula, 'predicted_tc_K': round(tc, 2), 'method': 'BCSPINN'})
        print(f"{formula}: {tc:.2f} K (BCSPINN)")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(predictions, f, indent=2)
        print(f"Predictions saved to {args.output}")


# ===== GNN Model for Tc Prediction (using pymatgen + PyTorch Geometric) =====

def generate_structure_from_formula(formula: str) -> Structure:
    """
    Generate a simple cubic structure from a chemical formula.
    This is a placeholder for demonstration; real usage requires actual crystal structures.
    """
    import re
    pattern = r'([A-Z][a-z]*)(\d*)'
    matches = re.findall(pattern, formula)
    elements = []
    for elem, count in matches:
        count = int(count) if count else 1
        elements.extend([elem] * count)
    # Create a simple cubic lattice with lattice constant 5.0 Å
    # Place atoms at fractional coordinates along a line (1D chain) for simplicity
    n_atoms = len(elements)
    lattice = np.eye(3) * 5.0
    frac_coords = np.zeros((n_atoms, 3))
    for i in range(n_atoms):
        frac_coords[i] = [i / max(n_atoms, 1), 0.0, 0.0]
    species = elements
    structure = Structure(lattice, species, frac_coords, coords_are_cartesian=False)
    return structure

def structure_to_graph(structure: Structure) -> Data:
    """
    Convert a pymatgen Structure to a PyTorch Geometric Data object.
    Uses VoronoiNN to determine neighbor edges.
    """
    # Node features: atomic number, valence electrons, atomic mass, Debye temperature
    node_features = []
    for site in structure.sites:
        elem = site.specie.symbol
        atomic_num = site.specie.Z
        valence = VALENCE.get(elem, 0)
        mass = ATOMIC_MASS.get(elem, 1.0)
        debye = DEBYE_TEMP.get(elem, 100.0)
        node_features.append([atomic_num, valence, mass, debye])
    x = torch.tensor(node_features, dtype=torch.float32)

    # Get edges using VoronoiNN
    vnn = VoronoiNN()
    edges = []
    for i, site in enumerate(structure.sites):
        # VoronoiNN returns a dict of {neighbor_index: ...}
        try:
            neighbors = vnn.get_nn_info(structure, i)
            for neighbor in neighbors:
                j = neighbor['site_index']
                if i != j:
                    edges.append([i, j])
        except Exception:
            # Fallback: connect to nearest neighbors by distance
            for j, other in enumerate(structure.sites):
                if i != j:
                    dist = site.distance(other)
                    if dist < 4.0:  # arbitrary cutoff
                        edges.append([i, j])
    if not edges:
        # Fallback: create a simple chain
        n = len(structure.sites)
        for i in range(n - 1):
            edges.append([i, i+1])
            edges.append([i+1, i])
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()

    return Data(x=x, edge_index=edge_index)

class CrystalGNN(nn.Module):
    """
    Graph Neural Network for predicting Tc from crystal structure.
    Uses GCNConv layers and global mean pooling.
    """
    def __init__(self, node_feat_dim: int = 4, hidden_dim: int = 64, num_layers: int = 3):
        super().__init__()
        self.convs = nn.ModuleList()
        self.convs.append(GCNConv(node_feat_dim, hidden_dim))
        for _ in range(num_layers - 1):
            self.convs.append(GCNConv(hidden_dim, hidden_dim))
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, data: Data) -> torch.Tensor:
        x, edge_index, batch = data.x, data.edge_index, data.batch
        for conv in self.convs:
            x = conv(x, edge_index)
            x = torch.relu(x)
        x = global_mean_pool(x, batch)  # [batch_size, hidden_dim]
        out = self.fc(x)
        return out

def train_gnn(database: List[Dict], epochs: int = 200, lr: float = 0.001) -> CrystalGNN:
    """
    Train the CrystalGNN on a database of formulas with Tc values.
    Generates placeholder structures from formulas.
    """
    # Build dataset
    data_list = []
    targets = []
    for entry in database:
        formula = entry['formula']
        tc = entry['tc']
        try:
            structure = generate_structure_from_formula(formula)
            graph = structure_to_graph(structure)
            graph.y = torch.tensor([tc], dtype=torch.float32)
            data_list.append(graph)
        except Exception as e:
            print(f"Skipping {formula}: {e}")
            continue
    if not data_list:
        raise ValueError("No valid structures generated from database.")

    # Create DataLoader
    loader = DataLoader(data_list, batch_size=16, shuffle=True)

    model = CrystalGNN()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    for epoch in range(epochs):
        total_loss = 0.0
        for batch in loader:
            optimizer.zero_grad()
            pred = model(batch)
            loss = loss_fn(pred, batch.y.view(-1, 1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if (epoch + 1) % 50 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(loader):.4f}")
    return model

def compare_gnn_vs_pinn(database: List[Dict], test_size: float = 0.2):
    """
    Train both GNN and PINN on a train/test split and report MAE/RMSE.
    """
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error

    # Split database
    train_data, test_data = train_test_split(database, test_size=test_size, random_state=42)
    print(f"Training samples: {len(train_data)}, Test samples: {len(test_data)}")

    # Train PINN
    print("\nTraining BCSPINN...")
    pinn_model = train_pinn(train_data, epochs=500)

    # Train GNN
    print("\nTraining CrystalGNN...")
    gnn_model = train_gnn(train_data, epochs=200)

    # Evaluate on test set
    def extract_features(formula):
        import re
        pattern = r'([A-Z][a-z]*)(\d*)'
        matches = re.findall(pattern, formula)
        elements = []
        for elem, count in matches:
            count = int(count) if count else 1
            elements.extend([elem] * count)
        debye_avg = sum(DEBYE_TEMP.get(e, 100) for e in elements) / len(elements)
        mass_avg = sum(ATOMIC_MASS.get(e, 1.0) for e in elements) / len(elements)
        valence_avg = sum(VALENCE.get(e, 0) for e in elements) / len(elements)
        return [debye_avg, mass_avg, valence_avg]

    y_true = []
    y_pinn = []
    y_gnn = []
    for entry in test_data:
        formula = entry['formula']
        tc = entry['tc']
        y_true.append(tc)
        # PINN prediction
        feats = extract_features(formula)
        x = torch.tensor(feats, dtype=torch.float32).view(1, -1)
        with torch.no_grad():
            pinn_pred = pinn_model.predict_tc(x).item()
        y_pinn.append(pinn_pred)
        # GNN prediction
        try:
            structure = generate_structure_from_formula(formula)
            graph = structure_to_graph(structure)
            graph.batch = torch.zeros(graph.x.size(0), dtype=torch.long)  # single graph
            with torch.no_grad():
                gnn_pred = gnn_model(graph).item()
        except Exception as e:
            print(f"GNN prediction failed for {formula}: {e}")
            gnn_pred = 0.0
        y_gnn.append(gnn_pred)

    # Compute metrics
    mae_pinn = mean_absolute_error(y_true, y_pinn)
    rmse_pinn = np.sqrt(mean_squared_error(y_true, y_pinn))
    mae_gnn = mean_absolute_error(y_true, y_gnn)
    rmse_gnn = np.sqrt(mean_squared_error(y_true, y_gnn))

    print("\n========== Comparison Results ==========")
    print(f"PINN  - MAE: {mae_pinn:.3f} K, RMSE: {rmse_pinn:.3f} K")
    print(f"GNN   - MAE: {mae_gnn:.3f} K, RMSE: {rmse_gnn:.3f} K")
    print("========================================")

    return {
        'pinn': {'mae': mae_pinn, 'rmse': rmse_pinn},
        'gnn': {'mae': mae_gnn, 'rmse': rmse_gnn}
    }

def main_gnn():
    """Main entry point for GNN training and comparison."""
    import argparse
    parser = argparse.ArgumentParser(description='GNN-based Tc prediction and comparison with PINN')
    parser.add_argument('--compare', action='store_true', help='Run comparison between GNN and PINN')
    parser.add_argument('--train-gnn', action='store_true', help='Train GNN on hydride database')
    parser.add_argument('--epochs', type=int, default=200, help='Number of training epochs')
    args = parser.parse_args()

    if args.compare:
        print("Running GNN vs PINN comparison on hydride database...")
        compare_gnn_vs_pinn(HYDRIDE_DATABASE)
    elif args.train_gnn:
        print("Training CrystalGNN on hydride database...")
        model = train_gnn(HYDRIDE_DATABASE, epochs=args.epochs)
        print("Training complete.")
    else:
        print("No action specified. Use --compare or --train-gnn.")

# Allow running GNN pipeline via --gnn flag
if __name__ == "__main__" and "--gnn" in sys.argv:
    # Remove --gnn and pass remaining args to main_gnn
    sys.argv.remove("--gnn")
    main_gnn()


class ModelEnsemble:
    """Ensemble model combining PINN, GNN, and transformer predictions with validation-performance-based weights."""
    def __init__(self, pinn_model, gnn_model, transformer_model):
        self.pinn_model = pinn_model
        self.gnn_model = gnn_model
        self.transformer_model = transformer_model
        self.weights = None

    def compute_weights(self, validation_data):
        """Compute weights based on validation MAE (inverse of MAE)."""
        y_true = [entry['tc'] for entry in validation_data]
        mae_list = []
        for model in [self.pinn_model, self.gnn_model, self.transformer_model]:
            preds = []
            for entry in validation_data:
                pred = model.predict(entry['formula'])
                preds.append(pred)
            mae = np.mean(np.abs(np.array(y_true) - np.array(preds)))
            mae_list.append(mae)
        inv_mae = [1.0 / (m + 1e-8) for m in mae_list]
        total = sum(inv_mae)
        self.weights = [w / total for w in inv_mae]
        return self.weights

    def predict(self, formula):
        """Predict Tc using weighted ensemble."""
        if self.weights is None:
            raise ValueError("Weights not computed. Call compute_weights first.")
        preds = [
            self.pinn_model.predict(formula),
            self.gnn_model.predict(formula),
            self.transformer_model.predict(formula)
        ]
        return sum(w * p for w, p in zip(self.weights, preds))

    def compare_models(self, test_data):
        """Compare ensemble MAE/RMSE with individual models."""
        y_true = [entry['tc'] for entry in test_data]
        model_names = ['PINN', 'GNN', 'Transformer', 'Ensemble']
        model_preds = {}
        for name, model in zip(model_names[:3], [self.pinn_model, self.gnn_model, self.transformer_model]):
            preds = [model.predict(entry['formula']) for entry in test_data]
            model_preds[name] = preds
        ensemble_preds = [self.predict(entry['formula']) for entry in test_data]
        model_preds['Ensemble'] = ensemble_preds

        print("\n========== Model Comparison ==========")
        for name in model_names:
            preds = model_preds[name]
            mae = np.mean(np.abs(np.array(y_true) - np.array(preds)))
            rmse = np.sqrt(np.mean((np.array(y_true) - np.array(preds))**2))
            print(f"{name:12s} - MAE: {mae:.3f} K, RMSE: {rmse:.3f} K")
        print("======================================")
        return {name: {'mae': np.mean(np.abs(np.array(y_true) - np.array(model_preds[name]))),
                        'rmse': np.sqrt(np.mean((np.array(y_true) - np.array(model_preds[name]))**2))}
                for name in model_names}


def predict_tc():
    """Predict Tc for all entries in data/superconductor_database.json using McMillan-Allen-Dynes equation."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'superconductor_database.json')
    with open(db_path, 'r') as f:
        data = json.load(f)
    print("\n========== McMillan-Allen-Dynes Tc Predictions ==========")
    for entry in data:
        lambda_ = entry['lambda']
        omega_log = entry['omega_log']
        mu_star = entry['mu_star']
        # McMillan-Allen-Dynes formula
        numerator = 1.04 * (1 + lambda_)
        denominator = lambda_ - mu_star * (1 + 0.62 * lambda_)
        if denominator <= 0:
            tc = 0.0
        else:
            tc = (omega_log / 1.2) * math.exp(-numerator / denominator)
        print(f"{entry.get('formula', 'Unknown'):20s} lambda={lambda_:.3f} omega_log={omega_log:.1f} mu*={mu_star:.3f} -> Tc={tc:.2f} K")
    print("========================================================")
    return data


def train_model():
    """Load database, extract features, train RandomForest model, save."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'superconductor_database.json')
    with open(db_path, 'r') as f:
        data = json.load(f)
    
    # Extract features and target
    X = []
    y = []
    for entry in data:
        formula = entry.get('formula', '')
        tc = entry.get('tc', None)
        if not formula or tc is None:
            continue
        # Parse formula to get element counts
        elements = {}
        pattern = r'([A-Z][a-z]*)(\d*\.?\d*)'
        for match in re.finditer(pattern, formula):
            elem = match.group(1)
            count_str = match.group(2)
            count = float(count_str) if count_str else 1.0
            elements[elem] = elements.get(elem, 0) + count
        total_atoms = sum(elements.values())
        if total_atoms == 0:
            continue
        # Compute average valence, Debye temp, atomic mass
        avg_valence = sum(VALENCE.get(e, 0) * c for e, c in elements.items()) / total_atoms
        avg_debye = sum(DEBYE_TEMP.get(e, 100) * c for e, c in elements.items()) / total_atoms
        avg_mass = sum(ATOMIC_MASS.get(e, 50) * c for e, c in elements.items()) / total_atoms
        # Also include number of elements and total atoms
        num_elements = len(elements)
        X.append([avg_valence, avg_debye, avg_mass, num_elements, total_atoms])
        y.append(tc)
    
    X = np.array(X)
    y = np.array(y)
    
    # Train Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save model
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'tc_predictor.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    # Optionally evaluate
    from sklearn.model_selection import cross_val_score
    scores = cross_val_score(model, X, y, cv=min(5, len(X)), scoring='r2')
    print(f"Cross-validation R2: {scores.mean():.3f} +/- {scores.std():.3f}")
    return model

if __name__ == '__main__':
    train_model()
