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
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

# Constants
ARXIV_API_URL = "http://export.arxiv.org/api/query"
DEFAULT_QUERY = "superconductivity room temperature"
DEFAULT_MAX_RESULTS = 10
SUMMARY_FILE = os.path.join(os.path.dirname(__file__), "..", "docs", "online_research_summary.md")

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


def fetch_papers(query: str, max_results: int = 10, start: int = 0) -> List[Dict[str, Any]]:
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
        "User-Agent": "RoomTempSuperconductorResearch/1.0 (mailto:research@example.com)"
    }

    try:
        response = requests.get(ARXIV_API_URL, params=params, headers=headers, timeout=30)
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
        paper["id"] = entry.find("atom:id", ns).text.strip() if entry.find("atom:id", ns) is not None else ""
        paper["title"] = entry.find("atom:title", ns).text.strip().replace("\n", " ") if entry.find("atom:title", ns) is not None else ""
        paper["summary"] = entry.find("atom:summary", ns).text.strip().replace("\n", " ") if entry.find("atom:summary", ns) is not None else ""
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
    args = parser.parse_args()

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


if __name__ == "__main__":
    main()
