from __future__ import annotations

from typing import Any

from backend.agents.reranker_agent import RerankerAgent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.synthesis_agent import SynthesisAgent
from backend.agents.ticket_agent import TicketAgent
from backend.agents.triage_agent import classify_intent
from backend.agents.validator_agent import ValidatorAgent
from backend.services.xai_explainer import XAIExplainer


class Orchestrator:
    def __init__(self) -> None:
        self.retrieval_agent = RetrievalAgent()
        self.ticket_agent = TicketAgent()
        self.reranker_agent = RerankerAgent()
        self.synthesis_agent = SynthesisAgent()
        self.validator_agent = ValidatorAgent()
        self.xai = XAIExplainer()

    def _collect_sources(self, contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str]] = set()
        sources: list[dict[str, Any]] = []
        for item in contexts:
            # Handle both formats: doc (with page) and ticket (with ticket_id)
            if item.get("source_type") == "doc":
                # SOP format uses 'file', other format uses 'doc'
                doc_name = item.get("file", item.get("doc", "unknown"))
                page = item.get("page", 1)
                key = ("doc", f"{doc_name}:{page}")
                if key not in seen:
                    sources.append({"doc": doc_name, "page": page})
                    seen.add(key)
            elif item.get("source_type") == "ticket":
                ticket_id = item.get("ticket_id", "unknown")
                key = ("ticket", ticket_id)
                if key not in seen:
                    sources.append({"ticket": ticket_id})
                    seen.add(key)
        return sources

    def run(self, query: str, context_mode: str = "auto") -> dict[str, Any]:
        trace: list[str] = []
        xai_explanations: list[dict[str, Any]] = []

        # Step 1: Triage
        intent = classify_intent(query) if context_mode == "auto" else context_mode
        trace.append(f"Triage Agent -> {intent}")

        # XAI for Triage
        triage_xai = self.xai.explain_triage(intent, query)
        xai_explanations.append(triage_xai)

        # Store results for XAI
        retrieval_result = None
        rerank_result = None
        synthesis_result = None
        validator_result = None
        had_fallback = False

        retry_count = 0
        while retry_count <= 1:
            doc_k = 5 if retry_count == 0 else 8
            ticket_k = 3 if retry_count == 0 else 5

            docs = (
                self.retrieval_agent.search(query, top_k=doc_k)
                if intent in {"docs", "both"}
                else []
            )
            tickets = (
                self.ticket_agent.search(query, top_k=ticket_k)
                if intent in {"tickets", "both"}
                else []
            )

            if docs:
                trace.append(f"Retrieval Agent -> Found {len(docs)} document chunks")
            if tickets:
                trace.append(f"Ticket Agent -> Found {len(tickets)} matching tickets")

            # XAI for Retrieval
            top_score = max([d.get("retrieval_score", 0) for d in docs], default=0)
            retrieval_xai = self.xai.explain_retrieval(
                len(docs), len(tickets), top_score
            )
            if retry_count == 0:
                xai_explanations.append(retrieval_xai)
                retrieval_result = retrieval_xai

            combined = docs + tickets
            if not combined:
                return {
                    "status": "escalated",
                    "reason": "No context chunks retrieved",
                    "suggestion": "Forward to human engineer",
                    "agent_trace": trace
                    + ["Guardrail -> Escalated due to empty context"],
                    "xai_explanation": xai_explanations,
                }

            ranked = self.reranker_agent.rerank(query, combined, top_k=3)
            trace.append(f"Reranker Agent -> Selected top {len(ranked)} context items")

            # XAI for Rerank
            reranker_scores = [r.get("reranker_score", 0) for r in ranked]
            rerank_xai = self.xai.explain_rerank(
                len(combined), len(ranked), reranker_scores
            )
            if retry_count == 0:
                xai_explanations.append(rerank_xai)
                rerank_result = rerank_xai

            answer, fallback_used = self.synthesis_agent.generate(query, ranked)
            had_fallback = had_fallback or fallback_used
            trace.append("Synthesis Agent -> Generated grounded answer")

            # XAI for Synthesis
            synthesis_xai = self.xai.explain_synthesis(
                len(answer), len(ranked), fallback_used
            )
            if retry_count == 0:
                xai_explanations.append(synthesis_xai)
                synthesis_result = synthesis_xai

            validation = self.validator_agent.validate(answer, ranked)
            trace.append(
                f"Validator Agent -> Confidence {validation['confidence']:.2f} ({validation['decision']})"
            )

            # XAI for Validator
            validator_xai = self.xai.explain_validator(
                validation["confidence"],
                validation["decision"],
                validation.get("retrieval_similarity", 0),
                validation.get("reranker_score", 0),
                validation.get("llm_self_eval", 0),
            )
            if retry_count == 0:
                xai_explanations.append(validator_xai)
                validator_result = validator_xai

            if validation["decision"] == "respond":
                return {
                    "answer": answer,
                    "sources": self._collect_sources(ranked),
                    "contexts": ranked,
                    "confidence": validation["confidence"],
                    "agent_trace": trace,
                    "status": "success",
                    "xai_explanation": xai_explanations,
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
                "xai_explanation": xai_explanations,
            }

        return {
            "status": "escalated",
            "reason": "Retry limit reached",
            "suggestion": "Forward to human engineer",
            "agent_trace": trace,
            "xai_explanation": xai_explanations,
        }
