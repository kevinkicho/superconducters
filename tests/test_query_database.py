import argparse
import json

import pytest

from superconductors.query import QueryFilters, high_throughput_screening, load_database, query

RECORDS = [
    {
        "name": "H3S",
        "Tc": 203,
        "pressure": 155,
        "material_class": "hydride",
        "feasibility_score": 0.8,
    },
    {
        "name": "MgB2",
        "Tc": 39,
        "pressure": 0,
        "material_class": "conventional",
        "feasibility_score": 0.95,
    },
]


def test_load_database_validates_top_level_shape(tmp_path):
    path = tmp_path / "database.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON list"):
        load_database(path)


def test_combined_filters():
    results = query(
        RECORDS,
        QueryFilters(tc_min=100, pressure_max=200, material_class="hydride"),
    )
    assert [record["name"] for record in results] == ["H3S"]


def test_legacy_argparse_namespace_is_supported():
    filters = argparse.Namespace(
        name="mgb2",
        tc_min=None,
        tc_max=None,
        pressure_min=None,
        pressure_max=None,
        synthesis_method=None,
        material_class=None,
        feasibility_score_min=None,
    )
    assert query(RECORDS, filters)[0]["name"] == "MgB2"


def test_invalid_filter_type_is_rejected():
    with pytest.raises(TypeError, match="Numeric"):
        query(RECORDS, QueryFilters(tc_min="hot"))


def test_high_throughput_screening_ranks_and_limits():
    results = high_throughput_screening(
        RECORDS,
        min_tc=0,
        max_tc=300,
        max_pressure=200,
        min_feasibility=0.5,
        max_results=1,
    )
    assert [record["name"] for record in results] == ["H3S"]


def test_load_database_reads_records(tmp_path):
    path = tmp_path / "database.json"
    path.write_text(json.dumps(RECORDS), encoding="utf-8")
    assert load_database(path) == RECORDS
