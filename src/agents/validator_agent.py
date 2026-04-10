from __future__ import annotations

from typing import Any

from src.core.confidence import compute_confidence, decide_action
from src.core.llm_client import get_llm_client


SELF_EVAL_PROMPT = (
    "Answer only based on the provided context. Do not hallucinate.\n"
    "You are validating the reliability of a previous answer.\n"
    "Rate your confidence from 0.0 to 1.0 given this context. Reply with only a float."
)


class ValidatorAgent:
    def validate(self, answer: str, contexts: list[dict[str, Any]], llm_self_eval: float = 0.5) -> dict[str, Any]:
        if not contexts:
            return {"confidence": 0.0, "decision": "escalate", "llm_self_eval": 0.0}

        # Use pre-calculated scores from retrieval/reranker
        retrieval_similarity = sum(
            item.get("retrieval_score", 0.0) for item in contexts
        ) / len(contexts)
        reranker_score = sum(item.get("reranker_score", 0.0) for item in contexts) / len(contexts)
        
        # Combined Confidence Formula from PRD
        confidence = compute_confidence(retrieval_similarity, reranker_score, llm_self_eval)

        return {
            "confidence": confidence,
            "decision": decide_action(confidence),
            "llm_self_eval": round(llm_self_eval, 4),
            "retrieval_similarity": round(retrieval_similarity, 4),
            "reranker_score": round(reranker_score, 4),
        }
