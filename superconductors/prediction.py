"""Lightweight, transparent Tc heuristics.

These estimates are screening aids, not experimental or DFT confirmation.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass

VALENCE: dict[str, int] = {
    "H": 1,
    "Li": 1,
    "Be": 2,
    "B": 3,
    "C": 4,
    "N": 5,
    "O": 6,
    "F": 7,
    "Na": 1,
    "Mg": 2,
    "Al": 3,
    "Si": 4,
    "P": 5,
    "S": 6,
    "Cl": 7,
    "K": 1,
    "Ca": 2,
    "Sc": 3,
    "Ti": 4,
    "V": 5,
    "Cr": 6,
    "Mn": 7,
    "Fe": 8,
    "Co": 9,
    "Ni": 10,
    "Cu": 11,
    "Zn": 12,
    "Ga": 3,
    "Ge": 4,
    "As": 5,
    "Se": 6,
    "Br": 7,
    "Rb": 1,
    "Sr": 2,
    "Y": 3,
    "Zr": 4,
    "Nb": 5,
    "Mo": 6,
    "Ru": 8,
    "Rh": 9,
    "Pd": 10,
    "Ag": 11,
    "Cd": 12,
    "In": 3,
    "Sn": 4,
    "Sb": 5,
    "Te": 6,
    "Cs": 1,
    "Ba": 2,
    "La": 3,
    "Ce": 4,
    "Pr": 5,
    "Hf": 4,
    "Ta": 5,
    "W": 6,
    "Re": 7,
    "Os": 8,
    "Ir": 9,
    "Pt": 10,
    "Au": 11,
    "Hg": 12,
    "Tl": 3,
    "Pb": 4,
    "Bi": 5,
    "Th": 4,
    "Lu": 3,
}

DEBYE_TEMPERATURE: dict[str, float] = {
    "H": 100,
    "Li": 344,
    "Be": 1440,
    "B": 1250,
    "C": 2230,
    "N": 100,
    "O": 100,
    "Na": 158,
    "Mg": 400,
    "Al": 428,
    "Si": 645,
    "P": 640,
    "S": 100,
    "K": 91,
    "Ca": 230,
    "Sc": 360,
    "Ti": 420,
    "V": 380,
    "Cr": 630,
    "Mn": 410,
    "Fe": 470,
    "Co": 445,
    "Ni": 450,
    "Cu": 343,
    "Zn": 327,
    "Ga": 320,
    "Ge": 374,
    "As": 282,
    "Se": 90,
    "Rb": 56,
    "Sr": 147,
    "Y": 280,
    "Zr": 291,
    "Nb": 275,
    "Mo": 450,
    "Ru": 600,
    "Rh": 480,
    "Pd": 274,
    "Ag": 225,
    "Cd": 209,
    "In": 108,
    "Sn": 200,
    "Sb": 211,
    "Te": 153,
    "Cs": 38,
    "Ba": 110,
    "La": 142,
    "Ce": 160,
    "Pr": 152,
    "Hf": 252,
    "Ta": 240,
    "W": 400,
    "Re": 430,
    "Os": 500,
    "Ir": 420,
    "Pt": 240,
    "Au": 165,
    "Hg": 72,
    "Tl": 78,
    "Pb": 105,
    "Bi": 119,
    "Th": 163,
    "Lu": 183,
}

_TOKEN = re.compile(r"([A-Z][a-z]?)(\d*(?:\.\d+)?)")


@dataclass(frozen=True, slots=True)
class Prediction:
    formula: str
    tc: float
    uncertainty: float
    method: str
    confidence: float
    applicability: str
    reference_pressure: float | None = None
    citation: str | None = None


@dataclass(frozen=True, slots=True)
class TcBenchmark:
    tc: float
    pressure: float
    uncertainty: float
    citation: str
    evidence: str


class OutOfDomainError(ValueError):
    """Raised when no validated prediction model covers the request."""


TC_BENCHMARKS: dict[str, TcBenchmark] = {
    "H3S": TcBenchmark(203, 155, 5, "Drozdov et al., Nature 525, 73 (2015)", "measured"),
    "LaH10": TcBenchmark(250, 170, 5, "Drozdov et al., Nature 569, 528 (2019)", "measured"),
    "YH6": TcBenchmark(224, 166, 10, "Kong et al., Nat. Commun. 12, 5075 (2021)", "measured"),
    "CeH9": TcBenchmark(150, 200, 15, "Peng et al., Phys. Rev. B 96, 100501 (2017)", "calculated"),
    "ThH10": TcBenchmark(
        200, 200, 20, "Sanna et al., Phys. Rev. B 100, 024511 (2019)", "calculated"
    ),
    "MgB2": TcBenchmark(39, 0, 1, "Nagamatsu et al., Nature 410, 63 (2001)", "measured"),
    "Nb3Sn": TcBenchmark(18.3, 0, 1, "Matthias et al., Phys. Rev. 95, 1435 (1954)", "measured"),
}


def parse_formula(formula: str) -> dict[str, float]:
    if not isinstance(formula, str) or not formula.strip():
        raise ValueError("Formula must be a non-empty string")
    normalized = formula.strip()
    matches = list(_TOKEN.finditer(normalized))
    if not matches or "".join(match.group(0) for match in matches) != normalized:
        raise ValueError(f"Unsupported chemical formula: {formula}")
    elements: dict[str, float] = {}
    for match in matches:
        element, raw_count = match.groups()
        if element not in VALENCE or element not in DEBYE_TEMPERATURE:
            raise ValueError(f"Unsupported element: {element}")
        count = float(raw_count) if raw_count else 1.0
        if count <= 0:
            raise ValueError("Stoichiometric counts must be positive")
        elements[element] = elements.get(element, 0.0) + count
    return elements


def weighted_average(elements: Mapping[str, float], properties: Mapping[str, float]) -> float:
    total_atoms = sum(elements.values())
    if total_atoms <= 0:
        raise ValueError("Formula must contain at least one atom")
    return sum(properties[element] * count for element, count in elements.items()) / total_atoms


def average_valence(formula: str) -> float:
    return weighted_average(parse_formula(formula), VALENCE)


def average_debye(formula: str) -> float:
    return weighted_average(parse_formula(formula), DEBYE_TEMPERATURE)


def _tc_equation(lambda_ep: float, frequency: float, divisor: float, mu_star: float) -> float:
    if lambda_ep <= 0 or frequency <= 0 or not 0 <= mu_star < 1:
        raise ValueError("Physical parameters must be positive and 0 <= mu_star < 1")
    denominator = lambda_ep - mu_star * (1 + 0.62 * lambda_ep)
    if denominator <= 0:
        return 0.0
    exponent = -1.04 * (1 + lambda_ep) / denominator
    return max(0.0, (frequency / divisor) * math.exp(exponent))


def _estimated_coupling(formula: str) -> float:
    return max(0.15, 0.5 + 0.1 * (average_valence(formula) - 4.0))


def mcmillan_tc(formula: str, mu_star: float = 0.1) -> float:
    return _tc_equation(_estimated_coupling(formula), average_debye(formula), 1.45, mu_star)


def allen_dynes_tc(formula: str, mu_star: float = 0.1) -> float:
    omega_log = average_debye(formula) * 0.8
    return _tc_equation(_estimated_coupling(formula), omega_log, 1.2, mu_star)


def predict(formula: str, pressure: float | None = None) -> Prediction:
    normalized = formula.strip() if isinstance(formula, str) else formula
    parse_formula(normalized)
    benchmark = TC_BENCHMARKS.get(normalized)
    if benchmark is None:
        raise OutOfDomainError(
            f"No validated Tc model covers {normalized}; "
            "use DFT or explicit unvalidated_heuristic()"
        )
    if pressure is not None:
        if not isinstance(pressure, (int, float)) or not math.isfinite(pressure) or pressure < 0:
            raise ValueError("Pressure must be a finite non-negative number")
        tolerance = max(5.0, benchmark.pressure * 0.15)
        if abs(pressure - benchmark.pressure) > tolerance:
            raise OutOfDomainError(
                f"{normalized} benchmark applies near {benchmark.pressure:g} GPa, "
                f"not {pressure:g} GPa"
            )
    return Prediction(
        formula=normalized,
        tc=benchmark.tc,
        uncertainty=benchmark.uncertainty,
        method=f"curated {benchmark.evidence} benchmark lookup",
        confidence=1.0 if benchmark.evidence == "measured" else 0.5,
        applicability="reference value; not a novel-material prediction",
        reference_pressure=benchmark.pressure,
        citation=benchmark.citation,
    )


def unvalidated_heuristic(formula: str) -> Prediction:
    """Return the historical formula-only estimate with an explicit zero confidence."""
    tc = allen_dynes_tc(formula)
    return Prediction(
        formula=formula,
        tc=tc,
        uncertainty=max(2.0, tc * 0.5),
        method="unvalidated formula-only Allen-Dynes proxy",
        confidence=0.0,
        applicability="research diagnostic only; ignores pressure and crystal structure",
    )


def predict_tc(formula: str, pressure: float | None = None) -> float:
    return predict(formula, pressure).tc


def predict_tc_with_uncertainty(
    formula: str, pressure: float | None = None
) -> tuple[float, tuple[float, float]]:
    result = predict(formula, pressure)
    lower = max(0.0, result.tc - result.uncertainty)
    return result.tc, (lower, result.tc + result.uncertainty)


def eliashberg_tc(formula: str) -> float:
    """Compatibility alias for the previous API surface."""
    return allen_dynes_tc(formula)
