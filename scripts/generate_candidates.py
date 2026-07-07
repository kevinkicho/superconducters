#!/usr/bin/env python3
"""
Candidate generation script for room-temperature superconductors.
Reads theoretical framework and chemistry/physics docs, then generates candidate
compositions (hydrides, oxides, etc.) and passes them to predict_tc.py.
"""

import os
import re
import subprocess
import sys

# Paths to the theoretical and chemistry/physics documents
DOCS_DIR = "docs"
THEORY_FILE = os.path.join(DOCS_DIR, "theoretical_framework.md")
CHEM_PHYS_FILE = os.path.join(DOCS_DIR, "proposed_chemistry_physics.md")

# Path to the prediction script
PREDICT_SCRIPT = "predict_tc.py"


def extract_candidates_from_text(text):
    """
    Extract candidate chemical formulas from text.
    Looks for patterns like LaH10, H3S, YH6, etc.
    Also looks for lines starting with '- ' or '* ' that contain chemical formulas.
    """
    candidates = set()
    # Pattern for common hydride/oxide formulas: e.g., LaH10, H3S, YH6, MgB2, etc.
    formula_pattern = r'\b([A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)+)\b'
    for match in re.finditer(formula_pattern, text):
        formula = match.group(1)
        # Basic sanity: must contain at least one metal and hydrogen or oxygen
        if re.search(r'[A-Z][a-z]?', formula) and re.search(r'[HO]', formula):
            candidates.add(formula)
    # Also look for explicit list items
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('- ') or line.startswith('* '):
            # Remove bullet marker
            content = line[2:].strip()
            # If it looks like a formula, add it
            if re.match(r'^[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)+$', content):
                candidates.add(content)
    return list(candidates)


def main():
    # Read the documents
    if not os.path.exists(THEORY_FILE):
        print(f"Error: {THEORY_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(CHEM_PHYS_FILE):
        print(f"Error: {CHEM_PHYS_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    with open(THEORY_FILE, 'r') as f:
        theory_text = f.read()
    with open(CHEM_PHYS_FILE, 'r') as f:
        chem_phys_text = f.read()

    # Extract candidates from both documents
    candidates = set()
    candidates.update(extract_candidates_from_text(theory_text))
    candidates.update(extract_candidates_from_text(chem_phys_text))

    if not candidates:
        print("No candidates found in documents.", file=sys.stderr)
        sys.exit(0)

    print(f"Found {len(candidates)} candidate compositions.")
    for formula in sorted(candidates):
        print(f"  - {formula}")

    # Pass each candidate to predict_tc.py
    for formula in sorted(candidates):
        print(f"\nRunning predict_tc.py for {formula}...")
        result = subprocess.run(
            [sys.executable, PREDICT_SCRIPT, formula],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error running predict_tc.py for {formula}:", result.stderr)
        else:
            print(result.stdout)


if __name__ == "__main__":
    main()
