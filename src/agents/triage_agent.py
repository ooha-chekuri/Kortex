from __future__ import annotations

from src.core.llm_client import get_llm_client


TRIAGE_PROMPT = (
    "You are the Triage Agent for Kortex, an agentic knowledge copilot.\n"
    "Classify the following user query into one of four categories:\n"
    "1. 'docs': For conceptual, architectural, installation, or 'how-to' questions.\n"
    "2. 'tickets': For error messages, specific incident IDs, known technical issues, or historical fix patterns.\n"
    "3. 'both': If the query spans both conceptual understanding and specific troubleshooting.\n"
    "4. 'summarize': If the user explicitly asks to summarize a document, topic, or recent activity.\n\n"
    "Respond with only one word: 'docs', 'tickets', 'both', or 'summarize'."
)


def classify_intent(query: str) -> str:
    client = get_llm_client()
    prompt = f"{TRIAGE_PROMPT}\n\nQuery: {query}"
    raw = client.generate(prompt, temperature=0.0).lower()
    
    if "summarize" in raw:
        return "summarize"
    if "docs" in raw and "tickets" in raw:
        return "both"
    if "docs" in raw:
        return "docs"
    if "tickets" in raw:
        return "tickets"
    return "both"
