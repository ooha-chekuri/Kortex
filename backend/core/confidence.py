from __future__ import annotations


def compute_confidence(
    retrieval_similarity: float,
    reranker_score: float,
    llm_self_eval: float,
) -> float:
    score = (
        (0.5 * retrieval_similarity)
        + (0.3 * reranker_score)
        + (0.2 * llm_self_eval)
    )
    return max(0.0, min(1.0, round(score, 4)))


def decide_action(confidence: float) -> str:
    if confidence > 0.75:
        return "respond"
    if confidence >= 0.5:
        return "retry"
    return "escalate"
