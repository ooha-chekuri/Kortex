from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.core.orchestrator import Orchestrator
from src.data.ingest import run_ingestion


app = FastAPI(title="Kortex API", version="0.1.0")
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


@app.post("/ingest")
def ingest() -> dict:
    try:
        summary = run_ingestion()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    global orchestrator
    orchestrator = Orchestrator()
    return {"status": "ok", "summary": summary}


@app.post("/query")
def query(request: QueryRequest) -> dict:
    try:
        return orchestrator.run(request.query, request.context_mode)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc
