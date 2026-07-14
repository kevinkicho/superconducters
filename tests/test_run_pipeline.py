import json

from superconductors.cli import main
from superconductors.pipeline import run_pipeline, screen_candidates
from superconductors.repository import CandidateRepository


def _repository(tmp_path):
    path = tmp_path / "candidates.json"
    path.write_text(
        json.dumps(
            [
                {"name": "LowPressure", "Tc": 150, "pressure": 0},
                {"name": "HighTc", "Tc": 260, "pressure": 170},
                {"name": "Control", "Tc": 20, "pressure": 0},
            ]
        ),
        encoding="utf-8",
    )
    return CandidateRepository(path)


def test_pipeline_filters_and_ranks_candidates(tmp_path):
    result = run_pipeline(
        repository=_repository(tmp_path),
        min_tc=100,
        max_pressure=200,
        limit=10,
    )

    assert result.candidates_loaded == 3
    assert [candidate.formula for candidate in result.candidates] == ["HighTc", "LowPressure"]


def test_screen_candidates_handles_missing_values():
    assert screen_candidates([], min_tc=100) == []


def test_cli_prints_json(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    (tmp_path / "superconductor_database.json").write_text(
        '[{"name": "H3S", "Tc": 203, "pressure": 155}]', encoding="utf-8"
    )

    assert main(["--min-tc", "200", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["candidates_selected"] == 1
    assert payload["candidates"][0]["formula"] == "H3S"


def test_legacy_wrapper_exports_canonical_pipeline():
    import scripts.run_pipeline as legacy

    assert legacy.run_pipeline is run_pipeline


def test_cli_validation_reports_schema_status(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    (tmp_path / "superconductor_database.json").write_text(
        json.dumps(
            [
                {
                    "name": "H3S",
                    "Tc": 203,
                    "pressure": 155,
                    "structure": "Im-3m",
                    "reference": "paper",
                    "source": "literature",
                    "evidence_type": "measured",
                    "verification_status": "original-only",
                }
            ]
        ),
        encoding="utf-8",
    )

    assert main(["--validate", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["is_valid"] is True
    assert payload["warnings"] == 0


def test_cli_evidence_audit_returns_traceable_review_queue(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    (tmp_path / "superconductor_database.json").write_text(
        json.dumps(
            [
                {"name": "Needs review", "Tc": 290, "pressure": 2, "reference": "paper"},
                {"name": "Measured", "Tc": 20, "measurement_method": "four probe"},
            ]
        ),
        encoding="utf-8",
    )

    assert main(["--evidence-audit", "unclassified", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["counts"] == {"measured": 1, "unclassified": 1}
    assert payload["items"][0]["record_index"] == 0
    assert payload["items"][0]["material"] == "Needs review"


def test_cli_validation_returns_failure_for_invalid_database(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    (tmp_path / "superconductor_database.json").write_text(
        '[{"name": "broken", "Tc": "hot", "pressure": 0}]', encoding="utf-8"
    )

    assert main(["--validate"]) == 1


def test_cli_named_objective_requires_verified_evidence(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    (tmp_path / "superconductor_database.json").write_text(
        json.dumps(
            [
                {
                    "name": "VerifiedRTS",
                    "Tc": 300,
                    "pressure": 0,
                    "evidence_type": "measured",
                    "verification_status": "independent",
                }
            ]
        ),
        encoding="utf-8",
    )
    assert main(["--objective", "ambient-room-temperature", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["evaluations"][0]["meets_objective"] is True
