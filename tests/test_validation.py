from superconductors.validation import validate_records


def test_citation_only_record_warns_about_provenance_and_evidence():
    report = validate_records(
        [{"name": "H3S", "Tc": 203, "pressure": 155, "structure": "Im-3m", "reference": "paper"}]
    )
    assert report.is_valid
    assert report.errors == 0
    assert [issue.code for issue in report.issues] == [
        "implicit-provenance",
        "evidence-unclassified",
    ]


def test_explicit_source_removes_provenance_warning():
    report = validate_records(
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
    )
    assert report.to_dict()["issues"] == []


def test_invalid_numbers_and_duplicates_are_errors():
    records = [
        {"name": "A", "Tc": "hot", "pressure": -1, "structure": "x", "reference": "r"},
        {"name": "a", "Tc": 10, "pressure": 0, "structure": "x", "reference": "r"},
    ]
    report = validate_records(records)
    codes = [issue.code for issue in report.issues if issue.severity == "error"]
    assert not report.is_valid
    assert "duplicate-name" in codes
    assert "invalid-Tc" in codes
    assert "invalid-pressure" in codes


def test_encoding_artifacts_are_reported():
    report = validate_records(
        [
            {
                "name": "A",
                "Tc": 10,
                "pressure": 0,
                "structure": "x",
                "reference": "900 Â°C",
                "source": "test",
            }
        ]
    )
    assert "encoding-artifact" in [issue.code for issue in report.issues]


def test_retracted_records_are_quarantined():
    report = validate_records(
        [
            {
                "name": "Lu-N-H",
                "Tc": 294,
                "pressure": 1,
                "structure": "unknown",
                "reference": "Nature 615, 244 (2023)",
                "doi": "10.1038/s41586-023-05742-0",
                "source": "literature",
            }
        ]
    )
    assert "evidence-retracted" in [issue.code for issue in report.issues]
