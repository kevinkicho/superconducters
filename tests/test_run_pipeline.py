import pytest
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
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
