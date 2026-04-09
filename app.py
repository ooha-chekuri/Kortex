import streamlit as st
import time
import os
from pathlib import Path
import json

# Absolute imports from root
from src.agents.orchestrator import run_kortex_agent
from src.data.ingest import build_indices

# --- CORE CONFIGURATION (MUST BE FIRST) ---
st.set_page_config(
    page_title="KORTEX | Enterprise Knowledge Copilot",
    layout="wide",
    page_icon="🔷",
    initial_sidebar_state="expanded"
)

# --- HIGH-FIDELITY FULL LIGHT THEME (DASHBOARD AESTHETIC) ---
st.markdown("""
    <style>
    /* Load Departure Mono via CDN */
    @font-face {
        font-family: 'Departure Mono';
        src: url('https://cdn.jsdelivr.net/gh/lucas-dlevy/departure-mono@main/fonts/DepartureMono-Regular.woff2') format('woff2');
        font-weight: normal;
        font-style: normal;
    }

    /* Force Full Light Theme (Strict White/Black/Blue) */
    :root {
        --primary-color: #4b49ff;
        --bg-color: #ffffff;
        --text-color: #000000;
        --border-color: #000000;
        --subtle-gray: #f9f9f9;
    }

    /* Global Overrides */
    .stApp {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }

    * {
        font-family: 'Departure Mono', monospace !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-color) !important;
        border-right: 1px solid var(--border-color);
    }

    /* CRISP DASHBOARD CONTAINERS (The "Box" Look) */
    .dashboard-box {
        border: 1px solid var(--border-color);
        padding: 20px;
        background-color: var(--bg-color);
        margin-bottom: 15px;
        border-radius: 0px;
    }

    .dashboard-label {
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
        color: #555;
        margin-bottom: 8px;
        display: block;
    }

    /* Input & Button Styling */
    .stTextInput input {
        border-radius: 0px !important;
        border: 1px solid var(--border-color) !important;
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        padding: 12px !important;
    }

    .stButton>button {
        border-radius: 0px !important;
        border: 1px solid var(--border-color) !important;
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        font-weight: bold !important;
        width: 100% !important;
        transition: 0.1s;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background-color: var(--border-color) !important;
        color: var(--bg-color) !important;
    }
    .stButton>button[kind="primary"] {
        background-color: var(--primary-color) !important;
        color: #ffffff !important;
        border: 1px solid var(--primary-color) !important;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: var(--text-color);
        text-transform: uppercase;
        margin-top: 0;
    }

    /* Custom Trace Logs */
    .trace-line {
        font-size: 0.85rem;
        padding: 4px 0;
        border-bottom: 1px solid #eee;
        color: #333;
    }

    /* Hide standard UI fluff */
    #MainMenu, footer, header {visibility: hidden;}

    /* Escalation Box */
    .escalation-box {
        border: 2px dashed #ff0000;
        background-color: #fffafa;
        color: #ff0000;
        padding: 20px;
        margin-top: 20px;
        text-align: center;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if 'agent_output' not in st.session_state: st.session_state.agent_output = None
if 'trace_logs' not in st.session_state: st.session_state.trace_logs = []
if 'query' not in st.session_state: st.session_state.query = ""

# --- SIDEBAR (ADMIN TOOLS) ---
with st.sidebar:
    st.markdown("### 🔷 SYSTEM_ADMIN")
    st.markdown("<p class='dashboard-label'>KNOWLEDGE_INGESTION</p>", unsafe_allow_html=True)
    
    with st.container():
        uploaded_files = st.file_uploader("UPLOAD_FILES", type=["pdf", "txt", "md"], accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files:
            docs_path = Path("docs")
            docs_path.mkdir(exist_ok=True)
            for uploaded_file in uploaded_files:
                with open(docs_path / uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success(f"SAVED_{len(uploaded_files)}_FILES")

    if st.button("SYNC_KNOWLEDGE_BASE"):
        with st.spinner("ANALYZING_DATA..."):
            stats = build_indices()
            st.success(f"OK: {stats['docs']} DOCS / {stats['tickets']} TIX")

    st.divider()
    st.markdown("<p class='dashboard-label'>SESSION_CONTROLS</p>", unsafe_allow_html=True)
    if st.button("RESET_SESSION"):
        st.session_state.clear()
        st.rerun()

# --- MAIN DASHBOARD INTERFACE ---
st.markdown("## 🔷 KORTEX // ENTERPRISE_COPILOT")
st.markdown("<p style='font-size:0.8rem; opacity:0.6;'>AGENTIC_REASONING_ACTIVE // GROUNDED_RETRIEVAL_MODE</p>", unsafe_allow_html=True)

# Main Query Section
st.markdown("<p class='dashboard-label'>QUERY_INPUT</p>", unsafe_allow_html=True)
query_input = st.text_input("INPUT", value=st.session_state.query, placeholder="ENTER COMMAND OR SEARCH QUERY...", label_visibility="collapsed")
if query_input:
    st.session_state.query = query_input

if st.button("INVESTIGATE_KNOWLEDGE", type="primary"):
    if st.session_state.query:
        st.session_state.trace_logs = []
        st.session_state.agent_output = None
        
        with st.status("EXECUTING_MULTI_AGENT_PIPELINE...", expanded=True) as status:
            final_result = {}
            for step in run_kortex_agent(st.session_state.query):
                node_name = list(step.keys())[0]
                node_data = step[node_name]
                
                status.write(f"**{node_name.upper()}**: PROCESSING...")
                
                if "trace" in node_data:
                    st.session_state.trace_logs.extend(node_data["trace"])
                
                for k, v in node_data.items():
                    if k != "trace":
                        final_result[k] = v
                time.sleep(0.1)
            
            status.update(label="PIPELINE_SUCCESS", state="complete")
        
        st.session_state.agent_output = final_result
        st.rerun()
    else:
        st.warning("EMPTY_QUERY_FIELD")

# --- RESULTS GRID ---
if st.session_state.agent_output:
    st.divider()
    col_activity, col_response = st.columns([1.5, 3])
    
    with col_activity:
        st.markdown("<p class='dashboard-label'>AGENT_ACTIVITY_TRACE</p>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='dashboard-box' style='min-height:450px;'>", unsafe_allow_html=True)
            for log in st.session_state.trace_logs:
                st.markdown(f"<div class='trace-line'>> {log}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with col_response:
        st.markdown("<p class='dashboard-label'>RESPONSE_SYNTHESIS</p>", unsafe_allow_html=True)
        res = st.session_state.agent_output
        
        with st.container():
            st.markdown("<div class='dashboard-box' style='min-height:450px;'>", unsafe_allow_html=True)
            
            if res.get("status") == "escalated":
                st.error(f"ESCALATION_TRIGGERED: {res.get('reason', 'LOW_CONFIDENCE')}")
                st.markdown("<div class='escalation-box'>SYSTEM_UNCERTAIN // REDIRECTING_TO_HUMAN_ENGINEER</div>", unsafe_allow_html=True)
            else:
                st.markdown("#### GENERATED_ANSWER")
                st.write(res.get('answer', 'NO_DATA_GENERATED'))
                
                st.divider()
                
                # Sources & Stats Row
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<p class='dashboard-label'>SOURCES_MAPPED</p>", unsafe_allow_html=True)
                    if res.get("context"):
                        seen = set()
                        for ctx in res["context"]:
                            sid = ctx.get("source", "UNK")
                            if sid not in seen:
                                st.markdown(f"<p style='font-size:0.75rem; border-bottom:1px solid #eee;'>ID: {sid} // TYPE: {ctx.get('type','DOC')}</p>", unsafe_allow_html=True)
                                seen.add(sid)
                    else:
                        st.caption("NO_SOURCES_CITED")

                with c2:
                    st.markdown("<p class='dashboard-label'>RELIABILITY_METRICS</p>", unsafe_allow_html=True)
                    conf = res.get("confidence", 0.0)
                    st.metric("CONFIDENCE_SCORE", f"{int(conf*100)}%")
                    if conf < 0.5:
                        st.warning("LOW_RELIABILITY_WARNING")
            
            st.markdown("</div>", unsafe_allow_html=True)

else:
    if not query_input:
        st.divider()
        st.markdown("""
            <div class='dashboard-box' style='text-align:center; padding:100px; opacity:0.4;'>
                SYSTEM_READY_FOR_INPUT<br>
                ENTER_QUERY_TO_INITIALIZE_AGENTIC_REASONING
            </div>
        """, unsafe_allow_html=True)
