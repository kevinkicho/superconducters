"""Raw experimental evidence manifests and independent replication checks."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

MeasurementType = Literal["resistivity", "susceptibility", "specific-heat", "xrd"]


@dataclass(frozen=True, slots=True)
class ExperimentRecord:
    sample_id: str
    formula: str
    laboratory: str
    pressure_gpa: float
    measurement_type: MeasurementType
    raw_data_path: str
    raw_data_sha256: str
    calibration_reference: str
    observed_transition_k: float | None = None
    zero_resistance: bool = False
    meissner_effect: bool = False


class ExperimentLedger:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def list(self) -> list[ExperimentRecord]:
        if not self.path.exists():
            return []
        values = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(values, list):
            raise ValueError("Experiment ledger must contain a JSON list")
        return [ExperimentRecord(**value) for value in values]

    def ingest(
        self,
        *,
        sample_id: str,
        formula: str,
        laboratory: str,
        pressure_gpa: float,
        measurement_type: MeasurementType,
        raw_data_path: str | Path,
        calibration_reference: str,
        observed_transition_k: float | None = None,
        zero_resistance: bool = False,
        meissner_effect: bool = False,
    ) -> ExperimentRecord:
        raw_path = Path(raw_data_path).resolve()
        if not raw_path.is_file():
            raise FileNotFoundError(f"Raw experimental data not found: {raw_path}")
        if not laboratory.strip() or not calibration_reference.strip():
            raise ValueError("Laboratory and calibration reference are required")
        if not sample_id.strip() or not formula.strip():
            raise ValueError("Sample ID and formula are required")
        if pressure_gpa < 0:
            raise ValueError("Pressure cannot be negative")
        if observed_transition_k is not None and observed_transition_k < 0:
            raise ValueError("Observed transition temperature cannot be negative")
        if zero_resistance and measurement_type != "resistivity":
            raise ValueError("Zero resistance requires a resistivity measurement")
        if meissner_effect and measurement_type != "susceptibility":
            raise ValueError("Meissner evidence requires a susceptibility measurement")
        record = ExperimentRecord(
            sample_id=sample_id.strip(),
            formula=formula.strip(),
            laboratory=laboratory.strip(),
            pressure_gpa=pressure_gpa,
            measurement_type=measurement_type,
            raw_data_path=str(raw_path),
            raw_data_sha256=_sha256(raw_path),
            calibration_reference=calibration_reference.strip(),
            observed_transition_k=observed_transition_k,
            zero_resistance=zero_resistance,
            meissner_effect=meissner_effect,
        )
        values = self.list()
        if any(
            existing.sample_id == record.sample_id
            and existing.measurement_type == record.measurement_type
            and existing.laboratory == record.laboratory
            for existing in values
        ):
            raise ValueError("Duplicate experiment manifest")
        values.append(record)
        self._write(values)
        return record

    def replication_summary(self, formula: str) -> dict[str, object]:
        values = [
            record
            for record in self.list()
            if record.formula == formula and self.verify_integrity(record)
        ]
        zero_labs = {record.laboratory for record in values if record.zero_resistance}
        meissner_labs = {record.laboratory for record in values if record.meissner_effect}
        independent_labs = zero_labs & meissner_labs
        return {
            "formula": formula,
            "laboratories": sorted({record.laboratory for record in values}),
            "zero_resistance_laboratories": sorted(zero_labs),
            "meissner_laboratories": sorted(meissner_labs),
            "independently_replicated": len(independent_labs) >= 2,
        }

    @staticmethod
    def verify_integrity(record: ExperimentRecord) -> bool:
        path = Path(record.raw_data_path)
        return path.is_file() and _sha256(path) == record.raw_data_sha256

    def _write(self, values: list[ExperimentRecord]) -> None:
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
