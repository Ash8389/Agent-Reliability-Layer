import warnings, asyncio
from .execution_engine import ExecutionEngine
from .stabilization_engine import StabilizationEngine
from .scoring_engine import ScoringEngine
from .response_builder import ResponseBuilder

class WrappedAgent:
    def __init__(self, agent_fn, config):
        self.agent_fn = agent_fn
        self.config = config
        self.scorer = ScoringEngine()

    def query(self, question: str):
        return asyncio.run(self._run(question))

    async def _run(self, question: str):
        engine = ExecutionEngine(self.agent_fn, k=self.config['runs'], timeout_seconds=self.config.get('timeout', 30))
        stab = StabilizationEngine()
        scorer = self.scorer
        builder = ResponseBuilder()

        raw_runs   = await engine.run_parallel(question)
        stabilized = stab.process(raw_runs)

        parsed_runs = stabilized.get('parsed_runs', [])
        runs_for_scoring = []
        for i, run in enumerate(raw_runs):
            if i < len(parsed_runs):
                runs_for_scoring.append({
                    'answer':   parsed_runs[i].get(
                                'main_answer', run.raw_output),
                    'findings': parsed_runs[i].get(
                                'key_findings', []),
                    'citations':parsed_runs[i].get(
                                'sources_used', [])
                })
            else:
                runs_for_scoring.append({
                    'answer':   run.raw_output,
                    'findings': [],
                    'citations':[]
                })

        scores   = self.scorer.compute(runs_for_scoring)
        builder  = ResponseBuilder()
        response = builder.build(stabilized, scores, raw_runs)

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
