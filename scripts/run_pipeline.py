#!/usr/bin/env python3
"""Deprecated wrapper for the canonical pipeline command.

Use ``python run_pipeline.py`` or the installed ``superconductors`` command.
"""

from superconductors.cli import main
from superconductors.pipeline import PipelineResult, run_pipeline, screen_candidates

__all__ = ["PipelineResult", "main", "run_pipeline", "screen_candidates"]


if __name__ == "__main__":
    raise SystemExit(main())
