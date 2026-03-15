# tests/test_integration.py
import pytest, warnings, random, time
from reliability_layer import ReliabilityLayer
from reliability_layer.sdk import ReliabilityWarning
from reliability_layer.response_builder import ReliabilityResponse
from fastapi.testclient import TestClient
from reliability_layer.api import app

client = TestClient(app)

# ■■ Mock Agents ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def stable_agent(q):
    return 'Drug X causes hepatotoxicity (liver damage)'

def unstable_agent(q):
    import random
    # Semantically distant responses to ensure real variance
    responses = [
        'The stock market crashed due to poor earnings reports',
        'Photosynthesis converts sunlight into glucose in plants',
        'Ancient Rome fell due to military and economic pressures',
        'Quantum entanglement enables faster than light correlation',
        'The recipe requires two cups of flour and one egg',
    ]
    return random.choice(responses)

def partial_agent(q):
    if not hasattr(partial_agent, "counter"):
        partial_agent.counter = 0
    partial_agent.counter += 1
    return 'Drug X causes liver damage' if partial_agent.counter <= 2 else 'completely unknown differences'

def slow_agent(q):
    import time
    time.sleep(1.5)
    return 'too slow'

def test_unstable_agent_returns_response():
    rl = ReliabilityLayer(runs=3)
    result = rl.wrap(unstable_agent).query('test question')
    assert isinstance(result, ReliabilityResponse)
    assert len(result.audit_trail) == 3

# ■■ Scenario 3: Partial Agreement ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def test_partial_agreement_detected():
    """
    Proves that when 2 out of 3 runs agree, the system correctly identifies
    a '2/3' agreement rate and outputs a 'MEDIUM' confidence label.
    """
    partial_agent.counter = 0 # reset counter
    rl = ReliabilityLayer(runs=3)
    result = rl.wrap(partial_agent).query('test')
    
    assert isinstance(result, ReliabilityResponse)
    assert result.runs_agreed == '2/3'
    assert result.confidence == 'MEDIUM'

# ■■ Scenario 4: Timeout Handled Gracefully ■■■■■■■■■■■■■■■■■■■■
def test_timeout_does_not_crash_system():
    """
    Proves that when an agent exceeds the timeout, the error is gracefully
    captured in the audit_trail, and the system still returns a response.
    """
    rl = ReliabilityLayer(runs=2, timeout=0.5) 
    result = rl.wrap(slow_agent).query('test')
    
    assert isinstance(result, ReliabilityResponse)
    error_runs = [r for r in result.audit_trail if r.had_error]
    assert len(error_runs) > 0 # timeout should be recorded

# ■■ Scenario 5: REST API End-to-End ■■■■■■■■■■■■■■■■■■■■■■■■■■■
def test_rest_api_score_endpoint():
    """
    Proves that posting pre-computed runs to the /score REST API endpoint
    returns a valid 200 response with correct variance scoring JSON fields.
    """
    payload = {'runs': [
        {'answer':'1987','findings':['Revenue grew 12%','CEO left'],
        'citations':['https://reuters.com/article1']},
        {'answer':'1987','findings':['Revenue grew 12%','Leadership change'],
        'citations':['https://reuters.com/article1','https://bloomberg.com/2']},
        {'answer':'1988','findings':['Revenue grew','New management'],
        'citations':['https://reuters.com/article1']},
    ]}
    r = client.post('/score', json=payload)
    
    assert r.status_code == 200
    data = r.json()
    assert 'overall_reliability' in data
    assert 'confidence_label' in data
    assert 0.0 <= data['overall_reliability'] <= 1.0

# ■■ Scenario 6: Audit Trail Completeness ■■■■■■■■■■■■■■■■■■■■■■
def test_audit_trail_completeness():
    """
    Proves that the audit_trail contains exactly 'runs' number of entries
    and each entry contains essential attributes like run_id, answer, and duration.
    """
    rl = ReliabilityLayer(runs=4)
    result = rl.wrap(stable_agent).query('audit test')
    
    assert len(result.audit_trail) == 4
    for record in result.audit_trail:
        assert hasattr(record, 'run_id')
        assert hasattr(record, 'answer')
        assert hasattr(record, 'duration_ms')
        assert len(record.answer) <= 300
        assert record.duration_ms >= 0

# ■■ Scenario 7: Contradiction Detection ■■■■■■■■■■■■■■■■■■■■■■
def test_contradiction_score_in_response():
    """
    Proves that the contradiction_score is present in the ReliabilityResponse
    and is bounded between 0.0 and 1.0.
    """
    rl = ReliabilityLayer(runs=2)
    result = rl.wrap(stable_agent).query('contradiction test')
    
    assert hasattr(result, 'contradiction_score')
    assert result.contradiction_score >= 0.0
    assert result.contradiction_score <= 1.0

def test_no_critical_contradiction_for_stable_agent():
    """
    Proves that identical responses (from stable_agent) do not
    trigger a critical contradiction.
    """
    rl = ReliabilityLayer(runs=3)
    result = rl.wrap(stable_agent).query('contradiction test')
    
    assert hasattr(result, 'has_critical_contradiction')
    assert result.has_critical_contradiction is False

# ■■ Scenario 8: Phase 2 API Enhancements ■■■■■■■■■■■■■■■■■■■■■■
def test_api_score_endpoint_returns_contradiction():
    payload = {'runs': [
        {'answer': 'Treatment X is safe.', 'findings': [], 'citations': []},
        {'answer': 'Treatment X is safe.', 'findings': [], 'citations': []},
        {'answer': 'Treatment X is safe.', 'findings': [], 'citations': []}
    ], 'mode': 'standard', 'escalate_threshold': 0.75}
    r = client.post('/score', json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert 'contradiction_score' in data
    assert data['contradiction_score'] >= 0.0
    assert 'has_critical_contradiction' in data

def test_api_health_returns_v2():
    r = client.get('/health')
    assert r.status_code == 200
    data = r.json()
    assert data['version'] == "2.0.0"

def test_remediation_report_in_response():
    rl = ReliabilityLayer(runs=3)
    result = rl.wrap(stable_agent).query('remediation test')
    assert hasattr(result, 'remediation_report')
    assert result.remediation_report is not None

def test_stable_agent_no_remediation_needed():
    rl = ReliabilityLayer(runs=3)
    result = rl.wrap(stable_agent).query('remediation test')
    assert len(result.remediation_report.recommendations) == 0

def test_unstable_agent_has_recommendations():
    rl = ReliabilityLayer(runs=3)
    result = rl.wrap(unstable_agent).query('remediation test')
    assert len(result.remediation_report.recommendations) >= 1

def test_full_pipeline_v2_complete():
    rl = ReliabilityLayer(runs=3, mode="full")
    result = rl.wrap(stable_agent).query('v2 complete test')
    assert result.contradiction_score >= 0.0
    assert result.remediation_report is not None
    assert result.reliability >= 0.0
