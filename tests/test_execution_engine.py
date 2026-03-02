import asyncio
import pytest
import time
from reliability_layer.execution_engine import ExecutionEngine, RunResult

# ■■ Mock agents ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def mock_deterministic(q): return 'Always same answer'
def mock_random(q):
    import random; return random.choice(['A','B','C'])
def mock_slow(q):
    time.sleep(35); return 'too slow' # triggers timeout
def mock_crash(q): raise ValueError('Agent crashed')

# ■■ Test 1: Returns exactly k results ■■■■■■■■■■■■■■■■■■■■■■■■■
def test_returns_k_results():
    engine = ExecutionEngine(mock_deterministic, k=3)
    results = asyncio.run(engine.run_parallel('test'))
    assert len(results) == 3
    assert all(isinstance(r, RunResult) for r in results)

# ■■ Test 2: Run IDs are unique and sequential ■■■■■■■■■■■■■■■■■■
def test_run_ids_sequential():
    engine = ExecutionEngine(mock_deterministic, k=5)
    results = asyncio.run(engine.run_parallel('test'))
    ids = sorted([r.run_id for r in results])
    assert ids == [1, 2, 3, 4, 5]

# ■■ Test 3: Captures duration correctly ■■■■■■■■■■■■■■■■■■■■■■■
def test_duration_positive():
    engine = ExecutionEngine(mock_deterministic, k=2)
    results = asyncio.run(engine.run_parallel('test'))
    assert all(r.duration_ms >= 0 for r in results)

# ■■ Test 4: One crash does not kill other runs ■■■■■■■■■■■■■■■■■
def test_partial_failure_isolation():
    count = 0
    def sometimes_crash(q):
        nonlocal count; count += 1
        # To guarantee exactly 1 task fails (requires 2 exceptions) and 2 succeed 
        # (requiring 0 or 1 exception), amidst 3 tasks with 1 retry each:
        # We need exactly 3 exceptions. 
        if count in [2, 3, 4]: raise Exception('run failed')
        return 'ok'
    engine = ExecutionEngine(sometimes_crash, k=3)
    results = asyncio.run(engine.run_parallel('test'))
    assert len(results) == 3
    successes = [r for r in results if r.error is None]
    assert len(successes) == 2

# ■■ Test 5: Timeout is enforced ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def test_timeout_enforced():
    engine = ExecutionEngine(mock_slow, k=1, timeout_seconds=1)
    results = asyncio.run(engine.run_parallel('test'))
    assert results[0].error is not None

# ■■ Test 6: Works with async agent ■■■■■■■■■■■■■■■■■■■■■■■■■■■■
async def async_agent(q): return 'async result'
def test_async_agent():
    engine = ExecutionEngine(async_agent, k=2)
    results = asyncio.run(engine.run_parallel('test'))
    assert all(r.raw_output == 'async result' for r in results)
