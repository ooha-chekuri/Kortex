# ⚡ KORTEX: User Walkthrough ⚡

Welcome to Kortex, your **Agentic Knowledge Copilot**. This guide will help you get started with the platform, from data ingestion to running queries and understanding the agent's reasoning.

---

## 🚀 1. Setup & Ingestion

Before you can query the system, you need to ingest the enterprise documents (SOPs) and historical tickets.

### **Step 1: Configure your LLM**
Ensure your `.env` file in the root directory points to your preferred provider (Ollama, OpenAI, Gemini, or Groq).
```bash
KORTEX_LLM_PROVIDER=ollama
KORTEX_LLM_MODEL=llama3.2:3b
OLLAMA_HOST=http://localhost:11434
```

### **Step 2: Run Ingestion**
This will clean, chunk, and embed your documents (`/data/synthetic/sops`) and tickets (`/backend/data/sample_tickets.csv`).
```bash
python -m backend.data.ingest
```
*Tip: Subsequent runs will automatically skip unchanged files using MD5 hashes.*

---

## 🔍 2. Running Your First Query

Start the backend and frontend, then visit `http://localhost:5173` (or the port Vite provides).

### **Types of Queries You Can Ask:**
1.  **SOP Search:** "How do I configure Kafka consumer lag monitoring?"
2.  **Incident Lookup:** "What past incidents mention SSO login loops?"
3.  **Complex Reasoning:** "How do I fix the VPN error from yesterday?" (The agent will check both docs and tickets).
4.  **Summarization:** "Summarize the data retention policy for user logs."

---

## 🤖 3. Understanding the Agent

Kortex uses a **ReAct (Reason + Act) loop**. You can watch this in real-time in the **Agent Activity Panel**:

1.  **Planning:** The agent thinks about what it needs to solve your query.
2.  **Actions:** It calls tools like `doc_search`, `ticket_search`, or `summarize`.
3.  **Observation:** It reads the results and decides if it has enough information.
4.  **Validation:** It performs a **Faithfulness Check** to ensure it isn't hallucinating.
5.  **Final Answer:** You receive a grounded response with citations.

---

## 📊 4. Running Evaluations

To see how well the system is performing, run the automated evaluation suite:
```bash
python scripts/run_evaluation.py
```
This generates a detailed `evaluation_report.md` in your root directory with Precision, Recall, and MRR metrics.

---

## 🐳 5. Docker Deployment

For a production-ready setup, use Docker Compose:
```bash
docker-compose up --build
```
This will start both the FastAPI backend (port 8000) and the Nginx-hosted frontend (port 80).
