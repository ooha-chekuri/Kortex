export default function QueryInput({ value, onChange, onSubmit, loading }) {
  return (
    <div className="mx-auto w-full max-w-5xl">
      <div className="rounded-3xl border border-pixel-border bg-pixel-card p-3 backdrop-blur" style={{ boxShadow: '0 0 20px rgba(0, 255, 65, 0.1)' }}>
        <form className="flex flex-col gap-3 md:flex-row" onSubmit={onSubmit}>
          <div className="relative flex-1">
            <span 
              className="absolute left-4 top-1/2 -translate-y-1/2"
              style={{ color: '#00ff41', fontFamily: '"Departure Mono", monospace' }}
            >
              {'>'}
            </span>
            <input
              className="min-h-14 flex-1 rounded-2xl border border-pixel-border bg-black/50 px-8 text-base text-white outline-none transition focus:border-pixel-green focus:ring-1 focus:ring-pixel-green/30 w-full"
              style={{ fontFamily: '"Departure Mono", monospace' }}
              placeholder="Ask Kortex about Kafka, Kubernetes, past incidents, or troubleshooting patterns..."
              value={value}
              onChange={(event) => onChange(event.target.value)}
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !value.trim()}
            className="inline-flex min-h-14 items-center justify-center rounded-2xl px-6 font-semibold text-black transition-all hover:scale-105 disabled:cursor-not-allowed disabled:opacity-50"
            style={{ 
              background: '#00ff41', 
              fontFamily: '"Departure Mono", monospace',
              boxShadow: '4px 4px 0px 0px #00d4ff'
            }}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-black/50 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-black/50 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-black/50 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span>RUNNING</span>
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <span>EXECUTE</span>
              </span>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}