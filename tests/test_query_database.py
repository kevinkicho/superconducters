import pytest
import scripts.query_database as qdb

def test_query_database_h3s():
    results = qdb.query_database(material="H3S")
    assert isinstance(results, list)
    assert len(results) > 0
    for r in results:
        assert "material" in r
        assert "tc" in r
        assert "pressure" in r
    h3s_entries = [r for r in results if r["material"] == "H3S"]
    assert len(h3s_entries) > 0
    tc_values = [r["tc"] for r in h3s_entries]
    assert any(180 <= tc <= 220 for tc in tc_values)

def test_query_database_lah10():
    results = qdb.query_database(material="LaH10")
    assert isinstance(results, list)
    assert len(results) > 0
    lah10_entries = [r for r in results if r["material"] == "LaH10"]
    assert len(lah10_entries) > 0
    tc_values = [r["tc"] for r in lah10_entries]
    assert any(230 <= tc <= 270 for tc in tc_values)

def test_query_database_all():
    results = qdb.query_database()
    assert isinstance(results, list)
    assert len(results) > 0

def test_query_database_invalid_material():
    results = qdb.query_database(material="NonExistent")
    assert results == []
