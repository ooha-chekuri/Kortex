# Kortex Architecture

## System Overview

Kortex is an **Agentic Enterprise Knowledge Copilot** - a multi-agent RAG system that:
- Retrieves enterprise knowledge (documents + support tickets)
- Uses agentic decision-making (Plan → Execute → Validate)
- Applies reranking for precision
- Generates grounded responses with citations
- Computes confidence scores and supports escalation

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                    USER                        │
                    │               (Query Input)                  │
                    └─────────────────────┬───────────────────────┘
                                          │
                    ┌───────────────────┴───────────────────────┐
                    │          ORCHESTRATOR                    │
                    │    (ReAct Agent Controller)             │
                    └─────────────────┬─────────────────────┘
                                      │
              ┌───────────────┬──────────┼───────────┬─────────────┐
              │               │          │           │             │
    ┌─────────┴─────────┐   │    ┌────┴────┐    │    ┌────────┴────────┐
    │  TRIAGE AGENT     │   │    │VALIDATOR│    │  SYNTHESIS      │
    │  (Intent        │   │    │ AGENT   │    │  AGENT         │
    │   Classification)  │   │    │(Conf.  │    │  (LLM         │
    └─────────┬─────────┘   │    │ Score) │    │  Generation)  │
              │         │    └───┬────┘    │    └───────┬────────┘
              │         │        │            │            │
    ┌─────────┴─────────┐   │    ┌────┴────┐    │            │
    │RETRIEVAL AGENT    │◄────────┴─────►│            │
    │  (FAISS Search)  │              │            │            │
    └─────────┬─────────┘              │            │            │
              │                     │            │            │
    ┌─────────┴─────────┐    ┌────┴────┐            │
    │  TICKET AGENT    │◄───┤RERANKER│            │
    │  (Ticket      │    │ AGENT  │            │
    │   Search)    │    └───────┘            │
    └────────────────┘                       │
                                              │
                                      ┌───────┴───────┐
                                      │   RESPONSE   │
                                      │ + Sources   │
                                      │ + Confidence│
                                      │ + Trace    │
                                      └─────────────┘
```

## Components

### 1. Triage Agent
- **Purpose**: Classifies query intent to decide tool usage
- **Inputs**: User query string
- **Outputs**: Intent classification (`docs`, `tickets`, or `both`)
- **Implementation**: Keyword-based classification

### 2. Retrieval Agent
- **Purpose**: Searches document FAISS index
- **Inputs**: User query, top_k
- **Outputs**: Top-K document chunks with scores
- **Implementation**: FAISS + sentence-transformers embeddings

### 3. Ticket Agent
- **Purpose**: Searches historical tickets
- **Inputs**: User query, top_k
- **Outputs**: Top-K matching tickets
- **Implementation**: FAISS + sentence-transformers embeddings

### 4. Reranker Agent
- **Purpose**: Re-ranks retrieved results
- **Inputs**: Query + retrieved items
- **Outputs**: Re-ranked items with cross-encoder scores
- **Implementation**: cross-encoder/ms-marco-MiniLM-L-6-v2

### 5. Synthesis Agent
- **Purpose**: Generates LLM response with citations
- **Inputs**: Query + context items
- **Outputs**: Grounded answer
- **Implementation**: Gemini/OpenAI/Ollama

### 6. Validator Agent
- **Purpose**: Computes confidence and decides action
- **Inputs**: Answer + contexts
- **Outputs**: Confidence score + decision
- **Formula**: `confidence = 0.5*retrieval + 0.3*reranker + 0.2*llm_self_eval`

### 7. Orchestrator
- **Purpose**: Coordinates the agent pipeline
- **Features**: Retry logic, escalation, trace logging

## Data Flow

1. **Query Input** → Triage Agent determines search scope
2. **Search** → Retrieval Agent + Ticket Agent fetch context
3. **Rerank** → Reranker Agent re-orders results
4. **Generate** → Synthesis Agent creates answer
5. **Validate** → Validator Agent computes confidence

## Decision Logic

| Confidence | Decision | Action |
|------------|----------|--------|
| > 0.75 | Respond | Return answer + sources |
| 0.5 - 0.75 | Retry | Expand retrieval and retry once |
| < 0.5 | Escalate | Return escalation message |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI |
| LLM | Gemini 2.0 Flash (configurable) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | FAISS |
| Reranking | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| Frontend | React + Vite |
| Data | PDF (pypdf) + CSV (pandas) |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ingest` | POST | Index data to FAISS |
| `/query` | POST | Run full pipeline |

## File Structure

```
/kortex
├── scripts/                  # Data collection scripts
│   ├── download_docs.py      # Download public docs
│   ├── generate_data.py      # Generate synthetic data
│   └── run_full_ingestion.py # Run full ingestion
├── backend/                  # Backend code
│   ├── main.py              # FastAPI app
│   ├── agents/              # Agent modules
│   │   ├── triage_agent.py
│   │   ├── retrieval_agent.py
│   │   ├── ticket_agent.py
│   │   ├── reranker_agent.py
│   │   ├── synthesis_agent.py
│   │   └── validator_agent.py
│   ├── core/                # Core utilities
│   │   ├── orchestrator.py
│   │   ├── embedder.py
│   │   ├── llm_client.py
│   │   └── confidence.py
│   ├── data/                # Data handling
│   │   └── ingest.py
│   └── services/            # Services
│       └── evaluation.py
├── frontend/                # React frontend
├── data/                   # Data storage
│   ├── public_docs/         # Downloaded docs
│   ├── synthetic/           # Generated data
│   ├── faiss_index/        # Document index
│   └─��� ticket_index/       # Ticket index
└── docs/                    # Documentation
```