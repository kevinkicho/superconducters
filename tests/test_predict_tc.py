import pytest
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import scripts.predict_tc as ptc
from unittest.mock import patch, MagicMock

def test_load_data_success(tmp_path):
    db_path = tmp_path / "superconductor_database.json"
    data = [{"name": "H3S", "Tc": 203, "pressure": 155, "composition": "H3S"}]
    db_path.write_text(json.dumps(data))
    with patch.object(ptc, 'DATABASE_PATH', str(db_path)):
        result = ptc.load_data()
        assert result == data

def test_load_data_file_not_found():
    with patch.object(ptc, 'DATABASE_PATH', 'nonexistent.json'):
        with pytest.raises(FileNotFoundError):
            ptc.load_data()

def test_mcmillan_tc():
    tc = ptc.mcmillan_tc(2.0, 1000, mu_star=0.1)
    assert isinstance(tc, float)
    assert tc > 0
    assert 180 < tc < 220

def test_allen_dynes_tc():
    tc = ptc.allen_dynes_tc(2.0, 1000, mu_star=0.1)
    assert isinstance(tc, float)
    assert tc > 0
    assert tc > ptc.mcmillan_tc(2.0, 1000, mu_star=0.1)

def test_predict_tc_h3s():
    result = ptc.predict_tc("H3S", pressure=155)
    assert isinstance(result, float)
    assert 180 <= result <= 220

def test_predict_tc_lah10():
    result = ptc.predict_tc("LaH10", pressure=170)
    assert isinstance(result, float)
    assert 230 <= result <= 270

def test_predict_tc_ybco():
    result = ptc.predict_tc("YBa2Cu3O7", pressure=0)
    assert isinstance(result, float)
    assert 80 <= result <= 100

def test_predict_tc_invalid_material():
    with pytest.raises(ValueError):
        ptc.predict_tc("InvalidMaterial", pressure=100)

def test_predict_tc_missing_pressure():
    result = ptc.predict_tc("YBa2Cu3O7")
    assert isinstance(result, float)
    assert 80 <= result <= 100

def test_train_model(monkeypatch):
    mock_data = [
        {"name": "H3S", "Tc": 203, "composition": "H3S", "pressure": 155},
        {"name": "LaH10", "Tc": 250, "composition": "LaH10", "pressure": 170},
    ]
    monkeypatch.setattr(ptc, 'load_data', lambda: mock_data)
    model = ptc.train_model()
    assert model is not None
    pred = model.predict([[ptc.average_valence("H3S"), ptc.average_debye("H3S")]])
    assert pred[0] > 0

def test_edge_cases():
    with pytest.raises(ValueError):
        ptc.predict_tc('', pressure=0)
    with pytest.raises(TypeError):
        ptc.predict_tc(None, pressure=0)
    result = ptc.predict_tc('H3S', pressure=-10)
    assert isinstance(result, float)

def test_prediction_accuracy():
    mock_data = [
        {"name": "H3S", "Tc": 203, "composition": "H3S", "pressure": 155},
        {"name": "LaH10", "Tc": 250, "composition": "LaH10", "pressure": 170},
    ]
    with patch.object(ptc, 'load_data', return_value=mock_data):
        model = ptc.train_model()
        pred_h3s = model.predict([[ptc.average_valence("H3S"), ptc.average_debye("H3S")]])[0]
        pred_lah10 = model.predict([[ptc.average_valence("LaH10"), ptc.average_debye("LaH10")]])[0]
        assert abs(pred_h3s - 203) < 20, f"H3S prediction {pred_h3s} too far from 203"
        assert abs(pred_lah10 - 250) < 20, f"LaH10 prediction {pred_lah10} too far from 250"

def test_screening_output_format():
    mock_data = [
        {"name": "H3S", "Tc": 203, "composition": "H3S", "pressure": 155},
        {"name": "LaH10", "Tc": 250, "composition": "LaH10", "pressure": 170},
        {"name": "YBa2Cu3O7", "Tc": 93, "composition": "YBa2Cu3O7", "pressure": 0},
    ]
    with patch.object(ptc, 'load_data', return_value=mock_data):
        results = ptc.screen_materials()
        assert isinstance(results, list)
        assert len(results) == 3
        for item in results:
            assert isinstance(item, dict)
            assert "name" in item
            assert "Tc" in item
            assert "pressure" in item
            assert "composition" in item
        tcs = [r["Tc"] for r in results]
        assert tcs == sorted(tcs, reverse=True)


def test_active_learning_selection():
    mock_data = [
        {"name": "H3S", "Tc": 203, "composition": "H3S", "pressure": 155},
        {"name": "LaH10", "Tc": 250, "composition": "LaH10", "pressure": 170},
        {"name": "YBa2Cu3O7", "Tc": 93, "composition": "YBa2Cu3O7", "pressure": 0},
    ]
    with patch.object(ptc, 'load_data', return_value=mock_data):
        candidates = ptc.select_candidates(n=2)
        assert isinstance(candidates, list)
        assert len(candidates) == 2
        for c in candidates:
            assert "name" in c
            assert "Tc" in c
            assert "uncertainty" in c

def test_retraining():
    mock_data = [
        {"name": "H3S", "Tc": 203, "composition": "H3S", "pressure": 155},
        {"name": "LaH10", "Tc": 250, "composition": "LaH10", "pressure": 170},
    ]
    with patch.object(ptc, 'load_data', return_value=mock_data):
        model1 = ptc.train_model()
        pred1 = model1.predict([[ptc.average_valence("H3S"), ptc.average_debye("H3S")]])[0]
        new_data = [{"name": "YBa2Cu3O7", "Tc": 93, "composition": "YBa2Cu3O7", "pressure": 0}]
        with patch.object(ptc, 'load_data', return_value=mock_data + new_data):
            model2 = ptc.train_model()
            pred2 = model2.predict([[ptc.average_valence("H3S"), ptc.average_debye("H3S")]])[0]
            assert pred1 != pred2

def test_screening_empty_dataset():
    with patch.object(ptc, 'load_data', return_value=[]):
        results = ptc.screen_materials()
        assert isinstance(results, list)
        assert len(results) == 0

def test_active_learning_no_candidates():
    with patch.object(ptc, 'load_data', return_value=[]):
        candidates = ptc.select_candidates(n=5)
        assert isinstance(candidates, list)
        assert len(candidates) == 0

def test_integration_full_pipeline():
    mock_data = [
        {"name": "H3S", "Tc": 203, "composition": "H3S", "pressure": 155},
        {"name": "LaH10", "Tc": 250, "composition": "LaH10", "pressure": 170},
    ]
    with patch.object(ptc, 'load_data', return_value=mock_data):
        model = ptc.train_model()
        screened = ptc.screen_materials()
        assert len(screened) == 2
        candidates = ptc.select_candidates(n=1)
        assert len(candidates) == 1
        new_data = [{"name": "YBa2Cu3O7", "Tc": 93, "composition": "YBa2Cu3O7", "pressure": 0}]
        with patch.object(ptc, 'load_data', return_value=mock_data + new_data):
            model2 = ptc.train_model()
            pred_new = model2.predict([[ptc.average_valence("YBa2Cu3O7"), ptc.average_debye("YBa2Cu3O7")]])[0]
            assert abs(pred_new - 93) < 20


def test_predict_uncertainty():
    mock_data = [
        {"name": "H3S", "Tc": 203, "composition": "H3S", "pressure": 155},
        {"name": "LaH10", "Tc": 250, "composition": "LaH10", "pressure": 170},
    ]
    with patch.object(ptc, 'load_data', return_value=mock_data):
        model = ptc.train_model()
        uncertainty = ptc.predict_uncertainty("H3S", model=model)
        assert isinstance(uncertainty, float)
        assert uncertainty >= 0


def test_generate_candidates():
    mock_data = [
        {"name": "H3S", "Tc": 203, "composition": "H3S", "pressure": 155},
        {"name": "LaH10", "Tc": 250, "composition": "LaH10", "pressure": 170},
        {"name": "YBa2Cu3O7", "Tc": 93, "composition": "YBa2Cu3O7", "pressure": 0},
    ]
    with patch.object(ptc, 'load_data', return_value=mock_data):
        candidates = ptc.generate_candidates(n=2)
        assert isinstance(candidates, list)
        assert len(candidates) == 2
        for c in candidates:
            assert "name" in c
            assert "Tc" in c
            assert "uncertainty" in c


def test_average_valence_non_existent_element():
    with pytest.raises(ValueError):
        ptc.average_valence("X")

def test_predict_tc_extreme_stoichiometry():
    result = ptc.predict_tc("H100S", pressure=100)
    assert isinstance(result, float)

def test_load_data_json_decode_error():
    with patch.object(ptc, 'DATABASE_PATH', 'invalid.json'):
        with patch('builtins.open', MagicMock(side_effect=json.JSONDecodeError("", "", 0))):
            with pytest.raises(json.JSONDecodeError):
                ptc.load_data()

def test_predict_tc_type_mismatch_pressure():
    with pytest.raises(TypeError):
        ptc.predict_tc("H3S", pressure="high")

def test_predict_tc_type_mismatch_composition():
    with pytest.raises(TypeError):
        ptc.predict_tc(123, pressure=100)
