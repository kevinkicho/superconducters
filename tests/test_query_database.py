import pytest
import json
import os
import sys
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import scripts.query_database as qdb

def test_load_database_exists():
    entries = qdb.load_database(qdb.DATABASE_PATH)
    assert isinstance(entries, list)
    assert len(entries) > 0

def test_load_database_invalid_path():
    with pytest.raises(FileNotFoundError):
        qdb.load_database("nonexistent.json")

def test_query_all():
    entries = qdb.load_database(qdb.DATABASE_PATH)
    results = qdb.query(entries, argparse.Namespace(
        name=None, tc_min=None, tc_max=None, pressure=None,
        pressure_min=None, pressure_max=None, composition=None,
        synthesis=None, synthesis_method=None, mechanism=None
    ))
    assert len(results) == len(entries)

def test_query_by_name():
    entries = qdb.load_database(qdb.DATABASE_PATH)
    first_name = entries[0].get('name', '')
    if first_name:
        results = qdb.query(entries, argparse.Namespace(
            name=first_name, tc_min=None, tc_max=None, pressure=None,
            pressure_min=None, pressure_max=None, composition=None,
            synthesis=None, synthesis_method=None, mechanism=None
        ))
        assert len(results) == 1
        assert results[0]['name'] == first_name

def test_query_by_tc_min():
    entries = qdb.load_database(qdb.DATABASE_PATH)
    tc_min = 100
    results = qdb.query(entries, argparse.Namespace(
        name=None, tc_min=tc_min, tc_max=None, pressure=None,
        pressure_min=None, pressure_max=None, composition=None,
        synthesis=None, synthesis_method=None, mechanism=None
    ))
    for r in results:
        assert r.get('Tc', 0) >= tc_min

def test_query_by_tc_max():
    entries = qdb.load_database(qdb.DATABASE_PATH)
    tc_max = 50
    results = qdb.query(entries, argparse.Namespace(
        name=None, tc_min=None, tc_max=tc_max, pressure=None,
        pressure_min=None, pressure_max=None, composition=None,
        synthesis=None, synthesis_method=None, mechanism=None
    ))
    for r in results:
        assert r.get('Tc', 0) <= tc_max

def test_query_no_match():
    entries = qdb.load_database(qdb.DATABASE_PATH)
    results = qdb.query(entries, argparse.Namespace(
        name="NonExistentMaterial", tc_min=None, tc_max=None, pressure=None,
        pressure_min=None, pressure_max=None, composition=None,
        synthesis=None, synthesis_method=None, mechanism=None
    ))
    assert results == []

def test_query_by_feasibility_score():
    mock_db = [
        {"name": "A", "Tc": 50, "feasibility_score": 0.9, "material_class": "cuprate"},
        {"name": "B", "Tc": 150, "feasibility_score": 0.3, "material_class": "iron-based"},
        {"name": "C", "Tc": 200, "feasibility_score": 0.7, "material_class": "cuprate"},
    ]
    results = qdb.query(mock_db, argparse.Namespace(
        name=None, tc_min=None, tc_max=None, pressure=None,
        pressure_min=None, pressure_max=None, composition=None,
        synthesis=None, synthesis_method=None, mechanism=None,
        feasibility_score_min=0.5, feasibility_score_max=None,
        material_class=None
    ))
    assert len(results) == 2
    for r in results:
        assert r['feasibility_score'] >= 0.5

def test_query_by_material_class():
    mock_db = [
        {"name": "A", "Tc": 50, "feasibility_score": 0.9, "material_class": "cuprate"},
        {"name": "B", "Tc": 150, "feasibility_score": 0.3, "material_class": "iron-based"},
        {"name": "C", "Tc": 200, "feasibility_score": 0.7, "material_class": "cuprate"},
    ]
    results = qdb.query(mock_db, argparse.Namespace(
        name=None, tc_min=None, tc_max=None, pressure=None,
        pressure_min=None, pressure_max=None, composition=None,
        synthesis=None, synthesis_method=None, mechanism=None,
        feasibility_score_min=None, feasibility_score_max=None,
        material_class="cuprate"
    ))
    assert len(results) == 2
    for r in results:
        assert r['material_class'] == "cuprate"

def test_query_combined_filters():
    mock_db = [
        {"name": "A", "Tc": 50, "feasibility_score": 0.9, "material_class": "cuprate"},
        {"name": "B", "Tc": 150, "feasibility_score": 0.3, "material_class": "iron-based"},
        {"name": "C", "Tc": 200, "feasibility_score": 0.7, "material_class": "cuprate"},
        {"name": "D", "Tc": 120, "feasibility_score": 0.6, "material_class": "cuprate"},
    ]
    results = qdb.query(mock_db, argparse.Namespace(
        name=None, tc_min=100, tc_max=None, pressure=None,
        pressure_min=None, pressure_max=None, composition=None,
        synthesis=None, synthesis_method=None, mechanism=None,
        feasibility_score_min=0.5, feasibility_score_max=None,
        material_class="cuprate"
    ))
    assert len(results) == 2
    for r in results:
        assert r['Tc'] >= 100
        assert r['feasibility_score'] >= 0.5
        assert r['material_class'] == "cuprate"



def test_load_database_json_decode_error():
    with patch('builtins.open', MagicMock(side_effect=json.JSONDecodeError("", "", 0))):
        with pytest.raises(json.JSONDecodeError):
            qdb.load_database("dummy.json")

def test_query_empty_database():
    results = qdb.query([], argparse.Namespace(
        name=None, tc_min=None, tc_max=None, pressure=None,
        pressure_min=None, pressure_max=None, composition=None,
        synthesis=None, synthesis_method=None, mechanism=None,
        feasibility_score_min=None, feasibility_score_max=None,
        material_class=None
    ))
    assert results == []

def test_query_pressure_min_max():
    mock_db = [
        {"name": "A", "Tc": 50, "pressure": 10},
        {"name": "B", "Tc": 150, "pressure": 100},
        {"name": "C", "Tc": 200, "pressure": 200},
    ]
    results = qdb.query(mock_db, argparse.Namespace(
        name=None, tc_min=None, tc_max=None, pressure=None,
        pressure_min=50, pressure_max=150, composition=None,
        synthesis=None, synthesis_method=None, mechanism=None,
        feasibility_score_min=None, feasibility_score_max=None,
        material_class=None
    ))
    assert len(results) == 1
    assert results[0]["name"] == "B"

def test_query_type_mismatch_tc_min():
    mock_db = [{"name": "A", "Tc": 50}]
    with pytest.raises(TypeError):
        qdb.query(mock_db, argparse.Namespace(
            name=None, tc_min="low", tc_max=None, pressure=None,
            pressure_min=None, pressure_max=None, composition=None,
            synthesis=None, synthesis_method=None, mechanism=None,
            feasibility_score_min=None, feasibility_score_max=None,
            material_class=None
        ))

def test_query_synthesis_method_filter():
    mock_db = [
        {"name": "A", "Tc": 50, "synthesis_method": "CVD"},
        {"name": "B", "Tc": 150, "synthesis_method": "HPHT"},
        {"name": "C", "Tc": 200, "synthesis_method": "CVD"},
    ]
    results = qdb.query(mock_db, argparse.Namespace(
        name=None, tc_min=None, tc_max=None, pressure=None,
        pressure_min=None, pressure_max=None, composition=None,
        synthesis=None, synthesis_method="CVD", mechanism=None,
        feasibility_score_min=None, feasibility_score_max=None,
        material_class=None
    ))
    assert len(results) == 2
    for r in results:
        assert r["synthesis_method"] == "CVD"


def test_load_database_permission_error():
    from unittest.mock import patch, MagicMock
    with patch('builtins.open', MagicMock(side_effect=PermissionError("Permission denied"))):
        with pytest.raises(PermissionError):
            qdb.load_database("dummy.json")


def test_query_missing_tc_key():
    mock_db = [{"name": "A", "pressure": 10}]
    results = qdb.query(mock_db, argparse.Namespace(
        name=None, tc_min=None, tc_max=None, pressure=None,
        pressure_min=None, pressure_max=None, composition=None,
        synthesis=None, synthesis_method=None, mechanism=None,
        feasibility_score_min=None, feasibility_score_max=None,
        material_class=None
    ))
    assert len(results) == 1


def test_query_invalid_pressure_min_type():
    mock_db = [{"name": "A", "Tc": 50, "pressure": 10}]
    with pytest.raises(TypeError):
        qdb.query(mock_db, argparse.Namespace(
            name=None, tc_min=None, tc_max=None, pressure=None,
            pressure_min="low", pressure_max=None, composition=None,
            synthesis=None, synthesis_method=None, mechanism=None,
            feasibility_score_min=None, feasibility_score_max=None,
            material_class=None
        ))


def test_query_invalid_feasibility_score_min_type():
    mock_db = [{"name": "A", "Tc": 50, "feasibility_score": 0.9}]
    with pytest.raises(TypeError):
        qdb.query(mock_db, argparse.Namespace(
            name=None, tc_min=None, tc_max=None, pressure=None,
            pressure_min=None, pressure_max=None, composition=None,
            synthesis=None, synthesis_method=None, mechanism=None,
            feasibility_score_min="high", feasibility_score_max=None,
            material_class=None
        ))


def test_query_invalid_material_class_type():
    mock_db = [{"name": "A", "Tc": 50, "material_class": "cuprate"}]
    with pytest.raises(TypeError):
        qdb.query(mock_db, argparse.Namespace(
            name=None, tc_min=None, tc_max=None, pressure=None,
            pressure_min=None, pressure_max=None, composition=None,
            synthesis=None, synthesis_method=None, mechanism=None,
            feasibility_score_min=None, feasibility_score_max=None,
            material_class=123
        ))
