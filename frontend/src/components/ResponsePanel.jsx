import React, { useState, useEffect, useMemo, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import EscalationBanner from "./EscalationBanner";
import CitationTooltip from "./CitationTooltip";

function confidenceTone(score) {
  if (score > 0.75) return "#00ff41";
  if (score >= 0.5) return "#ffff00";
  return "#ff0000";
}

function extractCitations(answer) {
  if (!answer) return [];
  const regex = /\[([^\]]+\.pdf|[^\]]+-\d+)\]/g;
  const citations = [];
  let match;
  while ((match = regex.exec(answer)) !== null) {
    if (!citations.find(c => c.name === match[1])) {
      citations.push({
        name: match[1],
        startIndex: match.index,
        endIndex: match.index + match[0].length
      });
    }
  }
  return citations;
}

function buildCitationMap(contexts) {
  const map = {};
  if (!contexts) return map;
  // Sort contexts by retrieval score if available to get best chunks first
  const sortedContexts = [...contexts].sort((a, b) => 
    (b.retrieval_score || b.reranker_score || 0) - (a.retrieval_score || a.reranker_score || 0)
  );
  
  for (const ctx of sortedContexts) {
    const file = ctx.file || ctx.doc || ctx.ticket_id;
    if (file && ctx.content && !map[file]) {
      map[file] = ctx.content;
    }
  }
  return map;
}

function PdfModal({ source, content, onClose }) {
  if (!source?.file) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="relative w-[250px] h-[250px] bg-[#1a1a2e] rounded-lg overflow-hidden flex flex-col"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-3 py-2 border-b" style={{ borderColor: '#00d4ff', background: 'rgba(0, 212, 255, 0.1)' }}>
          <span className="text-xs font-mono truncate" style={{ color: '#00d4ff' }}>
            {source.file}
          </span>
          <button
            onClick={onClose}
            className="w-6 h-6 flex items-center justify-center rounded bg-red-500 text-white hover:bg-red-600 text-sm font-bold"
          >
            ×
          </button>
        </div>
        
        <div className="flex-1 overflow-auto p-3" style={{ background: '#0f0f23' }}>
          <pre className="text-xs whitespace-pre-wrap" style={{ color: '#e0e0e0', fontFamily: '"Departure Mono", monospace' }}>
            {content || "No content available"}
          </pre>
        </div>
      </div>
    </div>
  );
}

function sourceLabel(source) {
  if (source.doc) return `${source.doc} - p.${source.page}`;
  if (source.ticket) return source.ticket;
  return "Source";
}

function getSourceContent(source, contexts) {
  if (!source?.doc || !contexts) return null;
  for (const ctx of contexts) {
    const file = ctx.file || ctx.doc;
    const page = ctx.page;
    if (file === source.doc && page === source.page) {
      return ctx.content || null;
    }
  }
  return null;
}
function CitationSpan({ name, content, onHover, onLeave, onClick, isHovered }) {
  const handleMouseEnter = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    onHover(name, { 
      left: rect.left + rect.width / 2, 
      top: rect.top 
    });
  };

  return (
    <span
      className={`inline-flex items-center mx-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold cursor-pointer transition-all duration-200 ${
        isHovered 
          ? 'scale-110 shadow-[0_0_10px_rgba(0,212,255,0.5)] z-20' 
          : 'opacity-90 hover:opacity-100'
      }`}
      style={{ 
        fontFamily: '"Departure Mono", monospace',
        background: isHovered ? '#00d4ff' : 'rgba(0, 212, 255, 0.15)',
        color: isHovered ? '#000' : '#00d4ff',
        border: `1px solid ${isHovered ? '#fff' : 'rgba(0, 212, 255, 0.4)'}`,
        verticalAlign: 'middle',
        position: 'relative',
        top: '-1px'
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={onLeave}
      onClick={onClick}
    >
      [{name}]
    </span>
  );
}


function AnswerWithCitations({ answer, citationMap, onCitationHover, onCitationLeave, onCitationClick, hoveredCitation }) {
  const parts = useMemo(() => {
    if (!answer) return [{ type: 'text', content: '' }];
    
    const regex = /\[([^\]]+\.pdf|[^\]]+-\d+)\]/g;
    const result = [];
    let lastIndex = 0;
    let match;
    
    while ((match = regex.exec(answer)) !== null) {
      if (match.index > lastIndex) {
        result.push({
          type: 'text',
          content: answer.slice(lastIndex, match.index)
        });
      }
      result.push({
        type: 'citation',
        content: match[0],
        name: match[1]
      });
      lastIndex = match.index + match[0].length;
    }
    
    if (lastIndex < answer.length) {
      result.push({
        type: 'text',
        content: answer.slice(lastIndex)
      });
    }
    
    return result;
  }, [answer]);

  return (
    <div className="markdown-body max-w-none" style={{ color: '#e0e0e0', fontFamily: '"Departure Mono", monospace' }}>
      {parts.map((part, idx) => {
        if (part.type === 'text') {
          return <ReactMarkdown key={idx}>{part.content}</ReactMarkdown>;
        }
        return (
          <CitationSpan
            key={idx}
            name={part.name}
            content={citationMap[part.name]}
            onHover={(name, pos) => onCitationHover(name, pos)}
            onLeave={onCitationLeave}
            onClick={onCitationClick}
            isHovered={hoveredCitation === part.name}
          />
        );
      })}
    </div>
  );
}

export default function ResponsePanel({ result, loading }) {
  const [selectedSource, setSelectedSource] = useState(null);
  const [hoveredCitation, setHoveredCitation] = useState(null);
  const [tooltipPosition, setTooltipPosition] = useState(null);
  const confidence = result?.confidence ?? 0;
  const escalated = result?.status === "escalated";
  const color = confidenceTone(confidence);

  const citationMap = useMemo(() => buildCitationMap(result?.contexts), [result?.contexts]);

  const handleCitationHover = useCallback((name, position) => {
    setHoveredCitation(name);
    setTooltipPosition(position);
  }, []);

  const handleCitationLeave = useCallback(() => {
    setHoveredCitation(null);
  }, []);

  const handleCitationClick = useCallback((name) => {
    const source = result?.sources?.find(s => s.doc === name || s.ticket === name);
    if (source) {
      const content = citationMap[name] || getSourceContent(source, result?.contexts);
      setSelectedSource({
        file: source.doc || source.ticket,
        page: source.page,
        content: content
      });
    }
  }, [result?.sources, result?.contexts, citationMap]);

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

      <div 
        className="min-h-64 rounded-2xl border border-pixel-border bg-black/50 p-5 relative z-10"
      >
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
            <AnswerWithCitations
              answer={result.answer || result.suggestion || "No answer available."}
              citationMap={citationMap}
              onCitationHover={handleCitationHover}
              onCitationLeave={handleCitationLeave}
              onCitationClick={handleCitationClick}
              hoveredCitation={hoveredCitation}
            />

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
                      onClick={() => setSelectedSource({ 
                        file: source.doc, 
                        page: source.page,
                        content: getSourceContent(source, result.contexts) 
                      })}
                      className="rounded px-3 py-1 text-sm transition-all hover:scale-105 hover:bg-[#00d4ff] hover:text-black cursor-pointer"
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

      {selectedSource && (
        <PdfModal 
          source={selectedSource} 
          content={selectedSource.content}
          onClose={() => setSelectedSource(null)} 
        />
      )}

      <CitationTooltip
        citation={hoveredCitation ? `[${hoveredCitation}]` : ""}
        content={hoveredCitation ? citationMap[hoveredCitation] : null}
        position={tooltipPosition}
        onClose={() => setHoveredCitation(null)}
        onClick={() => {
          if (hoveredCitation) {
            handleCitationClick(hoveredCitation);
          }
        }}
        visible={!!hoveredCitation}
      />
    </section>
  );
}