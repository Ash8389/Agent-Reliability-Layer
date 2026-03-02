# Agent Reliability Layer

Middleware SDK + REST API that wraps LLM agents, runs queries multiple times,
scores output consistency using Total Variance (TV) metric, and returns a
reliability-scored response with full audit trail.

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Installation
```bash
pip install reliability-layer
```

## Usage
```python
from reliability_layer import ReliabilityLayer

rl = ReliabilityLayer()
wrapped = rl.wrap(lambda x: "response")
print(rl.query(wrapped, prompt="Test").reliability)
```

## Architecture
See `docs/architecture.md` for complete details on the pipeline.

## API Reference
Start the API with `make run` and view the Swagger docs.

## Development
See `Makefile`.

## Running Tests
```bash
make test
```

## Contributing
Detailed guides inside docs.
