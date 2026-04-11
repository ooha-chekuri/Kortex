"""
XAI (Explainable AI) - Agent Decision Explanations
This module provides human-readable explanations for each agent's decisions.
"""

from __future__ import annotations

from typing import Any


class XAIExplainer:
    """Generate explanations for agent decisions."""

    @staticmethod
    def explain_triage(intent: str, query: str) -> dict[str, Any]:
        """Explain why Triage Agent chose this intent."""
        keywords_found = []

        # Document keywords
        doc_keywords = [
            "how",
            "what",
            "guide",
            "setup",
            "configure",
            "install",
            "kafka",
            "kubernetes",
            "docker",
            "vpn",
        ]
        # Ticket keywords
        ticket_keywords = [
            "error",
            "issue",
            "problem",
            "fix",
            "incident",
            "ticket",
            "bug",
            "failed",
            "auth",
            "login",
        ]

        query_lower = query.lower()
        for kw in doc_keywords:
            if kw in query_lower:
                keywords_found.append(kw)
        for kw in ticket_keywords:
            if kw in query_lower:
                keywords_found.append(f"[ticket]{kw}")

        explanation = f"Analyzed query for keywords. Found: {', '.join(keywords_found) if keywords_found else 'none specific'}."

        if intent == "both":
            explanation += (
                " Both document and ticket keywords detected - searching both sources."
            )
        elif intent == "docs":
            explanation += " Document keywords dominant - searching knowledge base."
        else:
            explanation += (
                " Ticket/issue keywords dominant - searching historical incidents."
            )

        return {
            "decision": intent,
            "reason": explanation,
            "confidence": "high" if len(keywords_found) >= 2 else "medium",
            "query_keywords": keywords_found,
        }

    @staticmethod
    def explain_retrieval(
        doc_count: int, ticket_count: int, top_score: float
    ) -> dict[str, Any]:
        """Explain why Retrieval Agent returned these results."""
        total = doc_count + ticket_count

        explanation = f"Searched vector database. Found {doc_count} document chunks and {ticket_count} ticket matches."

        if total == 0:
            explanation += " No relevant results found for this query."
            return {
                "decision": "no_results",
                "reason": explanation,
                "suggestion": "Try rephrasing the question or using different keywords.",
            }

        explanation += f" Top match had similarity score of {top_score:.2f}."

        if top_score > 0.7:
            explanation += " High relevance - strong semantic match."
            confidence = "high"
        elif top_score > 0.4:
            explanation += " Medium relevance - partial match found."
            confidence = "medium"
        else:
            explanation += " Low relevance - results may need verification."
            confidence = "low"

        return {
            "decision": f"found_{total}_results",
            "reason": explanation,
            "top_score": top_score,
            "confidence": confidence,
            "doc_count": doc_count,
            "ticket_count": ticket_count,
        }

    @staticmethod
    def explain_rerank(
        original_count: int, selected_count: int, scores: list[float]
    ) -> dict[str, Any]:
        """Explain why Reranker Agent selected these items."""

        explanation = f"Cross-encoder re-ranked {original_count} items. Selected top {selected_count} based on query-document relevance."

        if selected_count > 0:
            avg_score = sum(scores) / len(scores)
            explanation += f" Average relevance score: {avg_score:.2f}."

            if avg_score > 0.7:
                explanation += (
                    " High confidence in selection - strong semantic alignment."
                )
                confidence = "high"
            elif avg_score > 0.4:
                explanation += " Moderate confidence - some relevant content found."
                confidence = "medium"
            else:
                explanation += " Low confidence - selected best available but may need verification."
                confidence = "low"
        else:
            explanation += " No items passed the relevance threshold."
            confidence = "low"

        return {
            "decision": f"selected_{selected_count}",
            "reason": explanation,
            "scores": scores,
            "confidence": confidence,
        }

    @staticmethod
    def explain_synthesis(
        answer_length: int, source_count: int, had_fallback: bool
    ) -> dict[str, Any]:
        """Explain why Synthesis Agent generated this response."""

        explanation = f"Generated response based on {source_count} context sources."

        if answer_length < 50:
            explanation += " Brief response generated."
            confidence = "low"
        elif answer_length < 500:
            explanation += " Concise answer provided."
            confidence = "medium"
        else:
            explanation += " Detailed response with multiple citations."
            confidence = "high"

        if had_fallback:
            explanation += " Used fallback generation (LLM quota exceeded)."
            confidence = "low"

        return {
            "decision": "generated_response",
            "reason": explanation,
            "answer_length": answer_length,
            "source_count": source_count,
            "confidence": confidence,
            "used_fallback": had_fallback,
        }

    @staticmethod
    def explain_validator(
        confidence_score: float,
        decision: str,
        retrieval_sim: float,
        reranker_score: float,
        llm_self_eval: float,
    ) -> dict[str, Any]:
        """Explain why Validator Agent made this decision."""

        # Formula explanation
        formula = f"confidence = (0.4 * {retrieval_sim:.2f}) + (0.35 * {reranker_score:.2f}) + (0.25 * {llm_self_eval:.2f})"

        explanation = f"Computed confidence using weighted formula: retrieval({retrieval_sim:.2f} × 0.4) + reranker({reranker_score:.2f} × 0.35) + self_eval({llm_self_eval:.2f} × 0.25)"

        reasons = []

        if retrieval_sim > 0.6:
            reasons.append("Strong retrieval match")
        elif retrieval_sim > 0.3:
            reasons.append("Moderate retrieval relevance")
        else:
            reasons.append("Weak retrieval match")

        if reranker_score > 0.6:
            reasons.append("High reranking confidence")
        elif reranker_score > 0.3:
            reasons.append("Medium reranking score")
        else:
            reasons.append("Low reranking score")

        if llm_self_eval > 0.7:
            reasons.append("LLM self-assessment is confident")
        elif llm_self_eval > 0.4:
            reasons.append("LLM self-assessment is moderate")
        else:
            reasons.append("LLM self-assessment is uncertain")

        if decision == "respond":
            final_reason = "High enough confidence to provide answer directly."
        elif decision == "retry":
            final_reason = (
                "Medium confidence - attempting expanded retrieval for better results."
            )
        else:
            final_reason = (
                "Low confidence - insufficient reliable context. Escalating to human."
            )

        return {
            "decision": decision,
            "confidence_score": confidence_score,
            "reason": explanation,
            "factors": reasons,
            "formula": formula,
            "final_reason": final_reason,
            "thresholds": "respond >= 0.5, retry >= 0.35, escalate < 0.35",
        }

    @staticmethod
    def explain_orchestrator_retry(retry_count: int, expanded_k: int) -> dict[str, Any]:
        """Explain why Orchestrator decided to retry."""

        explanation = f"Initial confidence below threshold. Initiating retry #{retry_count + 1} with expanded search (top_k={expanded_k})."

        return {
            "decision": "retry",
            "reason": explanation,
            "retry_number": retry_count + 1,
            "expansion": f"Increased retrieval to top {expanded_k} items",
        }

    @staticmethod
    def explain_escalation(reason: str, confidence: float) -> dict[str, Any]:
        """Explain why system escalated to human."""

        explanation = f"Could not generate confident answer. Confidence: {confidence:.2f} (threshold: 0.35)"

        return {
            "decision": "escalate",
            "reason": explanation,
            "confidence": confidence,
            "suggestion": "This query requires human expertise. Please contact IT support or subject matter expert.",
        }


def generate_full_xai_trace(
    query: str,
    triage_result: dict,
    retrieval_result: dict,
    rerank_result: dict,
    synthesis_result: dict,
    validator_result: dict,
    final_decision: str,
) -> list[dict[str, Any]]:
    """Generate complete XAI trace with explanations for each step."""

    trace = []

    # Step 1: Triage
    trace.append(
        {
            "step": 1,
            "agent": "Triage Agent",
            "decision": triage_result.get("decision"),
            "reason": triage_result.get("reason"),
            "confidence": triage_result.get("confidence"),
            "query": query,
        }
    )

    # Step 2: Retrieval
    trace.append(
        {
            "step": 2,
            "agent": "Retrieval Agent",
            "decision": retrieval_result.get("decision"),
            "reason": retrieval_result.get("reason"),
            "confidence": retrieval_result.get("confidence"),
            "details": {
                "docs_found": retrieval_result.get("doc_count", 0),
                "tickets_found": retrieval_result.get("ticket_count", 0),
                "top_score": retrieval_result.get("top_score", 0),
            },
        }
    )

    # Step 3: Rerank
    trace.append(
        {
            "step": 3,
            "agent": "Reranker Agent",
            "decision": rerank_result.get("decision"),
            "reason": rerank_result.get("reason"),
            "confidence": rerank_result.get("confidence"),
            "details": {
                "items_selected": len(rerank_result.get("scores", [])),
                "scores": rerank_result.get("scores", []),
            },
        }
    )

    # Step 4: Synthesis
    trace.append(
        {
            "step": 4,
            "agent": "Synthesis Agent",
            "decision": synthesis_result.get("decision"),
            "reason": synthesis_result.get("reason"),
            "confidence": synthesis_result.get("confidence"),
            "details": {
                "answer_length": synthesis_result.get("answer_length", 0),
                "sources_used": synthesis_result.get("source_count", 0),
                "used_fallback": synthesis_result.get("used_fallback", False),
            },
        }
    )

    # Step 5: Validator
    trace.append(
        {
            "step": 5,
            "agent": "Validator Agent",
            "decision": validator_result.get("decision"),
            "reason": validator_result.get("final_reason"),
            "confidence": validator_result.get("confidence_score"),
            "details": {
                "formula": validator_result.get("formula"),
                "factors": validator_result.get("factors", []),
                "retrieval_similarity": validator_result.get("retrieval_similarity"),
                "reranker_score": validator_result.get("reranker_score"),
                "llm_self_eval": validator_result.get("llm_self_eval"),
            },
        }
    )

    # Step 6: Final Decision
    trace.append(
        {
            "step": 6,
            "agent": "System",
            "decision": final_decision,
            "reason": "Final decision based on validator confidence score",
            "confidence": validator_result.get("confidence_score"),
            "thresholds_applied": "respond >= 0.5, retry >= 0.35, escalate < 0.35",
        }
    )

    return trace
