import pytest, json
from reliability_layer.response_builder import ResponseBuilder, ReliabilityResponse
from reliability_layer.models.variance_scores import VarianceScores
from reliability_layer.models.run_result import RunResult

def make_mock_data(n=3, all_agree=True):
    answers = ['Drug X causes liver damage'] * n if all_agree else ['Drug X causes liver damage','Different answer','Another']
    runs = [RunResult(run_id=i+1, raw_output=answers[i], duration_ms=1000+i*100, timestamp="2026-03-02T20:54:42Z") for i in range(n)]
    stabilized = {'stabilized_output': answers[0], 'method_used': 'structured_consensus', 'agreement_rate': 1.0 if all_agree else 0.33}
    scores = VarianceScores(answer_variance=0.0 if all_agree else 0.9, findings_variance=0.1, citations_variance=0.1, overall_reliability=0.93 if all_agree else 0.37, confidence_label='HIGH' if all_agree else 'LOW')
    return runs, stabilized, scores

builder = ResponseBuilder()

# Test 1: Returns correct type
def test_returns_reliability_response():
    runs, stab, scores = make_mock_data()
    result = builder.build(stab, scores, runs)
    assert isinstance(result, ReliabilityResponse)

# Test 2: Answer field is set correctly
def test_answer_matches_stabilized():
    runs, stab, scores = make_mock_data()
    result = builder.build(stab, scores, runs)
    assert result.answer == stab['stabilized_output']

# Test 3: Runs agreed format
def test_runs_agreed_format():
    runs, stab, scores = make_mock_data(n=3)
    result = builder.build(stab, scores, runs)
    assert '/' in result.runs_agreed
    parts = result.runs_agreed.split('/')
    assert int(parts[1]) == 3

# Test 4: Reliability is within bounds
def test_reliability_bounds():
    runs, stab, scores = make_mock_data()
    result = builder.build(stab, scores, runs)
    assert 0.0 <= result.reliability <= 1.0

# Test 5: Confidence label is valid
def test_confidence_label_valid():
    runs, stab, scores = make_mock_data()
    result = builder.build(stab, scores, runs)
    assert result.confidence in ('HIGH','MEDIUM','LOW')

# Test 6: Audit trail has correct count
def test_audit_trail_count():
    runs, stab, scores = make_mock_data(n=5)
    result = builder.build(stab, scores, runs)
    assert len(result.audit_trail) == 5

# Test 7: Audit trail truncates long answers
def test_audit_trail_truncation():
    long_runs = [RunResult(run_id=1, raw_output='x'*500, duration_ms=100, timestamp="2026-03-02T20:54:42Z")]
    stab = {'stabilized_output':'x', 'method_used':'test','agreement_rate':1.0}
    scores = VarianceScores(answer_variance=0.0,findings_variance=0.0, citations_variance=0.0,overall_reliability=1.0,confidence_label='HIGH')
    result = builder.build(stab, scores, long_runs)
    assert len(result.audit_trail[0].answer) <= 300

# Test 8: Serializes to JSON without errors
def test_json_serialization():
    runs, stab, scores = make_mock_data()
    result = builder.build(stab, scores, runs)
    json_str = result.model_dump_json()
    parsed = json.loads(json_str)
    assert 'answer' in parsed
    assert 'reliability' in parsed
    assert 'audit_trail' in parsed

# Test 9: Confidence color property
def test_confidence_color():
    runs, stab, scores = make_mock_data()
    result = builder.build(stab, scores, runs)
    assert result.confidence_color.startswith('#')
    assert len(result.confidence_color) == 7
