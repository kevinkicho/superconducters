import pytest

from scripts.ingest_experiment import main as ingest_main
from superconductors.experiments import ExperimentLedger


def _raw(tmp_path, name):
    path = tmp_path / name
    path.write_text("temperature,resistance\n300,0\n", encoding="utf-8")
    return path


def test_experiment_ingestion_hashes_raw_data_and_persists(tmp_path):
    ledger = ExperimentLedger(tmp_path / "ledger.json")
    record = ledger.ingest(
        sample_id="sample-1",
        formula="H3S",
        laboratory="Lab A",
        pressure_gpa=155,
        measurement_type="resistivity",
        raw_data_path=_raw(tmp_path, "resistance.csv"),
        calibration_reference="calibration-1",
        observed_transition_k=203,
        zero_resistance=True,
    )
    assert len(record.raw_data_sha256) == 64
    assert ledger.verify_integrity(record) is True
    assert ledger.list() == [record]

    (tmp_path / "resistance.csv").write_text("modified", encoding="utf-8")
    assert ledger.verify_integrity(record) is False


def test_replication_requires_two_labs_with_electrical_and_magnetic_evidence(tmp_path):
    ledger = ExperimentLedger(tmp_path / "ledger.json")
    for laboratory in ("Lab A", "Lab B"):
        ledger.ingest(
            sample_id=f"{laboratory}-resistance",
            formula="H3S",
            laboratory=laboratory,
            pressure_gpa=155,
            measurement_type="resistivity",
            raw_data_path=_raw(tmp_path, f"{laboratory}-r.csv"),
            calibration_reference="resistance-calibration",
            zero_resistance=True,
        )
        ledger.ingest(
            sample_id=f"{laboratory}-magnetic",
            formula="H3S",
            laboratory=laboratory,
            pressure_gpa=155,
            measurement_type="susceptibility",
            raw_data_path=_raw(tmp_path, f"{laboratory}-m.csv"),
            calibration_reference="susceptibility-calibration",
            meissner_effect=True,
        )
    assert ledger.replication_summary("H3S")["independently_replicated"] is True


def test_experiment_ingestion_rejects_missing_raw_data_and_duplicates(tmp_path):
    ledger = ExperimentLedger(tmp_path / "ledger.json")
    kwargs = {
        "sample_id": "sample-1",
        "formula": "H3S",
        "laboratory": "Lab A",
        "pressure_gpa": 155,
        "measurement_type": "resistivity",
        "calibration_reference": "calibration-1",
    }
    with pytest.raises(FileNotFoundError):
        ledger.ingest(raw_data_path=tmp_path / "missing.csv", **kwargs)
    raw = _raw(tmp_path, "raw.csv")
    ledger.ingest(raw_data_path=raw, **kwargs)
    with pytest.raises(ValueError, match="Duplicate"):
        ledger.ingest(raw_data_path=raw, **kwargs)


def test_experiment_signatures_must_match_measurement_type(tmp_path):
    ledger = ExperimentLedger(tmp_path / "ledger.json")
    raw = _raw(tmp_path, "raw.csv")
    base = {
        "sample_id": "sample-1",
        "formula": "H3S",
        "laboratory": "Lab A",
        "pressure_gpa": 155,
        "raw_data_path": raw,
        "calibration_reference": "calibration-1",
    }
    with pytest.raises(ValueError, match="Zero resistance"):
        ledger.ingest(measurement_type="xrd", zero_resistance=True, **base)
    with pytest.raises(ValueError, match="Meissner"):
        ledger.ingest(measurement_type="resistivity", meissner_effect=True, **base)


def test_experiment_ingestion_cli_writes_output_ledger(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "output"))
    raw = _raw(tmp_path, "raw.csv")
    assert (
        ingest_main(
            [
                str(raw),
                "--sample-id",
                "sample-1",
                "--formula",
                "H3S",
                "--laboratory",
                "Lab A",
                "--pressure-gpa",
                "155",
                "--measurement-type",
                "resistivity",
                "--calibration-reference",
                "calibration-1",
                "--zero-resistance",
            ]
        )
        == 0
    )
    assert '"sample_id": "sample-1"' in capsys.readouterr().out
    assert len(ExperimentLedger(tmp_path / "output" / "experiment_ledger.json").list()) == 1
