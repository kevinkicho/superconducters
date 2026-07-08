import pytest
from scripts.generate_report import generate_report, format_candidate_table, write_pdf

def test_generate_report_returns_string():
    candidates = [{"formula": "H3S", "tc": 203, "pressure": 150}]
    report = generate_report(candidates)
    assert isinstance(report, str)
    assert "H3S" in report

def test_format_candidate_table_contains_headers():
    candidates = [
        {"formula": "A", "tc": 100, "pressure": 50},
        {"formula": "B", "tc": 200, "pressure": 100},
    ]
    table = format_candidate_table(candidates)
    assert "Formula" in table
    assert "Tc (K)" in table
    assert "Pressure (GPa)" in table

def test_format_candidate_table_handles_empty():
    table = format_candidate_table([])
    assert table == ""

def test_write_pdf_creates_file(tmp_path):
    content = "Test report content"
    output_path = tmp_path / "report.pdf"
    write_pdf(content, str(output_path))
    assert output_path.exists()
    assert output_path.stat().st_size > 0
