#!/usr/bin/env python3
"""Compatibility CLI for candidate-database queries."""

from __future__ import annotations

import argparse
import json

from superconductors.config import Settings
from superconductors.query import QueryFilters, high_throughput_screening, load_database, query

DATABASE_PATH = str(Settings.from_env().database_path)

__all__ = [
    "DATABASE_PATH",
    "QueryFilters",
    "high_throughput_screening",
    "load_database",
    "query",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query the candidate database")
    parser.add_argument("--name")
    parser.add_argument("--tc-min", type=float)
    parser.add_argument("--tc-max", type=float)
    parser.add_argument("--pressure-min", type=float)
    parser.add_argument("--pressure-max", type=float)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    records = query(
        load_database(),
        QueryFilters(
            name=args.name,
            tc_min=args.tc_min,
            tc_max=args.tc_max,
            pressure_min=args.pressure_min,
            pressure_max=args.pressure_max,
        ),
    )[: max(0, args.limit)]
    if args.json:
        print(json.dumps(records, indent=2))
    else:
        for record in records:
            print(
                f"{record.get('name', record.get('formula', '')):<24} "
                f"Tc={record.get('Tc', 'unknown')} K  P={record.get('pressure', 'unknown')} GPa"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
