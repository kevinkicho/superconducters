"""Provenance-aware candidate screening summaries."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date
from typing import Any

from .models import Candidate


def generate_candidate_announcement(
    candidates: Iterable[Candidate | Mapping[str, Any]],
    *,
    predictions: Mapping[str, float] | None = None,
    report_date: date | None = None,
    limit: int = 5,
) -> str:
    values = [_candidate_fields(candidate) for candidate in candidates]
    predictions = predictions or {}
    lines = [
        "# Candidate Screening Update",
        "",
        f"**Date:** {(report_date or date.today()).isoformat()}",
        "",
        "> Screening results are hypotheses, not experimental confirmation.",
        "",
        "## Leading Candidates",
        "",
    ]
    if not values:
        lines.append("No candidates matched the screening criteria.")
    for index, candidate in enumerate(values[: max(0, limit)], start=1):
        formula = candidate["formula"]
        tc = predictions.get(formula, candidate["tc"])
        tc_text = f"{tc:g} K" if isinstance(tc, (int, float)) else "not supplied"
        lines.append(
            f"{index}. **{formula}** - Tc: {tc_text}; evidence: "
            f"{candidate['evidence_type']}/{candidate['verification_status']}; "
            f"provenance: {candidate['source']}"
        )
    lines.extend(
        [
            "",
            "## Next Steps",
            "",
            "1. Verify citations and calculation provenance.",
            "2. Prioritize candidates for independent DFT or experimental review.",
            "3. Record measured results separately from predictions.",
            "",
        ]
    )
    return "\n".join(lines)


def _candidate_fields(candidate: Candidate | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(candidate, Candidate):
        return {
            "formula": candidate.formula,
            "tc": candidate.tc,
            "source": candidate.source,
            "evidence_type": candidate.evidence_type,
            "verification_status": candidate.verification_status,
        }
    formula = str(candidate.get("formula") or candidate.get("name") or "").strip()
    return {
        "formula": formula,
        "tc": candidate.get("tc", candidate.get("Tc")),
        "source": candidate.get("source") or "unspecified",
        "evidence_type": candidate.get("evidence_type") or "unclassified",
        "verification_status": candidate.get("verification_status") or "unverified",
    }
