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

if __name__ == "__main__":
    main()
