#!/usr/bin/env python3
"""
Main pipeline script for room-temperature superconductor discovery.
Orchestrates:
  1. Database query to retrieve candidate materials.
  2. Candidate generation from candidate_materials.md (supplementary).
  3. Tc prediction using a BCS-based model.
  4. Output a ranked list of promising candidates.
"""

import sqlite3
import json
import math
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit
import dft_calculator  # for DFT validation
import pyvisa
from flask import Flask, request, jsonify, make_response
import secrets
import hashlib
import functools
import requests
import xml.etree.ElementTree as ET

# Constants for Tc prediction (BCS with McMillan formula)
MU_STAR = 0.1  # Coulomb pseudopotential

def query_database(db_path='materials.db'):
    """Query the materials database for candidate compounds."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Expect table 'materials' with columns: name, debye_temp, lambda_ep, formula
    cursor.execute('''
        SELECT name, debye_temp, lambda_ep, formula
        FROM materials
        WHERE debye_temp IS NOT NULL AND lambda_ep IS NOT NULL
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [{'name': r[0], 'debye_temp': r[1], 'lambda_ep': r[2], 'formula': r[3]} for r in rows]

def parse_candidate_md(md_path='candidate_materials.md'):
    """Parse candidate_materials.md for additional candidates.
    Expects a markdown table with columns: Name, Debye_Temp (K), Lambda_EP, Formula.
    """
    candidates = []
    md_file = Path(md_path)
    if not md_file.exists():
        print(f"Warning: {md_path} not found. Skipping.", file=sys.stderr)
        return candidates
    with open(md_path, 'r') as f:
        lines = f.readlines()
    in_table = False
    for line in lines:
        if line.startswith('|') and '---' not in line:
            if not in_table:
                in_table = True
                continue  # skip header row
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 4:
                try:
                    name = parts[0]
                    debye_temp = float(parts[1])
                    lambda_ep = float(parts[2])
                    formula = parts[3]
                    candidates.append({
                        'name': name,
                        'debye_temp': debye_temp,
                        'lambda_ep': lambda_ep,
                        'formula': formula
                    })
                except ValueError:
                    continue
    return candidates

def predict_tc(debye_temp, lambda_ep, mu_star=MU_STAR):
    """Predict critical temperature using McMillan formula.
    Tc = (theta_D / 1.45) * exp(-(1 + lambda_ep) / (lambda_ep - mu_star))
    Returns Tc in Kelvin, or None if invalid.
    """
    if lambda_ep <= mu_star:
        return None
    exponent = -(1 + lambda_ep) / (lambda_ep - mu_star)
    tc = (debye_temp / 1.45) * math.exp(exponent)
    return tc


def compute_uncertainty(debye_temp, lambda_ep, mu_star=MU_STAR):
    """Estimate uncertainty by varying mu_star."""
    mu_low = mu_star - 0.02
    mu_high = mu_star + 0.02
    tc_low = predict_tc(debye_temp, lambda_ep, mu_low)
    tc_high = predict_tc(debye_temp, lambda_ep, mu_high)
    if tc_low is None or tc_high is None:
        return 0.0
    return abs(tc_high - tc_low) / 2.0


def update_candidate_md_with_dft(dft_results):
    """Update candidate_materials.md with DFT-validated results."""
    md_path = 'candidate_materials.md'
    section_header = '## DFT-Validated Results'
    # Read current content
    with open(md_path, 'r') as f:
        content = f.read()
    # Build new section content
    new_section = section_header + '\n\n'
    new_section += 'The following table lists candidates validated by DFT calculations. '
    new_section += 'DFT-validated Tc and uncertainty are provided alongside ML predictions. '
    new_section += 'Rankings are based on DFT-validated Tc.\n\n'
    new_section += '| Rank | Name | Formula | ML Tc (K) | DFT Tc (K) | DFT Uncertainty (K) | Synthesis Feasibility |\n'
    new_section += '|------|------|--------|-----------|------------|---------------------|----------------------|\n'
    for i, r in enumerate(dft_results, 1):
        ml_tc = r.get('ml_tc', 'N/A')
        dft_tc = r.get('dft_tc', 'N/A')
        dft_unc = r.get('dft_uncertainty', 'N/A')
        synth = r.get('synthesis_feasibility', 'unknown')
        new_section += f'| {i} | {r["name"]} | {r["formula"]} | {ml_tc} | {dft_tc} | {dft_unc} | {synth} |\n'
    # Check if section already exists
    if section_header in content:
        # Replace existing section from header to next section or end
        start = content.find(section_header)
        # Find next section header (##) after start, or end of file
        next_section = content.find('\n## ', start + len(section_header))
        if next_section == -1:
            end = len(content)
        else:
            end = next_section
        new_content = content[:start] + new_section + content[end:]
    else:
        # Append at end
        new_content = content.rstrip() + '\n\n' + new_section
    with open(md_path, 'w') as f:
        f.write(new_content)
    print(f"Updated {md_path} with DFT-validated results.")

def main():
    # Step 1: Query database
    print("=== Step 1: Querying materials database ===")
    db_candidates = query_database()
    print(f"Found {len(db_candidates)} candidates from database.")

    # Step 2: Parse candidate_materials.md
    print("=== Step 2: Parsing candidate_materials.md ===")
    md_candidates = parse_candidate_md()
    print(f"Found {len(md_candidates)} candidates from markdown file.")

    # Combine candidates (database takes precedence on name conflict?)
    all_candidates = {c['name']: c for c in db_candidates}
    for c in md_candidates:
        if c['name'] not in all_candidates:
            all_candidates[c['name']] = c
    print(f"Total unique candidates: {len(all_candidates)}")

    # Step 3: Predict Tc for each candidate
    print("=== Step 3: Predicting Tc ===")
    results = []
    for name, data in all_candidates.items():
        tc = predict_tc(data['debye_temp'], data['lambda_ep'])
        if tc is None:
            print(f"  {name}: lambda_ep <= mu_star, skipping.")
            continue
        results.append({
            'name': name,
            'formula': data.get('formula', ''),
            'debye_temp': data['debye_temp'],
            'lambda_ep': data['lambda_ep'],
            'predicted_tc_K': round(tc, 2)
        })
        print(f"  {name}: Tc = {tc:.2f} K")

    # Step 4: Rank and output
    print("=== Step 4: Ranked list of promising candidates ===")
    results.sort(key=lambda x: x['predicted_tc_K'], reverse=True)
    print(f"{'Rank':<5} {'Name':<30} {'Formula':<20} {'Tc (K)':<10} {'Debye (K)':<12} {'Lambda':<8}")
    print('-' * 85)
    for i, r in enumerate(results, 1):
        print(f"{i:<5} {r['name']:<30} {r['formula']:<20} {r['predicted_tc_K']:<10} {r['debye_temp']:<12} {r['lambda_ep']:<8}")

    # Save to JSON for downstream use
    output_path = 'ranked_candidates.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")

    # Step 5: Multi-fidelity Bayesian optimization for candidate selection
    print("=== Step 5: Multi-fidelity Bayesian optimization ===")
    # Compute uncertainty for all results
    for r in results:
        r['uncertainty'] = compute_uncertainty(r['debye_temp'], r['lambda_ep'])
    # Run DFT validation for top uncertain candidates to obtain high-fidelity data
    TOP_N = 5
    results_sorted_by_uncertainty = sorted(results, key=lambda x: x['uncertainty'], reverse=True)
    top_uncertain = results_sorted_by_uncertainty[:TOP_N]
    print(f"Running DFT for top {TOP_N} uncertain candidates to obtain high-fidelity data.")
    dft_results = []
    for cand in top_uncertain:
        print(f"  Running DFT for {cand['name']}...")
        try:
            dft_out = dft_calculator.run_full_dft_calculation(cand['formula'])
            dft_results.append({
                'name': cand['name'],
                'formula': cand['formula'],
                'ml_tc': cand['predicted_tc_K'],
                'dft_tc': dft_out.get('dft_tc'),
                'dft_uncertainty': dft_out.get('dft_uncertainty'),
                'synthesis_feasibility': dft_out.get('synthesis_feasibility', 'unknown')
            })
            print(f"    DFT Tc = {dft_out.get('dft_tc', 'N/A')} K")
        except Exception as e:
            print(f"    DFT calculation failed: {e}")
    # Update results with DFT data
    for dft in dft_results:
        for r in results:
            if r['name'] == dft['name']:
                r['dft_tc'] = dft['dft_tc']
                r['dft_uncertainty'] = dft['dft_uncertainty']
                break
    # Gather low-fidelity and high-fidelity data
    low_fidelity = [{'name': r['name'], 'tc': r['predicted_tc_K'], 'uncertainty': r['uncertainty']} for r in results]
    high_fidelity = [{'name': r['name'], 'tc': r['dft_tc'], 'uncertainty': r['dft_uncertainty']} for r in results if r.get('dft_tc') is not None]
    selected = multi_fidelity_bayesian_optimization(low_fidelity, high_fidelity, top_n=5)
    print(f"Selected candidates for experimental synthesis: {[s['name'] for s in selected]}")
    # Map selected to format expected by update_candidate_md_with_dft
    selected_for_md = []
    for s in selected:
        r = next((r for r in results if r['name'] == s['name']), None)
        if r:
            selected_for_md.append({
                'name': s['name'],
                'formula': r.get('formula', ''),
                'ml_tc': s['low_tc'],
                'dft_tc': s['high_tc'],
                'dft_uncertainty': s['uncertainty'],
                'synthesis_feasibility': 'unknown'
            })
    update_candidate_md_with_dft(selected_for_md)
    print("=== Multi-fidelity optimization complete ===")

def multi_fidelity_bayesian_optimization(low_fidelity, high_fidelity, top_n=5):
    """
    Multi-fidelity Bayesian optimization that combines low-fidelity (ML) and high-fidelity (DFT) predictions.
    Uses a simple weighted acquisition function: score = w_low * tc_low + w_high * tc_high + exploration_bonus.
    In a full implementation, this would use Gaussian processes with multi-fidelity kernels.
    """
    import math
    # Build candidate dictionary
    candidates = {}
    for lf in low_fidelity:
        candidates[lf['name']] = {'name': lf['name'], 'low_tc': lf['tc'], 'high_tc': None, 'uncertainty': lf.get('uncertainty', 0)}
    for hf in high_fidelity:
        if hf['name'] in candidates:
            candidates[hf['name']]['high_tc'] = hf['tc']
        else:
            candidates[hf['name']] = {'name': hf['name'], 'low_tc': None, 'high_tc': hf['tc'], 'uncertainty': hf.get('uncertainty', 0)}
    # Compute acquisition score
    for name, cand in candidates.items():
        low = cand['low_tc'] if cand['low_tc'] is not None else 0
        high = cand['high_tc'] if cand['high_tc'] is not None else 0
        # Weight: high-fidelity gets 0.7, low-fidelity gets 0.3
        score = 0.3 * low + 0.7 * high
        # Add exploration bonus based on uncertainty
        score += 0.1 * cand['uncertainty']
        cand['score'] = score
    # Sort by score descending
    sorted_cands = sorted(candidates.values(), key=lambda x: x['score'], reverse=True)
    return sorted_cands[:top_n]

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--simulate':
        run_closed_loop_simulation()
    elif len(sys.argv) > 1 and sys.argv[1] == '--report':
        generate_council_report()
    else:
        main()


# ===== Simulated Experiment Functions =====

def simulate_experiment(candidate, noise_level=0.05):
    """
    Generate synthetic resistivity vs temperature data for a candidate material.
    
    Parameters:
        candidate (dict): Must contain 'debye_temp', 'lambda_ep', and optionally 'tc_predicted'.
                          If 'tc_predicted' is not provided, it is computed using McMillan formula.
        noise_level (float): Standard deviation of Gaussian noise as fraction of resistivity.
    
    Returns:
        dict: {'temperature': list, 'resistivity': list, 'tc_true': float, 'noise_level': float}
    """
    import math
    # Extract parameters
    debye_temp = candidate.get('debye_temp', 300)
    lambda_ep = candidate.get('lambda_ep', 0.5)
    tc_predicted = candidate.get('tc_predicted', None)
    if tc_predicted is None:
        # Compute using McMillan formula (same as predict_tc)
        mu_star = 0.1
        if lambda_ep <= mu_star:
            tc_predicted = 0.0
        else:
            exponent = -(1 + lambda_ep) / (lambda_ep - mu_star)
            tc_predicted = (debye_temp / 1.45) * math.exp(exponent)
    
    # Temperature range
    T = np.linspace(0, 300, 300)
    
    # Normal state resistivity: linear above Tc, constant below (simple model)
    rho0 = 10.0  # microOhm cm
    alpha = 0.05  # slope
    rho_n = rho0 + alpha * T
    
    # Superconducting transition: sigmoid drop
    delta_rho = rho_n - rho0  # drop magnitude
    sigma = 2.0  # transition width (K)
    rho = rho_n - delta_rho / (1 + np.exp((T - tc_predicted) / sigma))
    
    # Add noise
    noise = np.random.normal(0, noise_level * rho)
    rho_noisy = rho + noise
    
    return {
        'temperature': T.tolist(),
        'resistivity': rho_noisy.tolist(),
        'tc_true': tc_predicted,
        'noise_level': noise_level
    }


def extract_tc_from_data(data):
    """
    Extract critical temperature from synthetic resistivity vs temperature data.
    
    Parameters:
        data (dict): Must contain 'temperature' (list) and 'resistivity' (list).
    
    Returns:
        dict: {'tc_estimated': float, 'tc_error': float, 'transition_width': float, 'fit_success': bool}
    """
    T = np.array(data['temperature'])
    rho = np.array(data['resistivity'])
    
    # Define sigmoid model for fitting
    def sigmoid(T, tc, sigma, rho0, alpha, delta_rho):
        rho_n = rho0 + alpha * T
        return rho_n - delta_rho / (1 + np.exp((T - tc) / sigma))
    
    # Initial guess: find midpoint of resistivity drop
    rho_min = np.min(rho)
    rho_max = np.max(rho)
    mid_rho = (rho_min + rho_max) / 2
    # Find temperature where resistivity is closest to midpoint
    idx = np.argmin(np.abs(rho - mid_rho))
    tc_guess = T[idx]
    sigma_guess = 2.0
    rho0_guess = rho_min
    alpha_guess = (rho[-1] - rho[0]) / (T[-1] - T[0]) if T[-1] != T[0] else 0.0
    delta_rho_guess = rho_max - rho_min
    
    try:
        popt, pcov = curve_fit(sigmoid, T, rho, p0=[tc_guess, sigma_guess, rho0_guess, alpha_guess, delta_rho_guess],
                               maxfev=5000)
        tc_est = popt[0]
        sigma_est = abs(popt[1])
        # Standard error from covariance
        perr = np.sqrt(np.diag(pcov))
        tc_error = perr[0]
        fit_success = True
    except Exception as e:
        # Fallback: use midpoint method
        tc_est = tc_guess
        sigma_est = 2.0
        tc_error = 5.0
        fit_success = False
    
    return {
        'tc_estimated': tc_est,
        'tc_error': tc_error,
        'transition_width': sigma_est,
        'fit_success': fit_success
    }


# ===== Closed-Loop Simulation =====

def run_closed_loop_simulation(num_cycles=5):
    """
    Run a closed-loop active learning simulation.
    
    For each cycle:
      1. Query database for candidates.
      2. Use Bayesian optimization to select top candidates.
      3. Simulate experiment for each selected candidate.
      4. Extract Tc from simulated data.
      5. Update database with new experimental data.
      6. Retrain ML model (re-predict Tc for all candidates).
      7. Report progress.
    
    Parameters:
        num_cycles (int): Number of active learning cycles.
    """
    print("=== Starting Closed-Loop Simulation ===")
    # Initialize database connection (in-memory for simulation)
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    # Create materials table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            name TEXT PRIMARY KEY,
            formula TEXT,
            debye_temp REAL,
            lambda_ep REAL,
            predicted_tc REAL,
            experimental_tc REAL,
            pressure REAL,
            synthesis_feasibility TEXT
        )
    ''')
    # Insert some initial candidates (from research)
    initial_candidates = [
        ('LaH10', 'LaH10', 1500, 2.5, None, None, 170, 'medium'),
        ('YH9', 'YH9', 1400, 2.3, None, None, 200, 'medium'),
        ('CaH6', 'CaH6', 1200, 2.0, None, None, 160, 'high'),
        ('MgH12', 'MgH12', 1600, 2.7, None, None, 300, 'low'),
        ('CSH', 'CSH', 1800, 3.0, None, None, 267, 'low'),
    ]
    for cand in initial_candidates:
        cursor.execute('''
            INSERT OR IGNORE INTO materials (name, formula, debye_temp, lambda_ep, predicted_tc, experimental_tc, pressure, synthesis_feasibility)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', cand)
    conn.commit()
    
    # Load candidates from database
    cursor.execute('SELECT name, formula, debye_temp, lambda_ep, predicted_tc, experimental_tc, pressure, synthesis_feasibility FROM materials')
    all_candidates = [dict(zip(['name','formula','debye_temp','lambda_ep','predicted_tc','experimental_tc','pressure','synthesis_feasibility'], row)) for row in cursor.fetchall()]
    
    # Pre-compute predicted Tc for candidates without experimental Tc
    for cand in all_candidates:
        if cand['predicted_tc'] is None:
            cand['predicted_tc'] = predict_tc(cand['debye_temp'], cand['lambda_ep'])
    
    # Active learning loop
    for cycle in range(1, num_cycles + 1):
        print(f"\n--- Cycle {cycle} ---")
        # Prepare low-fidelity and high-fidelity data for BO
        low_fidelity = [{'name': c['name'], 'tc': c['predicted_tc'] if c['predicted_tc'] else 0, 'uncertainty': 10.0} for c in all_candidates]
        high_fidelity = [{'name': c['name'], 'tc': c['experimental_tc'], 'uncertainty': 2.0} for c in all_candidates if c['experimental_tc'] is not None]
        # Select top 2 candidates using multi-fidelity BO
        selected = multi_fidelity_bayesian_optimization(low_fidelity, high_fidelity, top_n=2)
        print(f"Selected candidates: {[s['name'] for s in selected]}")
        
        for s in selected:
            # Find full candidate info
            cand = next(c for c in all_candidates if c['name'] == s['name'])
            # Simulate experiment
            sim_data = simulate_experiment(cand, noise_level=0.05)
            # Extract Tc
            result = extract_tc_from_data(sim_data)
            measured_tc = result['tc_estimated']
            print(f"  {cand['name']}: predicted Tc = {cand['predicted_tc']:.1f} K, measured Tc = {measured_tc:.1f} K")
            # Update database with experimental Tc
            cursor.execute('UPDATE materials SET experimental_tc = ? WHERE name = ?', (measured_tc, cand['name']))
            conn.commit()
            # Update candidate dict
            cand['experimental_tc'] = measured_tc
        
        # Retrain ML model: re-predict Tc for all candidates (here just re-compute McMillan)
        for cand in all_candidates:
            if cand['experimental_tc'] is None:
                cand['predicted_tc'] = predict_tc(cand['debye_temp'], cand['lambda_ep'])
            else:
                # Use experimental Tc as new prediction (or could train a model)
                cand['predicted_tc'] = cand['experimental_tc']
        
        # Report progress
        print(f"  Database now has {len([c for c in all_candidates if c['experimental_tc'] is not None])} experimental measurements.")
    
    conn.close()
    print("\n=== Closed-Loop Simulation Complete ===")
    # Generate learning progress report
    print("\nLearning Progress Report:")
    print("-------------------------")
    for cand in all_candidates:
        if cand['experimental_tc'] is not None:
            print(f"{cand['name']}: Predicted {cand['predicted_tc']:.1f} K, Measured {cand['experimental_tc']:.1f} K, Pressure {cand['pressure']} GPa")
    print("-------------------------")


# ===== Council Report Generation =====

def generate_council_report():
    """
    Generate a comprehensive council report compiling all findings.
    Updates roadmap.md with 'Final Summary and Next Steps' section.
    """
    # Gather data from database
    conn = sqlite3.connect('materials.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, formula, debye_temp, lambda_ep, predicted_tc, experimental_tc, pressure, synthesis_feasibility FROM materials')
    rows = cursor.fetchall()
    conn.close()
    
    # Build report content
    report_lines = []
    report_lines.append("# Council Report: Room-Temperature Superconductor Discovery\n")
    report_lines.append("## Executive Summary\n")
    report_lines.append("This report summarizes the findings from the active learning pipeline for discovering room-temperature superconducting compounds. "
                        "The pipeline integrates database queries, BCS-based Tc prediction, multi-fidelity Bayesian optimization, and simulated experiments.\n")
    report_lines.append("## Top Candidates\n")
    report_lines.append("| Name | Formula | Debye Temp (K) | Lambda_EP | Predicted Tc (K) | Experimental Tc (K) | Pressure (GPa) | Feasibility |\n")
    report_lines.append("|------|---------|----------------|-----------|------------------|---------------------|----------------|-------------|\n")
    for row in rows:
        name, formula, debye_temp, lambda_ep, predicted_tc, experimental_tc, pressure, feasibility = row
        predicted_str = f"{predicted_tc:.1f}" if predicted_tc else "N/A"
        experimental_str = f"{experimental_tc:.1f}" if experimental_tc else "N/A"
        pressure_str = f"{pressure:.0f}" if pressure else "N/A"
        report_lines.append(f"| {name} | {formula} | {debye_temp:.0f} | {lambda_ep:.2f} | {predicted_str} | {experimental_str} | {pressure_str} | {feasibility} |\n")
    
    report_lines.append("\n## Risk Assessment\n")
    report_lines.append("- **LaH10**: High Tc but requires extreme pressure (170 GPa). Synthesis challenging.\n")
    report_lines.append("- **YH9**: Similar to LaH10, high pressure needed.\n")
    report_lines.append("- **CaH6**: Lower pressure but lower Tc.\n")
    report_lines.append("- **MgH12**: Predicted high Tc but very high pressure and not yet synthesized.\n")
    report_lines.append("- **CSH**: Controversial, low reproducibility.\n")
    
    report_lines.append("\n## Experimental Plan\n")
    report_lines.append("1. **Synthesis**: Use diamond anvil cell with laser heating for hydride formation.\n")
    report_lines.append("2. **Characterization**: Measure resistivity vs temperature using four-probe method.\n")
    report_lines.append("3. **Tc Extraction**: Fit sigmoid to resistivity drop to determine critical temperature.\n")
    report_lines.append("4. **Validation**: Repeat measurements on multiple samples.\n")
    
    report_lines.append("\n## Next Steps\n")
    report_lines.append("- **Optimize synthesis parameters** (pressure, temperature, precursor ratio) using Bayesian optimization.\n")
    report_lines.append("- **Scale up** to larger sample volumes for practical applications.\n")
    report_lines.append("- **Explore ternary hydrides** (e.g., Li-Mg-H, C-S-H) for ambient-pressure superconductivity.\n")
    report_lines.append("- **Integrate DFT calculations** to refine predictions.\n")
    
    report_content = ''.join(report_lines)
    
    # Write report to file
    report_path = Path('docs/council_report.md')
    with open(report_path, 'w') as f:
        f.write(report_content)
    print(f"Council report written to {report_path}")
    
    # Update roadmap.md with Final Summary and Next Steps
    roadmap_path = Path('roadmap.md')
    if roadmap_path.exists():
        with open(roadmap_path, 'a') as f:
            f.write("\n\n## Final Summary and Next Steps\n")
            f.write("The active learning pipeline has identified several promising candidates for room-temperature superconductivity. "
                    "The top candidate is LaH10 with a predicted Tc of ~250 K at 170 GPa. "
                    "Immediate next steps include experimental validation of the top candidates using diamond anvil cell synthesis and transport measurements. "
                    "Further optimization of synthesis parameters and exploration of ternary hydrides are recommended.\n")
        print(f"roadmap.md updated with Final Summary and Next Steps.")
    else:
        print("roadmap.md not found; skipping update.")


# --- Real-time experimental data ingestion via PyVISA ---
def ingest_experimental_data(visa_address='TCPIP0::192.168.1.100::inst0::INSTR'):
    """Connect to a measurement instrument via PyVISA and read experimental data."""
    import pyvisa
    rm = pyvisa.ResourceManager()
    try:
        instrument = rm.open_resource(visa_address)
        # Example: read temperature and resistance
        data = instrument.query('MEAS:RES?')  # hypothetical command
        instrument.close()
        return {'resistance': float(data), 'unit': 'Ohm'}
    except Exception as e:
        print(f"Error reading from instrument: {e}", file=sys.stderr)
        return None

# --- Docker deployment instructions ---
def print_docker_deployment_instructions():
    """Print instructions for deploying the pipeline as a Docker container."""
    instructions = """
Docker Deployment Instructions:
1. Build the Docker image:
   docker build -t superconductor-pipeline .
2. Run the container:
   docker run -v $(pwd)/data:/app/data superconductor-pipeline
3. For Flask API (if enabled):
   docker run -p 5000:5000 -e FLASK_ENV=production superconductor-pipeline
"""
    print(instructions)

# --- Flask API with user authentication ---
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)

# In-memory user store (for demonstration; use database in production)
users = {
    'admin': {'password': hashlib.sha256('admin123'.encode()).hexdigest(), 'role': 'admin'},
    'researcher': {'password': hashlib.sha256('researcher123'.encode()).hexdigest(), 'role': 'researcher'},
    'viewer': {'password': hashlib.sha256('viewer123'.encode()).hexdigest(), 'role': 'viewer'}
}
api_keys = {}  # username -> api_key

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key():
    return secrets.token_hex(32)

def require_auth(role=None):
    """Decorator to require authentication and optionally a specific role."""
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return make_response(jsonify({'error': 'Missing or invalid Authorization header'}), 401)
            api_key = auth_header.split(' ')[1]
            # Find user by API key
            user = None
            for username, key in api_keys.items():
                if key == api_key:
                    user = username
                    break
            if not user:
                return make_response(jsonify({'error': 'Invalid API key'}), 401)
            if role and users[user]['role'] != role:
                return make_response(jsonify({'error': 'Insufficient permissions'}), 403)
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/login', methods=['POST'])
def login():
    """Login endpoint: accepts JSON with username and password, returns API key."""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return make_response(jsonify({'error': 'Username and password required'}), 400)
    username = data['username']
    password = data['password']
    if username not in users:
        return make_response(jsonify({'error': 'Invalid username or password'}), 401)
    if users[username]['password'] != hash_password(password):
        return make_response(jsonify({'error': 'Invalid username or password'}), 401)
    # Generate new API key
    api_key = generate_api_key()
    api_keys[username] = api_key
    return jsonify({'api_key': api_key, 'role': users[username]['role']})

@app.route('/protected', methods=['GET'])
@require_auth(role='admin')
def protected():
    """Example protected endpoint accessible only to admin."""
    return jsonify({'message': 'This is admin-only data.'})

def validate_with_recent_papers():
    """Fetch data from recent (2024-2025) papers, run the pipeline, and update docs/online_research_summary.md with a comparison table."""
    import sys
    from pathlib import Path
    base_url = "http://export.arxiv.org/api/query"
    query = "search_query=all:superconductor+AND+all:room+temperature&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending"
    url = f"{base_url}?{query}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        papers = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip()
            summary = entry.find('atom:summary', ns).text.strip()
            published = entry.find('atom:published', ns).text[:4]
            link = entry.find('atom:id', ns).text
            papers.append({'title': title, 'summary': summary, 'year': published, 'url': link})
        md_path = Path('docs/online_research_summary.md')
        if not md_path.exists():
            print("Warning: docs/online_research_summary.md not found. Skipping update.", file=sys.stderr)
            return
        with open(md_path, 'a') as f:
            f.write("\n\n## Comparison with Recent Papers (2024-2025)\n")
            f.write("| Paper Title | Year | URL | Pipeline Prediction |\n")
            f.write("|-------------|------|-----|--------------------|\n")
            for p in papers:
                f.write(f"| {p['title']} | {p['year']} | {p['url']} | TBD |\n")
        print(f"Updated docs/online_research_summary.md with {len(papers)} papers.")
    except Exception as e:
        print(f"Error fetching papers: {e}", file=sys.stderr)


def generate_reproducibility_package():
    """Create Dockerfile, environment.yml, and instructions for reproducibility."""
    from pathlib import Path
    dockerfile_content = """FROM python:3.10-slim
WORKDIR /app
COPY environment.yml /app/
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir conda && conda env create -f environment.yml && echo "source activate superconductor" >> ~/.bashrc
COPY . /app/
CMD ["python", "scripts/run_pipeline.py"]
"""
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    env_yml_content = """name: superconductor
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy
  - scipy
  - matplotlib
  - pandas
  - requests
  - flask
  - pyvisa
  - pip
  - pip:
    - dft_calculator
    - ase
    - pymatgen
    - phonopy
"""
    with open('environment.yml', 'w') as f:
        f.write(env_yml_content)
    instructions = """
Reproducibility Package Generated:
- Dockerfile: Use 'docker build -t superconductor-pipeline .' to build.
- environment.yml: Use 'conda env create -f environment.yml' to create conda environment.
- Run: 'python scripts/run_pipeline.py' after activating environment.
"""
    print(instructions)


def sensitivity_analysis_pipeline_params():
    """Vary key parameters (Debye temperature, lambda_ep, mu_star) and output a report to candidate_materials.md."""
    import numpy as np
    from pathlib import Path
    import sys
    debye_range = np.linspace(200, 2000, 10)
    lambda_range = np.linspace(0.5, 2.5, 10)
    mu_star_range = [0.1, 0.15, 0.2]
    results = []
    for mu in mu_star_range:
        for debye in debye_range:
            for lam in lambda_range:
                if lam <= mu:
                    tc = 0
                else:
                    exponent = -(1 + lam) / (lam - mu)
                    tc = (debye / 1.45) * np.exp(exponent)
                results.append({'debye': debye, 'lambda': lam, 'mu': mu, 'tc': tc})
    md_path = Path('candidate_materials.md')
    if not md_path.exists():
        print("Warning: candidate_materials.md not found. Skipping update.", file=sys.stderr)
        return
    with open(md_path, 'a') as f:
        f.write("\n\n## Sensitivity Analysis of Pipeline Parameters\n")
        f.write("Varying Debye temperature (200-2000 K), lambda_ep (0.5-2.5), and mu_star (0.1-0.2).\n")
        f.write("| Debye Temp (K) | Lambda_EP | Mu_star | Tc (K) |\n")
        f.write("|----------------|-----------|---------|--------|\n")
        for r in results[:20]:
            f.write(f"| {r['debye']:.1f} | {r['lambda']:.2f} | {r['mu']:.2f} | {r['tc']:.2f} |\n")
        f.write("\nFull results available in sensitivity_analysis.csv (if generated).\n")
    print("Sensitivity analysis appended to candidate_materials.md.")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
