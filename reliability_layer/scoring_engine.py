"""
Scoring Engine Module.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Any
from .models.variance_scores import VarianceScores


class ScoringEngine:
    """Computes variance scores for multiple agent outputs."""

    def __init__(self, fast_mode=True, *args: Any, **kwargs: Any) -> None:
        self.fast_mode = fast_mode
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def _tv(self, vectors: list) -> float:
        n = len(vectors)
        if n < 2: return 0.0
        total = sum(np.dot(vectors[i]-vectors[j], vectors[i]-vectors[j])
                    for i in range(n) for j in range(n) if i!=j)
        return total / (2 * n * (n-1))

    def answer_variance(self, answers: list[str]) -> float:
        n = len(answers)
        disagreements = sum(1 for i in range(n) for j in range(n)
                            if i!=j and answers[i]!=answers[j])
        return disagreements / (n*(n-1)) if n>1 else 0.0

    def findings_variance(self, all_findings: list[list[str]]) -> float:
        flat = [f for run in all_findings for f in run]
        if not flat: return 0.0
        embs = self.embedder.encode(flat)
        idx, run_vecs = 0, []
        for run in all_findings:
            chunk = embs[idx:idx+len(run)]
            run_vecs.append(chunk.mean(axis=0) if len(chunk) else np.zeros(384))
            idx += len(run)
        normed = [v/np.linalg.norm(v) if np.linalg.norm(v)>0 else v
                  for v in run_vecs]
        return self._tv(normed)

    def citations_variance(self, all_cites: list[list[str]]) -> float:
        def normalize(u): 
            return u.lower().rstrip('/').replace('https://','').replace('http://','').replace('www.','')
        
        sets = [set(normalize(u) for u in run) for run in all_cites]
        n = len(sets)
        if n < 2 or all(not s for s in sets): return 0.0
        total = sum((1 - len(sets[i]&sets[j])/(len(sets[i]|sets[j]) or 1))
                    for i in range(n) for j in range(n) if i!=j)
        return total / (n*(n-1))

    def compute(self, runs: list[dict], *args: Any, **kwargs: Any) -> VarianceScores:
        """Computes Total Variance metric over output set."""
        av = self.answer_variance([r.get('answer','') for r in runs])
        fv = self.findings_variance([r.get('findings',[]) for r in runs])
        cv = self.citations_variance([r.get('citations',[]) for r in runs])
        rel = round(1 - (av+fv+cv)/3, 3)
        label = 'HIGH' if rel>0.85 else ('MEDIUM' if rel>0.65 else 'LOW')
        return VarianceScores(
            answer_variance=round(av,3),
            findings_variance=round(fv,3), 
            citations_variance=round(cv,3),
            overall_reliability=rel, 
            confidence_label=label
        )
