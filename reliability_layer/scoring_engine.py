"""
Scoring Engine Module.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Any
from .models.variance_scores import VarianceScores
from reliability_layer.nli_checker import (
    ContradictionDetector, ContradictionResult
)

class VarianceScoresWithContradiction(VarianceScores):
    contradiction_result: Any = None


class ScoringEngine:
    """Computes variance scores for multiple agent outputs."""

    def __init__(self, fast_mode=True, *args: Any, **kwargs: Any) -> None:
        self.fast_mode = fast_mode
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.contradiction_detector = ContradictionDetector()

    def _tv(self, vectors: list) -> float:
        n = len(vectors)
        if n < 2: return 0.0
        total = sum(np.dot(vectors[i]-vectors[j], vectors[i]-vectors[j])
                    for i in range(n) for j in range(n) if i!=j)
        return total / (2 * n * (n-1))

    def answer_variance(self, answers: list[str]) -> float:
        if len(answers) < 2:
            return 0.0
        valid = [a for a in answers if a.strip()]
        if len(valid) < 2:
            return 0.0
        embeddings = self.embedder.encode(valid)
        normed = []
        for emb in embeddings:
            norm = np.linalg.norm(emb)
            normed.append(emb / norm if norm > 0 else emb)
        return self._tv(normed)

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

    def citations_variance(self,
                           all_cites: list[list[str]]
                           ) -> float:
        # Flatten all citations across all runs
        flat = [c for run in all_cites for c in run]

        # If no citations in any run, return 0
        if not flat:
            return 0.0

        # If all runs have empty citations, return 0
        if all(len(run) == 0 for run in all_cites):
            return 0.0

        # Use semantic embeddings — same approach as findings
        embeddings = self.embedder.encode(flat)

        # Build mean embedding per run
        idx = 0
        run_vecs = []
        for run in all_cites:
            if len(run) == 0:
                run_vecs.append(np.zeros(
                    embeddings.shape[1]))
            else:
                chunk = embeddings[idx:idx + len(run)]
                run_vecs.append(chunk.mean(axis=0))
            idx += len(run)

        # L2 normalize
        normed = []
        for v in run_vecs:
            norm = np.linalg.norm(v)
            normed.append(v / norm if norm > 0 else v)

        return self._tv(normed)

    def contradiction_variance(
        self, answers: list[str]
    ) -> ContradictionResult:
        if len(answers) < 2:
            from reliability_layer.nli_checker import ContradictionResult
            return ContradictionResult(0.0, 0.0)
        return self.contradiction_detector.check_all_pairs(answers)

    def compute(self, runs: list[dict], *args: Any, **kwargs: Any) -> VarianceScores:
        """Computes Total Variance metric over output set."""
        av = self.answer_variance([r.get('answer','') for r in runs])
        fv = self.findings_variance([r.get('findings',[]) for r in runs])
        cv = self.citations_variance([r.get('citations',[]) for r in runs])
        rel = round(1 - (av+fv+cv)/3, 3)
        label = 'HIGH' if rel>0.85 else ('MEDIUM' if rel>0.65 else 'LOW')
        
        answers = [r.get('answer','') for r in runs]
        c_res = self.contradiction_variance(answers)
        
        return VarianceScoresWithContradiction(
            answer_variance=round(av,3),
            findings_variance=round(fv,3), 
            citations_variance=round(cv,3),
            overall_reliability=rel, 
            confidence_label=label,
            contradiction_result=c_res
        )
