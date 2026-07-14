"""Compatibility wrapper for candidate screening announcements."""

from __future__ import annotations

from superconductors.announcements import generate_candidate_announcement
from superconductors.pipeline import run_pipeline


def generate_discovery_announcement(candidates=None, predictions=None):
    """Return a provenance-aware screening update under the historical name."""
    if candidates is None:
        candidates = run_pipeline(limit=5).candidates
    return generate_candidate_announcement(candidates, predictions=predictions)


__all__ = ["generate_candidate_announcement", "generate_discovery_announcement"]
