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
