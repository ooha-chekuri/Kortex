"""
Evaluation service for Kortex RAG pipeline.
Implements Precision@K, Recall@K, MRR, and other metrics.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EvaluationService:
    """Evaluation metrics for RAG pipeline."""

    def __init__(self) -> None:
        self.model = SentenceTransformer(MODEL_NAME)

    def precision_at_k(
        self,
        retrieved_docs: list[dict[str, Any]],
        relevance_scores: list[float],
        k: int = 5,
    ) -> float:
        """Calculate Precision@K.

        Args:
            retrieved_docs: List of retrieved documents
            relevance_scores: Relevance scores (0 or 1 for binary, 0-1 for graded)
            k: Number of top results to consider

        Returns:
            Precision@K score
        """
        if not retrieved_docs or k <= 0:
            return 0.0

        top_k = min(k, len(retrieved_docs), len(relevance_scores))
        if top_k == 0:
            return 0.0

        relevant_at_k = sum(relevance_scores[i] for i in range(top_k))
        return relevant_at_k / top_k

    def recall_at_k(
        self,
        retrieved_docs: list[dict[str, Any]],
        relevance_scores: list[float],
        k: int = 5,
    ) -> float:
        """Calculate Recall@K.

        Args:
            retrieved_docs: List of retrieved documents
            relevance_scores: Relevance scores for all relevant docs
            k: Number of top results to consider

        Returns:
            Recall@K score
        """
        if not relevance_scores:
            return 0.0

        total_relevant = sum(1 for s in relevance_scores if s > 0)
        if total_relevant == 0:
            return 0.0

        top_k = min(k, len(retrieved_docs), len(relevance_scores))
        relevant_at_k = sum(relevance_scores[i] for i in range(top_k))
        return relevant_at_k / total_relevant

    def mean_reciprocal_rank(
        self,
        retrieved_docs: list[dict[str, Any]],
        relevance_scores: list[float],
    ) -> float:
        """Calculate Mean Reciprocal Rank (MRR).

        Args:
            retrieved_docs: List of retrieved documents
            relevance_scores: Relevance scores (binary 0 or 1)

        Returns:
            MRR score
        """
        if not retrieved_docs or not relevance_scores:
            return 0.0

        for i, score in enumerate(relevance_scores):
            if score > 0:
                return 1.0 / (i + 1)

        return 0.0

    def average_precision(
        self,
        retrieved_docs: list[dict[str, Any]],
        relevance_scores: list[float],
    ) -> float:
        """Calculate Average Precision (AP).

        Args:
            retrieved_docs: List of retrieved documents
            relevance_scores: Relevance scores

        Returns:
            Average precision score
        """
        if not retrieved_docs or not relevance_scores:
            return 0.0

        num_relevant = 0
        sum_precision = 0.0

        for i, score in enumerate(relevance_scores):
            if score > 0:
                num_relevant += 1
                precision_at_i = sum(relevance_scores[j] for j in range(i + 1)) / (
                    i + 1
                )
                sum_precision += precision_at_i

        if num_relevant == 0:
            return 0.0

        return sum_precision / num_relevant

    def mean_average_precision(
        self,
        queries_results: list[list[dict[str, Any]]],
        all_relevance_scores: list[list[float]],
    ) -> float:
        """Calculate Mean Average Precision (MAP).

        Args:
            queries_results: List of query results (each is a list of retrieved docs)
            all_relevance_scores: List of relevance scores for each query

        Returns:
            MAP score
        """
        if not queries_results or not all_relevance_scores:
            return 0.0

        ap_scores = [
            self.average_precision(docs, scores)
            for docs, scores in zip(queries_results, all_relevance_scores)
        ]
        return sum(ap_scores) / len(ap_scores)

    def semantic_similarity(
        self,
        text1: str,
        text2: str,
    ) -> float:
        """Calculate semantic similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1
        """
        embeddings = self.model.encode([text1, text2])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(max(0.0, min(1.0, similarity)))

    def ndcg_at_k(
        self,
        retrieved_docs: list[dict[str, Any]],
        relevance_scores: list[float],
        k: int = 5,
    ) -> float:
        """Calculate Normalized Discounted Cumulative Gain (NDCG@K).

        Args:
            retrieved_docs: List of retrieved documents
            relevance_scores: Relevance scores
            k: Number of top results to consider

        Returns:
            NDCG@K score
        """
        if not relevance_scores or k <= 0:
            return 0.0

        top_k = min(k, len(retrieved_docs), len(relevance_scores))
        if top_k == 0:
            return 0.0

        dcg = 0.0
        for i in range(top_k):
            rel = relevance_scores[i] if i < len(relevance_scores) else 0
            dcg += rel / np.log2(i + 2)

        ideal_scores = sorted(relevance_scores, reverse=True)
        idcg = 0.0
        for i in range(top_k):
            rel = ideal_scores[i] if i < len(ideal_scores) else 0
            idcg += rel / np.log2(i + 2)

        if idcg == 0:
            return 0.0

        return dcg / idcg

    def f1_score(
        self,
        precision: float,
        recall: float,
    ) -> float:
        """Calculate F1 score from precision and recall.

        Args:
            precision: Precision score
            recall: Recall score

        Returns:
            F1 score
        """
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def evaluate_retrieval(
        self,
        query: str,
        retrieved_docs: list[dict[str, Any]],
        ground_truthrelevant_docs: list[dict[str, Any]],
    ) -> dict[str, float]:
        """Run full retrieval evaluation.

        Args:
            query: The query string
            retrieved_docs: Retrieved documents
            ground_truthrelevant_docs: Ground truth relevant documents

        Returns:
            Dictionary of evaluation metrics
        """
        if not retrieved_docs:
            return {
                "precision_at_1": 0.0,
                "precision_at_3": 0.0,
                "precision_at_5": 0.0,
                "recall_at_1": 0.0,
                "recall_at_3": 0.0,
                "recall_at_5": 0.0,
                "mrr": 0.0,
                "map": 0.0,
                "ndcg_at_5": 0.0,
            }

        relevance_scores = []
        for doc in retrieved_docs:
            is_relevant = any(
                self._is_relevant(doc, gt) for gt in ground_truthrelevant_docs
            )
            relevance_scores.append(1.0 if is_relevant else 0.0)

        return {
            "precision_at_1": self.precision_at_k(retrieved_docs, relevance_scores, 1),
            "precision_at_3": self.precision_at_k(retrieved_docs, relevance_scores, 3),
            "precision_at_5": self.precision_at_k(retrieved_docs, relevance_scores, 5),
            "recall_at_1": self.recall_at_k(retrieved_docs, relevance_scores, 1),
            "recall_at_3": self.recall_at_k(retrieved_docs, relevance_scores, 3),
            "recall_at_5": self.recall_at_k(retrieved_docs, relevance_scores, 5),
            "mrr": self.mean_reciprocal_rank(retrieved_docs, relevance_scores),
            "map": self.average_precision(retrieved_docs, relevance_scores),
            "ndcg_at_5": self.ndcg_at_k(retrieved_docs, relevance_scores, 5),
        }

    def _is_relevant(
        self,
        retrieved_doc: dict[str, Any],
        ground_truth_doc: dict[str, Any],
    ) -> bool:
        """Check if a document is relevant based on content matching."""
        retrieved_content = retrieved_doc.get("content", "").lower()
        gt_content = ground_truth_doc.get("content", "").lower()

        if retrieved_content == gt_content:
            return True

        if retrieved_doc.get("doc") == ground_truth_doc.get("doc"):
            if retrieved_doc.get("page") == ground_truth_doc.get("page"):
                return True

        if retrieved_doc.get("ticket_id") == ground_truth_doc.get("ticket_id"):
            return True

        return False


_evaluation_service: EvaluationService | None = None


def get_evaluation_service() -> EvaluationService:
    """Get the evaluation service singleton."""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = EvaluationService()
    return _evaluation_service


def evaluate_query(
    query: str,
    retrieved_docs: list[dict[str, Any]],
    ground_truthrelevant_docs: list[dict[str, Any]],
) -> dict[str, float]:
    """Convenience function to evaluate a single query.

    Args:
        query: The query string
        retrieved_docs: Retrieved documents
        ground_truthrelevant_docs: Ground truth relevant documents

    Returns:
        Dictionary of evaluation metrics
    """
    service = get_evaluation_service()
    return service.evaluate_retrieval(query, retrieved_docs, ground_truthrelevant_docs)
