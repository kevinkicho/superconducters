"""Application workflows shared by HTTP routes."""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass

from superconductors.models import Candidate
from superconductors.prediction import Prediction, predict
from superconductors.repository import CandidateRepository

from .errors import ApplicationDataError, DuplicateCandidateError
from .store import ApplicationStore

_IDENTITY_NAMESPACE = uuid.UUID("5f060994-194b-4db3-8ed2-dbaad06df874")


@dataclass(frozen=True, slots=True)
class IdentifiedCandidate:
    id: str
    candidate: Candidate

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, **self.candidate.to_dict()}


class ApplicationService:
    def __init__(self, repository: CandidateRepository, store: ApplicationStore):
        self.repository = repository
        self.store = store

    def candidates(self) -> list[IdentifiedCandidate]:
        try:
            base = [
                IdentifiedCandidate(_stable_id(candidate), candidate)
                for candidate in self.repository.list()
            ]
            created = [
                IdentifiedCandidate(value, candidate)
                for value, candidate in self.store.list_candidates()
            ]
        except (OSError, ValueError, sqlite3.Error) as exc:
            raise ApplicationDataError(f"Candidate storage is unavailable: {exc}") from exc
        return base + created

    def create_candidate(self, candidate: Candidate) -> IdentifiedCandidate:
        if any(existing.candidate == candidate for existing in self.candidates()):
            raise DuplicateCandidateError("An identical candidate already exists")
        try:
            candidate_id, stored = self.store.add_candidate(candidate)
        except (OSError, sqlite3.Error) as exc:
            raise ApplicationDataError(f"Candidate storage is unavailable: {exc}") from exc
        return IdentifiedCandidate(candidate_id, stored)

    def resolve_candidate(self, candidate_id: str | int) -> IdentifiedCandidate | None:
        candidates = self.candidates()
        if isinstance(candidate_id, int):
            return candidates[candidate_id - 1] if 0 < candidate_id <= len(candidates) else None
        return next((candidate for candidate in candidates if candidate.id == candidate_id), None)

    def submit(
        self,
        candidate_id: str | int,
        synthesis_params: dict[str, object] | None,
    ) -> dict[str, object] | None:
        identified = self.resolve_candidate(candidate_id)
        if identified is None:
            return None
        try:
            return self.store.add_submission(
                identified.id,
                identified.candidate.formula,
                synthesis_params,
            )
        except (OSError, sqlite3.Error) as exc:
            raise ApplicationDataError(f"Submission storage is unavailable: {exc}") from exc

    def submissions(self, *, offset: int = 0, limit: int = 100) -> list[dict[str, object]]:
        try:
            return self.store.list_submissions(offset=offset, limit=limit)
        except (OSError, ValueError, sqlite3.Error) as exc:
            raise ApplicationDataError(f"Submission storage is unavailable: {exc}") from exc

    def predict(self, formula: str) -> Prediction:
        return predict(formula)

    def ready(self) -> bool:
        try:
            self.candidates()
            return self.store.ready()
        except sqlite3.Error as exc:
            raise ApplicationDataError(f"Application state is unavailable: {exc}") from exc


def _stable_id(candidate: Candidate) -> str:
    identity = json.dumps(candidate.to_dict(), sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(_IDENTITY_NAMESPACE, identity))
