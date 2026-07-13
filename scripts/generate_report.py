#!/usr/bin/env python3
"""Compatibility CLI for candidate screening reports."""

from __future__ import annotations

import argparse

from superconductors.pipeline import run_pipeline
from superconductors.reporting import (
    format_candidate_table,
    generate_report,
    write_markdown,
    write_pdf,
)

__all__ = ["format_candidate_table", "generate_report", "write_markdown", "write_pdf"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a candidate screening report")
    parser.add_argument("--output", default="output/candidate_report.md")
    parser.add_argument("--min-tc", type=float)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    result = run_pipeline(min_tc=args.min_tc, limit=args.limit)
    report = generate_report(candidate.to_dict() for candidate in result.candidates)
    if args.output.lower().endswith(".pdf"):
        path = write_pdf(report, args.output)
    else:
        path = write_markdown(report, args.output)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
