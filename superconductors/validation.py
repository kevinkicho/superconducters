"""Non-destructive validation for candidate database records."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from typing import Any, Literal

from .evidence import classify_evidence


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    severity: Literal["error", "warning"]
    code: str
    message: str
    record_index: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    records_checked: int
    issues: tuple[ValidationIssue, ...]

    @property
    def errors(self) -> int:
        return sum(issue.severity == "error" for issue in self.issues)

    @property
    def warnings(self) -> int:
        return sum(issue.severity == "warning" for issue in self.issues)

    @property
    def is_valid(self) -> bool:
        return self.errors == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "records_checked": self.records_checked,
            "errors": self.errors,
            "warnings": self.warnings,
            "is_valid": self.is_valid,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def validate_records(records: Iterable[Mapping[str, Any]]) -> ValidationReport:
    values = list(records)
    issues: list[ValidationIssue] = []
    normalized_names = Counter(
        str(record.get("name") or record.get("formula") or "").strip().casefold()
        for record in values
    )
    for index, record in enumerate(values):
        name = str(record.get("name") or record.get("formula") or "").strip()
        if not name:
            issues.append(_issue("error", "missing-name", "Missing material name", index))
        elif normalized_names[name.casefold()] > 1:
            issues.append(
                _issue("error", "duplicate-name", f"Duplicate material name: {name}", index)
            )

        _validate_number(record, "Tc", index, issues, minimum=0)
        _validate_number(record, "pressure", index, issues, minimum=0)
        for field in ("structure", "reference"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                issues.append(
                    _issue("warning", f"missing-{field}", f"Missing {field} metadata", index)
                )
        if not record.get("source"):
            issues.append(
                _issue(
                    "warning",
                    "implicit-provenance",
                    "No explicit source classification; reference is retained as provenance",
                    index,
                )
            )
        evidence = classify_evidence(record)
        if evidence.evidence_type == "unclassified":
            issues.append(
                _issue(
                    "warning",
                    "evidence-unclassified",
                    f"Evidence type requires manual classification: {evidence.reason}",
                    index,
                )
            )
        if evidence.verification_status in {"disputed", "retracted"}:
            issues.append(
                _issue(
                    "warning",
                    f"evidence-{evidence.verification_status}",
                    f"Record is quarantined from default screening: {evidence.reason}",
                    index,
                )
            )
        if any("Â" in str(value) for value in record.values()):
            issues.append(
                _issue("warning", "encoding-artifact", "Possible mojibake encoding artifact", index)
            )
    return ValidationReport(len(values), tuple(issues))


def _validate_number(
    record: Mapping[str, Any],
    field: str,
    index: int,
    issues: list[ValidationIssue],
    *,
    minimum: float,
) -> None:
    value = record.get(field)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        issues.append(_issue("error", f"invalid-{field}", f"{field} must be numeric", index))
    elif value < minimum:
        issues.append(
            _issue("error", f"invalid-{field}", f"{field} cannot be less than {minimum}", index)
        )


def _issue(
    severity: Literal["error", "warning"],
    code: str,
    message: str,
    index: int,
) -> ValidationIssue:
    return ValidationIssue(severity, code, message, index)
