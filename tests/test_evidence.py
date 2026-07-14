from superconductors.evidence import classify_evidence
from superconductors.models import Candidate
from superconductors.pipeline import screen_candidates


def test_retracted_doi_is_quarantined():
    evidence = classify_evidence(
        {
            "doi": "10.1038/s41586-023-05742-0",
            "measurement_method": "four-probe resistance",
        }
    )
    assert evidence.evidence_type == "claimed"
    assert evidence.verification_status == "retracted"
    assert evidence.eligible_for_screening is False


def test_prediction_metadata_is_calculated_not_measured():
    evidence = classify_evidence(
        {"measurement_method": "predicted (Eliashberg)", "structure": "Fm-3m (predicted)"}
    )
    assert evidence.evidence_type == "calculated"
    assert evidence.verification_status == "unverified"


def test_pipeline_excludes_quarantined_claims_by_default():
    candidates = [
        Candidate("Retracted", tc=294, verification_status="retracted"),
        Candidate("Measured", tc=203, evidence_type="measured"),
    ]
    assert [candidate.formula for candidate in screen_candidates(candidates)] == ["Measured"]
    assert [
        candidate.formula for candidate in screen_candidates(candidates, include_quarantined=True)
    ] == ["Retracted", "Measured"]


def test_invalid_explicit_classification_does_not_bypass_quarantine_rules():
    evidence = classify_evidence(
        {"evidence_type": "certain", "verification_status": "trust-me", "reference": "paper"}
    )
    assert evidence.evidence_type == "unclassified"
    assert evidence.verification_status == "original-only"


def test_citation_alone_does_not_imply_measurement():
    evidence = classify_evidence({"reference": "A published paper"})
    assert evidence.evidence_type == "unclassified"
    assert evidence.verification_status == "original-only"


def test_physical_measurement_method_is_measured_despite_prediction_context():
    evidence = classify_evidence(
        {
            "measurement_method": "four-probe resistance and magnetic susceptibility",
            "structure": "structure predicted before synthesis",
        }
    )
    assert evidence.evidence_type == "measured"


def test_nested_prediction_method_is_calculated():
    evidence = classify_evidence(
        {"reference": "A paper", "external_database": {"prediction_method": "Eliashberg"}}
    )
    assert evidence.evidence_type == "calculated"
