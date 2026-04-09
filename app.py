import streamlit as st
import time
import os
from pathlib import Path
import json

# Absolute imports from root
from src.agents.orchestrator import run_kortex_agent
from src.data.ingest import build_indices

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Kortex | Enterprise Knowledge Copilot",
    layout="wide",
    page_icon="🔷",
    initial_sidebar_state="expanded"
)

# Custom CSS for Clean Light Theme + Departure Mono Aesthetic
st.markdown("""
    <style>
    /* Load Departure Mono via CDN */
    @font-face {
        font-family: 'Departure Mono';
        src: url('https://cdn.jsdelivr.net/gh/lucas-dlevy/departure-mono@main/fonts/DepartureMono-Regular.woff2') format('woff2');
        font-weight: normal;
        font-style: normal;
    }

    /* Force Light Theme Base */
    :root {
        --primary-color: #4b49ff;
        --bg-color: #ffffff;
        --text-color: #1a1a1a;
        --accent-bg: #f8f9fa;
        --border-color: #e0e0e0;
    }

    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
    }

    /* Global Font Override */
    * {
        font-family: 'Departure Mono', monospace !important;
    }

    /* Remove heavy black OS borders, use clean cards */
    .result-card {
        border: 1px solid var(--border-color);
        padding: 20px;
        background-color: var(--bg-color);
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }

    .thinking-trace {
        background-color: var(--accent-bg);
        border-left: 3px solid var(--primary-color);
        padding: 15px;
        border-radius: 0 4px 4px 0;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* Button Styling */
    .stButton>button {
        border-radius: 4px !important;
        border: 1px solid var(--primary-color) !important;
        background-color: var(--bg-color) !important;
        color: var(--primary-color) !important;
        font-weight: bold !important;
        width: 100% !important;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: var(--primary-color) !important;
        color: #ffffff !important;
    }
    .stButton>button[kind="primary"] {
        background-color: var(--primary-color) !important;
        color: #ffffff !important;
    }

    /* Headings */
    h1, h2, h3 {
        color: #000000;
        margin-top: 0;
    }

    /* Custom Badges */
    .badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .badge-doc { background-color: #e3f2fd; color: #0d47a1; }
    .badge-ticket { background-color: #f1f8e9; color: #33691e; }

    /* Escalation Banner */
    .escalation-banner {
        border: 1px solid #ff5252;
        background-color: #ffebee;
        color: #b71c1c;
        padding: 15px;
        margin-top: 20px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if 'agent_output' not in st.session_state: st.session_state.agent_output = None
if 'trace_logs' not in st.session_state: st.session_state.trace_logs = []
if 'query' not in st.session_state: st.session_state.query = ""

# --- SIDEBAR (ADMIN & CONFIG) ---
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM ADMIN")
    st.info("Upload technical docs or support tickets to build the enterprise knowledge base.")
    
    with st.expander("📁 UPLOAD KNOWLEDGE", expanded=False):
        uploaded_files = st.file_uploader("Upload PDF, TXT, or MD", type=["pdf", "txt", "md"], accept_multiple_files=True)
        if uploaded_files:
            docs_path = Path("docs")
            docs_path.mkdir(exist_ok=True)
            for uploaded_file in uploaded_files:
                with open(docs_path / uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success(f"Saved {len(uploaded_files)} files to /docs")

    if st.button("🔄 SYNC KNOWLEDGE BASE"):
        with st.spinner("Analyzing and indexing documents..."):
            stats = build_indices()
            st.success(f"Indexed: {stats['docs']} Documents | {stats['tickets']} Tickets")

    st.divider()
    st.markdown("### ℹ️ ABOUT")
    st.caption("Kortex leverages a multi-agent orchestration framework to provide validated answers from fragmented documentation.")
    if st.button("🗑️ CLEAR SESSION"):
        st.session_state.clear()
        st.rerun()

# --- MAIN INTERFACE ---
st.markdown("# 🔷 KORTEX")
st.markdown("### ENTERPRISE KNOWLEDGE COPILOT")
st.write("Search across PDFs, SOPs, and historical support tickets with agentic reasoning.")

# Query Input
query_input = st.text_input("Ask a question:", placeholder="e.g., 'How do I resolve Kafka consumer lag?'", label_visibility="collapsed")
if query_input:
    st.session_state.query = query_input

if st.button("ASK KORTEX", type="primary"):
    if st.session_state.query:
        st.session_state.trace_logs = []
        st.session_state.agent_output = None
        
        # Display thinking status
        with st.status("🧠 Agents collaborating...", expanded=True) as status:
            final_result = {}
            for step in run_kortex_agent(st.session_state.query):
                node_name = list(step.keys())[0]
                node_data = step[node_name]
                
                # Format node name for display
                display_name = node_name.replace("_", " ").title()
                status.write(f"**{display_name}**: Working...")
                
                if "trace" in node_data:
                    st.session_state.trace_logs.extend(node_data["trace"])
                
                # Save state
                for k, v in node_data.items():
                    if k != "trace":
                        final_result[k] = v
                
                time.sleep(0.2)
            
            status.update(label="✅ Reasoning Complete", state="complete")
        
        st.session_state.agent_output = final_result
        st.rerun()
    else:
        st.warning("Please enter a query first.")

# --- RESULTS AREA ---
if st.session_state.agent_output:
    st.divider()
    col_trace, col_ans = st.columns([1, 2])
    
    with col_trace:
        st.markdown("### 🧠 AGENT ACTIVITY")
        trace_box = ""
        for log in st.session_state.trace_logs:
            trace_box += f"- {log}\n"
        st.markdown(f"<div class='thinking-trace'>{trace_box}</div>", unsafe_allow_html=True)

    with col_ans:
        st.markdown("### 📄 GROUNDED RESPONSE")
        res = st.session_state.agent_output
        
        if res.get("status") == "escalated":
            st.error(f"**Escalation Triggered**: {res.get('reason', 'Confidence score below threshold.')}")
            st.markdown("<div class='escalation-banner'>⚠️ System uncertain. Redirecting to human engineer.</div>", unsafe_allow_html=True)
        else:
            # Answer Card
            st.markdown(f"<div class='result-card'>{res.get('answer', 'No response generated.')}</div>", unsafe_allow_html=True)
            
            # Sources & Confidence Row
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 📚 SOURCES")
                if res.get("context"):
                    # Deduplicate and display sources
                    seen_sources = set()
                    for ctx in res["context"]:
                        src_id = ctx.get("source", "Unknown")
                        src_type = ctx.get("type", "doc")
                        if src_id not in seen_sources:
                            badge_class = "badge-doc" if src_type == "doc" else "badge-ticket"
                            st.markdown(f"<span class='badge {badge_class}'>{src_type}</span> **{src_id}**", unsafe_allow_html=True)
                            seen_sources.add(src_id)
                else:
                    st.caption("No direct documents cited.")

            with c2:
                st.markdown("#### ⚖️ VALIDATION")
                conf = res.get("confidence", 0.0)
                conf_pct = int(conf * 100)
                st.metric("Confidence Score", f"{conf_pct}%")
                
                if conf < 0.5:
                    st.markdown("<div class='escalation-banner'>⚠️ Low confidence detected. Escalating.</div>", unsafe_allow_html=True)

else:
    if not query_input:
        st.divider()
        st.info("Kortex is ready. Enter a question above to start the agentic retrieval process.")
        st.caption("Tip: You can use the sidebar to upload your own enterprise data.")
