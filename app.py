import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="KORTEX OS",
    layout="wide",
    page_icon="B",
    initial_sidebar_state="collapsed"
)

import time
import os
from pathlib import Path
import json

# Absolute imports from root
from src.agents.orchestrator import run_kortex_agent
from src.data.ingest import build_indices

# Custom CSS for Light Theme + Departure Mono Aesthetic
st.markdown("""
    <style>
    /* Load Departure Mono from GitHub via JSDelivr */
    @font-face {
        font-family: 'Departure Mono';
        src: url('https://cdn.jsdelivr.net/gh/lucas-dlevy/departure-mono@main/fonts/DepartureMono-Regular.woff2') format('woff2');
        font-weight: normal;
        font-style: normal;
    }

    /* Force Light Theme */
    :root {
        --primary-color: #4b49ff;
        --bg-color: #ffffff;
        --text-color: #000000;
        --border-color: #000000;
    }

    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
    }

    * {
        font-family: 'Departure Mono', monospace !important;
        text-transform: uppercase;
    }

    /* Container Styling (Thin Black Borders) */
    .kortex-box {
        border: 1px solid var(--border-color);
        padding: 15px;
        background-color: #ffffff;
        margin-bottom: 10px;
    }

    .kortex-sidebar-item {
        border: 1px solid var(--border-color);
        padding: 10px;
        margin-bottom: 10px;
        background-color: #ffffff;
        font-size: 0.8rem;
    }

    .kortex-label {
        font-size: 0.7rem;
        color: #555;
        margin-bottom: 3px;
    }

    .kortex-value {
        font-size: 1.8rem;
        font-weight: 700;
    }

    /* Header Styling */
    .kortex-header {
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 5px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }

    /* Button Styling */
    .stButton>button {
        border-radius: 0px !important;
        border: 1px solid var(--border-color) !important;
        background-color: #fff !important;
        color: #000 !important;
        font-weight: 700 !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        background-color: #000 !important;
        color: #fff !important;
    }
    .stButton>button[kind="primary"] {
        background-color: var(--primary-color) !important;
        color: #fff !important;
        border: 1px solid var(--border-color) !important;
    }

    /* Hide default elements */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Escalation Banner */
    .escalation-box {
        border: 2px dashed #ff0000;
        background-color: #fff0f0;
        color: #ff0000;
        padding: 15px;
        margin-top: 20px;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State
if 'agent_output' not in st.session_state: st.session_state.agent_output = None
if 'trace_logs' not in st.session_state: st.session_state.trace_logs = []
if 'query' not in st.session_state: st.session_state.query = ""

# Layout: 3 Columns
l_col, m_col, r_col = st.columns([1, 4, 1.5])

# --- LEFT SIDEBAR (TRIAGE.ENV) ---
with l_col:
    st.markdown("### B TRIAGE.ENV")
    st.markdown("<p class='kortex-label'>SELECT_TASK</p>", unsafe_allow_html=True)
    tasks = ["TASK 1: BEST EXP", "TASK 2: OVERFIT", "TASK 3: NEXT EXP", "TASK 4: EXPERIMENTS", "TASK 5: FAILED RUN"]
    for task in tasks:
        st.markdown(f"<div class='kortex-sidebar-item'>{task}</div>", unsafe_allow_html=True)
    
    st.markdown("<p class='kortex-label'>SUPPORT</p>", unsafe_allow_html=True)
    st.markdown("<div class='kortex-sidebar-item'>HOW TO USE / GUIDE</div>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div style='border: 1px dashed #000; padding: 10px; font-size: 0.6rem;'>ENGINE_VERSION: QWEN_2.5_72B</div>", unsafe_allow_html=True)

# --- MAIN CONTENT (REASONING ACTIVE) ---
with m_col:
    # Header
    st.markdown(f"""
        <div class='kortex-header'>
            <div>
                <h2 style='margin:0;'>KORTEX_OS: REASONING_ACTIVE</h2>
                <p style='margin:0; font-size:0.7rem; color:#666;'>GROUNDED_RETRIEVAL_MODE</p>
            </div>
            <div style='color:green; font-size:0.7rem;'>STATE: STATUS_OK_ACTIVE</div>
        </div>
    """, unsafe_allow_html=True)

    # Stats Row
    s1, s2, s3 = st.columns(3)
    with s1: st.markdown("<div class='kortex-box'><p class='kortex-label'>RETRIEVAL_COUNT</p><div class='kortex-value'>5.00</div></div>", unsafe_allow_html=True)
    with s2: st.markdown("<div class='kortex-box'><p class='kortex-label'>STEP_COUNTER</p><div class='kortex-value'>0 // 10</div></div>", unsafe_allow_html=True)
    with s3:
        conf = st.session_state.agent_output.get("confidence", 0.0) if st.session_state.agent_output else 0.0
        st.markdown(f"<div class='kortex-box'><p class='kortex-label'>AI_CONFIDENCE</p><div class='kortex-value'>{conf*100:.0f}%</div></div>", unsafe_allow_html=True)

    # Input Bar
    query_input = st.text_input("INPUT", value=st.session_state.query, placeholder="ENTER COMMAND OR QUERY...", label_visibility="collapsed")
    if query_input != st.session_state.query: st.session_state.query = query_input

    # Reasoning Ledger
    st.markdown("<div class='kortex-box' style='min-height: 400px;'>", unsafe_allow_html=True)
    if st.session_state.agent_output:
        out = st.session_state.agent_output
        if out.get("status") == "escalated":
            st.error(f"TASK_ESCALATED: {out.get('reason', 'CONFIDENCE_LOW')}")
        else:
            st.markdown("### RESPONSE_SYNTHESIS")
            st.write(out.get("answer", ""))
            
            st.markdown("<br><p class='kortex-label'>SOURCES_MAPPING</p>", unsafe_allow_html=True)
            if out.get("context"):
                for ctx in list({(c['source'], c['type']) for c in out['context']}):
                    st.markdown(f"<div style='font-size:0.7rem; border-bottom:1px solid #eee; padding:2px 0;'>ID: {ctx[0]} // TYPE: {ctx[1]}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; padding:50px; opacity:0.3;'>WAITING_FOR_SYSTEM_INPUT...</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- RIGHT SIDEBAR (ACTIONS / UPLOAD / INGEST) ---
with r_col:
    st.markdown("<p class='kortex-label'>ACTIONS</p>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='kortex-box'>", unsafe_allow_html=True)
        if st.button("INVESTIGATE", type="primary"):
            if st.session_state.query:
                st.session_state.trace_logs = []
                with st.status("EXECUTING_PIPELINE...", expanded=True) as status:
                    final = {}
                    for step in run_kortex_agent(st.session_state.query):
                        node = list(step.keys())[0]
                        status.write(f"AGENT_{node.upper()}: PROCESSING...")
                        for k, v in step[node].items():
                            if k != "trace": final[k] = v
                        time.sleep(0.1)
                    status.update(label="PIPELINE_COMPLETE", state="complete")
                st.session_state.agent_output = final
                st.rerun()
        if st.button("DISCARD"):
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p class='kortex-label'>UPLOAD_KNOWLEDGE</p>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='kortex-box'>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("FILES", type=["pdf", "txt", "md"], accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files:
            docs_path = Path("docs")
            docs_path.mkdir(exist_ok=True)
            for uploaded_file in uploaded_files:
                with open(docs_path / uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success(f"SAVED_{len(uploaded_files)}_FILES")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p class='kortex-label'>INGESTION_CONTROLS</p>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='kortex-box'>", unsafe_allow_html=True)
        if st.button("SYNC_KNOWLEDGE"):
            with st.spinner("SYNCING..."):
                stats = build_indices()
                st.success(f"OK: {stats['docs']} DOCS / {stats['tickets']} TIX")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p class='kortex-label'>SYSTEM_INFO</p>", unsafe_allow_html=True)
    st.markdown("<div class='kortex-box' style='font-size:0.6rem;'>CLUSTER_ID: K-880<br>LATENCY: 42MS<br>UPTIME: 99.9%</div>", unsafe_allow_html=True)
