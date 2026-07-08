#!/usr/bin/env python3
"""
Automated literature mining module for room-temperature superconductivity research.

Fetches recent papers from arXiv API, parses abstracts to extract structured data
(material, Tc, pressure), and updates docs/online_research_summary.md.

Usage:
    python scripts/arxiv_scraper.py [--max-results 20] [--query "superconductivity"]
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

# Constants
ARXIV_API_URL = "http://export.arxiv.org/api/query"
DEFAULT_QUERY = "superconductivity room temperature"
DEFAULT_MAX_RESULTS = 10
SUMMARY_FILE = os.path.join(
    os.path.dirname(__file__), "..", "docs", "online_research_summary.md"
)

# Patterns for extracting material, Tc, pressure
MATERIAL_PATTERN = re.compile(
    r"(?:[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*)"  # simple chemical formula
    r"|(?:[A-Z][a-z]?\d*(?:_[A-Z][a-z]?\d*)*)"  # with underscores
)
TC_PATTERN = re.compile(
    r"(?:Tc|T_c|transition temperature|superconducting transition)"
    r"\s*(?:of|at|~|≈|:)?\s*(\d+(?:\.\d+)?)\s*(?:K|kelvin)",
    re.IGNORECASE
)
PRESSURE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:GPa|gigapascal|Mbar|megabar)",
    re.IGNORECASE
)


def fetch_papers(
    query: str, max_results: int = 10, start: int = 0
) -> List[Dict[str, Any]]:
    """
    Fetch papers from arXiv API.

    Args:
        query: Search query string.
        max_results: Number of results to fetch.
        start: Starting index for pagination.

    Returns:
        List of paper dictionaries with keys: id, title, summary, published, authors, link.
    """
    params = {
        "search_query": f"all:{query}",
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    headers = {
        "User-Agent": (
            "RoomTempSuperconductorResearch/1.0 (mailto:research@example.com)"
        )
    }

    try:
        response = requests.get(
            ARXIV_API_URL, params=params, headers=headers, timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching papers: {e}", file=sys.stderr)
        return []

    root = ET.fromstring(response.content)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    papers = []
    for entry in root.findall("atom:entry", ns):
        paper = {}
        id_elem = entry.find("atom:id", ns)
        paper["id"] = id_elem.text.strip() if id_elem is not None else ""
        title_elem = entry.find("atom:title", ns)
        paper["title"] = title_elem.text.strip().replace("\n", " ") if title_elem is not None else ""
        summary_elem = entry.find("atom:summary", ns)
        paper["summary"] = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""
        paper["published"] = entry.find("atom:published", ns).text.strip() if entry.find("atom:published", ns) is not None else ""
        paper["link"] = entry.find("atom:link", ns).attrib.get("href", "") if entry.find("atom:link", ns) is not None else ""
        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns)
            if name is not None:
                authors.append(name.text.strip())
        paper["authors"] = authors
        papers.append(paper)

    return papers


def extract_entities(abstract: str) -> Dict[str, Any]:
    """
    Extract material, Tc, and pressure from an abstract.

    Args:
        abstract: Paper abstract text.

    Returns:
        Dictionary with keys: materials (list), tc_values (list of floats), pressure_values (list of floats).
    """
    entities: Dict[str, Any] = {
        "materials": [],
        "tc_values": [],
        "pressure_values": [],
    }

    # Extract Tc values
    for match in TC_PATTERN.finditer(abstract):
        try:
            tc = float(match.group(1))
            entities["tc_values"].append(tc)
        except ValueError:
            continue

    # Extract pressure values
    for match in PRESSURE_PATTERN.finditer(abstract):
        try:
            pressure = float(match.group(1))
            entities["pressure_values"].append(pressure)
        except ValueError:
            continue

    # Extract material names (simple heuristic: capitalized chemical formulas)
    # This is a basic pattern; more sophisticated NER could be added.
    material_candidates = MATERIAL_PATTERN.findall(abstract)
    # Filter to likely chemical formulas (e.g., LaH10, H3S, YBCO)
    for candidate in material_candidates:
        if re.match(r"^[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*$", candidate):
            if len(candidate) >= 2 and candidate not in entities["materials"]:
                entities["materials"].append(candidate)

    return entities


def format_paper_entry(paper: Dict[str, Any], entities: Dict[str, Any]) -> str:
    """
    Format a paper entry for the summary markdown.

    Args:
        paper: Paper dictionary.
        entities: Extracted entities.

    Returns:
        Markdown string.
    """
    lines = []
    lines.append(f"- **{paper['title']}**")
    lines.append(f"  - Authors: {', '.join(paper['authors'][:5])}{' et al.' if len(paper['authors']) > 5 else ''}")
    lines.append(f"  - Published: {paper['published'][:10]}")
    lines.append(f"  - arXiv: [{paper['id']}]({paper['link']})")
    if entities["materials"]:
        lines.append(f"  - Materials: {', '.join(entities['materials'])}")
    if entities["tc_values"]:
        lines.append(f"  - Tc values (K): {', '.join(f'{tc:.1f}' for tc in entities['tc_values'])}")
    if entities["pressure_values"]:
        lines.append(f"  - Pressure (GPa): {', '.join(f'{p:.0f}' for p in entities['pressure_values'])}")
    lines.append("")
    return "\n".join(lines)


def update_summary(papers: List[Dict[str, Any]], query: str) -> None:
    """
    Append new papers to the summary markdown file.

    Args:
        papers: List of paper dictionaries.
        query: Search query used.
    """
    if not papers:
        print("No papers to add.")
        return

    summary_path = os.path.abspath(SUMMARY_FILE)
    if not os.path.exists(summary_path):
        print(f"Summary file not found: {summary_path}", file=sys.stderr)
        return

    # Build new section
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    section_lines = [
        f"\n## Automated Literature Mining Results (fetched {now})",
        f"\nQuery: `{query}`",
        "\n### New Papers",
    ]
    for paper in papers:
        entities = extract_entities(paper["summary"])
        section_lines.append(format_paper_entry(paper, entities))

    section_text = "\n".join(section_lines)

    try:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(section_text)
        print(f"Appended {len(papers)} papers to {summary_path}")
    except IOError as e:
        print(f"Error writing to summary file: {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated literature mining for superconductivity research.")
    parser.add_argument("--query", type=str, default=DEFAULT_QUERY,
                        help=f"Search query (default: '{DEFAULT_QUERY}')")
    parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS,
                        help=f"Maximum number of results to fetch (default: {DEFAULT_MAX_RESULTS})")
    parser.add_argument("--start", type=int, default=0,
                        help="Start index for pagination (default: 0)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON file for raw data (optional)")
    parser.add_argument("--no-update", action="store_true",
                        help="Do not update the summary markdown file")
    parser.add_argument("--extract-candidates", action="store_true",
                        help="Extract candidate materials and append to database and candidates file")
    args = parser.parse_args()

    if args.extract_candidates:
        extract_candidates_from_paper(args.query, args.max_results)
        return

    print(f"Fetching up to {args.max_results} papers for query: '{args.query}'...")
    papers = fetch_papers(args.query, args.max_results, args.start)
    print(f"Fetched {len(papers)} papers.")

    if not papers:
        sys.exit(0)

    # Extract entities and print summary
    for paper in papers:
        entities = extract_entities(paper["summary"])
        print(f"\n--- {paper['title'][:80]}... ---")
        print(f"  Materials: {entities['materials']}")
        print(f"  Tc values: {entities['tc_values']}")
        print(f"  Pressure: {entities['pressure_values']}")

    # Save raw data if requested
    if args.output:
        output_data = []
        for paper in papers:
            entry = {
                "id": paper["id"],
                "title": paper["title"],
                "summary": paper["summary"],
                "published": paper["published"],
                "authors": paper["authors"],
                "link": paper["link"],
                "entities": extract_entities(paper["summary"]),
            }
            output_data.append(entry)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
        print(f"Saved raw data to {args.output}")

    # Update summary file
    if not args.no_update:
        update_summary(papers, args.query)

    print("\nDone.")


def extract_candidates_from_paper(query: str = DEFAULT_QUERY, max_results: int = DEFAULT_MAX_RESULTS) -> None:
    """
    Fetch recent papers from arXiv, parse for material compositions and Tc values,
    and append new candidate entries to candidate_materials.md and data/superconductor_database.json.
    """
    papers = fetch_papers(query, max_results)
    if not papers:
        print("No papers fetched.", file=sys.stderr)
        return

    # Paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates_path = os.path.join(script_dir, "..", "candidate_materials.md")
    database_path = os.path.join(script_dir, "..", "data", "superconductor_database.json")

    # Load existing database to avoid duplicates
    existing_entries = []
    if os.path.exists(database_path):
        try:
            with open(database_path, "r", encoding="utf-8") as f:
                existing_entries = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing_entries = []

    existing_ids = {entry.get("id") for entry in existing_entries if "id" in entry}
    existing_formulas = {entry.get("formula", "").strip().lower() for entry in existing_entries}

    new_entries = []
    new_candidate_lines = []

    for paper in papers:
        entities = extract_entities(paper["summary"])
        materials = entities["materials"]
        tc_values = entities["tc_values"]
        pressure_values = entities["pressure_values"]

        if not materials or not tc_values:
            continue

        # Use the first material and first Tc as primary
        primary_material = materials[0] if materials else ""
        primary_tc = tc_values[0] if tc_values else None
        primary_pressure = pressure_values[0] if pressure_values else None

        # Check for duplicates by arXiv ID
        paper_id = paper["id"]
        if paper_id in existing_ids:
            continue

        # Also check by formula (case-insensitive)
        formula_lower = primary_material.strip().lower()
        if formula_lower in existing_formulas:
            continue

        # Build database entry
        entry = {
            "id": paper_id,
            "title": paper["title"],
            "formula": primary_material,
            "tc": primary_tc,
            "pressure": primary_pressure,
            "source": paper["link"],
            "summary": paper["summary"][:500],
            "date_added": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }
        new_entries.append(entry)
        existing_ids.add(paper_id)
        existing_formulas.add(formula_lower)

        # Build candidate_materials.md entry
        candidate_line = (
            f"\n### {primary_material}\n"
            f"- **Predicted Tc**: {primary_tc} K\n"
            f"- **Pressure**: {primary_pressure} GPa\n"
            f"- **Source**: [{paper['title'][:80]}]({paper['link']})\n"
            f"- **Date added**: {entry['date_added']}\n"
        )
        new_candidate_lines.append(candidate_line)

    if not new_entries:
        print("No new candidates found.")
        return

    # Append to database
    existing_entries.extend(new_entries)
    try:
        with open(database_path, "w", encoding="utf-8") as f:
            json.dump(existing_entries, f, indent=2)
        print(f"Added {len(new_entries)} new entries to {database_path}")
    except IOError as e:
        print(f"Error writing to database: {e}", file=sys.stderr)

    # Append to candidate_materials.md
    try:
        with open(candidates_path, "a", encoding="utf-8") as f:
            f.write("\n".join(new_candidate_lines))
        print(f"Appended {len(new_candidate_lines)} candidates to {candidates_path}")
    except IOError as e:
        print(f"Error writing to candidates file: {e}", file=sys.stderr)

    # Append to docs/online_research_summary.md
    try:
        with open(SUMMARY_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(new_candidate_lines))
        print(f"Appended {len(new_candidate_lines)} entries to {SUMMARY_FILE}")
    except IOError as e:
        print(f"Error writing to summary file: {e}", file=sys.stderr)

    # Trigger retraining of ML model
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "predict_tc.py")],
            capture_output=True, text=True, timeout=300
        )
        print(f"Retraining output: {result.stdout}")
        if result.returncode != 0:
            print(f"Retraining error: {result.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"Error triggering retraining: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
