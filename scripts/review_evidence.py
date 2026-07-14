#!/usr/bin/env python3
"""Record a source-reviewed evidence classification without editing legacy data."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from superconductors.config import Settings
from superconductors.evidence import EVIDENCE_TYPES, VERIFICATION_STATUSES
from superconductors.evidence_reviews import EvidenceReviewLedger
from superconductors.query import load_database


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record_index", type=int)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--primary-source", required=True)
    parser.add_argument("--evidence-type", required=True, choices=sorted(EVIDENCE_TYPES))
    parser.add_argument(
        "--verification-status", required=True, choices=sorted(VERIFICATION_STATUSES)
    )
    parser.add_argument("--rationale", required=True)
    args = parser.parse_args(argv)
    settings = Settings.from_env()
    ledger = EvidenceReviewLedger(settings.output_dir / "evidence_reviews.json")
    review = ledger.review(
        load_database(),
        record_index=args.record_index,
        reviewer=args.reviewer,
        primary_source=args.primary_source,
        evidence_type=args.evidence_type,
        verification_status=args.verification_status,
        rationale=args.rationale,
    )
    print(json.dumps({"review": asdict(review)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
