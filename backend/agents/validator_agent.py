from __future__ import annotations

from typing import Any

from backend.core.confidence import compute_confidence, decide_action
from backend.core.llm_client import get_llm_client


SELF_EVAL_PROMPT = (
    "Answer only based on the provided context. Do not hallucinate.\n"
    "You are validating the reliability of a previous answer.\n"
    "Rate your confidence from 0.0 to 1.0 given this context. Reply with only a float."
)


class ValidatorAgent:
    def __init__(self) -> None:
        self.client = get_llm_client()

    def _self_eval(self, answer: str, contexts: list[dict[str, Any]]) -> float:
        context_preview = "\n\n".join(item["content"][:500] for item in contexts)
        prompt = (
            f"{SELF_EVAL_PROMPT}\n\n"
            f"Answer:\n{answer}\n\n"
            f"Context:\n{context_preview}"
        )
        raw = self.client.generate(prompt, temperature=0.0)
        try:
            value = float(raw.strip())
        except ValueError:
            value = 0.3
        return max(0.0, min(1.0, value))

    def validate(self, answer: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
        if not contexts:
            return {"confidence": 0.0, "decision": "escalate", "llm_self_eval": 0.0}

        retrieval_similarity = sum(
            item.get("retrieval_score", 0.0) for item in contexts
        ) / len(contexts)
        reranker_score = sum(item.get("reranker_score", 0.0) for item in contexts) / len(contexts)
        llm_self_eval = self._self_eval(answer, contexts)
        confidence = compute_confidence(retrieval_similarity, reranker_score, llm_self_eval)

        return {
            "confidence": confidence,
            "decision": decide_action(confidence),
            "llm_self_eval": round(llm_self_eval, 4),
            "retrieval_similarity": round(retrieval_similarity, 4),
            "reranker_score": round(reranker_score, 4),
        }
