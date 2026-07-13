#!/usr/bin/env python3
"""Compatibility CLI for compact Markdown changelog generation."""

from __future__ import annotations

import argparse

from superconductors.changelog import (
    Commit,
    parse_git_log,
    read_commits,
    render_changelog,
    write_changelog,
)

__all__ = ["Commit", "parse_git_log", "read_commits", "render_changelog", "write_changelog"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a compact changelog from Git history")
    parser.add_argument("--output", default="output/changelog.md")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args(argv)
    print(write_changelog(args.output, limit=args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
