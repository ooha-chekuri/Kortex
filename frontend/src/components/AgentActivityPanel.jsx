const pickIcon = (trace) => {
  if (trace.includes("Triage")) return "🧭";
  if (trace.includes("Retrieval")) return "🔍";
  if (trace.includes("Ticket")) return "🎫";
  if (trace.includes("Reranker")) return "🎯";
  if (trace.includes("Synthesis")) return "🧠";
  if (trace.includes("Validator")) return "🛡️";
  if (trace.includes("Escalated")) return "⚠️";
  return "•";
};

export default function AgentActivityPanel({ trace, loading }) {
  return (
    <section className="rounded-3xl border border-white/70 bg-white/85 p-5 shadow-card backdrop-blur">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-pine/70">
            Agent Activity
          </p>
          <h2 className="font-display text-2xl text-ink">Explainable orchestration</h2>
        </div>
        {loading ? <span className="text-sm text-pine">Running...</span> : null}
      </div>

      <div className="space-y-3">
        {trace.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 p-4 text-sm text-slate-500">
            Agent steps will appear here as the pipeline runs.
          </div>
        ) : null}

        {trace.map((item, index) => (
          <div
            key={`${item}-${index}`}
            className="animate-fadeIn rounded-2xl border border-slate-200 bg-mist px-4 py-3"
          >
            <div className="flex items-start gap-3">
              <span className="text-xl">{pickIcon(item)}</span>
              <div>
                <p className="font-medium text-ink">{item}</p>
                <p className="text-sm text-slate-500">Step {index + 1} completed</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
