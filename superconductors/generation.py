"""Transparent candidate proposal helpers.

Candidate templates are hypothesis prompts. They are not novel-material claims.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .prediction import predict

HYDRIDE_TEMPLATES: tuple[tuple[str, float], ...] = (
    ("H3S", 155.0),
    ("LaH10", 170.0),
    ("YH6", 166.0),
    ("CeH9", 100.0),
    ("ThH10", 175.0),
)


def generate_candidates(limit: int = 5) -> list[dict[str, Any]]:
    if limit < 0:
        raise ValueError("Limit cannot be negative")
    candidates = []
    for formula, pressure in HYDRIDE_TEMPLATES[:limit]:
        estimate = predict(formula)
        candidates.append(
            {
                "formula": formula,
                "tc": round(estimate.tc, 2),
                "pressure": pressure,
                "source": "curated-template",
                "prediction_method": estimate.method,
            }
        )
    return candidates


def filter_candidates(
    candidates: Iterable[Mapping[str, Any]],
    *,
    min_tc: float | None = None,
    max_pressure: float | None = None,
) -> list[dict[str, Any]]:
    selected = []
    for candidate in candidates:
        formula = candidate.get("formula")
        tc = _number(candidate.get("tc", candidate.get("Tc")))
        pressure = _number(candidate.get("pressure"))
        if not isinstance(formula, str) or not formula.strip() or tc is None:
            continue
        if min_tc is not None and tc < min_tc:
            continue
        if max_pressure is not None and (pressure is None or pressure > max_pressure):
            continue
        selected.append(dict(candidate))
    return selected


def rank_candidates(candidates: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    values = [dict(candidate) for candidate in candidates]
    return sorted(
        values,
        key=lambda candidate: _number(candidate.get("tc", candidate.get("Tc")), float("-inf")),
        reverse=True,
    )


def _number(value: Any, default: float | None = None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
