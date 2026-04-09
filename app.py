import streamlit as st
import time
import os
from pathlib import Path
from src.agents.orchestrator import run_kortex_agent
from src.data.ingest import build_indices
import json

# Enforce light theme and wide layout MUST BE FIRST
st.set_page_config(page_title="KORTEX_OS", layout="wide", page_icon="B")

# Custom CSS: Strict Light Theme + Departure Mono (Mimicking OS wireframe)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase;
        color: #000000;
    }

    body, .stApp {
        background-color: #ffffff !important;
    }

    /* Container Styling (Thin Black Borders) */
    .kortex-box {
        border: 1px solid #000000;
        padding: 15px;
        background-color: #ffffff;
        margin-bottom: 10px;
    }

    .kortex-sidebar-item {
        border: 1px solid #000000;
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
        border-bottom: 2px solid #000;
        padding-bottom: 5px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }

    /* Button Styling */
    .stButton>button {
        border-radius: 0px !important;
        border: 1px solid #000 !important;
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
        background-color: #4b49ff !important;
        color: #fff !important;
        border: 1px solid #000 !important;
    }

    /* Hide default elements */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Session State
if 'agent_output' not in st.session_state: st.session_state.agent_output = None
if 'trace_logs' not in st.session_state: st.session_state.trace_logs = []
if 'query' not in st.session_state: st.session_state.query = ""

# Layout
l_col, m_col, r_col = st.columns([1, 4, 1.5])

# LEFT SIDEBAR
with l_col:
    st.markdown("### 🔷 TRIAGE.ENV")
    st.markdown("<p class='kortex-label'>SELECT_TASK</p>", unsafe_allow_html=True)
    for task in ["TASK 1: BEST EXP", "TASK 2: OVERFIT", "TASK 3: NEXT EXP"]:
        st.markdown(f"<div class='kortex-sidebar-item'>{task}</div>", unsafe_allow_html=True)
    
    st.markdown("<p class='kortex-label'>SUPPORT</p>", unsafe_allow_html=True)
    st.markdown("<div class='kortex-sidebar-item'>HOW TO USE / GUIDE</div>", unsafe_allow_html=True)

# MAIN CONTENT
with m_col:
    # Header
    st.markdown(f"""
        <div class='kortex-header'>
            <h2 style='margin:0;'>KORTEX_OS: REASONING_ACTIVE</h2>
            <div style='color:green; font-size:0.7rem;'>STATE: STATUS_OK</div>
        </div>
    """, unsafe_allow_html=True)

    # Top Row Stats
    s1, s2, s3 = st.columns(3)
    with s1: st.markdown("<div class='kortex-box'><p class='kortex-label'>QUERY_CONTEXT</p><div class='kortex-value'>LOCAL_RAG</div></div>", unsafe_allow_html=True)
    with s2: st.markdown("<div class='kortex-box'><p class='kortex-label'>STEP_COUNTER</p><div class='kortex-value'>0 // 10</div></div>", unsafe_allow_html=True)
    with s3:
        conf = st.session_state.agent_output.get("confidence", 0.0) if st.session_state.agent_output else 0.0
        st.markdown(f"<div class='kortex-box'><p class='kortex-label'>AI_CONFIDENCE</p><div class='kortex-value'>{conf*100:.0f}%</div></div>", unsafe_allow_html=True)

    # Search Bar
    query_input = st.text_input("INPUT", value=st.session_state.query, placeholder="ENTER COMMAND OR QUERY...", label_visibility="collapsed")
    if query_input != st.session_state.query: st.session_state.query = query_input

    # Response Area
    st.markdown("<div class='kortex-box' style='min-height: 400px;'>", unsafe_allow_html=True)
    if st.session_state.agent_output:
        out = st.session_state.agent_output
        if out.get("status") == "escalated":
            st.error(f"TASK_ESCALATED: {out.get('reason', 'Confidence below threshold')}")
        else:
            st.markdown("### RESPONSE_SYNTHESIS")
            st.write(out.get("answer", ""))
            
            st.markdown("<br><p class='kortex-label'>SOURCES_MAPPING</p>", unsafe_allow_html=True)
            if out.get("context"):
                for ctx in list({(c['source'], c['type']) for c in out['context']}):
                    st.markdown(f"<div style='font-size:0.7rem;'>ID: {ctx[0]} // TYPE: {ctx[1]}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; padding:50px; opacity:0.3;'>WAITING_FOR_INPUT...</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# RIGHT SIDEBAR
with r_col:
    st.markdown("<p class='kortex-label'>ACTIONS</p>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='kortex-box'>", unsafe_allow_html=True)
        if st.button("INVESTIGATE", type="primary"):
            if st.session_state.query:
                st.session_state.trace_logs = []
                with st.status("RUNNING_AGENTS...", expanded=True) as status:
                    final = {}
                    for step in run_kortex_agent(st.session_state.query):
                        node = list(step.keys())[0]
                        status.write(f"NODE_{node.upper()}: PROCESSING...")
                        for k, v in step[node].items():
                            if k != "trace": final[k] = v
                        time.sleep(0.1)
                    status.update(label="PIPELINE_OK", state="complete")
                st.session_state.agent_output = final
                st.rerun()
        if st.button("DISCARD"):
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p class='kortex-label'>UPLOAD_KNOWLEDGE</p>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='kortex-box'>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("UPLOAD_FILES", type=["pdf", "txt", "md"], accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files:
            docs_path = Path("docs")
            docs_path.mkdir(exist_ok=True)
            for uploaded_file in uploaded_files:
                with open(docs_path / uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success(f"SAVED_{len(uploaded_files)}_FILES")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p class='kortex-label'>INGESTION</p>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='kortex-box'>", unsafe_allow_html=True)
        if st.button("SYNC_KNOWLEDGE"):
            with st.spinner("INGESTING..."):
                stats = build_indices()
                st.success(f"OK: {stats['docs']} DOCS / {stats['tickets']} TIX")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p class='kortex-label'>SYSTEM_INFO</p>", unsafe_allow_html=True)
    st.markdown("<div class='kortex-box' style='font-size:0.6rem;'>VERSION: 2.0.0-STABLE<br>LATENCY: 12MS<br>STATE: ENCRYPTED</div>", unsafe_allow_html=True)
