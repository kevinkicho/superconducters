"""Compatibility entry point for ``uvicorn app:app``."""

from superconductors.api import create_app

app = create_app()

__all__ = ["app", "create_app"]
