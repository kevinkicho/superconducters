import pytest
import scripts.query_database as qdb

def test_query_database_function_exists():
    assert callable(qdb.query_database)

def test_query_database_returns_list():
    result = qdb.query_database()
    assert isinstance(result, list)

def test_query_database_returns_non_empty():
    result = qdb.query_database()
    assert len(result) > 0
