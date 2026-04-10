from __future__ import annotations

import json
from typing import Any

from src.core.llm_client import get_llm_client


SYSTEM_RULE = (
    "You are the Synthesis Agent for Kortex. Answer only based on the provided context. Do not hallucinate. "
    "If the intent is 'summarize', provide a structured summary of the key points in the context. "
    "Cite sources by name (e.g., [doc: Kafka Guide]). "
    "If the context is insufficient, state 'I don't know'.\n\n"
    "Your output MUST BE A JSON BLOCK with the following keys:\n"
    "1. 'answer': The markdown formatted response.\n"
    "2. 'confidence': A float from 0.0 to 1.0 based on how well the context answers the query."
)


class SynthesisAgent:
    def __init__(self) -> None:
        self.client = get_llm_client()

    def generate(self, query: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
        serialized_context = json.dumps(contexts, indent=2)
        prompt = (
            f"{SYSTEM_RULE}\n\n"
            f"User query: {query}\n\n"
            "Context:\n"
            f"{serialized_context}"
        )
        raw = self.client.generate(prompt, temperature=0.1)
        
        # Parse JSON from raw output
        try:
            # Handle possible markdown wrapping
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            return data
        except Exception:
            # Fallback if parsing fails
            return {"answer": raw, "confidence": 0.5}
