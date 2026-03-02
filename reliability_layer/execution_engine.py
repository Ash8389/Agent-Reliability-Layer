import asyncio
import time
import inspect
from typing import Callable, Optional, Any, List
from pydantic import BaseModel

class RunResult(BaseModel):
    """
    Represents the result of a single agent execution run.
    """
    run_id: int
    raw_output: str
    duration_ms: int
    error: Optional[str] = None

class ExecutionEngine:
    """
    Production-grade async execution engine for agents.
    Accepts any Python callable (sync or async) and runs it concurrently using asyncio.gather.
    Each run is isolated and executes with an optional timeout and a single retry mechanism.
    """
    def __init__(self, agent_fn: Callable[..., Any], k: int = 3, timeout_seconds: int = 30):
        """
        Initializes the ExecutionEngine.

        Args:
            agent_fn: The callable to act as the agent. Can be sync or async.
            k: Number of concurrent executions.
            timeout_seconds: Timeout per execution run in seconds.
        """
        self.agent_fn = agent_fn
        self.k = k
        self.timeout = timeout_seconds

    async def _invoke_agent(self, query: str) -> Any:
        """Invokes the agent appropriately based on whether it is async or sync."""
        if inspect.iscoroutinefunction(self.agent_fn) or \
           inspect.iscoroutinefunction(getattr(self.agent_fn, '__call__', None)):
            return await self.agent_fn(query)
        else:
            return await asyncio.to_thread(self.agent_fn, query)

    async def _single_run(self, query: str, run_id: int) -> RunResult:
        """
        Executes a single run of the agent function with timeout and retry logic.
        If a run fails, it retries once before recording the error.

        Args:
            query: The input query to pass to the agent function.
            run_id: The unique identifier for this run.

        Returns:
            RunResult containing the output, duration, and error (if any).
        """
        start = time.time()
        max_attempts = 2  # initial attempt + 1 retry
        last_error = None

        for attempt in range(max_attempts):
            try:
                # Execute with timeout
                output = await asyncio.wait_for(
                    self._invoke_agent(query),
                    timeout=self.timeout
                )
                duration_ms = int((time.time() - start) * 1000)
                return RunResult(
                    run_id=run_id,
                    raw_output=str(output),
                    duration_ms=duration_ms
                )
            except Exception as e:
                last_error = e
                # Do not immediately return; loop will continue to retry if attempts remain

        # If it failed after all attempts
        duration_ms = int((time.time() - start) * 1000)
        return RunResult(
            run_id=run_id,
            raw_output="",
            duration_ms=duration_ms,
            error=str(last_error)
        )

    async def run_parallel(self, query: str) -> List[RunResult]:
        """
        Runs the agent function k times concurrently.

        Args:
            query: The input query to process.

        Returns:
            A list of RunResult objects, one for each concurrent run.
        """
        tasks = [self._single_run(query, i + 1) for i in range(self.k)]
        results = await asyncio.gather(*tasks)
        return list(results)

if __name__ == "__main__":
    # --- Integration testing with mock agents ---
    import random

    def sample_sync_agent(q: str) -> str:
        """A mock synchronous agent that delays briefly."""
        time.sleep(0.1)
        return f"Echo {q}"

    async def sample_async_agent(q: str) -> str:
        """A mock asynchronous agent that delays briefly and sometimes fails to demo retries."""
        await asyncio.sleep(0.1)
        if random.random() < 0.3:
            raise RuntimeError("Random internal failure!")
        return f"Async Echo {q}"

    async def main():
        print("Testing Sync Agent:")
        sync_engine = ExecutionEngine(sample_sync_agent, k=2, timeout_seconds=1)
        res = await sync_engine.run_parallel("hello")
        for r in res:
            print(r.model_dump_json(indent=2))

        print("\nTesting Async Agent (may retry on failure):")
        async_engine = ExecutionEngine(sample_async_agent, k=3, timeout_seconds=1)
        ares = await async_engine.run_parallel("hello async")
        for r in ares:
            print(r.model_dump_json(indent=2))

    asyncio.run(main())
