"""Adapters for external literature and materials services."""

from __future__ import annotations

import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from typing import Any, Protocol

from .prediction import parse_formula

ARXIV_API_URL = "https://export.arxiv.org/api/query"


class IntegrationError(RuntimeError):
    """Raised when a configured external service cannot satisfy a request."""


class MaterialsSummaryClient(Protocol):
    def search(self, **kwargs: Any) -> list[Any]: ...


def search_arxiv(
    query: str,
    *,
    max_results: int = 10,
    transport: Callable[[str], bytes] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(query, str) or not query.strip() or max_results <= 0:
        return []
    parameters = urllib.parse.urlencode(
        {
            "search_query": f"all:{query.strip()}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    fetch = transport or _fetch_bytes
    try:
        return parse_arxiv_feed(fetch(f"{ARXIV_API_URL}?{parameters}"))
    except (OSError, TypeError, ET.ParseError) as exc:
        raise IntegrationError(f"arXiv request failed: {exc}") from exc


def fetch_paper_details(
    arxiv_id: str,
    *,
    transport: Callable[[str], bytes] | None = None,
) -> dict[str, Any] | None:
    if not isinstance(arxiv_id, str) or not arxiv_id.strip():
        return None
    parameters = urllib.parse.urlencode({"id_list": arxiv_id.strip(), "max_results": 1})
    fetch = transport or _fetch_bytes
    try:
        papers = parse_arxiv_feed(fetch(f"{ARXIV_API_URL}?{parameters}"))
    except (OSError, TypeError, ET.ParseError) as exc:
        raise IntegrationError(f"arXiv request failed: {exc}") from exc
    return papers[0] if papers else None


def parse_arxiv_feed(payload: bytes | str) -> list[dict[str, Any]]:
    root = ET.fromstring(payload)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    return [_parse_arxiv_entry(entry, namespace) for entry in root.findall("atom:entry", namespace)]


def fetch_materials_project(
    api_key: str,
    formula: str,
    *,
    max_results: int = 20,
    client_factory: Callable[[str], Any] | None = None,
) -> list[dict[str, Any]]:
    if not _valid_formula(formula) or max_results <= 0:
        return []
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("Materials Project API key is required")
    api_key = api_key.strip()
    factory = client_factory or _materials_project_client
    try:
        with factory(api_key) as client:
            documents = client.materials.summary.search(
                formula=formula,
                fields=["material_id", "formula_pretty", "band_gap", "energy_above_hull"],
            )
        if not isinstance(documents, list):
            raise IntegrationError("Materials Project response must contain a list")
        return [_material_document(document) for document in documents[:max_results]]
    except IntegrationError:
        raise
    except Exception as exc:
        raise IntegrationError(f"Materials Project request failed: {exc}") from exc


def fetch_icsd(
    api_key: str,
    formula: str,
    *,
    max_results: int = 20,
    endpoint: str | None = None,
    transport: Callable[[str, dict[str, str]], Any] | None = None,
) -> list[dict[str, Any]]:
    if not _valid_formula(formula) or max_results <= 0:
        return []
    endpoint = endpoint or os.getenv("ICSD_API_URL")
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise IntegrationError("ICSD_API_URL is not configured")
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("ICSD API key is required")
    endpoint = endpoint.strip()
    api_key = api_key.strip()
    fetch = transport or _fetch_json
    try:
        parameters = urllib.parse.urlencode({"formula": formula, "limit": max_results})
        payload = fetch(
            f"{endpoint.rstrip('/')}?{parameters}",
            {"Authorization": f"Bearer {api_key}"},
        )
    except Exception as exc:
        raise IntegrationError(f"ICSD request failed: {exc}") from exc
    records = payload.get("data", payload) if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise IntegrationError("ICSD response must contain a list")
    normalized = []
    for index, record in enumerate(records[:max_results]):
        if not isinstance(record, dict):
            raise IntegrationError(f"ICSD record at index {index} must be an object")
        normalized.append(dict(record))
    return normalized


def _parse_arxiv_entry(entry: ET.Element, namespace: dict[str, str]) -> dict[str, Any]:
    def text(tag: str) -> str:
        node = entry.find(f"atom:{tag}", namespace)
        return " ".join((node.text or "").split()) if node is not None else ""

    return {
        "title": text("title"),
        "authors": [
            " ".join((name.text or "").split())
            for author in entry.findall("atom:author", namespace)
            if (name := author.find("atom:name", namespace)) is not None
        ],
        "abstract": text("summary"),
        "url": text("id"),
        "published": text("published"),
    }


def _material_document(document: Any) -> dict[str, Any]:
    def value(name: str) -> Any:
        return (
            getattr(document, name, None) if not isinstance(document, dict) else document.get(name)
        )

    return {
        "material_id": str(value("material_id") or ""),
        "formula": value("formula_pretty") or "",
        "band_gap": value("band_gap"),
        "energy_above_hull": value("energy_above_hull"),
        "source": "Materials Project",
    }


def _valid_formula(formula: str) -> bool:
    try:
        parse_formula(formula)
    except (TypeError, ValueError):
        return False
    return True


def _fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "superconductors/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def _fetch_json(url: str, headers: dict[str, str]) -> Any:
    import json

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def _materials_project_client(api_key: str) -> Any:
    try:
        from mp_api.client import MPRester
    except ImportError as exc:
        raise IntegrationError(
            'Install Materials Project support with: pip install -e ".[dft]"'
        ) from exc
    return MPRester(api_key)
