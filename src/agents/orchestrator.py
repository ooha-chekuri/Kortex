import os
from typing import Any, Dict, List
from src.core.config import TOP_K_RETRIEVAL, TOP_K_RERANK
from src.retrieval.engine import get_retrieval_engine
from src.agents.triage_agent import classify_intent
from src.agents.synthesis_agent import SynthesisAgent
from src.agents.validator_agent import ValidatorAgent

engine = None
synthesis_agent = None
validator_agent = None


def _get_components():
    global engine, synthesis_agent, validator_agent
    if engine is None:
        engine = get_retrieval_engine()
        synthesis_agent = SynthesisAgent()
        validator_agent = ValidatorAgent()
    return engine, synthesis_agent, validator_agent


def run_kortex_agent(query: str):
    """Simple fast agent without LangGraph overhead."""
    engine, synthesis_agent, validator_agent = _get_components()

    intent = classify_intent(query)
    yield {
        "triage": {
            "intent": intent,
            "trace": [f"Triage: Classified intent as '{intent.upper()}'"],
        }
    }

    context = engine.get_context(
        query, type=intent, top_k=TOP_K_RETRIEVAL, rerank_k=TOP_K_RERANK
    )
    yield {
        "retrieval": {
            "context": context,
            "trace": [
                f"Retrieval: Found {len(context)} relevant documents/tickets (Reranked)"
            ],
        }
    }

    if not context:
        result = {
            "answer": "I couldn't find any relevant information in my knowledge base.",
            "confidence": 0.0,
            "status": "escalated",
        }
        yield {
            "synthesis": {
                "answer": result["answer"],
                "trace": ["Synthesis: No context found - escalating"],
            }
        }
        yield {
            "validator": {
                "confidence": 0.0,
                "decision": "escalate",
                "trace": ["Validator: Confidence 0.00 (Decision: ESCALATE)"],
            }
        }
        return

    result = synthesis_agent.generate(query, context)
    answer = result.get("answer", "NO_ANSWER")
    self_eval = result.get("confidence", 0.5)
    yield {
        "synthesis": {
            "answer": answer,
            "confidence": self_eval,
            "trace": [f"Synthesis: Generated response (Self-Eval: {self_eval})"],
        }
    }

    validation = validator_agent.validate(answer, context, llm_self_eval=self_eval)
    yield {
        "validator": {
            "confidence": validation["confidence"],
            "decision": validation["decision"],
            "trace": [
                f"Validator: Confidence Score: {validation['confidence']:.2f} (Decision: {validation['decision'].upper()})"
            ],
        }
    }
