import React from 'react';

const getAgentInfo = (trace) => {
  const t = trace.toLowerCase();
  if (t.includes('triage')) return { type: 'triage', icon: '📍', color: '#ff6b00', action: 'Analyzing intent' };
  if (t.includes('retrieval')) return { type: 'retrieval', icon: '🔎', color: '#00d4ff', action: 'Searching docs' };
  if (t.includes('ticket')) return { type: 'ticket', icon: '🎫', color: '#9d00ff', action: 'Finding tickets' };
  if (t.includes('rerank')) return { type: 'reranker', icon: '🎯', color: '#ffff00', action: 'Re-ranking results' };
  if (t.includes('synthes')) return { type: 'synthesis', icon: '⚡', color: '#00ff41', action: 'Generating answer' };
  if (t.includes('valid')) return { type: 'validator', icon: '🛡️', color: '#ff00ff', action: 'Validating confidence' };
  if (t.includes('escalated') || t.includes('escalat')) return { type: 'escalate', icon: '⚠️', color: '#ff0000', action: 'Escalating to human' };
  return { type: 'default', icon: '•', color: '#666666', action: 'Processing' };
};

export default function AgentActivityPanel({ trace, loading }) {
  return (
    <section className="rounded-3xl border border-pixel-border bg-pixel-card p-5 backdrop-blur relative overflow-hidden">
      {/* Decorative scanlines */}
      <div className="absolute inset-0 pointer-events-none opacity-10">
        <div className="w-full h-full" style={{
          background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, #00ff41 2px, #00ff41 4px)'
        }}></div>
      </div>
      
      <div className="mb-4 flex items-center justify-between relative z-10">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em]" style={{ color: '#00ff41' }}>
            Agent Activity
          </p>
          <h2 className="font-display text-2xl text-white" style={{ fontFamily: '"Departure Mono", monospace' }}>
            Agent Orchestration
          </h2>
        </div>
        {loading && (
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              {[0, 1, 2].map(i => (
                <div 
                  key={i}
                  className="w-2 h-2 animate-bounce"
                  style={{ 
                    background: '#00ff41', 
                    animationDelay: `${i * 150}ms` 
                  }}
                />
              ))}
            </div>
            <span className="text-sm" style={{ color: '#00ff41', fontFamily: '"Departure Mono", monospace' }}>
              RUNNING_
            </span>
          </div>
        )}
      </div>

      <div className="space-y-3 relative z-10">
        {trace.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-pixel-border p-4 text-sm" style={{ color: '#666' }}>
            <div className="flex items-center gap-2 mb-2">
              <span style={{ color: '#00ff41' }}>{'>'}</span>
              <span style={{ fontFamily: '"Departure Mono", monospace' }}>Waiting for query...</span>
            </div>
            <p style={{ fontFamily: '"Departure Mono", monospace', opacity: 0.7 }}>
              Agent pipeline steps will appear here in real-time.
            </p>
          </div>
        ) : null}

        {trace.map((item, index) => {
          const agentInfo = getAgentInfo(item);
          return (
            <div
              key={`${item}-${index}`}
              className="animate-fadeIn rounded-2xl border bg-black/30 px-4 py-3 transition-all hover:bg-black/40"
              style={{ 
                borderColor: agentInfo.color,
                fontFamily: '"Departure Mono", monospace'
              }}
            >
              <div className="flex items-start gap-3">
                {/* Pixel indicator */}
                <div 
                  className="w-3 h-3 mt-1"
                  style={{ 
                    background: agentInfo.color,
                    boxShadow: `0 0 8px ${agentInfo.color}`
                  }}
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span 
                      className="text-xs px-2 py-0.5"
                      style={{ 
                        background: agentInfo.color, 
                        color: '#000',
                        fontFamily: '"Departure Mono", monospace'
                      }}
                    >
                      {agentInfo.type.toUpperCase()}
                    </span>
                    <span className="text-sm" style={{ color: '#666' }}>
                      Step {index + 1}
                    </span>
                  </div>
                  <p className="text-sm" style={{ color: '#e0e0e0' }}>
                    {item}
                  </p>
                  <p className="text-xs mt-1" style={{ color: agentInfo.color, opacity: 0.8 }}>
                    {agentInfo.action}
                  </p>
                </div>
                {/* Status indicator */}
                <div className="flex items-center">
                  <div 
                    className="w-2 h-2 animate-pulse"
                    style={{ background: agentInfo.color }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Progress indicator at bottom */}
      {trace.length > 0 && (
        <div className="mt-4 pt-4 border-t border-pixel-border">
          <div className="flex items-center justify-between text-xs" style={{ fontFamily: '"Departure Mono", monospace', color: '#666' }}>
            <span>PROGRESS</span>
            <span>{Math.round((trace.length / 6) * 100)}%</span>
          </div>
          <div className="flex gap-1 mt-2">
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="flex-1 h-2"
                style={{
                  background: i < trace.length ? '#00ff41' : '#1e1e2e',
                  border: '1px solid #00ff41'
                }}
              />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}