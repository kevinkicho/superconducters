import json

import pytest

from superconductors.models import Candidate
from superconductors.repository import CandidateRepository


def test_repository_reads_legacy_schema(tmp_path):
    path = tmp_path / "database.json"
    path.write_text(
        json.dumps([{"name": "LaH10", "Tc": 250, "pressure": 170}]),
        encoding="utf-8",
    )

    candidates = CandidateRepository(path).list()

    assert candidates == [Candidate(formula="LaH10", tc=250.0, pressure=170.0)]


def test_append_preserves_existing_raw_fields(tmp_path):
    path = tmp_path / "database.json"
    path.write_text(
        json.dumps([{"name": "Existing", "Tc": 100, "reference": "paper"}]),
        encoding="utf-8",
    )
    repository = CandidateRepository(path)

    repository.append(Candidate(formula="New", tc=200, source="test"))

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw[0]["reference"] == "paper"
    assert raw[1]["formula"] == "New"


def test_save_round_trips_canonical_candidates(tmp_path):
    repository = CandidateRepository(tmp_path / "database.json")
    expected = [Candidate(formula="H3S", tc=203, pressure=155, source="test")]

    repository.save(expected)

    assert repository.list() == expected


def test_repository_rejects_non_list_database(tmp_path):
    path = tmp_path / "database.json"
    path.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON list"):
        CandidateRepository(path).list()


@pytest.mark.parametrize(
    ("record", "message"),
    [
        ("not an object", "index 0 must be a JSON object"),
        ({"tc": 100}, "index 0 must include a formula"),
    ],
)
def test_repository_reports_invalid_record_index(tmp_path, record, message):
    path = tmp_path / "database.json"
    path.write_text(json.dumps([record]), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        CandidateRepository(path).list()


def test_append_rejects_non_list_database_without_overwriting_it(tmp_path):
    path = tmp_path / "database.json"
    path.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON list"):
        CandidateRepository(path).append(Candidate(formula="H3S"))

    assert path.read_text(encoding="utf-8") == "{}"


@pytest.mark.parametrize("candidate", [Candidate(formula=""), Candidate(formula="   ")])
def test_repository_does_not_persist_empty_formulas(tmp_path, candidate):
    path = tmp_path / "database.json"
    repository = CandidateRepository(path)

    with pytest.raises(ValueError, match="formula must not be empty"):
        repository.save([candidate])

    assert not path.exists()


def test_repository_rejects_non_candidate_writes(tmp_path):
    repository = CandidateRepository(tmp_path / "database.json")

    with pytest.raises(TypeError, match="Candidate instances"):
        repository.append({"formula": "H3S"})
