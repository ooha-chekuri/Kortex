// Pixel Agent Sprites
// Animated pixel art agents

import React from 'react';

const PixelAgent = ({ type, active, delay = 0 }) => {
  const colors = {
    triage: '#ff6b00',    // Orange
    retrieval: '#00d4ff', // Cyan
    ticket: '#9d00ff',    // Purple
    reranker: '#ffff00',  // Yellow
    synthesis: '#00ff41', // Green
    validator: '#ff00ff'   // Magenta
  };

  const color = colors[type] || '#ffffff';

  return (
    <div 
      className={`relative transition-all duration-300 ${active ? 'scale-110' : 'scale-100'}`}
      style={{ 
        animationDelay: `${delay}ms`,
        filter: active ? `drop-shadow(0 0 8px ${color})` : 'none'
      }}
    >
      {/* Pixel art representation */}
      <div 
        className="w-16 h-16 md:w-20 md:h-20 relative"
        style={{
          imageRendering: 'pixelated',
        }}
      >
        {/* Agent body - pixel grid */}
        <div 
          className="absolute inset-0 grid grid-cols-4 grid-rows-4 gap-0"
          style={{
            boxShadow: active ? `0 0 20px ${color}, inset 0 0 10px ${color}` : 'none',
            border: `2px solid ${color}`,
            background: 'rgba(0,0,0,0.8)'
          }}
        >
          {/* Eyes */}
          <div className="col-start-2 row-start-2 bg-transparent"></div>
          <div className="col-start-3 row-start-2 bg-transparent"></div>
          
          {/* Eye pixels */}
          <div 
            className={`col-start-2 row-start-2 ${active ? 'animate-pulse' : ''}`}
            style={{ background: color, opacity: 0.9 }}
          ></div>
          <div 
            className={`col-start-3 row-start-2 ${active ? 'animate-pulse' : ''}`}
            style={{ background: color, opacity: 0.9 }}
          ></div>
          
          {/* Body rows */}
          <div className="col-span-4 row-start-3" style={{ background: color, opacity: 0.7 }}></div>
          <div className="col-span-4 row-start-4" style={{ background: color, opacity: 0.5 }}></div>
        </div>

        {/* Active indicator */}
        {active && (
          <div 
            className="absolute -top-2 left-1/2 -translate-x-1/2 w-2 h-2 animate-ping"
            style={{ background: color }}
          ></div>
        )}

        {/* Agent type label */}
        <div 
          className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs px-2 py-0.5 whitespace-nowrap"
          style={{ 
            background: color, 
            color: '#000',
            fontFamily: '"Departure Mono", monospace',
            fontSize: '10px'
          }}
        >
          {type.toUpperCase()}
        </div>
      </div>
    </div>
  );
};

// Connection lines between agents
const ConnectionLine = ({ from, to, active }) => {
  if (!active) return null;
  
  return (
    <div 
      className="absolute h-0.5 animate-pulse"
      style={{
        background: `linear-gradient(90deg, transparent, #00ff41, transparent)`,
        animationDuration: '0.5s'
      }}
    />
  );
};

// Agent pipeline visualization
export const AgentPipeline = ({ activeAgent, trace }) => {
  const agents = [
    { type: 'triage', label: 'Triage' },
    { type: 'retrieval', label: 'Retrieve' },
    { type: 'ticket', label: 'Ticket' },
    { type: 'reranker', label: 'Rerank' },
    { type: 'synthesis', label: 'Synthesize' },
    { type: 'validator', label: 'Validate' }
  ];

  const getAgentType = (traceStep) => {
    const step = traceStep.toLowerCase();
    if (step.includes('triage')) return 'triage';
    if (step.includes('retrieval')) return 'retrieval';
    if (step.includes('ticket')) return 'ticket';
    if (step.includes('rerank')) return 'reranker';
    if (step.includes('synthes')) return 'synthesis';
    if (step.includes('valid')) return 'validator';
    return null;
  };

  // Determine active agent based on trace
  const activeType = trace?.length > 0 ? getAgentType(trace[trace.length - 1]) : null;

  return (
    <div className="flex items-center justify-center gap-2 md:gap-4 flex-wrap py-4">
      {agents.map((agent, index) => {
        const isActive = activeType === agent.type || (index === 0 && trace?.length === 0);
        return (
          <React.Fragment key={agent.type}>
            <PixelAgent 
              type={agent.type} 
              active={isActive}
              delay={index * 100}
            />
            {index < agents.length - 1 && (
              <div className="hidden md:block text-pixel-green">
                <span className="text-lg animate-pulse">→</span>
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};

// Floating pixel decorations
export const PixelDecoration = () => {
  const pixels = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    left: Math.random() * 100,
    top: Math.random() * 100,
    delay: Math.random() * 3000,
    size: Math.random() * 4 + 2,
    color: ['#00ff41', '#00d4ff', '#ff00ff', '#ffff00'][Math.floor(Math.random() * 4)]
  }));

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {pixels.map(pixel => (
        <div
          key={pixel.id}
          className="absolute animate-float"
          style={{
            left: `${pixel.left}%`,
            top: `${pixel.top}%`,
            width: `${pixel.size}px`,
            height: `${pixel.size}px`,
            background: pixel.color,
            opacity: 0.3,
            animationDelay: `${pixel.delay}ms`,
            boxShadow: `0 0 ${pixel.size * 2}px ${pixel.color}`
          }}
        />
      ))}
    </div>
  );
};

// Terminal-style typing effect
export const TerminalText = ({ text, delay = 0 }) => {
  const [displayed, setDisplayed] = React.useState('');
  const [index, setIndex] = React.useState(0);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (index < text.length) {
        setDisplayed(text.slice(0, index + 1));
        setIndex(index + 1);
      }
    }, Math.random() * 30 + 20);
    return () => clearTimeout(timer);
  }, [index, text]);

  return (
    <span style={{ fontFamily: '"Departure Mono", monospace' }}>
      {displayed}
      {index < text.length && (
        <span className="animate-blink" style={{ color: '#00ff41' }}>_</span>
      )}
    </span>
  );
};

// Progress bar with pixel style
export const PixelProgress = ({ value, max = 100, color = '#00ff41' }) => {
  const percentage = (value / max) * 100;
  const blocks = Math.floor(percentage / 10);
  
  return (
    <div className="flex gap-1">
      {[...Array(10)].map((_, i) => (
        <div
          key={i}
          className={`w-3 h-4 ${i < blocks ? 'animate-pulse' : ''}`}
          style={{
            background: i < blocks ? color : 'transparent',
            border: `1px solid ${color}`,
            opacity: i < blocks ? 1 : 0.3
          }}
        />
      ))}
    </div>
  );
};

export default PixelAgent;