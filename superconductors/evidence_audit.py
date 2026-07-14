"""Build a deterministic, read-only queue for manual evidence review."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from typing import Any, Literal

from .evidence import classify_evidence

AuditScope = Literal["all", "unclassified", "quarantined"]


@dataclass(frozen=True, slots=True)
class EvidenceAuditItem:
    record_index: int
    material: str
    tc: float | None
    pressure: float | None
    reference: str | None
    doi: str | None
    evidence_type: str
    verification_status: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EvidenceAudit:
    records_checked: int
    counts: dict[str, int]
    scope: AuditScope
    items: tuple[EvidenceAuditItem, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "records_checked": self.records_checked,
            "counts": self.counts,
            "scope": self.scope,
            "items": [item.to_dict() for item in self.items],
        }


def build_evidence_audit(
    records: Iterable[Mapping[str, Any]],
    *,
    scope: AuditScope = "unclassified",
    limit: int | None = None,
) -> EvidenceAudit:
    """Return review items without changing or reclassifying source records."""
    if scope not in {"all", "unclassified", "quarantined"}:
        raise ValueError(f"Unsupported evidence audit scope: {scope}")
    if limit is not None and limit < 1:
        raise ValueError("Evidence audit limit must be positive")

    values = list(records)
    counts: Counter[str] = Counter()
    items: list[EvidenceAuditItem] = []
    for index, record in enumerate(values):
        evidence = classify_evidence(record)
        counts[evidence.evidence_type] += 1
        if scope == "unclassified" and evidence.evidence_type != "unclassified":
            continue
        if scope == "quarantined" and evidence.eligible_for_screening:
            continue
        items.append(
            EvidenceAuditItem(
                record_index=index,
                material=str(record.get("name") or record.get("formula") or "").strip(),
                tc=_number(record.get("Tc", record.get("tc"))),
                pressure=_number(record.get("pressure")),
                reference=_text(record.get("reference")),
                doi=_text(record.get("doi")),
                evidence_type=evidence.evidence_type,
                verification_status=evidence.verification_status,
                reason=evidence.reason,
            )
        )

    # Review the most consequential high-Tc, low-pressure claims first while
    # retaining the original index as a stable tie-breaker.
    items.sort(
        key=lambda item: (
            -(item.tc if item.tc is not None else float("-inf")),
            item.pressure if item.pressure is not None else float("inf"),
            item.record_index,
        )
    )
    if limit is not None:
        items = items[:limit]
    return EvidenceAudit(len(values), dict(sorted(counts.items())), scope, tuple(items))


def _number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None
