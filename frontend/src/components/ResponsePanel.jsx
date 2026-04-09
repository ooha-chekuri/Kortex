import ReactMarkdown from "react-markdown";
import EscalationBanner from "./EscalationBanner";

function confidenceTone(score) {
  if (score > 0.75) return "bg-emerald-500";
  if (score >= 0.5) return "bg-amber-500";
  return "bg-red-500";
}

function sourceLabel(source) {
  if (source.doc) return `${source.doc} - p.${source.page}`;
  if (source.ticket) return source.ticket;
  return "Source";
}

export default function ResponsePanel({ result, loading }) {
  const confidence = result?.confidence ?? 0;
  const escalated = result?.status === "escalated";

  return (
    <section className="rounded-3xl border border-white/70 bg-white/85 p-5 shadow-card backdrop-blur">
      <div className="mb-4">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-pine/70">
          Response
        </p>
        <h2 className="font-display text-2xl text-ink">Grounded answer</h2>
      </div>

      <EscalationBanner visible={escalated} reason={result?.reason} />

      <div className="min-h-64 rounded-2xl border border-slate-200 bg-white p-5">
        {loading ? (
          <div className="flex h-full min-h-52 items-center justify-center text-slate-500">
            Synthesizing a grounded response...
          </div>
        ) : result ? (
          <div className="space-y-5">
            <div className="markdown-body prose prose-slate max-w-none">
              <ReactMarkdown>{result.answer || result.suggestion || "No answer available."}</ReactMarkdown>
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-medium text-slate-700">Confidence</span>
                <span className="text-slate-500">{confidence.toFixed(2)}</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-slate-200">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${confidenceTone(confidence)}`}
                  style={{ width: `${confidence * 100}%` }}
                />
              </div>
            </div>

            <div>
              <p className="mb-2 text-sm font-medium text-slate-700">Sources</p>
              <div className="flex flex-wrap gap-2">
                {(result.sources || []).length > 0 ? (
                  result.sources.map((source, index) => (
                    <button
                      type="button"
                      key={`${sourceLabel(source)}-${index}`}
                      className="rounded-full border border-slate-300 bg-mist px-3 py-1 text-sm text-slate-700"
                    >
                      {sourceLabel(source)}
                    </button>
                  ))
                ) : (
                  <span className="text-sm text-slate-500">No sources returned.</span>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex h-full min-h-52 items-center justify-center text-center text-slate-500">
            Submit a query to see the answer, confidence score, and supporting sources.
          </div>
        )}
      </div>
    </section>
  );
}
