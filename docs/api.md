# Kortex API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response**:
```json
{
  "status": "ok"
}
```

### 2. Ingest Data

**POST** `/ingest`

Index documents and tickets into FAISS vector database.

**Response**:
```json
{
  "status": "ok",
  "summary": {
    "docs": {
      "documents_indexed": 26,
      "chunks_indexed": 43,
      "documents": [
        "vpn_setup_and_configuration.pdf",
        "password_reset_procedure.pdf",
        ...
      ]
    },
    "tickets": {
      "tickets_indexed": 250
    }
  }
}
```

### 3. Query

**POST** `/query`

Run the full multi-agent RAG pipeline.

**Request Body**:
```json
{
  "query": "How do I fix Kafka consumer lag after a deployment?",
  "user_id": "demo",
  "context_mode": "auto"
}
```

**Response** (Success):
```json
{
  "answer": "To fix Kafka consumer lag after deployment:\n\n1. **Check consumer group status**...\n\nBased on the retrieved context from Kafka Topic Management (page 3).",
  "sources": [
    {"doc": "kafka_topic_management.pdf", "page": 3},
    {"doc": "code_deployment_pipeline.pdf", "page": 2}
  ],
  "confidence": 0.82,
  "agent_trace": [
    "Triage Agent -> both",
    "Retrieval Agent -> Found 5 document chunks",
    "Ticket Agent -> Found 3 matching tickets",
    "Reranker Agent -> Selected top 3 context items",
    "Synthesis Agent -> Generated grounded answer",
    "Validator Agent -> Confidence 0.82 (respond)"
  ],
  "status": "success"
}
```

**Response** (Escalated):
```json
{
  "status": "escalated",
  "reason": "Confidence 0.29 below threshold",
  "suggestion": "Forward to human engineer",
  "confidence": 0.29,
  "agent_trace": [
    "Triage Agent -> both",
    "Retrieval Agent -> Found 5 document chunks",
    "Ticket Agent -> Found 3 matching tickets",
    "Reranker Agent -> Selected top 3 context items",
    "Synthesis Agent -> Generated grounded answer",
    "Validator Agent -> Confidence 0.29 (escalate)"
  ]
}
```

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The user question |
| `user_id` | string | No | User identifier (default: "demo") |
| `context_mode` | string | No | Search mode: "auto", "docs", "tickets", "both" (default: "auto") |

## Confidence Scoring

The system computes confidence using:

```
confidence = (0.5 × retrieval_score) + (0.3 × reranker_score) + (0.2 × llm_self_eval)
```

### Decision Thresholds

| Confidence | Status | Action |
|------------|--------|--------|
| > 0.75 | `success` | Return answer with sources |
| 0.5 - 0.75 | `retry` | Expand search and retry once |
| < 0.5 | `escalated` | Return escalation message |

## Agent Trace

The `agent_trace` array shows each step of the pipeline:

1. **Triage Agent** → Intent classification
2. **Retrieval Agent** → Document search results
3. **Ticket Agent** → Ticket search results
4. **Reranker Agent** → Re-ranking results
5. **Synthesis Agent** → LLM generation
6. **Validator Agent** → Confidence score

## Example Usage

### cURL

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I configure VPN?",
    "user_id": "demo"
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "How do I configure VPN?",
        "user_id": "demo"
    }
)
print(response.json())
```

### JavaScript

```javascript
const response = await fetch("http://localhost:8000/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "How do I configure VPN?",
    user_id: "demo"
  })
});
const data = await response.json();
console.log(data);
```

## OpenAPI Schema

The API uses OpenAPI 3.0. Run the server and visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`