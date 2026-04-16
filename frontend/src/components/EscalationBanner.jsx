export default function EscalationBanner({ visible, reason }) {
  if (!visible) return null;

  return (
    <div className="mb-4 rounded-2xl border border-red-500 bg-red-900/30 px-4 py-3 animate-pulse" style={{ borderColor: '#ff0000' }}>
      <div className="flex items-center gap-2">
        <span style={{ color: '#ff0000', fontSize: '18px' }}>⚠</span>
        <p className="font-semibold" style={{ color: '#ff0000', fontFamily: '"Departure Mono", monospace' }}>
          LOW CONFIDENCE — ESCALATED TO HUMAN
        </p>
      </div>
      {reason ? (
        <p className="mt-1 text-sm" style={{ color: '#ff6666', fontFamily: '"Departure Mono", monospace' }}>
          {'>'} {reason}
        </p>
      ) : null}
    </div>
  );
}