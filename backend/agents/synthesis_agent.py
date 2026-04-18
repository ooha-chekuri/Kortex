from __future__ import annotations

import json
from typing import Any

from backend.core.llm_client import get_llm_client


SYSTEM_RULE = (
    "Answer only based on the provided context. Do not hallucinate. "
    "You MUST extract and list specific details from the context - do not say details are not provided. "
    "If the context contains tickets, list each ticket ID with its summary. "
    "If the context contains docs, quote the relevant information."
)


class SynthesisAgent:
    def __init__(self) -> None:
        self.client = get_llm_client()

    def build_prompt(self, query: str, contexts: list[dict[str, Any]]) -> str:
        # Format context with source info for citations
        formatted_contexts = []
        for ctx in contexts:
            ctx_type = ctx.get("source_type", "doc")
            if ctx_type == "ticket":
                formatted_contexts.append(
                    {
                        "ticket_id": ctx.get("ticket_id", "?"),
                        "title": ctx.get("title", ""),
                        "description": ctx.get("description", ""),
                        "resolution": ctx.get("resolution", ""),
                    }
                )
            else:
                formatted_contexts.append(
                    {
                        "source": ctx.get("file", ctx.get("doc", "Unknown")),
                        "content": ctx.get("content", ""),
                    }
                )

        serialized_context = json.dumps(formatted_contexts, indent=2)
        return (
            f"{SYSTEM_RULE}\n\n"
            f"User question: {query}\n\n"
            "Context (from search results):\n"
            f"{serialized_context}\n\n"
            "Your task: Answer the question using the EXACT details from context above. "
            "For tickets: list each ticket_id with its title, description, and resolution. "
            "For docs: extract the relevant information. "
            "Do NOT say 'the details are not provided' - extract what IS there."
        )

    def generate(self, query: str, contexts: list[dict[str, Any]]) -> tuple[str, bool]:
        """Generate answer. Returns tuple of (answer, fallback_used)."""
        prompt = self.build_prompt(query, contexts)
        fallback_used = False
        try:
            result = self.client.generate(prompt, temperature=0.1)
            # Check if we got a valid response or an error
            if "FAILED" in result or "Error:" in result:
                raise Exception("LLM generation failed")
            # Check for generic/hallucinated responses - use fallback
            generic_phrases = [
                "list of",
                "not provided",
                "not available",
                "not included",
                "not specified",
            ]
            result_lower = result.lower()
            is_generic = result_lower.startswith("the") and any(
                p in result_lower for p in generic_phrases
            )
            if is_generic:
                raise Exception("Generic placeholder detected")
            return result, fallback_used
        except Exception as e:
            fallback_used = True
            # If LLM fails, generate a fallback answer based on contexts
            fallback_parts = [f"# Answer to: {query}\n"]

            for ctx in contexts[:5]:  # Use top 5 contexts for complete answer
                source = ctx.get(
                    "file", ctx.get("doc", ctx.get("ticket_id", "Unknown"))
                )
                content = ctx.get("content", "")

                if not content:
                    continue

                fallback_parts.append(f"\nFrom [{source}]\n")
                fallback_parts.append(content)

            fallback_parts.append(
                "\n\n**Note:** This answer was generated from retrieved context as the LLM is temporarily unavailable."
            )

            return "\n".join(fallback_parts), fallback_used
