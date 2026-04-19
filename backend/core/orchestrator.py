from __future__ import annotations

import logging
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

logger = logging.getLogger("kortex.orchestrator")


class Orchestrator:
    def __init__(self) -> None:
        logger.info("Initializing Kortex Orchestrator...")
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
        logger.info(f"Starting orchestration for: '{query}'")
        trace: list[str] = []
        xai_explanations: list[dict[str, Any]] = []
        history: List[str] = []
        contexts: List[Dict[str, Any]] = []
        last_answer = None

        max_steps = 5
        for step in range(max_steps):
            logger.info(f"Step {step + 1}: Planning next action")
            plan = self.planning_agent.plan_next_step(query, history)
            thought = plan.get("thought", "No thought provided")
            logger.info(f"Thought: {thought}")
            trace.append(f"Planning Agent -> Step {step + 1}: {thought}")

            # Structured XAI for Planning
            xai_explanations.append(
                {
                    "agent": "Planning Agent",
                    "reason": thought,
                    "decision": plan.get("action", "final_answer"),
                    "step": step + 1,
                }
            )

            # Only accept final_answer if it's a real answer (not placeholder) and we've retrieved contexts
            final_ans = plan.get("final_answer")
            # Block generic placeholders
            placeholder_patterns = [
                "not provided",
                "not available",
                "not included",
                "list of incident",
                "list of item",
                "will be provided",
            ]
            is_placeholder = (
                any(p in final_ans.lower() for p in placeholder_patterns)
                if final_ans
                else True
            )

            if (
                final_ans
                and contexts
                and step > 0
                and final_ans != "The final answer will be provided after validation."
                and len(final_ans) > 50
                and not is_placeholder
            ):
                final_ans = plan["final_answer"]
                logger.info("=" * 50)
                logger.info(f"FINAL ANSWER FROM AGENT:\n{final_ans}")
                logger.info("=" * 50)

                # Run quick validation to get confidence
                if contexts:
                    ranked = self.reranker_agent.rerank(query, contexts, top_k=3)
                    validation = self.validator_agent.validate(final_ans, ranked)
                    logger.info(
                        f"Validation: {validation['decision']} ({validation['confidence']:.2f})"
                    )
                    return {
                        "answer": final_ans,
                        "sources": self._collect_sources(ranked),
                        "contexts": ranked,
                        "confidence": validation["confidence"],
                        "agent_trace": trace,
                        "xai_explanation": xai_explanations,
                        "status": "success",
                    }

                return {
                    "answer": final_ans,
                    "sources": self._collect_sources(contexts),
                    "contexts": contexts,
                    "agent_trace": trace,
                    "xai_explanation": xai_explanations,
                    "status": "success",
                }

            # FORCE SEARCH if no contexts collected yet and action isn't a search
            action = plan.get("action")
            action_input = plan.get("action_input")
            if action not in ("doc_search", "ticket_search") and not contexts:
                logger.warning("No contexts collected. Forcing doc_search as fallback.")
                action = "doc_search"
                action_input = query
                plan["action"] = action
                plan["action_input"] = action_input

            if action == "doc_search":
                logger.info(f"Action: doc_search('{action_input}')")
                results = self.retrieval_agent.search(action_input or query)
                contexts.extend(results)
                history.append(f"Observation: doc_search found {len(results)} items.")
                trace.append(f"Retrieval Agent -> Found {len(results)} document chunks")

                # Structured XAI for Retrieval
                top_score = max(
                    [r.get("retrieval_score", 0) for r in results], default=0
                )
                xai_explanations.append(
                    self.xai.explain_retrieval(len(results), 0, top_score)
                )

            elif action == "ticket_search":
                logger.info(f"Action: ticket_search('{action_input}')")
                results = self.ticket_agent.search(action_input or query)
                contexts.extend(results)
                history.append(
                    f"Observation: ticket_search found {len(results)} items."
                )
                trace.append(f"Ticket Agent -> Found {len(results)} matching tickets")

                # Structured XAI for Ticket Search
                top_score = max(
                    [r.get("retrieval_score", 0) for r in results], default=0
                )
                xai_explanations.append(
                    self.xai.explain_retrieval(0, len(results), top_score)
                )

            elif action == "synthesize":
                logger.info("Action: synthesize")
                if not contexts:
                    logger.warning("No contexts available to synthesize.")
                    history.append("Observation: No contexts available to synthesize.")
                    continue
                ranked = self.reranker_agent.rerank(query, contexts, top_k=3)
                answer, fallback = self.synthesis_agent.generate(query, ranked)
                last_answer = answer
                history.append(
                    f"Observation: Synthesis generated an answer. Length: {len(answer)}"
                )
                trace.append("Synthesis Agent -> Generated grounded answer")

                # Structured XAI for Synthesis
                xai_explanations.append(
                    self.xai.explain_synthesis(len(answer), len(ranked), fallback)
                )

                # Auto-validate after synthesis (if next action isn't validate)
                if plan.get("action") != "validate":
                    logger.info("Auto-validating synthesized answer...")
                    validation = self.validator_agent.validate(answer, ranked)
                    logger.info(
                        f"Auto-validation: {validation['decision']} ({validation['confidence']:.2f})"
                    )
                    trace.append(
                        f"Validator Agent -> Confidence {validation['confidence']:.2f} ({validation['decision']})"
                    )
                    xai_explanations.append(
                        self.xai.explain_validator(
                            validation["confidence"],
                            validation["decision"],
                            validation.get("retrieval_similarity", 0),
                            validation.get("reranker_score", 0),
                            validation.get("llm_self_eval", 0),
                        )
                    )

                    if validation["decision"] == "respond":
                        return {
                            "answer": answer,
                            "sources": self._collect_sources(ranked),
                            "contexts": ranked,
                            "confidence": validation["confidence"],
                            "agent_trace": trace,
                            "xai_explanation": xai_explanations,
                            "status": "success",
                        }

            elif action == "validate":
                logger.info("Action: validate")
                if not last_answer:
                    logger.warning("No answer to validate.")
                    history.append("Observation: No answer to validate.")
                    continue
                ranked = self.reranker_agent.rerank(query, contexts, top_k=3)
                validation = self.validator_agent.validate(last_answer, ranked)
                logger.info(
                    f"Validation result: {validation['decision']} (score: {validation['confidence']:.2f})"
                )
                trace.append(
                    f"Validator Agent -> Confidence {validation['confidence']:.2f} ({validation['decision']})"
                )

                # Structured XAI for Validator (Formula and Factors)
                xai_explanations.append(
                    self.xai.explain_validator(
                        validation["confidence"],
                        validation["decision"],
                        validation.get("retrieval_similarity", 0),
                        validation.get("reranker_score", 0),
                        validation.get("llm_self_eval", 0),
                    )
                )

                if validation["decision"] == "respond":
                    logger.info("Validation successful. Responding to user.")
                    return {
                        "answer": last_answer,
                        "sources": self._collect_sources(ranked),
                        "contexts": ranked,
                        "confidence": validation["confidence"],
                        "agent_trace": trace,
                        "xai_explanation": xai_explanations,
                        "status": "success",
                    }
                else:
                    logger.info(f"Validation failed. Reason: {validation['decision']}")
                    history.append(
                        f"Observation: Validation failed with score {validation['confidence']}. Decision: {validation['decision']}"
                    )

            elif action == "summarize":
                logger.info("Action: summarize")
                if not contexts:
                    history.append("Observation: No contexts available to summarize.")
                    continue
                summary = self.summarizer_agent.summarize(contexts)
                last_answer = summary
                history.append(
                    f"Observation: Summarizer generated a summary. Length: {len(summary)}"
                )
                trace.append("Summarizer Agent -> Generated executive summary")
                xai_explanations.append(
                    {
                        "agent": "Summarizer Agent",
                        "reason": "Generated concise summary of retrieved context.",
                        "decision": "summarized",
                    }
                )

            elif action == "check_duplicates":
                logger.info("Action: check_duplicates")
                results = self.ticket_agent.search(action_input or query, top_k=1)
                if results and results[0].get("retrieval_score", 0) > 0.85:
                    duplicate = results[0]
                    logger.info(
                        f"Found high-confidence duplicate: {duplicate['ticket_id']}"
                    )
                    history.append(
                        f"Observation: Found potential duplicate ticket {duplicate['ticket_id']} with score {duplicate['retrieval_score']:.2f}"
                    )
                    trace.append(
                        f"Ticket Agent -> Flagged potential duplicate: {duplicate['ticket_id']}"
                    )
                    if duplicate.get("resolution"):
                        last_answer = f"This issue appears to be a duplicate of ticket **{duplicate['ticket_id']}**. \n\n**Previous Resolution:** {duplicate['resolution']}"
                else:
                    logger.info("No duplicates found.")
                    history.append(
                        "Observation: No high-confidence duplicate tickets found."
                    )
                    trace.append("Ticket Agent -> No duplicate issues detected")
                xai_explanations.append(
                    {
                        "agent": "Ticket Agent",
                        "reason": "Checked for high-similarity duplicates in historical records.",
                        "decision": "checked_duplicates",
                    }
                )
            else:
                logger.warning(f"Unknown action: {action}")
                break

        logger.warning("Max steps reached without high-confidence answer. Escalating.")
        return {
            "status": "escalated",
            "reason": "Max planning steps reached without confidence",
            "suggestion": "Forward to human engineer",
            "agent_trace": trace,
            "xai_explanation": xai_explanations,
        }
