#!/usr/bin/env python3
"""Compatibility CLI for the arXiv literature adapter."""

from __future__ import annotations

import argparse
import json

from superconductors.integrations import (
    IntegrationError,
    fetch_paper_details,
    parse_arxiv_feed,
    search_arxiv,
)

__all__ = ["IntegrationError", "fetch_paper_details", "parse_arxiv_feed", "search_arxiv"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search arXiv literature")
    parser.add_argument("query")
    parser.add_argument("--max-results", type=int, default=10)
    args = parser.parse_args(argv)
    print(json.dumps(search_arxiv(args.query, max_results=args.max_results), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
