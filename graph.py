import operator
from typing import Annotated, Any, Dict, List, Literal, TypedDict, Union

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END

from src.agents.reranker_agent import RerankerAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.synthesis_agent import SynthesisAgent
from src.agents.ticket_agent import TicketAgent
from src.agents.triage_agent import classify_intent
from src.agents.validator_agent import ValidatorAgent

# Initialize agents
retrieval_agent = RetrievalAgent()
ticket_agent = TicketAgent()
reranker_agent = RerankerAgent()
synthesis_agent = SynthesisAgent()
validator_agent = ValidatorAgent()

class AgentState(TypedDict):
    query: str
    intent: str
    docs: List[Dict[str, Any]]
    tickets: List[Dict[str, Any]]
    combined_context: List[Dict[str, Any]]
    ranked_context: List[Dict[str, Any]]
    answer: str
    confidence: float
    decision: str
    trace: Annotated[List[str], operator.add]
    retry_count: int
    status: str

def triage_node(state: AgentState):
    query = state["query"]
    intent = classify_intent(query)
    return {
        "intent": intent,
        "trace": [f"Triage: Intent identified as '{intent}'"]
    }

def retrieval_node(state: AgentState):
    query = state["query"]
    intent = state["intent"]
    retry_count = state.get("retry_count", 0)
    
    doc_k = 5 if retry_count == 0 else 8
    ticket_k = 3 if retry_count == 0 else 5
    
    docs = retrieval_agent.search(query, top_k=doc_k) if intent in {"docs", "both"} else []
    tickets = ticket_agent.search(query, top_k=ticket_k) if intent in {"tickets", "both"} else []
    
    trace = []
    if docs: trace.append(f"Retrieval: Found {len(docs)} documents")
    if tickets: trace.append(f"Ticket: Found {len(tickets)} historical cases")
    
    return {
        "docs": docs,
        "tickets": tickets,
        "combined_context": docs + tickets,
        "trace": trace
    }

def rerank_node(state: AgentState):
    query = state["query"]
    combined = state["combined_context"]
    
    if not combined:
        return {"status": "escalated", "trace": ["Guardrail: No context found. Escalating."]}
    
    ranked = reranker_agent.rerank(query, combined, top_k=3)
    return {
        "ranked_context": ranked,
        "trace": [f"Reranker: Selected top {len(ranked)} relevant items"]
    }

def synthesis_node(state: AgentState):
    query = state["query"]
    ranked = state["ranked_context"]
    answer = synthesis_agent.generate(query, ranked)
    return {
        "answer": answer,
        "trace": ["Synthesis: Generated grounded response"]
    }

def validator_node(state: AgentState):
    answer = state["answer"]
    ranked = state["ranked_context"]
    validation = validator_agent.validate(answer, ranked)
    
    return {
        "confidence": validation["confidence"],
        "decision": validation["decision"],
        "trace": [f"Validator: Confidence {validation['confidence']:.2f} - {validation['decision']}"]
    }

def router(state: AgentState) -> Literal["rerank", "synthesis", "validator", "retry", "escalate", "end"]:
    if state.get("status") == "escalated":
        return "escalate"
    
    decision = state.get("decision")
    if decision == "respond":
        return "end"
    elif decision == "retry":
        if state.get("retry_count", 0) < 1:
            return "retry"
        else:
            return "escalate"
    elif decision == "escalate":
        return "escalate"
    
    # Default flow progression
    if not state.get("intent"): return "triage"
    if not state.get("combined_context"): return "retrieval"
    if not state.get("ranked_context"): return "rerank"
    if not state.get("answer"): return "synthesis"
    return "validator"

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("triage", triage_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("rerank", rerank_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("validator", validator_node)
    
    workflow.set_entry_point("triage")
    
    workflow.add_edge("triage", "retrieval")
    workflow.add_edge("retrieval", "rerank")
    workflow.add_edge("rerank", "synthesis")
    workflow.add_edge("synthesis", "validator")
    
    def decide_next(state):
        if state.get("status") == "escalated":
            return END
        
        decision = state.get("decision")
        if decision == "respond":
            return END
        if decision == "retry":
            # This is a bit simplified for now, ideally we'd loop back to retrieval
            # but LangGraph needs explicit edge for loops
            return "retrieval"
        if decision == "escalate":
            return END
        return END

    workflow.add_conditional_edges(
        "validator",
        decide_next,
        {
            "retrieval": "retrieval",
            END: END
        }
    )
    
    return workflow.compile()

# For UI streaming
def run_kortex(query: str):
    app = build_graph()
    inputs = {
        "query": query,
        "retry_count": 0,
        "trace": [],
        "docs": [],
        "tickets": [],
        "combined_context": [],
        "ranked_context": [],
        "answer": "",
        "confidence": 0.0,
        "decision": "",
        "status": "processing"
    }
    
    for output in app.stream(inputs):
        # output is a dict with node name as key and its return as value
        yield output
