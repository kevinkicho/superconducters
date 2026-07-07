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

if __name__ == "__main__":
    main()
