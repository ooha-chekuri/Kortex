import json
import faiss
import numpy as np
from typing import List, Dict, Any, Optional
from src.core.config import (
    DOC_INDEX_DIR,
    TICKET_INDEX_DIR,
    TOP_K_RETRIEVAL,
    TOP_K_RERANK,
)
from src.core.embedder import embed_query
from src.agents.reranker_agent import RerankerAgent


class RetrievalEngine:
    """Fast retrieval engine with optional reranking."""

    def __init__(self, use_reranker: bool = True):
        self.doc_index = None
        self.ticket_index = None
        self.doc_metadata = []
        self.ticket_metadata = []
        self.reranker = RerankerAgent() if use_reranker else None
        self.use_reranker = use_reranker
        self._load()

    def _load(self):
        # Docs
        doc_idx_path = DOC_INDEX_DIR / "docs.index"
        doc_meta_path = DOC_INDEX_DIR / "metadata.json"
        if doc_idx_path.exists() and doc_meta_path.exists():
            self.doc_index = faiss.read_index(str(doc_idx_path))
            self.doc_metadata = json.loads(doc_meta_path.read_text(encoding="utf-8"))

        # Tickets
        ticket_idx_path = TICKET_INDEX_DIR / "tickets.index"
        ticket_meta_path = TICKET_INDEX_DIR / "metadata.json"
        if ticket_idx_path.exists() and ticket_meta_path.exists():
            self.ticket_index = faiss.read_index(str(ticket_idx_path))
            self.ticket_metadata = json.loads(
                ticket_meta_path.read_text(encoding="utf-8")
            )

    def search(
        self, query: str, type: str = "both", top_k: int = TOP_K_RETRIEVAL
    ) -> List[Dict[str, Any]]:
        """Performs initial top-k retrieval."""
        results = []
        query_vec = np.asarray([embed_query(query)], dtype="float32")

        # Doc search
        if (type in ["docs", "both"]) and self.doc_index:
            scores, indices = self.doc_index.search(query_vec, top_k)
            for s, idx in zip(scores[0], indices[0]):
                if idx < 0:
                    continue
                item = self.doc_metadata[idx].copy()
                item["retrieval_score"] = float(s)
                item["source_type"] = "doc"
                results.append(item)

        # Ticket search
        if (type in ["tickets", "both"]) and self.ticket_index:
            scores, indices = self.ticket_index.search(query_vec, top_k)
            for s, idx in zip(scores[0], indices[0]):
                if idx < 0:
                    continue
                item = self.ticket_metadata[idx].copy()
                item["retrieval_score"] = float(s)
                item["source_type"] = "ticket"
                results.append(item)

        return results

    def get_context(
        self,
        query: str,
        type: str = "both",
        top_k: int = TOP_K_RETRIEVAL,
        rerank_k: int = TOP_K_RERANK,
    ) -> List[Dict[str, Any]]:
        """Retrieves and optionally reranks context."""
        initial_results = self.search(query, type, top_k=top_k)
        if not initial_results:
            return []

        # Rerank (optional for speed)
        if self.use_reranker and self.reranker:
            return self.reranker.rerank(query, initial_results, top_k=rerank_k)

        # No reranking - just return top k results sorted by score
        return initial_results[:rerank_k]


# Singleton with caching
_engine = None


def get_retrieval_engine() -> RetrievalEngine:
    global _engine
    if _engine is None:
        _engine = RetrievalEngine(use_reranker=True)  # Enable reranker for quality
    return _engine
