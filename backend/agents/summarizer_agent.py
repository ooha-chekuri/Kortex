from __future__ import annotations

from typing import Any, List
from backend.core.llm_client import get_llm_client

SUMMARIZE_PROMPT = """
You are a summarization expert. Your task is to provide a concise, executive summary of the provided information.
Highlight key technical points, solutions, or policies.
If the information contains multiple sources, synthesize them into a coherent summary.

Information to summarize:
{content}

Concise Summary:
"""

class SummarizerAgent:
    def __init__(self) -> None:
        self.client = get_llm_client()

    def summarize(self, contexts: List[dict[str, Any]]) -> str:
        if not contexts:
            return "No information available to summarize."
            
        combined_text = "\n\n".join([f"Source: {c.get('doc', c.get('ticket_id', 'Unknown'))}\nContent: {c.get('content', '')}" for c in contexts])
        
        # Limit input length for LLM
        truncated_text = combined_text[:4000]
        
        prompt = SUMMARIZE_PROMPT.format(content=truncated_text)
        
        try:
            summary = self.client.generate(prompt, temperature=0.1)
            return summary.strip()
        except Exception as e:
            return f"Error during summarization: {e}"
