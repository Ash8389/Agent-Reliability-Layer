from dataclasses import dataclass

@dataclass
class Recommendation:
    dimension: str  # "answer" | "findings" | "citations" | "logic" | "overall"
    severity: str   # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    fix: str        # short actionable fix description
    detail: str     # longer explanation

@dataclass
class RemediationReport:
    recommendations: list[Recommendation]
    priority_fix: Recommendation | None
    needs_human_review: bool
    estimated_improvement: str


class RemediationEngine:
    def diagnose(
        self,
        answer_variance: float,
        findings_variance: float,
        citations_variance: float,
        contradiction_score: float,
        overall_reliability: float,
    ) -> RemediationReport:
        recommendations = []

        # RULE 1 — Critical contradiction:
        if contradiction_score > 0.7:
            recommendations.append(
                Recommendation(
                    dimension="logic",
                    severity="CRITICAL",
                    fix="Do not serve — flag for human review",
                    detail="Runs directly contradict each other",
                )
            )

        # RULE 2 — High answer variance:
        if answer_variance > 0.3:
            recommendations.append(
                Recommendation(
                    dimension="answer",
                    severity="HIGH",
                    fix="Lower LLM temperature to 0.1-0.2",
                    detail="High variance means agent is non-deterministic",
                )
            )

        # RULE 3 — High findings variance:
        if findings_variance > 0.5:
            recommendations.append(
                Recommendation(
                    dimension="findings",
                    severity="HIGH",
                    fix="Add chain-of-thought structure to system prompt",
                    detail="Agent reasons differently each run",
                )
            )

        # RULE 4 — High citations variance:
        if citations_variance > 0.5:
            recommendations.append(
                Recommendation(
                    dimension="citations",
                    severity="MEDIUM",
                    fix="Pin sources via RAG or force citation format",
                    detail="Agent cites inconsistent sources",
                )
            )

        # RULE 5 — Overall low reliability:
        if overall_reliability < 0.5:
            recommendations.append(
                Recommendation(
                    dimension="overall",
                    severity="CRITICAL",
                    fix="Review entire system prompt and model choice",
                    detail="Fundamental reliability problem detected",
                )
            )

        # RULE 6 — No issues:
        if not recommendations:
            return RemediationReport(
                recommendations=[],
                priority_fix=None,
                needs_human_review=False,
                estimated_improvement="Agent is reliable — no action needed",
            )

        # PRIORITY LOGIC:
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda r: severity_order.get(r.severity, 4))

        priority_fix = recommendations[0]
        needs_human_review = any(r.severity == "CRITICAL" for r in recommendations)

        # estimated_improvement logic:
        if any(r.severity == "CRITICAL" for r in recommendations):
            estimated_improvement = "Requires human review first"
        elif any(r.severity == "HIGH" for r in recommendations):
            estimated_improvement = "30-50% variance reduction if fixes applied"
        elif any(r.severity == "MEDIUM" for r in recommendations):
            estimated_improvement = "10-30% variance reduction expected"
        else:
            estimated_improvement = "Agent is reliable — no action needed"

        return RemediationReport(
            recommendations=recommendations,
            priority_fix=priority_fix,
            needs_human_review=needs_human_review,
            estimated_improvement=estimated_improvement,
        )
