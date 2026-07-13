import pytest

from superconductors.integrations import (
    IntegrationError,
    fetch_paper_details,
    parse_arxiv_feed,
    search_arxiv,
)

ATOM_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>https://arxiv.org/abs/1234.5678</id>
    <published>2026-01-02T00:00:00Z</published>
    <title>  Test   superconductor paper </title>
    <summary> A useful abstract. </summary>
    <author><name>Ada Researcher</name></author>
  </entry>
</feed>
"""


def test_parse_arxiv_feed_normalizes_entry():
    paper = parse_arxiv_feed(ATOM_FEED)[0]
    assert paper["title"] == "Test superconductor paper"
    assert paper["authors"] == ["Ada Researcher"]
    assert paper["url"].endswith("1234.5678")


def test_search_arxiv_uses_injected_transport():
    urls = []

    def transport(url):
        urls.append(url)
        return ATOM_FEED

    assert len(search_arxiv("superconductor", max_results=1, transport=transport)) == 1
    assert "max_results=1" in urls[0]


def test_empty_search_does_not_call_transport():
    assert search_arxiv("", transport=lambda _: pytest.fail("transport called")) == []


def test_transport_errors_have_stable_exception():
    def failed_transport(_):
        raise OSError("offline")

    with pytest.raises(IntegrationError, match="arXiv request failed"):
        search_arxiv("superconductor", transport=failed_transport)


def test_fetch_paper_details_returns_first_result():
    paper = fetch_paper_details("1234.5678", transport=lambda _: ATOM_FEED)
    assert paper["title"] == "Test superconductor paper"


def test_fetch_paper_details_returns_none_for_empty_feed():
    empty_feed = b'<feed xmlns="http://www.w3.org/2005/Atom" />'
    assert fetch_paper_details("1234.5678", transport=lambda _: empty_feed) is None
