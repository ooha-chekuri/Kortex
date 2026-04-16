from __future__ import annotations


def compute_confidence(
    retrieval_similarity: float,
    reranker_score: float,
    llm_self_eval: float,
    faithfulness_score: float = 1.0,
) -> float:
    # Adjusted weights: more forgiving of low self-eval
    # If self-eval is 0 (LLM failed), default to 0.5
    effective_self_eval = llm_self_eval if llm_self_eval > 0 else 0.5

    score = (
        (0.3 * retrieval_similarity)
        + (0.25 * reranker_score)
        + (0.15 * effective_self_eval)
        + (0.3 * faithfulness_score)
    )
    # Apply a minimum floor based on retrieval success
    if retrieval_similarity > 0.3 and reranker_score > 0.3 and faithfulness_score > 0.6:
        score = max(score, 0.55)  # Minimum 0.55 if we have decent retrieval and it's faithful

    return max(0.0, min(1.0, round(score, 4)))


def decide_action(confidence: float) -> str:
    # Even lower thresholds - more likely to respond
    if confidence >= 0.5:
        return "respond"
    if confidence >= 0.35:
        return "retry"
    return "escalate"
