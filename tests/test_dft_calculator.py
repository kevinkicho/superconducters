from pathlib import Path

import pytest

import dft_calculator
from superconductors.dft.inputs import generate_ph_input, generate_scf_input
from superconductors.dft.parsing import compute_tc, parse_lambda_output, parse_phonon_frequencies
from superconductors.dft.runner import DFTExecutionError, run_dft_pipeline, run_full_dft_calculation


@pytest.fixture
def structure():
    return {
        "cell_parameters": [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
        "atomic_species": [{"element": "H", "mass": 1.008, "pseudo": "H.UPF"}],
        "atomic_positions": [{"element": "H", "x": 0, "y": 0, "z": 0}],
    }


def test_scf_input_contains_validated_structure(structure):
    rendered = generate_scf_input(structure, prefix="hydrogen", kpoints=(6, 6, 6, 0, 0, 0))
    assert "prefix = 'hydrogen'" in rendered
    assert "nat = 1" in rendered
    assert "6 6 6 0 0 0" in rendered


def test_invalid_structure_is_rejected():
    with pytest.raises(ValueError, match="required fields"):
        generate_scf_input({})


def test_phonon_input_uses_prefix_specific_dynamical_matrix():
    assert "fildyn = 'sample.dyn'" in generate_ph_input("sample")


def test_output_parsers_extract_signed_values():
    assert parse_phonon_frequencies("freq ( 1) = -12.5 [cm-1]") == [-12.5]
    assert parse_lambda_output("lambda = 1.4\nomega_log = 900 K\nTc = 210 K") == {
        "lambda": 1.4,
        "omega_log": 900.0,
        "Tc": 210.0,
    }


def test_tc_formula_handles_invalid_denominator():
    assert compute_tc(0, 1000) == 0
    assert compute_tc(1.5, 1000) > 0


def test_execution_requires_explicit_authorization(structure, tmp_path):
    with pytest.raises(DFTExecutionError, match="execute=True"):
        run_full_dft_calculation(structure, workdir=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_injected_runner_writes_outputs_and_preserves_cwd(structure, tmp_path):
    calls = []

    def runner(command, workdir: Path):
        calls.append((list(command), workdir))
        if command[0] == "ph.x":
            return "freq ( 1) = 123.4 [cm-1]\n"
        if command[0] == "lambda.x":
            return "lambda = 1.5\nomega_log = 1000 K\n"
        return "completed\n"

    before = Path.cwd()
    result = run_full_dft_calculation(
        structure,
        prefix="test",
        workdir=tmp_path,
        execute=True,
        runner=runner,
    )
    assert Path.cwd() == before
    assert len(calls) == 5
    assert result["phonon_frequencies"] == [123.4]
    assert result["elph"]["lambda"] == 1.5
    assert (tmp_path / "test.lambda.out").read_text(encoding="utf-8").startswith("lambda")


def test_pipeline_computes_tc_from_injected_outputs(structure, tmp_path):
    def runner(command, _):
        if command[0] == "lambda.x":
            return "lambda = 1.5\nomega_log = 1000 K\n"
        return ""

    result = run_dft_pipeline(structure, workdir=tmp_path, execute=True, runner=runner)
    assert result["tc"] > 0


def test_compatibility_module_uses_modular_formula():
    assert dft_calculator.compute_tc_mcmillan_allen_dynes(1.5, 1000) == pytest.approx(
        compute_tc(1.5, 1000)
    )
    assert callable(dft_calculator.fine_tune_pinn_on_real_data)
    assert callable(dft_calculator.generate_scf_input)
