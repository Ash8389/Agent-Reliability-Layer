"""
Example using OpenAI with Reliability Layer.
"""

# import os
# import openai
# from reliability_layer import ReliabilityLayer
#
# openai.api_key = os.getenv("OPENAI_API_KEY")
#
# def openai_agent(prompt: str) -> str:
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response.choices[0].message.content
#
# rl = ReliabilityLayer()
# safe_agent = rl.wrap(openai_agent)
#
# result = rl.query(safe_agent, prompt="Explain quantum computing.")
#
# print(f"Confidence: {result.confidence}")
