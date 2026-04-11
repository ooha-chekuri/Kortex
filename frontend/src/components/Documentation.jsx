import React, { useState, useEffect } from 'react';
import {
  House,
  BookOpen,
  Gear,
  Plugs,
  Warning,
  Database,
  Brain,
  ChartLine,
  CaretRight,
  Lightning,
  MagnifyingGlass,
  Ticket,
  ArrowsDownUp,
  ChatsCircle,
  ShieldCheck
} from '@phosphor-icons/react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#00ff41',
    primaryTextColor: '#000',
    primaryBorderColor: '#00ff41',
    lineColor: '#00ff41',
    secondaryColor: '#00d4ff',
    tertiaryColor: '#12121a',
    background: '#0a0a0f',
    mainBkg: '#12121a',
    nodeBorder: '#00ff41',
    clusterBkg: '#12121a',
    clusterBorder: '#1e1e2e',
    titleColor: '#00ff41',
    edgeLabelBackground: '#12121a'
  }
});

const docsSections = [
  {
    id: 'overview',
    title: '1. Overview',
    icon: BookOpen,
    content: `Kortex is an Agentic Enterprise Knowledge Copilot that combines multi-agent orchestration with RAG (Retrieval Augmented Generation) to answer employee queries about IT systems, documentation, and historical incidents.

Key Features:
• Multi-agent pipeline with XAI (Explainable AI)
• FAISS vector database for semantic search
• Cross-encoder reranking for precision
• Confidence-based decision making
• Source citation with evidence`
  },
  {
    id: 'architecture',
    title: '2. System Architecture',
    icon: ChartLine,
    diagram: `flowchart TB
      subgraph INPUT
        Q[User Query]
      end
      
      subgraph AGENTS
        T[Triage<br/>Agent] --> R[Retrieval<br/>Agent]
        T --> K[Ticket<br/>Agent]
        R --> RR[Reranker<br/>Agent]
        K --> RR
        RR --> S[Synthesis<br/>Agent]
        S --> V[Validator<br/>Agent]
      end
      
      subgraph OUTPUT
        V --> A[Answer]
        V --> SRC[Sources]
        V --> CONF[Confidence]
        V --> XAI[XAI Trace]
      end
      
      Q --> T
      A --> RESP[Response]
      
      style T fill:#ff6b00,color:#000
      style R fill:#00d4ff,color:#000
      style K fill:#9d00ff,color:#000
      style RR fill:#ffff00,color:#000
      style S fill:#00ff41,color:#000
      style V fill:#ff00ff,color:#000`,
    content: `Kortex uses a 6-stage agent pipeline:

1. [Lightning] Triage Agent
Analyzes query intent to determine search strategy
- docs: User needs documentation
- tickets: User needs historical incidents  
- both: User needs both

2. [MagnifyingGlass] Retrieval Agent
Searches FAISS vector database for document chunks
- Uses sentence-transformers embeddings
- Returns top-K semantically similar results

3. [Ticket] Ticket Agent
Searches historical support tickets
- Finds related incident resolutions

4. [ArrowsDownUp] Reranker Agent
Re-ranks results using cross-encoder
- Improves precision of top results

5. [ChatsCircle] Synthesis Agent
Generates LLM response with citations
- Grounds answer in retrieved context

6. [ShieldCheck] Validator Agent
Computes confidence score
- Formula: 0.4*retrieval + 0.35*reranker + 0.25*llm_self_eval`
  },
  {
    id: 'confidence',
    title: '3. Confidence Scoring',
    icon: Gear,
    content: `Kortex uses a weighted confidence formula:

confidence = (0.4 × retrieval_similarity) + (0.35 × reranker_score) + (0.25 × llm_self_eval)

Decision Thresholds:
• Respond (>= 0.5): Answer provided directly
• Retry (>= 0.35): Expand search and try again  
• Escalate (< 0.35): Forward to human engineer

This ensures we only provide answers when we have sufficient context evidence.`
  },
  {
    id: 'api',
    title: '4. API Reference',
    icon: Plugs,
    content: `POST /query
Request:
{
  "query": "How do I configure VPN?",
  "user_id": "demo", 
  "context_mode": "auto"
}

Response:
{
  "answer": "To configure VPN...",
  "sources": [{"doc": "vpn_setup.pdf", "page": 1}],
  "confidence": 0.75,
  "status": "success",
  "agent_trace": ["Triage Agent -> docs", ...],
  "xai_explanation": [{ "decision": "docs", "reason": "...", "confidence": "high" }, ...]
}

POST /ingest
Indexes all documents and tickets into FAISS

GET /health
Returns {"status": "ok"}`
  },
  {
    id: 'config',
    title: '5. Configuration',
    icon: Gear,
    content: `Environment variables in .env:

LLM Providers:
• KORTEX_LLM_PROVIDER=ollama  (Options: gemini, openai, ollama, groq)
• KORTEX_LLM_MODEL=llama3.2:3b

API Keys:
• GEMINI_API_KEY=your_key
• OPENAI_API_KEY=your_key  
• GROQ_API_KEY=your_key

Ollama:
• OLLAMA_HOST=http://localhost:11434`
  },
  {
    id: 'troubleshooting',
    title: '6. Troubleshooting',
    icon: Warning,
    content: `Issue: "No context chunks retrieved"
Solution: Run POST /ingest to index data

Issue: "LLM quota exceeded"  
Solution: Switch to ollama or add API key

Issue: "Low confidence escalation"
Solution: Add more relevant documents to docs/ folder

Issue: "Ollama not connecting"
Solution: Run 'ollama serve' and 'ollama pull llama3'`
  },
  {
    id: 'data',
    title: '7. Data Sources',
    icon: Database,
    content: `Kortex supports three data sources:

Option A: Public IT Documentation
• Apache Kafka docs
• Kubernetes docs  
• Docker docs
• Python/FastAPI docs

Option B: Sample Corporate Data
• 26 SOP PDFs (VPN, Password Reset, etc.)
• 250 IT Support Tickets
(Generated automatically in data/synthetic/)

Option C: Custom Data
• Add PDFs to docs/ folder
• Add CSV tickets to backend/data/sample_tickets.csv
• Run POST /ingest to index`
  },
  {
    id: 'xai',
    title: '8. Explainable AI (XAI)',
    icon: Brain,
    content: `Every agent decision includes human-readable explanations:

Triage: Shows which keywords triggered intent
Retrieval: Shows similarity scores and result counts  
Reranker: Shows cross-encoder relevance scores
Synthesis: Shows if LLM fallback was used
Validator: Shows confidence formula breakdown

The XAI panel displays:
• WHY each decision was made
• What factors contributed
• Confidence scores at each step
• The formula used for calculations`
  }
];

export default function Documentation() {
  const [activeSection, setActiveSection] = useState('overview');
  const [expandedSections, setExpandedSections] = useState({});

  useEffect(() => {
    mermaid.run();
  }, [activeSection]);

  const toggleSection = (id) => {
    setExpandedSections(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  return (
    <div className="min-h-screen px-4 py-8 md:px-8 relative overflow-hidden" style={{ background: '#0a0a0f' }}>
      {/* Scanline effect */}
      <div className="fixed inset-0 pointer-events-none opacity-5" style={{
        background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, #00ff41 2px, #00ff41 4px)',
        zIndex: 9999
      }} />
      
      <div className="mx-auto max-w-7xl relative z-10">
        {/* Header */}
        <header className="mb-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold" style={{ 
            fontFamily: '"Departure Mono", monospace',
            color: '#00ff41',
            textShadow: '0 0 30px rgba(0,255,65,0.5)'
          }}>
            KORTEX DOCUMENTATION
          </h1>
          <p className="mt-4 text-lg" style={{ color: '#888', fontFamily: '"Departure Mono", monospace' }}>
            Enterprise Knowledge Copilot - Technical Reference
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          {/* Sidebar */}
          <nav className="space-y-2">
            {docsSections.map(section => {
              const Icon = section.icon;
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className="w-full text-left px-4 py-3 rounded-lg transition-all flex items-center gap-3"
                  style={{
                    fontFamily: '"Departure Mono", monospace',
                    background: activeSection === section.id ? 'rgba(0,255,65,0.1)' : 'transparent',
                    border: `1px solid ${activeSection === section.id ? '#00ff41' : '#1e1e2e'}`,
                    color: activeSection === section.id ? '#00ff41' : '#888'
                  }}
                >
                  <Icon size={20} weight="fill" />
                  {section.title}
                </button>
              );
            })}
          </nav>

          {/* Content */}
          <main className="rounded-3xl border border-pixel-border bg-pixel-card p-6" style={{ fontFamily: '"Departure Mono", monospace' }}>
            {docsSections.map(section => {
              const Icon = section.icon;
              return (
                <div 
                  key={section.id}
                  className={activeSection === section.id ? 'block' : 'hidden'}
                >
                  <h2 className="text-2xl mb-4 flex items-center gap-3" style={{ color: '#00ff41' }}>
                    <Icon size={28} weight="fill" />
                    {section.title}
                  </h2>
                  
                  {/* Mermaid Diagram */}
                  {section.diagram && (
                    <div className="mb-6 p-4 rounded-lg bg-black/30 border border-pixel-border overflow-x-auto">
                      <div className="mermaid">
                        {section.diagram}
                      </div>
                    </div>
                  )}
                  
                  {/* Content */}
                  <pre className="whitespace-pre-wrap text-sm leading-relaxed" style={{ color: '#e0e0e0' }}>
                    {section.content}
                  </pre>
                </div>
              );
            })}
          </main>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-sm" style={{ color: '#444', fontFamily: '"Departure Mono", monospace' }}>
          <div className="flex items-center justify-center gap-4">
            <span style={{ color: '#00ff41' }}>◆</span>
            <span>Kortex v1.0 - Agentic Knowledge Copilot</span>
            <span style={{ color: '#00ff41' }}>◆</span>
          </div>
        </footer>
      </div>
    </div>
  );
}