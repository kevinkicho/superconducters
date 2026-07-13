#!/usr/bin/env python3
"""Compatibility CLI for curated candidate hypotheses."""

from __future__ import annotations

import argparse
import json

from superconductors.generation import filter_candidates, generate_candidates, rank_candidates

__all__ = ["filter_candidates", "generate_candidates", "rank_candidates"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate curated candidate hypotheses")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--min-tc", type=float)
    parser.add_argument("--max-pressure", type=float)
    args = parser.parse_args(argv)
    candidates = generate_candidates(args.limit)
    candidates = filter_candidates(
        candidates,
        min_tc=args.min_tc,
        max_pressure=args.max_pressure,
    )
    print(json.dumps(rank_candidates(candidates), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
