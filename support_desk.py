import os
import csv
from datetime import datetime
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

from vector_kb import kb_engine

load_dotenv()

# Tool 1: Knowledge Base Search via FAISS
def search_kb(query: str) -> str:
    """Tool for KnowledgeBaseAgent: Searches documents and returns matched passages with source filenames."""
    return kb_engine.search(query)

# Tool 2: CSV Ticket Logger
def log_ticket(
    ticket_id: str,
    customer_info: str,
    complaint: str,
    category: str,
    urgency: str,
    sentiment: str,
    kb_sources: str,
    response: str,
    status: str,
    escalation_reason: str
) -> str:
    """Tool for LogAgent: Appends the ticket record to logs/tickets.csv matching assignment schema."""
    os.makedirs("logs", exist_ok=True)
    csv_path = "logs/tickets.csv"
    headers = [
        "ticket_id", "timestamp", "customer_name / order_id", "complaint",
        "category urgency sentiment", "kb_sources", "response",
        "status", "escalation_reason"
    ]
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow([
            ticket_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            customer_info,
            complaint,
            f"{category} | {urgency} | {sentiment}",
            kb_sources,
            response,
            status,
            escalation_reason
        ])
    return f"LOGGED: Ticket {ticket_id} has been recorded with status {status}."

# Multi-Agent Team Setup
def create_support_team():
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    # 1. Customer Query Agent
    query_agent = AssistantAgent(
        name="CustomerQueryAgent",
        model_client=model_client,
        description="Extracts category, urgency, sentiment, summary, and query keywords.",
        system_message="""You are the Customer Query Agent.
Analyze the customer's complaint.

GUIDELINES FOR URGENCY:
- Standard questions regarding delayed shipments, returns, replacements, or password resets MUST be marked 'Low' or 'Medium' urgency.
- Mark 'High' urgency ONLY if the customer is extremely hostile, threatening legal/bank action, or reporting critical payment fraud.

Format your output strictly:
Category: [Shipping | Refund | Account | Hardware | Billing | General]
Urgency: [Low | Medium | High]
Sentiment: [Positive | Neutral | Frustrated | Angry]
Summary: <One-line clear summary>
Focus Query: <A natural 4-8 word search phrase describing the topic, e.g. 'late delivery shipping policy tracking updates'>"""
    )

    # 2. Knowledge Base Agent
    knowledge_agent = AssistantAgent(
        name="KnowledgeBaseAgent",
        model_client=model_client,
        tools=[search_kb],
        description="Searches the FAISS vector database for company policies and product manuals.",
        system_message="""You are the Knowledge Base Agent.
Use the search_kb tool using the 'Focus Query' phrase from CustomerQueryAgent.
Pass ONLY a single clean string query to the tool.
Return the matched passages, making sure to show which document file was used (e.g. shipping_policy.md, apexsound_headphones_manual.pdf).
If the tool returns NO_MATCH, output: 'NO_MATCH: No relevant company policies or manual entries found.'"""
    )

    # 3. Resolution Agent
    resolution_agent = AssistantAgent(
        name="ResolutionAgent",
        model_client=model_client,
        description="Drafts grounded customer replies using only the facts provided.",
        system_message="""You are the Resolution Agent.
Write a courteous, professional reply directly addressed to the customer.
CRITICAL GROUNDING RULES:
- Use ONLY facts retrieved by KnowledgeBaseAgent. Never invent return windows, delivery timelines, or warranty terms.
- If no matching documents exist (NO_MATCH), state politely and honestly that this case requires dedicated support.
At the very end of your response, output:
Confidence: [High | Medium | Low]"""
    )

    # 4. Log Agent
    log_agent = AssistantAgent(
        name="LogAgent",
        model_client=model_client,
        tools=[log_ticket],
        description="Applies escalation criteria and appends ticket to the CSV log.",
        system_message="""You are the Log Agent.
Review the previous conversation and determine ticket status and escalation reason.

ESCALATION RULES:
1. Urgency is 'High' OR Sentiment is 'Angry'.
2. KnowledgeBaseAgent found no matching documents (NO_MATCH).
3. The issue involves legal threats, repeated payment errors, or fraud disputes.
4. ResolutionAgent confidence is 'Low'.

If ANY rule is met:
Status: Escalated
Reason: <State the exact trigger, e.g., High urgency + angry customer>
Otherwise:
Status: Resolved
Reason: None

Call the log_ticket tool with all required fields.
End your final output message with the exact keyword: LOGGED"""
    )

    # Termination when LogAgent completes logging
    termination = TextMentionTermination("LOGGED")
    team = RoundRobinGroupChat(
        participants=[query_agent, knowledge_agent, resolution_agent, log_agent],
        termination_condition=termination,
        max_turns=6
    )
    return team

if __name__ == "__main__":
    import asyncio

    async def test_run():
        print("Testing AutoGen team workflow with Test Case 1...")
        team = create_support_team()
        sample_task = (
            "Ticket ID: TKT-1001\n"
            "Customer: David Miller (ORD-1102)\n"
            "Complaint: Where is my order? It was supposed to arrive yesterday."
        )
        async for message in team.run_stream(task=sample_task):
            if hasattr(message, "source") and hasattr(message, "content") and message.content:
                print(f"\n--- [{message.source}] ---")
                print(message.content)

    asyncio.run(test_run())