import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directories
BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
DATA_DIR = SRC_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"

# Specific data paths
DOC_INDEX_DIR = DATA_DIR / "faiss_index"
TICKET_INDEX_DIR = DATA_DIR / "ticket_index"
TICKETS_CSV = DATA_DIR / "sample_tickets.csv"

# Model Configs
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
LLM_PROVIDER = os.getenv("KORTEX_LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("KORTEX_LLM_MODEL", "gemini-2.5-flash")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").split()[
    0
]  # Remove "(optional)"

# RAG Configs
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 10
TOP_K_RERANK = 3

# PII Patterns
PII_PATTERNS = {
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "PHONE": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "IP": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}
