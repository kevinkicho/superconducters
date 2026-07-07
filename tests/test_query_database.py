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

