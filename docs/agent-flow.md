# Kortex Agent Flow

## Overview

This document describes the agent orchestration flow in Kortex, explaining how each agent contributes to producing a grounded, confident answer.

## Agent Pipeline

```
┌─────────┐   ┌──────────┐   ┌────────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐
│ Triage  │ → │Retrieve │ → │ Rerank   │ → │Synthesize│ → │Validate │ → │ Response│
│ Agent   │   │Agent(s) │   │ Agent    │   │ Agent  │   │ Agent   │   │
└─────────┘   └──────────┘   └────────────┘   └─────────┘   └──────────┘   └──────────┘
    │            │              │               │           │              │
  Intent    Context Items  Ranked Items   Grounded      Decision    Answer +
  Decision                         Response    Score       Sources
```

## Step-by-Step Flow

### Step 1: Triage Agent

**Purpose**: Determine what to search

**Process**:
1. Analyze user query for keywords
2. Classify intent as one of:
   - `docs`: User wants documentation
   - `tickets`: User wants historical issues
   - `both`: User wants both

**Example**:
- Query: "How do I fix Kafka lag?"
  - Detects: "kafka", "fix" → Intent: `docs`
- Query: "What past incidents mention auth errors?"
  - Detects: "incidents", "errors" → Intent: `tickets`

### Step 2: Retrieval Agent + Ticket Agent

**Purpose**: Fetch relevant context

**Process**:
1. Generate query embedding using sentence-transformers
2. Search FAISS index for top-K similar chunks
3. Return results with cosine similarity scores

**Parameters**:
- Initial search: 5 docs + 3 tickets
- Retry search: 8 docs + 5 tickets

**Output**:
```python
[
    {"doc": "kafka_topic_management.pdf", "page": 3, "content": "...", "retrieval_score": 0.85},
    {"ticket_id": "TICKET-00123", "description": "...", "retrieval_score": 0.72},
    ...
]
```

### Step 3: Reranker Agent

**Purpose**: Re-order results by relevance

**Process**:
1. Use cross-encoder to score (query, document) pairs
2. Normalize scores to 0-1 range
3. Sort by reranker score (descending)

**Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Output**: Top 3 re-ranked items with scores

### Step 4: Synthesis Agent

**Purpose**: Generate answer with LLM

**Process**:
1. Build prompt with context items
2. Call LLM (Gemini/OpenAI/Ollama)
3. Include citations

**Prompt Template**:
```
Answer only based on the provided context. Do not hallucinate.
Answer concisely, cite sources by name, and say "I don't know" if the context is insufficient.

User question: {query}

Context:
{context_items}

Return a concise answer in markdown. Include citations inline using the source names.
```

### Step 5: Validator Agent

**Purpose**: Compute confidence score

**Formula**:
```
confidence = (0.5 × retrieval_score) + (0.3 × reranker_score) + (0.2 × llm_self_eval)
```

Where:
- `retrieval_score`: Average retrieval similarity
- `reranker_score`: Average reranker score
- `llm_self_eval`: LLM's self-assessment (0-1)

### Step 6: Decision

**Thresholds**:
| Confidence | Decision | Action |
|------------|----------|--------|
| > 0.75 | `respond` | Return answer |
| 0.5-0.75 | `retry` | Expand search, retry once |
| < 0.5 | `escalate` | Return escalation message |

## Retry Logic

The orchestrator implements a retry loop:

```
1. Run pipeline with initial K (5 docs, 3 tickets)
2. If confidence < 0.5 and retry_count < 1:
   - Expand to (8 docs, 5 tickets)
   - Retry synthesis
3. If still low confidence:
   - Escalate to human
```

## Agent Trace

Each query produces an `agent_trace` for debugging:

```python
[
    "Triage Agent -> both",
    "Retrieval Agent -> Found 5 document chunks",
    "Ticket Agent -> Found 3 matching tickets",
    "Reranker Agent -> Selected top 3 context items",
    "Synthesis Agent -> Generated grounded answer",
    "Validator Agent -> Confidence 0.82 (respond)"
]
```

## Example: Full Flow

### Query
"How do I fix Kafka consumer lag after a deployment?"

### Flow
1. **Triage**: Keywords "kafka", "fix" → Intent: `docs`
2. **Retrieval**: Found "Kafka Topic Management", "Code Deployment Pipeline" chunks
3. **Rerank**: Re-ranked with cross-encoder
4. **Synthesis**: "To fix Kafka consumer lag after deployment..."
5. **Validation**: Confidence 0.82 → Decision: `respond`

### Response
```json
{
  "answer": "To fix Kafka consumer lag after deployment:\n\n1. **Check consumer group status**...",
  "sources": [{"doc": "kafka_topic_management.pdf", "page": 3}],
  "confidence": 0.82,
  "status": "success"
}
```

## Error Handling

| Error | Handling |
|-------|----------|
| No context retrieved | Escalate immediately |
| LLM generation fails | Return error message with retry option |
| Empty answer | Retry with expanded search |
| Confidence < 0.5 | Escalate to human |

## Guardrails

1. **No Hallucination**: Only answer based on retrieved context
2. **I Don't Know**: Say this if context is insufficient
3. **Source Citation**: Always cite sources
4. **Confidence Filtering**: Escalate low-confidence answers