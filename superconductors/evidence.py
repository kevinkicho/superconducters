"""Evidence classification for mixed experimental and computational records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

EvidenceType = Literal["measured", "calculated", "claimed", "unclassified"]
VerificationStatus = Literal[
    "independent",
    "original-only",
    "disputed",
    "retracted",
    "unverified",
]

RETRACTED_DOIS = {
    "10.1038/s41586-020-2801-z",
    "10.1038/s41586-023-05742-0",
}
EVIDENCE_TYPES = {"measured", "calculated", "claimed", "unclassified"}
VERIFICATION_STATUSES = {
    "independent",
    "original-only",
    "disputed",
    "retracted",
    "unverified",
}


@dataclass(frozen=True, slots=True)
class EvidenceClassification:
    evidence_type: EvidenceType
    verification_status: VerificationStatus
    reason: str

    @property
    def eligible_for_screening(self) -> bool:
        return self.verification_status not in {"disputed", "retracted"}


def classify_evidence(record: Mapping[str, Any]) -> EvidenceClassification:
    explicit_type = record.get("evidence_type")
    explicit_status = record.get("verification_status")
    if explicit_type in EVIDENCE_TYPES and explicit_status in VERIFICATION_STATUSES:
        return EvidenceClassification(
            explicit_type,  # type: ignore[arg-type]
            explicit_status,  # type: ignore[arg-type]
            "explicit record classification",
        )

    doi = str(record.get("doi") or "").strip().lower()
    if doi in RETRACTED_DOIS:
        return EvidenceClassification("claimed", "retracted", f"retracted DOI: {doi}")

    external_database = record.get("external_database")
    prediction_method = (
        external_database.get("prediction_method")
        if isinstance(external_database, Mapping)
        else None
    )
    context = " ".join(
        str(record.get(field) or "")
        for field in (
            "structure",
            "reference",
            "synthesis_method",
            "synthesis_parameters",
            "measurement_method",
            "composition_uncertainty",
        )
    ).casefold()
    if "retract" in context:
        return EvidenceClassification("claimed", "retracted", "record text marks retraction")
    if any(token in context for token in ("controversial", "claimed", "not widely replicated")):
        return EvidenceClassification("claimed", "disputed", "record text marks disputed claim")
    measurement_method = str(record.get("measurement_method") or "").strip().casefold()
    computational_tokens = (
        "predicted",
        "prediction",
        "eliashberg",
        "calculated",
        "computational",
        "simulation",
        "theoretical",
        "density functional",
        "dft",
    )
    if measurement_method and not any(
        token in measurement_method for token in computational_tokens
    ):
        return EvidenceClassification("measured", "original-only", "measurement method supplied")
    if prediction_method or any(token in context for token in computational_tokens):
        return EvidenceClassification("calculated", "unverified", "computational record metadata")
    if record.get("reference") or record.get("references"):
        return EvidenceClassification(
            "unclassified",
            "original-only",
            "citation supplied without measurement or calculation metadata",
        )
    return EvidenceClassification("unclassified", "unverified", "insufficient evidence metadata")
