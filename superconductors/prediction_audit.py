"""Prospective prediction registration and outcome-based calibration metrics."""

from __future__ import annotations

import json
import math
import os
import tempfile
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .prediction import Prediction


@dataclass(frozen=True, slots=True)
class ProspectivePrediction:
    prediction_id: str
    registered_at: str
    formula: str
    pressure_gpa: float | None
    predicted_tc_k: float
    lower_tc_k: float
    upper_tc_k: float
    method: str
    model_version: str
    dataset_version: str
    applicability: str
    observed_tc_k: float | None = None
    observed_at: str | None = None
    experiment_reference: str | None = None
    experiment_sha256: str | None = None
    measurement_type: str | None = None


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    resolved_predictions: int
    minimum_required: int
    mean_absolute_error_k: float | None
    root_mean_squared_error_k: float | None
    mean_bias_k: float | None
    interval_coverage: float | None

    @property
    def sufficient_sample_size(self) -> bool:
        return self.resolved_predictions >= self.minimum_required

    def to_dict(self) -> dict[str, object]:
        return {**asdict(self), "sufficient_sample_size": self.sufficient_sample_size}


class PredictionLedger:
    """JSON ledger that prevents predictions from being changed after outcomes."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def list(self) -> list[ProspectivePrediction]:
        if not self.path.exists():
            return []
        values = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(values, list):
            raise ValueError("Prediction ledger must contain a JSON list")
        return [ProspectivePrediction(**value) for value in values]

    def register(
        self,
        prediction: Prediction,
        *,
        pressure_gpa: float | None,
        model_version: str,
        dataset_version: str,
    ) -> ProspectivePrediction:
        if not model_version.strip() or not dataset_version.strip():
            raise ValueError("Model and dataset versions are required")
        if pressure_gpa is not None and (not math.isfinite(pressure_gpa) or pressure_gpa < 0):
            raise ValueError("Pressure must be finite and non-negative")
        record = ProspectivePrediction(
            prediction_id=str(uuid.uuid4()),
            registered_at=_now(),
            formula=prediction.formula,
            pressure_gpa=pressure_gpa,
            predicted_tc_k=prediction.tc,
            lower_tc_k=max(0.0, prediction.tc - prediction.uncertainty),
            upper_tc_k=prediction.tc + prediction.uncertainty,
            method=prediction.method,
            model_version=model_version.strip(),
            dataset_version=dataset_version.strip(),
            applicability=prediction.applicability,
        )
        values = self.list()
        values.append(record)
        self._write(values)
        return record

    def record_outcome(
        self,
        prediction_id: str,
        *,
        observed_tc_k: float,
        experiment_reference: str,
    ) -> ProspectivePrediction:
        if not math.isfinite(observed_tc_k) or observed_tc_k < 0:
            raise ValueError("Observed Tc must be finite and non-negative")
        if not experiment_reference.strip():
            raise ValueError("Experiment reference is required")
        values = self.list()
        matches = [
            index for index, value in enumerate(values) if value.prediction_id == prediction_id
        ]
        if not matches:
            raise KeyError(f"Unknown prediction ID: {prediction_id}")
        index = matches[0]
        existing = values[index]
        if existing.observed_tc_k is not None:
            raise ValueError("Prediction outcome is append-only and already recorded")
        updated = ProspectivePrediction(
            **{
                **asdict(existing),
                "observed_tc_k": observed_tc_k,
                "observed_at": _now(),
                "experiment_reference": experiment_reference.strip(),
            }
        )
        values[index] = updated
        self._write(values)
        return updated

    def record_verified_outcome(
        self,
        prediction_id: str,
        *,
        experiment_ledger: object,
        sample_id: str,
        laboratory: str,
        measurement_type: str,
        pressure_tolerance_gpa: float = 1.0,
    ) -> ProspectivePrediction:
        """Resolve a prediction from one intact, physically signed experiment."""
        from .experiments import ExperimentLedger

        if not isinstance(experiment_ledger, ExperimentLedger):
            raise TypeError("A verified ExperimentLedger is required")
        if pressure_tolerance_gpa < 0:
            raise ValueError("Pressure tolerance cannot be negative")
        predictions = self.list()
        prediction_matches = [
            (index, value)
            for index, value in enumerate(predictions)
            if value.prediction_id == prediction_id
        ]
        if not prediction_matches:
            raise KeyError(f"Unknown prediction ID: {prediction_id}")
        prediction_index, prediction = prediction_matches[0]
        if prediction.observed_tc_k is not None:
            raise ValueError("Prediction outcome is append-only and already recorded")
        matches = [
            record
            for record in experiment_ledger.list()
            if record.sample_id == sample_id
            and record.laboratory == laboratory
            and record.measurement_type == measurement_type
        ]
        if len(matches) != 1:
            raise ValueError("Exactly one matching experiment record is required")
        experiment = matches[0]
        if not experiment_ledger.verify_integrity(experiment):
            raise ValueError("Experiment raw-data integrity check failed")
        if experiment.formula != prediction.formula:
            raise ValueError("Experiment formula does not match prediction")
        if prediction.pressure_gpa is None:
            raise ValueError("Prediction pressure is required for verified outcomes")
        if abs(experiment.pressure_gpa - prediction.pressure_gpa) > pressure_tolerance_gpa:
            raise ValueError("Experiment pressure is outside the prediction tolerance")
        if experiment.observed_transition_k is None:
            raise ValueError("Experiment has no observed transition temperature")
        signature_valid = (
            experiment.measurement_type == "resistivity" and experiment.zero_resistance
        ) or (experiment.measurement_type == "susceptibility" and experiment.meissner_effect)
        if not signature_valid:
            raise ValueError("Experiment lacks a physical superconducting signature")
        verified = ProspectivePrediction(
            **{
                **asdict(prediction),
                "observed_tc_k": experiment.observed_transition_k,
                "observed_at": _now(),
                "experiment_reference": (
                    f"experiment-ledger:{experiment.laboratory}:{experiment.sample_id}:"
                    f"{experiment.measurement_type}"
                ),
                "experiment_sha256": experiment.raw_data_sha256,
                "measurement_type": experiment.measurement_type,
            }
        )
        predictions[prediction_index] = verified
        self._write(predictions)
        return verified

    def calibration_report(
        self, *, minimum_required: int = 20, verified_only: bool = True
    ) -> CalibrationReport:
        if minimum_required < 1:
            raise ValueError("Minimum required sample size must be positive")
        resolved = [
            value
            for value in self.list()
            if value.observed_tc_k is not None
            and (not verified_only or value.experiment_sha256 is not None)
        ]
        if not resolved:
            return CalibrationReport(0, minimum_required, None, None, None, None)
        errors = [value.predicted_tc_k - value.observed_tc_k for value in resolved]  # type: ignore[operator]
        absolute = [abs(error) for error in errors]
        squared = [error**2 for error in errors]
        covered = [
            value.lower_tc_k <= value.observed_tc_k <= value.upper_tc_k  # type: ignore[operator]
            for value in resolved
        ]
        count = len(resolved)
        return CalibrationReport(
            count,
            minimum_required,
            sum(absolute) / count,
            math.sqrt(sum(squared) / count),
            sum(errors) / count,
            sum(covered) / count,
        )

    def _write(self, values: list[ProspectivePrediction]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp", text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump([asdict(value) for value in values], handle, indent=2)
                handle.write("\n")
            os.replace(temporary, self.path)
        except BaseException:
            Path(temporary).unlink(missing_ok=True)
            raise


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
