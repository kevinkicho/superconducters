"""Measurable discovery objectives and transparent Pareto screening."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .models import Candidate


@dataclass(frozen=True, slots=True)
class DiscoveryObjective:
    name: str = "ambient-pressure room-temperature superconductivity"
    minimum_tc_k: float = 273.15
    maximum_operating_pressure_gpa: float = 1.0
    require_measured: bool = True
    require_independent_verification: bool = True

    def evaluate(self, candidate: Candidate) -> ObjectiveEvaluation:
        gates = {
            "temperature": candidate.tc is not None and candidate.tc >= self.minimum_tc_k,
            "pressure": candidate.pressure is not None
            and candidate.pressure <= self.maximum_operating_pressure_gpa,
            "evidence": not self.require_measured or candidate.evidence_type == "measured",
            "verification": not self.require_independent_verification
            or candidate.verification_status == "independent",
        }
        return ObjectiveEvaluation(candidate.formula, gates)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ObjectiveEvaluation:
    formula: str
    gates: dict[str, bool]

    @property
    def meets_objective(self) -> bool:
        return all(self.gates.values())

    def to_dict(self) -> dict[str, object]:
        return {
            "formula": self.formula,
            "meets_objective": self.meets_objective,
            "gates": dict(self.gates),
        }


def pareto_front(candidates: list[Candidate]) -> list[Candidate]:
    """Return candidates not dominated on higher Tc and lower pressure."""
    eligible = [
        candidate
        for candidate in candidates
        if candidate.tc is not None
        and candidate.pressure is not None
        and candidate.verification_status not in {"disputed", "retracted"}
    ]
    return [
        candidate
        for candidate in eligible
        if not any(_dominates(other, candidate) for other in eligible if other is not candidate)
    ]


def _dominates(left: Candidate, right: Candidate) -> bool:
    assert left.tc is not None and left.pressure is not None
    assert right.tc is not None and right.pressure is not None
    no_worse = left.tc >= right.tc and left.pressure <= right.pressure
    strictly_better = left.tc > right.tc or left.pressure < right.pressure
    return no_worse and strictly_better
