"""
Full data ingestion orchestrator.
Combines all data sources and builds FAISS indices.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Add parent directory to path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.core.embedder import embed_texts
from backend.data.ingest import (
    chunk_text,
    redact_pii,
    save_faiss_index,
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DOC_INDEX_DIR = DATA_DIR / "faiss_index"
TICKET_INDEX_DIR = DATA_DIR / "ticket_index"


def load_public_docs() -> list[dict[str, Any]]:
    """Load public documentation from downloaded text files."""
    records = []
    text_dir = DATA_DIR / "public_docs" / "text"

    if not text_dir.exists():
        print(f"Warning: Public docs directory not found: {text_dir}")
        return records

    for doc_dir in text_dir.iterdir():
        if not doc_dir.is_dir():
            continue

        doc_name = doc_dir.name
        for txt_file in doc_dir.glob("*.txt"):
            try:
                text = txt_file.read_text(encoding="utf-8")
                if len(text) < 100:
                    continue

                chunks = chunk_text(text, chunk_size=500, overlap=50)
                for chunk_id, chunk in enumerate(chunks, start=1):
                    records.append(
                        {
                            "source": "public_doc",
                            "doc_source": doc_name,
                            "file": f"{doc_dir.name}/{txt_file.name}",
                            "chunk_id": chunk_id,
                            "content": chunk,
                        }
                    )
            except Exception as e:
                print(f"Error loading {txt_file}: {e}")

    return records


def load_sops() -> list[dict[str, Any]]:
    """Load SOP PDFs."""
    records = []
    sops_dir = DATA_DIR / "synthetic" / "sops"

    if not sops_dir.exists():
        print(f"Warning: SOPs directory not found: {sops_dir}")
        return records

    from pypdf import PdfReader

    for pdf_file in sops_dir.glob("*.pdf"):
        try:
            reader = PdfReader(str(pdf_file))
            for page_number, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if not text:
                    continue

                chunks = chunk_text(text, chunk_size=500, overlap=50)
                for chunk_id, chunk in enumerate(chunks, start=1):
                    records.append(
                        {
                            "source": "sop",
                            "doc_source": "sop",
                            "file": pdf_file.name,
                            "page": page_number,
                            "chunk_id": chunk_id,
                            "content": chunk,
                        }
                    )
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")

    return records


def load_tickets() -> list[dict[str, Any]]:
    """Load support tickets from CSV."""
    records = []

    # Check synthetic tickets first
    ticket_csv = DATA_DIR / "synthetic" / "tickets.csv"
    if ticket_csv.exists():
        return _load_tickets_csv(ticket_csv)

    # Fallback to original sample tickets
    ticket_csv = BASE_DIR / "backend" / "data" / "sample_tickets.csv"
    if ticket_csv.exists():
        return _load_tickets_csv(ticket_csv)

    print(f"Warning: Tickets CSV not found")
    return records


def _load_tickets_csv(csv_path: Path) -> list[dict[str, Any]]:
    """Load tickets from CSV file."""
    import pandas as pd

    records = []
    try:
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
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
                    "source": "ticket",
                    "ticket_id": row.get("ticket_id", ""),
                    "title": redact_pii(str(row.get("title", ""))),
                    "description": redact_pii(str(row.get("description", ""))),
                    "resolution": redact_pii(str(row.get("resolution", ""))),
                    "category": redact_pii(str(row.get("category", ""))),
                    "content": content,
                }
            )
    except Exception as e:
        print(f"Error loading tickets from {csv_path}: {e}")

    return records


def run_full_ingestion() -> dict[str, Any]:
    """Run full ingestion pipeline."""
    print("=" * 60)
    print("KORTEX FULL INGESTION PIPELINE")
    print("=" * 60)

    results = {}

    # 1. Load public documentation
    print("\n[1/4] Loading public documentation...")
    public_docs = load_public_docs()
    results["public_docs"] = {"documents": len(public_docs)}
    print(f"  -> Loaded {len(public_docs)} document chunks")

    # 2. Load SOPs
    print("\n[2/4] Loading SOPs...")
    sops = load_sops()
    results["sops"] = {"documents": len(sops)}
    print(f"  -> Loaded {len(sops)} SOP chunks")

    # 3. Build document FAISS index
    print("\n[3/4] Building document FAISS index...")
    all_docs = public_docs + sops
    if all_docs:
        DOC_INDEX_DIR.mkdir(parents=True, exist_ok=True)
        save_faiss_index(all_docs, DOC_INDEX_DIR, "docs")
        results["docs_index"] = {"indexed": len(all_docs)}
        print(f"  -> Indexed {len(all_docs)} document chunks")
    else:
        print("  -> No documents to index")
        results["docs_index"] = {"indexed": 0}

    # 4. Build ticket FAISS index
    print("\n[4/4] Building ticket FAISS index...")
    tickets = load_tickets()
    if tickets:
        TICKET_INDEX_DIR.mkdir(parents=True, exist_ok=True)
        save_faiss_index(tickets, TICKET_INDEX_DIR, "tickets")
        results["tickets_index"] = {"indexed": len(tickets)}
        print(f"  -> Indexed {len(tickets)} tickets")
    else:
        print("  -> No tickets to index")
        results["tickets_index"] = {"indexed": 0}

    # Summary
    print("\n" + "=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)
    print(f"  Public docs: {len(public_docs)} chunks")
    print(f"  SOPs: {len(sops)} chunks")
    print(f"  Total documents: {len(all_docs)}")
    print(f"  Tickets: {len(tickets)}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    print(json.dumps(run_full_ingestion(), indent=2))
