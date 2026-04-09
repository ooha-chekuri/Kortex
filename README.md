# Kortex – Agentic Knowledge Copilot

Kortex is an agentic enterprise knowledge copilot built for hackathon demos. It transforms fragmented organizational data (PDFs, Markdown, Tickets) into actionable intelligence using a multi-agent orchestration framework.

## 🚀 Quick Start (Streamlit Prototype)

This project has been restructured for a high-impact Streamlit prototype.

### Prerequisites
- [uv](https://github.com/astral-sh/uv) installed.

### Setup & Run
1. **Clone and Branch**: Ensure you are on the `csp/streamlit-prototype` branch.
2. **Environment Setup**:
   ```powershell
   uv venv
   uv pip install -r requirements.txt
   ```
3. **Ingest Data**:
   ```powershell
   $env:PYTHONPATH="."
   uv run python data/ingest.py
   ```
4. **Launch Kortex**:
   ```powershell
   uv run streamlit run app.py
   ```

## 🧠 Architecture

Kortex utilizes **LangGraph** for non-linear, stateful agent orchestration:
- **Triage Agent**: Classifies user intent (Docs, Tickets, or Both).
- **Retrieval Agent**: Performs semantic search across Vector DBs.
- **Ticket Agent**: Specialized retrieval for historical support tickets.
- **Reranker Agent**: Optimizes context relevance using Cross-Encoders.
- **Synthesis Agent**: Generates grounded responses with citations.
- **Validator Agent**: Audits responses for confidence and hallucinations.

## 🖥️ UI/UX Features
- **Departure Mono Aesthetic**: Retro-futuristic "terminal" style.
- **Agent Activity Panel**: Real-time visibility into the "AI Thinking" process.
- **Confidence Scoring**: Quantitative reliability metrics (87% etc.).
- **Escalation Loop**: Automatic detection of low-confidence scenarios for human intervention.
