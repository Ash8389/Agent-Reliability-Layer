"""
RunResult model.
"""

from typing import Optional
from pydantic import BaseModel


class RunResult(BaseModel):
    """Result of a single agent execution run."""
    run_id: int
    raw_output: str
    duration_ms: int
    error: Optional[str] = None
    timestamp: str
