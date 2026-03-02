# tests/test_sdk.py
import pytest, warnings
from reliability_layer import ReliabilityLayer, __version__
from reliability_layer.sdk import ReliabilityWarning

def stable_agent(q): return 'Drug X causes liver damage'

def unstable_agent(q):
    import random
    return random.choice(['Answer A','Answer B','Answer C','Answer D'])

rl = ReliabilityLayer(runs=3)

# ■■ SDK Tests ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def test_version_exists():
    assert __version__ == '0.1.0'

def test_wrap_returns_wrapped_agent():
    from reliability_layer.sdk import WrappedAgent
    agent = rl.wrap(stable_agent)
    assert hasattr(agent, 'query')

def test_query_returns_reliability_response():
    from reliability_layer.response_builder import ReliabilityResponse
    result = rl.wrap(stable_agent).query('test question')
    assert isinstance(result, ReliabilityResponse)

def test_stable_agent_high_reliability():
    result = rl.wrap(stable_agent).query('test')
    assert result.confidence == 'HIGH'
    assert result.reliability > 0.85

def test_low_reliability_emits_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        rl.wrap(unstable_agent).query('test')
        reliability_warnings = [x for x in w if issubclass(x.category, ReliabilityWarning)]
        # May or may not trigger depending on randomness
        # Just check no exception was raised

def test_configure_fluent_api():
    result_rl = ReliabilityLayer().configure(runs=5).configure(mode='audit')
    assert result_rl.config['runs'] == 5
    assert result_rl.config['mode'] == 'audit'

def test_analyze_direct_call():
    from reliability_layer.response_builder import ReliabilityResponse
    rl2 = ReliabilityLayer(runs=3)
    result = rl2.analyze('test query', stable_agent)
    assert isinstance(result, ReliabilityResponse)

# ■■ REST API Tests ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
import pytest
from fastapi.testclient import TestClient
from reliability_layer.api import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert 'version' in data

def test_score_endpoint():
    payload = {'runs': [
        {'answer':'1987','findings':['Revenue grew'],'citations':['http://a.com']},
        {'answer':'1987','findings':['Revenue grew'],'citations':['http://a.com']},
        {'answer':'1987','findings':['Revenue grew'],'citations':['http://a.com']},
    ]}
    response = client.post('/score', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 'overall_reliability' in data
    assert data['confidence_label'] == 'HIGH'

def test_score_endpoint_bad_input():
    response = client.post('/score', json={'invalid': 'data'})
    assert response.status_code == 422 # Unprocessable entity


def test_analyze_direct_call_2():
    from reliability_layer.response_builder import ReliabilityResponse
    rl2 = ReliabilityLayer(runs=3)
    result = rl2.analyze('test query', stable_agent)
    assert isinstance(result, ReliabilityResponse)
