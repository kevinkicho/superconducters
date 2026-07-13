"""Compatibility exports for external data adapters."""

from superconductors.integrations import (
    IntegrationError,
    fetch_icsd,
    fetch_materials_project,
    search_arxiv,
)

fetch_arxiv = search_arxiv

__all__ = [
    "IntegrationError",
    "fetch_arxiv",
    "fetch_icsd",
    "fetch_materials_project",
]
