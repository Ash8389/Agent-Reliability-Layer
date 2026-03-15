# Agent Reliability Layer

> **Middleware SDK + REST API that wraps any LLM agent, runs it multiple times in parallel, detects contradictions, and tells you exactly what to fix when reliability is low.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-red.svg)](https://docs.pydantic.dev)
[![Tests](https://img.shields.io/badge/Tests-80%20passing-brightgreen.svg)](tests/)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What Does This Do?

LLM agents are non-deterministic. Ask the same question twice and you get two different answers. Sometimes they even contradict themselves. For casual use this is fine. For production — banks, hospitals, law firms, fintech — this is a dealbreaker.

This product wraps your existing agent, runs it multiple times, and gives you three things:

```
1. A reliability score     — how consistent is the agent?
2. A contradiction check   — do the runs logically contradict each other?
3. A remediation report    — if reliability is low, what exactly should you fix?
```

Two lines of code. No changes to your agent.

```python
from reliability_layer import ReliabilityLayer

rl = ReliabilityLayer(runs=3)
result = rl.wrap(your_agent).query("What are the risks of Drug X?")

print(result.reliability)           # 0.89
print(result.confidence)            # HIGH
print(result.contradiction_score)   # 0.012 — no contradictions
print(result.remediation_report)    # None required
```

---

## The Problem — In Plain English

```
Run 1: "Drug X is safe for pregnant women."
Run 2: "Drug X should be avoided during pregnancy."
Run 3: "Drug X has no known side effects."
```

Which answer do you trust? Without this product — you have no idea. You serve one of these to your user and hope for the best.

With this product:

```
Reliability:   0.21      CRITICAL
Contradiction: 0.891     ← runs directly contradict each other
Runs Agreed:   1/3

Remediation:
 [CRITICAL] Do not serve — flag for human review
 [HIGH]     Lower LLM temperature to 0.1-0.2
 [HIGH]     Add chain-of-thought structure to system prompt
```

You catch the failure before it reaches your user.

---

## Live Demo Output — Version 2

```
=======================================================
  Agent Reliability Layer — Live Groq Demo
=======================================================

Query: What will happen to the global economy in the next 5 years?
---------------------------------------------
Answer:      The global economy is expected to experience moderate
             growth, with potential risks including inflation,
             trade tensions, and geopolitical uncertainty.
Reliability: 0.850
Confidence:  MEDIUM
Runs Agreed: 2/5
Ans Variance:  0.169
Find Variance: 0.138
Cite Variance: 0.077
Contradiction: 0.923
■■ CRITICAL CONTRADICTION DETECTED
Remediation:
 [CRITICAL] Do not serve — flag for human review
Audit Trail: 5 runs stored

Query: Is cryptocurrency a good investment or a terrible idea?
---------------------------------------------
Answer:      Cryptocurrency can be a high-risk, high-reward
             investment, but it is not suitable for everyone.
Reliability: 0.847
Confidence:  MEDIUM
Runs Agreed: 5/5
Ans Variance:  0.039
Find Variance: 0.330
Cite Variance: 0.089
Contradiction: 0.002
Remediation:
 [HIGH] Add chain-of-thought structure to system prompt
Audit Trail: 5 runs stored

Query: What are the main causes of inflation?
---------------------------------------------
Answer:      The main causes of inflation are demand and supply
             imbalances, monetary policy, and external factors.
Reliability: 0.921
Confidence:  HIGH
Runs Agreed: 5/5
Ans Variance:  0.029
Find Variance: 0.130
Cite Variance: 0.124
Contradiction: 0.018
Remediation: None required
Audit Trail: 5 runs stored
```

---

## Three Layers of Detection

### Layer 1 — Semantic Consistency (Version 1)

Measures how differently the agent phrases its answers, reasons through findings, and cites sources across runs. Uses sentence embeddings and the Total Variance (TV) formula from the research paper.

```
Answer Variance   → is the agent giving the same answer?
Findings Variance → is the agent reasoning the same way?
Citations Variance → is the agent citing the same sources?
```

### Layer 2 — Logical Contradiction Detection (New in Version 2)

Uses a pretrained NLI (Natural Language Inference) model to check whether any two runs directly contradict each other. This catches failures that embedding variance misses entirely.

```
Run 1: "Drug X is safe."
Run 2: "Drug X is dangerous."

Embedding Variance → MEDIUM (they are somewhat different)
NLI Contradiction  → CRITICAL (they are logically opposite)
```

Embedding variance measures difference. NLI measures logical opposition. These are not the same thing.

### Layer 3 — Remediation Engine (New in Version 2)

When reliability is low, the system diagnoses which dimension failed and recommends the specific fix.

| Failure | What You See | What To Do |
|---------|-------------|------------|
| High answer variance | `[HIGH]` | Lower LLM temperature to 0.1-0.2 |
| High findings variance | `[HIGH]` | Add chain-of-thought to system prompt |
| High citations variance | `[MEDIUM]` | Pin sources via RAG |
| Critical contradiction | `[CRITICAL]` | Flag for human review — do not serve |
| Everything failing | `[CRITICAL]` | Review entire system prompt |

---

## Installation

### Prerequisites

- Python 3.11 or higher
- A free Groq API key — get one at https://console.groq.com/keys

### Step 1 — Clone

```bash
git clone https://github.com/Ash8389/Agent-Reliability-Layer.git
cd Agent-Reliability-Layer
```

### Step 2 — Create Virtual Environment

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install

**Windows:**
```powershell
.venv\Scripts\pip.exe install -e ".[dev]"
```

**macOS / Linux:**
```bash
pip install -e ".[dev]"
```

### Step 4 — Add API Key

```powershell
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env`:
```env
GROQ_API_KEY=gsk_your_key_here
```

### Step 5 — Verify

**Windows:**
```powershell
.venv\Scripts\python.exe -c "from reliability_layer import ReliabilityLayer; print('OK')"
```

**macOS / Linux:**
```bash
python -c "from reliability_layer import ReliabilityLayer; print('OK')"
```

Expected: `OK`

---

## Quick Start

### Run the Live Demo

**Windows:**
```powershell
.venv\Scripts\python.exe examples/with_groq_agent.py
```

**macOS / Linux:**
```bash
python examples/with_groq_agent.py
```

### Wrap Your Own Agent

```python
from reliability_layer import ReliabilityLayer

def my_agent(query: str) -> str:
    return call_your_llm(query)

rl = ReliabilityLayer(runs=3)
result = rl.wrap(my_agent).query("What are the risks of Drug X?")

# Core output
print(f"Answer:        {result.answer}")
print(f"Reliability:   {result.reliability}")
print(f"Confidence:    {result.confidence}")
print(f"Runs Agreed:   {result.runs_agreed}")

# Version 2 — contradiction detection
print(f"Contradiction: {result.contradiction_score:.3f}")
if result.has_critical_contradiction:
    print("WARNING: Do not serve this response")

# Version 2 — remediation
if result.remediation_report.recommendations:
    for rec in result.remediation_report.recommendations:
        print(f"[{rec.severity}] {rec.fix}")
else:
    print("Remediation: None required")
```

### Three Operating Modes

```python
# Standard — default, runs k times with variance scoring
rl = ReliabilityLayer(runs=3, mode="standard")

# Full — runs k times with variance + NLI contradiction check
rl = ReliabilityLayer(runs=5, mode="full")

# Adaptive — cheap fast path first, escalates only when needed
# Best for production at scale
rl = ReliabilityLayer(
    runs=3,
    mode="adaptive",
    escalate_threshold=0.75,   # escalate if reliability drops below this
    escalate_runs=5,           # use k=5 on escalation
)
```

**How adaptive mode works:**

```
Query arrives
    → Run k=2 quick check
    → Score reliability

If reliability > 0.75:
    → Return result fast (2 runs total, cheap)

If reliability ≤ 0.75:
    → Run k=5 full check
    → Run NLI contradiction detection
    → Return enhanced report with recommendations
```

High-reliability queries pay for 2 runs. Low-reliability queries get the full investigation.

---

## Understanding the Output

```python
result.answer                        # Consensus answer (clean text)
result.reliability                   # 0.0 to 1.0 overall score
result.confidence                    # "HIGH" / "MEDIUM" / "LOW"
result.runs_agreed                   # e.g. "3/3"

# Variance breakdown
result.variance_report.answer_variance      # How differently agent phrases answers
result.variance_report.findings_variance    # How consistently agent reasons
result.variance_report.citations_variance   # How consistently agent cites sources

# Version 2 — contradiction
result.contradiction_score           # 0.0 to 1.0 (above 0.7 = critical)
result.has_critical_contradiction    # True / False

# Version 2 — remediation
result.remediation_report.recommendations      # List of Recommendation objects
result.remediation_report.priority_fix         # Most urgent fix
result.remediation_report.needs_human_review   # True if CRITICAL found
result.remediation_report.estimated_improvement  # "30-50% variance reduction..."

# Audit
result.audit_trail                   # Every raw run stored for compliance
result.metadata                      # runs_executed, avg_duration_ms, timestamp
```

### Reliability Scale

| Score | Label | What It Means |
|-------|-------|---------------|
| 0.85 – 1.00 | HIGH | Production ready. Trust the answer. |
| 0.70 – 0.85 | MEDIUM | Usable. Add human review for edge cases. |
| 0.50 – 0.70 | LOW | Unreliable. Do not deploy in production. |
| 0.00 – 0.50 | CRITICAL | Agent is broken or prompt needs major work. |

### Contradiction Scale

| Score | Meaning |
|-------|---------|
| 0.00 – 0.30 | Logically consistent — runs agree |
| 0.30 – 0.70 | Some tension — monitor closely |
| 0.70 – 1.00 | CRITICAL — runs directly contradict each other |

### Healthy Variance Ranges

| Metric | Healthy | Concern If Above |
|--------|---------|-----------------|
| `answer_variance` | 0.0 – 0.2 | 0.3 — agent answers inconsistently |
| `findings_variance` | 0.0 – 0.4 | 0.5 — agent reasons differently each run |
| `citations_variance` | 0.0 – 0.35 | 0.5 — agent cites inconsistent sources |
| `contradiction_score` | 0.0 – 0.3 | 0.7 — runs are logically contradictory |

---

## REST API

### Start the Server

**Windows:**
```powershell
.venv\Scripts\uvicorn.exe reliability_layer.api:app --reload --port 8000
```

**macOS / Linux:**
```bash
uvicorn reliability_layer.api:app --reload --port 8000
```

Then open **http://localhost:8000/docs** for interactive API documentation.

### `GET /health`

```json
{
  "status": "ok",
  "version": "2.0.0",
  "timestamp": "2026-03-15T10:30:00Z"
}
```

### `POST /score`

Send pre-computed runs and get variance scores + contradiction + remediation back.

```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
    "runs": [
      {
        "answer": "Inflation is caused by money supply growth",
        "findings": ["Money supply grew 8%", "Demand outpaced supply"],
        "citations": ["Federal Reserve", "World Bank"]
      },
      {
        "answer": "Inflation is caused by money supply growth",
        "findings": ["Monetary expansion drove prices", "Supply constraints"],
        "citations": ["IMF", "Federal Reserve"]
      }
    ],
    "mode": "standard"
  }'
```

**Response:**
```json
{
  "answer_variance": 0.021,
  "findings_variance": 0.134,
  "citations_variance": 0.187,
  "overall_reliability": 0.886,
  "confidence_label": "HIGH",
  "contradiction_score": 0.012,
  "has_critical_contradiction": false,
  "remediation_report": {
    "recommendations": [],
    "priority_fix": null,
    "needs_human_review": false,
    "estimated_improvement": "Agent is reliable — no action needed"
  }
}
```

---

## Running Tests

```powershell
# Windows — run all 80 tests
.venv\Scripts\pytest.exe tests/ -v

# macOS / Linux
pytest tests/ -v
```

### Expected Output

```
tests/test_execution_engine.py           6 passed
tests/test_stabilization_engine.py      10 passed
tests/test_scoring_engine.py            15 passed
tests/test_response_builder.py          11 passed
tests/test_sdk.py                       13 passed
tests/test_integration.py              11 passed
tests/test_nli_checker.py               6 passed
tests/test_adaptive_mode.py             5 passed
tests/test_remediation_engine.py        6 passed
================================ 80 passed ================================
```

---

## How It Works — The Math

### Total Variance Formula

From the research paper arXiv:2602.23271:

```
TV(X) = (1 / 2n(n-1)) × Σᵢ Σⱼ ||xᵢ - xⱼ||²
```

Where `xᵢ` are L2-normalized sentence embedding vectors of each run's output.

```python
reliability = 1 - mean(answer_TV, findings_TV, citations_TV)
```

### NLI Contradiction Detection

Uses `cross-encoder/nli-MiniLM2-L6-H768` to classify the relationship between every pair of runs as entailment, neutral, or contradiction. Checks all n×(n-1)/2 unique pairs. Scores above 0.7 trigger CRITICAL.

### Why Both Are Needed

```
Semantic variance catches:   "different phrasing of similar ideas"
NLI contradiction catches:   "logically opposite statements"

Example:
  "The economy will grow slowly"  vs  "The economy will shrink"

  Embedding similarity: MEDIUM (somewhat different)
  NLI contradiction:    HIGH   (directly contradictory)
```

---

## Architecture

```
Your Agent
    │
    ▼
ReliabilityLayer(runs=3, mode="adaptive")
    │
    ├──► ExecutionEngine          Run agent k times in parallel
    │
    ├──► StabilizationEngine      Reduce variance before scoring
    │
    ├──► ScoringEngine            TV math + NLI contradiction
    │         ├── answer_variance()
    │         ├── findings_variance()
    │         ├── citations_variance()
    │         └── contradiction_variance()   ← New in V2
    │
    ├──► RemediationEngine        Diagnose failure + recommend fix
    │                             ← New in V2
    │
    ├──► ResponseBuilder          Package everything into typed output
    │
    ▼
SDK / REST API
```

---

## Choosing the Right Mode

| Use Case | Mode | Runs | Why |
|----------|------|------|-----|
| Developer testing | standard | 2–3 | Speed over precision |
| Production default | standard | 3 | Best cost vs signal |
| High volume production | adaptive | 3 → 5 | Cost-efficient escalation |
| Medical / Legal / Finance | full | 5–7 | Contradiction detection required |
| Compliance audits | full | 10 | Maximum evidence trail |

---

## Supported LLM Providers

Any LLM can be wrapped — the SDK is completely provider-agnostic:

| Provider | Example Model | Cost |
|----------|--------------|------|
| Groq | llama-3.3-70b-versatile | Free tier available |
| OpenAI | gpt-4o | Paid |
| Anthropic | claude-3-5-sonnet | Paid |
| Ollama | llama3, mistral | Free (local) |
| Any callable | custom endpoint | Varies |

---

## Project Structure

```
reliability-layer/
├── reliability_layer/
│   ├── __init__.py
│   ├── sdk.py                    # ReliabilityLayer + WrappedAgent + adaptive mode
│   ├── api.py                    # FastAPI REST endpoints
│   ├── execution_engine.py       # Module 01 — parallel execution
│   ├── stabilization_engine.py   # Module 02 — variance reduction
│   ├── scoring_engine.py         # Module 03 — TV math + NLI wiring
│   ├── response_builder.py       # Module 04 — output packaging
│   ├── nli_checker.py            # V2 — contradiction detection
│   ├── remediation_engine.py     # V2 — diagnose and recommend fixes
│   └── config.py
├── tests/                        # 80 automated tests
│   ├── test_execution_engine.py
│   ├── test_stabilization_engine.py
│   ├── test_scoring_engine.py
│   ├── test_response_builder.py
│   ├── test_sdk.py
│   ├── test_integration.py
│   ├── test_nli_checker.py
│   ├── test_adaptive_mode.py
│   └── test_remediation_engine.py
├── examples/
│   └── with_groq_agent.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Common Commands Reference

### Windows (PowerShell)

| Task | Command |
|------|---------|
| Install | `.venv\Scripts\pip.exe install -e ".[dev]"` |
| Run all tests | `.venv\Scripts\pytest.exe tests/ -v` |
| Run demo | `.venv\Scripts\python.exe examples/with_groq_agent.py` |
| Start API | `.venv\Scripts\uvicorn.exe reliability_layer.api:app --reload --port 8000` |
| Verify install | `.venv\Scripts\python.exe -c "from reliability_layer import ReliabilityLayer; print('OK')"` |

### macOS / Linux

| Task | Command |
|------|---------|
| Install | `pip install -e ".[dev]"` |
| Run all tests | `pytest tests/ -v` |
| Run demo | `python examples/with_groq_agent.py` |
| Start API | `uvicorn reliability_layer.api:app --reload --port 8000` |

---

## Troubleshooting

### Answer field is empty in output
Check your GROQ_API_KEY is set in `.env`. Verify the API call returns content before it enters the pipeline.

### Model loads twice on startup
`ContradictionDetector()` is being instantiated in more than one place. It should only exist inside `ScoringEngine.__init__()`.

### `ModuleNotFoundError: No module named 'transformers'`
```powershell
.venv\Scripts\pip.exe install transformers torch
```

### `ModuleNotFoundError: No module named 'sentence_transformers'`
```powershell
.venv\Scripts\pip.exe install sentence-transformers
```

### `GROQ_API_KEY not found`
Make sure `.env` exists in the project root with your key: `GROQ_API_KEY=gsk_your_key_here`

### Warnings during model load
These are safe to ignore:
```
Warning: unauthenticated requests to HF Hub   ← add HF_TOKEN to .env to silence
embeddings.position_ids | UNEXPECTED           ← cosmetic warning, no effect
```

### `make` is not recognized (Windows)
Use the direct commands from the table above.

---

## Research Foundation

This product implements findings from:

> **"Evaluating Stochasticity in Deep Research Agents"**
> arXiv:2602.23271 — https://arxiv.org/abs/2602.23271

Key techniques from the paper: Total Variance (TV) formula, structured output enforcement (22% variance reduction), query ensembling, and three-dimensional scoring across answers, findings, and citations.

---

## Roadmap

- [ ] Dashboard UI — per-agent reliability trends over time
- [ ] Regression alerts — notify when reliability drops below threshold
- [ ] Compliance PDF exports — audit-ready reliability reports
- [ ] LangChain / CrewAI / AutoGen native integrations
- [ ] Hosted API — no self-hosting required
- [ ] Factual grounding layer — RAG-based source verification (Layer 3)

---

## Contributing

1. Fork the repository
2. Create your branch: `git checkout -b feature/my-feature`
3. Run tests: `.venv\Scripts\pytest.exe tests/ -v`
4. All 80 tests must pass with 0 failures
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

Built by [@Ash8389](https://github.com/Ash8389)

---

*If this helped you, give it a ⭐ on GitHub*
