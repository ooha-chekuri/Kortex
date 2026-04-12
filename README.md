# Kortex - Agentic Knowledge Copilot

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0-green" alt="Version">
  <img src="https://img.shields.io/badge/FastAPI-0.115-blue" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-blue" alt="React">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

A production-quality **Multi-Agent RAG System** with Explainable AI (XAI) for enterprise knowledge retrieval. Kortex combines document search, ticket lookup, and LLM generation into an intelligent copilot that explains every decision.

![Kortex Demo](https://via.placeholder.com/800x400?text=Kortex+Agentic+Knowledge+Copilot)

## ✨ Features

| Feature | Description |
|---------|-------------|
| **6-Agent Pipeline** | Triage → Retrieve → Ticket → Rerank → Synthesize → Validate |
| **XAI Explanations** | Every decision explained with human-readable reasoning |
| **Confidence Scoring** | Weighted formula: 0.4×retrieval + 0.35×reranker + 0.25×LLM |
| **Source Citation** | All answers cite their sources |
| **Multi-LLM Support** | Gemini, OpenAI, Ollama, Groq |
| **Pixel Art UI** | Retro terminal-style frontend with animations |
| **Mermaid Diagrams** | Architecture visualized in docs |

## 🏗️ Architecture

```
User Query
    ↓
[Triage Agent]    → Classifies intent (docs/tickets/both)
    ↓
[Retrieval Agent] → Searches FAISS vector DB
    ↓
[Ticket Agent]   → Searches historical tickets
    ↓
[Reranker Agent] → Cross-encoder re-ranking
    ↓
[Synthesis Agent] → LLM generates grounded answer
    ↓
[Validator Agent] → Computes confidence
    ↓
Response + Sources + XAI Trace
```

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/ooha-chekuri/Kortex.git
cd Kortex

# Backend
cd backend
pip install -r requirements.txt

# Frontend  
cd ../frontend
npm install
```

### 2. Configure LLM

Edit `.env`:
```bash
# Choose provider: gemini, openai, ollama, groq
KORTEX_LLM_PROVIDER=ollama
KORTEX_LLM_MODEL=llama3.2:3b

# For Ollama
OLLAMA_HOST=http://localhost:11434

# Or for Gemini
GEMINI_API_KEY=your_key_here
```

### 3. Run

```bash
# From project root (Kortex folder)
# Terminal 1 - Backend
$env:PYTHONPATH = "."  # Windows PowerShell
# or on Linux/Mac: export PYTHONPATH=.
uvicorn backend.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Visit: **http://localhost:5173**

### 4. Test

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I configure VPN?"}'
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ingest` | POST | Index documents to FAISS |
| `/query` | POST | Run RAG pipeline |
| `/docs` | GET | API documentation |

## 🎯 Confidence System

```
confidence = (0.4 × retrieval) + (0.35 × reranker) + (0.25 × llm_self_eval)
```

| Confidence | Action |
|------------|--------|
| ≥ 0.5 | Respond with answer |
| ≥ 0.35 | Retry with expanded search |
| < 0.35 | Escalate to human |

## 📁 Project Structure

```
Kortex/
├── backend/
│   ├── agents/           # 6 agent modules
│   │   ├── triage_agent.py
│   │   ├── retrieval_agent.py
│   │   ├── ticket_agent.py
│   │   ├── reranker_agent.py
│   │   ├── synthesis_agent.py
│   │   └── validator_agent.py
│   ├── core/            # Orchestrator, LLM client
│   ├── services/        # XAI, Evaluation
│   └── data/           # Ingestion, FAISS
├── frontend/
│   └── src/
│       └── components/
│           ├── Documentation.jsx  # Docs with Mermaid
│           ├── PixelAgent.jsx    # Animated agents
│           └── ...
├── scripts/            # Data generation
├── data/               # Indices (auto-generated)
└── docs/               # Architecture docs
```

## 📊 Data Sources

- **26 SOP PDFs** - VPN, Password Reset, Kubernetes, Kafka, etc.
- **250 IT Tickets** - Sample support tickets with resolutions
- **Custom Data** - Add PDFs to `docs/` and run `/ingest`

## 🧪 Testing

```bash
# Backend tests
pytest tests/test_agents.py -v

# Manual test
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the password reset procedure?"}'
```

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Make changes
4. Submit PR

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- FastAPI & Uvicorn
- Sentence Transformers
- FAISS
- React + Vite
- Mermaid.js
- Phosphor Icons
