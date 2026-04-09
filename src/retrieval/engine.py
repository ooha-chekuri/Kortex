import json
import faiss
import numpy as np
import streamlit as st
from typing import List, Dict, Any
from src.core.config import DOC_INDEX_DIR, TICKET_INDEX_DIR, TOP_K_RETRIEVAL, TOP_K_RERANK
from src.core.embedder import embed_query
from src.agents.reranker_agent import RerankerAgent

class RetrievalEngine:
    """Retrieval engine for hybrid search and reranking."""
    def __init__(self):
        self.doc_index = None
        self.ticket_index = None
        self.doc_metadata = []
        self.ticket_metadata = []
        self.reranker = RerankerAgent()
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
            self.ticket_metadata = json.loads(ticket_meta_path.read_text(encoding="utf-8"))

    def search(self, query: str, type: str = "both") -> List[Dict[str, Any]]:
        """Performs initial top-k retrieval."""
        results = []
        query_vec = np.asarray([embed_query(query)], dtype="float32")
        
        # Doc search
        if (type in ["docs", "both"]) and self.doc_index:
            scores, indices = self.doc_index.search(query_vec, TOP_K_RETRIEVAL)
            for s, idx in zip(scores[0], indices[0]):
                if idx < 0: continue
                item = self.doc_metadata[idx].copy()
                item["score"] = float(s)
                results.append(item)
                
        # Ticket search
        if (type in ["tickets", "both"]) and self.ticket_index:
            scores, indices = self.ticket_index.search(query_vec, TOP_K_RETRIEVAL)
            for s, idx in zip(scores[0], indices[0]):
                if idx < 0: continue
                item = self.ticket_metadata[idx].copy()
                item["score"] = float(s)
                results.append(item)
        
        return results

    def get_context(self, query: str, type: str = "both") -> List[Dict[str, Any]]:
        """Retrieves and reranks context."""
        initial_results = self.search(query, type)
        if not initial_results:
            return []
        
        # Rerank
        ranked = self.reranker.rerank(query, initial_results, top_k=TOP_K_RERANK)
        return ranked

@st.cache_resource
def get_retrieval_engine():
    return RetrievalEngine()
