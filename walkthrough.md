# Kortex Walkthrough

A complete guide to setting up, running, and testing the Kortex Agentic Knowledge Copilot.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Running the Application](#running-the-application)
4. [Testing the System](#testing-the-system)
5. [API Usage](#api-usage)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | Required |
| pip | Latest | For package installation |
| Git | Any | For version control |

### Install Python Dependencies

```bash
cd backend
uv venv
uv pip install -r requirements.txt
```

Required packages:
- FastAPI, Uvicorn
- sentence-transformers, faiss-cpu
- pandas, numpy, scikit-learn
- pypdf, reportlab
- google-genai, openai

---

## Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd kortex
```

### Step 2: Generate Data

```bash
# Option A: Run the generation script
python scripts/generate_data.py

# This creates:
# - 26 SOP PDFs in data/synthetic/sops/
# - 250 IT tickets in data/synthetic/tickets.csv
```

### Step 3: Run Ingestion

```bash
# Option B: Use the API directly (after starting server)
# See "Running the Application" below
```

### Step 4: Configure LLM Provider

Edit `.env` file:

```bash
# Choose your provider: gemini, openai, ollama, groq
KORTEX_LLM_PROVIDER=gemini

# Add your API key
GEMINI_API_KEY=your_key_here

# Model selection
KORTEX_LLM_MODEL=gemini-2.0-flash
```

---

## Running the Application

### Start the Backend

```bash
# From project root
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000`

### Ingest Data

Once the server is running:

```bash
curl -X POST http://localhost:8000/ingest
```

Expected response:
```json
{
  "status": "ok",
  "summary": {
    "docs": {"documents_indexed": 26, "chunks_indexed": 43},
    "tickets": {"tickets_indexed": 250}
  }
}
```

### Start the Frontend (Optional)

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` for the UI.

---

## Testing the System

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status": "ok"}`

### Test 2: Query with cURL

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I fix Kafka consumer lag after a deployment?"
  }'
```

Expected response:
```json
{
  "answer": "To fix Kafka consumer lag...",
  "sources": [{"doc": "kafka_topic_management.pdf", "page": 3}],
  "confidence": 0.82,
  "status": "success",
  "agent_trace": ["Triage Agent -> docs", ...]
}
```

### Test 3: Query with Python

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "What is the password reset procedure?"}
)
print(response.json())
```

### Test 4: Run Unit Tests

```bash
pytest tests/test_agents.py -v
```

Expected: 14 tests passing

### Test 5: Evaluation Metrics

```bash
python -c "
import sys
sys.path.insert(0, '.')
from backend.services.evaluation import get_evaluation_service

eval = get_evaluation_service()

# Test Precision@K
docs = [{'content': 'doc1'}, {'content': 'doc2'}, {'content': 'doc3'}]
scores = [1.0, 0.0, 1.0]
print('Precision@K:', eval.precision_at_k(docs, scores, 3))

# Test Recall@K
print('Recall@K:', eval.recall_at_k(docs, scores, 3))

# Test MRR
print('MRR:', eval.mean_reciprocal_rank(docs, scores))

# Test Semantic Similarity
print('Similarity:', eval.semantic_similarity('VPN setup', 'VPN configuration'))
"
```

---

## API Usage

### Full Query Example

```python
import requests

def query_kortex(question):
    response = requests.post(
        "http://localhost:8000/query",
        json={
            "query": question,
            "user_id": "demo",
            "context_mode": "auto"
        }
    )
    return response.json()

# Test questions
questions = [
    "How do I fix Kafka consumer lag after a deployment?",
    "What is the password reset procedure?",
    "How do I configure VPN?",
    "Why would a Kubernetes pod enter CrashLoopBackOff?",
    "What past incidents mention SSO login issues?"
]

for q in questions:
    result = query_kortex(q)
    print(f"Q: {q}")
    print(f"Status: {result.get('status')}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")
    print(f"Answer: {result.get('answer', 'N/A')[:150]}...")
    print("-" * 50)
```

### Check Agent Trace

```python
result = query_kortex("How do I configure VPN?")
print("Agent Trace:")
for step in result.get('agent_trace', []):
    print(f"  - {step}")
```

---

## Sample Data Available

### Documents (26 SOPs)

- VPN Setup and Configuration
- Password Reset Procedure
- Email Configuration Guide
- Database Backup and Recovery
- Kubernetes Cluster Management
- Kafka Topic Management
- Incident Response Procedure
- Security Patch Management
- And more...

### Tickets (250 IT Support Tickets)

Categories: Network, Hardware, Software, Security, Email, Database, VPN, Authentication, Cloud, Application

---

## Troubleshooting

### Issue: "Module not found"

```bash
# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue: "FAISS index not found"

```bash
# Re-run ingestion
curl -X POST http://localhost:8000/ingest
```

### Issue: "LLM API quota exceeded"

- Switch provider in `.env`
- Or wait for quota to reset

### Issue: Port already in use

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it or use different port
uvicorn backend.main:app --port 8001
```

### Issue: Tests failing

```bash
# Run with verbose output
pytest tests/test_agents.py -v -s
```

---

## Architecture Overview

```
User Query
    ↓
Triage Agent (intent classification)
    ↓
Retrieval Agent + Ticket Agent (FAISS search)
    ↓
Reranker Agent (cross-encoder)
    ↓
Synthesis Agent (LLM generation)
    ↓
Validator Agent (confidence scoring)
    ↓
Response (+ sources, confidence, trace)
```

### Confidence Formula

```
confidence = 0.5 × retrieval_score + 0.3 × reranker_score + 0.2 × llm_self_eval
```

### Decision Thresholds

| Confidence | Action |
|------------|--------|
| > 0.75 | Respond with answer |
| 0.5-0.75 | Retry with expanded search |
| < 0.5 | Escalate to human |

---

## Next Steps

1. **Add more data**: Place PDFs in `docs/` or `data/synthetic/sops/`
2. **Switch LLM**: Try OpenAI or Ollama in `.env`
3. **Customize agents**: Modify agents in `backend/agents/`
4. **Add evaluation**: Use services in `backend/services/evaluation.py`

---

## Support

For issues or questions, check:
- `docs/architecture.md` - Full architecture
- `docs/agent-flow.md` - Agent pipeline details
- `docs/api.md` - API reference