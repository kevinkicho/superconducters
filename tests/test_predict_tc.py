import pytest

from superconductors.prediction import (
    average_debye,
    average_valence,
    parse_formula,
    predict,
    predict_tc,
    predict_tc_with_uncertainty,
    unvalidated_heuristic,
)


def test_parse_formula_combines_repeated_elements():
    assert parse_formula("H2SH") == {"H": 3.0, "S": 1.0}


@pytest.mark.parametrize("formula", ["", "   ", "H3S!", "Unknown", None])
def test_invalid_formulas_are_rejected(formula):
    with pytest.raises(ValueError):
        parse_formula(formula)


def test_descriptors_are_weighted_by_stoichiometry():
    assert average_valence("H3S") == pytest.approx(2.25)
    assert average_debye("H3S") == pytest.approx(100.0)


def test_prediction_reports_benchmark_provenance():
    result = predict("H3S")
    assert result.tc == 203
    assert result.reference_pressure == 155
    assert "benchmark" in result.method.lower()
    assert "not a novel-material prediction" in result.applicability


def test_compatibility_prediction_functions_agree():
    assert predict_tc("LaH10", pressure=170) == pytest.approx(250)


def test_uncertainty_interval_contains_prediction():
    tc, interval = predict_tc_with_uncertainty("Nb3Sn")
    assert interval[0] <= tc <= interval[1]


def test_non_numeric_pressure_is_rejected():
    with pytest.raises(ValueError, match="Pressure"):
        predict_tc("H3S", pressure="high")


def test_out_of_domain_requests_are_rejected():
    with pytest.raises(ValueError, match="No validated Tc model"):
        predict("LiH")
    with pytest.raises(ValueError, match="applies near 155 GPa"):
        predict("H3S", pressure=0)


def test_historical_heuristic_requires_explicit_opt_in():
    result = unvalidated_heuristic("H3S")
    assert result.confidence == 0
    assert "ignores pressure" in result.applicability
