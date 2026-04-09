# Kortex

Kortex is an agentic enterprise knowledge copilot built for hackathon demos. It combines document retrieval, historical ticket retrieval, reranking, LLM synthesis, and confidence-aware validation into one explainable pipeline. The system is optimized for a working end-to-end demo first, with a clean React UI layered on top of a FastAPI backend.

## Project Overview

Kortex routes each question through a multi-agent pipeline that decides whether to search documentation, tickets, or both. It pulls grounded context from FAISS indexes, improves precision with a cross-encoder reranker, and generates a concise answer with source references. A validator computes confidence and either returns the answer, retries once, or escalates to a human.

## Setup Instructions

1. Install backend dependencies.
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Add technical PDFs to [`docs/README.md`](c:/Users/oohac/OneDrive/Documents/Kortex/docs/README.md).

3. Configure your LLM provider.
```bash
# Ollama
set KORTEX_LLM_PROVIDER=ollama
set KORTEX_LLM_MODEL=llama3

# Or OpenAI
set KORTEX_LLM_PROVIDER=openai
set KORTEX_LLM_MODEL=gpt-4.1-mini
set OPENAI_API_KEY=your_key_here
```

4. Start the backend and ingest data.
```bash
uvicorn backend.main:app --reload
curl -X POST http://localhost:8000/ingest
```

5. Start the frontend.
```bash
cd frontend
npm install
npm run dev
```

## Sample Queries To Demo

- `How do I fix Kafka consumer lag after a deployment?`
- `Why would a Kubernetes pod enter CrashLoopBackOff after a config change?`
- `What past incidents mention SSO login loops or auth callback issues?`
- `How should I troubleshoot Kafka SASL authentication failures?`

## Architecture Diagram Description

```text
User Query
  -> Triage Agent
  -> Retrieval Agent (docs) + Ticket Agent (tickets)
  -> Reranker Agent
  -> Synthesis Agent
  -> Validator Agent
     -> respond
     -> retry once with expanded retrieval
     -> escalate to human
```

Each run also records an `agent_trace` so the frontend can show why the system made each decision.

## API Summary

- `GET /health` returns `{"status": "ok"}`
- `POST /ingest` indexes PDFs from `docs/` and tickets from [`backend/data/sample_tickets.csv`](c:/Users/oohac/OneDrive/Documents/Kortex/backend/data/sample_tickets.csv)
- `POST /query` runs the full six-agent RAG pipeline

## Team Roles

- Charan: AI/orchestration
- Oohaa: data/retrieval
- Neelima: frontend
