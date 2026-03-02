import warnings, asyncio
from .execution_engine import ExecutionEngine
from .stabilization_engine import StabilizationEngine
from .scoring_engine import ScoringEngine
from .response_builder import ResponseBuilder

class WrappedAgent:
    def __init__(self, agent_fn, config):
        self.agent_fn = agent_fn
        self.config = config

    def query(self, question: str):
        return asyncio.run(self._run(question))

    async def _run(self, question: str):
        engine = ExecutionEngine(self.agent_fn, k=self.config['runs'], timeout_seconds=self.config.get('timeout', 30))
        stab = StabilizationEngine()
        scorer = ScoringEngine()
        builder = ResponseBuilder()

        runs = await engine.run_parallel(question)
        stabilized = stab.process(runs)
        
        parsed_runs = [{'answer': r.raw_output, 'findings': [], 'citations': []} for r in runs]
        scores = scorer.compute(parsed_runs)
        
        response = builder.build(stabilized, scores, runs)

        if response.reliability < 0.7:
            warnings.warn(f'Low reliability: {response.reliability}',
                          ReliabilityWarning)

        return response


class ReliabilityLayer:
    def __init__(self, runs=3, mode='stabilize', timeout=30):
        self.config = {'runs': runs, 'mode': mode, 'timeout': timeout}

    def wrap(self, agent_fn) -> WrappedAgent:
        return WrappedAgent(agent_fn, self.config)

    def configure(self, **kwargs):
        self.config.update(kwargs)
        return self

    def analyze(self, query: str, agent_fn):
        return self.wrap(agent_fn).query(query)


class ReliabilityWarning(UserWarning): pass
