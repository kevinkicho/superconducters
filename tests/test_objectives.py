from superconductors.models import Candidate
from superconductors.objectives import DiscoveryObjective, pareto_front


def test_ambient_objective_requires_all_evidence_gates():
    objective = DiscoveryObjective()
    candidate = Candidate(
        "Verified",
        tc=300,
        pressure=0,
        evidence_type="measured",
        verification_status="independent",
    )
    assert objective.evaluate(candidate).meets_objective is True

    claimed = Candidate(
        "Claimed",
        tc=300,
        pressure=0,
        evidence_type="claimed",
        verification_status="disputed",
    )
    evaluation = objective.evaluate(claimed)
    assert evaluation.meets_objective is False
    assert evaluation.gates == {
        "temperature": True,
        "pressure": True,
        "evidence": False,
        "verification": False,
    }


def test_pareto_front_keeps_real_tradeoffs_and_quarantines_claims():
    candidates = [
        Candidate("Low pressure", tc=100, pressure=0),
        Candidate("High Tc", tc=250, pressure=150),
        Candidate("Dominated", tc=90, pressure=10),
        Candidate("Retracted", tc=300, pressure=0, verification_status="retracted"),
    ]
    assert {candidate.formula for candidate in pareto_front(candidates)} == {
        "Low pressure",
        "High Tc",
    }
