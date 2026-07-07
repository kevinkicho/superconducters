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
