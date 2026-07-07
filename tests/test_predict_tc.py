import pytest
import scripts.predict_tc as ptc

def test_predict_tc_function_exists():
    assert callable(ptc.predict_tc)

def test_predict_tc_returns_float():
    result = ptc.predict_tc()
    assert isinstance(result, float)

def test_predict_tc_raises_on_invalid_input():
    with pytest.raises(TypeError):
        ptc.predict_tc(invalid_arg=True)
