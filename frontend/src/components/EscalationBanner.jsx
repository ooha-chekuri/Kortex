export default function EscalationBanner({ visible, reason }) {
  if (!visible) return null;

  return (
    <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-red-800">
      <p className="font-semibold">⚠️ Low Confidence — Escalated to Human</p>
      {reason ? <p className="mt-1 text-sm">{reason}</p> : null}
    </div>
  );
}
