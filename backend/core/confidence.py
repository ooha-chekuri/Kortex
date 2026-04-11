from __future__ import annotations


def compute_confidence(
    retrieval_similarity: float,
    reranker_score: float,
    llm_self_eval: float,
) -> float:
    # Adjusted weights: more forgiving of low self-eval
    # If self-eval is 0 (LLM failed), default to 0.5
    effective_self_eval = llm_self_eval if llm_self_eval > 0 else 0.5

    score = (
        (0.4 * retrieval_similarity)
        + (0.35 * reranker_score)
        + (0.25 * effective_self_eval)
    )
    # Apply a minimum floor based on retrieval success
    if retrieval_similarity > 0.3 and reranker_score > 0.3:
        score = max(score, 0.55)  # Minimum 0.55 if we have decent retrieval

    return max(0.0, min(1.0, round(score, 4)))


def decide_action(confidence: float) -> str:
    # Even lower thresholds - more likely to respond
    if confidence >= 0.5:
        return "respond"
    if confidence >= 0.35:
        return "retry"
    return "escalate"
