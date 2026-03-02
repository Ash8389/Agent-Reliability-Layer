"""
Example using OpenAI with Reliability Layer.
"""

import openai
from reliability_layer import ReliabilityLayer
from reliability_layer.config import settings

openai.api_key = settings.openai_api_key

def openai_agent(query: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are a research assistant. 
                Always respond in this exact JSON format:
                {
                  "main_answer": "<direct answer>",
                  "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],
                  "confidence": "<HIGH|MEDIUM|LOW>",
                  "sources_used": ["<source 1>", "<source 2>"]
                }"""
            },
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    rl = ReliabilityLayer(runs=3, mode="stabilize")
    result = rl.wrap(openai_agent).query(
        "What are the main risks of combining Drug X with alcohol?"
    )
    
    print(f"Answer:      {result.answer}")
    print(f"Reliability: {result.reliability}")
    print(f"Confidence:  {result.confidence}")
    print(f"Runs Agreed: {result.runs_agreed}")
    print(f"Variance:    {result.variance_report}")