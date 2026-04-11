# Kortex - Enterprise Knowledge Copilot

## Platform Documentation

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     KORTEX PLATFORM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│   │  Frontend │◄──►│  FastAPI │◄──►│  FAISS   │               │
│   │ Streamlit │    │   API    │    │   DB     │               │
│   └──────────┘    └──────────┘    └──────────┘               │
│                                       │                       │
│                              ┌────────┴────────┐             │
│                              │                 │             │
│                          ┌───▼────┐    ┌────▼────┐         │
│                          │ Docs   │    │ Tickets │         │
│                          └────────┘    └─────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Agent Orchestration Flow

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                  TRIAGE AGENT                            │
│  • Classifies intent (docs/tickets/both)              │
│  • Determines search strategy                       │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│               RETRIEVAL AGENTS                          │
│                                                         │
│  ┌─────────────────┐    ┌─────────────────┐       │
│  │ Doc Retrieval    │    │ Ticket Retrieval │       │
│  │ (FAISS + Docs)  │    │ (FAISS + CSV)    │       │
│  └─────────────────┘    └─────────────────┘       │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                RERANKER AGENT                          │
│  • Cross-encoder reranking                            │
│  • Precision enhancement                            │
│  • Top-K selection                                  │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│               SYNTHESIS AGENT                           │
│  • LLM-based answer generation                       │
│  • Source citation                                  │
│  • Self-confidence evaluation                     │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│               VALIDATOR AGENT                           │
│  • Confidence scoring                              │
│  • Hallucination detection                        │
│  • Decision (respond/retry/escalate)              │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                    RESPONSE                            │
│  • Answer with sources                              │
│  • Confidence score                            │
│  • Agent trace                                │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Confidence Scoring (PRD Formula)

```
Confidence = (0.5 × Retrieval Similarity) 
            + (0.3 × Reranker Score) 
            + (0.2 × LLM Self-Evaluation)
```

### Decision Matrix

| Confidence | Action | Description |
|------------|--------|-------------|
| > 0.75 | **ANSWER** | Return response with sources |
| 0.5-0.75 | **RETRY** | Expand search, retry |
| < 0.5 | **ESCALATE** | Human-in-the-loop |

---

## 🎯 Demo Scenarios

### Scenario 1: High Confidence Answer
- **Query**: "How do I reset my password?"
- **Expected**: Confidence > 0.75, ANSWER response
- **Shows**: Answer + Sources + Trace

### Scenario 2: Multi-Source Query
- **Query**: "Kafka deployment best practices?"
- **Expected**: Reranked results from docs
- **Shows**: Combined context

### Scenario 3: Escalation (Low Confidence)
- **Query**: "Quantum computing principles?"
- **Expected**: Confidence < 0.5, ESCALATE
- **Shows**: "Forward to human engineer"

---

## 📁 Demo Data Structure

```
demo/
└── inputs/
    ├── docs/           # 30 SOP documents
    │   ├── Network_Security_SOP.txt
    │   ├── VPN_Access_Policy.txt
    │   ├── Password_Policy.txt
    │   ├── Kubernetes_Onboarding.txt
    │   ├── Kafka_Deployment_Guide.txt
    │   └── ... (25 more)
    │
    └── tickets/        # 300 IT support tickets
        └── tickets.csv
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| AI/ML | Gemini 2.5 Flash, Sentence Transformers |
| Vector DB | FAISS |
| Orchestration | Custom Python State Machine |

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
uv pip install -r requirements.txt

# 2. Build knowledge base
python -c "from src.data.ingest import build_indices; print(build_indices())"

# 3. Run Streamlit
uv run streamlit run app.py

# 4. Open browser
# http://localhost:8501
```

---

## 📋 Sample Queries for Demo

1. **How do I reset my password?**
2. **What is the VPN access policy?**
3. **How to deploy Kafka?**
4. **What is incident response procedure?**
5. **Tell me about Kubernetes onboarding**
6. **What are the Docker standards?**
7. **How do I request software installation?**
8. **What's the remote work policy?**

---

## 🏆 Judging Criteria Alignment

| Criteria | Kortex Feature |
|----------|--------------|
| Technical Soundness | Multi-agent orchestration, confidence formula |
| Functional Value | Source citation, escalation loop |
| Problem Understanding | Enterprise RAG with tickets |
| Innovation | Agent trace visibility |
| Robustness | PII redaction, fallback mode |

---

## 📞 Escalation Flow

```
Low Confidence (< 0.5)
       │
       ▼
┌─────────────────────────┐
│    ESCALATION          │
│  • Not confident      │
│  • Forward to human   │
│  • Document reason    │
└─────────────────────────┘
```