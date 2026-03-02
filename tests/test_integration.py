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
