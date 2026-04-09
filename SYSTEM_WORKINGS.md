# KORTEX SYSTEM WORKTHROUGH

## 1. Vision & Purpose
Kortex is an Agentic Knowledge Copilot designed to solve the problem of fragmented enterprise information. It leverages a multi-agent orchestration framework (built on **LangGraph**) to retrieve, reason over, and act on knowledge stored in documents (PDFs, Markdown, TXT) and historical support tickets.

## 2. Core Architecture: The "NOC" Framework
Kortex operates using a **Neural Orchestration Core (NOC)** which follows a **Plan-Execute-Validate** paradigm.

### Agent Breakdown:
- **Triage Agent**: The entry point. It analyzes the user query to determine if it requires technical documentation, historical ticket data, or both.
- **Retrieval Engine**: Performs semantic search using **FAISS** vector indices. It queries separate pools for corporate SOPs and support cases.
- **Reranker Agent**: Enhances precision. It uses a cross-encoder model to re-evaluate the relevance of retrieved chunks, ensuring only the highest quality context reaches the synthesizer.
- **Synthesis Agent**: The "writer". It combines the multi-source context into a structured, grounded response, ensuring all claims are backed by the provided data.
- **Validator Agent**: The "quality control". It computes a **Confidence Score** based on retrieval similarity, reranker scores, and LLM self-evaluation. It detects hallucinations and decides whether to respond, retry with broader context, or escalate.

## 3. Key Technical Components
- **Orchestration**: LangGraph (Stateful, non-linear workflows).
- **Data Layer**: FAISS (Vector DB) with root-relative indexing.
- **AI Models**: Sentence Transformers (Embeddings) & Cross-Encoders (Reranking).
- **Frontend**: Streamlit (Modern Light Theme, Terminal OS Aesthetic).
- **Compliance**: Built-in PII Redaction layer for sensitive data in tickets and documents.

## 4. UI/UX: KORTEX_OS
The interface is designed as a high-fidelity system dashboard:
- **TRIAGE.ENV**: Sidebar for task context and support status.
- **KNOWLEDGE_LEDGER**: Central reasoning area showing real-time agent "thinking" and final grounded answers.
- **ACTIONS**: Dedicated controls for Investigation (Analysis), Knowledge Upload, and Index Synchronization.

---
*Built by Neural Orchestration Core (NOC)*
