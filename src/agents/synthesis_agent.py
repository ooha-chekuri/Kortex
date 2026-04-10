from __future__ import annotations

import json
from typing import Any

from src.core.llm_client import get_llm_client


SYSTEM_RULE = (
    "You are the Synthesis Agent for Kortex, an enterprise knowledge copilot. "
    "Your job is to answer user questions based on the provided context from documents and tickets. "
    "Be helpful and direct - extract the relevant information from context to answer the query. "
    "Do NOT say 'I don't know' if there is any relevant information in the context - synthesize it. "
    "Cite sources using [doc: filename] or [ticket: id] format.\n\n"
    "IMPORTANT: Return ONLY valid JSON, no markdown code blocks:\n"
    '{"answer": "your answer here", "confidence": 0.85}'
)


class SynthesisAgent:
    def __init__(self) -> None:
        self.client = get_llm_client()

    def generate(self, query: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
        if not contexts:
            return {
                "answer": "No relevant information found in the knowledge base.",
                "confidence": 0.0,
            }

        # Prepare context - extract key info
        context_text = ""
        for ctx in contexts:
            src = ctx.get("doc", ctx.get("ticket_id", "Unknown"))
            content = ctx.get("content", ctx.get("text", ""))
            context_text += f"- Source: {src}\n  Content: {content}\n\n"

        prompt = (
            f"{SYSTEM_RULE}\n\n"
            f"User Query: {query}\n\n"
            f"Context:\n{context_text}\n\n"
            "Now provide your response as JSON with 'answer' and 'confidence' keys."
        )

        try:
            raw = self.client.generate(prompt, temperature=0.2)

            # Try to extract JSON from response
            try:
                # Handle potential markdown
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0]
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0]

                data = json.loads(raw.strip())

                # Ensure confidence is a number
                if isinstance(data.get("confidence"), str):
                    conf = data["confidence"].lower()
                    if conf in ["high", "0.8", "0.9", "1.0"]:
                        data["confidence"] = 0.85
                    elif conf in ["medium", "0.5", "0.6"]:
                        data["confidence"] = 0.6
                    else:
                        data["confidence"] = 0.4

                return data
            except json.JSONDecodeError:
                # Return raw text as answer with default confidence
                return {"answer": raw, "confidence": 0.5}

        except Exception as e:
            return {"answer": f"Error generating response: {str(e)}", "confidence": 0.0}
