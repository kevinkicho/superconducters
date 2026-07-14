import pytest

from superconductors.evidence_audit import build_evidence_audit


def test_unclassified_queue_is_ranked_and_traceable():
    audit = build_evidence_audit(
        [
            {"name": "Low", "Tc": 20, "pressure": 0, "reference": "paper A"},
            {"name": "Measured", "Tc": 100, "measurement_method": "four probe"},
            {"name": "High", "Tc": 290, "pressure": 2, "reference": "paper B"},
        ]
    )

    assert audit.records_checked == 3
    assert audit.counts == {"measured": 1, "unclassified": 2}
    assert [item.material for item in audit.items] == ["High", "Low"]
    assert audit.items[0].record_index == 2


def test_quarantine_scope_only_returns_disputed_or_retracted_records():
    audit = build_evidence_audit(
        [
            {"name": "Normal", "reference": "paper"},
            {"name": "Retracted", "doi": "10.1038/s41586-020-2801-z"},
        ],
        scope="quarantined",
    )
    assert [item.material for item in audit.items] == ["Retracted"]


def test_audit_rejects_invalid_scope_and_limit():
    with pytest.raises(ValueError, match="scope"):
        build_evidence_audit([], scope="unknown")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="positive"):
        build_evidence_audit([], limit=0)
