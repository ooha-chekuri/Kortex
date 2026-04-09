import { useEffect, useRef, useState } from "react";
import AgentActivityPanel from "./components/AgentActivityPanel";
import QueryInput from "./components/QueryInput";
import ResponsePanel from "./components/ResponsePanel";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const demoQueries = [
  "How do I fix Kafka consumer lag after a deployment?",
  "Why would a Kubernetes pod enter CrashLoopBackOff after a config change?",
  "What past incidents mention SSO login loops or auth callback issues?",
];

export default function App() {
  const [query, setQuery] = useState(demoQueries[0]);
  const [result, setResult] = useState(null);
  const [visibleTrace, setVisibleTrace] = useState([]);
  const [loading, setLoading] = useState(false);
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
      const timeoutId = window.setTimeout(() => {
        setVisibleTrace((current) => [...current, item]);
      }, index * 450);
      timeoutsRef.current.push(timeoutId);
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);
    setVisibleTrace([]);

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
    <main className="min-h-screen px-4 py-8 text-ink md:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 space-y-4 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.32em] text-pine/70">
            Kortex
          </p>
          <h1 className="font-display text-4xl text-ink md:text-6xl">
            Agentic Enterprise Knowledge Copilot
          </h1>
          <p className="mx-auto max-w-3xl text-base text-slate-600 md:text-lg">
            A multi-agent RAG pipeline that triages questions, retrieves document and ticket context,
            reranks evidence, synthesizes answers, and escalates when confidence drops.
          </p>
        </header>

        <QueryInput value={query} onChange={setQuery} onSubmit={handleSubmit} loading={loading} />

        <div className="mt-6 flex flex-wrap justify-center gap-2">
          {demoQueries.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setQuery(item)}
              className="rounded-full border border-slate-300 bg-white/75 px-4 py-2 text-sm text-slate-700 backdrop-blur transition hover:border-pine hover:text-pine"
            >
              {item}
            </button>
          ))}
        </div>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1fr,1.2fr]">
          <AgentActivityPanel trace={visibleTrace} loading={loading} />
          <ResponsePanel result={result} loading={loading} />
        </section>
      </div>
    </main>
  );
}
