"""
VarianceScores model.
"""

from typing import Literal
from pydantic import BaseModel


class VarianceScores(BaseModel):
    """Stores total variance and its components."""
    answer_variance: float
    findings_variance: float
    citations_variance: float
    overall_reliability: float
    confidence_label: Literal['HIGH', 'MEDIUM', 'LOW']
