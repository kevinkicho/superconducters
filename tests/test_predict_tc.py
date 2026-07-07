import pytest
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

def test_predict_tc_invalid_material():
    with pytest.raises(ValueError):
        ptc.predict_tc("InvalidMaterial", pressure=100)

def test_predict_tc_missing_pressure():
    with pytest.raises(TypeError):
        ptc.predict_tc("H3S")

def test_predict_tc_zero_pressure():
    result = ptc.predict_tc("H3S", pressure=0)
    assert result == 0.0
