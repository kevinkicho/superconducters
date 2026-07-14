"""Evidence gates for a real computational-to-experimental discovery workflow."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Protocol

GateName = Literal[
    "structure-search",
    "thermodynamic-stability",
    "dynamical-stability",
    "electron-phonon",
    "synthesis",
    "independent-replication",
    "complete",
]


@dataclass(frozen=True, slots=True)
class CalculationArtifact:
    """A content-addressed output with enough provenance to reproduce it."""

    path: str
    sha256: str
    software: str
    software_version: str
    input_parameters: Mapping[str, Any]

    @classmethod
    def capture(
        cls,
        path: str | Path,
        *,
        software: str,
        software_version: str,
        input_parameters: Mapping[str, Any],
    ) -> CalculationArtifact:
        artifact_path = Path(path).resolve()
        if not artifact_path.is_file():
            raise FileNotFoundError(f"Calculation artifact not found: {artifact_path}")
        if not software.strip() or not software_version.strip():
            raise ValueError("Calculation software and version are required")
        if not input_parameters:
            raise ValueError("Calculation input parameters are required")
        return cls(
            str(artifact_path),
            _sha256(artifact_path),
            software.strip(),
            software_version.strip(),
            dict(input_parameters),
        )

    def verify_integrity(self) -> bool:
        artifact_path = Path(self.path)
        return artifact_path.is_file() and _sha256(artifact_path) == self.sha256


@dataclass(frozen=True, slots=True)
class StructureHypothesis:
    identifier: str
    formula: str
    pressure_gpa: float
    artifact: CalculationArtifact
    enthalpy_ev_atom: float
    provider: str


@dataclass(frozen=True, slots=True)
class StabilityAssessment:
    structure_id: str
    energy_above_hull_ev_atom: float
    minimum_phonon_frequency_thz: float | None
    artifact: CalculationArtifact

    @property
    def thermodynamically_competitive(self) -> bool:
        return self.energy_above_hull_ev_atom <= 0.05

    @property
    def dynamically_stable(self) -> bool:
        return (
            self.minimum_phonon_frequency_thz is not None and self.minimum_phonon_frequency_thz >= 0
        )


@dataclass(frozen=True, slots=True)
class ElectronPhononAssessment:
    structure_id: str
    lambda_ep: float
    omega_log_k: float
    tc_k: float
    artifact: CalculationArtifact
    anharmonic: bool = False
    converged: bool = False


@dataclass(slots=True)
class DiscoveryDossier:
    formula: str
    target_pressure_gpa: float
    structures: list[StructureHypothesis] = field(default_factory=list)
    stability: list[StabilityAssessment] = field(default_factory=list)
    electron_phonon: list[ElectronPhononAssessment] = field(default_factory=list)
    synthesized_sample_ids: list[str] = field(default_factory=list)
    independently_replicated: bool = False

    def next_gate(self) -> GateName:
        verified_structures = {
            result.identifier for result in self.structures if result.artifact.verify_integrity()
        }
        if not verified_structures:
            return "structure-search"
        verified_stability = [
            result
            for result in self.stability
            if result.structure_id in verified_structures and result.artifact.verify_integrity()
        ]
        if not verified_stability:
            return "thermodynamic-stability"
        stable_ids = {
            result.structure_id
            for result in verified_stability
            if result.thermodynamically_competitive and result.dynamically_stable
        }
        if not any(result.thermodynamically_competitive for result in verified_stability):
            return "structure-search"
        if not stable_ids:
            return "dynamical-stability"
        if not any(
            result.structure_id in stable_ids and result.converged
            for result in self.electron_phonon
            if result.artifact.verify_integrity()
        ):
            return "electron-phonon"
        if not self.synthesized_sample_ids:
            return "synthesis"
        if not self.independently_replicated:
            return "independent-replication"
        return "complete"


class StructureSearchProvider(Protocol):
    def search(self, formula: str, pressure_gpa: float) -> list[StructureHypothesis]: ...


def run_structure_search(
    dossier: DiscoveryDossier,
    provider: StructureSearchProvider | None,
) -> list[StructureHypothesis]:
    if provider is None:
        raise RuntimeError(
            "A real crystal-structure search provider is required; simulation fallback is disabled"
        )
    results = provider.search(dossier.formula, dossier.target_pressure_gpa)
    if not results:
        raise ValueError("Structure search returned no hypotheses")
    if len({result.identifier for result in results}) != len(results):
        raise ValueError("Structure search returned duplicate identifiers")
    for result in results:
        if result.formula != dossier.formula or result.pressure_gpa != dossier.target_pressure_gpa:
            raise ValueError("Structure hypothesis does not match dossier formula and pressure")
        if not result.provider.strip() or not result.artifact.verify_integrity():
            raise ValueError("Structure hypothesis lacks verifiable provider output")
    dossier.structures.extend(results)
    return results


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
