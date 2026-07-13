from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from superconductors.integrations import IntegrationError, fetch_icsd, fetch_materials_project


def test_materials_project_maps_summary_documents():
    summary = SimpleNamespace(
        search=lambda **_: [
            SimpleNamespace(
                material_id="mp-1",
                formula_pretty="H3S",
                band_gap=0.0,
                energy_above_hull=0.01,
            )
        ]
    )
    client = SimpleNamespace(materials=SimpleNamespace(summary=summary))

    results = fetch_materials_project("key", "H3S", client_factory=lambda _: nullcontext(client))

    assert results[0]["material_id"] == "mp-1"
    assert results[0]["source"] == "Materials Project"


def test_invalid_formula_skips_materials_project_client():
    assert fetch_materials_project("key", "InvalidFormula", client_factory=None) == []


def test_materials_project_errors_are_wrapped():
    def failed_factory(_):
        raise OSError("offline")

    with pytest.raises(IntegrationError, match="Materials Project"):
        fetch_materials_project("key", "H3S", client_factory=failed_factory)


def test_icsd_requires_explicit_configuration():
    with pytest.raises(IntegrationError, match="ICSD_API_URL"):
        fetch_icsd("key", "LaH10", endpoint=None)


def test_icsd_uses_injected_transport():
    def transport(url, headers):
        assert "formula=LaH10" in url
        assert headers["Authorization"] == "Bearer key"
        return {"data": [{"icsd_id": 123, "formula": "LaH10"}]}

    assert fetch_icsd("key", "LaH10", endpoint="https://example.test", transport=transport) == [
        {"icsd_id": 123, "formula": "LaH10"}
    ]
