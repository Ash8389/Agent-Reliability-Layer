import pytest
from reliability_layer.nli_checker import (
    ContradictionDetector, ContradictionResult
)

@pytest.fixture(scope="module")
def detector():
    return ContradictionDetector() # load once for all tests

def test_identical_outputs_no_contradiction(detector):
    result = detector.check_all_pairs([
        "Smoking causes lung cancer.",
        "Smoking causes lung cancer.",
        "Smoking causes lung cancer.",
    ])
    assert result.max_contradiction < 0.1

def test_direct_contradiction_is_critical(detector):
    result = detector.check_all_pairs([
        "Drug X is completely safe for pregnant women.",
        "Drug X must be avoided during pregnancy.",
    ])
    assert result.has_critical_contradiction == True
    assert result.max_contradiction > 0.5

def test_single_output_returns_zero(detector):
    result = detector.check_all_pairs(["Only one output"])
    assert result.max_contradiction == 0.0
    assert result.avg_contradiction == 0.0

def test_empty_list_returns_zero(detector):
    result = detector.check_all_pairs([])
    assert result.max_contradiction == 0.0

def test_critical_pair_is_logged(detector):
    result = detector.check_all_pairs([
        "The patient should take Drug X daily.",
        "The patient should never take Drug X.",
        "Drug X is recommended by doctors.",
    ])
    assert len(result.critical_pairs) >= 1

def test_check_pair_returns_all_keys(detector):
    result = detector.check_pair(
        "Inflation is caused by money supply growth.",
        "Inflation is driven by demand pressures.",
    )
    assert "contradiction_score" in result
    assert "entailment_score" in result
    assert "neutral_score" in result
    assert "is_critical" in result
