import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run_pipeline import (
    scrape_arxiv,
    generate_candidates,
    screen_candidates,
    retrain_model,
    run_autonomous_loop
)

# Mock data for external services
MOCK_ARXIV_RESULTS = [
    {
        'title': 'Room-temperature superconductivity in hydride compounds',
        'authors': ['Smith, J.', 'Doe, A.'],
        'abstract': 'We report a new hydride superconductor with Tc above 300 K.',
        'url': 'https://arxiv.org/abs/2401.12345'
    },
    {
        'title': 'Machine learning for superconductor discovery',
        'authors': ['Lee, K.', 'Wang, L.'],
        'abstract': 'We use graph neural networks to predict new superconductors.',
        'url': 'https://arxiv.org/abs/2402.67890'
    }
]

MOCK_MATERIALS_PROJECT_RESULTS = [
    {
        'material_id': 'mp-1234',
        'formula': 'YH3',
        'band_gap': 0.0,
        'e_above_hull': 0.05,
        'energy_per_atom': -3.5
    },
    {
        'material_id': 'mp-5678',
        'formula': 'LaH10',
        'band_gap': 0.0,
        'e_above_hull': 0.02,
        'energy_per_atom': -4.2
    }
]

MOCK_CLOUD_LAB_RESPONSE = {
    'experiment_id': 'exp-001',
    'status': 'completed',
    'results': {
        'tc': 250.0,
        'pressure': 150.0,
        'structure': 'Fm-3m'
    }
}

@pytest.fixture
def mock_external_services():
    """Mock all external API calls used in the autonomous loop."""
    with patch('run_pipeline.arxiv.Search') as mock_arxiv_search, \
         patch('run_pipeline.MPRester') as mock_mprester, \
         patch('run_pipeline.requests.post') as mock_requests_post:
        
        # Mock arxiv search results
        mock_arxiv_result = MagicMock()
        mock_arxiv_result.title = MOCK_ARXIV_RESULTS[0]['title']
        mock_arxiv_result.authors = [MagicMock(name=a) for a in MOCK_ARXIV_RESULTS[0]['authors']]
        mock_arxiv_result.summary = MOCK_ARXIV_RESULTS[0]['abstract']
        mock_arxiv_result.entry_id = MOCK_ARXIV_RESULTS[0]['url']
        mock_arxiv_search.return_value.results.return_value = [mock_arxiv_result]
        
        # Mock Materials Project API
        mock_mprester_instance = mock_mprester.return_value
        mock_mprester_instance.query.return_value = MOCK_MATERIALS_PROJECT_RESULTS
        
        # Mock cloud lab API
        mock_requests_post.return_value.json.return_value = MOCK_CLOUD_LAB_RESPONSE
        mock_requests_post.return_value.status_code = 200
        
        yield

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary directory for output files."""
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    return output_dir

class TestAutonomousLoop:
    """Integration tests for the autonomous loop."""

    def test_scrape_arxiv_returns_results(self, mock_external_services):
        """Test that arxiv scraping returns expected papers."""
        results = scrape_arxiv(query='superconductor', max_results=10)
        assert len(results) > 0
        assert results[0]['title'] == MOCK_ARXIV_RESULTS[0]['title']
        assert results[0]['url'] == MOCK_ARXIV_RESULTS[0]['url']

    def test_generate_candidates_creates_list(self, mock_external_services):
        """Test that candidate generation produces a list of materials."""
        candidates = generate_candidates()
        assert isinstance(candidates, list)
        assert len(candidates) > 0
        # Check that each candidate has required fields
        for c in candidates:
            assert 'formula' in c
            assert 'predicted_tc' in c
            assert 'structure' in c

    def test_screen_candidates_filters_by_criteria(self, mock_external_services):
        """Test that screening removes low-quality candidates."""
        candidates = [
            {'formula': 'YH3', 'predicted_tc': 250, 'e_above_hull': 0.05},
            {'formula': 'LaH10', 'predicted_tc': 260, 'e_above_hull': 0.02},
            {'formula': 'H2O', 'predicted_tc': 0, 'e_above_hull': 0.5}
        ]
        screened = screen_candidates(candidates, min_tc=100, max_e_above_hull=0.1)
        assert len(screened) == 2
        assert all(c['formula'] in ['YH3', 'LaH10'] for c in screened)

    def test_retrain_model_updates_weights(self, mock_external_services):
        """Test that retraining updates model parameters."""
        # Mock model file
        with patch('builtins.open', mock_open(read_data='{}')) as mock_file:
            result = retrain_model(new_data=MOCK_MATERIALS_PROJECT_RESULTS)
            assert result is True
            # Check that model file was written
            mock_file.assert_called()

    def test_full_autonomous_loop_updates_output_files(self, mock_external_services, temp_output_dir):
        """Test that the full loop updates candidate_materials.md and other output files."""
        # Change working directory to temp_output_dir for the test
        original_cwd = os.getcwd()
        os.chdir(temp_output_dir)
        try:
            # Create initial output files if they don't exist
            if not os.path.exists('candidate_materials.md'):
                with open('candidate_materials.md', 'w') as f:
                    f.write('# Candidate Materials\n\n')
            if not os.path.exists('docs/experimental_feedback_loop.md'):
                os.makedirs('docs', exist_ok=True)
                with open('docs/experimental_feedback_loop.md', 'w') as f:
                    f.write('# Experimental Feedback Loop\n\n')
            
            # Run the autonomous loop (mocked)
            result = run_autonomous_loop(
                arxiv_query='superconductor',
                max_candidates=5,
                min_tc=100,
                max_e_above_hull=0.1
            )
            
            # Verify that output files were updated
            assert os.path.exists('candidate_materials.md')
            with open('candidate_materials.md', 'r') as f:
                content = f.read()
            assert 'YH3' in content or 'LaH10' in content
            
            assert os.path.exists('docs/experimental_feedback_loop.md')
            with open('docs/experimental_feedback_loop.md', 'r') as f:
                content = f.read()
            assert 'autonomous loop' in content.lower() or 'retraining' in content.lower()
            
            # Check that the loop returned a summary
            assert 'status' in result
            assert result['status'] == 'completed'
            assert 'candidates_generated' in result
            assert result['candidates_generated'] > 0
        finally:
            os.chdir(original_cwd)

    def test_autonomous_loop_handles_api_failures_gracefully(self):
        """Test that the loop continues when external APIs fail."""
        with patch('run_pipeline.arxiv.Search', side_effect=Exception('API failure')), \
             patch('run_pipeline.MPRester', side_effect=Exception('MP down')), \
             patch('run_pipeline.requests.post', side_effect=Exception('Cloud lab unreachable')):
            
            result = run_autonomous_loop(
                arxiv_query='superconductor',
                max_candidates=5,
                min_tc=100,
                max_e_above_hull=0.1
            )
            # Should still return a result with error status
            assert 'status' in result
            assert result['status'] in ['partial', 'failed']
            assert 'errors' in result

    def test_output_files_are_consistent_after_loop(self, mock_external_services, temp_output_dir):
        """Test that output files maintain consistent formatting after updates."""
        original_cwd = os.getcwd()
        os.chdir(temp_output_dir)
        try:
            # Create initial files with known content
            initial_candidates = '# Candidate Materials\n\n| Formula | Tc (K) | Structure |\n|---------|--------|-----------|\n| YH3 | 250 | Fm-3m |\n'
            with open('candidate_materials.md', 'w') as f:
                f.write(initial_candidates)
            
            initial_feedback = '# Experimental Feedback Loop\n\n## Previous Cycle\n- Generated 3 candidates\n'
            os.makedirs('docs', exist_ok=True)
            with open('docs/experimental_feedback_loop.md', 'w') as f:
                f.write(initial_feedback)
            
            # Run loop
            run_autonomous_loop(
                arxiv_query='superconductor',
                max_candidates=5,
                min_tc=100,
                max_e_above_hull=0.1
            )
            
            # Verify candidate_materials.md still has valid markdown table
            with open('candidate_materials.md', 'r') as f:
                lines = f.readlines()
            # Check that table header is preserved
            assert any('| Formula |' in line for line in lines)
            # Check that at least one data row exists
            data_rows = [l for l in lines if l.startswith('|') and '---' not in l and 'Formula' not in l]
            assert len(data_rows) > 0
            
            # Verify feedback doc has new cycle entry
            with open('docs/experimental_feedback_loop.md', 'r') as f:
                content = f.read()
            assert '## Cycle' in content
        finally:
            os.chdir(original_cwd)

    def test_autonomous_loop_respects_max_candidates_limit(self, mock_external_services):
        """Test that the loop does not generate more than max_candidates."""
        with patch('run_pipeline.generate_candidates', return_value=[
            {'formula': f'Mat{i}', 'predicted_tc': 200, 'structure': 'Fm-3m'}
            for i in range(20)
        ]):
            result = run_autonomous_loop(
                arxiv_query='superconductor',
                max_candidates=5,
                min_tc=100,
                max_e_above_hull=0.1
            )
            assert result['candidates_generated'] <= 5

    def test_autonomous_loop_logs_errors_to_file(self, mock_external_services, temp_output_dir):
        """Test that errors are logged to a file for debugging."""
        original_cwd = os.getcwd()
        os.chdir(temp_output_dir)
        try:
            with patch('run_pipeline.arxiv.Search', side_effect=Exception('Arxiv timeout')):
                run_autonomous_loop(
                    arxiv_query='superconductor',
                    max_candidates=5,
                    min_tc=100,
                    max_e_above_hull=0.1
                )
            # Check that error log exists
            log_files = [f for f in os.listdir('.') if f.endswith('.log')]
            assert len(log_files) > 0
            with open(log_files[0], 'r') as f:
                log_content = f.read()
            assert 'Arxiv timeout' in log_content
        finally:
            os.chdir(original_cwd)
