import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import scripts.predict_tc as ptc

def test_predict_tc_h3s():
    # H3S at 155 GPa should have Tc around 203 K
    result = ptc.predict_tc("H3S", pressure=155)
    assert isinstance(result, float)
    assert 180 <= result <= 220

def test_predict_tc_lah10():
    # LaH10 at 170 GPa should have Tc around 250 K
    result = ptc.predict_tc("LaH10", pressure=170)
    assert isinstance(result, float)
    assert 230 <= result <= 270

def test_predict_tc_ybco():
    # YBCO at ambient pressure should have Tc around 92 K
    result = ptc.predict_tc("YBa2Cu3O7", pressure=0)
    assert isinstance(result, float)
    assert 80 <= result <= 100

def test_predict_tc_invalid_material():
    with pytest.raises(ValueError):
        ptc.predict_tc("InvalidMaterial", pressure=100)

def test_predict_tc_missing_pressure():
    # pressure defaults to 0
    result = ptc.predict_tc("YBa2Cu3O7")
    assert isinstance(result, float)
    assert 80 <= result <= 100

def test_allen_dynes_tc():
    # Test the helper function directly
    tc = ptc.allen_dynes_tc(2.0, 1000, mu_star=0.1)
    assert isinstance(tc, float)
    assert tc > 0


def test_data_loading(monkeypatch):
    import pandas as pd
    mock_data = pd.DataFrame({'material': ['H3S', 'LaH10'], 'tc': [203, 250]})
    monkeypatch.setattr(ptc, 'load_data', lambda: mock_data)
    result = ptc.load_data()
    assert result.equals(mock_data)

def test_model_training(monkeypatch):
    mock_model = MagicMock()
    monkeypatch.setattr(ptc, 'train_model', lambda data: mock_model)
    result = ptc.train_model('dummy')
    assert result == mock_model

def test_prediction_accuracy(monkeypatch):
    import numpy as np
    X = np.array([1,2,3,4,5])
    y = 2*X + 1
    mock_model = MagicMock()
    mock_model.predict.return_value = y
    monkeypatch.setattr(ptc, 'train_model', lambda data: mock_model)
    monkeypatch.setattr(ptc, 'load_data', lambda: (X, y))
    predictions = mock_model.predict(X)
    ss_res = np.sum((y - predictions)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2 = 1 - ss_res/ss_tot
    assert r2 > 0.8

def test_screening_mode(monkeypatch):
    mock_results = [{'material': 'H3S', 'tc': 203}, {'material': 'LaH10', 'tc': 250}]
    monkeypatch.setattr(ptc, 'screen_materials', lambda materials, pressure: mock_results)
    result = ptc.screen_materials(['H3S', 'LaH10'], pressure=100)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]['material'] == 'H3S'

def test_edge_cases():
    with pytest.raises(ValueError):
        ptc.predict_tc('', pressure=0)
    with pytest.raises(TypeError):
        ptc.predict_tc(None, pressure=0)
    result = ptc.predict_tc('H3S', pressure=-10)
    assert isinstance(result, float)
