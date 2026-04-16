import { useState, useEffect, useRef } from "react";

export default function CitationTooltip({ 
  citation, 
  content, 
  position, 
  onClose, 
  onClick,
  visible 
}) {
  const tooltipRef = useRef(null);
  const [style, setStyle] = useState({});

  useEffect(() => {
    if (!visible || !position || !tooltipRef.current) return;

    const tooltip = tooltipRef.current;
    const tooltipWidth = 320;
    const tooltipHeight = 280;
    const padding = 20;

    let left = position.left - (tooltipWidth / 2);
    let top = position.top - tooltipHeight - 15;

    // Boundary checks
    if (left + tooltipWidth > window.innerWidth - padding) {
      left = window.innerWidth - tooltipWidth - padding;
    }
    if (left < padding) left = padding;
    
    if (top < padding) {
      top = position.top + 25; // Show below if not enough space above
    }

    setStyle({
      left: `${left}px`,
      top: `${top}px`,
      width: `${tooltipWidth}px`,
      height: `${tooltipHeight}px`,
    });
  }, [visible, position]);

  if (!visible) return null;

  return (
    <div
      ref={tooltipRef}
      className="fixed z-50 rounded-xl overflow-hidden border transition-all duration-200 animate-in fade-in zoom-in slide-in-from-bottom-2"
      style={{
        width: style.width,
        height: style.height,
        left: style.left,
        top: style.top,
        background: "rgba(15, 15, 35, 0.95)",
        borderColor: "#00d4ff",
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 212, 255, 0.2)",
        backdropFilter: "blur(8px)",
        pointerEvents: "auto",
      }}
    >
      <div
        className="px-4 py-2 flex items-center justify-between bg-white/5 border-b"
        style={{ borderColor: "rgba(0, 212, 255, 0.3)" }}
      >
        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider font-bold" style={{ color: "#00d4ff" }}>
            Source Context
          </span>
          <span className="text-sm font-medium text-white truncate max-w-[200px]">
            {citation}
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div className="p-4 overflow-y-auto" style={{ height: "calc(100% - 90px)" }}>
        <p className="text-xs leading-relaxed text-gray-200 font-sans" style={{ letterSpacing: '0.01em' }}>
          {content ? (
            content
          ) : (
            <span className="italic opacity-50">No preview text available for this citation.</span>
          )}
        </p>
      </div>

      <div className="px-4 py-2 bg-black/20 border-t flex items-center justify-between" style={{ borderColor: "rgba(0, 212, 255, 0.1)" }}>
        <span className="text-[10px] text-gray-500 font-mono">
          Interactive Citation
        </span>
        <button
          onClick={onClick}
          className="text-xs font-semibold flex items-center gap-1 py-1 px-3 rounded-full transition-all hover:scale-105"
          style={{ 
            background: "linear-gradient(135deg, #00d4ff 0%, #0088ff 100%)",
            color: "#000"
          }}
        >
          View Full Document
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14"></path>
            <path d="M12 5l7 7-7 7"></path>
          </svg>
        </button>
      </div>
    </div>
  );
}