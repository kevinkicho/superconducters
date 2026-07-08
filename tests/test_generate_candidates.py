import pytest
from scripts.generate_candidates import generate_candidates, filter_candidates, rank_candidates

def test_generate_candidates_returns_list():
    result = generate_candidates()
    assert isinstance(result, list)

def test_generate_candidates_non_empty():
    result = generate_candidates()
    assert len(result) > 0

def test_filter_candidates_removes_invalid():
    candidates = [
        {"formula": "H3S", "tc": 203, "pressure": 150},
        {"formula": "LaH10", "tc": 250, "pressure": 170},
        {"formula": "", "tc": 0, "pressure": 0},
    ]
    filtered = filter_candidates(candidates)
    assert len(filtered) == 2
    assert all(c["formula"] for c in filtered)

def test_rank_candidates_orders_by_tc():
    candidates = [
        {"formula": "A", "tc": 100},
        {"formula": "B", "tc": 200},
        {"formula": "C", "tc": 150},
    ]
    ranked = rank_candidates(candidates)
    assert ranked[0]["tc"] == 200
    assert ranked[1]["tc"] == 150
    assert ranked[2]["tc"] == 100

def test_generate_candidates_includes_required_keys():
    result = generate_candidates()
    for c in result:
        assert "formula" in c
        assert "tc" in c
        assert "pressure" in c

def test_filter_candidates_all_valid():
    candidates = [
        {"formula": "H3S", "tc": 203, "pressure": 150},
        {"formula": "LaH10", "tc": 250, "pressure": 170},
    ]
    filtered = filter_candidates(candidates)
    assert filtered == candidates


def test_rank_candidates_ties():
    candidates = [
        {"formula": "A", "tc": 100},
        {"formula": "B", "tc": 100},
    ]
    ranked = rank_candidates(candidates)
    assert ranked[0]["tc"] == 100
    assert ranked[1]["tc"] == 100


def test_filter_candidates_handles_none_formula():
    candidates = [
        {"formula": None, "tc": 0, "pressure": 0},
        {"formula": "H3S", "tc": 203, "pressure": 150},
    ]
    filtered = filter_candidates(candidates)
    assert len(filtered) == 1
    assert filtered[0]["formula"] == "H3S"
