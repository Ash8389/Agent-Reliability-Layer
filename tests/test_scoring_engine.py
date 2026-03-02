import pytest
from reliability_layer.scoring_engine import ScoringEngine, VarianceScores

engine = ScoringEngine(fast_mode=True)

# ■■ Answer Variance Tests ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def test_answer_variance_zero_on_agreement():
    assert engine.answer_variance(['1987','1987','1987']) == 0.0

def test_answer_variance_max_on_all_different():
    score = engine.answer_variance(['A','B','C'])
    assert score == 1.0

def test_answer_variance_partial():
    score = engine.answer_variance(['A','A','B'])
    assert 0.0 < score < 1.0


# ■■ Findings Variance Tests ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def test_findings_variance_zero_on_identical():
    f = [['Revenue grew 12%', 'CEO changed']] * 3
    score = engine.findings_variance(f)
    assert score < 0.05 # near zero

def test_findings_variance_high_on_different():
    f = [['Drug causes liver damage'],
         ['The product revenue doubled'],
         ['Interest rates rose sharply']]
    score = engine.findings_variance(f)
    assert score > 0.3 # substantial variance

def test_findings_variance_empty_returns_zero():
    assert engine.findings_variance([[], [], []]) == 0.0


# ■■ Citations Variance Tests ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def test_citations_variance_zero_on_same_urls():
    c = [['https://source1.com','https://source2.com']] * 3
    assert engine.citations_variance(c) == 0.0

def test_citations_variance_handles_url_normalization():
    # These should be treated as the same URL
    c = [['https://www.source1.com/'],
         ['http://source1.com'],
         ['https://source1.com']]
    score = engine.citations_variance(c)
    assert score < 0.05 # normalized, should be near zero

def test_citations_variance_different_sources():
    c = [['https://a.com'],['https://b.com'],['https://c.com']]
    assert engine.citations_variance(c) == 1.0


# ■■ Master Compute Tests ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def test_compute_returns_variance_scores():
    runs = [{'answer':'1987','findings':['Revenue grew'],'citations':['http://a.com']}] * 3
    result = engine.compute(runs)
    assert isinstance(result, VarianceScores)
    assert result.confidence_label == 'HIGH'
    assert result.overall_reliability > 0.9

def test_compute_low_confidence_on_chaos():
    runs = [
        {'answer':'1987','findings':['X happened'],'citations':['http://a.com']},
        {'answer':'1992','findings':['Y happened'],'citations':['http://b.com']},
        {'answer':'2001','findings':['Z happened'],'citations':['http://c.com']},
    ]
    result = engine.compute(runs)
    assert result.confidence_label in ('LOW', 'MEDIUM')
    assert result.overall_reliability < 0.7

def test_reliability_score_not_none():
    runs = [{'answer':'A','findings':['f1'],'citations':['http://x.com']}] * 3
    result = engine.compute(runs)
    assert 0.0 <= result.overall_reliability <= 1.0


def test_reliability_is_between_0_and_1():
    """
    Boundary validation test.
    Guards against normalization bugs where overall_reliability
    could exceed 1.0 or drop below 0.0.
    """
    runs = [
        {'answer': 'A', 'findings': ['f1'], 'citations': ['http://x.com']}
    ] * 3
    result = engine.compute(runs)
    assert 0.0 <= result.overall_reliability <= 1.0
