import React from "react";
import ReactMarkdown from "react-markdown";
import EscalationBanner from "./EscalationBanner";

function confidenceTone(score) {
  if (score > 0.75) return "#00ff41";  // Green - good
  if (score >= 0.5) return "#ffff00"; // Yellow - retry
  return "#ff0000";                    // Red - escalate
}

function sourceLabel(source) {
  if (source.doc) return `${source.doc} - p.${source.page}`;
  if (source.ticket) return source.ticket;
  return "Source";
}

export default function ResponsePanel({ result, loading }) {
  const confidence = result?.confidence ?? 0;
  const escalated = result?.status === "escalated";
  const color = confidenceTone(confidence);

  return (
    <section className="rounded-3xl border border-pixel-border bg-pixel-card p-5 backdrop-blur relative overflow-hidden">
      {/* Scanline effect */}
      <div className="absolute inset-0 pointer-events-none opacity-5">
        <div className="w-full h-full" style={{
          background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, #fff 2px, #fff 4px)'
        }}></div>
      </div>
      
      <div className="mb-4 relative z-10">
        <p className="text-xs font-semibold uppercase tracking-[0.24em]" style={{ color: '#00d4ff' }}>
          Response
        </p>
        <h2 className="font-display text-2xl text-white" style={{ fontFamily: '"Departure Mono", monospace' }}>
          Generated Answer
        </h2>
      </div>

      <EscalationBanner visible={escalated} reason={result?.reason} />

      <div className="min-h-64 rounded-2xl border border-pixel-border bg-black/50 p-5 relative z-10">
        {loading ? (
          <div className="flex h-full min-h-52 items-center justify-center flex-col gap-4">
            <div className="flex gap-2">
              {[0, 1, 2, 3, 4].map(i => (
                <div 
                  key={i}
                  className="w-4 h-8 animate-bounce"
                  style={{ 
                    background: i % 2 === 0 ? '#00ff41' : '#00d4ff',
                    animationDelay: `${i * 100}ms`
                  }}
                />
              ))}
            </div>
            <span style={{ color: '#00ff41', fontFamily: '"Departure Mono", monospace' }}>
              {'>'} Synthesizing response...
            </span>
          </div>
        ) : result ? (
          <div className="space-y-5">
            <div className="markdown-body max-w-none" style={{ color: '#e0e0e0', fontFamily: '"Departure Mono", monospace' }}>
              <ReactMarkdown>{result.answer || result.suggestion || "No answer available."}</ReactMarkdown>
            </div>

            <div className="border-t border-pixel-border pt-4">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-medium" style={{ color: '#00d4ff' }}>CONFIDENCE</span>
                <span style={{ color: color, fontFamily: '"Departure Mono", monospace' }}>
                  {confidence.toFixed(2)}
                </span>
              </div>
              <div className="h-4 overflow-hidden rounded border" style={{ borderColor: color }}>
                <div
                  className="h-full transition-all duration-500"
                  style={{ 
                    width: `${confidence * 100}%`,
                    background: color,
                    boxShadow: `0 0 10px ${color}`
                  }}
                />
              </div>
            </div>

            <div className="border-t border-pixel-border pt-4">
              <p className="mb-2 text-sm font-medium" style={{ color: '#00d4ff', fontFamily: '"Departure Mono", monospace' }}>
                SOURCES_
              </p>
              <div className="flex flex-wrap gap-2">
                {(result.sources || []).length > 0 ? (
                  result.sources.map((source, index) => (
                    <button
                      key={`${sourceLabel(source)}-${index}`}
                      className="rounded px-3 py-1 text-sm transition-all hover:scale-105"
                      style={{ 
                        border: '1px solid #00d4ff', 
                        color: '#00d4ff',
                        fontFamily: '"Departure Mono", monospace',
                        background: 'rgba(0, 212, 255, 0.1)'
                      }}
                    >
                      {sourceLabel(source)}
                    </button>
                  ))
                ) : (
                  <span className="text-sm" style={{ color: '#666', fontFamily: '"Departure Mono", monospace' }}>
                    No sources returned_
                  </span>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex h-full min-h-52 items-center justify-center text-center" style={{ color: '#666', fontFamily: '"Departure Mono", monospace' }}>
            <div>
              <div className="mb-2" style={{ color: '#00ff41' }}>{'>'}_</div>
              <p>Submit a query to see the answer, confidence score, and supporting sources.</p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}