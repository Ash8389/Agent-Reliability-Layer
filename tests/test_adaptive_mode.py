import pytest
from reliability_layer import ReliabilityLayer

def test_default_mode_is_standard():
    rl = ReliabilityLayer()
    assert rl.mode == "standard"

def test_invalid_mode_raises_error():
    with pytest.raises(ValueError):
        ReliabilityLayer(mode="invalid")

def test_all_valid_modes_accepted():
    for mode in ("standard", "full", "adaptive"):
        rl = ReliabilityLayer(mode=mode)
        assert rl.mode == mode

def test_adaptive_mode_returns_response():
    def stable_agent(q): return "Consistent answer every time."
    rl = ReliabilityLayer(runs=2, mode="adaptive", escalate_threshold=0.75)
    result = rl.wrap(stable_agent).query("test")
    assert result is not None
    assert hasattr(result, "reliability")
    assert 0.0 <= result.reliability <= 1.0

def test_full_mode_includes_contradiction_score():
    def stable_agent(q): return "Same answer every run."
    rl = ReliabilityLayer(runs=2, mode="full")
    result = rl.wrap(stable_agent).query("test")
    assert hasattr(result, "contradiction_score")
    assert result.contradiction_score >= 0.0
