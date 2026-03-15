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
        # Step 1: Remove markdown fences
        cleaned = re.sub(r'```json|```', '', raw).strip()

        # Step 2: Try standard JSON parse first
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Step 3: Regex fallback for malformed JSON
        # Handles case where LLM omits quotes around values
        answer_match = re.search(
            r'"main_answer"\s*:\s*"?([^"\n}{]+?)(?:"\s*,|\s*,\s*"[a-z])',
            cleaned,
            re.DOTALL
        )
        if not answer_match:
            # Broader fallback: grab everything after main_answer
            # until next JSON key
            answer_match = re.search(
                r'"main_answer"\s*:\s*"?([^"}{]{10,})',
                cleaned
            )
        findings_matches = re.findall(
            r'"([^"]{10,})"',
            cleaned
        )

        if answer_match:
            return {
                'main_answer': answer_match.group(1).strip(),
                'key_findings': findings_matches[1:4]
                                if len(findings_matches) > 1
                                else [],
                'confidence': 'MEDIUM',
                'sources_used': []
            }

        # Step 4: Total fallback — raise so process() catches it
        raise ValueError(
            f'Cannot parse output: {raw[:100]}'
        )

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
        outputs = [r.raw_output for r in raw_runs
                   if r.error is None]

        if not outputs:
            return {
                'stabilized_output': '',
                'method_used': 'fallback_empty',
                'agreement_rate': 0.0,
                'parsed_runs': []
            }

        enforcer = StructuredOutputEnforcer()

        clean_outputs = []
        parsed_runs = []
        for output in outputs:
            try:
                parsed = enforcer.parse_output(output)
                # Fall back to raw output if main_answer came back empty
                ma = parsed.get('main_answer', '') or output
                clean_outputs.append(ma)
                parsed_runs.append(parsed)
            except Exception:
                clean_outputs.append(output)
                parsed_runs.append({
                    'main_answer': output,
                    'key_findings': [],
                    'confidence': 'LOW',
                    'sources_used': []
                })

        from collections import Counter
        counts = Counter(clean_outputs)
        best_answer, best_count = counts.most_common(1)[0]
        agreement_rate = best_count / len(clean_outputs)

        return {
            'stabilized_output': best_answer,
            'method_used': 'structured_consensus',
            'agreement_rate': round(agreement_rate, 3),
            'parsed_runs': parsed_runs
        }
