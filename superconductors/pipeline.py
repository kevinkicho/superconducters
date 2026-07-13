"""Small, deterministic orchestration service for candidate screening."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .config import Settings
from .models import Candidate
from .repository import CandidateRepository


@dataclass(frozen=True, slots=True)
class PipelineResult:
    candidates_loaded: int
    candidates_selected: int
    candidates: tuple[Candidate, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "candidates_loaded": self.candidates_loaded,
            "candidates_selected": self.candidates_selected,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
        }


def screen_candidates(
    candidates: Iterable[Candidate],
    *,
    min_tc: float | None = None,
    max_pressure: float | None = None,
    limit: int = 20,
) -> list[Candidate]:
    selected = [
        candidate
        for candidate in candidates
        if (min_tc is None or (candidate.tc is not None and candidate.tc >= min_tc))
        and (
            max_pressure is None
            or (candidate.pressure is not None and candidate.pressure <= max_pressure)
        )
    ]

    def tc_sort_key(candidate: Candidate) -> float:
        return candidate.tc if candidate.tc is not None else float("-inf")

    selected.sort(
        key=tc_sort_key,
        reverse=True,
    )
    return selected[: max(0, limit)]


def run_pipeline(
    *,
    settings: Settings | None = None,
    repository: CandidateRepository | None = None,
    min_tc: float | None = None,
    max_pressure: float | None = None,
    limit: int = 20,
) -> PipelineResult:
    settings = settings or Settings.from_env()
    repository = repository or CandidateRepository(settings.database_path)
    candidates = repository.list()
    selected = screen_candidates(
        candidates,
        min_tc=min_tc,
        max_pressure=max_pressure,
        limit=limit,
    )
    return PipelineResult(len(candidates), len(selected), tuple(selected))
