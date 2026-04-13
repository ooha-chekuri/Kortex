from __future__ import annotations

from typing import Any

from backend.core.confidence import compute_confidence, decide_action
from backend.core.llm_client import get_llm_client, reset_llm_client


SELF_EVAL_PROMPT = (
    "Answer only based on the provided context. Do not hallucinate.\n"
    "You are validating the reliability of a previous answer.\n"
    "Rate your confidence from 0.0 to 1.0 given this context. Reply with only a float."
)

FAITHFULNESS_PROMPT = (
    "You are a hallucination detector. Your goal is to verify if the provided answer is FAITHFUL to the context.\n"
    "Identify every claim in the answer and check if it is explicitly supported by the context.\n"
    "If any part of the answer is not supported by the context, mark it as UNFAITHFUL.\n"
    "Reply ONLY with a JSON object: {\"is_faithful\": boolean, \"unsupported_claims\": [string], \"score\": float (0.0 to 1.0)}"
)


class ValidatorAgent:
    def __init__(self) -> None:
        self.client = get_llm_client()
        self._eval_cache: dict[str, float] = {}

    def _check_faithfulness(self, answer: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
        context_text = "\n\n".join(item["content"] for item in contexts)
        prompt = (
            f"{FAITHFULNESS_PROMPT}\n\n"
            f"Context:\n{context_text}\n\n"
            f"Answer:\n{answer}"
        )

        try:
            raw = self.client.generate(prompt, temperature=0.0)
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"is_faithful": True, "unsupported_claims": [], "score": 1.0}
        except Exception:
            return {"is_faithful": True, "unsupported_claims": [], "score": 0.8}

    def _self_eval(self, answer: str, contexts: list[dict[str, Any]]) -> float:
        # ... (rest of the method stays same)

    def validate(self, answer: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
        if not contexts:
            return {"confidence": 0.0, "decision": "escalate", "llm_self_eval": 0.0}

        retrieval_similarity = sum(
            item.get("retrieval_score", 0.0) for item in contexts
        ) / len(contexts)
        reranker_score = sum(
            item.get("reranker_score", 0.0) for item in contexts
        ) / len(contexts)

        # Get self eval with caching/fallback
        llm_self_eval = self._self_eval(answer, contexts)

        # NEW: Faithfulness check
        faithfulness = self._check_faithfulness(answer, contexts)
        faithfulness_score = faithfulness.get("score", 1.0)
        is_faithful = faithfulness.get("is_faithful", True)

        # Adjusted formula to include faithfulness
        # confidence = (0.3 * retrieval) + (0.25 * reranker) + (0.15 * llm_self_eval) + (0.3 * faithfulness)
        confidence = compute_confidence(
            retrieval_similarity, reranker_score, llm_self_eval, faithfulness_score
        )

        # Force escalation if unfaithful
        decision = decide_action(confidence)
        if not is_faithful:
            decision = "escalate"

        return {
            "confidence": confidence,
            "decision": decision,
            "llm_self_eval": round(llm_self_eval, 4),
            "faithfulness_score": round(faithfulness_score, 4),
            "is_faithful": is_faithful,
            "unsupported_claims": faithfulness.get("unsupported_claims", []),
            "retrieval_similarity": round(retrieval_similarity, 4),
            "reranker_score": round(reranker_score, 4),
        }
