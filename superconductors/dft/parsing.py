"""Pure parsers and physics helpers for Quantum ESPRESSO output."""

from __future__ import annotations

import math
import re
from pathlib import Path

_FREQUENCY = re.compile(r"freq\s*\(\s*\d+\s*\)\s*=\s*([-+]?\d+(?:\.\d+)?)\s*\[cm-1\]")


def parse_phonon_frequencies(content: str) -> list[float]:
    return [float(value) for value in _FREQUENCY.findall(content)]


def extract_phonon_frequencies(path: str | Path) -> list[float]:
    return parse_phonon_frequencies(Path(path).read_text(encoding="utf-8", errors="replace"))


def parse_lambda_output(content: str) -> dict[str, float]:
    patterns = {
        "lambda": r"\blambda\s*=\s*([-+]?\d+(?:\.\d+)?)",
        "omega_log": r"\bomega_log\s*=\s*([-+]?\d+(?:\.\d+)?)\s*K",
        "Tc": r"\bTc\s*=\s*([-+]?\d+(?:\.\d+)?)\s*K",
    }
    values = {}
    for name, pattern in patterns.items():
        if match := re.search(pattern, content):
            values[name] = float(match.group(1))
    return values


def extract_lambda(path: str | Path) -> dict[str, float]:
    return parse_lambda_output(Path(path).read_text(encoding="utf-8", errors="replace"))


def compute_tc(lambda_val: float, omega_log: float, mu_star: float = 0.1) -> float:
    if lambda_val <= 0 or omega_log <= 0 or not 0 <= mu_star < 1:
        return 0.0
    denominator = lambda_val - mu_star * (1 + 0.62 * lambda_val)
    if denominator <= 0:
        return 0.0
    exponent = -1.04 * (1 + lambda_val) / denominator
    return (omega_log / 1.2) * math.exp(exponent)
