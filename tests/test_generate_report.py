import pytest

from superconductors.reporting import (
    format_candidate_table,
    generate_report,
    write_markdown,
    write_pdf,
)


def test_report_includes_candidates_and_provenance_warning():
    report = generate_report([{"formula": "H3S", "tc": 203, "pressure": 155, "source": "measured"}])
    assert "H3S" in report
    assert "experimental confirmation" in report


def test_empty_report_is_explicit():
    assert "No candidates" in generate_report([])
    assert format_candidate_table([]) == ""


def test_markdown_table_has_stable_headers():
    table = format_candidate_table([{"formula": "MgB2", "tc": 39, "pressure": 0}])
    assert "| Formula | Tc (K) | Pressure (GPa) | Evidence | Verification | Source |" in table


def test_markdown_table_escapes_cell_separators_and_newlines():
    table = format_candidate_table([{"formula": "A|B", "tc": None, "source": "paper\nappendix"}])
    assert "A\\|B" in table
    assert "paper appendix" in table
    assert "None" not in table


def test_write_markdown_creates_parent_directory(tmp_path):
    path = write_markdown("report", tmp_path / "nested" / "report.md")
    assert path.read_text(encoding="utf-8") == "report"


def test_write_pdf_creates_a_pdf(tmp_path):
    pytest.importorskip("reportlab")
    path = write_pdf("Candidate report\nH3S: 203 K", tmp_path / "nested" / "report.pdf")
    assert path.read_bytes().startswith(b"%PDF")
