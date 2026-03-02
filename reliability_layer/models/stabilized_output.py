"""
StabilizedOutput model.
"""

from pydantic import BaseModel


class StabilizedOutput(BaseModel):
    """Holds the result of the stabilization engine."""
    stabilized_output: str
    method_used: str
    agreement_rate: float
