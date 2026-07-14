import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing

import pytest

from superconductors.api.errors import DuplicateCandidateError
from superconductors.api.store import SCHEMA_VERSION, ApplicationStore
from superconductors.models import Candidate


def test_store_sets_schema_version(tmp_path):
    path = tmp_path / "application.sqlite3"
    ApplicationStore(path)

    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION


def test_store_rejects_newer_schema(tmp_path):
    path = tmp_path / "application.sqlite3"
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION + 1}")

    with pytest.raises(RuntimeError, match="newer than supported"):
        ApplicationStore(path)


def test_store_rejects_incomplete_existing_table(tmp_path):
    path = tmp_path / "application.sqlite3"
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("CREATE TABLE candidates (id TEXT PRIMARY KEY)")

    with pytest.raises(RuntimeError, match="table candidates is missing"):
        ApplicationStore(path)


def test_concurrent_candidate_writes_are_not_lost(tmp_path):
    store = ApplicationStore(tmp_path / "application.sqlite3")

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(
            executor.map(
                store.add_candidate,
                [Candidate(formula=f"Candidate{index}", source="api") for index in range(20)],
            )
        )

    assert len(results) == 20
    assert len({candidate_id for candidate_id, _ in results}) == 20
    assert len(store.list_candidates()) == 20


def test_concurrent_duplicate_candidates_are_atomic(tmp_path):
    store = ApplicationStore(tmp_path / "application.sqlite3")
    candidate = Candidate(formula="H3S", tc=203, pressure=155, source="api")

    def add_candidate(_):
        try:
            store.add_candidate(candidate)
            return True
        except DuplicateCandidateError:
            return False

    with ThreadPoolExecutor(max_workers=8) as executor:
        inserted = list(executor.map(add_candidate, range(12)))

    assert sum(inserted) == 1
    assert len(store.list_candidates()) == 1


def test_concurrent_submission_ids_are_unique(tmp_path):
    store = ApplicationStore(tmp_path / "application.sqlite3")

    def submit(index):
        return store.add_submission("candidate-id", "H3S", {"attempt": index})

    with ThreadPoolExecutor(max_workers=8) as executor:
        submissions = list(executor.map(submit, range(20)))

    assert len({submission["id"] for submission in submissions}) == 20
    assert len(store.list_submissions()) == 20
