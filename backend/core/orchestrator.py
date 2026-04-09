from __future__ import annotations

from typing import Any

from backend.agents.reranker_agent import RerankerAgent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.synthesis_agent import SynthesisAgent
from backend.agents.ticket_agent import TicketAgent
from backend.agents.triage_agent import classify_intent
from backend.agents.validator_agent import ValidatorAgent


class Orchestrator:
    def __init__(self) -> None:
        self.retrieval_agent = RetrievalAgent()
        self.ticket_agent = TicketAgent()
        self.reranker_agent = RerankerAgent()
        self.synthesis_agent = SynthesisAgent()
        self.validator_agent = ValidatorAgent()

    def _collect_sources(self, contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str]] = set()
        sources: list[dict[str, Any]] = []
        for item in contexts:
            if item["source_type"] == "doc":
                key = ("doc", f'{item["doc"]}:{item["page"]}')
                if key not in seen:
                    sources.append({"doc": item["doc"], "page": item["page"]})
                    seen.add(key)
            else:
                key = ("ticket", item["ticket_id"])
                if key not in seen:
                    sources.append({"ticket": item["ticket_id"]})
                    seen.add(key)
        return sources

    def run(self, query: str, context_mode: str = "auto") -> dict[str, Any]:
        trace: list[str] = []
        intent = classify_intent(query) if context_mode == "auto" else context_mode
        trace.append(f"Triage Agent -> {intent}")

        retry_count = 0
        while retry_count <= 1:
            doc_k = 5 if retry_count == 0 else 8
            ticket_k = 3 if retry_count == 0 else 5

            docs = self.retrieval_agent.search(query, top_k=doc_k) if intent in {"docs", "both"} else []
            tickets = (
                self.ticket_agent.search(query, top_k=ticket_k) if intent in {"tickets", "both"} else []
            )

            if docs:
                trace.append(f"Retrieval Agent -> Found {len(docs)} document chunks")
            if tickets:
                trace.append(f"Ticket Agent -> Found {len(tickets)} matching tickets")

            combined = docs + tickets
            if not combined:
                return {
                    "status": "escalated",
                    "reason": "No context chunks retrieved",
                    "suggestion": "Forward to human engineer",
                    "agent_trace": trace + ["Guardrail -> Escalated due to empty context"],
                }

            ranked = self.reranker_agent.rerank(query, combined, top_k=3)
            trace.append(f"Reranker Agent -> Selected top {len(ranked)} context items")

            answer = self.synthesis_agent.generate(query, ranked)
            trace.append("Synthesis Agent -> Generated grounded answer")

            validation = self.validator_agent.validate(answer, ranked)
            trace.append(
                f"Validator Agent -> Confidence {validation['confidence']:.2f} ({validation['decision']})"
            )

            if validation["decision"] == "respond":
                return {
                    "answer": answer,
                    "sources": self._collect_sources(ranked),
                    "confidence": validation["confidence"],
                    "agent_trace": trace,
                    "status": "success",
                }

            if validation["decision"] == "retry" and retry_count == 0:
                trace.append("Orchestrator -> Retrying once with expanded retrieval")
                retry_count += 1
                continue

            return {
                "status": "escalated",
                "reason": f"Confidence {validation['confidence']:.2f} below threshold",
                "suggestion": "Forward to human engineer",
                "confidence": validation["confidence"],
                "agent_trace": trace,
            }

        return {
            "status": "escalated",
            "reason": "Retry limit reached",
            "suggestion": "Forward to human engineer",
            "agent_trace": trace,
        }
