import streamlit as st
import time
import os
from pathlib import Path
import json

# --- CORE CONFIGURATION (MUST BE FIRST) ---
st.set_page_config(
    page_title="KORTEX | Enterprise Knowledge Copilot",
    layout="wide",
    page_icon="🔷",
    initial_sidebar_state="expanded",
)

# Absolute imports from root
from src.agents.orchestrator import run_kortex_agent
from src.data.ingest import build_indices

# --- HIGH-FIDELITY FULL LIGHT THEME ---
st.markdown(
    """
    <style>
    @font-face {
        font-family: 'Departure Mono';
        src: url('https://cdn.jsdelivr.net/gh/lucas-dlevy/departure-mono@main/fonts/DepartureMono-Regular.woff2') format('woff2');
    }

    :root {
        --primary-color: #4b49ff;
        --bg-color: #ffffff;
        --text-color: #000000;
        --border-color: #000000;
    }

    .stApp { background-color: #ffffff !important; }
    
    /* Global Pure Dark Text */
    span, p, div, h1, h2, h3, h4, li, label, .stMarkdown, [data-testid="stMetricValue"], .stCaption {
        color: #000000 !important;
        font-family: 'Departure Mono', monospace !important;
    }

    .dashboard-box {
        border: 1px solid #000;
        padding: 20px;
        background-color: #fff;
        margin-bottom: 15px;
    }

    .dashboard-label {
        font-size: 0.7rem;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: block;
    }

    .stButton>button {
        border-radius: 0px !important;
        border: 1px solid #000 !important;
        background-color: #fff !important;
        color: #000 !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }
    .stButton>button[kind="primary"] {
        background-color: #4b49ff !important;
        color: #fff !important;
    }

    /* Pixel Agent Styling */
    .agent-stage {
        display: flex;
        justify-content: space-around;
        padding: 30px 0;
        background: #fff;
        border: 1px solid #000;
        margin-bottom: 20px;
    }
    .pixel-agent {
        text-align: center;
        transition: transform 0.3s;
    }
    .pixel-agent svg {
        width: 60px;
        height: 60px;
    }
    .active-agent {
        transform: scale(1.3);
        filter: drop-shadow(0 0 10px #4b49ff);
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1.3); }
        50% { transform: scale(1.4); }
        100% { transform: scale(1.3); }
    }
    .active-text {
        color: #4b49ff !important;
        font-size: 0.6rem;
        font-weight: bold;
        animation: blink 0.8s infinite;
    }
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# Pixel SVGs (Detailed Humanoid Pixel Style)
def get_pixel_icon(name, active=False):
    color = "#4b49ff" if active else "#000000"
    # Detailed Pixel Art SVGs (16x16 grid style)
    icons = {
        "TRIAGE": f'''<svg viewBox="0 0 16 16" fill="{color}">
            <path d="M6 0h4v2H6V0zm-2 2h8v2H4V2zm-2 2h12v2H2V4zM0 6h16v4H0V6zm2 4h12v2H2v-2zm2 2h8v2H4v-2zm2 2h4v2H6v-2z"/>
            <rect x="6" y="6" width="4" height="4" fill="white"/>
        </svg>''',
        "RETRIEVAL": f'''<svg viewBox="0 0 16 16" fill="{color}">
            <path d="M4 0h8v2H4V0zM2 2h12v2H2V2zM0 4h16v2H0V4zm0 4h16v2H0V8zm2 4h12v2H2v-2zm2 2h8v2H4v-2z"/>
            <rect x="4" y="6" width="8" height="2" fill="white"/>
        </svg>''',
        "SYNTHESIS": f'''<svg viewBox="0 0 16 16" fill="{color}">
            <path d="M2 0h12v2H2V0zm0 4h12v2H2V4zm0 4h12v2H2V8zm0 12h12v2H2v-2z"/>
            <path d="M4 2v12h8V2H4z" fill="white" opacity="0.3"/>
        </svg>''',
        "VALIDATOR": f'''<svg viewBox="0 0 16 16" fill="{color}">
            <path d="M8 0L0 8l8 8 8-8-8-8zM8 4l4 4-4 4-4-4 4-4z"/>
            <circle cx="8" cy="8" r="2" fill="white"/>
        </svg>''',
    }
    return icons.get(name, "")


def render_visualizer(active_node=""):
    st.markdown("<div class='agent-stage'>", unsafe_allow_html=True)
    cols = st.columns(4)
    nodes = ["TRIAGE", "RETRIEVAL", "SYNTHESIS", "VALIDATOR"]
    for i, name in enumerate(nodes):
        is_active = active_node.upper() in name
        with cols[i]:
            st.markdown(
                f"<div class='pixel-agent {'active-agent' if is_active else ''}'>{get_pixel_icon(name, is_active)}<div style='font-size:0.6rem; margin-top:5px;'>{name}</div></div>",
                unsafe_allow_html=True,
            )
            if is_active:
                st.markdown(
                    "<p class='active-text' style='text-align:center;'>TALKING...</p>",
                    unsafe_allow_html=True,
                )
    st.markdown("</div>", unsafe_allow_html=True)


def render_knowledge_graph(query, context):
    """SVG-based minimalist Knowledge Graph."""
    if not context:
        return

    # Simple SVG Graph
    width = 800
    height = 250
    query_node = (width / 2, 40)

    svg = f'<svg width="100%" viewBox="0 0 {width} {height}" style="background:#fff; border:1px solid #000; margin-bottom:15px;">'

    # Draw Lines
    for i, item in enumerate(context):
        x = (i + 1) * (width / (len(context) + 1))
        y = 180
        svg += f'<line x1="{query_node[0]}" y1="{query_node[1]}" x2="{x}" y2="{y}" stroke="#4b49ff" stroke-width="1.5" opacity="0.4" />'

    # Query Node
    svg += f'<rect x="{query_node[0] - 40}" y="{query_node[1] - 15}" width="80" height="30" fill="#4b49ff" stroke="#000" />'
    svg += f'<text x="{query_node[0]}" y="{query_node[1] + 5}" fill="#fff" font-size="10" text-anchor="middle" font-family="Departure Mono">QUERY</text>'

    # Context Nodes
    for i, item in enumerate(context):
        x = (i + 1) * (width / (len(context) + 1))
        y = 180
        is_doc = item.get("source_type") == "doc"
        color = "#000" if is_doc else "#444"
        label = item.get("doc", item.get("ticket_id", "UNK"))

        # Node Shape
        if is_doc:
            svg += f'<rect x="{x - 35}" y="{y - 15}" width="70" height="30" fill="#fff" stroke="{color}" />'
        else:
            svg += f'<path d="M{x - 35} {y - 15} L{x + 35} {y - 15} L{x + 25} {y + 15} L{x - 25} {y + 15} Z" fill="#fff" stroke="{color}" />'

        svg += f'<text x="{x}" y="{y + 5}" fill="#000" font-size="8" text-anchor="middle" font-family="Departure Mono">{label[:12]}</text>'
        svg += f'<text x="{x}" y="{y + 25}" fill="#4b49ff" font-size="7" text-anchor="middle" font-family="Departure Mono">{int(item.get("reranker_score", 0) * 100)}% REL</text>'

    svg += "</svg>"
    st.markdown(
        "<p class='dashboard-label'>NEURAL_KNOWLEDGE_NETWORK</p>",
        unsafe_allow_html=True,
    )
    st.markdown(svg, unsafe_allow_html=True)


# Session Initialization
if "agent_output" not in st.session_state:
    st.session_state.agent_output = None
if "trace_logs" not in st.session_state:
    st.session_state.trace_logs = []
if "query" not in st.session_state:
    st.session_state.query = ""

with st.sidebar:
    st.markdown("### 🔷 SYSTEM_ADMIN")

    # API Key Handling
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "GEMINI_API_KEY", value=env_key, type="password", placeholder="ENTER KEY..."
    )
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    st.divider()
    st.markdown("#### 📁 DEMO_INPUTS")
    st.info(
        "Technical docs are in `/demo/inputs/docs` and Tickets are in `/demo/inputs/tickets`."
    )

    uploaded_files = st.file_uploader(
        "UPLOAD_FILES",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded_files:
        docs_path = Path("docs")
        docs_path.mkdir(exist_ok=True)
        for f in uploaded_files:
            with open(docs_path / f.name, "wb") as file:
                file.write(f.getbuffer())
        st.success(f"SAVED_{len(uploaded_files)}_FILES")

    if st.button("SYNC_KNOWLEDGE_BASE"):
        with st.spinner("ANALYZING..."):
            stats = build_indices()
            st.success(f"OK: {stats['docs']} DOCS / {stats['tickets']} TIX")
    st.divider()

    # Demo Mode Button
    st.markdown("#### 🎯 DEMO_MODE")
    demo_queries = [
        "How do I reset my password?",
        "What is the VPN access policy?",
        "How to deploy Kafka?",
        "What is the incident response procedure?",
        "Tell me about the Kubernetes onboarding",
    ]
    selected_query = st.selectbox(
        "SELECT_DEMO_QUERY",
        options=[""] + demo_queries,
        format_func=lambda x: "Choose..." if x == "" else x,
    )
    if selected_query:
        st.session_state.query = selected_query
        st.rerun()

    st.divider()

    # Documentation Button
    st.markdown("#### 📖 PLATFORM_DOCS")
    if st.button("SHOW_ARCHITECTURE"):
        st.session_state.show_docs = not st.session_state.get("show_docs", False)

    if st.button("OPEN_FULL_DOCS"):
        # Open the full docs markdown file
        import webbrowser

        webbrowser.open("docs/PLATFORM.md")

    if st.session_state.get("show_docs", False):
        with st.expander("🏗️ System Architecture", expanded=True):
            st.markdown("""
## Kortex Architecture

```
User Query
    ↓
Triage Agent (Intent Classification)
    ↓
Retrieval Agent (FAISS + Documents)
    ↓
Ticket Agent (Historical Tickets)
    ↓
Reranker Agent (Cross-Encoder)
    ↓
Synthesis Agent (LLM Generation)
    ↓
Validator Agent (Confidence Scoring)
    ↓
Answer / Escalate
```

### Confidence Formula
```
Confidence = (0.5 × Retrieval) + (0.3 × Reranker) + (0.2 × LLM Self-Eval)
```

### Decision Logic
| Confidence | Decision |
|------------|----------|
| > 0.75 | Return Answer |
| 0.5-0.75 | Retry/Search |
| < 0.5 | Escalate |
""")

        with st.expander("🔄 Agent Workflow", expanded=True):
            st.markdown("""
## Multi-Agent Orchestration

1. **Triage**: Classifies query as docs/tickets/both
2. **Retrieval**: Searches FAISS vector DB
3. **Rerank**: Uses cross-encoder for precision
4. **Synthesize**: Generates answer with LLM
5. **Validate**: Computes confidence score
""")

    st.divider()
    if st.button("RESET_SESSION"):
        st.session_state.clear()
        st.rerun()

    st.divider()

    # Documentation Button
    st.markdown("#### 📖 PLATFORM_DOCS")

    # Show inline docs
    if st.button("SHOW_ARCHITECTURE"):
        st.session_state.show_docs = not st.session_state.get("show_docs", False)

    if st.session_state.get("show_docs", False):
        with st.expander("🏗️ System Architecture", expanded=True):
            st.markdown("""
## Kortex Architecture

```
User Query
    ↓
Triage Agent (Intent Classification)
    ↓
Retrieval Agent (FAISS + Documents)
    ↓
Ticket Agent (Historical Tickets)
    ↓
Reranker Agent (Cross-Encoder)
    ↓
Synthesis Agent (LLM Generation)
    ↓
Validator Agent (Confidence Scoring)
    ↓
Answer / Escalate
```

### Confidence Formula
```
Confidence = (0.5 × Retrieval) + (0.3 × Reranker) + (0.2 × LLM Self-Eval)
```

### Decision Logic
| Confidence | Decision |
|------------|----------|
| > 0.75 | Return Answer |
| 0.5-0.75 | Retry/Search |
| < 0.5 | Escalate |
""")

        with st.expander("🔄 Agent Workflow", expanded=True):
            st.markdown("""
## Multi-Agent Orchestration

1. **Triage**: Classifies query as docs/tickets/both
2. **Retrieval**: Searches FAISS vector DB
3. **Rerank**: Uses cross-encoder for precision
4. **Synthesize**: Generates answer with LLM
5. **Validate**: Computes confidence score
""")

    st.divider()
    if st.button("RESET_SESSION"):
        st.session_state.clear()
        st.rerun()

st.markdown("## 🔷 KORTEX // ENTERPRISE_COPILOT")
st.markdown(
    "<p style='font-size:0.8rem; opacity:0.6; color:#000 !important;'>AGENTIC_REASONING_ACTIVE // GROUNDED_RETRIEVAL_MODE</p>",
    unsafe_allow_html=True,
)

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs(["🔍 QUERY", "🎯 DEMO", "📖 DOCS"])

with tab1:
    st.markdown("<p class='dashboard-label'>QUERY_INPUT</p>", unsafe_allow_html=True)
    query_input = st.text_input(
        "INPUT",
        value=st.session_state.query,
        placeholder="ENTER COMMAND...",
        label_visibility="collapsed",
    )
    if query_input:
        st.session_state.query = query_input

    col_go, col_clear = st.columns([1, 1])
    with col_go:
        if st.button("INVESTIGATE_KNOWLEDGE", type="primary"):
            if st.session_state.query:
                st.session_state.trace_logs = []
                st.session_state.agent_output = None
                viz_placeholder = st.empty()

                try:
                    with st.status("EXECUTING_PIPELINE...", expanded=True) as status:
                        final_result = {}
                        for step in run_kortex_agent(st.session_state.query):
                            node_name = list(step.keys())[0]
                            node_data = step[node_name]
                            with viz_placeholder.container():
                                render_visualizer(active_node=node_name)
                            status.write(f"**{node_name.upper()}**: PROCESSING...")
                            if "trace" in node_data:
                                st.session_state.trace_logs.extend(node_data["trace"])
                            for k, v in node_data.items():
                                if k != "trace":
                                    final_result[k] = v
                            time.sleep(0.4)
                    status.update(label="PIPELINE_SUCCESS", state="complete")
                    st.session_state.agent_output = final_result
                except Exception as e:
                    st.error(f"PIPELINE_ERROR: {str(e)}")
                    st.session_state.agent_output = {
                        "status": "error",
                        "answer": "The system encountered a pipeline error. Check LLM/Connectivity.",
                    }
                st.rerun()
    with col_clear:
        if st.button("CLEAR"):
            st.session_state.query = ""
            st.session_state.agent_output = None
            st.session_state.trace_logs = []
            st.rerun()

with tab2:
    st.markdown("### 🎯 Select a Demo Query")
    st.markdown("Click any query below to auto-fill and run:")

    demo_queries = [
        ("How do I reset my password?", "Password management SOP"),
        ("What is the VPN access policy?", "Remote access policy"),
        ("How to deploy Kafka?", "Kafka deployment guide"),
        ("What is the incident response procedure?", "Security incidents"),
        ("Tell me about the Kubernetes onboarding", "DevOps onboarding"),
        ("What are the Docker standards?", "Container standards"),
        ("How do I request software installation?", "IT request process"),
        ("What's the remote work policy?", "HR policies"),
    ]

    for i, (query, desc) in enumerate(demo_queries):
        st.markdown(f"**{i + 1}. {query}**")
        st.caption(f"_{desc}_")
        if st.button(f"RUN #{i + 1}", key=f"demo_{i}"):
            st.session_state.query = query
            st.session_state.trace_logs = []
            st.session_state.agent_output = None

            viz_placeholder = st.empty()
            try:
                with st.status("EXECUTING_DEMO...", expanded=True) as status:
                    final_result = {}
                    for step in run_kortex_agent(query):
                        node_name = list(step.keys())[0]
                        node_data = step[node_name]
                        with viz_placeholder.container():
                            render_visualizer(active_node=node_name)
                        status.write(f"**{node_name.upper()}**: PROCESSING...")
                        if "trace" in node_data:
                            st.session_state.trace_logs.extend(node_data["trace"])
                        for k, v in node_data.items():
                            if k != "trace":
                                final_result[k] = v
                        time.sleep(0.4)
                    status.update(label="DEMO_COMPLETE", state="complete")
                    st.session_state.agent_output = final_result
            except Exception as e:
                st.error(f"Error: {str(e)}")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Expected Demo Outcomes")
    st.markdown("""
    | Query | Expected Confidence | Shows |
    |-------|-------------------|-------|
    | Password reset | > 0.75 | Answer + Sources |
    | VPN policy | > 0.75 | Answer + Trace |
    | Kafka deploy | > 0.75 | Multi-source |
    | Unknown query | < 0.5 | Escalation |
    """)

with tab3:
    st.markdown("### 📖 Platform Documentation")

    st.markdown("""
    ## 🏗️ System Architecture
    
    ```
    User Query
        ↓
    Triage Agent → Intent Classification
        ↓
    Retrieval Agent → FAISS + Documents
        ↓
    Ticket Agent → Historical Tickets  
        ↓
    Reranker Agent → Cross-Encoder
        ↓
    Synthesis Agent → LLM Generation
        ↓
    Validator Agent → Confidence Scoring
        ↓
    Answer / Escalate
    ```
    
    ### Confidence Formula (PRD)
    ```
    Confidence = (0.5 × Retrieval) 
                + (0.3 × Reranker) 
                + (0.2 × LLM Self-Eval)
    ```
    
    ### Decision Matrix
    | Confidence | Decision |
    |------------|----------|
    | > 0.75 | **ANSWER** |
    | 0.5-0.75 | **RETRY** |
    | < 0.5 | **ESCALATE** |
    """)

    st.markdown("---")
    st.markdown("""
    ## 🔧 Tech Stack
    
    | Layer | Technology |
    |-------|------------|
    | Frontend | Streamlit |
    | Backend | FastAPI |
    | AI/ML | Gemini 2.5 Flash |
    | Embeddings | Sentence Transformers |
    | Vector DB | FAISS |
    | Reranking | Cross-Encoder |
    """)

    st.markdown("---")
    st.markdown("""
    ## 📁 Demo Data Structure
    
    ```
    demo/inputs/
    ├── docs/        (30 SOP documents)
    └── tickets/     (300 IT tickets)
    ```
    """)

if st.session_state.agent_output:
    st.divider()
    col1, col2 = st.columns([1.5, 3])
    with col1:
        st.markdown(
            "<p class='dashboard-label'>AGENT_ACTIVITY_TRACE</p>",
            unsafe_allow_html=True,
        )
        with st.container():
            st.markdown(
                "<div class='dashboard-box' style='height:750px; overflow-y:auto;'>",
                unsafe_allow_html=True,
            )
            for log in st.session_state.trace_logs:
                st.markdown(
                    f"<div style='font-size:0.8rem; border-bottom:1px solid #eee; padding:5px 0; color:#000 !important;'>{log}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        res = st.session_state.agent_output
        render_knowledge_graph(st.session_state.query, res.get("context", []))

        confidence_val = res.get("confidence", 0)
        confidence_pct = int(confidence_val * 100)
        conf_color = (
            "#22c55e"
            if confidence_pct >= 70
            else "#f59e0b"
            if confidence_pct >= 40
            else "#ef4444"
        )
        conf_label = "ANSWER" if confidence_val >= 0.5 else "ESCALATE"

        st.markdown(
            f"""
        <div style="border:1px solid #000; padding:20px; margin-bottom:15px; background:#fff;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                <span style="font-size:0.7rem; font-weight:bold; text-transform:uppercase; background:{conf_color}; color:#fff; padding:4px 12px;">{conf_label}</span>
                <span style="font-size:0.8rem; color:#000;">CONFIDENCE: {confidence_pct}%</span>
            </div>
            <div style="font-size:0.9rem; line-height:1.6; color:#000 !important;">{res.get("answer", "NO_DATA")}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p class='dashboard-label'>SOURCES_REFERENCED</p>", unsafe_allow_html=True
        )
        if res.get("context"):
            for ctx in res["context"]:
                src_type = ctx.get("source_type", "UNKNOWN")
                src_badge = "DOC" if src_type == "doc" else "TICKET"
                src_id = ctx.get("doc", ctx.get("ticket_id", "UNK"))
                rel_score = int(ctx.get("reranker_score", 0) * 100)
                preview = (
                    ctx.get("text", "")[:100] + "..."
                    if len(ctx.get("text", "")) > 100
                    else ctx.get("text", "")
                )
                st.markdown(
                    f"""
                <div style="border:1px solid #ccc; padding:12px; margin:8px 0; background:#fafafa;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <span style="font-size:0.7rem; font-weight:bold; color:#4b49ff;">{src_badge}</span>
                        <span style="font-size:0.7rem; color:#666;">{rel_score}% REL</span>
                    </div>
                    <div style="font-size:0.75rem; font-weight:bold; color:#000; margin-bottom:4px;">{src_id}</div>
                    <div style="font-size:0.7rem; color:#444; font-style:italic;">{preview}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("NO_SOURCES_CITED")
else:
    if not query_input:
        st.divider()
        st.markdown(
            "<div class='dashboard-box' style='text-align:center; padding:100px; opacity:0.4;'>SYSTEM_READY</div>",
            unsafe_allow_html=True,
        )
