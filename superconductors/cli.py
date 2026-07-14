"""Command-line entry point for the supported pipeline."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .evidence_audit import build_evidence_audit
from .objectives import DiscoveryObjective
from .pipeline import run_pipeline
from .query import load_database
from .validation import validate_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load, filter, and rank superconductor candidates."
    )
    parser.add_argument("--min-tc", type=float, default=None, help="Minimum measured Tc in kelvin")
    parser.add_argument("--max-pressure", type=float, default=None, help="Maximum pressure in GPa")
    parser.add_argument("--limit", type=int, default=20, help="Maximum candidates to return")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate database schema and provenance without modifying records",
    )
    parser.add_argument(
        "--objective",
        choices=["ambient-room-temperature"],
        help="Apply a named, evidence-aware discovery objective",
    )
    parser.add_argument(
        "--evidence-audit",
        choices=["all", "unclassified", "quarantined"],
        help="Print a read-only evidence review queue",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.evidence_audit:
        audit = build_evidence_audit(load_database(), scope=args.evidence_audit, limit=args.limit)
        if args.json:
            print(json.dumps(audit.to_dict(), indent=2))
        else:
            print(
                f"Audited {audit.records_checked} records; showing {len(audit.items)} "
                f"{audit.scope} review items."
            )
            print(
                "Classification counts: " + ", ".join(f"{k}={v}" for k, v in audit.counts.items())
            )
            for item in audit.items:
                print(
                    f"- record {item.record_index}: {item.material or '(unnamed)'}; "
                    f"Tc={item.tc}; pressure={item.pressure}; {item.reason}"
                )
        return 0
    if args.validate:
        report = validate_records(load_database())
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(
                f"Validated {report.records_checked} records: "
                f"{report.errors} errors, {report.warnings} warnings."
            )
            for issue in report.issues[:20]:
                print(f"- {issue.severity}: record {issue.record_index}: {issue.message}")
        return 0 if report.is_valid else 1
    result = run_pipeline(
        min_tc=273.15 if args.objective else args.min_tc,
        max_pressure=1.0 if args.objective else args.max_pressure,
        limit=args.limit,
    )
    if args.json:
        payload = result.to_dict()
        if args.objective:
            objective = DiscoveryObjective()
            payload["objective"] = objective.to_dict()
            payload["evaluations"] = [
                objective.evaluate(candidate).to_dict() for candidate in result.candidates
            ]
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Loaded {result.candidates_loaded} candidates; selected {result.candidates_selected}.")
    for index, candidate in enumerate(result.candidates, start=1):
        tc = f"{candidate.tc:g} K" if candidate.tc is not None else "unknown Tc"
        pressure = (
            f"{candidate.pressure:g} GPa" if candidate.pressure is not None else "unknown pressure"
        )
        print(f"{index:>2}. {candidate.formula:<20} {tc:<14} {pressure}")
    return 0
