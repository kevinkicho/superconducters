#!/usr/bin/env python3
"""Compatibility entry point for the canonical pipeline CLI.

Application code lives in :mod:`superconductors`; this file remains so existing
commands such as ``python run_pipeline.py`` continue to work.
"""

from superconductors.cli import main
from superconductors.pipeline import PipelineResult, run_pipeline, screen_candidates

__all__ = ["PipelineResult", "main", "run_pipeline", "screen_candidates"]


if __name__ == "__main__":
    raise SystemExit(main())
