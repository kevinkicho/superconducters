import pytest
from scripts.api_client import fetch_materials_project, fetch_icsd, fetch_arxiv

def test_fetch_materials_project_returns_dict():
    result = fetch_materials_project("H3S")
    assert isinstance(result, dict)
    assert "data" in result

def test_fetch_icsd_returns_list():
    result = fetch_icsd("LaH10")
    assert isinstance(result, list)

def test_fetch_arxiv_returns_papers():
    result = fetch_arxiv("room temperature superconductor")
    assert isinstance(result, list)
    assert len(result) > 0

def test_fetch_materials_project_handles_empty():
    result = fetch_materials_project("")
    assert result == {"data": []}

def test_fetch_icsd_handles_invalid():
    result = fetch_icsd("InvalidFormula")
    assert result == []


def test_fetch_materials_project_network_error():
    """Test fetch_materials_project raises exception on network error."""
    with patch('scripts.api_client.requests.get', side_effect=Exception("Network error")):
        with pytest.raises(Exception):
            fetch_materials_project("H3S")


def test_fetch_arxiv_handles_empty():
    """Test fetch_arxiv returns empty list for empty query."""
    result = fetch_arxiv("")
    assert result == []


def test_fetch_icsd_network_error():
    """Test fetch_icsd raises exception on network error."""
    with patch('scripts.api_client.requests.get', side_effect=Exception("Network error")):
        with pytest.raises(Exception):
            fetch_icsd("LaH10")
