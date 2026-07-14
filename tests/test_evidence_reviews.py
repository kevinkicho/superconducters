import pytest

from scripts.review_evidence import main as review_main
from superconductors.evidence import classify_evidence
from superconductors.evidence_reviews import (
    EvidenceReviewLedger,
    dataset_fingerprint,
    record_fingerprint,
)


def _records():
    return [{"name": "H3S", "Tc": 203, "reference": "primary paper"}]


def test_review_overlay_is_traceable_and_non_destructive(tmp_path):
    records = _records()
    ledger = EvidenceReviewLedger(tmp_path / "reviews.json")
    review = ledger.review(
        records,
        record_index=0,
        reviewer="Researcher A",
        primary_source="doi:10.example/paper",
        evidence_type="measured",
        verification_status="original-only",
        rationale="Four-probe resistance is reported in the primary source.",
    )

    reviewed = ledger.apply(records)
    assert "evidence_type" not in records[0]
    assert reviewed[0]["evidence_review_id"] == review.review_id
    assert classify_evidence(reviewed[0]).evidence_type == "measured"
    assert len(review.record_sha256) == 64


def test_changed_record_invalidates_review_overlay(tmp_path):
    records = _records()
    ledger = EvidenceReviewLedger(tmp_path / "reviews.json")
    ledger.review(
        records,
        record_index=0,
        reviewer="Reviewer",
        primary_source="doi:source",
        evidence_type="calculated",
        verification_status="unverified",
        rationale="The source reports a calculation.",
    )
    records[0]["Tc"] = 250
    with pytest.raises(ValueError, match="changed"):
        ledger.apply(records)


def test_duplicate_reviews_and_retraction_override_are_rejected(tmp_path):
    records = _records()
    ledger = EvidenceReviewLedger(tmp_path / "reviews.json")
    kwargs = {
        "record_index": 0,
        "reviewer": "Reviewer",
        "primary_source": "doi:source",
        "evidence_type": "measured",
        "verification_status": "original-only",
        "rationale": "Reviewed primary data.",
    }
    ledger.review(records, **kwargs)
    with pytest.raises(ValueError, match="already"):
        ledger.review(records, **kwargs)

    retracted = [{"name": "Claim", "doi": "10.1038/s41586-020-2801-z"}]
    with pytest.raises(ValueError, match="retraction"):
        EvidenceReviewLedger(tmp_path / "other.json").review(retracted, **kwargs)


def test_fingerprints_are_stable_and_order_sensitive():
    first = {"name": "A", "Tc": 1}
    same = {"Tc": 1, "name": "A"}
    assert record_fingerprint(first) == record_fingerprint(same)
    assert dataset_fingerprint([first, {"name": "B"}]) != dataset_fingerprint(
        [{"name": "B"}, first]
    )


def test_review_cli_writes_separate_ledger(monkeypatch, tmp_path, capsys):
    data = tmp_path / "data"
    output = tmp_path / "output"
    data.mkdir()
    (data / "superconductor_database.json").write_text(
        '[{"name":"H3S","Tc":203,"reference":"paper"}]', encoding="utf-8"
    )
    monkeypatch.setenv("DATA_DIR", str(data))
    monkeypatch.setenv("OUTPUT_DIR", str(output))
    assert (
        review_main(
            [
                "0",
                "--reviewer",
                "Researcher A",
                "--primary-source",
                "doi:source",
                "--evidence-type",
                "measured",
                "--verification-status",
                "original-only",
                "--rationale",
                "Primary data reviewed.",
            ]
        )
        == 0
    )
    assert '"record_index": 0' in capsys.readouterr().out
    assert len(EvidenceReviewLedger(output / "evidence_reviews.json").list()) == 1
