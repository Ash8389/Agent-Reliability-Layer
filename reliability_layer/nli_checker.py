from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ContradictionPair:
    run_i: int
    run_j: int
    contradiction_score: float
    is_critical: bool


@dataclass
class ContradictionResult:
    max_contradiction: float
    avg_contradiction: float
    critical_pairs: list[ContradictionPair] = field(default_factory=list)
    has_critical_contradiction: bool = False


class ContradictionDetector:
    """
    Uses NLI (Natural Language Inference) to detect when
    two LLM outputs directly contradict each other.
    Complements embedding variance — catches logical failures
    that semantic similarity alone would miss.
    """

    def __init__(self):
        from transformers import pipeline
        # Load the NLI model ONCE via text-classification pipeline.
        # This gives per-label scores (contradiction / neutral / entailment)
        # for a (premise, hypothesis) pair, which is what check_pair() needs.
        self._classifier = pipeline("text-classification", model="cross-encoder/nli-MiniLM2-L6-H768", top_k=None)

    def check_pair(
        self, text1: str, text2: str
    ) -> dict:
        # Run NLI on text1 as premise, text2 as hypothesis
        # candidate_labels = ["contradiction", "neutral", "entailment"]
        res = self._classifier({"text": text1, "text_pair": text2})
        if isinstance(res, list) and len(res) > 0 and isinstance(res[0], list):
            res = res[0]
        
        scores = {item["label"].lower(): item["score"] for item in res}
        
        con_score = scores.get("contradiction", 0.0)
        ent_score = scores.get("entailment", 0.0)
        neu_score = scores.get("neutral", 0.0)
        
        is_crit = bool(con_score > 0.7)
        
        return {
            "contradiction_score": con_score,
            "entailment_score": ent_score,
            "neutral_score": neu_score,
            "is_critical": is_crit
        }

    def check_all_pairs(
        self, outputs: list[str]
    ) -> ContradictionResult:
        if len(outputs) < 2:
            return ContradictionResult(0.0, 0.0)
            
        contradiction_scores = []
        critical_pairs = []
        
        for i in range(len(outputs)):
            for j in range(i + 1, len(outputs)):
                res = self.check_pair(outputs[i], outputs[j])
                score = res["contradiction_score"]
                contradiction_scores.append(score)
                
                if res["is_critical"]:
                    critical_pairs.append(
                        ContradictionPair(
                            run_i=i, run_j=j, contradiction_score=score, is_critical=True
                        )
                    )
                    
        max_c = max(contradiction_scores) if contradiction_scores else 0.0
        avg_c = sum(contradiction_scores) / len(contradiction_scores) if contradiction_scores else 0.0
        
        return ContradictionResult(
            max_contradiction=float(max_c),
            avg_contradiction=float(avg_c),
            critical_pairs=critical_pairs,
            has_critical_contradiction=len(critical_pairs) > 0
        )

