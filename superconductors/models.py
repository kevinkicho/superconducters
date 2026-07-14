"""Domain models shared by the CLI, API, and services."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from .evidence import EvidenceType, VerificationStatus, classify_evidence


@dataclass(frozen=True, slots=True)
class Candidate:
    formula: str
    tc: float | None = None
    pressure: float | None = None
    structure: str | None = None
    source: str = "database"
    evidence_type: EvidenceType = "unclassified"
    verification_status: VerificationStatus = "unverified"

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> Candidate:
        formula = value.get("formula") or value.get("name") or value.get("composition") or ""
        evidence = classify_evidence(value)
        return cls(
            formula=str(formula),
            tc=_optional_float(value.get("tc", value.get("Tc", value.get("temperature")))),
            pressure=_optional_float(value.get("pressure")),
            structure=value.get("structure"),
            source=str(value.get("source") or "database"),
            evidence_type=evidence.evidence_type,
            verification_status=evidence.verification_status,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
