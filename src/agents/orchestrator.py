import operator
import time
import streamlit as st
from typing import Annotated, Any, Dict, List, Literal, TypedDict, Union
from langgraph.graph import StateGraph, END
from src.retrieval.engine import get_retrieval_engine
from src.agents.triage_agent import classify_intent
from src.agents.synthesis_agent import SynthesisAgent
from src.agents.validator_agent import ValidatorAgent

# Initialize Core Components
engine = get_retrieval_engine()
synthesis_agent = SynthesisAgent()
validator_agent = ValidatorAgent()

class AgentState(TypedDict):
    query: str
    intent: str
    context: List[Dict[str, Any]]
    answer: str
    confidence: float
    decision: str
    trace: Annotated[List[str], operator.add]
    status: str

def triage_node(state: AgentState):
    intent = classify_intent(state["query"])
    return {"intent": intent, "trace": [f"Triage: Classified intent as '{intent.upper()}'"]}

def retrieval_node(state: AgentState):
    context = engine.get_context(state["query"], type=state["intent"])
    return {
        "context": context,
        "trace": [f"Retrieval: Found {len(context)} relevant documents/tickets (Reranked)"]
    }

def synthesis_node(state: AgentState):
    if not state["context"]:
        return {"answer": "I'm sorry, I couldn't find any relevant information in my knowledge base.", "status": "escalated"}
    
    answer = synthesis_agent.generate(state["query"], state["context"])
    return {"answer": answer, "trace": ["Synthesis: Generated response based on context"]}

def validator_node(state: AgentState):
    if state.get("status") == "escalated":
        return {"decision": "escalate"}
    
    validation = validator_agent.validate(state["answer"], state["context"])
    return {
        "confidence": validation["confidence"],
        "decision": validation["decision"],
        "trace": [f"Validator: Confidence Score: {validation['confidence']:.2f} (Decision: {validation['decision'].upper()})"]
    }

def build_agentic_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("triage", triage_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("validator", validator_node)
    
    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "retrieval")
    workflow.add_edge("retrieval", "synthesis")
    workflow.add_edge("synthesis", "validator")
    
    def decide_next(state):
        if state.get("status") == "escalated" or state.get("decision") == "escalate":
            return END
        if state.get("decision") == "respond":
            return END
        if state.get("decision") == "retry":
            # Just end for now to prevent infinite loops in demo, but could loop back
            return END
        return END

    workflow.add_conditional_edges("validator", decide_next, {END: END})
    return workflow.compile()

def run_kortex_agent(query: str):
    app = build_agentic_graph()
    inputs = {
        "query": query,
        "trace": [],
        "context": [],
        "answer": "",
        "confidence": 0.0,
        "decision": "",
        "status": "processing"
    }
    for output in app.stream(inputs):
        yield output
