"""
ReliabilityResponse model.
"""

from typing import Any, Dict, List
from pydantic import BaseModel

from .run_result import RunResult
from .variance_scores import VarianceScores


class ReliabilityResponse(BaseModel):
    """The final response object returned by the Reliability Layer."""
    answer: str
    reliability: float
    confidence: str
    runs_agreed: str
    variance_report: VarianceScores
    metadata: Dict[str, Any]
    audit_trail: List[RunResult]

    @property
    def confidence_color(self) -> str:
        """Returns a hex color based on confidence level."""
        colors = {
            "HIGH": "#00FF00",
            "MEDIUM": "#FFFF00",
            "LOW": "#FF0000"
        }
        return colors.get(self.confidence.upper(), "#FFFFFF")

    def to_dict(self) -> Dict[str, Any]:
        """Converts the model to a dictionary."""
        return self.model_dump()
