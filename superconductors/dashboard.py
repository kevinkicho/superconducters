"""Pure view-model helpers for the Streamlit dashboard."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Candidate
from .pipeline import PipelineResult, run_pipeline
from .prediction import Prediction, predict
from .repository import CandidateRepository


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    result: PipelineResult
    measured: tuple[Candidate, ...]
    near_ambient: tuple[Candidate, ...]

    @property
    def rows(self) -> list[dict[str, object]]:
        return [candidate.to_dict() for candidate in self.result.candidates]


def build_snapshot(
    repository: CandidateRepository,
    *,
    min_tc: float | None = None,
    max_pressure: float | None = None,
    limit: int = 20,
) -> DashboardSnapshot:
    result = run_pipeline(
        repository=repository,
        min_tc=min_tc,
        max_pressure=max_pressure,
        limit=limit,
    )
    measured = tuple(candidate for candidate in result.candidates if candidate.tc is not None)
    ambient = tuple(
        candidate
        for candidate in result.candidates
        if candidate.pressure is not None and candidate.pressure <= 1
    )
    return DashboardSnapshot(result, measured, ambient)


def estimate_formula(formula: str) -> Prediction:
    return predict(formula.strip())
