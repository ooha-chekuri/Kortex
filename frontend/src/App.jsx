import { useEffect, useRef, useState } from "react";
import { House, BookOpen } from '@phosphor-icons/react';
import AgentActivityPanel from "./components/AgentActivityPanel";
import QueryInput from "./components/QueryInput";
import ResponsePanel from "./components/ResponsePanel";
import Documentation from "./components/Documentation";
import { AgentPipeline, PixelDecoration } from "./components/PixelAgent";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

const demoQueries = [
  "How do I fix Kafka consumer lag after a deployment?",
  "Why would a Kubernetes pod enter CrashLoopBackOff after a config change?",
  "What past incidents mention SSO login loops or auth callback issues?",
];

export default function App() {
  const [query, setQuery] = useState(demoQueries[0]);
  const [result, setResult] = useState(null);
  const [visibleTrace, setVisibleTrace] = useState([]);
  const [xaiExplanation, setXaiExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');
  const timeoutsRef = useRef([]);

  useEffect(() => {
    return () => {
      timeoutsRef.current.forEach((timeoutId) => window.clearTimeout(timeoutId));
    };
  }, []);

  const revealTrace = (trace) => {
    timeoutsRef.current.forEach((timeoutId) => window.clearTimeout(timeoutId));
    timeoutsRef.current = [];
    setVisibleTrace([]);

    trace.forEach((item, index) => {
      // Update active agent
      const timeoutId = window.setTimeout(() => {
        setActiveAgent(getAgentType(item));
        setVisibleTrace((current) => [...current, item]);
      }, index * 600);
      timeoutsRef.current.push(timeoutId);
    });
  };

  const getAgentType = (traceStep) => {
    const step = traceStep.toLowerCase();
    if (step.includes('triage')) return 'triage';
    if (step.includes('retrieval')) return 'retrieval';
    if (step.includes('ticket')) return 'ticket';
    if (step.includes('rerank')) return 'reranker';
    if (step.includes('synthes')) return 'synthesis';
    if (step.includes('valid')) return 'validator';
    return null;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);
    setVisibleTrace([]);
    setActiveAgent(null);

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          user_id: "demo",
          context_mode: "auto",
        }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Kortex request failed.");
      }

      setResult(payload);
      setXaiExplanation(payload.xai_explanation || null);
      revealTrace(payload.agent_trace || []);
    } catch (error) {
      setResult({
        status: "escalated",
        reason: error.message,
        suggestion: "Check the backend server, model provider, and index files.",
        confidence: 0,
        sources: [],
        agent_trace: ["Frontend -> Request failed before completion"],
      });
      revealTrace(["Frontend -> Request failed before completion"]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen px-4 py-8 md:px-8 relative overflow-hidden">
      <PixelDecoration />
      
      <div className="mx-auto max-w-7xl relative z-10">
        {/* Navigation */}
        <nav className="mb-6 flex justify-center gap-4">
          <button
            onClick={() => setCurrentPage('home')}
            className="px-4 py-2 rounded-lg transition-all flex items-center gap-2"
            style={{
              fontFamily: '"Departure Mono", monospace',
              background: currentPage === 'home' ? 'rgba(0,255,65,0.2)' : 'transparent',
              border: `1px solid ${currentPage === 'home' ? '#00ff41' : '#1e1e2e'}`,
              color: currentPage === 'home' ? '#00ff41' : '#666'
            }}
          >
            <House size={18} weight="fill" />
            HOME
          </button>
          <button
            onClick={() => setCurrentPage('docs')}
            className="px-4 py-2 rounded-lg transition-all flex items-center gap-2"
            style={{
              fontFamily: '"Departure Mono", monospace',
              background: currentPage === 'docs' ? 'rgba(0,255,65,0.2)' : 'transparent',
              border: `1px solid ${currentPage === 'docs' ? '#00ff41' : '#1e1e2e'}`,
              color: currentPage === 'docs' ? '#00ff41' : '#666'
            }}
          >
            <BookOpen size={18} weight="fill" />
            DOCUMENTATION
          </button>
        </nav>

        {currentPage === 'home' ? (
          <>
            <header className="mb-8 space-y-4 text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.32em]" style={{ color: '#00ff41', fontFamily: '"Departure Mono", monospace' }}>
                Kortex v1.0
              </p>
              <h1 className="font-display text-4xl text-white md:text-6xl" style={{ fontFamily: '"Departure Mono", monospace', textShadow: '0 0 20px rgba(0, 255, 65, 0.5)' }}>
                AGENTIC KNOWLEDGE COPILOT
              </h1>
              <p className="mx-auto max-w-3xl text-base" style={{ color: '#888', fontFamily: '"Departure Mono", monospace' }}>
                {'>'} Multi-agent RAG pipeline with confidence-based decision making
              </p>
            </header>

            {/* Agent Pipeline Visualization */}
            <div className="mb-8">
              <AgentPipeline activeAgent={activeAgent} trace={visibleTrace} />
            </div>

            <QueryInput value={query} onChange={setQuery} onSubmit={handleSubmit} loading={loading} />

            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {demoQueries.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => setQuery(item)}
                  className="rounded px-4 py-2 text-sm transition-all hover:scale-105"
                  style={{ 
                    border: '1px solid #00d4ff', 
                    color: '#00d4ff',
                    fontFamily: '"Departure Mono", monospace',
                    background: 'rgba(0, 212, 255, 0.1)'
                  }}
                >
                  {item}
                </button>
              ))}
            </div>

            <section className="mt-8 grid gap-6 lg:grid-cols-[1fr,1.2fr]">
              <AgentActivityPanel trace={visibleTrace} loading={loading} xaiExplanation={xaiExplanation} />
              <ResponsePanel result={result} loading={loading} />
            </section>
          </>
        ) : (
          <Documentation />
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-xs" style={{ color: '#444', fontFamily: '"Departure Mono", monospace' }}>
          <div className="flex items-center justify-center gap-4">
            <span style={{ color: '#00ff41' }}>◆</span>
            <span>Kortex Agentic Knowledge Copilot</span>
            <span style={{ color: '#00ff41' }}>◆</span>
            <span>v1.0</span>
            <span style={{ color: '#00ff41' }}>◆</span>
          </div>
        </footer>
      </div>
    </main>
  );
}