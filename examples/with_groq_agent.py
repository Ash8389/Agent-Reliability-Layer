"""
Example: Agent Reliability Layer with Groq LLM
Run with: python examples/with_groq_agent.py
"""

from groq import Groq
from reliability_layer import ReliabilityLayer
from reliability_layer.config import settings

# Initialize Groq client
client = Groq(api_key=settings.groq_api_key)

def groq_agent(query: str) -> str:
    """
    Real LLM agent using Groq's free API.
    Uses llama-3.3-70b — fast and accurate.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a research assistant.
Always respond in this exact JSON format and nothing else:
{
  "main_answer": "<one sentence direct answer>",
  "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],
  "confidence": "<HIGH or MEDIUM or LOW>",
  "sources_used": ["<source 1>", "<source 2>"]
}
Do not add any text outside the JSON."""
            },
            {
                "role": "user",
                "content": query
            }
        ],
        temperature=1.0,
        max_tokens=500
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("=" * 55)
    print("  Agent Reliability Layer — Live Groq Demo")
    print("=" * 55)

    rl = ReliabilityLayer(runs=5, mode="standard")

    queries = [
        "Is cryptocurrency a good investment or a terrible idea?",
        "What will happen to the global economy in the next 5 years?",
        "List the top 3 most important skills for a software engineer"
    ]

    wrapped = rl.wrap(groq_agent)
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 45)

        result = wrapped.query(query)

        print(f"Answer:      {result.answer}")
        print(f"Reliability: {result.reliability}")
        print(f"Confidence:  {result.confidence}")
        print(f"Runs Agreed: {result.runs_agreed}")
        print(f"Ans Variance:  {result.variance_report.answer_variance}")
        print(f"Find Variance: {result.variance_report.findings_variance}")
        print(f"Cite Variance: {result.variance_report.citations_variance}")
        print(f"Contradiction: {result.contradiction_score:.3f}")
        if result.has_critical_contradiction:
            print("■■ CRITICAL CONTRADICTION DETECTED")
        
        if result.remediation_report:
            report = result.remediation_report
            if report.recommendations:
                print("Remediation:")
                for rec in report.recommendations:
                    print(f" [{rec.severity}] {rec.fix}")
            else:
                print("Remediation: None required")
                
        print(f"Audit Trail: {len(result.audit_trail)} runs stored")