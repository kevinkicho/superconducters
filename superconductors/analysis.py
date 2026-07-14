"""Optional analysis helpers with lightweight import behavior."""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from typing import Any

from .multifidelity import MultiFidelityGP

__all__ = [
    "MultiFidelityGP",
    "correlation_sensitivity_analysis",
    "sobol_sensitivity_analysis",
]

DEFAULT_BOUNDS: dict[str, tuple[float, float]] = {
    "pressure_GPa": (50, 300),
    "temperature_K": (300, 3000),
    "precursor_ratio": (0.5, 2.0),
    "annealing_time_hours": (0.5, 48),
}

_SURROGATE_WEIGHTS = {
    "pressure_GPa": 0.5,
    "temperature_K": 0.02,
    "precursor_ratio": 10.0,
    "annealing_time_hours": 0.5,
}


def correlation_sensitivity_analysis(
    parameters: Sequence[str] | None = None,
    *,
    samples: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    if samples < 3:
        raise ValueError("samples must be at least 3")
    names = list(parameters or DEFAULT_BOUNDS)
    if not names:
        raise ValueError("at least one parameter is required")
    rng = random.Random(seed)
    sampled = {
        name: [rng.uniform(*DEFAULT_BOUNDS.get(name, (0.0, 1.0))) for _ in range(samples)]
        for name in names
    }
    outcomes = [
        200
        + sum(_SURROGATE_WEIGHTS.get(name, 1.0) * sampled[name][index] for name in names)
        + rng.gauss(0, 10)
        for index in range(samples)
    ]
    raw = {name: abs(_pearson(sampled[name], outcomes)) for name in names}
    total = sum(raw.values())
    normalized = {name: value / total if total else 0.0 for name, value in raw.items()}
    ranked = dict(sorted(normalized.items(), key=lambda item: item[1], reverse=True))
    return {
        "method": "Pearson correlation sensitivity proxy (not Sobol indices)",
        "samples": samples,
        "seed": seed,
        "sensitivity_indices": ranked,
        "most_influential": next(iter(ranked), None),
    }


def sobol_sensitivity_analysis(
    candidates: Sequence[Any] | None = None,
    parameters: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Compatibility name for the historical correlation proxy."""
    del candidates
    return correlation_sensitivity_analysis(parameters)


def _pearson(left: Sequence[float], right: Sequence[float]) -> float:
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    covariance = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right, strict=True))
    left_variance = sum((value - left_mean) ** 2 for value in left)
    right_variance = sum((value - right_mean) ** 2 for value in right)
    denominator = math.sqrt(left_variance * right_variance)
    return covariance / denominator if denominator else 0.0
