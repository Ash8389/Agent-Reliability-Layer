import re
import json
from typing import Any, List
from pydantic import BaseModel

class StabilizedOutput(BaseModel):
    stabilized_output: str
    method_used: str
    agreement_rate: float

class StructuredOutputEnforcer:
    """Enforces structured output formats on unstable model responses."""
    SCHEMA = '''Respond ONLY in JSON:
{
"main_answer": "",
"key_findings": ["","",""],
"confidence": "",
"sources_used": [""]
}'''

    def wrap_prompt(self, prompt: str) -> str:
        return f'{prompt}\n\n{self.SCHEMA}'

    def parse_output(self, raw: str) -> dict:
        # Remove markdown fences
        raw = re.sub(r'```json|```', '', raw).strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            raise ValueError('No JSON found')
        return json.loads(match.group())

class QueryEnsembler:
    """Ensembles multiple query results to produce a generic stabilized form."""
    
    def get_consensus_queries(self, all_run_queries: List[List[str]], step: int, total_steps: int) -> List[str]:
        progress = step / total_steps
        if progress > 0.5:
            return list({q for run in all_run_queries for q in run})
            
        normalized = [set(q.strip().lower() for q in run) for run in all_run_queries]
        if not normalized:
            return []
            
        intersection = set.intersection(*normalized)
        return list(intersection) if intersection else list(all_run_queries[0])

    def compute_agreement_rate(self, all_run_queries: List[List[str]]) -> float:
        """
        Returns 0.0 to 1.0 representing how much runs agree on queries.
        Use Jaccard similarity averaged across all pairs.
        """
        if not all_run_queries or len(all_run_queries) < 2:
            return 1.0
            
        normalized = [set(q.strip().lower() for q in run) for run in all_run_queries]
        num_runs = len(normalized)
        total_sim = 0.0
        pairs = 0
        
        for i in range(num_runs):
            for j in range(i + 1, num_runs):
                set1 = normalized[i]
                set2 = normalized[j]
                
                if not set1 and not set2:
                    sim = 1.0
                else:
                    intersect = len(set1.intersection(set2))
                    union = len(set1.union(set2))
                    sim = intersect / union if union > 0 else 0.0
                    
                total_sim += sim
                pairs += 1
                
        return total_sim / pairs if pairs > 0 else 1.0

    def decay_schedule(self, step: int, total_steps: int) -> float:
        """
        Returns the restrictness factor from 1.0 (step 1) to 0.0 (final step).
        Use linear decay.
        """
        if total_steps <= 1:
            return 0.0
        # step 1 -> 1.0, step total_steps -> 0.0
        decay = 1.0 - (step - 1) / (total_steps - 1)
        return max(0.0, min(1.0, decay))

class StabilizationEngine:
    """Main stabilization pipeline."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def process(self, raw_runs: list) -> dict:
        """
        Takes a list of RunResult objects from ExecutionEngine.
        Returns a dict with keys: stabilized_output, method_used, agreement_rate
        """
        # Extract raw outputs from RunResult objects
        outputs = [r.raw_output for r in raw_runs if r.error is None]
        
        # Fallback if all runs failed
        if not outputs:
            return {
                'stabilized_output': '',
                'method_used': 'fallback_empty',
                'agreement_rate': 0.0
            }
        
        # Find the most common output (consensus)
        from collections import Counter
        counts = Counter(outputs)
        best_answer, best_count = counts.most_common(1)[0]
        agreement_rate = best_count / len(outputs)
        
        return {
            'stabilized_output': best_answer,
            'method_used': 'consensus_majority',
            'agreement_rate': round(agreement_rate, 3)
        }
