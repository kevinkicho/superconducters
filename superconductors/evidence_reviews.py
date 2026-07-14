"""Append-only, source-traceable manual evidence classifications."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence import EVIDENCE_TYPES, VERIFICATION_STATUSES, classify_evidence


@dataclass(frozen=True, slots=True)
class EvidenceReview:
    review_id: str
    reviewed_at: str
    record_index: int
    record_sha256: str
    reviewer: str
    primary_source: str
    evidence_type: str
    verification_status: str
    rationale: str


class EvidenceReviewLedger:
    """Store reviewed classifications separately from the legacy database."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def list(self) -> list[EvidenceReview]:
        if not self.path.exists():
            return []
        values = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(values, list):
            raise ValueError("Evidence review ledger must contain a JSON list")
        return [EvidenceReview(**value) for value in values]

    def review(
        self,
        records: Iterable[Mapping[str, Any]],
        *,
        record_index: int,
        reviewer: str,
        primary_source: str,
        evidence_type: str,
        verification_status: str,
        rationale: str,
    ) -> EvidenceReview:
        values = list(records)
        if record_index < 0 or record_index >= len(values):
            raise IndexError(f"Record index out of range: {record_index}")
        if evidence_type not in EVIDENCE_TYPES:
            raise ValueError(f"Unsupported evidence type: {evidence_type}")
        if verification_status not in VERIFICATION_STATUSES:
            raise ValueError(f"Unsupported verification status: {verification_status}")
        if verification_status == "independent" and evidence_type != "measured":
            raise ValueError("Independent verification requires measured evidence")
        reviewer = reviewer.strip()
        primary_source = primary_source.strip()
        rationale = rationale.strip()
        if not reviewer or not primary_source or not rationale:
            raise ValueError("Reviewer, primary source, and rationale are required")

        record = values[record_index]
        inferred = classify_evidence(record)
        if inferred.verification_status == "retracted" and verification_status != "retracted":
            raise ValueError("A known retraction cannot be cleared by a manual review overlay")
        reviews = self.list()
        if any(review.record_index == record_index for review in reviews):
            raise ValueError("Record already has an evidence review")
        review = EvidenceReview(
            review_id=str(uuid.uuid4()),
            reviewed_at=datetime.now(timezone.utc).isoformat(),
            record_index=record_index,
            record_sha256=record_fingerprint(record),
            reviewer=reviewer,
            primary_source=primary_source,
            evidence_type=evidence_type,
            verification_status=verification_status,
            rationale=rationale,
        )
        reviews.append(review)
        self._write(reviews)
        return review

    def apply(self, records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
        """Return classified copies, rejecting reviews against changed records."""
        values = [dict(record) for record in records]
        for review in self.list():
            if review.record_index >= len(values):
                raise ValueError(f"Reviewed record no longer exists: {review.record_index}")
            record = values[review.record_index]
            if record_fingerprint(record) != review.record_sha256:
                raise ValueError(f"Reviewed record changed at index {review.record_index}")
            record["evidence_type"] = review.evidence_type
            record["verification_status"] = review.verification_status
            record["evidence_review_id"] = review.review_id
            record["evidence_primary_source"] = review.primary_source
        return values

    def _write(self, reviews: list[EvidenceReview]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp", text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump([asdict(review) for review in reviews], handle, indent=2)
                handle.write("\n")
            os.replace(temporary, self.path)
        except BaseException:
            Path(temporary).unlink(missing_ok=True)
            raise


def record_fingerprint(record: Mapping[str, Any]) -> str:
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def dataset_fingerprint(records: Iterable[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(record_fingerprint(record).encode("ascii"))
    return digest.hexdigest()
