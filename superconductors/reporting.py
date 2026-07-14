"""Small report renderers for screened candidates."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


def format_candidate_table(candidates: Iterable[Mapping[str, Any]]) -> str:
    values = list(candidates)
    if not values:
        return ""
    rows = [
        "| Formula | Tc (K) | Pressure (GPa) | Evidence | Verification | Source |",
        "|---|---:|---:|---|---|---|",
    ]
    for candidate in values:
        rows.append(
            "| {formula} | {tc} | {pressure} | {evidence} | {verification} | {source} |".format(
                formula=_markdown_cell(candidate.get("formula", candidate.get("name", ""))),
                tc=_markdown_cell(candidate.get("tc", candidate.get("Tc", ""))),
                pressure=_markdown_cell(candidate.get("pressure", "")),
                evidence=_markdown_cell(candidate.get("evidence_type", "unclassified")),
                verification=_markdown_cell(candidate.get("verification_status", "unverified")),
                source=_markdown_cell(candidate.get("source", "unspecified")),
            )
        )
    return "\n".join(rows)


def _markdown_cell(value: Any) -> str:
    """Keep supplied values inside one Markdown table cell."""
    return (
        str(value if value is not None else "")
        .replace("|", "\\|")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def generate_report(candidates: Iterable[Mapping[str, Any]]) -> str:
    values = list(candidates)
    if not values:
        return "# Candidate Screening Report\n\nNo candidates matched the screening criteria.\n"
    return (
        "# Candidate Screening Report\n\n"
        "Values retain their supplied provenance. Predictions and simulations are not "
        "experimental confirmation.\n\n"
        f"{format_candidate_table(values)}\n"
    )


def write_markdown(content: str, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_pdf(content: str, output_path: str | Path) -> Path:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError('Install PDF support with: pip install -e ".[reports]"') from exc

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    document = canvas.Canvas(str(path), pagesize=letter)
    _, page_height = letter
    y = page_height - 50
    for line in content.splitlines() or [""]:
        if y < 50:
            document.showPage()
            y = page_height - 50
        document.drawString(50, y, line[:110])
        y -= 14
    document.save()
    return path
