# Agent Reliability Layer

> **Middleware SDK + REST API that wraps any LLM agent, runs queries multiple times in parallel, and returns a reliability score — so you know whether to trust the output.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-red.svg)](https://docs.pydantic.dev)
[![Tests](https://img.shields.io/badge/Tests-55%20passing-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## The Problem

LLM agents are non-deterministic. Ask the same question twice and you get two different answers. For casual use this is fine. For enterprise use — banks, hospitals, law firms — this is a dealbreaker.

```
Run 1: "Inflation is caused by money supply growth"
Run 2: "Inflation stems from demand-pull pressures"
Run 3: "The primary driver of inflation is monetary policy"

Which answer do you trust?
```

**Before this product:** No way to know.
**After this product:** A single reliability score tells you exactly how consistent the agent is.

---

## The Solution

```python
from reliability_layer import ReliabilityLayer

# Wrap your existing agent — no changes needed to your agent code
rl = ReliabilityLayer(runs=3)
result = rl.wrap(your_agent).query("What are the risks of Drug X?")

print(result.answer)       # Best consensus answer
print(result.reliability)  # 0.89
print(result.confidence)   # HIGH
print(result.runs_agreed)  # 3/3
```

---

## Live Demo Output

```
=======================================================
  Agent Reliability Layer — Live Groq Demo
=======================================================

Query: What are the main causes of inflation?
---------------------------------------------
Answer:      The main causes of inflation are demand and supply
             imbalances, monetary policy, and external factors
             such as exchange rates and commodity prices.
Reliability: 0.898
Confidence:  HIGH
Runs Agreed: 5/5
Ans Variance:  0.053
Find Variance: 0.130
Cite Variance: 0.124
Audit Trail:   5 runs stored

Query: What are the health risks of smoking?
---------------------------------------------
Answer:      Smoking poses significant health risks, including
             increased chances of developing heart disease,
             various types of cancer, and respiratory diseases.
Reliability: 0.838
Confidence:  MEDIUM
Runs Agreed: 5/5
Ans Variance:  0.029
Find Variance: 0.157
Cite Variance: 0.300
Audit Trail:   5 runs stored
```

---

## Research Foundation

This product directly implements findings from:

> **"Evaluating Stochasticity in Deep Research Agents"**
> arXiv:2602.23271 — https://arxiv.org/abs/2602.23271

Key techniques implemented from the paper:

- **Total Variance (TV) formula** — mathematical measurement of output consistency
- **Early-stage stochasticity control** — consensus-based query ensembling
- **Structured output enforcement** — reduces variance by 22% (per paper findings)
- **Three-dimensional scoring** — answers, findings, and citations scored separately

---

## Features

- **Reliability Score** — single 0.0–1.0 score based on Total Variance math
- **Three-Dimensional Variance** — separate scores for answers, findings, and citations
- **Semantic Scoring** — uses sentence embeddings, not brittle exact string matching
- **Parallel Execution** — runs k queries concurrently, no extra latency
- **Stabilization Engine** — structured output + query ensembling reduces variance
- **Full Audit Trail** — every run stored for enterprise compliance
- **Python SDK** — wrap any callable agent in 2 lines of code
- **REST API** — language-agnostic HTTP endpoints for Java, Node.js, Go clients
- **Framework Agnostic** — works with OpenAI, Anthropic, Groq, Ollama, or any LLM

---

## Architecture

```
Your Agent
    │
    ▼
ReliabilityLayer(runs=3)
    │
    ├──► ExecutionEngine        Module 01 — run k times in parallel
    │         │
    │         ▼
    │    [RunResult × k]        k raw LLM outputs with timing
    │
    ├──► StabilizationEngine    Module 02 — reduce variance
    │         │
    │         ▼
    │    StabilizedOutput       consensus answer + parsed JSON
    │
    ├──► ScoringEngine          Module 03 — measure variance (TV math)
    │         │
    │         ▼
    │    VarianceScores         answer / findings / citations TV
    │
    ├──► ResponseBuilder        Module 04 — package output
    │         │
    │         ▼
    │    ReliabilityResponse    typed Pydantic object
    │
    ▼
SDK / REST API                  Module 05 — deliver to customer
```

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Ash8389/Agent-Reliability-Layer.git
cd Agent-Reliability-Layer
```

### Step 2 — Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install Dependencies

**Windows:**
```powershell
.venv\Scripts\pip.exe install -e ".[dev]"
```

**macOS / Linux:**
```bash
pip install -e ".[dev]"
```

### Step 4 — Verify Installation

**Windows:**
```powershell
.venv\Scripts\python.exe -c "from reliability_layer import ReliabilityLayer; print('OK')"
```

**macOS / Linux:**
```bash
python -c "from reliability_layer import ReliabilityLayer; print('OK')"
```

Expected output: `OK`

---

## Configuration

### Create `.env` File

**Windows:**
```powershell
copy .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

### Edit `.env` with Your API Keys

```env
# Required — get a FREE key at https://console.groq.com/keys
GROQ_API_KEY=gsk_your_groq_key_here

# Optional — OpenAI alternative
OPENAI_API_KEY=sk_your_openai_key_here

# Optional — silences HuggingFace rate limit warning
HF_TOKEN=hf_your_token_here

# Optional — these are already the defaults
RELIABILITY_DEFAULT_RUNS=3
RELIABILITY_DEFAULT_TIMEOUT=30
RELIABILITY_DEFAULT_MODE=stabilize
RELIABILITY_LOG_LEVEL=INFO
```

> **Never commit your `.env` file.** It is already listed in `.gitignore`.

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

### Python SDK — Basic Usage

```python
from reliability_layer import ReliabilityLayer

def my_agent(query: str) -> str:
    # Replace with your actual LLM call
    return call_your_llm(query)

rl = ReliabilityLayer(runs=3)
result = rl.wrap(my_agent).query("What are the risks of Drug X?")

print(f"Answer:      {result.answer}")
print(f"Reliability: {result.reliability}")
print(f"Confidence:  {result.confidence}")
print(f"Runs Agreed: {result.runs_agreed}")
print(f"Audit Trail: {len(result.audit_trail)} runs stored")
```

### Python SDK — With Groq (Free LLM API)

```python
from groq import Groq
from reliability_layer import ReliabilityLayer
from reliability_layer.config import settings

client = Groq(api_key=settings.groq_api_key)

def groq_agent(query: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """Respond ONLY in this JSON format:
{
  "main_answer": "<direct one sentence answer>",
  "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],
  "confidence": "<HIGH|MEDIUM|LOW>",
  "sources_used": ["<source 1>", "<source 2>"]
}"""
            },
            {"role": "user", "content": query}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

rl = ReliabilityLayer(runs=3)
result = rl.wrap(groq_agent).query("What causes inflation?")
print(f"Reliability: {result.reliability} — {result.confidence}")
```

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

---

### `GET /health`

Check if the server is running.

**Windows:**
```powershell
curl.exe http://localhost:8000/health
```

**macOS / Linux:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2026-03-01T10:30:00Z"
}
```

---

### `POST /score`

Score pre-computed runs without calling any agent.
Use this if you already have LLM outputs and just want the variance scores.

**macOS / Linux:**
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
      },
      {
        "answer": "Inflation is caused by money supply growth",
        "findings": ["Money supply grew 8%", "Demand pressures"],
        "citations": ["Federal Reserve", "Reuters"]
      }
    ]
  }'
```

**Windows — use the /docs UI at http://localhost:8000/docs instead of curl for easier testing.**

**Response:**
```json
{
  "answer_variance": 0.021,
  "findings_variance": 0.134,
  "citations_variance": 0.187,
  "overall_reliability": 0.886,
  "confidence_label": "HIGH"
}
```

---

## Running Tests

### Run All 55 Tests

**Windows:**
```powershell
.venv\Scripts\pytest.exe tests/ -v
```

**macOS / Linux:**
```bash
pytest tests/ -v
```

### Run Specific Module Tests

**Windows:**
```powershell
.venv\Scripts\pytest.exe tests/test_execution_engine.py -v
.venv\Scripts\pytest.exe tests/test_scoring_engine.py -v
.venv\Scripts\pytest.exe tests/test_integration.py -v
```

**macOS / Linux:**
```bash
pytest tests/test_execution_engine.py -v
pytest tests/test_scoring_engine.py -v
pytest tests/test_integration.py -v
```

### Run with Coverage Report

**Windows:**
```powershell
.venv\Scripts\pytest.exe tests/ -v --cov=reliability_layer
```

**macOS / Linux:**
```bash
pytest tests/ --cov=reliability_layer
```

### Expected Output

```
tests/test_execution_engine.py         6 passed
tests/test_stabilization_engine.py    10 passed
tests/test_scoring_engine.py          13 passed
tests/test_response_builder.py         9 passed
tests/test_sdk.py                     11 passed
tests/test_integration.py              6 passed
================================ 55 passed ================================
```

---

## Common Commands Reference

### Windows (PowerShell)

| Task | Command |
|------|---------|
| Activate venv | `.venv\Scripts\activate` |
| Install dependencies | `.venv\Scripts\pip.exe install -e ".[dev]"` |
| Run all tests | `.venv\Scripts\pytest.exe tests/ -v` |
| Start API server | `.venv\Scripts\uvicorn.exe reliability_layer.api:app --reload --port 8000` |
| Run demo | `.venv\Scripts\python.exe examples/with_groq_agent.py` |
| Verify install | `.venv\Scripts\python.exe -c "from reliability_layer import ReliabilityLayer; print('OK')"` |
| Format code | `.venv\Scripts\ruff.exe format .` |
| Lint code | `.venv\Scripts\ruff.exe check .` |

### macOS / Linux

| Task | Command |
|------|---------|
| Activate venv | `source .venv/bin/activate` |
| Install dependencies | `pip install -e ".[dev]"` |
| Run all tests | `pytest tests/ -v` |
| Start API server | `uvicorn reliability_layer.api:app --reload --port 8000` |
| Run demo | `python examples/with_groq_agent.py` |
| Format code | `ruff format .` |
| Lint code | `ruff check .` |

> macOS / Linux users can also use `make install`, `make test`, `make run` etc.

---

## Configuration Options

```python
# Default — good for most use cases
rl = ReliabilityLayer(runs=3)

# Higher confidence — for important decisions
rl = ReliabilityLayer(runs=5)

# Maximum reliability measurement — for audits
rl = ReliabilityLayer(runs=10)

# Audit only — measure without stabilization
rl = ReliabilityLayer(runs=3, mode="audit")

# Custom timeout per run (seconds)
rl = ReliabilityLayer(runs=3, timeout=60)

# Fluent configuration
rl = ReliabilityLayer().configure(runs=5).configure(timeout=60)
```

### Choosing the Right `runs` Value

| Use Case | Recommended | Reason |
|----------|-------------|--------|
| Developer testing | 2–3 | Speed over precision |
| Production API | 3 | Best cost vs signal balance |
| Medical / Legal decisions | 5–7 | Higher stakes need more evidence |
| Compliance audits | 10 | Maximum evidence trail |
| Real-time chatbot | 1 | No latency budget |

---

## Understanding the Output

```python
result.answer              # Consensus stabilized answer (clean text)
result.reliability         # 0.0 to 1.0 overall consistency score
result.confidence          # "HIGH" / "MEDIUM" / "LOW"
result.runs_agreed         # e.g. "3/3" — how many runs matched
result.variance_report
  .answer_variance         # How differently agent phrases answers
  .findings_variance       # How consistently agent reasons
  .citations_variance      # How consistently agent cites sources
result.metadata            # runs_executed, avg_duration_ms, timestamp
result.audit_trail         # Every raw run stored for compliance
```

### Reliability Scale

| Score | Label | What It Means |
|-------|-------|---------------|
| 0.85 – 1.00 | HIGH | Production ready. Trust the answer. |
| 0.70 – 0.85 | MEDIUM | Usable. Add human review for edge cases. |
| 0.50 – 0.70 | LOW | Unreliable. Do not deploy in production. |
| 0.00 – 0.50 | CRITICAL | Agent is broken or prompt needs fixing. |

### Healthy Variance Ranges

| Metric | Healthy Range | Concern If Above |
|--------|--------------|-----------------|
| `answer_variance` | 0.0 – 0.2 | 0.3 — agent is inconsistent |
| `findings_variance` | 0.0 – 0.4 | 0.5 — reasoning is unstable |
| `citations_variance` | 0.0 – 0.35 | 0.5 — sources are unreliable |

---

## How It Works — The Math

The core metric is **Total Variance (TV)** directly from the research paper:

```
TV(X) = (1 / 2n(n-1)) × Σᵢ Σⱼ ||xᵢ - xⱼ||²
```

Where `xᵢ` are L2-normalized semantic embedding vectors of each run's output.

```python
reliability = 1 - mean(answer_TV, findings_TV, citations_TV)
```

Key implementation decisions:
- Vectors are **L2 normalized** before TV computation — ensures 0.0 to 1.0 range
- **Semantic embeddings** used instead of exact string matching — handles natural LLM variation
- **Three separate scorers** — because answers, findings, and citations have different variance profiles
- **`all-MiniLM-L6-v2`** sentence transformer — fast, accurate, cached locally after first run

---

## Supported LLM Providers

Any LLM can be wrapped — the SDK is completely provider-agnostic:

| Provider | Example Model | Cost |
|----------|--------------|------|
| Groq | llama-3.3-70b-versatile | Free tier available |
| OpenAI | gpt-4o | Paid |
| Anthropic | claude-3-5-sonnet | Paid |
| Ollama | llama3, mistral | Free (runs locally) |
| Any REST API | custom endpoint | Varies |

---

## Project Structure

```
reliability-layer/
├── reliability_layer/           # Main package
│   ├── __init__.py              # ReliabilityLayer export + version
│   ├── sdk.py                   # ReliabilityLayer + WrappedAgent
│   ├── api.py                   # FastAPI REST endpoints
│   ├── execution_engine.py      # Module 01 — parallel execution
│   ├── stabilization_engine.py  # Module 02 — variance reduction
│   ├── scoring_engine.py        # Module 03 — TV math scoring
│   ├── response_builder.py      # Module 04 — output packaging
│   ├── config.py                # Pydantic settings from .env
│   ├── models/
│   │   ├── run_result.py
│   │   ├── variance_scores.py
│   │   ├── reliability_response.py
│   │   └── stabilized_output.py
│   └── utils/
│       ├── text_utils.py
│       ├── url_utils.py
│       └── logger.py
├── tests/                       # 55 automated tests
│   ├── conftest.py
│   ├── test_execution_engine.py    # 6 tests
│   ├── test_stabilization_engine.py # 10 tests
│   ├── test_scoring_engine.py      # 13 tests
│   ├── test_response_builder.py    # 9 tests
│   ├── test_sdk.py                 # 11 tests
│   └── test_integration.py         # 6 end-to-end tests
├── examples/
│   ├── basic_usage.py
│   ├── with_groq_agent.py       # Start here for live demo
│   └── with_openai_agent.py
├── docs/
│   └── architecture.md
├── .env.example                 # Copy to .env and add your keys
├── .gitignore
├── Makefile                     # Build commands (macOS/Linux only)
├── pyproject.toml
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'sentence_transformers'`
```powershell
# Windows
.venv\Scripts\pip.exe install sentence-transformers

# macOS / Linux
pip install sentence-transformers
```

### `ModuleNotFoundError: No module named 'groq'`
```powershell
# Windows
.venv\Scripts\pip.exe install groq

# macOS / Linux
pip install groq
```

### `GROQ_API_KEY not found`
Make sure `.env` exists in the project root with your key:
```powershell
# Windows — view .env contents
type .env
```

### `make` is not recognized (Windows)
`make` is a Linux/Mac tool. Use the direct commands from the
**Common Commands Reference** table instead. For example use
`.venv\Scripts\pytest.exe tests/ -v` instead of `make test`.

### Model downloading on every run
The sentence transformer caches after first download. Cache location on Windows:
```
C:\Users\YourName\.cache\torch\sentence_transformers\
```

### Port 8000 already in use
```powershell
# Windows — find what is using port 8000
netstat -ano | findstr :8000
# Then kill it (replace 1234 with the PID shown)
taskkill /PID 1234 /F
```

### Warnings during model load (safe to ignore)
These three messages are harmless and do not affect accuracy:
```
Warning: unauthenticated requests to HF Hub   ← add HF_TOKEN to silence
embeddings.position_ids | UNEXPECTED           ← known cosmetic warning
Loading weights: 100%                          ← normal first-run load
```

---

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Run tests before committing:
   - Windows: `.venv\Scripts\pytest.exe tests/ -v`
   - macOS/Linux: `pytest tests/ -v`
4. Ensure all 55 tests pass with 0 failures
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

---

## Roadmap

- [ ] Dashboard UI — per-agent reliability trends over time
- [ ] Regression alerts — notify when reliability drops below threshold
- [ ] Compliance PDF exports — audit-ready reliability reports
- [ ] LangChain / CrewAI / AutoGen native integrations
- [ ] Benchmark dataset — industry-specific reliability thresholds
- [ ] Hosted API — no self-hosting required

---

## Research Reference

**"Evaluating Stochasticity in Deep Research Agents"**
arXiv:2602.23271
https://arxiv.org/abs/2602.23271

Key findings implemented:
- Total Variance (TV) metric for measuring output stochasticity
- Early-stage stochasticity propagates most strongly to final outputs
- Structured output + consensus query ensembling reduces variance by 22%
- Findings are more variable than citations across runs

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

Built by [@Ash8389](https://github.com/Ash8389)

---

*If this project helped you, give it a ⭐ on GitHub*
