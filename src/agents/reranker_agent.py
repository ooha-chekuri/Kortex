from __future__ import annotations

from functools import lru_cache
from typing import Any

from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker_model = None


def get_reranker_model() -> CrossEncoder:
    global _reranker_model
    if _reranker_model is None:
        _reranker_model = CrossEncoder(MODEL_NAME)
    return _reranker_model


class RerankerAgent:
    def rerank(
        self, query: str, items: list[dict[str, Any]], top_k: int = 3
    ) -> list[dict[str, Any]]:
        if not items:
            return []

        pairs = [(query, item.get("content", item.get("text", ""))) for item in items]
        model = get_reranker_model()
        raw_scores = model.predict(pairs)

        scored_items: list[dict[str, Any]] = []
        min_score = float(min(raw_scores))
        max_score = float(max(raw_scores))
        score_range = max(max_score - min_score, 1e-6)

        for item, raw_score in zip(items, raw_scores, strict=False):
            normalized = (float(raw_score) - min_score) / score_range
            enriched = dict(item)
            enriched["reranker_score"] = round(max(0.0, min(1.0, normalized)), 4)
            scored_items.append(enriched)

        scored_items.sort(
            key=lambda candidate: (
                candidate.get("reranker_score", 0.0),
                candidate.get("retrieval_score", 0.0),
            ),
            reverse=True,
        )
        return scored_items[:top_k]
