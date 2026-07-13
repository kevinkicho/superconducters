"""Command-line entry point for the supported pipeline."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load, filter, and rank superconductor candidates."
    )
    parser.add_argument("--min-tc", type=float, default=None, help="Minimum measured Tc in kelvin")
    parser.add_argument("--max-pressure", type=float, default=None, help="Maximum pressure in GPa")
    parser.add_argument("--limit", type=int, default=20, help="Maximum candidates to return")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_pipeline(
        min_tc=args.min_tc,
        max_pressure=args.max_pressure,
        limit=args.limit,
    )
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    print(f"Loaded {result.candidates_loaded} candidates; selected {result.candidates_selected}.")
    for index, candidate in enumerate(result.candidates, start=1):
        tc = f"{candidate.tc:g} K" if candidate.tc is not None else "unknown Tc"
        pressure = (
            f"{candidate.pressure:g} GPa" if candidate.pressure is not None else "unknown pressure"
        )
        print(f"{index:>2}. {candidate.formula:<20} {tc:<14} {pressure}")
    return 0
