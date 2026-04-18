from __future__ import annotations

import json
import logging
from collections import deque
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.core.orchestrator import Orchestrator
from backend.data.ingest import run_ingestion

# Global log buffer for frontend visibility
log_buffer = deque(maxlen=100)

class BufferHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            log_buffer.append(msg)
        except Exception:
            self.handleError(record)

# Filter out polling noise from terminal
class LogFilter(logging.Filter):
    def filter(self, record):
        # Suppress Uvicorn access logs for polling endpoints
        msg = record.getMessage()
        if "GET /api/logs" in msg or "GET /health" in msg:
            return False
        return True

# Configure logging
logging.basicConfig(level=logging.INFO)
root_logger = logging.getLogger()

# Clear existing handlers to avoid duplicates if reloaded
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# 1. Terminal Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
console_handler.addFilter(LogFilter()) # Apply filter
root_logger.addHandler(console_handler)

# Also apply filter to uvicorn access logger
logging.getLogger("uvicorn.access").addFilter(LogFilter())

# 2. Frontend Buffer Handler
buffer_handler = BufferHandler()
buffer_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
root_logger.addHandler(buffer_handler)

logger = logging.getLogger("kortex")
logger.setLevel(logging.INFO)
# Ensure kortex logs don't double-print if root also has a handler
logger.propagate = True 

app = FastAPI(
    title="Kortex API",
    version="0.1.0",
    description="Agentic Enterprise Knowledge Copilot - Multi-agent RAG system with XAI",
)

# Documentation files
DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3)
    user_id: str = "demo"
    context_mode: str = "auto"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/source")
def get_source(file: str, page: int = 1):
    """Serve a PDF source file at a specific page."""
    BASE_DIR = Path(__file__).resolve().parents[1]
    SOP_DIR = BASE_DIR / "data" / "synthetic" / "sops"

    pdf_path = SOP_DIR / file
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        pdf_path, media_type="application/pdf", headers={"Accept-Ranges": "bytes"}
    )


@app.get("/docs")
def get_docs():
    """Serve API documentation page."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kortex API Documentation</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Space Mono', monospace;
            background: #0a0a0f;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 2rem;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { 
            color: #00ff41; 
            font-size: 2rem; 
            margin-bottom: 1rem;
            text-shadow: 0 0 20px rgba(0,255,65,0.5);
        }
        h2 { color: #00d4ff; margin: 2rem 0 1rem; border-bottom: 1px solid #1e1e2e; padding-bottom: 0.5rem; }
        h3 { color: #ff6b00; margin: 1.5rem 0 0.5rem; }
        code { 
            background: #12121a; 
            color: #00ff41; 
            padding: 0.2rem 0.5rem; 
            border-radius: 4px;
            border: 1px solid #00ff41;
        }
        pre { 
            background: #12121a; 
            padding: 1rem; 
            border-radius: 8px; 
            border: 1px solid #1e1e2e;
            overflow-x: auto;
            margin: 1rem 0;
        }
        .endpoint {
            background: #12121a;
            border: 1px solid #1e1e2e;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .method {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-weight: bold;
            margin-right: 0.5rem;
        }
        .get { background: #00ff41; color: #000; }
        .post { background: #00d4ff; color: #000; }
        .param { color: #ff6b00; }
        .desc { color: #888; margin-top: 0.5rem; }
        a { color: #00d4ff; }
        .logo { 
            font-size: 3rem; 
            text-align: center; 
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">⚡ KORTEX ⚡</div>
        <h1>Kortex API Documentation</h1>
        <p>Agentic Enterprise Knowledge Copilot - Multi-agent RAG system with Explainable AI (XAI)</p>
        
        <h2>📡 Endpoints</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/health</code>
            <p class="desc">Health check - returns API status</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/ingest</code>
            <p class="desc">Ingest documents and tickets into FAISS vector database</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/query</code>
            <p class="desc">Run the full multi-agent RAG pipeline</p>
        </div>
        
        <h2>📝 API Reference</h2>
        
        <h3>POST /query</h3>
        <pre><code>{
  "query": "How do I configure VPN?",
  "user_id": "demo",
  "context_mode": "auto"
}</code></pre>
        
        <h3>Response</h3>
        <pre><code>{
  "answer": "To configure VPN...",
  "sources": [{"doc": "vpn_setup.pdf", "page": 1}],
  "confidence": 0.75,
  "status": "success",
  "agent_trace": ["Triage Agent -> docs", ...],
  "xai_explanation": [{ "decision": "both", "reason": "...", "confidence": "high" }, ...]
}</code></pre>
        
        <h2>🔧 Confidence Scoring</h2>
        <p>Formula: <code>confidence = (0.4 * retrieval) + (0.35 * reranker) + (0.25 * llm_self_eval)</code></p>
        
        <h3>Decision Thresholds</h3>
        <ul>
            <li><code>>= 0.5</code> - Respond with answer</li>
            <li><code>>= 0.35</code> - Retry with expanded search</li>
            <li><code>< 0.35</code> - Escalate to human</li>
        </ul>
        
        <h2>🤖 Agent Pipeline</h2>
        <ol>
            <li><strong>Triage Agent</strong> - Classifies query intent</li>
            <li><strong>Retrieval Agent</strong> - Searches document FAISS index</li>
            <li><strong>Ticket Agent</strong> - Searches historical tickets</li>
            <li><strong>Reranker Agent</strong> - Re-ranks with cross-encoder</li>
            <li><strong>Synthesis Agent</strong> - Generates LLM response</li>
            <li><strong>Validator Agent</strong> - Computes confidence</li>
        </ol>
        
        <h2>💻 Example Usage</h2>
        
        <h3>cURL</h3>
        <pre><code>curl -X POST http://localhost:8000/query \\
  -H "Content-Type: application/json" \\
  -d '{"query": "How do I configure VPN?"}'</code></pre>
        
        <h3>Python</h3>
        <pre><code>import requests
response = requests.post(
    "http://localhost:8000/query",
    json={"query": "How do I configure VPN?"}
)
print(response.json())</code></pre>
        
        <h2>⚙️ Configuration</h2>
        <p>Set in <code>.env</code> file:</p>
        <pre><code>KORTEX_LLM_PROVIDER=ollama  # Options: gemini, openai, ollama, groq
KORTEX_LLM_MODEL=llama3.2:3b
OLLAMA_HOST=http://localhost:11434</code></pre>
        
        <p style="margin-top: 2rem; color: #666; text-align: center;">
            Kortex v1.0 | <a href="https://github.com/ooha-chekuri/Kortex">GitHub</a>
        </p>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.post("/ingest")
def ingest() -> dict:
    try:
        summary = run_ingestion()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    global orchestrator
    orchestrator = Orchestrator()
    return {"status": "ok", "summary": summary}


@app.get("/api/logs")
def get_logs():
    """Retrieve recent system logs."""
    return list(log_buffer)


@app.post("/query")
def query(request: QueryRequest) -> dict:
    try:
        logger.info(f"Processing query: {request.query}")
        result = orchestrator.run(request.query, request.context_mode)
        logger.info(f"Query processed successfully. Status: {result.get('status')}")
        return result
    except Exception as exc:
        logger.error(f"Error processing query: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Kortex Internal Error: {str(exc)}")


# Serve static files from the React build
# This should be mounted last so it doesn't override API routes
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
