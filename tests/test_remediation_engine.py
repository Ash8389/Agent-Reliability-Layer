import pytest
from reliability_layer.remediation_engine import RemediationEngine

@pytest.fixture
def engine():
    return RemediationEngine()

def test_high_answer_variance_triggers_recommendation(engine):
    report = engine.diagnose(
        answer_variance=0.5,
        findings_variance=0.1,
        citations_variance=0.1,
        contradiction_score=0.0,
        overall_reliability=0.75,
    )
    assert len(report.recommendations) >= 1
    dims = [r.dimension for r in report.recommendations]
    assert "answer" in dims

def test_critical_contradiction_triggers_human_review(engine):
    report = engine.diagnose(
        answer_variance=0.1,
        findings_variance=0.1,
        citations_variance=0.1,
        contradiction_score=0.85,
        overall_reliability=0.7,
    )
    assert report.needs_human_review == True
    assert report.priority_fix.severity == "CRITICAL"

def test_all_low_variance_no_recommendations(engine):
    report = engine.diagnose(
        answer_variance=0.05,
        findings_variance=0.10,
        citations_variance=0.10,
        contradiction_score=0.01,
        overall_reliability=0.92,
    )
    assert len(report.recommendations) == 0
    assert report.priority_fix is None
    assert report.needs_human_review == False

def test_priority_fix_is_highest_severity(engine):
    report = engine.diagnose(
        answer_variance=0.5,  # High, triggers HIGH severity
        findings_variance=0.6, # High, triggers HIGH severity
        citations_variance=0.1,
        contradiction_score=0.0,
        overall_reliability=0.8,
    )
    assert report.priority_fix is not None
    assert report.priority_fix.severity in ("CRITICAL", "HIGH")

def test_low_overall_reliability_triggers_critical(engine):
    report = engine.diagnose(
        answer_variance=0.1,
        findings_variance=0.1,
        citations_variance=0.1,
        contradiction_score=0.1,
        overall_reliability=0.4, # < 0.5 triggers CRITICAL
    )
    assert any(r.severity == "CRITICAL" for r in report.recommendations)

def test_estimated_improvement_string_not_empty(engine):
    report = engine.diagnose(
        answer_variance=0.5,
        findings_variance=0.1,
        citations_variance=0.8,
        contradiction_score=0.9,
        overall_reliability=0.3,
    )
    assert len(report.estimated_improvement) > 0
