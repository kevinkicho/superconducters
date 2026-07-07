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
