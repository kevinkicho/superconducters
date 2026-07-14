import pytest

from superconductors.scientific_workflow import (
    CalculationArtifact,
    DiscoveryDossier,
    ElectronPhononAssessment,
    StabilityAssessment,
    StructureHypothesis,
    run_structure_search,
)


def _artifact(tmp_path, name="output.json"):
    path = tmp_path / name
    path.write_text('{"converged": true}', encoding="utf-8")
    return CalculationArtifact.capture(
        path,
        software="test-code",
        software_version="1.0",
        input_parameters={"cutoff_ev": 800},
    )


def _structure(tmp_path):
    return StructureHypothesis("s1", "H3S", 155, _artifact(tmp_path), -0.5, "test-provider")


def test_workflow_requires_real_structure_provider():
    dossier = DiscoveryDossier("H3S", 155)
    with pytest.raises(RuntimeError, match="simulation fallback is disabled"):
        run_structure_search(dossier, None)


def test_workflow_advances_only_when_evidence_gates_pass(tmp_path):
    dossier = DiscoveryDossier("H3S", 155)
    assert dossier.next_gate() == "structure-search"
    dossier.structures.append(_structure(tmp_path))
    assert dossier.next_gate() == "thermodynamic-stability"

    dossier.stability.append(StabilityAssessment("s1", 0.01, -0.2, _artifact(tmp_path, "p1")))
    assert dossier.next_gate() == "dynamical-stability"
    dossier.stability[0] = StabilityAssessment("s1", 0.01, 0.1, _artifact(tmp_path, "p2"))
    assert dossier.next_gate() == "electron-phonon"

    dossier.electron_phonon.append(
        ElectronPhononAssessment("s1", 2.0, 1000, 203, _artifact(tmp_path, "elph"), converged=True)
    )
    assert dossier.next_gate() == "synthesis"
    dossier.synthesized_sample_ids.append("sample-1")
    assert dossier.next_gate() == "independent-replication"
    dossier.independently_replicated = True
    assert dossier.next_gate() == "complete"


def test_structure_provider_must_return_artifacts():
    class EmptyProvider:
        def search(self, formula, pressure_gpa):
            return []

    with pytest.raises(ValueError, match="no hypotheses"):
        run_structure_search(DiscoveryDossier("H3S", 155), EmptyProvider())


def test_tampered_artifact_cannot_advance_gate(tmp_path):
    structure = _structure(tmp_path)
    dossier = DiscoveryDossier("H3S", 155, structures=[structure])
    assert dossier.next_gate() == "thermodynamic-stability"
    (tmp_path / "output.json").write_text("tampered", encoding="utf-8")
    assert dossier.next_gate() == "structure-search"


def test_structure_search_rejects_mismatched_results(tmp_path):
    class MismatchedProvider:
        def search(self, formula, pressure_gpa):
            return [
                StructureHypothesis(
                    "s1", "Other", pressure_gpa, _artifact(tmp_path), -0.5, "provider"
                )
            ]

    with pytest.raises(ValueError, match="does not match"):
        run_structure_search(DiscoveryDossier("H3S", 155), MismatchedProvider())


def test_artifact_capture_requires_provenance(tmp_path):
    path = tmp_path / "result"
    path.write_text("result", encoding="utf-8")
    with pytest.raises(ValueError, match="software and version"):
        CalculationArtifact.capture(
            path, software="", software_version="", input_parameters={"cutoff": 800}
        )
    with pytest.raises(ValueError, match="input parameters"):
        CalculationArtifact.capture(
            path, software="code", software_version="1", input_parameters={}
        )
