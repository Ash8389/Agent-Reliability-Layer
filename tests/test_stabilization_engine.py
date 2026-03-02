"""
Tests for StabilizationEngine Python implementation.
"""

import pytest
# The user's code snippet uses:
# from stabilization_engine import StructuredOutputEnforcer, QueryEnsembler
# But based on typical module structure we might need absolute import:
from reliability_layer.stabilization_engine import StructuredOutputEnforcer, QueryEnsembler

enforcer = StructuredOutputEnforcer()
ensembler = QueryEnsembler()

# ■■ Structured Output Tests ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

def test_wrap_prompt_appends_schema():
    wrapped = enforcer.wrap_prompt('What is drug X risk?')
    assert 'main_answer' in wrapped
    assert 'key_findings' in wrapped
    assert 'sources_used' in wrapped

def test_parse_clean_json():
    raw = '{"main_answer":"yes","key_findings":["f1"],"confidence":"HIGH","sources_used":["http://x.com"]}'
    result = enforcer.parse_output(raw)
    assert result['main_answer'] == 'yes'

def test_parse_json_with_markdown_fences():
    raw = '```json\n{"main_answer":"yes","key_findings":[],"confidence":"LOW","sources_used":[]}\n```'
    result = enforcer.parse_output(raw)
    assert isinstance(result, dict)

def test_parse_json_embedded_in_text():
    raw = 'Here is my answer: {"main_answer":"no","key_findings":["x"],"confidence":"MEDIUM","sources_used":[]} Thanks!'
    result = enforcer.parse_output(raw)
    assert result['main_answer'] == 'no'

def test_parse_raises_on_no_json():
    with pytest.raises((ValueError, Exception)):
        enforcer.parse_output('this has no JSON at all')

# ■■ Query Ensembler Tests ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

def test_early_step_returns_intersection():
    queries = [['drug liver','drug dose'],['drug liver','drug warning'],['drug liver','drug interaction']]
    result = ensembler.get_consensus_queries(queries, step=1, total_steps=5)
    assert 'drug liver' in result
    assert len(result) == 1  # only the common query

def test_late_step_returns_all_queries():
    queries = [['q1','q2'],['q3','q4'],['q5','q6']]
    result = ensembler.get_consensus_queries(queries, step=4, total_steps=5)
    assert len(result) >= 5  # union = all queries

def test_empty_intersection_falls_back():
    queries = [['a','b'],['c','d'],['e','f']]  # no overlap
    result = ensembler.get_consensus_queries(queries, step=1, total_steps=5)
    assert result == ['a','b']  # fallback to run 1

def test_agreement_rate_perfect():
    queries = [['drug liver'],['drug liver'],['drug liver']]
    rate = ensembler.compute_agreement_rate(queries)
    assert rate == 1.0

def test_agreement_rate_zero():
    queries = [['a'],['b'],['c']]
    rate = ensembler.compute_agreement_rate(queries)
    assert rate == 0.0
