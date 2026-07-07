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
import dft_calculator  # for DFT validation

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

    # Step 5: DFT validation for top uncertain candidates
    print("=== Step 5: DFT validation for top uncertain candidates ===")
    TOP_N = 5
    # Compute uncertainty for each result
    for r in results:
        r['uncertainty'] = compute_uncertainty(r['debye_temp'], r['lambda_ep'])
    # Sort by uncertainty descending
    results.sort(key=lambda x: x['uncertainty'], reverse=True)
    top_candidates = results[:TOP_N]
    print(f"Selected top {TOP_N} candidates with highest uncertainty for DFT validation.")
    dft_results = []
    for cand in top_candidates:
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
    # Update candidate_materials.md with DFT results
    update_candidate_md_with_dft(dft_results)
    print("=== DFT validation complete ===")

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
