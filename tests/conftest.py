"""
Pytest fixtures.
"""

import pytest
from typing import Any
from reliability_layer.models.run_result import RunResult
from reliability_layer.models.variance_scores import VarianceScores
from reliability_layer.models.stabilized_output import StabilizedOutput


@pytest.fixture
def stable_agent() -> Any:
    """Returns an agent function that always returns the same string."""
    def agent(*args: Any, **kwargs: Any) -> str:
        return "Stable output"
    return agent


@pytest.fixture
def unstable_agent() -> Any:
    """Returns an agent function that returns a random string each call."""
    import random
    def agent(*args: Any, **kwargs: Any) -> str:
        return f"Random output {random.randint(1, 1000)}"
    return agent


@pytest.fixture
def sample_runs() -> list[RunResult]:
    """Returns a list of 3 mock RunResult objects."""
    return [
        RunResult(run_id=1, raw_output="Run 1 output", duration_ms=100, timestamp="2023-01-01T12:00:00Z"),
        RunResult(run_id=2, raw_output="Run 2 output", duration_ms=110, timestamp="2023-01-01T12:00:01Z"),
        RunResult(run_id=3, raw_output="Run 3 output", duration_ms=105, timestamp="2023-01-01T12:00:02Z"),
    ]


@pytest.fixture
def sample_variance_scores() -> VarianceScores:
    """Returns a mock VarianceScores with HIGH confidence."""
    return VarianceScores(
        answer_variance=0.1,
        findings_variance=0.1,
        citations_variance=0.1,
        overall_reliability=0.9,
        confidence_label="HIGH"
    )


@pytest.fixture
def sample_stabilized() -> StabilizedOutput:
    """Returns a mock StabilizedOutput."""
    return StabilizedOutput(
        stabilized_output="Stabilized mock output",
        method_used="ensemble",
        agreement_rate=0.95
    )
