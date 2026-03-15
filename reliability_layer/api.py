import time
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import httpx
import asyncio

from reliability_layer.sdk import ReliabilityLayer
from reliability_layer.scoring_engine import ScoringEngine
from reliability_layer.remediation_engine import RemediationEngine
from reliability_layer import __version__
import dataclasses

logger = logging.getLogger("reliability_layer.api")
logging.basicConfig(level=logging.INFO)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Agent Reliability Layer", version=__version__)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    query: str
    agent_endpoint: str
    runs: int = 3
    mode: str = 'stabilize'


class ScoreRun(BaseModel):
    answer: str
    findings: List[str]
    citations: List[str]


class ScoreRequest(BaseModel):
    runs: List[ScoreRun]
    mode: str = "standard"
    escalate_threshold: float = 0.75


class ScoreResponse(BaseModel):
    answer_variance: float
    findings_variance: float
    citations_variance: float
    overall_reliability: float
    confidence_label: str
    contradiction_score: float
    has_critical_contradiction: bool
    remediation_report: Optional[Dict[str, Any]] = None


async def call_agent_endpoint(url: str, query: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json={"query": query}, timeout=120.0)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and "answer" in data:
                return data["answer"]
            return response.text
        except httpx.HTTPError as e:
            raise Exception(f"Agent HTTP error: {e}")
        except Exception as e:
            raise Exception(f"Agent connection error: {str(e)}")


@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze_endpoint(request: Request, payload: AnalyzeRequest):
    start_time = time.time()
    query_hash = hashlib.md5(payload.query.encode()).hexdigest()

    async def wrapped_agent(q):
        return await call_agent_endpoint(payload.agent_endpoint, q)
    
    rl = ReliabilityLayer(runs=payload.runs, mode=payload.mode)
    
    try:
        # We need to run `rl.analyze` within `asyncio.wait_for`.
        # However `rl.analyze` is synchronous (calls asyncio.run internally) which will fail if called from a running event loop unless put in a thread.
        # But `call_agent_endpoint` is async. Wait! The prompt's sdk.py `def query(self, question: str)` calls `asyncio.run(self._run(question))`.
        # You cannot call `asyncio.run()` from within an async FastApi endpoint securely unless you run it in a thread, or you make it async.
        # Wait, the `WrappedAgent.query` calls `asyncio.run`.
        result = await asyncio.wait_for(
            asyncio.to_thread(rl.analyze, payload.query, wrapped_agent),
            timeout=120.0
        )
        
        duration = time.time() - start_time
        
        logger.info(
            f"timestamp={datetime.now(timezone.utc).isoformat()} "
            f"query_hash={query_hash} "
            f"runs={payload.runs} "
            f"duration={duration:.2f}s "
            f"reliability_score={result.reliability}"
        )
        
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@app.post("/score", response_model=ScoreResponse)
@limiter.limit("10/minute")
async def score_endpoint(request: Request, payload: ScoreRequest):
    start_time = time.time()
    rl = ReliabilityLayer(mode=payload.mode, escalate_threshold=payload.escalate_threshold)
    scorer = ScoringEngine()
    
    # Convert payload runs to list of dicts
    runs_dicts = [run.model_dump() for run in payload.runs]
    scores = scorer.compute(runs_dicts)
    
    c_score = 0.0
    has_crit = False
    if getattr(scores, 'contradiction_result', None):
        c_score = scores.contradiction_result.max_contradiction
        has_crit = scores.contradiction_result.has_critical_contradiction

    report = RemediationEngine().diagnose(
        answer_variance=scores.answer_variance,
        findings_variance=scores.findings_variance,
        citations_variance=scores.citations_variance,
        contradiction_score=c_score,
        overall_reliability=scores.overall_reliability
    )

    return ScoreResponse(
        answer_variance=scores.answer_variance,
        findings_variance=scores.findings_variance,
        citations_variance=scores.citations_variance,
        overall_reliability=scores.overall_reliability,
        confidence_label=scores.confidence_label,
        contradiction_score=c_score,
        has_critical_contradiction=has_crit,
        remediation_report=dataclasses.asdict(report)
    )


@app.get("/health")
async def health_endpoint():
    return {
        "status": "ok",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
