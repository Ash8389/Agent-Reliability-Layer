from pydantic import BaseModel, field_validator
from datetime import datetime, timezone

class VarianceReport(BaseModel):
    answer_variance: float
    findings_variance: float
    citations_variance: float
    overall_reliability: float

    @field_validator('*', mode='before')
    @classmethod
    def check_float(cls, v):
        return float(v)

class RunRecord(BaseModel):
    run_id: int
    answer: str
    duration_ms: int
    had_error: bool = False

    @field_validator('run_id', 'duration_ms')
    @classmethod
    def check_int(cls, v: int) -> int:
        return v

    @field_validator('answer')
    @classmethod
    def check_answer(cls, v: str) -> str:
        return v[:300]

    @field_validator('had_error')
    @classmethod
    def check_bool(cls, v: bool) -> bool:
        return v

class ReliabilityResponse(BaseModel):
    answer: str
    reliability: float
    confidence: str
    runs_agreed: str
    variance_report: VarianceReport
    metadata: dict
    audit_trail: list[RunRecord]

    @field_validator('answer')
    @classmethod
    def check_answer(cls, v: str) -> str:
        return v

    @field_validator('reliability')
    @classmethod
    def check_reliability(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('reliability must be between 0.0 and 1.0')
        return v

    @field_validator('confidence')
    @classmethod
    def check_confidence(cls, v: str) -> str:
        if v not in ('HIGH', 'MEDIUM', 'LOW'):
            raise ValueError('confidence must be HIGH, MEDIUM, or LOW')
        return v

    @field_validator('runs_agreed')
    @classmethod
    def check_runs_agreed(cls, v: str) -> str:
        if '/' not in v:
            raise ValueError('runs_agreed must contain /')
        return v

    @field_validator('variance_report')
    @classmethod
    def check_variance_report(cls, v: VarianceReport) -> VarianceReport:
        return v

    @field_validator('metadata')
    @classmethod
    def check_metadata(cls, v: dict) -> dict:
        return v

    @field_validator('audit_trail')
    @classmethod
    def check_audit_trail(cls, v: list[RunRecord]) -> list[RunRecord]:
        return v

    @property
    def confidence_color(self) -> str:
        return {'HIGH': '#16A34A', 'MEDIUM': '#D97706', 'LOW': '#DC2626'}.get(self.confidence, '#64748B')
        
    def to_dict(self) -> dict:
        return self.model_dump()

class ResponseBuilder:
    def build(self, stabilized: dict, scores, raw_runs: list) -> ReliabilityResponse:
        final = stabilized['stabilized_output']
        agreed = sum(1 for r in raw_runs if self._match(r.raw_output, final))
        
        return ReliabilityResponse(
            answer=final,
            reliability=scores.overall_reliability,
            confidence=scores.confidence_label,
            runs_agreed=f'{agreed}/{len(raw_runs)}',
            variance_report=VarianceReport(
                answer_variance=scores.answer_variance,
                findings_variance=scores.findings_variance,
                citations_variance=scores.citations_variance,
                overall_reliability=scores.overall_reliability
            ),
            metadata={
                'runs_executed': len(raw_runs),
                'avg_duration_ms': int(sum(r.duration_ms for r in raw_runs) / len(raw_runs)) if raw_runs else 0,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            audit_trail=[
                RunRecord(
                    run_id=r.run_id,
                    answer=r.raw_output[:300],
                    duration_ms=r.duration_ms,
                    had_error=r.error is not None
                ) for r in raw_runs
            ]
        )

    def _match(self, output: str, final: str, threshold: float = 0.6) -> bool:
        fw = set(final.lower().split())
        ow = set(output.lower().split())
        return len(fw & ow) / len(fw) > threshold if fw else False
