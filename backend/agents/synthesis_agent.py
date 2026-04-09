from __future__ import annotations

import json
from typing import Any

from backend.core.llm_client import get_llm_client


SYSTEM_RULE = (
    "Answer only based on the provided context. Do not hallucinate. "
    "Answer concisely, cite sources by name, and say \"I don't know\" if the context is insufficient."
)


class SynthesisAgent:
    def __init__(self) -> None:
        self.client = get_llm_client()

    def build_prompt(self, query: str, contexts: list[dict[str, Any]]) -> str:
        serialized_context = json.dumps(contexts, indent=2)
        return (
            f"{SYSTEM_RULE}\n\n"
            f"User question: {query}\n\n"
            "Context:\n"
            f"{serialized_context}\n\n"
            "Return a concise answer in markdown. Include citations inline using the source names."
        )

    def generate(self, query: str, contexts: list[dict[str, Any]]) -> str:
        prompt = self.build_prompt(query, contexts)
        return self.client.generate(prompt, temperature=0.1)
