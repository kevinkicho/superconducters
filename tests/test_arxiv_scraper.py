import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from unittest.mock import patch, MagicMock
import scripts.arxiv_scraper as arx


def test_search_arxiv_success():
    """Test that search_arxiv returns parsed results."""
    mock_entry = MagicMock()
    mock_entry.title = "Test Title"
    mock_entry.authors = [MagicMock(name="Author1")]
    mock_entry.summary = "Test abstract"
    mock_entry.entry_id = "http://arxiv.org/abs/1234.56789v1"
    with patch('scripts.arxiv_scraper.arxiv.Search') as mock_search:
        mock_search.return_value.results.return_value = [mock_entry]
        results = arx.search_arxiv("superconductor", max_results=1)
        assert len(results) == 1
        assert results[0]['title'] == "Test Title"
        assert results[0]['authors'] == ["Author1"]
        assert results[0]['abstract'] == "Test abstract"
        assert results[0]['url'] == "http://arxiv.org/abs/1234.56789v1"


def test_search_arxiv_no_results():
    """Test that search_arxiv returns empty list when no results."""
    with patch('scripts.arxiv_scraper.arxiv.Search') as mock_search:
        mock_search.return_value.results.return_value = []
        results = arx.search_arxiv("nonexistent", max_results=10)
        assert results == []


def test_search_arxiv_network_error():
    """Test that search_arxiv raises exception on network error."""
    with patch('scripts.arxiv_scraper.arxiv.Search', side_effect=Exception("Network error")):
        with pytest.raises(Exception):
            arx.search_arxiv("superconductor")


def test_fetch_paper_details_success():
    """Test fetch_paper_details returns parsed details."""
    mock_entry = MagicMock()
    mock_entry.title = "Detail Title"
    mock_entry.authors = [MagicMock(name="Author2")]
    mock_entry.summary = "Detail abstract"
    mock_entry.entry_id = "http://arxiv.org/abs/5678.12345v2"
    with patch('scripts.arxiv_scraper.arxiv.Search') as mock_search:
        mock_search.return_value.results.return_value = [mock_entry]
        details = arx.fetch_paper_details("5678.12345")
        assert details['title'] == "Detail Title"
        assert details['authors'] == ["Author2"]
        assert details['abstract'] == "Detail abstract"
        assert details['url'] == "http://arxiv.org/abs/5678.12345v2"


def test_fetch_paper_details_not_found():
    """Test fetch_paper_details returns None or raises when not found."""
    with patch('scripts.arxiv_scraper.arxiv.Search') as mock_search:
        mock_search.return_value.results.return_value = []
        result = arx.fetch_paper_details("0000.00000")
        assert result is None


def test_parse_arxiv_entry():
    """Test parse_arxiv_entry returns correct dict."""
    mock_entry = MagicMock()
    mock_entry.title = "Parsed Title"
    mock_entry.authors = [MagicMock(name="Author3"), MagicMock(name="Author4")]
    mock_entry.summary = "Parsed abstract"
    mock_entry.entry_id = "http://arxiv.org/abs/9999.88888v3"
    result = arx.parse_arxiv_entry(mock_entry)
    assert result['title'] == "Parsed Title"
    assert result['authors'] == ["Author3", "Author4"]
    assert result['abstract'] == "Parsed abstract"
    assert result['url'] == "http://arxiv.org/abs/9999.88888v3"


def test_parse_arxiv_entry_empty_authors():
    """Test parse_arxiv_entry handles empty authors list."""
    mock_entry = MagicMock()
    mock_entry.title = "No Authors"
    mock_entry.authors = []
    mock_entry.summary = "Abstract"
    mock_entry.entry_id = "http://arxiv.org/abs/1111.22222"
    result = arx.parse_arxiv_entry(mock_entry)
    assert result['authors'] == []
