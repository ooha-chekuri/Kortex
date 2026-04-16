from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from backend.core.embedder import embed_query


INDEX_DIR = Path(__file__).resolve().parents[2] / "data" / "ticket_index"
INDEX_PATH = INDEX_DIR / "tickets.index"
METADATA_PATH = INDEX_DIR / "metadata.json"


class TicketAgent:
    def __init__(self) -> None:
        self.index = None
        self.metadata: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not INDEX_PATH.exists() or not METADATA_PATH.exists():
            return
        self.index = faiss.read_index(str(INDEX_PATH))
        self.metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    def is_ready(self) -> bool:
        return self.index is not None and bool(self.metadata)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        if not self.is_ready():
            return []

        query_vector = np.asarray([embed_query(query)], dtype="float32")
        scores, indices = self.index.search(query_vector, top_k)

        results: list[dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0], strict=False):
            if idx < 0 or idx >= len(self.metadata):
                continue
            item = dict(self.metadata[idx])
            item["retrieval_score"] = float(max(0.0, min(1.0, score)))
            item["source_type"] = "ticket"
            results.append(item)
        return results
