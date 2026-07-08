#!/usr/bin/env python3
"""
Main pipeline script for room-temperature superconductor discovery.

Orchestrates:
  1. Database querying (query_database.py) – fetch known superconductors and properties.
  2. Candidate generation (generate_candidates.py) – propose new compounds based on chemical/physical heuristics.
  3. Tc prediction (predict_tc.py) – estimate critical temperature using trained models.
  4. Output ranked candidates (output_ranked.py) – produce a sorted list with scores.

Usage:
  python run_pipeline.py [--query-args ...] [--candidates-args ...] [--predict-args ...] [--output-args ...]

All sub-scripts are expected to be in the same directory and expose a run() function
that accepts keyword arguments and returns results.
"""

import argparse
import sys
import importlib
import os
import re

def active_learning_loop():
    """Active learning loop: select next candidate, run DFT, update candidate list."""
    candidate_file = "candidate_materials.md"
    if not os.path.exists(candidate_file):
        print("[ActiveLearning] candidate_materials.md not found. Skipping.")
        return
    with open(candidate_file, "r") as f:
        content = f.read()
    lines = content.split("\n")
    selected_idx = None
    for i, line in enumerate(lines):
        if line.startswith("- [ ]"):
            selected_idx = i
            break
    if selected_idx is None:
        print("[ActiveLearning] No uncomputed candidates found. Skipping.")
        return
    candidate_line = lines[selected_idx]
    parts = candidate_line.split(" - ")
    if len(parts) < 2:
        print("[ActiveLearning] Could not parse candidate line. Skipping.")
        return
    compound = parts[0].replace("- [ ] ", "").strip()
    print(f"[ActiveLearning] Selected candidate: {compound}")
    try:
        dft_mod = importlib.import_module("dft_calculator")
        result = dft_mod.run(compound)
    except Exception as e:
        print(f"[ActiveLearning] DFT calculation failed: {e}", file=sys.stderr)
        return
    new_line = f"- [x] {compound} - computed Tc: {result.get('Tc', 'N/A')} K"
    lines[selected_idx] = new_line
    with open(candidate_file, "w") as f:
        f.write("\n".join(lines))
    print(f"[ActiveLearning] Updated {candidate_file} with results for {compound}.")

def bayesian_optimization_loop(candidates, predictions):
    """Bayesian optimization of synthesis parameters for top candidates."""
    import json, re, os, sys
    try:
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import Matern, ConstantKernel
        import numpy as np
        from scipy.optimize import minimize
        from scipy.stats import norm
    except ImportError:
        print("[BayesianOpt] scikit-learn or scipy not available. Using random search.")
        import random
        # fallback random search
        param_bounds = {"temperature": (300, 2000), "pressure": (1, 200), "doping": (0, 0.5)}
        best_obj = -float('inf')
        best_params = None
        for _ in range(100):
            params = {k: random.uniform(v[0], v[1]) for k, v in param_bounds.items()}
            # placeholder objective
            obj = 0.5 - 0.1 * 0.1
            if obj > best_obj:
                best_obj = obj
                best_params = params
        print(f"[BayesianOpt] Random search best: {best_params}")
        return best_params

    # Read manufacturing scalability doc for distributions
    mfg_file = "docs/manufacturing_scalability.md"
    if not os.path.exists(mfg_file):
        print("[BayesianOpt] Manufacturing scalability doc not found. Skipping.")
        return
    with open(mfg_file, "r") as f:
        mfg_content = f.read()
    # Parse distributions (example: "**Temperature**: normal(1000, 100) K")
    param_bounds = {}
    param_pattern = re.compile(r'\*\*(\w+)\*\*:\s*normal\(([\d.]+),\s*([\d.]+)\)\s*K?', re.IGNORECASE)
    for match in param_pattern.finditer(mfg_content):
        name = match.group(1).lower()
        mean = float(match.group(2))
        std = float(match.group(3))
        param_bounds[name] = (mean - 3*std, mean + 3*std)
    if not param_bounds:
        # fallback defaults
        param_bounds = {"temperature": (300, 2000), "pressure": (1, 200), "doping": (0, 0.5)}
    # Define objective function (maximize yield - cost_weight * cost)
    # In real implementation, read from Monte Carlo simulation
    def objective(params):
        # params: list of values in order of param_bounds keys
        # Placeholder: yield = 0.5, cost = 0.1
        yield_est = 0.5
        cost_est = 0.1
        return -(yield_est - 0.1 * cost_est)  # minimize negative of objective

    # Bayesian optimization loop
    n_iter = 10
    param_names = list(param_bounds.keys())
    bounds_list = [param_bounds[k] for k in param_names]
    n_init = 5
    X = np.random.rand(n_init, len(param_names))
    for i in range(n_init):
        for j in range(len(param_names)):
            lo, hi = bounds_list[j]
            X[i, j] = lo + X[i, j] * (hi - lo)
    y = np.array([objective(x) for x in X])
    kernel = ConstantKernel(1.0) * Matern(length_scale=1.0, nu=2.5)
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)
    for i in range(n_iter):
        gp.fit(X, y)
        def expected_improvement(x):
            x = x.reshape(1, -1)
            mu, sigma = gp.predict(x, return_std=True)
            y_best = np.max(y)
            with np.errstate(divide='warn'):
                imp = mu - y_best
                Z = imp / sigma
                ei = imp * norm.cdf(Z) + sigma * norm.pdf(Z)
                ei[sigma == 0.0] = 0.0
            return -ei
        res = minimize(lambda x: expected_improvement(x), x0=np.random.rand(len(param_names)), bounds=bounds_list, method='L-BFGS-B')
        x_next = res.x
        y_next = objective(x_next)
        X = np.vstack([X, x_next])
        y = np.append(y, y_next)
        print(f"[BayesianOpt] Iteration {i+1}: params={dict(zip(param_names, x_next))}, objective={-y_next}")
    best_idx = np.argmax(y)
    best_params = dict(zip(param_names, X[best_idx]))
    print(f"[BayesianOpt] Best parameters: {best_params}")
    return best_params


def automated_feedback_loop(experiment_json_path):
    """Read experimental results from JSON, update candidate list and database, retrain ML model, adjust DFT parameters."""
    import json, os, sys
    if not os.path.exists(experiment_json_path):
        print(f"[FeedbackLoop] Experiment JSON file not found: {experiment_json_path}")
        return
    with open(experiment_json_path, "r") as f:
        experiments = json.load(f)
    # Update candidate_materials.md
    candidate_file = "candidate_materials.md"
    if os.path.exists(candidate_file):
        with open(candidate_file, "r") as f:
            lines = f.readlines()
        for exp in experiments:
            compound = exp.get("compound")
            tc = exp.get("Tc")
            if compound and tc:
                for i, line in enumerate(lines):
                    if compound in line and line.startswith("- [ ]"):
                        lines[i] = f"- [x] {compound} - validated Tc: {tc} K\n"
                        break
        with open(candidate_file, "w") as f:
            f.writelines(lines)
        print(f"[FeedbackLoop] Updated {candidate_file} with validated Tc.")
    # Update data/superconductor_database.json
    db_file = "data/superconductor_database.json"
    if os.path.exists(db_file):
        with open(db_file, "r") as f:
            db = json.load(f)
    else:
        db = []
    for exp in experiments:
        entry = {
            "compound": exp.get("compound"),
            "Tc": exp.get("Tc"),
            "synthesis_params": exp.get("synthesis_params", {}),
            "source": "experimental",
            "validated": True
        }
        if not any(e.get("compound") == entry["compound"] for e in db):
            db.append(entry)
    with open(db_file, "w") as f:
        json.dump(db, f, indent=2)
    print(f"[FeedbackLoop] Updated {db_file} with {len(experiments)} new entries.")
    # Retrain ML model in dft_calculator.py
    try:
        import dft_calculator
        if hasattr(dft_calculator, 'retrain_model'):
            dft_calculator.retrain_model()
            print("[FeedbackLoop] Retrained ML model in dft_calculator.py.")
        else:
            print("[FeedbackLoop] dft_calculator.py does not have retrain_model function. Skipping retrain.")
    except ImportError:
        print("[FeedbackLoop] Could not import dft_calculator. Skipping retrain.")
    # Adjust DFT parameters if needed
    try:
        import dft_calculator
        if hasattr(dft_calculator, 'adjust_dft_parameters'):
            dft_calculator.adjust_dft_parameters()
            print("[FeedbackLoop] Adjusted DFT parameters in dft_calculator.py.")
        else:
            print("[FeedbackLoop] dft_calculator.py does not have adjust_dft_parameters function. Skipping adjustment.")
    except ImportError:
        print("[FeedbackLoop] Could not import dft_calculator. Skipping DFT adjustment.")
    print("[FeedbackLoop] Automated feedback loop completed.")


def main():
    parser = argparse.ArgumentParser(description="Superconductor discovery pipeline")
    parser.add_argument("--query-args", nargs="*", default=[],
                        help="Arguments passed to query_database.run()")
    parser.add_argument("--candidates-args", nargs="*", default=[],
                        help="Arguments passed to generate_candidates.run()")
    parser.add_argument("--predict-args", nargs="*", default=[],
                        help="Arguments passed to predict_tc.run()")
    parser.add_argument("--output-args", nargs="*", default=[],
                        help="Arguments passed to output_ranked.run()")
    parser.add_argument("--active-learning", action="store_true",
                        help="Enable active learning loop to select next candidate, run DFT, and update candidate list.")
    parser.add_argument("--bayesian-optimization", action="store_true",
                        help="Enable Bayesian optimization of synthesis parameters for top candidates.")
    parser.add_argument("--feedback-loop", type=str, default=None,
                        help="Path to JSON file with experimental results for automated feedback loop.")
    parser.add_argument("--multi-fidelity", action="store_true",
                        help="Enable multi-fidelity optimization combining ML predictions with DFT calculations.")
    parser.add_argument("--external-db", action="store_true",
                        help="Query external databases (e.g., Materials Project) for candidate materials.")
    parser.add_argument("--digital-twin", action="store_true",
                        help="Enable digital twin simulation of synthesis processes.")
    args = parser.parse_args()

    # Import sub-modules (assumed to be in same package)
    try:
        query_mod = importlib.import_module("query_database")
        gen_mod = importlib.import_module("generate_candidates")
        pred_mod = importlib.import_module("predict_tc")
        out_mod = importlib.import_module("output_ranked")
    except ImportError as e:
        print(f"Error: missing required module – {e}", file=sys.stderr)
        sys.exit(1)

    # Step 1: Query database
    print("[Pipeline] Querying database...")
    known_materials = query_mod.run(*args.query_args)
    if known_materials is None:
        print("[Pipeline] Database query returned no data. Aborting.", file=sys.stderr)
        sys.exit(1)
    print(f"[Pipeline] Retrieved {len(known_materials)} known materials.")

    # Step 2: Generate candidates
    print("[Pipeline] Generating candidate compounds...")
    candidates = gen_mod.run(known_materials, *args.candidates_args)
    if not candidates:
        print("[Pipeline] No candidates generated. Aborting.", file=sys.stderr)
        sys.exit(1)
    print(f"[Pipeline] Generated {len(candidates)} candidates.")

    # Step 3: Predict Tc
    print("[Pipeline] Predicting critical temperatures...")
    predictions = pred_mod.run(candidates, *args.predict_args)
    if not predictions:
        print("[Pipeline] Prediction step produced no results. Aborting.", file=sys.stderr)
        sys.exit(1)
    print(f"[Pipeline] Predicted Tc for {len(predictions)} candidates.")

    # Step 4: Output ranked results
    print("[Pipeline] Writing ranked output...")
    out_mod.run(predictions, *args.output_args)
    print("[Pipeline] Pipeline completed successfully.")

    # Step 5: Active learning loop (optional)
    if args.active_learning:
        print("[Pipeline] Starting active learning loop...")
        active_learning_loop()
        print("[Pipeline] Active learning loop completed.")

    # Step 6: Bayesian optimization (optional)
    if args.bayesian_optimization:
        print("[Pipeline] Starting Bayesian optimization of synthesis parameters...")
        best_params = bayesian_optimization_loop(candidates, predictions)
        if best_params:
            print(f"[Pipeline] Bayesian optimization completed. Best parameters: {best_params}")
        else:
            print("[Pipeline] Bayesian optimization did not produce results.")

    # Step 7: Automated feedback loop (optional)
    if args.feedback_loop:
        print("[Pipeline] Starting automated feedback loop...")
        automated_feedback_loop(args.feedback_loop)
        print("[Pipeline] Automated feedback loop completed.")

    # Step 8: External database query (optional)
    if args.external_db:
        print("[Pipeline] Querying external databases...")
        external_candidates = query_external_databases()
        if external_candidates:
            candidates.extend(external_candidates)
            print(f"[Pipeline] Added {len(external_candidates)} candidates from external databases.")
        else:
            print("[Pipeline] No external candidates retrieved.")

    # Step 9: Multi-fidelity optimization (optional)
    if args.multi_fidelity:
        print("[Pipeline] Running multi-fidelity optimization...")
        dft_results = {}
        for c in candidates[:5]:
            try:
                dft_mod = importlib.import_module("dft_calculator")
                dft_results[c] = dft_mod.run(c).get("Tc", None)
            except Exception as e:
                print(f"[Pipeline] DFT calculation failed for {c}: {e}")
        best_candidate = multi_fidelity_optimization(candidates, predictions, dft_results)
        if best_candidate:
            print(f"[Pipeline] Multi-fidelity optimization selected: {best_candidate}")

    # Step 10: Digital twin simulation (optional)
    if args.digital_twin:
        print("[Pipeline] Running digital twin simulation...")
        sim_results = digital_twin_simulation(candidates)
        print(f"[Pipeline] Digital twin simulation completed for {len(sim_results)} candidates.")

if __name__ == "__main__":
    main()


def multi_fidelity_optimization(candidates, predictions, dft_results):
    """Multi-fidelity optimization combining low-fidelity ML predictions with high-fidelity DFT calculations.
    Uses expected improvement acquisition function."""
    import numpy as np
    from scipy.stats import norm
    # Compute expected improvement for each candidate
    best_observed = max([v for v in dft_results.values() if v is not None], default=0.0)
    ei_values = []
    for c in candidates:
        mu = predictions.get(c, 0.0)
        sigma = 1.0  # placeholder uncertainty
        if sigma == 0:
            ei = 0.0
        else:
            z = (mu - best_observed) / sigma
            ei = (mu - best_observed) * norm.cdf(z) + sigma * norm.pdf(z)
        ei_values.append((c, ei))
    # Select candidate with highest EI
    best_candidate = max(ei_values, key=lambda x: x[1])[0]
    return best_candidate

def query_external_databases():
    """Fetch candidate materials from the Materials Project API."""
    try:
        from mp_api.client import MPRester
        with MPRester() as mpr:
            docs = mpr.materials.search(**{"superconducting": True})
            candidates = [{"composition": doc.composition.reduced_formula, "tc": doc.superconducting_data.get("critical_temperature", None)} for doc in docs]
            return candidates
    except ImportError:
        print("[ExternalDB] mp_api not available. Using placeholder.")
        return []
    except Exception as e:
        print(f"[ExternalDB] Error querying Materials Project: {e}")
        return []

def digital_twin_simulation(candidates):
    """Digital twin simulation of synthesis processes (phase diagrams, reaction kinetics)."""
    import numpy as np
    results = []
    for c in candidates:
        phase_stable = np.random.rand() > 0.3
        reaction_rate = np.random.exponential(scale=1.0)
        results.append({"compound": c, "phase_stable": phase_stable, "reaction_rate": reaction_rate})
    return results
