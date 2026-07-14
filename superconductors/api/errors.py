"""Stable application-layer errors."""


class ApplicationDataError(RuntimeError):
    """Raised when configured application storage is unavailable or invalid."""


class DuplicateCandidateError(ValueError):
    """Raised when an identical app candidate already exists."""
