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

    def _prepare_scoring(self, raw_runs, stabilized):
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
        return runs_for_scoring

    async def _run(self, question: str):
        mode = self.config.get('mode', 'standard')

        if mode == "standard":
            engine = ExecutionEngine(self.agent_fn, k=self.config['runs'], timeout_seconds=self.config.get('timeout', 30))
            raw_runs = await engine.run_parallel(question)
            
            stab = StabilizationEngine()
            stabilized = stab.process(raw_runs)
            
            runs_for_scoring = self._prepare_scoring(raw_runs, stabilized)
            scores = self.scorer.compute(runs_for_scoring)
            
            builder = ResponseBuilder()
            response = builder.build(stabilized, scores, raw_runs)
            
            if response.reliability < 0.7:
                warnings.warn(f'Low reliability: {response.reliability}', ReliabilityWarning)
                
            return response

        elif mode == "full":
            engine = ExecutionEngine(self.agent_fn, k=self.config['runs'], timeout_seconds=self.config.get('timeout', 30))
            raw_runs = await engine.run_parallel(question)
            
            stab = StabilizationEngine()
            stabilized = stab.process(raw_runs)
            
            runs_for_scoring = self._prepare_scoring(raw_runs, stabilized)
            scores = self.scorer.compute(runs_for_scoring)
            
            builder = ResponseBuilder()
            response = builder.build(stabilized, scores, raw_runs)
            
            if response.reliability < 0.7:
                warnings.warn(f'Low reliability: {response.reliability}', ReliabilityWarning)
                
            return response

        elif mode == "adaptive":
            engine_quick = ExecutionEngine(self.agent_fn, k=2, timeout_seconds=self.config.get('timeout', 30))
            raw_runs_quick = await engine_quick.run_parallel(question)
            
            stab = StabilizationEngine()
            stabilized_quick = stab.process(raw_runs_quick)
            
            runs_for_scoring_quick = self._prepare_scoring(raw_runs_quick, stabilized_quick)
            scores_quick = self.scorer.compute(runs_for_scoring_quick)
            
            builder = ResponseBuilder()
            response_quick = builder.build(stabilized_quick, scores_quick, raw_runs_quick)
            
            if response_quick.reliability > self.config.get('escalate_threshold', 0.75):
                response_quick.contradiction_score = 0.0
                return response_quick
            else:
                escalate_runs = self.config.get('escalate_runs', 5)
                engine_full = ExecutionEngine(self.agent_fn, k=escalate_runs, timeout_seconds=self.config.get('timeout', 30))
                raw_runs_full = await engine_full.run_parallel(question)
                
                stabilized_full = stab.process(raw_runs_full)
                runs_for_scoring_full = self._prepare_scoring(raw_runs_full, stabilized_full)
                
                scores_full = self.scorer.compute(runs_for_scoring_full)
                response_full = builder.build(stabilized_full, scores_full, raw_runs_full)
                
                if response_full.reliability < 0.7:
                    warnings.warn(f'Low reliability: {response_full.reliability}', ReliabilityWarning)
                    
                return response_full


class ReliabilityLayer:
    def __init__(
        self,
        runs: int = 3,
        timeout: int = 30,
        mode: str = "standard",
        escalate_threshold: float = 0.75,
        escalate_runs: int = 5,
    ):
        self.runs = runs
        self.timeout = timeout
        self.mode = mode
        self.escalate_threshold = escalate_threshold
        self.escalate_runs = escalate_runs

        if mode not in ("standard", "full", "adaptive"):
            raise ValueError(
                f"Invalid mode: {mode}. Must be standard, full, or adaptive"
            )

        self.config = {
            'runs': runs, 
            'mode': mode, 
            'timeout': timeout,
            'escalate_threshold': escalate_threshold,
            'escalate_runs': escalate_runs
        }

    def wrap(self, agent_fn) -> WrappedAgent:
        return WrappedAgent(agent_fn, self.config)

    def configure(self, **kwargs):
        self.config.update(kwargs)
        return self

    def analyze(self, query: str, agent_fn):
        return self.wrap(agent_fn).query(query)


class ReliabilityWarning(UserWarning): pass
