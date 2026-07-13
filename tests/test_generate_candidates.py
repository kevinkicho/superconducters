import pytest

from superconductors.generation import filter_candidates, generate_candidates, rank_candidates


def test_generated_candidates_have_provenance():
    candidates = generate_candidates(2)
    assert len(candidates) == 2
    assert all(candidate["source"] == "curated-template" for candidate in candidates)
    assert all("prediction_method" in candidate for candidate in candidates)


def test_negative_limit_is_rejected():
    with pytest.raises(ValueError, match="negative"):
        generate_candidates(-1)


def test_filter_removes_invalid_and_applies_thresholds():
    candidates = [
        {"formula": "A", "tc": 200, "pressure": 50},
        {"formula": "B", "tc": 100, "pressure": 10},
        {"formula": "", "tc": 300, "pressure": 0},
    ]
    assert filter_candidates(candidates, min_tc=150, max_pressure=100) == [candidates[0]]


def test_rank_candidates_orders_descending_without_mutating_input():
    candidates = [{"formula": "A", "tc": 100}, {"formula": "B", "tc": 200}]
    ranked = rank_candidates(candidates)
    assert [candidate["formula"] for candidate in ranked] == ["B", "A"]
    assert [candidate["formula"] for candidate in candidates] == ["A", "B"]
