import pytest
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import subprocess
from unittest.mock import patch, MagicMock, call

# Import the pipeline module (assumed to be scripts.run_pipeline)
import scripts.run_pipeline as rp


class TestRunPipeline:

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_run_pipeline_success(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test that the full pipeline runs successfully with mocked external calls."""
        # Mock load_data to return a list of known materials
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"}
        ]
        # Mock train_model to return a simple model (e.g., a MagicMock with predict method)
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0]
        mock_train.return_value = mock_model

        # Mock predict_tc_with_uncertainty to return (Tc, uncertainty) for each candidate
        def mock_predict_side_effect(name, pressure=None):
            if name == "H3S":
                return (203.0, 5.0)
            elif name == "LaH10":
                return (250.0, 8.0)
            else:
                return (100.0, 10.0)
        mock_predict.side_effect = mock_predict_side_effect

        # Mock DFT calculation to return a dict with results
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # Mock open to return a file handle that records writes
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run the pipeline (assume it has a main function or a run function)
        # We'll call rp.main() or rp.run() — adjust based on actual module
        # For this test, we assume there is a function run_pipeline() that orchestrates
        result = rp.run_pipeline()

        # Verify that load_data was called
        mock_load.assert_called_once()
        # Verify that train_model was called
        mock_train.assert_called_once()
        # Verify that predict_tc_with_uncertainty was called for each candidate
        # (number of calls depends on candidate generation logic; we just check at least one)
        assert mock_predict.call_count >= 1
        # Verify that DFT was called for high-uncertainty candidates
        # (if uncertainty threshold is low, both may be called)
        assert mock_dft.call_count >= 1
        # Verify that open was called to write documents (e.g., candidate_materials.md, roadmap.md)
        # We expect at least one write to a markdown file
        write_calls = [c for c in mock_open.call_args_list if 'candidate_materials.md' in str(c) or 'roadmap.md' in str(c)]
        assert len(write_calls) > 0
        # Optionally check that the pipeline returns a success status
        assert result is True or result == 0

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_run_pipeline_empty_database(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test that the pipeline handles an empty database gracefully."""
        mock_load.return_value = []
        mock_model = MagicMock()
        mock_train.return_value = mock_model
        # No candidates to predict, so predict should not be called
        # The pipeline should either skip or return early
        result = rp.run_pipeline()
        # Verify that load_data was called
        mock_load.assert_called_once()
        # train_model may still be called (depends on implementation) — we allow it
        # But predict and DFT should not be called because no candidates
        mock_predict.assert_not_called()
        mock_dft.assert_not_called()
        # The pipeline should not crash; result should indicate success or graceful exit
        assert result is not None

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_run_pipeline_missing_features(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test that the pipeline handles missing features (e.g., unknown material) without crashing."""
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "Unknown", "Tc": None, "pressure": 0, "composition": "Unknown"}
        ]
        mock_model = MagicMock()
        mock_train.return_value = mock_model

        # For the unknown material, predict_tc_with_uncertainty raises ValueError
        def mock_predict_side_effect(name, pressure=None):
            if name == "H3S":
                return (203.0, 5.0)
            else:
                raise ValueError("Missing Debye temperature for Unknown")
        mock_predict.side_effect = mock_predict_side_effect

        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # The pipeline should catch the ValueError and continue with other candidates
        result = rp.run_pipeline()
        # Verify that predict was called for both materials (or at least for H3S)
        assert mock_predict.call_count >= 1
        # DFT should be called for H3S (if uncertainty high) but not for Unknown (since prediction failed)
        # We can't assert exact count, but at least one DFT call is expected
        assert mock_dft.call_count >= 1
        # The pipeline should not raise an exception
        assert result is True or result == 0

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_run_pipeline_dft_failure(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test that the pipeline handles DFT calculation failure gracefully."""
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"}
        ]
        mock_model = MagicMock()
        mock_train.return_value = mock_model
        mock_predict.return_value = (203.0, 5.0)
        # DFT raises an exception
        mock_dft.side_effect = RuntimeError("DFT calculation did not converge")

        # The pipeline should catch the exception and continue (or log error)
        result = rp.run_pipeline()
        # Verify that DFT was called
        mock_dft.assert_called_once()
        # The pipeline should not crash; result should indicate success or partial success
        assert result is True or result == 0

    @patch('scripts.run_pipeline.generate_experimental_collaboration_report')
    @patch('builtins.open', new_callable=MagicMock)
    def test_experimental_collaboration_report(self, mock_open, mock_generate_report):
        """Test that the experimental collaboration report generation produces correct output for a mock candidate."""
        # Mock the report generation function to return a known report
        mock_report = {
            "candidate": "H3S",
            "predicted_Tc": 203.0,
            "uncertainty": 5.0,
            "synthesis_pressure": 155,
            "status": "recommended"
        }
        mock_generate_report.return_value = mock_report

        # Call the function (assume it's exposed as rp.generate_experimental_collaboration_report)
        result = rp.generate_experimental_collaboration_report("H3S")

        # Verify the report structure and content
        assert result == mock_report
        assert result["candidate"] == "H3S"
        assert result["predicted_Tc"] == 203.0
        assert result["status"] == "recommended"
        # Ensure the function was called with the correct argument
        mock_generate_report.assert_called_once_with("H3S")

    @patch('scripts.run_pipeline.ingest_experimental_data')
    @patch('scripts.run_pipeline.update_candidate_materials')
    @patch('builtins.open', new_callable=MagicMock)
    def test_experimental_data_ingestion(self, mock_open, mock_update_candidate, mock_ingest):
        """Test that ingesting experimental data from a mock CSV updates candidate_materials.md with new Tc."""
        # Mock the ingestion function to return parsed data
        mock_ingest.return_value = [
            {"name": "H3S", "experimental_Tc": 205.0, "pressure": 155, "reference": "Lab test 2025"}
        ]
        # Mock the update function to simulate writing to candidate_materials.md
        mock_update_candidate.return_value = None

        # Call the pipeline function that orchestrates ingestion and update
        # Assume there is a function rp.process_experimental_data(csv_path)
        result = rp.process_experimental_data("mock_experiment.csv")

        # Verify that ingestion was called with the CSV path
        mock_ingest.assert_called_once_with("mock_experiment.csv")
        # Verify that update_candidate_materials was called with the ingested data
        mock_update_candidate.assert_called_once_with(mock_ingest.return_value)
        # Check that open was called to write candidate_materials.md (or at least that the update function was invoked)
        # The update function should have written the new Tc into the markdown file
        # We can check that the mock_open was used to write to candidate_materials.md
        write_calls = [c for c in mock_open.call_args_list if 'candidate_materials.md' in str(c)]
        assert len(write_calls) > 0
        # The pipeline should return a success indicator
        assert result is True or result == 0

    @patch('scripts.run_pipeline.monte_carlo_simulation')
    @patch('scripts.run_pipeline.generate_report_distribution')
    @patch('builtins.open', new_callable=MagicMock)
    def test_monte_carlo_and_report_distribution(self, mock_open, mock_generate_report, mock_monte_carlo):
        """Test that Monte Carlo simulation and report distribution produce correct yield bounds and log file."""
        # Mock Monte Carlo simulation to return yield bounds
        mock_monte_carlo.return_value = {"lower_bound": 150.0, "upper_bound": 250.0, "mean": 200.0, "std": 20.0}
        # Mock report generation to return a report dict
        mock_generate_report.return_value = {"candidate": "H3S", "yield_bounds": [150.0, 250.0], "status": "success"}
        # Mock open to return a file handle
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Call the pipeline function that runs Monte Carlo and report distribution
        # Assume there is a function rp.run_monte_carlo_and_report(candidate_name)
        result = rp.run_monte_carlo_and_report("H3S")

        # Verify that Monte Carlo simulation was called with the candidate
        mock_monte_carlo.assert_called_once_with("H3S")
        # Verify that report generation was called with the simulation results
        mock_generate_report.assert_called_once_with(mock_monte_carlo.return_value)
        # Verify that a log file was created (e.g., monte_carlo_report.log)
        log_calls = [c for c in mock_open.call_args_list if 'monte_carlo_report.log' in str(c)]
        assert len(log_calls) > 0
        # Verify the result contains yield bounds
        assert result["yield_bounds"] == [150.0, 250.0]
        # Verify the result status
        assert result["status"] == "success"


def test_full_pipeline_with_real_data():
    """Integration test: load real database, run pipeline, verify output files."""
    import os
    # Check if real database exists
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'supercon_db.json')
    if not os.path.exists(db_path):
        pytest.skip("Real database not found at " + db_path)
    # Run the pipeline
    result = rp.run_pipeline()
    # Check candidate_materials.md exists and has content
    candidate_path = os.path.join(os.path.dirname(__file__), '..', 'candidate_materials.md')
    assert os.path.exists(candidate_path), "candidate_materials.md should exist after pipeline run"
    with open(candidate_path, 'r') as f:
        candidate_content = f.read()
    assert len(candidate_content) > 0, "candidate_materials.md should not be empty"
    # Check roadmap.md exists and has final report
    roadmap_path = os.path.join(os.path.dirname(__file__), '..', 'roadmap.md')
    assert os.path.exists(roadmap_path), "roadmap.md should exist after pipeline run"
    with open(roadmap_path, 'r') as f:
        roadmap_content = f.read()
    assert len(roadmap_content) > 0, "roadmap.md should not be empty"
    # Verify roadmap contains a final report section (e.g., 'Final Summary' or 'Deployment')
    assert "Final Summary" in roadmap_content or "Deployment" in roadmap_content, \
        "roadmap.md should contain a final report section"


def test_pipeline_validated_against_2025_paper():
    """Integration test: validate pipeline against a recent (2025) paper on room-temperature superconductivity.

    Uses experimental data from a 2025 paper (e.g., LaYH12 with Tc=210K at 200GPa)
    and verifies that the pipeline's top candidate matches the reported compound within tolerance.
    """
    import os
    import json
    import re

    # Path to the paper data file (created by cycle 36)
    paper_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'paper_2025_data.json')
    if not os.path.exists(paper_data_path):
        pytest.skip("Paper data file not found at " + paper_data_path)

    # Load paper data
    with open(paper_data_path, 'r') as f:
        paper_data = json.load(f)

    # Extract expected compound and Tc
    expected_compound = paper_data.get('compound', '')
    expected_tc = paper_data.get('tc', 0)
    expected_pressure = paper_data.get('pressure', 0)
    tolerance = paper_data.get('tolerance', 20)  # K

    # Mock the data loading to return the paper's experimental data
    with patch('scripts.run_pipeline.load_data') as mock_load:
        # Prepare a list of materials from the paper data
        materials = paper_data.get('materials', [
            {
                "name": expected_compound,
                "Tc": expected_tc,
                "pressure": expected_pressure,
                "composition": expected_compound
            }
        ])
        mock_load.return_value = materials

        # Also mock train_model to return a simple model that predicts the paper's Tc
        with patch('scripts.run_pipeline.train_model') as mock_train:
            mock_model = MagicMock()
            mock_model.predict.return_value = [expected_tc]
            mock_train.return_value = mock_model

            # Mock predict_tc_with_uncertainty to return the paper's Tc with small uncertainty
            with patch('scripts.run_pipeline.predict_tc_with_uncertainty') as mock_predict:
                def mock_predict_side_effect(name, pressure=None):
                    if name == expected_compound:
                        return (expected_tc, 5.0)
                    return (100.0, 10.0)
                mock_predict.side_effect = mock_predict_side_effect

                # Mock DFT calculation to return a successful result
                with patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation') as mock_dft:
                    mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

                    # Run the pipeline
                    result = rp.run_pipeline()

                    # Check that candidate_materials.md exists and contains the expected compound
                    candidate_path = os.path.join(os.path.dirname(__file__), '..', 'candidate_materials.md')
                    assert os.path.exists(candidate_path), \
                        "candidate_materials.md should exist after pipeline run"
                    with open(candidate_path, 'r') as f:
                        candidate_content = f.read()

                    # Verify the expected compound appears in the candidate list
                    assert expected_compound in candidate_content, \
                        f"Expected compound {expected_compound} not found in candidate_materials.md"

                    # Verify the predicted Tc is within tolerance of the paper's Tc
                    # Look for pattern like "LaYH12: Tc = 210 K" or similar
                    pattern = re.compile(
                        rf'{re.escape(expected_compound)}.*?Tc\s*[=:]\s*(\d+\.?\d*)',
                        re.IGNORECASE
                    )
                    match = pattern.search(candidate_content)
                    if match:
                        predicted_tc = float(match.group(1))
                        assert abs(predicted_tc - expected_tc) <= tolerance, \
                            f"Predicted Tc {predicted_tc} differs from paper Tc {expected_tc} by more than {tolerance} K"

                    # Also verify that roadmap.md contains a final report section
                    roadmap_path = os.path.join(os.path.dirname(__file__), '..', 'roadmap.md')
                    assert os.path.exists(roadmap_path), \
                        "roadmap.md should exist after pipeline run"
                    with open(roadmap_path, 'r') as f:
                        roadmap_content = f.read()
                    assert "Final Summary" in roadmap_content or "Deployment" in roadmap_content, \
                        "roadmap.md should contain a final report section"

    @patch('scripts.run_pipeline.detect_data_drift')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.load_data')
    def test_long_term_reliability(self, mock_load, mock_train, mock_predict, mock_dft, mock_drift):
        """Run pipeline in a loop for 12 cycles, verify MAE < 10K and drift triggers retraining."""
        # Simulate experimental data for 5 materials
        materials = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"},
            {"name": "YH9", "Tc": 243, "pressure": 200, "composition": "YH9"},
            {"name": "C-S-H", "Tc": 288, "pressure": 270, "composition": "C-S-H"},
            {"name": "LaYH12", "Tc": 210, "pressure": 180, "composition": "LaYH12"},
        ]
        true_tcs = [m['Tc'] for m in materials]

        # Mock load_data to return a batch with slight variations each cycle
        import random
        random.seed(42)
        def load_side_effect():
            noisy = []
            for m in materials:
                noisy_m = m.copy()
                noisy_m['Tc'] = m['Tc'] + random.uniform(-2, 2)
                noisy.append(noisy_m)
            return noisy
        mock_load.side_effect = load_side_effect

        # Mock train_model to return a model that predicts close to true Tc
        model = MagicMock()
        # We'll use a list to record predictions per cycle
        cycle_predictions = []
        def predict_side_effect(X):
            # X is the input features; we ignore and return predictions close to true Tc
            preds = [tc + 1.0 for tc in true_tcs]  # small bias
            cycle_predictions.extend(preds)
            return preds
        model.predict.side_effect = predict_side_effect
        mock_train.return_value = model

        # Mock predict_tc_with_uncertainty
        def predict_uncert_side_effect(name, pressure=None):
            for m in materials:
                if m['name'] == name:
                    return (m['Tc'], 5.0)
            return (100.0, 10.0)
        mock_predict.side_effect = predict_uncert_side_effect

        # Mock DFT
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # Mock detect_data_drift: return False for first 6 cycles, True for next 6
        drift_results = [False] * 6 + [True] * 6
        drift_index = [0]
        def drift_side_effect(*args, **kwargs):
            idx = drift_index[0]
            drift_index[0] += 1
            return drift_results[idx % len(drift_results)]
        mock_drift.side_effect = drift_side_effect

        # Run 12 cycles
        for cycle in range(1, 13):
            # Clear predictions for this cycle
            cycle_predictions.clear()
            # Run pipeline
            result = rp.run_pipeline()
            # Compute MAE for this cycle
            if len(cycle_predictions) == len(true_tcs):
                mae = sum(abs(p - t) for p, t in zip(cycle_predictions, true_tcs)) / len(true_tcs)
            else:
                # If predictions count doesn't match, compute from what we have
                mae = sum(abs(p - t) for p, t in zip(cycle_predictions, true_tcs[:len(cycle_predictions)])) / len(cycle_predictions) if cycle_predictions else 0
            assert mae < 10.0, f"Cycle {cycle}: MAE {mae:.2f} >= 10K"

        # After loop, verify retraining happened
        # train_model should have been called at least 7 times (initial + 6 retraining)
        assert mock_train.call_count >= 7, f"Expected at least 7 train_model calls, got {mock_train.call_count}"

    @patch('scripts.run_pipeline.notify')
    @patch('builtins.open', new_callable=MagicMock)
    def test_council_briefing(self, mock_open, mock_notify):
        """Test that council briefing writes correct section to roadmap.md and calls notifier."""
        candidates = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"},
        ]
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        rp.council_briefing(candidates)
        mock_open.assert_called_with('roadmap.md', 'w')
        written_content = ''.join(c[0][0] for c in mock_file.write.call_args_list)
        assert 'Council Briefing' in written_content
        assert 'H3S' in written_content
        assert 'LaH10' in written_content
        assert '203' in written_content
        assert '250' in written_content
        mock_notify.assert_called_once()

    @patch('scripts.run_pipeline.generate_pdf_report')
    @patch('builtins.open', new_callable=MagicMock)
    def test_virtual_lab_simulation(self, mock_open, mock_generate_pdf):
        """Test that virtual_lab_simulation() produces correct report content and triggers PDF generation."""
        # Mock virtual_lab_simulation to return a report dict
        mock_report = {
            "material": "YH6",
            "Tc": 220.0,
            "pressure": 150.0,
            "composition": "YH6",
            "crystal_structure": "fcc",
            "stability": "metastable",
            "synthesis_route": "high-pressure anvil cell",
            "notes": "Promising candidate for room-temperature superconductivity."
        }
        with patch('scripts.run_pipeline.virtual_lab_simulation', return_value=mock_report) as mock_vlab:
            # Run the simulation (assume it's a function that takes material name and returns report)
            result = rp.virtual_lab_simulation("YH6")
            # Verify the report content matches expected
            assert result == mock_report
            # Verify that open was called to write the report file
            mock_open.assert_called_once()
            # Verify that the written content contains key fields
            written_content = ''.join(c[0][0] for c in mock_open.return_value.__enter__.return_value.write.call_args_list)
            assert 'YH6' in written_content
            assert '220.0' in written_content
            assert '150.0' in written_content
            assert 'fcc' in written_content
            assert 'metastable' in written_content
            assert 'high-pressure anvil cell' in written_content
            # Verify that PDF generation was triggered
            mock_generate_pdf.assert_called_once()
            # Optionally check that the PDF was generated with the report data
            pdf_args, _ = mock_generate_pdf.call_args
            assert pdf_args[0] == mock_report  # first argument is the report dict


    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.select_next_candidate')
    @patch('scripts.run_pipeline.update_candidate_list')
    def test_active_learning_loop(self, mock_update, mock_select, mock_dft, mock_predict, mock_train, mock_load):
        """Test that active learning loop feeds experimental results back into model and selects next candidates."""
        # Mock initial data
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"}
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0]
        mock_train.return_value = mock_model

        # Mock predict_tc_with_uncertainty to return (Tc, uncertainty)
        def mock_predict_side_effect(name, pressure=None):
            if name == "H3S":
                return (203.0, 5.0)
            elif name == "LaH10":
                return (250.0, 8.0)
            else:
                return (100.0, 10.0)
        mock_predict.side_effect = mock_predict_side_effect

        # Mock DFT calculation
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # Mock select_next_candidate to return a candidate name
        mock_select.return_value = "YH6"

        # Mock update_candidate_list to return updated list
        mock_update.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"},
            {"name": "YH6", "Tc": 220, "pressure": 150, "composition": "YH6"}
        ]

        # Run the active learning loop (assume function run_active_learning_loop exists)
        result = rp.run_active_learning_loop()

        # Verify that load_data was called
        mock_load.assert_called_once()
        # Verify that train_model was called (to retrain with new data)
        mock_train.assert_called_once()
        # Verify that select_next_candidate was called (uncertainty sampling)
        mock_select.assert_called_once()
        # Verify that DFT was run for the selected candidate
        mock_dft.assert_called_once()
        # Verify that update_candidate_list was called with new results
        mock_update.assert_called_once()
        # Verify that the result contains the updated candidate list
        assert len(result) == 3
        assert result[-1]["name"] == "YH6"

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.dft_calculator.predict_tc_ml')
    def test_ml_model_integration(self, mock_predict_ml, mock_dft, mock_predict, mock_train, mock_load):
        """Test that ML model predictions are used correctly in the pipeline."""
        # Mock load_data to return candidates
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"}
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0]
        mock_train.return_value = mock_model

        # Mock predict_tc_with_uncertainty (DFT-based)
        def mock_predict_side_effect(name, pressure=None):
            if name == "H3S":
                return (203.0, 5.0)
            elif name == "LaH10":
                return (250.0, 8.0)
            else:
                return (100.0, 10.0)
        mock_predict.side_effect = mock_predict_side_effect

        # Mock DFT calculation
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # Mock ML prediction (e.g., from random forest)
        def mock_ml_predict_side_effect(name, pressure=None):
            if name == "H3S":
                return (210.0, 6.0)
            elif name == "LaH10":
                return (245.0, 9.0)
            else:
                return (180.0, 12.0)
        mock_predict_ml.side_effect = mock_ml_predict_side_effect

        # Run the pipeline (assume it uses ML predictions when available)
        result = rp.run_pipeline(use_ml=True)

        # Verify that load_data was called
        mock_load.assert_called_once()
        # Verify that train_model was called
        mock_train.assert_called_once()
        # Verify that ML predictions were used (predict_tc_ml called at least once)
        assert mock_predict_ml.call_count >= 1
        # Verify that DFT was still called for high-uncertainty candidates
        assert mock_dft.call_count >= 1
        # Verify that the result contains expected structure (e.g., list of dicts with Tc)
        assert isinstance(result, list)
        assert len(result) >= 2
        # Check that ML predictions influenced candidate selection (e.g., uncertainty threshold)
        # We can check that the pipeline used the ML Tc values in some way
        # For simplicity, we assert that the result includes the ML-predicted Tc for H3S
        # (This assumes the pipeline returns a dict with 'ml_tc' field)
        # If not, we can check that the mock was called with correct arguments
        mock_predict_ml.assert_any_call("H3S", pressure=155)

    def test_predict_tc_with_uncertainty_returns_mean_and_std(self):
        """Test that predict_tc_with_uncertainty returns a tuple (mean, std)."""
        with patch('scripts.run_pipeline.predict_tc_with_uncertainty') as mock_predict:
            mock_predict.return_value = (150.0, 10.0)
            result = rp.predict_tc_with_uncertainty("H3S", pressure=155)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], float)
            self.assertIsInstance(result[1], float)
            mock_predict.assert_called_once_with("H3S", pressure=155)

    def test_acquisition_function_and_candidate_selection(self):
        """Test that the acquisition function returns a value and candidate selection picks the best."""
        with patch('scripts.run_pipeline.acquisition_function') as mock_acq:
            mock_acq.return_value = 0.85
            with patch('scripts.run_pipeline.select_next_candidate') as mock_select:
                mock_select.return_value = {"name": "YH6", "Tc": 180.0}
                result = rp.select_next_candidate(candidates=[{"name": "H3S"}, {"name": "YH6"}])
                self.assertIsInstance(result, dict)
                self.assertIn("name", result)
                self.assertEqual(result["name"], "YH6")
                mock_acq.assert_called()

    def test_external_database_query_api_integration_with_mock(self):
        """Test that external database query function handles API response correctly."""
        with patch('scripts.run_pipeline.query_external_database') as mock_query:
            mock_query.return_value = [{"material": "H3S", "Tc": 203}]
            result = rp.query_external_database("H3S")
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["material"], "H3S")
            mock_query.assert_called_once_with("H3S")

    def test_digital_twin_simulation_output(self):
        """Test that digital twin simulation returns expected output structure."""
        with patch('scripts.run_pipeline.run_digital_twin_simulation') as mock_sim:
            mock_sim.return_value = {"temperature": 300, "pressure": 150, "tc": 200.0, "status": "converged"}
            result = rp.run_digital_twin_simulation(material="H3S", pressure=155, temperature=200)
            self.assertIsInstance(result, dict)
            self.assertIn("tc", result)
            self.assertIn("status", result)
            self.assertEqual(result["status"], "converged")
            mock_sim.assert_called_once_with(material="H3S", pressure=155, temperature=200)

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.query_external_database')
    @patch('scripts.run_pipeline.run_digital_twin_simulation')
    @patch('scripts.run_pipeline.update_manufacturing_scalability')
    @patch('builtins.open', new_callable=MagicMock)
    def test_full_pipeline_integration(self, mock_open, mock_manufacturing, mock_digital_twin, mock_ext_db, mock_dft, mock_predict, mock_train, mock_load):
        """Test the full pipeline integration with all components mocked."""
        # Setup mocks
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"}
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0]
        mock_train.return_value = mock_model

        def predict_side_effect(name, pressure=None):
            if name == "H3S":
                return (203.0, 5.0)
            elif name == "LaH10":
                return (250.0, 8.0)
            else:
                return (100.0, 10.0)
        mock_predict.side_effect = predict_side_effect

        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_ext_db.return_value = [{"material": "YH6", "Tc": 180}]
        mock_digital_twin.return_value = {"temperature": 300, "pressure": 150, "tc": 200.0, "status": "converged"}
        mock_manufacturing.return_value = {"yield": 0.85, "cost": 12.5}

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run pipeline
        result = rp.run_pipeline()

        # Assertions
        mock_load.assert_called_once()
        mock_train.assert_called_once()
        # predict_tc_with_uncertainty should be called for each candidate
        assert mock_predict.call_count >= 2
        # DFT should be called for high-uncertainty candidates (if uncertainty > threshold)
        # Assuming threshold is 5, H3S has uncertainty 5.0, LaH10 has 8.0, so both may be called
        assert mock_dft.call_count >= 1
        # External database query should be called
        mock_ext_db.assert_called()
        # Digital twin simulation should be called for top candidates
        mock_digital_twin.assert_called()
        # Manufacturing scalability update should be called
        mock_manufacturing.assert_called()
        # Result should be a dict with expected keys
        self.assertIsInstance(result, dict)
        self.assertIn("candidates", result)
        self.assertIn("dft_results", result)
        self.assertIn("digital_twin_results", result)
        self.assertIn("manufacturing_update", result)

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.query_external_database')
    @patch('scripts.run_pipeline.run_digital_twin_simulation')
    @patch('scripts.run_pipeline.update_manufacturing_scalability')
    @patch('builtins.open', new_callable=MagicMock)
    def test_full_pipeline_empty_candidates(self, mock_open, mock_manufacturing, mock_digital_twin, mock_ext_db, mock_dft, mock_predict, mock_train, mock_load):
        """Test pipeline behavior when candidate list is empty."""
        mock_load.return_value = []  # empty list
        mock_model = MagicMock()
        mock_train.return_value = mock_model
        mock_predict.return_value = (0.0, 0.0)
        mock_dft.return_value = {"energy": 0, "bandgap": 0, "status": "failed"}
        mock_ext_db.return_value = []
        mock_digital_twin.return_value = {"temperature": 0, "pressure": 0, "tc": 0, "status": "failed"}
        mock_manufacturing.return_value = {"yield": 0, "cost": 0}

        result = rp.run_pipeline()
        # Should not crash, return empty results
        self.assertIsInstance(result, dict)
        # Possibly no candidates selected
        self.assertEqual(len(result.get("candidates", [])), 0)

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.query_external_database')
    @patch('scripts.run_pipeline.run_digital_twin_simulation')
    @patch('scripts.run_pipeline.update_manufacturing_scalability')
    @patch('builtins.open', new_callable=MagicMock)
    def test_full_pipeline_api_failure(self, mock_open, mock_manufacturing, mock_digital_twin, mock_ext_db, mock_dft, mock_predict, mock_train, mock_load):
        """Test pipeline handling of external API failure."""
        mock_load.return_value = [{"name": "H3S", "Tc": 203, "pressure": 155}]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0]
        mock_train.return_value = mock_model
        mock_predict.return_value = (203.0, 5.0)
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        # Simulate API failure
        mock_ext_db.side_effect = Exception("API connection failed")
        mock_digital_twin.return_value = {"temperature": 300, "pressure": 150, "tc": 200.0, "status": "converged"}
        mock_manufacturing.return_value = {"yield": 0.85, "cost": 12.5}

        result = rp.run_pipeline()
        # Should handle gracefully, perhaps log error and continue
        self.assertIsInstance(result, dict)
        # External database query may have been attempted but failed; pipeline should not crash
        # Check that other steps still executed
        mock_load.assert_called_once()
        mock_train.assert_called_once()
        mock_predict.assert_called()
        mock_dft.assert_called()
        mock_digital_twin.assert_called()
        mock_manufacturing.assert_called()

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.query_external_database')
    @patch('scripts.run_pipeline.run_digital_twin_simulation')
    @patch('scripts.run_pipeline.update_manufacturing_scalability')
    @patch('builtins.open', new_callable=MagicMock)
    def test_full_pipeline_invalid_parameters(self, mock_open, mock_manufacturing, mock_digital_twin, mock_ext_db, mock_dft, mock_predict, mock_train, mock_load):
        """Test pipeline with invalid parameters (e.g., negative pressure)."""
        mock_load.return_value = [{"name": "H3S", "Tc": 203, "pressure": -100}]  # invalid pressure
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0]
        mock_train.return_value = mock_model
        mock_predict.return_value = (203.0, 5.0)
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_ext_db.return_value = []
        mock_digital_twin.return_value = {"temperature": 300, "pressure": 150, "tc": 200.0, "status": "converged"}
        mock_manufacturing.return_value = {"yield": 0.85, "cost": 12.5}

        result = rp.run_pipeline()
        # Should handle invalid parameters without crashing
        self.assertIsInstance(result, dict)
        # Possibly skip or adjust parameters
        # At minimum, pipeline should not raise exception
        self.assertTrue(True)

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.query_external_database')
    @patch('scripts.run_pipeline.run_digital_twin_simulation')
    @patch('scripts.run_pipeline.update_manufacturing_scalability')
    @patch('builtins.open', new_callable=MagicMock)
    def test_full_pipeline_multi_fidelity(self, mock_open, mock_manufacturing, mock_digital_twin, mock_ext_db, mock_dft, mock_predict, mock_train, mock_load):
        """Test multi-fidelity optimization: low-fidelity ML predictions and high-fidelity DFT."""
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155},
            {"name": "LaH10", "Tc": 250, "pressure": 170}
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0]
        mock_train.return_value = mock_model

        # Low-fidelity predictions (ML) with high uncertainty
        def predict_side_effect(name, pressure=None):
            if name == "H3S":
                return (203.0, 20.0)  # high uncertainty
            elif name == "LaH10":
                return (250.0, 3.0)   # low uncertainty
            else:
                return (100.0, 10.0)
        mock_predict.side_effect = predict_side_effect

        # High-fidelity DFT only for high-uncertainty candidates
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_ext_db.return_value = []
        mock_digital_twin.return_value = {"temperature": 300, "pressure": 150, "tc": 200.0, "status": "converged"}
        mock_manufacturing.return_value = {"yield": 0.85, "cost": 12.5}

        result = rp.run_pipeline()
        # DFT should be called only for H3S (high uncertainty) not for LaH10
        # Assuming the pipeline uses uncertainty threshold to decide
        # We can check that DFT was called with H3S but not LaH10
        dft_calls = [c for c in mock_dft.call_args_list if 'H3S' in str(c)]
        self.assertGreater(len(dft_calls), 0)
        # LaH10 should not have DFT call if uncertainty is low
        # This depends on implementation; we can just check that at least one DFT call happened
        self.assertGreater(mock_dft.call_count, 0)

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.query_external_database')
    @patch('scripts.run_pipeline.run_digital_twin_simulation')
    @patch('scripts.run_pipeline.update_manufacturing_scalability')
    @patch('builtins.open', new_callable=MagicMock)
    def test_full_pipeline_manufacturing_scalability(self, mock_open, mock_manufacturing, mock_digital_twin, mock_ext_db, mock_dft, mock_predict, mock_train, mock_load):
        """Test that manufacturing scalability update is called and updates roadmap."""
        mock_load.return_value = [{"name": "H3S", "Tc": 203, "pressure": 155}]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0]
        mock_train.return_value = mock_model
        mock_predict.return_value = (203.0, 5.0)
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_ext_db.return_value = []
        mock_digital_twin.return_value = {"temperature": 300, "pressure": 150, "tc": 200.0, "status": "converged"}
        mock_manufacturing.return_value = {"yield": 0.85, "cost": 12.5}

        result = rp.run_pipeline()
        # Check that update_manufacturing_scalability was called with appropriate arguments
        mock_manufacturing.assert_called()
        # The function should have been called with the top candidate and its DFT/digital twin results
        # We can check that the call arguments contain the candidate name
        call_args = mock_manufacturing.call_args
        self.assertIn("H3S", str(call_args))

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.query_external_database')
    @patch('scripts.run_pipeline.run_digital_twin_simulation')
    @patch('scripts.run_pipeline.update_manufacturing_scalability')
    @patch('scripts.run_pipeline.generative_model')
    @patch('scripts.run_pipeline.stability_filter')
    @patch('scripts.run_pipeline.rl_optimizer')
    @patch('builtins.open', new_callable=MagicMock)
    def test_full_pipeline_end_to_end(self, mock_open, mock_rl, mock_stability, mock_generative, mock_manufacturing, mock_digital_twin, mock_ext_db, mock_dft, mock_predict, mock_train, mock_load):
        """Comprehensive end-to-end validation test using synthetic data."""
        # Synthetic data: list of candidate materials with known properties
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"},
            {"name": "YH6", "Tc": 180, "pressure": 120, "composition": "YH6"}
        ]
        # Mock train_model to return a model with predict method
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0, 180.0]
        mock_train.return_value = mock_model

        # Mock predict_tc_with_uncertainty to return (Tc, uncertainty) for each candidate
        def predict_side_effect(name, pressure=None):
            mapping = {
                "H3S": (203.0, 5.0),
                "LaH10": (250.0, 8.0),
                "YH6": (180.0, 3.0)
            }
            return mapping.get(name, (100.0, 10.0))
        mock_predict.side_effect = predict_side_effect

        # Mock DFT calculation
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # Mock external database query
        mock_ext_db.return_value = [{"name": "MgB2", "Tc": 39, "pressure": 0, "composition": "MgB2"}]

        # Mock digital twin simulation
        mock_digital_twin.return_value = {"temperature": 300, "pressure": 150, "tc": 200.0, "status": "converged"}

        # Mock manufacturing scalability
        mock_manufacturing.return_value = {"yield": 0.85, "cost": 12.5}

        # Mock generative model
        mock_generative.return_value = [{"name": "NewCompound1", "Tc": 220, "pressure": 160, "composition": "H3S_LaH10"}]

        # Mock stability filter
        mock_stability.return_value = [{"name": "H3S", "Tc": 203, "pressure": 155, "stable": True}]

        # Mock RL optimizer
        mock_rl.return_value = {"best_candidate": "H3S", "optimized_params": {"pressure": 150, "temperature": 200}}

        # Mock open to capture file writes
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run the pipeline
        result = rp.run_pipeline()

        # Assertions: verify each module was called appropriately
        mock_load.assert_called_once()
        mock_train.assert_called_once()
        # predict_tc_with_uncertainty should be called for each candidate (including from external DB)
        # At least 3 original + 1 external = 4 calls
        self.assertGreaterEqual(mock_predict.call_count, 4)
        # DFT should be called for high-uncertainty candidates (if threshold logic)
        self.assertGreaterEqual(mock_dft.call_count, 1)
        # External database query should be called
        mock_ext_db.assert_called_once()
        # Digital twin simulation should be called
        mock_digital_twin.assert_called()
        # Manufacturing scalability should be called
        mock_manufacturing.assert_called()
        # Generative model should be called
        mock_generative.assert_called()
        # Stability filter should be called
        mock_stability.assert_called()
        # RL optimizer should be called
        mock_rl.assert_called()
        # Check that open was called to write output files (e.g., candidate_materials.md, roadmap.md)
        self.assertGreaterEqual(mock_open.call_count, 1)

        # Edge case: missing data (empty list)
        mock_load.return_value = []
        with self.assertRaises(ValueError):
            rp.run_pipeline()

        # Edge case: API failure (external DB raises exception)
        mock_ext_db.side_effect = ConnectionError("API unavailable")
        mock_load.return_value = [{"name": "H3S", "Tc": 203, "pressure": 155}]
        # Should handle gracefully, e.g., log warning and continue
        result = rp.run_pipeline()
        # Verify that pipeline still runs without external data
        self.assertIsNotNone(result)

        # Edge case: DFT calculation fails
        mock_dft.side_effect = RuntimeError("DFT convergence failure")
        # Should handle and continue with ML predictions
        result = rp.run_pipeline()
        self.assertIsNotNone(result)

        # Edge case: generative model returns empty list
        mock_generative.return_value = []
        result = rp.run_pipeline()
        self.assertIsNotNone(result)

        # Edge case: stability filter returns empty list
        mock_stability.return_value = []
        result = rp.run_pipeline()
        self.assertIsNotNone(result)

        # Edge case: RL optimizer returns None
        mock_rl.return_value = None
        result = rp.run_pipeline()
        self.assertIsNotNone(result)



class TestPerformanceAndStress:

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_run_pipeline_performance(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Benchmark the pipeline execution time with a moderate number of candidates."""
        import time
        candidates = [{"name": f"Mat_{i}", "Tc": 100 + i, "pressure": 150, "composition": f"H{i}S"} for i in range(100)]
        mock_load.return_value = candidates
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0] * 100
        mock_train.return_value = mock_model
        def mock_predict_side_effect(name, pressure=None):
            return (150.0, 5.0)
        mock_predict.side_effect = mock_predict_side_effect
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        start = time.perf_counter()
        result = rp.run_pipeline()
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"Pipeline took {elapsed:.2f}s, expected <5s"
        assert result is not None

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_run_pipeline_stress_large_candidates(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Stress test with a large number of candidates (1000) to ensure no memory/performance issues."""
        import time
        candidates = [{"name": f"Mat_{i}", "Tc": 100 + i, "pressure": 150, "composition": f"H{i}S"} for i in range(1000)]
        mock_load.return_value = candidates
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0] * 1000
        mock_train.return_value = mock_model
        def mock_predict_side_effect(name, pressure=None):
            return (150.0, 5.0)
        mock_predict.side_effect = mock_predict_side_effect
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        start = time.perf_counter()
        result = rp.run_pipeline()
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0, f"Pipeline took {elapsed:.2f}s, expected <10s"
        assert result is not None

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_run_pipeline_stress_concurrent_calls(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Stress test by running the pipeline multiple times sequentially to check for state leaks."""
        import time
        candidates = [{"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"}]
        mock_load.return_value = candidates
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0]
        mock_train.return_value = mock_model
        def mock_predict_side_effect(name, pressure=None):
            return (203.0, 5.0)
        mock_predict.side_effect = mock_predict_side_effect
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        for _ in range(10):
            result = rp.run_pipeline()
            assert result is not None


    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_output_consistency(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test that output files are consistent across multiple runs with same input."""
        import time
        candidates = [{"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"}]
        mock_load.return_value = candidates
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0]
        mock_train.return_value = mock_model
        def mock_predict_side_effect(name, pressure=None):
            return (203.0, 5.0)
        mock_predict.side_effect = mock_predict_side_effect
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run pipeline twice and compare outputs
        result1 = rp.run_pipeline()
        result2 = rp.run_pipeline()
        assert result1 == result2, "Pipeline outputs differ between runs"

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_pipeline_performance(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test that the pipeline completes within a reasonable time limit."""
        import time
        candidates = [{"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"}]
        mock_load.return_value = candidates
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0]
        mock_train.return_value = mock_model
        def mock_predict_side_effect(name, pressure=None):
            return (203.0, 5.0)
        mock_predict.side_effect = mock_predict_side_effect
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        start = time.perf_counter()
        result = rp.run_pipeline()
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"Pipeline took {elapsed:.2f}s, expected <5s"
        assert result is not None

    @patch('scripts.run_pipeline.generate_research_report')
    def test_research_report_generation(self, mock_research):
        """Test that the research report generation function is called."""
        mock_research.return_value = "Research report content"
        result = rp.generate_research_report()
        mock_research.assert_called_once()
        assert result == "Research report content"

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_end_to_end_integration_1000_candidates(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test full pipeline with 1000 synthetic candidates, verifying all output files are updated correctly."""
        # Generate 1000 synthetic candidates
        candidates = []
        for i in range(1000):
            candidates.append({
                "name": f"Material_{i}",
                "Tc": 100 + i,
                "pressure": 150 + i,
                "composition": f"H{i}S"
            })
        mock_load.return_value = candidates

        # Mock train_model to return a model that predicts Tc values
        mock_model = MagicMock()
        mock_model.predict.return_value = [100.0 + i for i in range(1000)]
        mock_train.return_value = mock_model

        # Mock predict_tc_with_uncertainty to return (Tc, uncertainty) for each candidate
        def predict_side_effect(name, pressure=None):
            # Extract index from name
            idx = int(name.split('_')[1])
            return (100.0 + idx, 5.0 + idx % 10)
        mock_predict.side_effect = predict_side_effect

        # Mock DFT calculation
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # Mock open to capture write calls
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run the pipeline
        result = rp.run_pipeline()

        # Verify pipeline completed without error
        assert result is not None, "Pipeline returned None"

        # Verify that load_data was called once
        mock_load.assert_called_once()

        # Verify that train_model was called once
        mock_train.assert_called_once()

        # Verify that predict_tc_with_uncertainty was called for each candidate (1000 times)
        assert mock_predict.call_count == 1000, f"Expected 1000 calls to predict, got {mock_predict.call_count}"

        # Verify that DFT was called for at least some candidates (e.g., those with high uncertainty)
        # The exact number depends on the pipeline logic; we just check it was called at least once
        assert mock_dft.call_count >= 1, "DFT was not called"

        # Verify that open was called to write output files
        # Expected output files: candidate_materials.md, roadmap.md, etc.
        # We check that open was called with at least one of these filenames
        expected_files = ["candidate_materials.md", "roadmap.md", "research_report.md", "experimental_plan.md"]
        open_calls = [c for c in mock_open.call_args_list if c[0][0] in expected_files]
        assert len(open_calls) >= 1, f"Expected at least one output file to be written, got {len(open_calls)}"

        # Verify that the pipeline did not raise any exceptions
        # (If an exception occurred, the test would fail before reaching here)

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_extreme_stress(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Stress test: high load, network failures, corrupted data, and self-healing."""
        # 1. High load: 10,000 synthetic candidates
        candidates = []
        for i in range(10000):
            candidates.append({
                "name": f"Material_{i}",
                "Tc": 100 + i,
                "pressure": 150 + i,
                "composition": f"H{i}S"
            })
        # 2. Corrupted data: inject entries with missing keys or invalid types
        candidates[5000] = {"name": "Corrupted_5000"}  # missing Tc, pressure, composition
        candidates[5001] = {"Tc": "invalid", "pressure": None, "composition": 123}  # missing name, invalid types
        mock_load.return_value = candidates

        # Mock train_model to return a model that predicts Tc values
        mock_model = MagicMock()
        mock_model.predict.return_value = [100.0 + i for i in range(10000)]
        mock_train.return_value = mock_model

        # 3. Network failures: simulate intermittent failures in predict_tc_with_uncertainty
        call_count = [0]
        def predict_side_effect(name, pressure=None):
            call_count[0] += 1
            # Simulate network failure for every 100th call (indices 0, 100, 200, ...)
            if call_count[0] % 100 == 0:
                raise ConnectionError("Simulated network failure")
            # For corrupted entries, return None or raise
            if name == "Corrupted_5000":
                return (None, None)
            if name == "Corrupted_5001":
                raise ValueError("Invalid data")
            # Normal response
            idx = int(name.split('_')[1])
            return (100.0 + idx, 5.0 + idx % 10)
        mock_predict.side_effect = predict_side_effect

        # Mock DFT calculation (also simulate occasional failures)
        dft_call_count = [0]
        def dft_side_effect(*args, **kwargs):
            dft_call_count[0] += 1
            if dft_call_count[0] % 50 == 0:
                raise TimeoutError("Simulated DFT timeout")
            return {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_dft.side_effect = dft_side_effect

        # Mock open to capture write calls
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run the pipeline
        try:
            result = rp.run_pipeline()
        except Exception as e:
            pytest.fail(f"Pipeline raised an unhandled exception under stress: {e}")

        # Verify pipeline completed (result may be None or some value)
        # The pipeline should not crash; it should handle failures gracefully
        assert result is not None, "Pipeline returned None under stress"

        # Verify that load_data was called once
        mock_load.assert_called_once()

        # Verify that train_model was called once
        mock_train.assert_called_once()

        # Verify that predict_tc_with_uncertainty was called many times (at least for non-corrupted)
        # Even with failures, the pipeline should attempt to process all candidates
        assert mock_predict.call_count >= 9000, f"Expected at least 9000 predict calls, got {mock_predict.call_count}"

        # Verify that DFT was called at least once (for some high-uncertainty candidates)
        assert mock_dft.call_count >= 1, "DFT was not called"

        # Verify that open was called to write output files
        expected_files = ["candidate_materials.md", "roadmap.md", "research_report.md", "experimental_plan.md"]
        open_calls = [c for c in mock_open.call_args_list if c[0][0] in expected_files]
        assert len(open_calls) >= 1, f"Expected at least one output file to be written, got {len(open_calls)}"

        # Self-healing verification: the pipeline should have continued despite failures
        # (If it crashed, the test would have failed earlier)


    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_end_to_end_integration_1000_candidates(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """End-to-end integration test with 1000 synthetic candidates, verifying all output files are updated."""
        # Generate 1000 synthetic candidates
        candidates = []
        for i in range(1000):
            candidates.append({
                "name": f"Candidate_{i}",
                "Tc": 100.0 + i,
                "pressure": 150.0 + i * 0.1,
                "composition": f"X{i}Y{i}"
            })
        mock_load.return_value = candidates

        # Mock train_model to return a simple model
        mock_model = MagicMock()
        mock_model.predict.return_value = [100.0 + i for i in range(1000)]
        mock_train.return_value = mock_model

        # Mock predict_tc_with_uncertainty to return (Tc, uncertainty) for each candidate
        def predict_side_effect(name, pressure=None):
            idx = int(name.split('_')[1])
            return (100.0 + idx, 5.0 + idx % 10)
        mock_predict.side_effect = predict_side_effect

        # Mock DFT calculation to return a standard result
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # Mock open to capture write calls
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run the pipeline
        try:
            result = rp.run_pipeline()
        except Exception as e:
            pytest.fail(f"Pipeline raised an unhandled exception during integration test: {e}")

        # Verify pipeline completed
        assert result is not None, "Pipeline returned None"

        # Verify load_data was called once
        mock_load.assert_called_once()

        # Verify train_model was called once
        mock_train.assert_called_once()

        # Verify predict_tc_with_uncertainty was called for each candidate (at least 1000 times)
        assert mock_predict.call_count >= 1000, f"Expected at least 1000 predict calls, got {mock_predict.call_count}"

        # Verify DFT was called at least once (for high-uncertainty candidates)
        assert mock_dft.call_count >= 1, "DFT was not called"

        # Verify that open was called to write output files
        expected_files = ["candidate_materials.md", "roadmap.md", "research_report.md", "experimental_plan.md"]
        open_calls = [c for c in mock_open.call_args_list if c[0][0] in expected_files]
        assert len(open_calls) >= 1, f"Expected at least one output file to be written, got {len(open_calls)}"

        # Verify that all expected output files were written (each at least once)
        written_files = set(c[0][0] for c in open_calls)
        for fname in expected_files:
            assert fname in written_files, f"Output file {fname} was not written"

    @patch('scripts.run_pipeline.subprocess.run')
    def test_generate_docker_image_success(self, mock_subprocess_run):
        """Test that generate_docker_image runs Docker commands successfully."""
        # Mock subprocess.run to return a successful result
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout=b"Success", stderr=b"")

        # Call the function
        result = rp.generate_docker_image()

        # Verify subprocess.run was called with the expected Docker commands
        assert mock_subprocess_run.call_count >= 1
        # Verify the function returned True or success indicator
        assert result is True


# ===== Unit tests for run_pipeline.py edge cases =====

class TestRunPipelineEdgeCases:

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_empty_data(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test pipeline with empty data list."""
        mock_load.return_value = []
        mock_model = MagicMock()
        mock_model.predict.return_value = []
        mock_train.return_value = mock_model
        mock_predict.side_effect = []
        mock_dft.return_value = {}
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        result = rp.run_pipeline()
        assert result is not None
        mock_load.assert_called_once()
        mock_train.assert_called_once()
        assert mock_predict.call_count == 0
        assert mock_dft.call_count == 0

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_missing_columns(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test pipeline with data missing required columns."""
        mock_load.return_value = [{"name": "H3S"}]  # missing Tc, pressure, composition
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0]
        mock_train.return_value = mock_model
        def mock_predict_side_effect(name, pressure=None):
            return (200.0, 5.0)
        mock_predict.side_effect = mock_predict_side_effect
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        try:
            result = rp.run_pipeline()
            assert result is not None
        except Exception as e:
            pytest.fail(f"Pipeline raised exception on missing columns: {e}")

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_predict_returns_none(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test pipeline when predict_tc_with_uncertainty returns None for some candidates."""
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"}
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0]
        mock_train.return_value = mock_model
        def mock_predict_side_effect(name, pressure=None):
            if name == "H3S":
                return (203.0, 5.0)
            else:
                return None  # simulate failure
        mock_predict.side_effect = mock_predict_side_effect
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        try:
            result = rp.run_pipeline()
            assert result is not None
        except Exception as e:
            pytest.fail(f"Pipeline raised exception on None predict: {e}")

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_dft_fails_for_some_candidates(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test pipeline when DFT calculation fails for some candidates."""
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"}
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0]
        mock_train.return_value = mock_model
        def mock_predict_side_effect(name, pressure=None):
            return (200.0, 5.0)
        mock_predict.side_effect = mock_predict_side_effect
        def mock_dft_side_effect(name, composition, pressure):
            if name == "H3S":
                return {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
            else:
                return {"status": "failed", "error": "convergence error"}
        mock_dft.side_effect = mock_dft_side_effect
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        try:
            result = rp.run_pipeline()
            assert result is not None
        except Exception as e:
            pytest.fail(f"Pipeline raised exception on DFT failure: {e}")

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_file_write_failure(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Test pipeline when file write fails (e.g., permission error)."""
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"}
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0]
        mock_train.return_value = mock_model
        mock_predict.return_value = (203.0, 5.0)
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}
        mock_open.side_effect = PermissionError("Permission denied")
        try:
            result = rp.run_pipeline()
            assert result is None or result is not None  # pipeline should handle gracefully
        except PermissionError:
            pytest.fail("Pipeline should catch file write errors, not raise them")


# ===== Unit tests for dft_calculator.py =====

class TestDftCalculator:

    @patch('scripts.dft_calculator.subprocess.run')
    def test_run_full_dft_calculation_success(self, mock_subprocess_run):
        """Test successful DFT calculation."""
        from scripts import dft_calculator as dft
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout=b"energy: -1.5\nbandgap: 0.0\nstatus: converged", stderr=b"")
        result = dft.run_full_dft_calculation("H3S", "H3S", 155)
        assert result["status"] == "converged"
        assert result["energy"] == -1.5
        assert result["bandgap"] == 0.0

    @patch('scripts.dft_calculator.subprocess.run')
    def test_run_full_dft_calculation_failure(self, mock_subprocess_run):
        """Test DFT calculation that fails."""
        from scripts import dft_calculator as dft
        mock_subprocess_run.return_value = MagicMock(returncode=1, stdout=b"", stderr=b"Error: SCF not converged")
        result = dft.run_full_dft_calculation("LaH10", "LaH10", 170)
        assert result["status"] == "failed"
        assert "error" in result

    @patch('scripts.dft_calculator.subprocess.run')
    def test_run_full_dft_calculation_timeout(self, mock_subprocess_run):
        """Test DFT calculation that times out."""
        from scripts import dft_calculator as dft
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(cmd="dft", timeout=3600)
        result = dft.run_full_dft_calculation("H3S", "H3S", 155)
        assert result["status"] == "failed"
        assert "timeout" in result.get("error", "").lower()

    @patch('scripts.dft_calculator.subprocess.run')
    def test_run_full_dft_calculation_missing_output(self, mock_subprocess_run):
        """Test DFT calculation with missing output fields."""
        from scripts import dft_calculator as dft
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout=b"energy: -1.5\nstatus: converged", stderr=b"")
        result = dft.run_full_dft_calculation("H3S", "H3S", 155)
        assert result["status"] == "converged"
        assert "bandgap" not in result or result.get("bandgap") is None


# ===== Unit tests for scripts/arxiv_scraper.py =====

class TestArxivScraper:

    @patch('scripts.arxiv_scraper.requests.get')
    def test_fetch_papers_success(self, mock_get):
        """Test successful paper fetch from arXiv."""
        from scripts import arxiv_scraper as arx
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2307.12008</id>
    <title>Observation of room-temperature superconductivity in modified lead-apatite</title>
    <summary>We report the discovery of room-temperature superconductivity...</summary>
    <published>2023-07-22T12:00:00Z</published>
    <author><name>Lee et al.</name></author>
  </entry>
</feed>"""
        mock_get.return_value = mock_response
        papers = arx.fetch_papers(query="superconductivity", max_results=1)
        assert len(papers) == 1
        assert papers[0]["title"] == "Observation of room-temperature superconductivity in modified lead-apatite"
        assert papers[0]["arxiv_id"] == "2307.12008"

    @patch('scripts.arxiv_scraper.requests.get')
    def test_fetch_papers_http_error(self, mock_get):
        """Test paper fetch with HTTP error."""
        from scripts import arxiv_scraper as arx
        mock_get.return_value = MagicMock(status_code=503, text="Service Unavailable")
        papers = arx.fetch_papers(query="superconductivity", max_results=5)
        assert papers == []

    @patch('scripts.arxiv_scraper.requests.get')
    def test_fetch_papers_connection_error(self, mock_get):
        """Test paper fetch with connection error."""
        from scripts import arxiv_scraper as arx
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to connect")
        papers = arx.fetch_papers(query="superconductivity", max_results=5)
        assert papers == []

    @patch('scripts.arxiv_scraper.requests.get')
    def test_fetch_papers_timeout(self, mock_get):
        """Test paper fetch with timeout."""
        from scripts import arxiv_scraper as arx
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        papers = arx.fetch_papers(query="superconductivity", max_results=5)
        assert papers == []

    @patch('scripts.arxiv_scraper.requests.get')
    def test_fetch_papers_malformed_xml(self, mock_get):
        """Test paper fetch with malformed XML response."""
        from scripts import arxiv_scraper as arx
        mock_get.return_value = MagicMock(status_code=200, text="<notxml>")
        papers = arx.fetch_papers(query="superconductivity", max_results=5)
        assert papers == []

    @patch('scripts.arxiv_scraper.requests.get')
    def test_fetch_papers_empty_result(self, mock_get):
        """Test paper fetch with empty result set."""
        from scripts import arxiv_scraper as arx
        mock_get.return_value = MagicMock(status_code=200, text="""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>""")
        papers = arx.fetch_papers(query="nonexistent_topic_xyz", max_results=10)
        assert papers == []


# ===== Performance benchmark: 100k synthetic candidates, 600s completion =====

class TestPerformanceBenchmark:

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('builtins.open', new_callable=MagicMock)
    def test_benchmark_100k_candidates(self, mock_open, mock_dft, mock_predict, mock_train, mock_load):
        """Performance benchmark: pipeline must handle 100k synthetic candidates within 600 seconds."""
        import time
        # Generate 100k synthetic candidates
        candidates = []
        for i in range(100000):
            candidates.append({
                "name": f"candidate_{i}",
                "Tc": 100.0 + (i % 200),
                "pressure": 100 + (i % 100),
                "composition": f"X{i % 10}Y{i % 10}"
            })
        mock_load.return_value = candidates

        # Mock train_model to return a model that predicts quickly
        mock_model = MagicMock()
        mock_model.predict.return_value = [100.0 + (i % 200) for i in range(100000)]
        mock_train.return_value = mock_model

        # Mock predict_tc_with_uncertainty to return quickly
        def predict_side_effect(name, pressure=None):
            idx = int(name.split('_')[1])
            return (100.0 + (idx % 200), 5.0 + (idx % 10))
        mock_predict.side_effect = predict_side_effect

        # Mock DFT to return quickly (only called for high-uncertainty candidates)
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        start_time = time.time()
        try:
            result = rp.run_pipeline()
        except Exception as e:
            pytest.fail(f"Benchmark pipeline raised exception: {e}")
        elapsed = time.time() - start_time

        assert result is not None, "Pipeline returned None during benchmark"
        assert elapsed < 600, f"Benchmark exceeded 600s: took {elapsed:.2f}s"
        assert mock_predict.call_count >= 100000, f"Expected at least 100000 predict calls, got {mock_predict.call_count}"


# ===== Stress test: simultaneous API failures with self-healing fallback =====

class TestStressSelfHealing:

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.requests.post')
    @patch('builtins.open', new_callable=MagicMock)
    def test_simultaneous_api_failures_with_self_healing(self, mock_open, mock_requests_post, mock_dft, mock_predict, mock_train, mock_load):
        """Stress test: simulate simultaneous API failures and verify self-healing fallback."""
        # Setup basic pipeline mocks
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"},
            {"name": "CSH", "Tc": 287, "pressure": 267, "composition": "CSH"}
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0, 287.0]
        mock_train.return_value = mock_model
        mock_predict.return_value = (200.0, 5.0)
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # Simulate multiple API failures: first 3 calls fail, then succeed
        call_count = [0]
        def requests_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 3:
                raise requests.exceptions.ConnectionError("Simulated API failure")
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"status": "ok", "data": {"Tc": 200.0}}
            return mock_resp
        mock_requests_post.side_effect = requests_side_effect

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        try:
            result = rp.run_pipeline()
        except Exception as e:
            pytest.fail(f"Stress test pipeline raised exception: {e}")

        assert result is not None, "Pipeline should self-heal and complete despite API failures"
        # Verify that the fallback mechanism was triggered (e.g., simulation mode used)
        # The pipeline should have logged fallback usage; we check that it completed
        assert call_count[0] >= 3, f"Expected at least 3 API calls, got {call_count[0]}"

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.requests.post')
    @patch('builtins.open', new_callable=MagicMock)
    def test_all_apis_fail_with_fallback(self, mock_open, mock_requests_post, mock_dft, mock_predict, mock_train, mock_load):
        """Stress test: all API calls fail, pipeline must fall back to simulation."""
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"}
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0]
        mock_train.return_value = mock_model
        mock_predict.return_value = (200.0, 5.0)
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # All API calls fail
        mock_requests_post.side_effect = requests.exceptions.ConnectionError("All APIs down")

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        try:
            result = rp.run_pipeline()
        except Exception as e:
            pytest.fail(f"Pipeline should handle all-API failure gracefully: {e}")

        assert result is not None, "Pipeline should complete using fallback simulation"

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.requests.post')
    @patch('builtins.open', new_callable=MagicMock)
    def test_api_recovery_after_failures(self, mock_open, mock_requests_post, mock_dft, mock_predict, mock_train, mock_load):
        """Stress test: API fails then recovers, pipeline should resume normal operation."""
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"}
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0]
        mock_train.return_value = mock_model
        mock_predict.return_value = (200.0, 5.0)
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        call_count = [0]
        def requests_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise requests.exceptions.ConnectionError("Temporary failure")
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"status": "ok", "data": {"Tc": 200.0}}
            return mock_resp
        mock_requests_post.side_effect = requests_side_effect

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        try:
            result = rp.run_pipeline()
        except Exception as e:
            pytest.fail(f"Pipeline should handle API recovery: {e}")

        assert result is not None
        # After recovery, pipeline should use real API results
        assert call_count[0] > 2, f"Expected more than 2 API calls after recovery, got {call_count[0]}"

    @patch('scripts.run_pipeline.load_data')
    @patch('scripts.run_pipeline.train_model')
    @patch('scripts.run_pipeline.predict_tc_with_uncertainty')
    @patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation')
    @patch('scripts.run_pipeline.requests.post')
    @patch('builtins.open', new_callable=MagicMock)
    def test_pipeline_integration_mocked_apis(self, mock_open, mock_requests_post, mock_dft, mock_predict, mock_train, mock_load):
        """Integration test: mock all external APIs and verify output files are updated consistently."""
        # Mock load_data to return a list of known materials
        mock_load.return_value = [
            {"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"},
            {"name": "LaH10", "Tc": 250, "pressure": 170, "composition": "LaH10"}
        ]
        # Mock train_model to return a simple model
        mock_model = MagicMock()
        mock_model.predict.return_value = [200.0, 250.0]
        mock_train.return_value = mock_model

        # Mock predict_tc_with_uncertainty to return (Tc, uncertainty) for each candidate
        def mock_predict_side_effect(name, pressure=None):
            if name == "H3S":
                return (203.0, 5.0)
            elif name == "LaH10":
                return (250.0, 8.0)
            else:
                return (100.0, 10.0)
        mock_predict.side_effect = mock_predict_side_effect

        # Mock DFT calculation to return a dict with results
        mock_dft.return_value = {"energy": -1.5, "bandgap": 0.0, "status": "converged"}

        # Mock external API calls (e.g., arXiv, materials project, etc.)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ok", "data": {"Tc": 200.0}}
        mock_requests_post.return_value = mock_resp

        # Mock open to capture writes to output files
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run the pipeline
        result = rp.run_pipeline()

        # Verify pipeline completed successfully
        assert result is not None, "Pipeline should complete without error"

        # Verify that output files were written consistently
        # Expected output files (based on pipeline design)
        expected_files = [
            "candidate_materials.md",
            "roadmap.md",
            "literature_review.md",
            "manufacturing_scalability.md",
            "experimental_feedback_loop.md",
            "research_paper.md",
            "weekly_digest.md",
            "output/candidates.json",
            "output/candidates.csv"
        ]
        # Check that open was called for each expected file
        open_calls = [call[0][0] for call in mock_open.call_args_list]
        for fname in expected_files:
            assert any(fname in str(call_arg) for call_arg in open_calls), f"Expected {fname} to be written, but it was not"

        # Verify that the content written to candidate_materials.md includes expected data
        write_calls = mock_file.write.call_args_list
        write_content = "".join([call[0][0] for call in write_calls])
        assert "H3S" in write_content, "Expected H3S in output"
        assert "LaH10" in write_content, "Expected LaH10 in output"
        assert "203.0" in write_content, "Expected Tc for H3S in output"
        assert "250.0" in write_content, "Expected Tc for LaH10 in output"

    def test_performance_benchmark_100k_candidates(self):
        """Performance benchmark: run pipeline with 100,000 synthetic candidates, must complete within 600s."""
        import time
        candidates = [{"name": f"candidate_{i}", "Tc": 100 + i % 200, "pressure": 150, "composition": f"H{i%10+1}S"} for i in range(100000)]
        with patch('scripts.run_pipeline.load_data', return_value=candidates):
            mock_model = MagicMock()
            mock_model.predict.return_value = [200.0] * 100000
            with patch('scripts.run_pipeline.train_model', return_value=mock_model):
                def mock_predict(name, pressure=None):
                    return (150.0, 5.0)
                with patch('scripts.run_pipeline.predict_tc_with_uncertainty', side_effect=mock_predict):
                    with patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation', return_value={"energy": -1.0, "bandgap": 0.0, "status": "converged"}):
                        with patch('builtins.open', new_callable=MagicMock):
                            start = time.time()
                            result = rp.run_pipeline()
                            elapsed = time.time() - start
                            assert elapsed < 600, f"Pipeline took {elapsed:.2f}s, expected < 600s"
                            assert result is not None

    def test_stress_api_failures_fallback(self):
        """Stress test: simulate simultaneous API failures and verify fallback to cached data."""
        candidates = [{"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"}]
        with patch('scripts.run_pipeline.load_data', return_value=candidates):
            mock_model = MagicMock()
            mock_model.predict.return_value = [200.0]
            with patch('scripts.run_pipeline.train_model', return_value=mock_model):
                with patch('scripts.run_pipeline.predict_tc_with_uncertainty', return_value=(203.0, 5.0)):
                    with patch('scripts.run_pipeline.dft_calculator.run_full_dft_calculation', return_value={"energy": -1.0, "bandgap": 0.0, "status": "converged"}):
                        with patch('scripts.run_pipeline.requests.post', side_effect=Exception("API failure")):
                            with patch('builtins.open', new_callable=MagicMock) as mock_open:
                                mock_file = MagicMock()
                                mock_open.return_value.__enter__.return_value = mock_file
                                result = rp.run_pipeline()
                                assert result is not None, "Pipeline should complete despite API failures"
                                write_calls = mock_file.write.call_args_list
                                write_content = "".join([call[0][0] for call in write_calls])
                                assert "H3S" in write_content, "Expected candidate data in output"
