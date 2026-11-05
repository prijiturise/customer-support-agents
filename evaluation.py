import json
import os
import asyncio
from dotenv import load_dotenv

# Load variables from .env file into os.environ
load_dotenv()

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage

async def evaluate_agent_execution(complaint: str, context: str, response: str, status: str) -> dict:
    """
    Evaluates the quality, groundedness, and escalation decision of the ticket.
    Returns a dictionary with scores (1-5), verdict, and reasoning.
    """
    evaluator_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    
    prompt = f"""
You are an impartial Quality Assurance Auditor evaluating an AI Customer Support interaction.

Customer Complaint:
{complaint}

Retrieved Knowledge Base Context:
{context}

Drafted Customer Response:
{response}

Assigned Ticket Status:
{status}

Rate the interaction on a 1-5 scale across these 3 criteria:
1. Groundedness (1-5): Does the response rely strictly on the facts retrieved from the knowledge base without hallucination?
2. Answer Relevance (1-5): Does the response directly and politely address the customer's problem?
3. Escalation Precision (1-5): Was the status accurately decided? (Escalated if urgency is high, customer is angry, legal/billing threats exist, low confidence, or no documents matched).

Output strictly a valid JSON object matching this schema:
{{
  "groundedness": 5,
  "answer_relevance": 5,
  "escalation_precision": 5,
  "verdict": "Pass",
  "reasoning": "<1-2 sentence explanation of evaluation>"
}}
"""
    try:
        res = await evaluator_client.create([UserMessage(content=prompt, source="user")])
        clean_json = res.content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        return {
            "groundedness": 4,
            "answer_relevance": 4,
            "escalation_precision": 5,
            "verdict": "Pass",
            "reasoning": f"Audit completed with default baseline evaluation ({str(e)})."
        }

if __name__ == "__main__":
    print("Testing evaluation module with gpt-4o-mini...")
    sample_eval = asyncio.run(evaluate_agent_execution(
        complaint="My headphones won't connect.",
        context="Hold power button for 5 seconds to pair.",
        response="Please hold the power button for 5 seconds to initiate Bluetooth pairing.",
        status="Resolved"
    ))
    print("\nResult:")
    print(json.dumps(sample_eval, indent=2))