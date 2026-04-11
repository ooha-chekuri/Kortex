from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import faiss
import pandas as pd
from pypdf import PdfReader

from backend.core.embedder import embed_texts


BASE_DIR = Path(__file__).resolve().parents[2]
# Check both docs folder and synthetic SOPs folder
DOCS_DIR = BASE_DIR / "docs"
SYNTHETIC_SOPS = BASE_DIR / "data" / "synthetic" / "sops"
DATA_DIR = BASE_DIR / "backend" / "data"
DOC_INDEX_DIR = DATA_DIR / "faiss_index"
TICKET_INDEX_DIR = DATA_DIR / "ticket_index"
TICKETS_CSV = DATA_DIR / "sample_tickets.csv"

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"
)


def redact_pii(text: str) -> str:
    text = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    text = PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
    return text


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_size)
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(words):
            break
        start = max(0, end - overlap)
    return chunks


def load_pdf_chunks() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    # Check docs folder
    pdf_dirs = [DOCS_DIR]
    if SYNTHETIC_SOPS.exists():
        pdf_dirs.append(SYNTHETIC_SOPS)

    for pdf_dir in pdf_dirs:
        for pdf_path in sorted(pdf_dir.glob("*.pdf")):
            try:
                reader = PdfReader(str(pdf_path))
                for page_number, page in enumerate(reader.pages, start=1):
                    text = (page.extract_text() or "").strip()
                    if not text:
                        continue
                    for chunk_id, chunk in enumerate(chunk_text(text), start=1):
                        records.append(
                            {
                                "doc": pdf_path.name,
                                "page": page_number,
                                "chunk_id": chunk_id,
                                "content": chunk,
                            }
                        )
            except Exception as e:
                print(f"Error loading {pdf_path}: {e}")
    return records


def save_faiss_index(
    records: list[dict[str, Any]], output_dir: Path, stem: str
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    embeddings = embed_texts(item["content"] for item in records)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, str(output_dir / f"{stem}.index"))
    (output_dir / "metadata.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )


def ingest_docs() -> dict[str, Any]:
    records = load_pdf_chunks()
    if not records:
        return {"documents_indexed": 0, "chunks_indexed": 0}
    save_faiss_index(records, DOC_INDEX_DIR, "docs")
    unique_docs = sorted({item["doc"] for item in records})
    return {
        "documents_indexed": len(unique_docs),
        "chunks_indexed": len(records),
        "documents": unique_docs,
    }


def ingest_tickets() -> dict[str, Any]:
    if not TICKETS_CSV.exists():
        return {"tickets_indexed": 0}

    frame = pd.read_csv(TICKETS_CSV)
    records: list[dict[str, Any]] = []
    for row in frame.to_dict(orient="records"):
        content = " ".join(
            [
                redact_pii(str(row.get("title", ""))),
                redact_pii(str(row.get("description", ""))),
                redact_pii(str(row.get("resolution", ""))),
                redact_pii(str(row.get("category", ""))),
            ]
        ).strip()
        records.append(
            {
                "ticket_id": row["ticket_id"],
                "title": redact_pii(str(row.get("title", ""))),
                "description": redact_pii(str(row.get("description", ""))),
                "resolution": redact_pii(str(row.get("resolution", ""))),
                "category": redact_pii(str(row.get("category", ""))),
                "content": content,
            }
        )

    save_faiss_index(records, TICKET_INDEX_DIR, "tickets")
    return {"tickets_indexed": len(records)}


def run_ingestion() -> dict[str, Any]:
    docs_summary = ingest_docs()
    tickets_summary = ingest_tickets()
    return {"docs": docs_summary, "tickets": tickets_summary}


if __name__ == "__main__":
    print(json.dumps(run_ingestion(), indent=2))
