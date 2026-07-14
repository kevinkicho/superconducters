import json

import pytest

import streamlit_dashboard
from superconductors.dashboard import build_snapshot, estimate_formula
from superconductors.repository import CandidateRepository


def _repository(tmp_path, records):
    path = tmp_path / "candidates.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    return CandidateRepository(path)


def test_dashboard_imports_without_optional_ui_dependencies():
    assert callable(streamlit_dashboard.main)


def test_dashboard_snapshot_prepares_metrics_and_rows(tmp_path):
    snapshot = build_snapshot(
        _repository(
            tmp_path,
            [
                {"formula": "H3S", "tc": 203, "pressure": 155},
                {"formula": "MgB2", "tc": 39, "pressure": 0},
                {"formula": "Unknown", "pressure": 0},
            ],
        ),
        limit=10,
    )

    assert snapshot.result.candidates_loaded == 3
    assert len(snapshot.measured) == 2
    assert {candidate.formula for candidate in snapshot.near_ambient} == {"MgB2", "Unknown"}
    assert snapshot.rows[0]["formula"] == "H3S"


def test_dashboard_snapshot_applies_filters(tmp_path):
    snapshot = build_snapshot(
        _repository(
            tmp_path,
            [
                {"formula": "H3S", "tc": 203, "pressure": 155},
                {"formula": "MgB2", "tc": 39, "pressure": 0},
            ],
        ),
        min_tc=100,
        max_pressure=200,
    )
    assert [candidate.formula for candidate in snapshot.result.candidates] == ["H3S"]


def test_dashboard_prediction_reports_invalid_formula():
    assert estimate_formula(" H3S ").formula == "H3S"
    with pytest.raises(ValueError, match="Unsupported chemical formula"):
        estimate_formula("not valid!")


def test_dashboard_snapshot_surfaces_malformed_database(tmp_path):
    path = tmp_path / "candidates.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON list"):
        build_snapshot(CandidateRepository(path))


class _Frame:
    def __init__(self, rows):
        self.rows = rows

    def to_csv(self, index=False):
        assert index is False
        return "formula,tc\nH3S,203\n"


class _Pandas:
    DataFrame = _Frame


class _DashboardUI:
    def __init__(self):
        self.errors = []
        self.download = None

    def columns(self, count):
        return [self] * count

    def number_input(self, label, **kwargs):
        return 0.0 if label == "Minimum Tc (K)" else 200.0

    def checkbox(self, *args, **kwargs):
        return False

    def slider(self, *args, **kwargs):
        return 25

    def dataframe(self, *args, **kwargs):
        return None

    def download_button(self, label, **kwargs):
        self.download = (label, kwargs)

    def error(self, message):
        self.errors.append(message)

    def warning(self, message):
        raise AssertionError(message)


def test_candidates_view_wires_csv_export(tmp_path):
    ui = _DashboardUI()
    repository = _repository(tmp_path, [{"formula": "H3S", "tc": 203, "pressure": 155}])

    streamlit_dashboard._candidates(ui, _Pandas, repository)

    assert ui.download[0] == "Export filtered CSV"
    assert ui.download[1]["mime"] == "text/csv"
    assert "H3S" in ui.download[1]["data"]


def test_candidates_view_displays_database_error(tmp_path):
    ui = _DashboardUI()
    path = tmp_path / "candidates.json"
    path.write_text("{}", encoding="utf-8")

    streamlit_dashboard._candidates(ui, _Pandas, CandidateRepository(path))

    assert "database is unavailable" in ui.errors[0]


class _PredictionUI:
    def __init__(self):
        self.errors = []

    def subheader(self, *args):
        return None

    def text_input(self, *args, **kwargs):
        return "not valid!"

    def button(self, *args):
        return True

    def error(self, message):
        self.errors.append(message)


def test_prediction_view_displays_formula_error():
    ui = _PredictionUI()
    streamlit_dashboard._prediction(ui)
    assert "Unsupported chemical formula" in ui.errors[0]
