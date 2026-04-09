export default function QueryInput({ value, onChange, onSubmit, loading }) {
  return (
    <div className="mx-auto w-full max-w-5xl">
      <div className="rounded-3xl border border-white/70 bg-white/80 p-3 shadow-card backdrop-blur">
        <form className="flex flex-col gap-3 md:flex-row" onSubmit={onSubmit}>
          <input
            className="min-h-14 flex-1 rounded-2xl border border-slate-200 bg-white px-5 text-base text-ink outline-none transition focus:border-pine focus:ring-2 focus:ring-pine/20"
            placeholder="Ask Kortex about Kafka, Kubernetes, past incidents, or troubleshooting patterns..."
            value={value}
            onChange={(event) => onChange(event.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !value.trim()}
            className="inline-flex min-h-14 items-center justify-center rounded-2xl bg-pine px-6 font-semibold text-white transition hover:bg-pine/90 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                Running agents
              </span>
            ) : (
              "Ask Kortex"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
