# Kortex System Updates - April 2026

This document summarizes the major enhancements made to the Kortex Knowledge Copilot to meet and exceed the Enterprise Knowledge Copilot (RAG + Agentic Workflow) requirements.
13-04-2026.

## 1. Reliability & Evaluation
- **Automated Evaluation Suite**: Created `scripts/run_evaluation.py` and `tests/evaluation_dataset.json`. The system now generates an `evaluation_report.md` measuring Precision@K, Recall@K, and MRR.
- **Hallucination Guardrails**: Enhanced `ValidatorAgent` with a dedicated **Faithfulness/NLI check**. It now explicitly verifies every claim in an answer against the retrieved context before approving a response.

## 2. Agentic Intelligence
- **Dynamic ReAct Workflow**: Refactored the `Orchestrator` to use a **Planning Agent**. The system no longer follows a fixed pipeline but autonomously decides which tools (Search, Summarize, Validate, etc.) to use based on the query.
- **Summarization Agent**: Added a specialized `SummarizerAgent` tool for handling long context and providing executive summaries.
- **Duplicate Ticket Detection**: Integrated a `check_duplicates` tool that flags similar historical incidents (threshold > 0.85) to prevent redundant support effort.

## 3. Data Infrastructure
- **Advanced Recursive Chunking**: Replaced simple word-based splitting with a recursive character-based strategy in `ingest.py` to preserve document hierarchy and semantic structure.
- **Incremental Ingestion**: Implemented MD5 hashing in the ingestion pipeline to track file changes and skip indexing for unchanged documents.

## 4. DevOps & Deployment
- **Containerization**: Added `Dockerfile.backend`, `Dockerfile.frontend`, and `docker-compose.yml` for unified, cross-platform deployment.
