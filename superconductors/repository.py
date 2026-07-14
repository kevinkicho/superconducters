"""Persistence adapters for candidate materials."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from threading import RLock

from .models import Candidate


class CandidateRepository:
    """JSON-backed repository with validated reads and atomic writes."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self._lock = RLock()

    def list(self) -> list[Candidate]:
        with self._lock:
            values = self._read_values()
            candidates = []
            for index, item in enumerate(values):
                if not isinstance(item, Mapping):
                    raise ValueError(f"Candidate at index {index} must be a JSON object")
                candidate = Candidate.from_mapping(item)
                if not candidate.formula:
                    raise ValueError(f"Candidate at index {index} must include a formula")
                candidates.append(candidate)
            return candidates

    def save(self, candidates: Iterable[Candidate]) -> None:
        values = [self._serialize(candidate) for candidate in candidates]
        self._write_values(values)

    def append(self, candidate: Candidate) -> None:
        """Append without discarding fields belonging to existing raw records."""
        value = self._serialize(candidate)
        with self._lock:
            values = self._read_values()
            values.append(value)
            self._write_values(values)

    @staticmethod
    def _serialize(candidate: Candidate) -> dict[str, object]:
        if not isinstance(candidate, Candidate):
            raise TypeError("CandidateRepository accepts Candidate instances")
        if not candidate.formula.strip():
            raise ValueError("Candidate formula must not be empty")
        return candidate.to_dict()

    def _read_values(self) -> list[object]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            values = json.load(handle)
        if not isinstance(values, list):
            raise ValueError(f"Candidate database must contain a JSON list: {self.path}")
        return values

    def _write_values(self, values: list[object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            fd, temporary_name = tempfile.mkstemp(
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                text=True,
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(values, handle, indent=2, ensure_ascii=False)
                    handle.write("\n")
                os.replace(temporary_name, self.path)
            except BaseException:
                try:
                    os.unlink(temporary_name)
                except FileNotFoundError:
                    pass
                raise
