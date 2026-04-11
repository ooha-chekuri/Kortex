from __future__ import annotations

import json
from typing import Any

from backend.core.llm_client import get_llm_client


SYSTEM_RULE = (
    "Answer only based on the provided context. Do not hallucinate. "
    "Answer concisely, cite sources by name, and say 'I don't know' if the context is insufficient."
)


class SynthesisAgent:
    def __init__(self) -> None:
        self.client = get_llm_client()

    def build_prompt(self, query: str, contexts: list[dict[str, Any]]) -> str:
        # Format context with source info for citations
        formatted_contexts = []
        for ctx in contexts:
            source_name = ctx.get(
                "file", ctx.get("doc", ctx.get("ticket_id", "Unknown"))
            )
            formatted_contexts.append(
                {"source": source_name, "content": ctx.get("content", "")}
            )

        serialized_context = json.dumps(formatted_contexts, indent=2)
        return (
            f"{SYSTEM_RULE}\n\n"
            f"User question: {query}\n\n"
            "Context:\n"
            f"{serialized_context}\n\n"
            "Return a concise answer in markdown. For each piece of information, cite the source name in brackets like [source.pdf] or [TICKET-001]."
        )

    def generate(self, query: str, contexts: list[dict[str, Any]]) -> str:
        prompt = self.build_prompt(query, contexts)
        try:
            result = self.client.generate(prompt, temperature=0.1)
            # Check if we got a valid response or an error
            if "FAILED" in result or "Error:" in result:
                raise Exception("LLM generation failed")
            return result
        except Exception as e:
            # If LLM fails, generate a fallback answer based on contexts
            # This allows the system to still respond even without an LLM
            fallback_parts = [f"# Answer to: {query}\n"]

            for ctx in contexts[:3]:  # Use top 3 contexts
                source = ctx.get(
                    "file", ctx.get("doc", ctx.get("ticket_id", "Unknown"))
                )
                content = ctx.get("content", "")

                # Extract the key information based on the query
                fallback_parts.append(f"\n### From [{source}]\n")

                # Add the content (truncated if too long)
                if len(content) > 400:
                    fallback_parts.append(content[:400] + "...")
                else:
                    fallback_parts.append(content)

            fallback_parts.append(
                "\n\n**Note:** This answer was generated from retrieved context as the LLM is temporarily unavailable."
            )

            return "\n".join(fallback_parts)
