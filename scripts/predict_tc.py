#!/usr/bin/env python3
"""Compatibility CLI for lightweight Tc screening estimates."""

from __future__ import annotations

import argparse

from superconductors.prediction import (
    Prediction,
    allen_dynes_tc,
    average_debye,
    average_valence,
    eliashberg_tc,
    mcmillan_tc,
    parse_formula,
    predict,
    predict_tc,
    predict_tc_with_uncertainty,
)

__all__ = [
    "Prediction",
    "allen_dynes_tc",
    "average_debye",
    "average_valence",
    "eliashberg_tc",
    "mcmillan_tc",
    "parse_formula",
    "predict",
    "predict_tc",
    "predict_tc_with_uncertainty",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Estimate Tc with a transparent Allen-Dynes screening heuristic"
    )
    parser.add_argument("formulas", nargs="+", help="Chemical formulas such as H3S or LaH10")
    args = parser.parse_args(argv)
    for formula in args.formulas:
        result = predict(formula)
        print(
            f"{result.formula}: {result.tc:.2f} K +/- {result.uncertainty:.2f} K ({result.method})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
