from datetime import date

import pytest

from superconductors.analysis import correlation_sensitivity_analysis
from superconductors.announcements import generate_candidate_announcement
from superconductors.models import Candidate


def test_announcement_labels_screening_and_provenance():
    announcement = generate_candidate_announcement(
        [Candidate("H3S", tc=203, pressure=155, source="literature")],
        report_date=date(2026, 7, 13),
    )
    assert "Candidate Screening Update" in announcement
    assert "not experimental confirmation" in announcement
    assert "evidence: unclassified/unverified" in announcement
    assert "provenance: literature" in announcement
    assert "2026-07-13" in announcement


def test_empty_announcement_is_explicit():
    assert "No candidates" in generate_candidate_announcement([], report_date=date(2026, 7, 13))


def test_sensitivity_is_deterministic_and_normalized():
    first = correlation_sensitivity_analysis(samples=100, seed=7)
    second = correlation_sensitivity_analysis(samples=100, seed=7)
    assert first == second
    assert sum(first["sensitivity_indices"].values()) == pytest.approx(1.0)
    assert "not Sobol" in first["method"]


@pytest.mark.parametrize("samples", [0, 1, 2])
def test_sensitivity_requires_enough_samples(samples):
    with pytest.raises(ValueError, match="at least 3"):
        correlation_sensitivity_analysis(samples=samples)


def test_legacy_modules_import_without_analysis_dependencies():
    import discovery
    import sensitivity
    import simulation

    assert callable(discovery.generate_discovery_announcement)
    assert callable(sensitivity.sobol_sensitivity_analysis)
    assert simulation.MultiFidelityGP.__name__ == "MultiFidelityGP"
