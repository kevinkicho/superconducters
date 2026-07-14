"""Transactional state for candidates created through the app and submissions."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path
from typing import Any

from superconductors.models import Candidate

from .errors import DuplicateCandidateError

SCHEMA_VERSION = 1


class ApplicationStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 30000")
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute("PRAGMA journal_mode = WAL")
                connection.execute("PRAGMA synchronous = NORMAL")
                version = connection.execute("PRAGMA user_version").fetchone()[0]
                if version > SCHEMA_VERSION:
                    raise RuntimeError(
                        f"Application database schema {version} is newer than supported "
                        f"version {SCHEMA_VERSION}"
                    )
                connection.executescript(
                    """
                CREATE TABLE IF NOT EXISTS candidates (
                    id TEXT PRIMARY KEY,
                    formula TEXT NOT NULL,
                    tc REAL,
                    pressure REAL,
                    structure TEXT,
                    source TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id TEXT NOT NULL,
                    formula TEXT NOT NULL,
                    synthesis_params TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
                )
                connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
                self._validate_schema(connection)

    @staticmethod
    def _validate_schema(connection: sqlite3.Connection) -> None:
        expected = {
            "candidates": {"id", "formula", "tc", "pressure", "structure", "source"},
            "submissions": {
                "id",
                "candidate_id",
                "formula",
                "synthesis_params",
                "status",
                "created_at",
            },
        }
        for table, columns in expected.items():
            actual = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
            if not columns <= actual:
                missing = ", ".join(sorted(columns - actual))
                raise RuntimeError(f"Application database table {table} is missing: {missing}")

    def add_candidate(self, candidate: Candidate) -> tuple[str, Candidate]:
        candidate_id = str(uuid.uuid4())
        with closing(self._connect()) as connection:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                duplicate = connection.execute(
                    """SELECT 1 FROM candidates
                    WHERE formula = ? AND tc IS ? AND pressure IS ?
                    AND structure IS ? AND source = ?""",
                    (
                        candidate.formula,
                        candidate.tc,
                        candidate.pressure,
                        candidate.structure,
                        candidate.source,
                    ),
                ).fetchone()
                if duplicate:
                    raise DuplicateCandidateError("An identical candidate already exists")
                connection.execute(
                    "INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        candidate_id,
                        candidate.formula,
                        candidate.tc,
                        candidate.pressure,
                        candidate.structure,
                        candidate.source,
                    ),
                )
        return candidate_id, candidate

    def list_candidates(self) -> list[tuple[str, Candidate]]:
        with closing(self._connect()) as connection:
            rows = connection.execute("SELECT * FROM candidates ORDER BY rowid").fetchall()
        return [
            (
                row["id"],
                Candidate(
                    formula=row["formula"],
                    tc=row["tc"],
                    pressure=row["pressure"],
                    structure=row["structure"],
                    source=row["source"],
                ),
            )
            for row in rows
        ]

    def add_submission(
        self,
        candidate_id: str,
        formula: str,
        synthesis_params: dict[str, Any] | None,
    ) -> dict[str, Any]:
        encoded = json.dumps(synthesis_params) if synthesis_params is not None else None
        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """INSERT INTO submissions (candidate_id, formula, synthesis_params, status)
                VALUES (?, ?, ?, 'submitted')""",
                    (candidate_id, formula, encoded),
                )
                submission_id = int(cursor.lastrowid)
                created_at = connection.execute(
                    "SELECT created_at FROM submissions WHERE id = ?", (submission_id,)
                ).fetchone()["created_at"]
        return {
            "id": submission_id,
            "candidate_id": candidate_id,
            "formula": formula,
            "synthesis_params": synthesis_params,
            "status": "submitted",
            "created_at": created_at,
        }

    def list_submissions(self, *, offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM submissions ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "candidate_id": row["candidate_id"],
                "formula": row["formula"],
                "synthesis_params": (
                    json.loads(row["synthesis_params"])
                    if row["synthesis_params"] is not None
                    else None
                ),
                "status": row["status"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def ready(self) -> bool:
        with closing(self._connect()) as connection:
            return connection.execute("SELECT 1").fetchone()[0] == 1
