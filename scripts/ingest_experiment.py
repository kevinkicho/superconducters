#!/usr/bin/env python3
"""Register a raw experimental artifact without claiming confirmation."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from superconductors.config import Settings
from superconductors.experiments import ExperimentLedger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_data")
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--formula", required=True)
    parser.add_argument("--laboratory", required=True)
    parser.add_argument("--pressure-gpa", required=True, type=float)
    parser.add_argument(
        "--measurement-type",
        required=True,
        choices=["resistivity", "susceptibility", "specific-heat", "xrd"],
    )
    parser.add_argument("--calibration-reference", required=True)
    parser.add_argument("--transition-k", type=float)
    parser.add_argument("--zero-resistance", action="store_true")
    parser.add_argument("--meissner-effect", action="store_true")
    args = parser.parse_args(argv)
    ledger = ExperimentLedger(Settings.from_env().output_dir / "experiment_ledger.json")
    record = ledger.ingest(
        sample_id=args.sample_id,
        formula=args.formula,
        laboratory=args.laboratory,
        pressure_gpa=args.pressure_gpa,
        measurement_type=args.measurement_type,
        raw_data_path=args.raw_data,
        calibration_reference=args.calibration_reference,
        observed_transition_k=args.transition_k,
        zero_resistance=args.zero_resistance,
        meissner_effect=args.meissner_effect,
    )
    print(json.dumps({"record": asdict(record)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
