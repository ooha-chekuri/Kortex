from __future__ import annotations

from typing import Any, List, Dict

from backend.agents.reranker_agent import RerankerAgent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.synthesis_agent import SynthesisAgent
# Removed TicketAgent import, assumed handled by RetrievalAgent if it handles tickets
# Wait, looking back at the code, TicketAgent exists.
from backend.agents.ticket_agent import TicketAgent
from backend.agents.validator_agent import ValidatorAgent
from backend.agents.planning_agent import PlanningAgent
from backend.agents.summarizer_agent import SummarizerAgent
from backend.services.xai_explainer import XAIExplainer


class Orchestrator:
    def __init__(self) -> None:
        self.retrieval_agent = RetrievalAgent()
        self.ticket_agent = TicketAgent()
        self.reranker_agent = RerankerAgent()
        self.synthesis_agent = SynthesisAgent()
        self.validator_agent = ValidatorAgent()
        self.planning_agent = PlanningAgent()
        self.summarizer_agent = SummarizerAgent()
        self.xai = XAIExplainer()

    def _collect_sources(self, contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str]] = set()
        sources: list[dict[str, Any]] = []
        for item in contexts:
            # Handle both formats: doc (with page) and ticket (with ticket_id)
            if item.get("source_type") == "doc":
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
        history: List[str] = []
        contexts: List[Dict[str, Any]] = []
        last_answer = None
        
        max_steps = 5
        for step in range(max_steps):
            plan = self.planning_agent.plan_next_step(query, history)
            trace.append(f"Planning Agent -> Step {step+1}: {plan['thought']}")
            
            if plan.get("final_answer"):
                return {
                    "answer": plan["final_answer"],
                    "sources": self._collect_sources(contexts),
                    "contexts": contexts,
                    "agent_trace": trace,
                    "status": "success"
                }
                
            action = plan.get("action")
            action_input = plan.get("action_input")
            
            if action == "doc_search":
                results = self.retrieval_agent.search(action_input or query)
                contexts.extend(results)
                history.append(f"Observation: doc_search found {len(results)} items.")
                trace.append(f"Retrieval Agent -> Found {len(results)} document chunks")
            elif action == "ticket_search":
                results = self.ticket_agent.search(action_input or query)
                contexts.extend(results)
                history.append(f"Observation: ticket_search found {len(results)} items.")
                trace.append(f"Ticket Agent -> Found {len(results)} matching tickets")
            elif action == "synthesize":
                if not contexts:
                    history.append("Observation: No contexts available to synthesize.")
                    continue
                # Rerank first
                ranked = self.reranker_agent.rerank(query, contexts, top_k=3)
                answer, fallback = self.synthesis_agent.generate(query, ranked)
                last_answer = answer
                history.append(f"Observation: Synthesis generated an answer. Length: {len(answer)}")
                trace.append("Synthesis Agent -> Generated grounded answer")
            elif action == "validate":
                if not last_answer:
                    history.append("Observation: No answer to validate.")
                    continue
                # Rerank again or use already ranked items? Let's use top 3 for validation
                ranked = self.reranker_agent.rerank(query, contexts, top_k=3)
                validation = self.validator_agent.validate(last_answer, ranked)
                trace.append(f"Validator Agent -> Confidence {validation['confidence']:.2f} ({validation['decision']})")
                
                if validation["decision"] == "respond":
                    return {
                        "answer": last_answer,
                        "sources": self._collect_sources(ranked),
                        "contexts": ranked,
                        "confidence": validation["confidence"],
                        "agent_trace": trace,
                        "status": "success"
                    }
                else:
                    history.append(f"Observation: Validation failed with score {validation['confidence']}. Decision: {validation['decision']}")
            elif action == "summarize":
                if not contexts:
                    history.append("Observation: No contexts available to summarize.")
                    continue
                summary = self.summarizer_agent.summarize(contexts)
                last_answer = summary
                history.append(f"Observation: Summarizer generated a summary. Length: {len(summary)}")
                trace.append("Summarizer Agent -> Generated executive summary")
            elif action == "check_duplicates":
                results = self.ticket_agent.search(action_input or query, top_k=1)
                if results and results[0].get("retrieval_score", 0) > 0.85:
                    duplicate = results[0]
                    history.append(f"Observation: Found potential duplicate ticket {duplicate['ticket_id']} with score {duplicate['retrieval_score']:.2f}")
                    trace.append(f"Ticket Agent -> Flagged potential duplicate: {duplicate['ticket_id']}")
                    # If it's a very strong match, we can even provide the resolution directly
                    if duplicate.get("resolution"):
                        last_answer = f"This issue appears to be a duplicate of ticket **{duplicate['ticket_id']}**. \n\n**Previous Resolution:** {duplicate['resolution']}"
                else:
                    history.append("Observation: No high-confidence duplicate tickets found.")
                    trace.append("Ticket Agent -> No duplicate issues detected")
            else:
                break
                
        return {
            "status": "escalated",
            "reason": "Max planning steps reached without confidence",
            "suggestion": "Forward to human engineer",
            "agent_trace": trace,
        }
