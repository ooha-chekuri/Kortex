import React, { useEffect, useState, useRef } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function SystemLogs() {
  const [logs, setLogs] = useState([]);
  const scrollRef = useRef(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/logs`);
        if (response.ok) {
          const data = await response.json();
          setLogs(data);
        }
      } catch (err) {
        // Silently fail to not clutter console if backend is restarting
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="mt-8 rounded-3xl border border-pixel-border bg-black/50 p-5 backdrop-blur relative overflow-hidden">
       {/* Decorative subtle pulse */}
       <div className="absolute top-4 right-4 flex items-center gap-2">
         <div className="w-1.5 h-1.5 rounded-full bg-[#00d4ff] animate-pulse" />
         <span className="text-[10px]" style={{ color: '#00d4ff', fontFamily: '"Departure Mono", monospace' }}>LIVE_STREAM</span>
       </div>

      <h3 className="text-xs font-semibold uppercase tracking-[0.24em] mb-3" style={{ color: '#00d4ff', fontFamily: '"Departure Mono", monospace' }}>
        System Logs
      </h3>
      <div 
        ref={scrollRef}
        className="h-48 overflow-y-auto font-mono text-[10px] space-y-1 p-3 bg-black/40 rounded-xl border border-pixel-border/30 custom-scrollbar"
        style={{ 
          fontFamily: '"Departure Mono", monospace',
          boxShadow: 'inset 0 0 10px rgba(0,0,0,0.5)'
        }}
      >
        {logs.length === 0 ? (
          <div className="text-gray-600 italic">Initializing log stream...</div>
        ) : (
          logs.map((log, i) => {
            let color = '#888';
            if (log.includes('[ERROR]')) color = '#ff4444';
            else if (log.includes('[WARNING]')) color = '#ffaa00';
            else if (log.includes('successfully')) color = '#00ff41';
            
            return (
              <div key={i} className="whitespace-pre-wrap break-all border-l-2 pl-2 mb-1" style={{ borderColor: color, color: color }}>
                {log}
              </div>
            );
          })
        )}
      </div>
      <style dangerouslySetInnerHTML={{ __html: `
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #0a0a0f; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #00d4ff; border-radius: 10px; }
      `}} />
    </div>
  );
}
