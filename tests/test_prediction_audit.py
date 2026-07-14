import pytest

from superconductors.experiments import ExperimentLedger
from superconductors.prediction import Prediction
from superconductors.prediction_audit import PredictionLedger


def _prediction(tc=100, uncertainty=10):
    return Prediction("Test", tc, uncertainty, "model", 0.5, "declared domain")


def test_prospective_prediction_is_versioned_before_outcome(tmp_path):
    ledger = PredictionLedger(tmp_path / "predictions.json")
    record = ledger.register(
        _prediction(), pressure_gpa=1, model_version="model-1", dataset_version="data-1"
    )
    assert record.observed_tc_k is None
    assert record.lower_tc_k == 90
    assert ledger.list() == [record]

    resolved = ledger.record_outcome(
        record.prediction_id, observed_tc_k=105, experiment_reference="experiment-ledger:sample-1"
    )
    assert resolved.observed_tc_k == 105
    with pytest.raises(ValueError, match="append-only"):
        ledger.record_outcome(
            record.prediction_id, observed_tc_k=106, experiment_reference="replacement"
        )


def test_calibration_reports_error_bias_coverage_and_sample_warning(tmp_path):
    ledger = PredictionLedger(tmp_path / "predictions.json")
    first = ledger.register(
        _prediction(100, 10), pressure_gpa=0, model_version="v1", dataset_version="d1"
    )
    second = ledger.register(
        _prediction(200, 5), pressure_gpa=0, model_version="v1", dataset_version="d1"
    )
    ledger.record_outcome(first.prediction_id, observed_tc_k=105, experiment_reference="exp:1")
    ledger.record_outcome(second.prediction_id, observed_tc_k=220, experiment_reference="exp:2")

    assert ledger.calibration_report().resolved_predictions == 0
    report = ledger.calibration_report(minimum_required=3, verified_only=False)
    assert report.resolved_predictions == 2
    assert report.mean_absolute_error_k == pytest.approx(12.5)
    assert report.mean_bias_k == pytest.approx(-12.5)
    assert report.interval_coverage == 0.5
    assert report.sufficient_sample_size is False


def test_empty_report_and_invalid_registration_are_fail_closed(tmp_path):
    ledger = PredictionLedger(tmp_path / "predictions.json")
    assert ledger.calibration_report().mean_absolute_error_k is None
    with pytest.raises(ValueError, match="versions"):
        ledger.register(_prediction(), pressure_gpa=0, model_version="", dataset_version="d1")
    with pytest.raises(KeyError, match="Unknown"):
        ledger.record_outcome("missing", observed_tc_k=1, experiment_reference="exp")


def test_verified_outcome_is_linked_to_intact_experiment(tmp_path):
    predictions = PredictionLedger(tmp_path / "predictions.json")
    prediction = predictions.register(
        _prediction(), pressure_gpa=1, model_version="v1", dataset_version="d1"
    )
    raw = tmp_path / "raw.csv"
    raw.write_text("temperature,resistance\n105,0\n", encoding="utf-8")
    experiments = ExperimentLedger(tmp_path / "experiments.json")
    experiments.ingest(
        sample_id="blind-1",
        formula="Test",
        laboratory="Lab A",
        pressure_gpa=1,
        measurement_type="resistivity",
        raw_data_path=raw,
        calibration_reference="cal-1",
        observed_transition_k=105,
        zero_resistance=True,
    )

    resolved = predictions.record_verified_outcome(
        prediction.prediction_id,
        experiment_ledger=experiments,
        sample_id="blind-1",
        laboratory="Lab A",
        measurement_type="resistivity",
    )
    assert resolved.experiment_sha256 is not None
    assert predictions.calibration_report().resolved_predictions == 1


def test_verified_outcome_rejects_tampered_or_mismatched_experiment(tmp_path):
    predictions = PredictionLedger(tmp_path / "predictions.json")
    prediction = predictions.register(
        _prediction(), pressure_gpa=1, model_version="v1", dataset_version="d1"
    )
    raw = tmp_path / "raw.csv"
    raw.write_text("original", encoding="utf-8")
    experiments = ExperimentLedger(tmp_path / "experiments.json")
    experiments.ingest(
        sample_id="sample",
        formula="Other",
        laboratory="Lab A",
        pressure_gpa=1,
        measurement_type="resistivity",
        raw_data_path=raw,
        calibration_reference="cal",
        observed_transition_k=100,
        zero_resistance=True,
    )
    with pytest.raises(ValueError, match="formula"):
        predictions.record_verified_outcome(
            prediction.prediction_id,
            experiment_ledger=experiments,
            sample_id="sample",
            laboratory="Lab A",
            measurement_type="resistivity",
        )
    raw.write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="integrity"):
        predictions.record_verified_outcome(
            prediction.prediction_id,
            experiment_ledger=experiments,
            sample_id="sample",
            laboratory="Lab A",
            measurement_type="resistivity",
        )
